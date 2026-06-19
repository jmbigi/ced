from __future__ import annotations

from pathlib import Path

import pytest

from ced.app import Ced
from ced.panels.search_bar import SearchBar


@pytest.mark.asyncio
async def test_search_bar_show_hide(tmp_path: Path) -> None:
    src = tmp_path / "sh.py"
    src.write_text("text")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        sb = app.query_one("#search-bar")
        sb.display = False
        app.action_search()
        await pilot.pause()
        assert sb.display is True
        app.action_search()
        await pilot.pause()
        assert sb.display is False


@pytest.mark.asyncio
async def test_search_bar_show_replace_ui(tmp_path: Path) -> None:
    src = tmp_path / "sr.py"
    src.write_text("text")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        sb = app.query_one("#search-bar", SearchBar)
        app.action_search_replace()
        await pilot.pause()
        assert sb.display is True


@pytest.mark.asyncio
async def test_search_bar_input_submitted(tmp_path: Path) -> None:
    src = tmp_path / "is.py"
    src.write_text("findable content")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        app.action_search()
        await pilot.pause()
        inp = app.query_one("#find-input")
        inp.value = "findable"
        inp.action_submit()
        await pilot.pause()


@pytest.mark.asyncio
async def test_search_bar_toggle_replace(tmp_path: Path) -> None:
    src = tmp_path / "tr.py"
    src.write_text("text")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        sb = app.query_one("#search-bar", SearchBar)
        sb.show_replace_ui(True)
        await pilot.pause()
        sb.show_replace_ui(False)
        await pilot.pause()


@pytest.mark.asyncio
async def test_search_bar_get_text(tmp_path: Path) -> None:
    src = tmp_path / "gt.py"
    src.write_text("text")
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        app.action_search()
        await pilot.pause()
        sb = app.query_one("#search-bar", SearchBar)
        inp = app.query_one("#find-input")
        inp.value = "hello"
        assert sb.get_search_text() == "hello"
