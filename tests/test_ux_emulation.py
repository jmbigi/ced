from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from ced.app import Ced


# ── Real-user workflow: open file, edit, save ───────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_open_edit_save(tmp_path: Path) -> None:
    """User: Ctrl+O → open file → type text → Ctrl+S."""
    src = tmp_path / "work.py"
    src.write_text("")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        editor_area = app.query_one("#editor")
        editor_area.open_file(src)
        await pilot.pause()

        active = editor_area.get_active_editor()
        assert active is not None

        active.text = "x = 1\ny = 2\nprint(x + y)"
        await pilot.pause()

        result = editor_area.save_active()
        assert result is True
        assert src.read_text() == "x = 1\ny = 2\nprint(x + y)"


# ── Real-user workflow: search and replace ──────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_search_replace(tmp_path: Path) -> None:
    """User: open file → Ctrl+F → find → Ctrl+H → replace all."""
    src = tmp_path / "search_replace.py"
    src.write_text("aaa bbb aaa bbb aaa")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor_area = app.query_one("#editor")
        editor_area.open_file(src)
        await pilot.pause()
        active = editor_area.get_active_editor()
        assert active is not None

        app.action_search_replace()
        await pilot.pause()

        find_inp = app.query_one("#find-input")
        find_inp.value = "aaa"
        rep_inp = app.query_one("#replace-input")
        rep_inp.value = "xxx"

        from ced.panels.search_bar import SearchBar

        app.on_search_bar_replace_requested(
            SearchBar.ReplaceRequested("aaa", "xxx", all=True)
        )
        await pilot.pause()

        assert active.text == "xxx bbb xxx bbb xxx"


# ── Real-user workflow: multiple tabs ──────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_multiple_tabs(tmp_path: Path) -> None:
    """User: open 2 files → switch tabs → close one."""
    a = tmp_path / "a.py"
    b = tmp_path / "b.py"
    a.write_text("file a")
    b.write_text("file b")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")

        ea.open_file(a)
        await pilot.pause()
        ea.open_file(b)
        await pilot.pause()
        assert ea.buffers.count >= 2

        ea.tab_next()
        await pilot.pause()
        ea.tab_prev()
        await pilot.pause()


# ── Real-user workflow: theme switching ─────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_theme_cycle() -> None:
    """User: cycle through all themes."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        themes_seen = {app.config.theme.name}
        for _ in range(6):
            app.action_theme_next()
            await pilot.pause()
            themes_seen.add(app.config.theme.name)
        assert len(themes_seen) >= 2


# ── Real-user workflow: keyboard shortcuts ──────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_keyboard_shortcuts(tmp_path: Path) -> None:
    """User: press Ctrl+N (new), Ctrl+Tab (next), Ctrl+W (close)."""
    src = tmp_path / "keys.py"
    src.write_text("")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_new_file()
        await pilot.pause()
        app.action_new_file()
        await pilot.pause()
        app.action_next_tab()
        await pilot.pause()
        app.action_prev_tab()
        await pilot.pause()


# ── Real-user workflow: sidebar toggle ──────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_sidebar_toggle() -> None:
    """User: toggle sidebar on/off."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        sb = app.query_one("#sidebar")
        v0 = sb.display
        app.action_toggle_sidebar()
        assert sb.display != v0
        app.action_toggle_sidebar()
        assert sb.display == v0


# ── Real-user workflow: command palette ─────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_command_palette() -> None:
    """User: open command palette → type query → dismiss."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_command_palette()
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()


# ── Real-user workflow: jump mode ───────────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_jump_mode(tmp_path: Path) -> None:
    """User: open file → Ctrl+J → type 2 chars."""
    src = tmp_path / "jump_target.py"
    src.write_text("hello world\ntarget here\nend")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        app.action_jump_mode()
        await pilot.pause()
        await pilot.press("t", "a")
        await pilot.pause()


# ── Real-user workflow: undo/redo ───────────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_undo_redo(tmp_path: Path) -> None:
    """User: type text → Ctrl+Z → Ctrl+Y."""
    src = tmp_path / "undoredo.py"
    src.write_text("")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None

        active.text = "typing..."
        app.action_undo()
        await pilot.pause()
        app.action_redo()
        await pilot.pause()


# ── Real-user workflow: toggle opencode panel ───────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_opencode_toggle() -> None:
    """User: toggle OpenCode panel."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        oc = app.query_one("#opencode-panel")
        v0 = oc.display
        app.action_toggle_opencode()
        assert oc.display != v0
        app.action_toggle_opencode()
        assert oc.display == v0


