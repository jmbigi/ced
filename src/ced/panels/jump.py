from __future__ import annotations

from textual.app import ComposeResult
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Static


class JumpMode(ModalScreen[str | None]):
    """Modal screen for 2-character jump navigation.

    The user types two characters and the editor jumps to their
    first occurrence in the active file.
    """

    DEFAULT_CSS = """
    JumpMode {
        align: center middle;
    }

    JumpMode > Static {
        width: 12;
        height: 3;
        border: thick $primary;
        background: $surface;
        content-align: center middle;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._buffer = ""

    def compose(self) -> ComposeResult:
        """Yield the jump label widget."""
        yield Static("__", id="jump-label")

    def on_mount(self) -> None:
        """Update display on mount."""
        self._update_display()

    def _update_display(self) -> None:
        chars = self._buffer.ljust(2, "_")
        self.query_one("#jump-label", Static).update(chars)

    def key_press(self, event: Key) -> None:
        """Accumulate up to 2 characters then dismiss."""
        ch = event.character
        if ch is None:
            return
        self._buffer += ch
        self._update_display()
        if len(self._buffer) >= 2:
            self.dismiss(self._buffer)

    def key_backspace(self) -> None:
        """Remove the last character from the buffer."""
        self._buffer = self._buffer[:-1]
        self._update_display()

    def key_escape(self) -> None:
        """Dismiss without jumping."""
        self.dismiss(None)
