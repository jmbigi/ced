from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical


class QuickOpen(ModalScreen[Path | None]):
    DEFAULT_CSS = """
    QuickOpen {
        align: center middle;
    }

    QuickOpen > Vertical {
        width: 60;
        height: 60%;
        border: thick $primary;
        background: $surface;
    }

    QuickOpen Input {
        dock: top;
        margin: 1;
    }

    QuickOpen ListView {
        height: 1fr;
        margin: 0 1 1 1;
    }

    QuickOpen ListItem {
        padding: 0 1;
    }

    QuickOpen .file-path {
        color: $text-muted;
    }
    """

    def __init__(self, root_path: Path) -> None:
        super().__init__()
        self._root = root_path
        self._all_files: list[Path] = []
        self._filtered: list[Path] = []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Type to search files...", id="quick-input")
            yield ListView(id="quick-list")

    def on_mount(self) -> None:
        self._scan_files()
        self._populate(self._all_files)
        self.query_one("#quick-input", Input).focus()

    def _scan_files(self) -> None:
        import os

        excluded = {".venv", "__pycache__", ".git", "node_modules", ".ced"}
        for dirpath, dirnames, filenames in os.walk(self._root):
            dirnames[:] = [d for d in dirnames if d not in excluded]
            for fn in filenames:
                full = Path(dirpath) / fn
                try:
                    if full.is_file():
                        self._all_files.append(full)
                except (PermissionError, OSError):
                    pass

    def _populate(self, files: list[Path]) -> None:
        list_view = self.query_one("#quick-list", ListView)
        list_view.clear()
        for fp in files:
            try:
                rel = fp.relative_to(self._root)
            except ValueError:
                rel = fp
            item = ListItem(
                Label(fp.name),
                Label(str(rel), classes="file-path"),
            )
            list_view.append(item)
        self._filtered = list(files)
        if files:
            list_view.index = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        if not query:
            self._populate(self._all_files)
            return
        filtered = [
            f
            for f in self._all_files
            if query in f.name.lower() or query in str(f).lower()
        ]
        self._populate(filtered)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        list_view = self.query_one("#quick-list", ListView)
        idx = list_view.index
        if idx is not None and 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        list_view = self.query_one("#quick-list", ListView)
        idx = list_view.index
        if idx is not None and 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx])

    def key_escape(self) -> None:
        self.dismiss(None)
