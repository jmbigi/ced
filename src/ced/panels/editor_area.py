from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import TabbedContent, TabPane
from textual.widget import Widget

from ced.editor.widget import EnhancedCodeEditor
from ced.editor.buffer import BufferManager


class EditorArea(Widget):
    class OpenedFile(Message):
        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    class FileSaved(Message):
        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.buffers = BufferManager()
        self._editors: dict[str, EnhancedCodeEditor] = {}
        self._open_tabs: set[str] = set()

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="tab_untitled"):
            with TabPane("untitled", id="tab_untitled"):
                yield EnhancedCodeEditor(id="editor_untitled")

    def on_mount(self) -> None:
        self._editors["untitled"] = self.query_one(
            "#editor_untitled", EnhancedCodeEditor
        )
        self._open_tabs.add("tab_untitled")
        self.buffers.add()

    def _tab_id(self, name: str) -> str:
        return f"tab_{name}"

    def _editor_id(self, name: str) -> str:
        return f"editor_{name}"

    def open_file(self, path: Path) -> None:
        name = path.name
        tab_id = self._tab_id(name)
        editor_id = self._editor_id(name)

        tabs = self.query_one(TabbedContent)

        if tab_id in self._open_tabs:
            tabs.active = tab_id
            return

        self.buffers.open(path)
        try:
            editor = EnhancedCodeEditor(path=path, id=editor_id)
            editor.load_file(path)
        except (PermissionError, FileNotFoundError) as exc:
            self.notify(f"Cannot open {path.name}: {exc}", severity="error", timeout=5)
            self.buffers.close_active()
            return

        pane = TabPane(name, id=tab_id)
        pane.compose_add_child(editor)
        tabs.add_pane(pane)
        tabs.active = tab_id
        self._editors[name] = editor
        self._open_tabs.add(tab_id)

    def get_active_editor(self) -> EnhancedCodeEditor | None:
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        if active and active != "":
            name = active.removeprefix("tab_")
            editor_id = self._editor_id(name)
            try:
                return self.query_one(f"#{editor_id}", EnhancedCodeEditor)
            except Exception:
                return None
        return None

    def get_editor_paths(self) -> list[tuple[str, str]]:
        result = []
        for tab_id in self._open_tabs:
            name = tab_id.removeprefix("tab_")
            if name == "untitled":
                result.append((tab_id, "untitled"))
            else:
                result.append((tab_id, name))
        return result

    def save_active(self) -> bool:
        editor = self.get_active_editor()
        if editor and editor.file_path:
            result = editor.save_file()
            if result:
                self.post_message(self.FileSaved(editor.file_path))
            return result
        return False

    def close_active(self) -> None:
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        if active in ("", "tab_untitled", None):
            return
        tabs.remove_pane(active)
        self._open_tabs.discard(active)
        self.buffers.close_active()
