from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical


class CommandPalette(ModalScreen[str | None]):
    """Modal command palette with fuzzy filtering of registered commands."""

    DEFAULT_CSS = """
    CommandPalette {
        align: center middle;
    }

    CommandPalette > Vertical {
        width: 60;
        height: 60%;
        border: thick $primary;
        background: $surface;
    }

    CommandPalette Input {
        dock: top;
        margin: 1;
    }

    CommandPalette ListView {
        height: 1fr;
        margin: 0 1 1 1;
    }

    CommandPalette .command-category {
        color: $text-muted;
        margin-left: 1;
    }
    """

    def __init__(
        self, commands: list[tuple[str, str, str]]
    ) -> None:
        super().__init__()
        self._all_commands = commands
        self._filtered = commands

    def compose(self) -> ComposeResult:
        """Yield the command input and results list."""
        with Vertical():
            yield Input(placeholder="Type a command...", id="palette-input")
            yield ListView(id="palette-list")

    def on_mount(self) -> None:
        """Populate the list and focus the input."""
        self._populate(self._all_commands)
        self.query_one("#palette-input", Input).focus()

    def _populate(self, commands: list[tuple[str, str, str]]) -> None:
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()
        for cmd_id, desc, cat in commands:
            item = ListItem(
                Label(f"{cmd_id}  {desc}"),
                Label(cat, classes="command-category"),
            )
            list_view.append(item)
        self._filtered = commands
        if commands:
            list_view.index = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as the user types."""
        query = event.value.lower()
        if not query:
            self._populate(self._all_commands)
            return
        filtered = [
            (cid, desc, cat)
            for cid, desc, cat in self._all_commands
            if query in cid.lower()
            or query in desc.lower()
            or query in cat.lower()
        ]
        self._populate(filtered)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Dismiss with the selected command id."""
        list_view = self.query_one("#palette-list", ListView)
        idx = list_view.index
        if idx is not None and 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx][0])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Dismiss with the currently highlighted command."""
        list_view = self.query_one("#palette-list", ListView)
        idx = list_view.index
        if idx is not None and 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx][0])

    def key_escape(self) -> None:
        """Dismiss without selecting a command."""
        self.dismiss(None)
