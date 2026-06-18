from __future__ import annotations

from pathlib import Path

from textual.message import Message
from textual.widgets import DirectoryTree


class FileTreePanel(DirectoryTree):
    def __init__(
        self,
        path: Path | str | None = None,
        *args,
        **kwargs,
    ) -> None:
        self._base_path = Path(path) if path else Path.cwd()
        super().__init__(self._base_path.as_posix(), *args, **kwargs)

    def on_mount(self) -> None:
        self.loading = False

    def refresh_tree(self, path: Path | None = None) -> None:
        self.path = (path or self._base_path).as_posix()
        self.reload()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        event.stop()
        path = Path(event.path)
        if path.is_file():
            self.post_message(self.FileOpened(path))

    class FileOpened(Message):
        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path
