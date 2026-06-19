from __future__ import annotations

import io
import re
from pathlib import Path
from typing import TYPE_CHECKING

from rich.text import Text
from textual.widgets import TextArea

if TYPE_CHECKING:
    from textual.app import App
    from textual.pilot import Pilot
    from textual.widget import Widget


# ---------------------------------------------------------------------------
# SVG normalization — strips random identifiers for stable snapshots
# ---------------------------------------------------------------------------

_SVG_RANDOM_RE = re.compile(r"\bterminal-\d+\b")


def normalize_svg(svg: str) -> str:
    """Replace random class/ID suffixes (``terminal-<digits>``) with a
    fixed placeholder so SVG snapshots are stable across runs."""
    return _SVG_RANDOM_RE.sub("terminal-SNAPSHOT", svg)


# ---------------------------------------------------------------------------
# Screen capture — advanced recording of terminal output
# ---------------------------------------------------------------------------


def capture_svg(app: App, normalized: bool = True) -> str:
    """Capture the current screen as an SVG image (terminal recording).

    If *normalized* is ``True`` (default), random identifiers are replaced
    with a fixed placeholder so the output is suitable for snapshot comparison.
    """
    svg = app.export_screenshot()
    return normalize_svg(svg) if normalized else svg


async def capture_svg_to_file(app: App, path: str | Path) -> str:
    """Capture an SVG screenshot and write it to *path*."""
    svg = capture_svg(app, normalized=False)
    Path(path).write_text(svg, encoding="utf-8")
    return svg


# ---------------------------------------------------------------------------
# PNG capture — convert terminal SVG to PNG for image-level assertions
# ---------------------------------------------------------------------------

_PNG_AVAILABLE: bool | None = None


def _png_supported() -> bool:
    global _PNG_AVAILABLE
    if _PNG_AVAILABLE is not None:
        return _PNG_AVAILABLE
    try:
        import cairosvg  # noqa: F401
        _PNG_AVAILABLE = True
    except ImportError:
        try:
            from svglib.svglib import svg2rlg  # noqa: F401
            from reportlab.graphics import renderPM  # noqa: F401
            _PNG_AVAILABLE = True
        except ImportError:
            _PNG_AVAILABLE = False
    return _PNG_AVAILABLE


def capture_png(app: App) -> bytes | None:
    """Capture the current screen as PNG bytes.

    Requires **cairosvg** or **svglib+reportlab** to be installed.
    Returns ``None`` if no converter is available.
    """
    svg = app.export_screenshot()
    try:
        import cairosvg
        return cairosvg.svg2png(bytestring=svg.encode("utf-8"))
    except ImportError:
        pass
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        drawing = svg2rlg(io.StringIO(svg))
        buf = io.BytesIO()
        renderPM.drawToFile(drawing, buf, fmt="PNG")
        return buf.getvalue()
    except ImportError:
        return None


async def capture_png_to_file(app: App, path: str | Path) -> bytes | None:
    """Capture a PNG screenshot and write it to *path*.

    Returns the PNG bytes, or ``None`` if no converter is available.
    """
    data = capture_png(app)
    if data is not None:
        Path(path).write_bytes(data)
    return data


# ---------------------------------------------------------------------------
# Screen-text extraction — "OCR" for terminal content
# ---------------------------------------------------------------------------


def extract_screen_text(app: App) -> str:
    """Extract all visible text from the current screen ("terminal OCR")."""
    lines: list[str] = []

    def _walk(widget: Widget) -> None:
        if not widget.display or not widget.visible:
            return
        if isinstance(widget, TextArea):
            text = widget.text.strip()
            if text:
                lines.append(text)
        else:
            try:
                rendered = widget.render()
            except Exception:
                rendered = None
            if rendered is not None:
                rich_text = Text.from_ansi(str(rendered))
                plain = rich_text.plain.strip()
                if plain:
                    lines.append(plain)
        for child in widget.children:
            _walk(child)

    _walk(app.screen)
    return "\n".join(lines)


def extract_widget_text(widget: Widget) -> str:
    """Extract the plain text content of a single widget."""
    if isinstance(widget, TextArea):
        return widget.text
    try:
        rendered = widget.render()
    except Exception:
        return ""
    rich_text = Text.from_ansi(str(rendered))
    return rich_text.plain


def extract_widgets_by_id(app: App) -> dict[str, str]:
    """Return {widget_id: rendered_text} for every widget with an explicit id."""
    result: dict[str, str] = {}

    def _walk(w: Widget) -> None:
        if w.id:
            text = extract_widget_text(w)
            if text:
                result[w.id] = text
        for child in w.children:
            _walk(child)

    _walk(app.screen)
    return result


# ---------------------------------------------------------------------------
# Screen description — Vision-modeling helpers
# ---------------------------------------------------------------------------


def describe_screen(app: App) -> str:
    """Produce a structured, human-readable description of the current screen."""
    parts: list[str] = [f"Screen: {app.screen.__class__.__name__}"]

    def _walk(w: Widget, depth: int = 0) -> None:
        indent = "  " * depth
        info = f"{w.__class__.__name__}"
        if w.id:
            info += f" #{w.id}"
        try:
            region = w.region
            info += f" [{region.x},{region.y} {region.width}x{region.height}]"
        except Exception:
            pass
        text = extract_widget_text(w)[:80]
        if text:
            info += f" = {text!r}"
        parts.append(f"{indent}{info}")
        for child in w.children:
            _walk(child, depth + 1)

    _walk(app.screen)
    return "\n".join(parts)


def assert_screen_contains(app: App, *texts: str) -> None:
    """Assert that all *texts* appear somewhere in the rendered screen."""
    full = extract_screen_text(app)
    missing = [t for t in texts if t not in full]
    if missing:
        raise AssertionError(
            f"Screen did not contain expected text(s): {missing}\n"
            f"--- screen text ---\n{full}"
        )


def assert_widget_contains(app: App, widget_id: str, text: str) -> None:
    """Assert that a specific widget (by id) contains *text*."""
    widgets = extract_widgets_by_id(app)
    if widget_id not in widgets:
        raise AssertionError(f"Widget #{widget_id} not found on screen")
    if text not in widgets[widget_id]:
        raise AssertionError(
            f"Widget #{widget_id} does not contain {text!r}\n"
            f"  actual: {widgets[widget_id]!r}"
        )


# ---------------------------------------------------------------------------
# User interaction helpers — real keystroke sequences
# ---------------------------------------------------------------------------


async def type_text(pilot: Pilot, text: str) -> None:
    """Simulate a user typing *text* one character at a time."""
    for ch in text:
        await pilot.press(ch)


async def press_keys(pilot: Pilot, *keys: str) -> None:
    """Simulate pressing a sequence of keys."""
    for key in keys:
        await pilot.press(key)
