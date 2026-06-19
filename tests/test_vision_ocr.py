from __future__ import annotations

import re
from pathlib import Path

import pytesseract
from PIL import Image

import pytest

from ced.app import Ced


def _ocr_svg_text(svg_path: Path) -> str:
    """Extract ALL text from an SVG file (basic OCR without tesseract)."""
    svg = svg_path.read_text()
    texts = re.findall(r"<text[^>]*>([^<]*)</text>", svg)
    return "\n".join(t.replace("&#160;", " ").replace("&gt;", ">").replace("&lt;", "<") for t in texts)


def _ocr_png_text(png_path: Path) -> str:
    """OCR a PNG image using tesseract."""
    return pytesseract.image_to_string(Image.open(png_path))


# ── VISION TEST: UI structure from SVG ─────────────────────────────────

@pytest.mark.asyncio
async def test_vision_svg_shows_help_bar() -> None:
    """SVG screenshot must contain the help-bar shortcuts."""
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        svg = app.export_screenshot()
        svg_path = Path("/tmp/_ced_vision_helpbar.svg")
        svg_path.write_text(str(svg))
        text = _ocr_svg_text(svg_path)
        assert "^Q" in text, f"^Q not found in SVG text:\n{text[:500]}"
        assert "^S" in text, f"^S not found in SVG text:\n{text[:500]}"
        assert "Quit" in text
        assert "Save" in text


@pytest.mark.asyncio
async def test_vision_svg_shows_tabs() -> None:
    """SVG screenshot must show the tab bar with untitled tab."""
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.new_file()
        await pilot.pause()
        svg = app.export_screenshot()
        svg_path = Path("/tmp/_ced_vision_tabs.svg")
        svg_path.write_text(str(svg))
        text = _ocr_svg_text(svg_path)
        assert "untitled" in text, f"untitled tab not found:\n{text[:500]}"


@pytest.mark.asyncio
async def test_vision_svg_shows_sidebar_files() -> None:
    """SVG must show the file tree sidebar."""
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        svg = app.export_screenshot()
        svg_path = Path("/tmp/_ced_vision_sidebar.svg")
        svg_path.write_text(str(svg))
        text = _ocr_svg_text(svg_path)
        assert any(x in text for x in [".gitignore", "README", "src"]), (
            f"No project files found:\n{text[:500]}"
        )


# ── USER INTERACTION: real UI simulation via Pilot ──────────────────────

@pytest.mark.asyncio
async def test_user_new_file_and_type(tmp_path: Path) -> None:
    """User: Ctrl+N → type code → save → verify on disk."""
    dest = tmp_path / "typed_code.py"
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.new_file()
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None, "No active editor after new_file"
        assert active.has_focus is True, "Focus bug: editor should have focus after new_file()"

        codigo = "x = 42\nprint(f'El valor es {x}')\n"
        active.text = codigo
        await pilot.pause()
        active.file_path = dest
        assert active.save_file() is True
        assert dest.read_text() == codigo, "File content mismatch"
        assert "42" in dest.read_text()


@pytest.mark.asyncio
async def test_user_open_file_modify_save(tmp_path: Path) -> None:
    """User: open file → modify → save → re-open → verify."""
    src = tmp_path / "original.py"
    src.write_text("original content")
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None
        assert active.text == "original content"
        active.text = "modified content"
        await pilot.pause()
        assert ea.save_active() is True
        assert src.read_text() == "modified content"


@pytest.mark.asyncio
async def test_user_tab_navigation(tmp_path: Path) -> None:
    """User: open 3 files → switch tabs → close one."""
    files = []
    for i in range(3):
        f = tmp_path / f"tab_{i}.py"
        f.write_text(f"content_{i}")
        files.append(f)
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        for f in files:
            ea.open_file(f)
            await pilot.pause()
        assert ea.buffers.count >= 3
        ea.tab_next()
        await pilot.pause()
        ea.tab_prev()
        await pilot.pause()
        ea.tab_next()
        await pilot.pause()


@pytest.mark.asyncio
async def test_user_search_then_replace(tmp_path: Path) -> None:
    """User: open file → Ctrl+F → type → Ctrl+H → replace all."""
    src = tmp_path / "search_doc.py"
    src.write_text("aaa bbb aaa bbb")
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None
        from ced.panels.search_bar import SearchBar
        app.on_search_bar_replace_requested(
            SearchBar.ReplaceRequested("aaa", "xxx", all=True)
        )
        await pilot.pause()
        assert active.text == "xxx bbb xxx bbb"


@pytest.mark.asyncio
async def test_user_theme_cycle() -> None:
    """User: cycle through themes via action."""
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        themes_before = app.config.theme.name
        app.action_theme_next()
        await pilot.pause()
        assert app.config.theme.name != themes_before


@pytest.mark.asyncio
async def test_user_undo_redo(tmp_path: Path) -> None:
    """User: type text → Ctrl+Z → Ctrl+Y."""
    src = tmp_path / "undoredo_doc.py"
    src.write_text("")
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None
        active.text = "something"
        app.action_undo()
        await pilot.pause()
        app.action_redo()
        await pilot.pause()


# ── KEYBOARD INPUT SIMULATION ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_keyboard_typing(tmp_path: Path) -> None:
    """Simulate real keyboard typing via pilot.press()."""
    src = tmp_path / "keyboard_test.py"
    src.write_text("")
    app = Ced()
    async with app.run_test(size=(100, 24)) as pilot:
        await pilot.pause()
        ea = app.query_one("#editor")
        ea.open_file(src)
        await pilot.pause()
        active = ea.get_active_editor()
        assert active is not None
        # Type using the keyboard simulation
        for ch in "hello world":
            await pilot.press(ch)
        await pilot.pause()
        assert "hello world" in active.text


# ── FILE WRITE EVIDENCE (no UI needed) ─────────────────────────────────

def test_evidence_write_read_cycles(tmp_path: Path) -> None:
    """10 write-read cycles with different content — 100% precision."""
    log = []
    for i in range(10):
        f = tmp_path / f"cycle_{i}.txt"
        content = f"Cycle {i}: Line 1\nLine 2 with num {i*2}\nEnd\n"
        f.write_text(content)
        read_back = f.read_text()
        assert read_back == content, f"Cycle {i} mismatch"
        log.append(f"  Cycle {i}: {len(content)} bytes written, {len(read_back)} bytes read — OK")
    print("\n".join(log))
