from __future__ import annotations

from pathlib import Path

from textual.message import Message
from textual.widgets import DirectoryTree


class FileTreePanel(DirectoryTree):
    """Sidebar file tree that emits FileOpened when a file is selected."""

    def __init__(
        self,
        path: Path | str | None = None,
        *args,
        **kwargs,
    ) -> None:
        self._base_path = Path(path) if path else Path.cwd()
        super().__init__(self._base_path.as_posix(), *args, **kwargs)

    def on_mount(self) -> None:
        """Disable loading indicator after mount."""
        self.loading = False

    def refresh_tree(self, path: Path | None = None) -> None:
        """Reload the directory tree, optionally at a new path."""
        self.path = (path or self._base_path).as_posix()
        self.reload()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Post a FileOpened message when a file node is selected."""
        event.stop()
        path = Path(event.path)
        if not path.exists():
            return
        if path.is_file():
            self.post_message(self.FileOpened(path))

    class FileOpened(Message):
        """Posted when a file is selected in the tree."""

        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path
