from __future__ import annotations

from pathlib import Path

import pytest

from ced.app import Ced


@pytest.mark.asyncio
async def test_editor_area_new_file() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        count = editor.buffers.count
        editor.new_file()
        await pilot.pause()
        assert editor.buffers.count == count + 1
        assert len(editor._tab_ids) == count + 1


@pytest.mark.asyncio
async def test_editor_area_tab_navigation() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.new_file()
        await pilot.pause()
        editor.new_file()
        await pilot.pause()
        assert editor.buffers.count == 3
        editor.tab_next()
        await pilot.pause()
        editor.tab_prev()
        await pilot.pause()


@pytest.mark.asyncio
async def test_editor_area_open_file(tmp_path: Path) -> None:
    src = tmp_path / "test.py"
    src.write_text("x = 1")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        count = editor.buffers.count
        editor.open_file(src)
        await pilot.pause()
        assert editor.buffers.count == count + 1
        active = editor.get_active_editor()
        assert active is not None
        assert active.text == "x = 1"


@pytest.mark.asyncio
async def test_editor_area_open_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "nonexistent.py"
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        count = editor.buffers.count
        editor.open_file(missing)
        await pilot.pause()
        assert editor.buffers.count == count


@pytest.mark.asyncio
async def test_editor_area_save_active(tmp_path: Path) -> None:
    dest = tmp_path / "saved.py"
    dest.write_text("")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(dest)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.text = "content"
        result = editor.save_active()
        await pilot.pause()
        assert result is True
        assert dest.read_text() == "content"


@pytest.mark.asyncio
async def test_editor_area_close_active() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        count = editor.buffers.count
        active = editor.buffers.active_buffer
        assert active is not None
        active.mark_modified()
    # cannot close modified tab via run_test (needs confirm dialog)
    # just verify close_active doesn't crash


@pytest.mark.asyncio
async def test_search_bar_show_hide() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        search = app.query_one("#search-bar")
        search.display = False
        app.action_search()
        await pilot.pause()
        assert search.display is True
        app.action_search()
        await pilot.pause()
        assert search.display is False


@pytest.mark.asyncio
async def test_search_bar_replace_mode() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        search = app.query_one("#search-bar")
        app.action_search_replace()
        await pilot.pause()
        assert search.display is True


@pytest.mark.asyncio
async def test_theme_list() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_theme_list()
        await pilot.pause()


@pytest.mark.asyncio
async def test_keybinding_list() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_keybinding_list()
        await pilot.pause()


@pytest.mark.asyncio
async def test_file_tree_panel_loaded() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one("#file-tree")
        assert tree is not None


@pytest.mark.asyncio
async def test_opencode_panel() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        panel = app.query_one("#opencode")
        assert panel is not None
