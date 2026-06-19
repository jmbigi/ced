from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmScreen(ModalScreen[bool]):
    def __init__(self, message: str, title: str = "Confirm") -> None:
        super().__init__()
        self._message = message
        self._title = title

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }

    ConfirmScreen > #dialog {
        width: 50;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }

    ConfirmScreen #message {
        margin: 1 0 2 0;
        text-align: center;
    }

    ConfirmScreen #buttons {
        align: center middle;
    }

    ConfirmScreen Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self._message, id="message")
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="cancel", variant="default")
                yield Button("Close", id="close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss(True)
        else:
            self.dismiss(False)


class QuitConfirmScreen(ModalScreen[str]):
    DEFAULT_CSS = """
    QuitConfirmScreen {
        align: center middle;
    }
    QuitConfirmScreen > #dialog {
        width: 50;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }
    QuitConfirmScreen #message {
        margin: 1 0 1 0;
        text-align: center;
    }
    QuitConfirmScreen Label {
        margin: 0 1;
    }
    QuitConfirmScreen #buttons {
        align: center middle;
        margin-top: 1;
    }
    QuitConfirmScreen Button {
        margin: 0 1;
    }
    """

    def __init__(self, files: list[str]) -> None:
        super().__init__()
        self._files = files

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("You have unsaved changes:", id="message")
            for f in self._files:
                yield Label(f"  \u2022 {f}")
            with Horizontal(id="buttons"):
                yield Button("Save & Quit", id="save", variant="primary")
                yield Button("Discard & Quit", id="discard", variant="error")
                yield Button("Cancel", id="cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id)
