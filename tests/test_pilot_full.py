from __future__ import annotations

from pathlib import Path

import pytest

from ced.app import Ced


@pytest.mark.asyncio
async def test_pilot_theme_cycle() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        before = app.config.theme.name
        app.action_theme_next()
        await pilot.pause()
        assert app.config.theme.name != before
        assert app.config.theme.name in (
            "monokai",
            "dracula",
            "nord",
            "catppuccin",
            "github-dark",
            "solarized-dark",
        )


@pytest.mark.asyncio
async def test_pilot_theme_list() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_theme_list()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_search_toggle() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        s = app.query_one("#search-bar")
        s.display = False
        app.action_search()
        await pilot.pause()
        assert s.display is True
        app.action_search()
        await pilot.pause()
        assert s.display is False


@pytest.mark.asyncio
async def test_pilot_search_replace() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        s = app.query_one("#search-bar")
        app.action_search_replace()
        await pilot.pause()
        assert s.display is True


@pytest.mark.asyncio
async def test_pilot_open_file() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_open_file()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_new_file() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        c = editor.buffers.count
        app.action_new_file()
        await pilot.pause()
        assert editor.buffers.count == c + 1


@pytest.mark.asyncio
async def test_pilot_save_untitled() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_save()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_save_file(tmp_path: Path) -> None:
    dest = tmp_path / "save_me.py"
    dest.write_text("")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(dest)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.text = "saved"
        assert editor.save_active() is True
        assert dest.read_text() == "saved"


@pytest.mark.asyncio
async def test_pilot_jump_mode() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_jump_mode()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_command_palette() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_command_palette()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_quick_open() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_quick_open()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_toggle_sidebar() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        sb = app.query_one("#sidebar")
        v = sb.display
        app.action_toggle_sidebar()
        assert sb.display != v


@pytest.mark.asyncio
async def test_pilot_toggle_opencode() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        oc = app.query_one("#opencode-panel")
        v = oc.display
        app.action_toggle_opencode()
        assert oc.display != v


@pytest.mark.asyncio
async def test_pilot_tab_navigation() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.new_file()
        await pilot.pause()
        editor.new_file()
        await pilot.pause()
        assert editor.buffers.count >= 2
        editor.tab_next()
        await pilot.pause()
        editor.tab_prev()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_help_action() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_help()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_keybinding_list() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_keybinding_list()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_search_request(tmp_path: Path) -> None:
    src = tmp_path / "findme.py"
    src.write_text("hello world\nfoo bar\n")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        # Fire search event
        from ced.panels.search_bar import SearchBar

        msg = SearchBar.SearchRequested("hello")
        app.on_search_bar_search_requested(msg)
        await pilot.pause()
        assert active.cursor_location is not None


@pytest.mark.asyncio
async def test_pilot_replace_request(tmp_path: Path) -> None:
    src = tmp_path / "replace_me.py"
    src.write_text("foo foo foo")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        from ced.panels.search_bar import SearchBar

        msg = SearchBar.ReplaceRequested("foo", "bar", all=False)
        app.on_search_bar_replace_requested(msg)
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_replace_all(tmp_path: Path) -> None:
    src = tmp_path / "replace_all.py"
    src.write_text("foo foo foo")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        from ced.panels.search_bar import SearchBar

        msg = SearchBar.ReplaceRequested("foo", "bar", all=True)
        app.on_search_bar_replace_requested(msg)
        await pilot.pause()
        assert active.text == "bar bar bar"


@pytest.mark.asyncio
async def test_pilot_undo_redo(tmp_path: Path) -> None:
    src = tmp_path / "undome.py"
    src.write_text("start")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.text = "changed"
        app.action_undo()
        await pilot.pause()
        app.action_redo()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_active_editor_is_none() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_undo()
        app.action_redo()
        await pilot.pause()
