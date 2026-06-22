from __future__ import annotations


from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button


class ConfirmScreen(Screen[bool]):
    """Generic confirmation dialog with Save/Discard/Cancel options."""

    def __init__(
        self,
        message: str,
        title: str = "Confirm",
    ) -> None:
        super().__init__()
        self._message = message
        self._title = title

    def compose(self) -> ComposeResult:
        """Yield the title, message, and action buttons."""
        yield Static(self._title, id="confirm-title")
        yield Static(self._message, id="confirm-message")
        with Static(id="confirm-buttons"):
            yield Button("Save", id="save", variant="primary")
            yield Button("Discard", id="discard", variant="error")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dismiss with the button id as result."""
        self.dismiss(event.button.id)


class QuitConfirmScreen(Screen[str | None]):
    """Quit confirmation showing modified files."""

    def __init__(
        self,
        names: list[str],
    ) -> None:
        super().__init__()
        self._names = names or []

    def compose(self) -> ComposeResult:
        """Yield the quit confirmation UI."""
        yield Static("Unsaved Changes", id="quit-title")
        yield Static("\n".join(f"  • {n}" for n in self._names))
        yield Static("Save changes before quitting?", id="quit-question")
        with Static(id="quit-buttons"):
            yield Button("Save All", id="save", variant="primary")
            yield Button("Discard", id="discard", variant="error")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dismiss with save/discard/cancel."""
        self.dismiss(event.button.id)
