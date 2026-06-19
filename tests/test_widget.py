from __future__ import annotations

from pathlib import Path

import pytest

from ced.editor.widget import EnhancedCodeEditor, detect_language


class TestEnhancedCodeEditor:
    def test_default_constructor(self) -> None:
        editor = EnhancedCodeEditor()
        assert editor.file_path is None

    def test_constructor_with_path(self) -> None:
        editor = EnhancedCodeEditor(path=Path("/tmp/test.py"))
        assert editor.file_path == Path("/tmp/test.py")

    def test_constructor_with_path_string(self) -> None:
        editor = EnhancedCodeEditor(path="/tmp/test.py")
        assert editor.file_path == Path("/tmp/test.py")

    def test_save_file_no_path(self) -> None:
        editor = EnhancedCodeEditor()
        assert editor.save_file() is False

    def test_file_path_setter(self) -> None:
        editor = EnhancedCodeEditor()
        editor.file_path = "/tmp/foo.py"
        assert editor.file_path == Path("/tmp/foo.py")

    def test_file_path_setter_none(self) -> None:
        editor = EnhancedCodeEditor(path="/tmp/foo.py")
        editor.file_path = None
        assert editor.file_path is None

    def test_save_file_error(self) -> None:
        editor = EnhancedCodeEditor(path=Path("/nonexistent/dir/file.txt"))
        editor.text = "hello"
        with pytest.raises(OSError):
            editor.save_file()

    def test_detect_language_python(self) -> None:
        assert detect_language(Path("test.py")) == "python"

    def test_detect_language_none(self) -> None:
        assert detect_language(None) is None

    def test_detect_language_no_ext(self) -> None:
        assert detect_language(Path("Makefile")) is None

    def test_language_detected_on_constructor(self) -> None:
        editor = EnhancedCodeEditor(path=Path("main.py"))
        assert editor.language == "python"

    def test_file_path_setter_updates_language(self) -> None:
        editor = EnhancedCodeEditor(path=Path("main.py"))
        assert editor.language == "python"
        editor.file_path = Path("main.rs")
        assert editor.language == "rust"

    def test_file_path_setter_none_keeps_language(self) -> None:
        editor = EnhancedCodeEditor(path=Path("main.py"))
        assert editor.language == "python"
        editor.file_path = None
        assert editor.language == "python"

    def test_indent_width_default(self) -> None:
        editor = EnhancedCodeEditor()
        assert editor.indent_width == 4

    def test_indent_width_custom(self) -> None:
        editor = EnhancedCodeEditor(indent_width=2)
        assert editor.indent_width == 2
