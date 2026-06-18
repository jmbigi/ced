from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static
from textual.widget import Widget


class HelpBar(Widget):
    def __init__(
        self,
        shortcuts: list[tuple[str, str]] | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._shortcuts = shortcuts or [
            ("^Q", "Quit"),
            ("^S", "Save"),
            ("^P", "Open"),
            ("^F", "Search"),
            ("^B", "Sidebar"),
            ("GRV", "OpenCode"),
        ]

    def compose(self) -> ComposeResult:
        yield Static("", id="help-text")

    def on_mount(self) -> None:
        self.render_shortcuts()

    def set_shortcuts(self, shortcuts: list[tuple[str, str]]) -> None:
        self._shortcuts = shortcuts
        self.render_shortcuts()

    def render_shortcuts(self) -> None:
        parts = []
        for key, action in self._shortcuts:
            parts.append(f" {key} {action} ")
        self.query_one("#help-text", Static).update("".join(parts))
