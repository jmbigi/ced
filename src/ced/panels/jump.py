from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label
from textual.containers import Vertical


class JumpMode(Screen[str | None]):
    DEFAULT_CSS = """
    JumpMode {
        align: center middle;
    }

    JumpMode > Vertical {
        width: 40;
        height: 6;
        border: thick $secondary;
        background: $surface;
        align: center middle;
    }

    JumpMode Label {
        text-align: center;
    }

    JumpMode .key-display {
        width: 100%;
        padding: 1;
        background: $boost;
        color: $text;
        text-style: bold;
        text-align: center;
    }

    JumpMode .hint {
        color: $text-muted;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._buffer = ""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Jump Mode: type 2 characters to jump to", classes="hint")
            yield Label("__", id="jump-display", classes="key-display")

    def on_mount(self) -> None:
        self._update_display()

    def _update_display(self) -> None:
        display = self.query_one("#jump-display", Label)
        display.update(self._buffer.ljust(2, "_"))

    def key_press(self, event) -> None:
        char = event.character
        if char is None:
            return
        if len(self._buffer) < 2:
            self._buffer += char
            self._update_display()
        if len(self._buffer) == 2:
            self.dismiss(self._buffer)

    def key_backspace(self) -> None:
        if self._buffer:
            self._buffer = self._buffer[:-1]
            self._update_display()

    def key_escape(self) -> None:
        self.dismiss(None)
