from __future__ import annotations

from pathlib import Path

import pytest

from ced.editor.widget import EnhancedCodeEditor, detect_language

# These tests construct EnhancedCodeEditor without mounting in a Textual app.
# They verify logic that is independent of the UI event loop.


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

    def test_save_as_writes_file(self, tmp_path: Path) -> None:
        dest = tmp_path / "saved.txt"
        editor = EnhancedCodeEditor()
        editor.text = "hello world"
        editor.save_as(dest)
        assert dest.read_text() == "hello world"
        assert editor.file_path == dest

    def test_save_as_updates_language(self, tmp_path: Path) -> None:
        dest = tmp_path / "script.py"
        editor = EnhancedCodeEditor()
        editor.save_as(dest)
        assert editor.language == "python"

    def test_load_file_reads_content(self, tmp_path: Path) -> None:
        src = tmp_path / "hello.py"
        src.write_text("print('hello')")
        editor = EnhancedCodeEditor()
        editor.load_file(src)
        assert editor.text == "print('hello')"
        assert editor.file_path == src
        assert editor.language == "python"

    def test_load_file_clears_history(self, tmp_path: Path) -> None:
        src = tmp_path / "foo.txt"
        src.write_text("data")
        editor = EnhancedCodeEditor()
        editor.text = "old data"
        editor.load_file(src)
        assert editor.text == "data"

    def test_save_file_success(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.txt"
        editor = EnhancedCodeEditor(path=dest)
        editor.text = "saved content"
        result = editor.save_file()
        assert result is True
        assert dest.read_text() == "saved content"

    def test_save_file_updates_modified_flag(self, tmp_path: Path) -> None:
        dest = tmp_path / "flag.txt"
        editor = EnhancedCodeEditor(path=dest)
        editor.text = "data"
        editor.save_file()
        assert editor.file_path == dest

    def test_save_file_creates_parent_dir(self, tmp_path: Path) -> None:
        dest = tmp_path / "newdir" / "nested" / "out.txt"
        editor = EnhancedCodeEditor(path=dest)
        editor.text = "content"
        result = editor.save_file()
        assert result is True
        assert dest.exists()
        assert dest.read_text() == "content"

    def test_save_as_creates_parent_dir(self, tmp_path: Path) -> None:
        dest = tmp_path / "otherdir" / "sub" / "output.txt"
        editor = EnhancedCodeEditor()
        editor.text = "save_as content"
        editor.save_as(dest)
        assert dest.exists()
        assert dest.read_text() == "save_as content"
        assert editor.file_path == dest
