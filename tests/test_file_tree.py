from __future__ import annotations

from pathlib import Path

from ced.panels.file_tree import FileTreePanel


class TestFileTreePanel:
    def test_refresh_tree_method(self) -> None:
        panel = FileTreePanel(path=Path("/tmp"))
        assert hasattr(panel, "refresh_tree")
        assert callable(panel.refresh_tree)
