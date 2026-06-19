from __future__ import annotations

from ced.panels.editor_area import EditorArea, EditorSettings


class TestEditorSettings:
    def test_defaults(self) -> None:
        s = EditorSettings()
        assert s.show_line_numbers is True
        assert s.soft_wrap is False
        assert s.indent_width == 4

    def test_custom_values(self) -> None:
        s = EditorSettings(show_line_numbers=False, soft_wrap=True, indent_width=2)
        assert s.show_line_numbers is False
        assert s.soft_wrap is True
        assert s.indent_width == 2


class TestEditorArea:
    def test_sanitize_id(self) -> None:
        editor = EditorArea()
        assert editor._sanitize_id("test.py") == "test_py"
        assert editor._sanitize_id("hello world") == "hello_world"
        assert editor._sanitize_id("file.name.ext") == "file_name_ext"
        assert editor._sanitize_id("simple") == "simple"
        assert editor._sanitize_id("123abc") == "123abc"

    def test_tab_id_sanitized(self) -> None:
        editor = EditorArea()
        assert editor._tab_id("test.py") == "tab_test_py"

    def test_editor_id_sanitized(self) -> None:
        editor = EditorArea()
        assert editor._editor_id("test.py") == "editor_test_py"
