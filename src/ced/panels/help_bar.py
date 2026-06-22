from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static
from textual.widget import Widget


class HelpBar(Widget):
    """Bottom status bar displaying active keyboard shortcuts."""

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
        """Yield the help text widget."""
        yield Static("", id="help-text")

    def on_mount(self) -> None:
        """Render shortcuts on mount."""
        self.render_shortcuts()

    def set_shortcuts(self, shortcuts: list[tuple[str, str]]) -> None:
        """Update the displayed shortcuts and re-render."""
        self._shortcuts = shortcuts
        self.render_shortcuts()

    def render_shortcuts(self) -> None:
        """Build and update the help text from current shortcuts."""
        parts = []
        for key, action in self._shortcuts:
            parts.append(f" {key} {action} ")
        self.query_one("#help-text", Static).update("".join(parts))
