from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from unittest.mock import patch

from ced.editor.buffer import Buffer, BufferManager
from ced.panels.editor_area import EditorArea
from ced.panels.search_bar import SearchBar
from ced.commands.registry import Command, CommandRegistry


class TestBufferEdgeCases:
    def test_buffer_repr_modified(self) -> None:
        b = Buffer(Path("f.py"))
        b.mark_modified()
        assert "modified=True" in repr(b)

    def test_buffer_repr_unmodified(self) -> None:
        b = Buffer()
        assert "modified=False" in repr(b)

    def test_buffer_manager_remove_before_active(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        assert bm.active_index == 2
        bm.remove(0)
        assert bm.active_index == 1

    def test_buffer_manager_remove_after_active(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        bm.active_index = 0
        bm.remove(2)
        assert bm.active_index == 0

    def test_buffer_manager_remove_active(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        bm.active_index = 1
        bm.remove(1)
        assert bm.count == 2
        assert bm.active_index == 1

    def test_buffer_manager_remove_out_of_range(self) -> None:
        bm = BufferManager()
        bm.add()
        bm.remove(99)
        assert bm.count == 1

    def test_buffer_manager_get_by_path_resolved(self) -> None:
        bm = BufferManager()
        bm.open(Path("/a/b.py"))
        found = bm.get_by_path(Path("/a/b.py"))
        assert found is not None
        assert found.name == "b.py"

    def test_buffer_dot_name(self) -> None:
        b = Buffer(Path("file.with.dots.py"))
        assert b.name == "file.with.dots.py"


class TestCommandEdgeCases:
    def test_command_registry_get_nonexistent(self) -> None:
        reg = CommandRegistry()
        assert reg.get("nonexistent") is None

    def test_command_registry_execute_with_kwargs(self) -> None:
        reg = CommandRegistry()
        result = {}

        def handler(**kwargs: str) -> None:
            result.update(kwargs)

        reg.register(Command("app.test", "Test", handler, "Test"))
        reg.execute("app.test", key="value")
        assert result.get("key") == "value"

    def test_command_registry_search_returns_multiple(self) -> None:
        reg = CommandRegistry()
        reg.register(Command("app.save", "Save file", lambda: None, "File"))
        reg.register(Command("app.save_as", "Save as", lambda: None, "File"))
        results = reg.search("save")
        assert len(results) >= 2

    def test_command_registry_search_sorted(self) -> None:
        reg = CommandRegistry()
        reg.register(Command("app.xxx_save", "Save data", lambda: None, "File"))
        reg.register(Command("app.save", "Save", lambda: None, "File"))
        results = reg.search("save")
        assert results[0][0].id == "app.save"


class TestEditorAreaEdgeCases:
    def test_unique_name_first_call(self) -> None:
        ea = EditorArea()
        assert ea._unique_name("test.py") == "test.py"

    def test_unique_name_second_call(self) -> None:
        ea = EditorArea()
        ea._tab_ids.append("tab_test_py")
        result = ea._unique_name("test.py")
        assert result.startswith("test.py_")

    def test_sanitize_id_special_chars(self) -> None:
        ea = EditorArea()
        assert ea._sanitize_id("a.b.c") == "a_b_c"
        assert ea._sanitize_id("hello world!") == "hello_world_"
        assert ea._sanitize_id("___") == "___"
        assert ea._sanitize_id("") == ""


class TestSearchBarEdgeCases:
    def test_search_requested_message(self) -> None:
        msg = SearchBar.SearchRequested("find me")
        assert msg.query == "find me"

    def test_replace_requested_message(self) -> None:
        msg = SearchBar.ReplaceRequested("find", "repl", all=True)
        assert msg.find == "find"
        assert msg.replace == "repl"
        assert msg.all is True

    def test_replace_requested_single(self) -> None:
        msg = SearchBar.ReplaceRequested("a", "b", all=False)
        assert msg.all is False


class TestMainModule:
    def test_main_name_block(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", "import ced.__main__; print('ok')"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "ok" in result.stdout

    def test_main_name_block_import(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", "import ced.__main__ as m; assert callable(m.main)"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0


class TestDetectDarkModeWinreg:
    def test_winreg_success_dark(self) -> None:
        """Windows registry path returns 0 (dark mode)."""
        from ced.themes.manager import detect_dark_mode

        class FakeWinreg:
            HKEY_CURRENT_USER = object()

            @staticmethod
            def OpenKey(*args):
                return "fake_key"

            @staticmethod
            def QueryValueEx(key, name):
                return (0, 1)

        with patch("os.name", "nt"):
            with patch.dict("sys.modules", {"winreg": FakeWinreg}):
                result = detect_dark_mode()
                assert result is True

    def test_winreg_success_light(self) -> None:
        """Windows registry path returns 1 (light mode)."""
        from ced.themes.manager import detect_dark_mode

        class FakeWinreg:
            HKEY_CURRENT_USER = object()

            @staticmethod
            def OpenKey(*args):
                return "fake_key"

            @staticmethod
            def QueryValueEx(key, name):
                return (1, 1)

        with patch("os.name", "nt"):
            with patch.dict("sys.modules", {"winreg": FakeWinreg}):
                result = detect_dark_mode()
                assert result is False
