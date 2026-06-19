from __future__ import annotations

from pathlib import Path

import pytest

from ced.app import Ced


@pytest.mark.asyncio
async def test_pilot_command_palette_dismiss() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_command_palette()
        await pilot.pause()
        # Press escape to dismiss
        await pilot.press("escape")
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_command_palette_search() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_command_palette()
        await pilot.pause()
        # Type a search query
        await pilot.press("s", "a", "v", "e")
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_quick_open_dismiss() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_quick_open()
        await pilot.pause()
        # Press escape to dismiss
        await pilot.press("escape")
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_quick_open_filter(tmp_path: Path) -> None:
    # Create a file to find
    (tmp_path / "target_file.py").write_text("")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Override root path for quick open
        from ced.panels.quick_open import QuickOpen

        app.push_screen(QuickOpen(tmp_path))
        await pilot.pause()
        # Type to filter
        await pilot.press("t", "a", "r", "g", "e", "t")
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_jump_mode_dismiss() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_jump_mode()
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_jump_mode_input() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Open a file first so there's text to jump in
        editor = app.query_one("#editor")
        from pathlib import Path
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("hello world\nfoo bar\n")
            f.flush()
            editor.open_file(Path(f.name))
        await pilot.pause()
        app.action_jump_mode()
        await pilot.pause()
        # Type "he" to jump to "hello"
        await pilot.press("h", "e")
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_search_bar_find(tmp_path: Path) -> None:
    src = tmp_path / "search_me.py"
    src.write_text("find this text here")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        app.action_search()
        await pilot.pause()
        # Type in search bar
        inp = app.query_one("#find-input")
        inp.value = "find"
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_sidebar_toggle() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_toggle_sidebar()
        await pilot.pause()
        app.action_toggle_sidebar()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_opencode_toggle() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_toggle_opencode()
        await pilot.pause()
        app.action_toggle_opencode()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_keybinding_cycle() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Call keybinding_next which calls _update_help_bar
        # (needs to be mounted for query_one)
        app._keybinding_manager.set_preset("nano")
        app._apply_keybindings()
        await pilot.pause()


@pytest.mark.asyncio
async def test_pilot_widgets_mounted() -> None:
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one("#file-tree") is not None
        assert app.query_one("#help-bar") is not None
        assert app.query_one("#search-bar") is not None
        assert app.query_one("#editor") is not None
        assert app.query_one("#opencode") is not None
