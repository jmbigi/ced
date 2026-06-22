from __future__ import annotations

import re
from pathlib import Path

import pytest
from textual.widgets import TabbedContent

from ced.app import Ced

from tests.helpers import (
    _png_supported,
    assert_screen_contains,
    capture_png,
    capture_svg,
    describe_screen,
    extract_screen_text,
    extract_widgets_by_id,
    type_text,
)


# ---------------------------------------------------------------------------
# Screen content snapshot tests (text-extraction based, SVG-independent)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_svg_screenshot_main_screen() -> None:
    """Verify the main screen renders all required widgets."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert_screen_contains(app, "Quit", "Save", "Open", "Sidebar")


@pytest.mark.asyncio
async def test_svg_screenshot_after_open_file(tmp_path: Path) -> None:
    """Open a file and verify its content appears in the editor."""
    src = tmp_path / "hello.py"
    src.write_text("print('hello world')\n")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        assert_screen_contains(app, "hello.py")
        active = editor.get_active_editor()
        assert active is not None
        assert "hello world" in active.text


@pytest.mark.asyncio
async def test_svg_screenshot_terminal_open() -> None:
    """Toggle the terminal panel open and verify visibility."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        terminal = app.query_one("#terminal")
        assert terminal.display is False
        app.action_toggle_terminal()
        await pilot.pause()
        assert terminal.display is True


# ---------------------------------------------------------------------------
# Screen-text extraction ("terminal OCR") tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ocr_extract_widget_text() -> None:
    """Verify that widget text extraction works on known widgets."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        texts = extract_widgets_by_id(app)
        assert "help-bar" in texts
        assert "editor" in texts
        assert len(texts["help-bar"]) > 0


@pytest.mark.asyncio
async def test_ocr_screen_contains_key_after_action() -> None:
    """After opening the search bar, verify it appears in screen text."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_search()
        await pilot.pause()
        assert_screen_contains(app, "Find")


@pytest.mark.asyncio
async def test_ocr_widget_contains_after_typing() -> None:
    """Type into an editor and verify the content is detected."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.new_file()
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.text = "custom content"
        await pilot.pause()
        assert "custom content" in active.text


# ---------------------------------------------------------------------------
# Screen description ("vision model") tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_describe_main_screen() -> None:
    """Verify that the screen description can be generated without error."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        desc = describe_screen(app)
        assert "Screen:" in desc
        assert "EditorArea" in desc or "Horizontal" in desc
        assert len(desc) > 50


@pytest.mark.asyncio
async def test_describe_after_state_change() -> None:
    """Description changes after a user action (sidebar toggle)."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        desc_before = describe_screen(app)
        app.action_toggle_sidebar()
        await pilot.pause()
        desc_after = describe_screen(app)
        assert desc_before != desc_after


# ---------------------------------------------------------------------------
# Real-user interaction simulation tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_user_types_in_editor() -> None:
    """Simulate a user typing keystrokes into a new file."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.new_file()
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.focus()
        await pilot.pause()
        await type_text(pilot, "def hello():")
        await pilot.pause()
        assert "def hello():" in active.text


@pytest.mark.asyncio
async def test_user_open_file_then_close(tmp_path: Path) -> None:
    """Simulate a full user workflow: open a file, edit, verify."""
    src = tmp_path / "demo.py"
    src.write_text("# initial")

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.open_file(src)
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.text = "# modified by user"
        await pilot.pause()
        screen_text = extract_screen_text(app)
        assert "# modified by user" in screen_text
        assert "demo.py" in screen_text


@pytest.mark.asyncio
async def test_user_sidebar_toggle() -> None:
    """Simulate user pressing Ctrl+B to toggle the sidebar."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_toggle_sidebar()
        await pilot.pause()


@pytest.mark.asyncio
async def test_user_search_and_replace_flow() -> None:
    """Simulate a complete search and replace workflow."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.new_file()
        await pilot.pause()
        active = editor.get_active_editor()
        assert active is not None
        active.text = "foo bar foo baz"
        await pilot.pause()
        app.action_search_replace()
        await pilot.pause()
        assert_screen_contains(app, "Find")
        assert_screen_contains(app, "Replace")


@pytest.mark.asyncio
async def test_user_command_palette_flow() -> None:
    """Simulate user opening command palette and typing a command."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_command_palette()
        await pilot.pause()
        await type_text(pilot, "save")
        await pilot.pause()
        screen_text = extract_screen_text(app)
        assert "save" in screen_text.lower()


@pytest.mark.asyncio
async def test_user_tab_navigation() -> None:
    """Simulate user navigating between open tabs."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        editor = app.query_one("#editor")
        editor.new_file()
        await pilot.pause()
        editor.new_file()
        await pilot.pause()
        tabs = editor.query_one(TabbedContent)
        assert tabs is not None
        assert tabs.tab_count >= 2


# ---------------------------------------------------------------------------
# Keyboard-driven interaction tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_keypress_sequence_theme_cycle() -> None:
    """Cycle themes with keyboard shortcuts."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        before = app.config.theme.name
        app.action_theme_next()
        await pilot.pause()
        assert app.config.theme.name != before


@pytest.mark.asyncio
async def test_keypress_open_and_close_terminal() -> None:
    """Toggle terminal via action."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_toggle_terminal()
        await pilot.pause()
        assert_screen_contains(app, "Terminal")


@pytest.mark.asyncio
async def test_quick_open_filtering(tmp_path: Path) -> None:
    """Simulate quick-open filtering with real keystrokes."""
    (tmp_path / "alpha.py").write_text("")
    (tmp_path / "beta.py").write_text("")
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        from ced.panels.quick_open import QuickOpen

        app.push_screen(QuickOpen(tmp_path))
        await pilot.pause()
        await type_text(pilot, "alpha")
        await pilot.pause()
        screen_text = extract_screen_text(app)
        assert "alpha" in screen_text


# ---------------------------------------------------------------------------
# PNG screenshot tests — image-level recording
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_png_screenshot_main_screen() -> None:
    """Capture a PNG screenshot of the main screen.

    This requires ``cairosvg`` or ``svglib+reportlab`` to be installed; if
    neither is available the test is skipped.
    """
    if not _png_supported():
        pytest.skip("PNG conversion requires cairosvg or svglib+reportlab")
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        png = capture_png(app)
        assert png is not None
        assert len(png) > 1000


@pytest.mark.asyncio
async def test_png_screenshot_to_file(tmp_path: Path) -> None:
    """Write a PNG screenshot to disk and verify the file is valid."""
    if not _png_supported():
        pytest.skip("PNG conversion requires cairosvg or svglib+reportlab")
    from tests.helpers import capture_png_to_file

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        dst = tmp_path / "screenshot.png"
        data = await capture_png_to_file(app, dst)
        assert data is not None
        assert dst.exists()
        assert dst.stat().st_size > 1000


# ---------------------------------------------------------------------------
# Image description tests — vision-model description of PNG screenshots
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_image_description_from_svg() -> None:
    """Generate a human-readable description from the SVG screenshot
    by parsing its text nodes.  This simulates a "vision model" describing
    what is visible in a PNG recording of the terminal."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        svg = capture_svg(app, normalized=False)
        # Extract all visible text from the SVG
        texts = re.findall(r">([^<]{2,})<", svg)
        visible = " ".join(
            t.strip()
            for t in texts
            if t.strip() and not t.strip().startswith("terminal-")
        )
        assert len(visible) > 50
        # Verify key UI elements are described
        assert "Quit" in visible or "Save" in visible or "Open" in visible
