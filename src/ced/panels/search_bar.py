from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Input, Button
from textual.widget import Widget
from textual.containers import Horizontal


class SearchBar(Widget):
    """Find and Replace widget with toggleable replace UI."""

    DEFAULT_CSS = """
    SearchBar {
        height: auto;
        border: solid $primary;
        background: $surface;
        display: none;
    }

    SearchBar Input {
        width: 1fr;
    }

    #replace-row {
        height: auto;
    }
    """

    class SearchRequested(Message):
        """Posted when the user submits a search query."""

        def __init__(self, query: str, find_text: str = "") -> None:
            super().__init__()
            self.query = query

    class ReplaceRequested(Message):
        """Posted when the user requests a replacement."""

        def __init__(
            self, find: str, replace: str, all: bool = False
        ) -> None:
            super().__init__()
            self.find = find
            self.replace = replace
            self.all = all

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._show_replace = False

    def compose(self) -> ComposeResult:
        """Yield the find and replace UI rows."""
        with Horizontal():
            yield Input(placeholder="Find...", id="find-input")
            yield Button("X", id="close-search", variant="error")
            yield Button("Aa", id="toggle-replace")
        with Horizontal(id="replace-row"):
            yield Input(placeholder="Replace...", id="replace-input")
            yield Button("Replace", id="replace-btn")
            yield Button("All", id="replace-all-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle search bar button clicks."""
        bid = event.button.id
        if bid == "close-search":
            self.display = False
        elif bid == "toggle-replace":
            self._show_replace = not self._show_replace
            self.query_one("#replace-row").display = self._show_replace
        elif bid == "replace-btn":
            self.post_message(
                self.ReplaceRequested(
                    self.get_search_text(),
                    self.get_replace_text(),
                    all=False,
                )
            )
        elif bid == "replace-all-btn":
            self.post_message(
                self.ReplaceRequested(
                    self.get_search_text(),
                    self.get_replace_text(),
                    all=True,
                )
            )

    def show_replace_ui(self, show: bool) -> None:
        """Toggle the replace row visibility."""
        self._show_replace = show
        self.query_one("#replace-row").display = show

    def get_search_text(self) -> str:
        """Return the current search query."""
        return self.query_one("#find-input", Input).value

    def get_replace_text(self) -> str:
        """Return the current replace text."""
        return self.query_one("#replace-input", Input).value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Post a search request when the user presses Enter."""
        if event.input.id == "find-input":
            self.post_message(
                self.SearchRequested(self.get_search_text())
            )
