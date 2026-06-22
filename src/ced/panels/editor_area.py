from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import TabbedContent, TabPane
from textual.widget import Widget

from ced.editor.widget import EnhancedCodeEditor
from ced.editor.buffer import BufferManager

MAX_TABS = 100


@dataclass
class EditorSettings:
    """Settings for the editor area: line numbers, wrapping, indentation."""

    show_line_numbers: bool = True
    soft_wrap: bool = False
    indent_width: int = 4


class EditorArea(Widget):
    """Multi-tab editor area managing tabs, editors, and buffers."""

    def __init__(
        self, editor_settings: EditorSettings | None = None, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._editor_settings = editor_settings or EditorSettings()
        self.buffers = BufferManager()
        self._editors: dict[str, EnhancedCodeEditor] = {}
        self._tab_ids: list[str] = []
        self._tab_counter = 0

    def compose(self) -> ComposeResult:
        """Yield the initial untitled tab."""
        with TabbedContent(initial="tab_untitled"):
            with TabPane("untitled", id="tab_untitled"):
                yield EnhancedCodeEditor(
                    id="editor_untitled",
                    show_line_numbers=self._editor_settings.show_line_numbers,
                    soft_wrap=self._editor_settings.soft_wrap,
                    indent_width=self._editor_settings.indent_width,
                )

    def on_mount(self) -> None:
        """Register the initial editor and buffer."""
        self._editors["untitled"] = self.query_one(
            "#editor_untitled", EnhancedCodeEditor
        )
        self._tab_ids.append("tab_untitled")
        self.buffers.add()

    def _unique_name(self, base: str) -> str:
        if self._tab_id(base) not in self._tab_ids:
            return base
        self._tab_counter += 1
        return f"{base}_{self._tab_counter}"

    def _sanitize_id(self, name: str) -> str:
        return "".join(c if c.isalnum() or c == "_" else "_" for c in name)

    def _tab_id(self, name: str) -> str:
        return f"tab_{self._sanitize_id(name)}"

    def _editor_id(self, name: str) -> str:
        return f"editor_{self._sanitize_id(name)}"

    def new_file(self) -> None:
        """Create a new untitled tab."""
        if len(self._tab_ids) >= MAX_TABS:
            self.notify("Maximum tabs reached", severity="warning", timeout=3)
            return
        self._tab_counter += 1
        name = f"untitled_{self._tab_counter}"
        safe_key = self._sanitize_id(name)
        tab_id = self._tab_id(name)
        editor_id = self._editor_id(name)
        tabs = self.query_one(TabbedContent)
        self.buffers.add()
        editor = EnhancedCodeEditor(
            id=editor_id,
            show_line_numbers=self._editor_settings.show_line_numbers,
            soft_wrap=self._editor_settings.soft_wrap,
            indent_width=self._editor_settings.indent_width,
        )
        pane = TabPane(name, id=tab_id)
        pane.compose_add_child(editor)
        tabs.add_pane(pane)
        tabs.active = tab_id
        self._editors[safe_key] = editor
        self._tab_ids.append(tab_id)
        editor.focus()

    def open_file(self, path: Path | str) -> None:
        """Open a file in a new or existing tab."""
        if isinstance(path, str):
            path = Path(path)
        if len(self._tab_ids) >= MAX_TABS:
            self.notify("Maximum tabs reached", severity="warning", timeout=3)
            return
        existing = self.buffers.get_by_path(path)
        if existing is not None:
            idx = next(
                i for i in range(self.buffers.count) if self.buffers[i] is existing
            )
            if 0 <= idx < len(self._tab_ids):
                self.query_one(TabbedContent).active = self._tab_ids[idx]
            return

        name = path.name
        unique = self._unique_name(name)
        safe_key = self._sanitize_id(unique)
        tab_id = self._tab_id(unique)
        editor_id = self._editor_id(unique)

        tabs = self.query_one(TabbedContent)
        self.buffers.open(path)
        try:
            editor = EnhancedCodeEditor(
                path=path,
                id=editor_id,
                show_line_numbers=self._editor_settings.show_line_numbers,
                soft_wrap=self._editor_settings.soft_wrap,
                indent_width=self._editor_settings.indent_width,
            )
            editor.load_file(path)
        except (PermissionError, FileNotFoundError) as exc:
            self.notify(f"Cannot open {path.name}: {exc}", severity="error", timeout=5)
            self.buffers.close_active()
            return

        pane = TabPane(name, id=tab_id)
        pane.compose_add_child(editor)
        tabs.add_pane(pane)
        tabs.active = tab_id
        self._editors[safe_key] = editor
        self._tab_ids.append(tab_id)
        editor.focus()

    def get_active_editor(self) -> EnhancedCodeEditor | None:
        """Return the editor widget in the active tab, or None."""
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        if not active:
            return None
        name = active.removeprefix("tab_")
        return self._editors.get(name)

    def _sync_buffer_index(self) -> None:
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        if active in self._tab_ids:
            idx = self._tab_ids.index(active)
            if idx < self.buffers.count:
                self.buffers.active_index = idx

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        """Sync buffer index when the user switches tabs."""
        event.stop()
        self._sync_buffer_index()

    def tab_next(self) -> None:
        """Switch to the next tab."""
        if not self._tab_ids:
            return
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        try:
            i = self._tab_ids.index(active)
        except ValueError:
            i = -1
        next_idx = (i + 1) % len(self._tab_ids)
        tabs.active = self._tab_ids[next_idx]

    def tab_prev(self) -> None:
        """Switch to the previous tab."""
        if not self._tab_ids:
            return
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        try:
            i = self._tab_ids.index(active)
        except ValueError:
            i = 0
        prev_idx = (i - 1) % len(self._tab_ids)
        tabs.active = self._tab_ids[prev_idx]

    def save_all_modified(self) -> None:
        """Save all modified buffers that have an associated file path."""
        for i, buf in enumerate(self.buffers):
            if buf.is_modified and i < len(self._tab_ids):
                name = self._tab_ids[i].removeprefix("tab_")
                ed = self._editors.get(name)
                if ed and ed.file_path:
                    try:
                        ed.save_file()
                        buf.mark_saved()
                    except OSError:
                        pass

    def save_active(self) -> bool:
        """Save the active buffer. Returns True on success."""
        editor = self.get_active_editor()
        if not editor or not editor.file_path:
            return False
        try:
            result = editor.save_file()
        except OSError as exc:
            self.notify(f"Cannot save: {exc}", severity="error", timeout=5)
            return False
        if result:
            self._sync_buffer_index()
            buf = self.buffers.active_buffer
            if buf:
                buf.mark_saved()
        return result

    def close_active(self) -> None:
        """Close the active tab (or reset it if it's the last one)."""
        tabs = self.query_one(TabbedContent)
        active = tabs.active
        if active in ("", None):
            return
        name = active.removeprefix("tab_")
        if len(self._tab_ids) <= 1:
            editor = self._editors.get(name)
            if editor:
                editor.text = ""
            buf = self.buffers.active_buffer
            if buf:
                buf.mark_saved()
            return
        self.buffers.close_active()
        tabs.remove_pane(active)
        self._tab_ids.remove(active)
        self._editors.pop(name, None)

    def on_text_area_changed(self, event: EnhancedCodeEditor.Changed) -> None:
        """Mark the buffer as modified when the editor content changes."""
        event.stop()
        self._sync_buffer_index()
        buf = self.buffers.active_buffer
        if buf and not buf.is_modified:
            buf.mark_modified()
