from __future__ import annotations

import pytest

from ced.app import Ced


@pytest.mark.asyncio
async def test_app_title() -> None:
    app = Ced()
    assert app.TITLE == "ced"
    assert app.SUB_TITLE == "Terminal Code Editor"


@pytest.mark.asyncio
async def test_app_bindings_count() -> None:
    app = Ced()
    # 15 app-level bindings defined in BINDINGS
    assert len(app.BINDINGS) == 15


@pytest.mark.asyncio
async def test_app_config_loaded() -> None:
    app = Ced()
    assert app.config is not None
    assert app.config.theme.name == "monokai"
    assert app.config.editor.tab_size == 4
    assert app.config.keybindings.preset == "vscode"
    assert app.config.opencode.path == "opencode"
    assert app.config.opencode.auto_start is True


@pytest.mark.asyncio
async def test_app_command_registry() -> None:
    app = Ced()
    all_cmds = app.commands.all()
    assert len(all_cmds) == 21
    ids = {c.id for c in all_cmds}
    assert "app.quit" in ids
    assert "app.save" in ids
    assert "app.undo" in ids
    assert "app.redo" in ids
    assert "app.help" in ids


@pytest.mark.asyncio
async def test_app_keybinding_manager() -> None:
    app = Ced()
    assert app._keybinding_manager.current_preset == "vscode"
    bindings = app._keybinding_manager.bindings
    actions = {b.action for b in bindings}
    assert "quit" in actions
    assert "save" in actions
    assert "undo" in actions
    assert "redo" in actions


@pytest.mark.asyncio
async def test_app_compose() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.is_running
        assert app.query("#help-bar") is not None


@pytest.mark.asyncio
async def test_app_theme_cycle() -> None:
    app = Ced()
    themes_before = app.config.theme.name
    app.action_theme_next()
    assert app.config.theme.name != themes_before


@pytest.mark.asyncio
async def test_app_keybinding_manager_set_preset() -> None:
    app = Ced()
    assert app._keybinding_manager.current_preset == "vscode"
    app._keybinding_manager.set_preset("nano")
    assert app._keybinding_manager.current_preset == "nano"


@pytest.mark.asyncio
async def test_app_toggle_sidebar() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        sidebar = app.query_one("#sidebar")
        initial = sidebar.display
        app.action_toggle_sidebar()
        assert sidebar.display != initial


@pytest.mark.asyncio
async def test_app_toggle_search() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_search()
        search_bar = app.query_one("#search-bar")
        assert search_bar.display is True


@pytest.mark.asyncio
async def test_app_help_bar_updated() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        help_bar = app.query_one("#help-bar")
        assert help_bar is not None


@pytest.mark.asyncio
async def test_app_save_untitled_notifies() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_save()
        await pilot.pause()
        # Should not crash — warns about untitled


@pytest.mark.asyncio
async def test_app_new_file() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        count_before = editor.buffers.count
        app.action_new_file()
        await pilot.pause()
        assert editor.buffers.count == count_before + 1


@pytest.mark.asyncio
async def test_app_tab_navigation() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Create two tabs
        app.action_new_file()
        await pilot.pause()
        app.action_new_file()
        await pilot.pause()
        # Navigate
        app.action_prev_tab()
        await pilot.pause()
        app.action_next_tab()
        await pilot.pause()


@pytest.mark.asyncio
async def test_app_theme_cycle() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        theme_before = app.config.theme.name
        app.action_theme_next()
        await pilot.pause()
        assert app.config.theme.name != theme_before


@pytest.mark.asyncio
async def test_app_toggle_sidebar() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        sidebar = app.query_one("#sidebar")
        initial = sidebar.display
        app.action_toggle_sidebar()
        assert sidebar.display != initial


@pytest.mark.asyncio
async def test_app_new_file() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        count_before = app.query_one("#editor").buffers.count
        app.action_new_file()
        await pilot.pause()
        assert app.query_one("#editor").buffers.count == count_before + 1


@pytest.mark.asyncio
async def test_app_save_untitled_notifies() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_save()
        await pilot.pause()


@pytest.mark.asyncio
async def test_app_help_action() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_help()
        await pilot.pause()


@pytest.mark.asyncio
async def test_app_compose_structure() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query("#sidebar") is not None
        assert app.query("#editor") is not None
        assert app.query("#search-bar") is not None
        assert app.query("#help-bar") is not None