# ── Real-user workflow: keyboard-driven search ─────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_keyboard_search(tmp_path: Path) -> None:
    """User: open file → Ctrl+F → type query → Enter."""
    src = tmp_path / "find_target.py"
    src.write_text("searchable content here")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()

        app.action_search()
        await pilot.pause()
        inp = app.query_one("#find-input")
        inp.value = "searchable"
        await pilot.pause()


# ── Snapshot test: syrupy baseline comparison ───────────────────────────


@pytest.mark.asyncio
async def test_ux_snapshot_help_bar(snapshot) -> None:
    """Snapshot baseline of help-bar rendered text."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        hb = app.query_one("#help-bar")
        rendered = hb.query_one("#help-text").render()
        text = str(rendered)
        assert text == snapshot


# ── Snapshot test: verify help bar content ──────────────────────────────


@pytest.mark.asyncio
async def test_ux_help_bar_content() -> None:
    """Verify help-bar shows expected shortcuts for VS Code preset."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        hb = app.query_one("#help-bar")
        rendered = hb.query_one("#help-text").render()
        text = str(rendered)
        assert "^Q" in text
        assert "^S" in text
        assert "^B" in text


# ── Heavy test: large file + sandbox ────────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_heavy_large_file(tmp_path: Path) -> None:
    """Heavy test: open 1MB file, scroll, edit, save — sandboxed."""
    large = tmp_path / "large.py"
    large.write_text("line\n" * 50000)

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(large)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None
        assert len(active.text) > 50000
        active.text += "\n# new line"
        assert ea.save_active() is True


# ── Heavy test: rapid file operations ────────────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_rapid_open_close(tmp_path: Path) -> None:
    """Heavy: open and close 20 files rapidly — sandboxed."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        files = []
        for i in range(20):
            f = tmp_path / f"f{i}.py"
            f.write_text(f"file {i}")
            files.append(f)

        ea = app.query_one("#editor")
        for f in files:
            ea.open_file(f)
            await pilot.pause()
        assert ea.buffers.count >= 20


# ── Full workflow: write → open → modify → save → save_as → open_again → edit ─


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_full_file_workflow(tmp_path: Path) -> None:
    """Create → open → modify → save → save as → reopen → modify again."""
    original = tmp_path / "original.py"
    original.write_text("")
    copy = tmp_path / "copy.py"

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")

        # 1. Open empty file → edit text
        ea.open_file(original)
        await pilot.pause()
        ed = ea.get_active_editor()
        assert ed is not None
        ed.text = "x = 1"
        await pilot.pause()

        # 2. Save → verify on disk
        assert ea.save_active() is True
        assert original.read_text() == "x = 1"

        # 3. Modify again
        ed.text = "x = 1\ny = 2"
        await pilot.pause()

        # 4. Save as → new file
        ed.save_as(copy)
        await pilot.pause()
        assert copy.read_text() == "x = 1\ny = 2"

        # 5. Open another file, edit, save
        third = tmp_path / "third.py"
        third.write_text("")
        ea.open_file(third)
        await pilot.pause()
        ed2 = ea.get_active_editor()
        assert ed2 is not None
        ed2.text = "z = 3"
        await pilot.pause()
        assert ea.save_active() is True
        assert third.read_text() == "z = 3"

        # 6. Re-open original → buffer cache returns last-saved text
        ea.open_file(original)
        await pilot.pause()
        ed3 = ea.get_active_editor()
        assert ed3 is not None
        # Buffer was modified (x=1\n y=2) and saved-as → cache has modified text
        assert ed3.text == "x = 1\ny = 2"


# ── Real-user flow: unsaved changes warning ─────────────────────────────


@pytest.mark.sandbox
@pytest.mark.asyncio
async def test_ux_unsaved_warning(tmp_path: Path) -> None:
    """User: edit file → try close → confirm dialog."""
    src = tmp_path / "unsaved.py"
    src.write_text("original")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None
        active.text = "modified"
        buf = ea.buffers.active_buffer
        if buf:
            buf.mark_modified()
        app.confirm = AsyncMock(return_value=True)
        ea.close_active()
        await pilot.pause()
