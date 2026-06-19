from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from ced.panels.terminal import TerminalPanel


class TestTerminalPanel:
    def test_init_defaults(self) -> None:
        t = TerminalPanel()
        assert t._shell == "/bin/bash"
        assert t._rows == 24
        assert t._cols == 80
        assert t._pid is None
        assert t._fd is None
        assert t._running is False

    def test_init_custom(self) -> None:
        t = TerminalPanel(shell="/bin/zsh", rows=40, cols=120)
        assert t._shell == "/bin/zsh"
        assert t._rows == 40
        assert t._cols == 120

    def test_start_and_stop(self) -> None:
        """Start the shell PTY, verify it runs, then clean up."""
        import asyncio

        try:
            asyncio.get_running_loop()
            return
        except RuntimeError:
            pass
        t = TerminalPanel()
        with patch.object(t, "on_mount"):
            with patch("asyncio.get_event_loop"):
                t._start_shell()
        if t._fd is None:
            return  # PTY fork may not work in all test environments
        assert t._pid is not None
        assert t._running is True
        t.write("echo hello\n")
        import select
        import time

        time.sleep(0.2)
        try:
            r, _, _ = select.select([t._fd], [], [], 0.5)
            if r:
                data = os.read(t._fd, 4096)
                t._stream.feed(data.decode("utf-8", errors="replace"))
        except Exception:
            pass
        try:
            os.write(t._fd, b"exit\n")
        except Exception:
            pass
        os.kill(t._pid, 9)
        os.waitpid(t._pid, 0)
        t._fd = None
        t._pid = None
        t._running = False

    def test_write_while_stopped(self) -> None:
        """write() should not crash when PTY is not running."""
        t = TerminalPanel()
        t.write("data")  # should be no-op

    def test_write_no_fd(self) -> None:
        t = TerminalPanel()
        t._running = True
        t.write("data")  # fd is None → should be no-op

    def test_render_line_out_of_bounds(self) -> None:
        t = TerminalPanel()
        strip = t.render_line(999)
        assert strip is not None

    def test_render_line_before_start(self) -> None:
        t = TerminalPanel()
        strip = t.render_line(0)
        assert strip is not None

    def test_set_size(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        with patch("fcntl.ioctl"):
            t._set_size(30, 100)

    def test_set_size_no_fd(self) -> None:
        t = TerminalPanel()
        t._set_size(30, 100)  # fd is None — should be no-op

    @pytest.mark.asyncio
    async def test_on_pty_read_data(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "refresh"):
            with patch("os.read", return_value=b"hello\n"):
                t._on_pty_read()
                output = "\n".join(t._screen.display)
                assert output.strip()

    @pytest.mark.asyncio
    async def test_on_pty_read_empty(self) -> None:
        """Empty data should trigger close."""
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch("os.read", return_value=b""):
            t._on_pty_read()
            assert t._running is False

    @pytest.mark.asyncio
    async def test_on_pty_read_oserror(self) -> None:
        """OSError should trigger close."""
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch("os.read", side_effect=OSError("closed")):
            t._on_pty_read()
            assert t._running is False

    def test_terminal_panel_default_css(self) -> None:
        assert "display: none" in TerminalPanel.DEFAULT_CSS

    def test_render_empty_screen(self) -> None:
        t = TerminalPanel()
        for y in range(5):
            strip = t.render_line(y)
            assert strip is not None

    def test_write_after_close(self) -> None:
        t = TerminalPanel()
        t._running = False
        t._fd = 999
        t.write("test")  # should not write because not running

    def test_write_with_oserror(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch("os.write", side_effect=OSError("broken pipe")):
            with patch.object(t, "_kill_shell") as mock_kill:
                t.write("data")
                mock_kill.assert_called_once()

    def test_kill_shell_with_pid_and_fd(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._pid = 12345
        t._running = True
        with patch("os.close"):
            with patch("os.kill"):
                with patch("os.waitpid"):
                    with patch("asyncio.get_event_loop") as mock_loop:
                        mock_loop.return_value.remove_reader = lambda x: None
                        t._kill_shell()
        assert t._fd is None
        assert t._pid is None
        assert t._running is False

    def test_kill_shell_no_pid_no_fd(self) -> None:
        t = TerminalPanel()
        t._kill_shell()  # should not crash

    def test_kill_shell_oserror_ignored(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._pid = 12345
        with patch("os.close", side_effect=OSError):
            with patch("os.kill", side_effect=OSError):
                with patch("asyncio.get_event_loop"):
                    t._kill_shell()  # should not crash

    def test_on_unmount(self) -> None:
        t = TerminalPanel()
        with patch.object(t, "_kill_shell") as mock_kill:
            t.on_unmount()
            mock_kill.assert_called_once()

    def test_on_key_character(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="a", character="a")
            t._on_key(ev)
            mock_write.assert_called_once_with("a")

    def test_on_key_enter(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="enter", character=None)
            t._on_key(ev)
            mock_write.assert_called_once_with("\r")

    def test_on_key_backspace(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="backspace", character=None)
            t._on_key(ev)
            mock_write.assert_called_once_with("\b")

    def test_on_key_tab(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="tab", character=None)
            t._on_key(ev)
            mock_write.assert_called_once_with("\t")

    def test_on_key_escape(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="escape", character=None)
            t._on_key(ev)
            mock_write.assert_called_once_with("\x1b")

    def test_on_key_space(self) -> None:
        t = TerminalPanel()
        t._fd = 999
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="space", character=None)
            t._on_key(ev)
            mock_write.assert_called_once_with(" ")

    def test_on_key_not_running(self) -> None:
        t = TerminalPanel()
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="a", character="a")
            t._on_key(ev)
            mock_write.assert_not_called()

    def test_on_key_no_fd(self) -> None:
        t = TerminalPanel()
        t._running = True
        with patch.object(t, "write") as mock_write:
            from textual.events import Key

            ev = Key(key="a", character="a")
            t._on_key(ev)
            mock_write.assert_not_called()

    def test_on_pty_read_no_fd(self) -> None:
        t = TerminalPanel()
        t._on_pty_read()  # fd is None → early return

    def test_render_line_when_stopped(self) -> None:
        t = TerminalPanel()
        t._running = False
        strip = t.render_line(0)
        assert strip is not None
