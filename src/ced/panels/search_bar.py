from __future__ import annotations


from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Input, Button, Label
from textual.widget import Widget


class SearchBar(Widget):
    DEFAULT_CSS = """
    SearchBar {
        dock: top;
        height: auto;
        background: $surface;
        padding: 0 1;
        border-bottom: solid $primary;
    }

    SearchBar Input {
        width: 30;
    }

    SearchBar > Vertical {
        height: auto;
    }

    SearchBar > Vertical > Horizontal {
        height: 1;
    }

    SearchBar .label {
        width: auto;
        padding: 0 1;
    }

    SearchBar #replace-row {
        display: none;
    }
    """

    class SearchRequested(Message):
        def __init__(self, query: str) -> None:
            super().__init__()
            self.query = query

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._show_replace = False

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label("Find:", classes="label")
                yield Input(placeholder="Search...", id="find-input")
                yield Button("▽", id="toggle-replace", variant="default")
                yield Button("×", id="close-search", variant="default")
            with Horizontal(id="replace-row"):
                yield Label("Replace:", classes="label")
                yield Input(placeholder="Replace...", id="replace-input")
                yield Button("Replace", id="replace-btn", variant="primary")
                yield Button("All", id="replace-all-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-search":
            self.display = False
        elif event.button.id == "toggle-replace":
            self._show_replace = not self._show_replace
            row = self.query_one("#replace-row")
            row.display = self._show_replace
            event.button.label = "△" if self._show_replace else "▽"

    def get_search_text(self) -> str:
        return self.query_one("#find-input", Input).value

    def get_replace_text(self) -> str:
        return self.query_one("#replace-input", Input).value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "find-input":
            self.post_message(self.SearchRequested(self.get_search_text()))
