from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical


class CommandPalette(ModalScreen[str | None]):
    DEFAULT_CSS = """
    CommandPalette {
        align: center middle;
    }

    CommandPalette > Vertical {
        width: 60;
        height: 70%;
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

    CommandPalette ListItem {
        padding: 0 1;
    }

    CommandPalette ListItem > Label {
        width: 1fr;
    }

    CommandPalette .command-id {
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, commands: list[tuple[str, str, str]]) -> None:
        super().__init__()
        self._all_commands = commands
        self._filtered: list[tuple[str, str, str]] = list(commands)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Type a command...", id="palette-input")
            yield ListView(id="palette-list")

    def on_mount(self) -> None:
        self._populate(self._all_commands)
        self.query_one("#palette-input", Input).focus()

    def _populate(self, commands: list[tuple[str, str, str]]) -> None:
        list_view = self.query_one("#palette-list", ListView)
        list_view.clear()
        for cmd_id, cmd_name, cmd_category in commands:
            item = ListItem(
                Label(f"[bold]{cmd_name}[/bold]"),
                Label(f"[dim]{cmd_category}[/dim]  {cmd_id}", classes="command-id"),
            )
            list_view.append(item)
        if commands:
            list_view.index = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        if not query:
            self._populate(self._all_commands)
            return
        filtered = [
            c
            for c in self._all_commands
            if query in c[0].lower() or query in c[1].lower()
        ]
        self._populate(filtered)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item:
            index = self.query_one("#palette-list", ListView).index
            if index is not None and 0 <= index < len(self._filtered):
                self.dismiss(self._filtered[index][0])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        list_view = self.query_one("#palette-list", ListView)
        if list_view.index is not None and 0 <= list_view.index < len(self._filtered):
            self.dismiss(self._filtered[list_view.index][0])
