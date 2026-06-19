from __future__ import annotations

from ced.panels.editor_area import EditorSettings


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
