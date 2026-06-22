from __future__ import annotations

import os
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical


class QuickOpen(ModalScreen[Path | None]):
    """Modal file finder with fuzzy search via os.walk in a thread worker."""

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
        """Yield the search input and results list."""
        with Vertical():
            yield Input(placeholder="Type to search files...", id="quick-input")
            yield ListView(id="quick-list")

    def on_mount(self) -> None:
        """Start scanning and focus the input."""
        self._scan_files()
        self.query_one("#quick-input", Input).focus()

    def _scan_files_inner(self) -> list[Path]:
        excluded = {".venv", "__pycache__", ".git", "node_modules", ".ced"}
        max_depth = 15
        files: list[Path] = []
        root_str = str(self._root)
        for dirpath, dirnames, filenames in os.walk(self._root):
            depth = dirpath[len(root_str):].count(os.sep)
            if depth >= max_depth:
                dirnames.clear()
                continue
            dirnames[:] = [d for d in dirnames if d not in excluded]
            for fn in filenames:
                full = Path(dirpath) / fn
                try:
                    if full.is_file():
                        files.append(full)
                except (PermissionError, OSError):
                    pass
        return files

    @work(thread=True, exclusive=True)
    def _scan_files(self) -> None:
        """Scan files in a background thread."""
        files = self._scan_files_inner()
        self.app.call_from_thread(self._on_files_scanned, files)

    def _on_files_scanned(self, files: list[Path]) -> None:
        self._all_files = files
        self._populate(files)

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
        """Filter the file list as the user types."""
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
        """Dismiss with the selected file path."""
        list_view = self.query_one("#quick-list", ListView)
        idx = list_view.index
        if idx is not None and 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Dismiss with the currently highlighted file."""
        list_view = self.query_one("#quick-list", ListView)
        idx = list_view.index
        if idx is not None and 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx])

    def key_escape(self) -> None:
        """Dismiss without selecting a file."""
        self.dismiss(None)
