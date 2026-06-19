from __future__ import annotations

from pathlib import Path

from ced.panels.file_tree import FileTreePanel


class TestFileTreePanel:
    def test_refresh_tree_method(self) -> None:
        panel = FileTreePanel(path=Path("/tmp"))
        assert hasattr(panel, "refresh_tree")
        assert callable(panel.refresh_tree)

    def test_default_path_is_cwd(self) -> None:
        panel = FileTreePanel()
        assert panel._base_path == Path.cwd()


class TestFileOpened:
    def test_file_opened_message(self) -> None:
        msg = FileTreePanel.FileOpened(Path("/a/b.py"))
        assert msg.path == Path("/a/b.py")

    def test_file_opened_message_is_file(self) -> None:
        msg = FileTreePanel.FileOpened(Path("/x/y/z.txt"))
        assert isinstance(msg.path, Path)
        assert msg.path.suffix == ".txt"
