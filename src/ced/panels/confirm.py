from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Horizontal, Vertical


class ConfirmScreen(ModalScreen[bool]):
    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }

    ConfirmScreen > Vertical {
        width: 50;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    ConfirmScreen #confirm-label {
        text-align: center;
        margin: 1 0 2 0;
    }

    ConfirmScreen #confirm-buttons {
        align: center middle;
        height: auto;
    }

    ConfirmScreen Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str, title: str = "Confirm") -> None:
        super().__init__()
        self._message = message
        self._title = title

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._message, id="confirm-label")
            with Horizontal(id="confirm-buttons"):
                yield Button("Yes", variant="primary", id="yes")
                yield Button("No", variant="default", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")
