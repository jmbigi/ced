from __future__ import annotations

import asyncio
import os
import pty
import signal
import struct
import termios
import fcntl

import pyte

from textual.events import Key
from textual.strip import Strip
from textual.widget import Widget


class TerminalPanel(Widget):
    """A real PTY-based terminal emulator panel.

    Forks a shell in a pseudo-terminal (PTY) and renders its output
    using pyte (Python Terminal Emulator).  Keystrokes from the user
    are forwarded into the PTY so the shell receives them.
    """

    DEFAULT_CSS = """
    TerminalPanel {
        height: 12;
        border: solid $primary;
        background: $surface;
        display: none;
    }
    """

    def __init__(
        self,
        shell: str = "/bin/bash",
        rows: int = 24,
        cols: int = 80,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._shell = shell
        self._rows = rows
        self._cols = cols
        self._screen = pyte.Screen(cols, rows)
        self._screen.set_mode(pyte.modes.LNM)
        self._stream = pyte.Stream(self._screen)
        self._pid: int | None = None
        self._fd: int | None = None
        self._running = False

    def on_mount(self) -> None:
        self._start_shell()

    def on_unmount(self) -> None:
        self._kill_shell()

    def _kill_shell(self) -> None:
        self._running = False
        if self._fd is not None:
            loop = asyncio.get_event_loop()
            try:
                loop.remove_reader(self._fd)
            except Exception:
                pass
            try:
                os.close(self._fd)
            except Exception:
                pass
            self._fd = None
        if self._pid is not None:
            try:
                os.kill(self._pid, signal.SIGKILL)
                os.waitpid(self._pid, 0)
            except Exception:
                pass
            self._pid = None
        self.refresh()

    def _start_shell(self) -> None:
        """Fork a shell process in a PTY."""
        if not hasattr(os, "fork"):
            self._running = False
            return
        if not os.path.isfile(self._shell) or not os.access(self._shell, os.X_OK):
            self._running = False
            return
        try:
            pid, fd = pty.fork()
        except (AttributeError, OSError, FileNotFoundError):
            self._running = False
            return
        if pid == 0:
            os.environ.setdefault("TERM", "xterm-256color")
            os.execvp(self._shell, [self._shell])
        else:
            self._pid = pid
            self._fd = fd
            self._running = True
            self._set_size(self._rows, self._cols)
            loop = asyncio.get_event_loop()
            loop.add_reader(fd, self._on_pty_read)

    def _set_size(self, rows: int, cols: int) -> None:
        """Send window size change to the child process."""
        if self._fd is not None:
            packed = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self._fd, termios.TIOCSWINSZ, packed)

    def _on_pty_read(self) -> None:
        """Called by the event loop when data is available on the PTY."""
        if self._fd is None:
            return
        try:
            data = os.read(self._fd, 65536)
        except OSError:
            self._kill_shell()
            return
        if not data:
            self._kill_shell()
            return
        self._stream.feed(data.decode("utf-8", errors="replace"))
        self.refresh()

    def write(self, data: str) -> None:
        """Write data to the PTY (sent by the user's keystrokes)."""
        if self._fd is not None and self._running:
            try:
                os.write(self._fd, data.encode("utf-8"))
            except OSError:
                self._kill_shell()

    def _on_key(self, event: Key) -> None:
        """Forward key events to the PTY."""
        if not self._running or self._fd is None:
            return
        if event.character is not None:
            self.write(event.character)
        elif event.key == "enter":
            self.write("\r")
        elif event.key == "backspace":
            self.write("\b")
        elif event.key == "tab":
            self.write("\t")
        elif event.key == "escape":
            self.write("\x1b")
        elif event.key == "space":
            self.write(" ")

    def render_line(self, y: int) -> Strip:
        """Render one line of the terminal output."""
        if not self._running or y >= self._screen.lines:
            return Strip.blank(self._cols)
        line = self._screen.buffer[y]
        segments = []
        for col in range(self._cols):
            char = line[col]
            fg = char.fg or "default"
            bg = char.bg or "default"
            style = f"#{fg} on #{bg}" if bg != "default" else f"#{fg}"
            segments.append((style, char.data or " "))
        return Strip(segments)

    def on_resize(self, event: Widget.Resize) -> None:
        cols = max(20, event.size.width)
        rows = max(5, event.size.height)
        self._cols = cols
        self._rows = rows
        self._screen.resize(rows, cols)
        self._set_size(rows, cols)
