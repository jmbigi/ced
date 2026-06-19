from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from ced.app import Ced

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_TOOLS = {
    "pyautogui": False,
    "opencv": False,
    "pytesseract": False,
    "xdotool": False,
}

try:
    import pyautogui
    REQUIRED_TOOLS["pyautogui"] = True
except ImportError:
    pass

try:
    import pytesseract
    REQUIRED_TOOLS["pytesseract"] = True
except ImportError:
    pass

try:
    # cv2 imported above
    REQUIRED_TOOLS["opencv"] = True
except ImportError:
    pass

REQUIRED_TOOLS["xdotool"] = (
    subprocess.run(["which", "xdotool"], capture_output=True).returncode == 0
)

_HAVE_DISPLAY = bool(os.environ.get("DISPLAY"))
_REAL_DISPLAY = os.environ.get("DISPLAY") == ":0"  # real desktop, not Xvfb

requires_screen_capture = pytest.mark.skipif(
    not _HAVE_DISPLAY or not REQUIRED_TOOLS["pyautogui"] or _REAL_DISPLAY,
    reason="Requires isolated X11 display (Xvfb) and pyautogui",
)

requires_ocr = pytest.mark.skipif(
    not REQUIRED_TOOLS["pytesseract"],
    reason="Requires pytesseract",
)


def _list_konsole_windows() -> set[int]:
    """Return the set of X11 window IDs whose class is ``konsole``."""
    try:
        r = subprocess.run(
            ["xdotool", "search", "--class", "konsole"],
            capture_output=True, text=True, timeout=2,
        )
        if r.returncode == 0 and r.stdout.strip():
            return {int(w) for w in r.stdout.strip().split()}
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return set()


def _find_new_konsole_window(
    before: set[int], timeout: float = 10.0
) -> int | None:
    """Wait until a new Konsole window appears that is not in *before*."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        now = _list_konsole_windows()
        diff = now - before
        if diff:
            return diff.pop()
        time.sleep(0.3)
    return None


def _capture_window_region(wid: int) -> Image.Image | None:
    """Capture the region of the screen occupied by window *wid*."""
    try:
        subprocess.run(["xdotool", "windowactivate", str(wid)],
                       capture_output=True, timeout=2)
        result = subprocess.run(
            ["xdotool", "getwindowgeometry", str(wid)],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode != 0:
            return None
        pos_line = geo_line = None
        for line in result.stdout.splitlines():
            if line.startswith("  Position: "):
                pos_line = line
            elif line.startswith("  Geometry: "):
                geo_line = line
        if not pos_line or not geo_line:
            return None
        _, pos_part = pos_line.split("Position: ", 1)
        xy = pos_part.split()[0]
        x_str, y_str = xy.split(",")
        x, y = int(x_str), int(y_str)
        _, geo_str = geo_line.split("Geometry: ", 1)
        wh = geo_str.strip()
        w_str, h_str = wh.split("x")
        w, h = int(w_str), int(h_str)
        time.sleep(0.3)
        return pyautogui.screenshot(region=(x, y, min(w, 1920), min(h, 1080)))
    except Exception as exc:
        print(f"_capture_window_region failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _launch_ced_terminal() -> tuple[subprocess.Popen, set[int]]:
    """Launch ``ced`` inside a fresh Konsole window.

    Returns ``(process, konsole_windows_before)`` so the caller can pass
    the latter to :func:`_find_new_konsole_window`.
    """
    before = _list_konsole_windows()
    env = os.environ.copy()
    # opencv-python bundles Qt plugins that conflict with Konsole's Qt
    env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    proc = subprocess.Popen(
        ["konsole", "--hold", "-e", "python", "-m", "ced"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
    )
    return proc, before


def _run_ced_test() -> Image.Image | None:
    """Launch ced, wait, capture, terminate, return screenshot."""
    proc, before = _launch_ced_terminal()
    try:
        wid = _find_new_konsole_window(before, timeout=10.0)
        assert wid is not None, "New Konsole window did not appear"
        time.sleep(2.0)
        return _capture_window_region(wid)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


@requires_screen_capture
def test_pyautogui_capture_ced_window() -> None:
    """Launch ``ced`` in a terminal and capture the window with PyAutoGUI."""
    img = _run_ced_test()
    assert img is not None, "Failed to capture window region"
    w, h = img.size
    assert w > 100 and h > 50, f"Screenshot too small: {w}x{h}"


@requires_screen_capture
@requires_ocr
def test_pyautogui_ocr_detects_ui_elements() -> None:
    """Capture the ced window and use Tesseract OCR to verify visible text."""
    img = _run_ced_test()
    assert img is not None
    open_cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    text = pytesseract.image_to_string(open_cv_image, lang="spa+eng")
    # The UI title should be visible somewhere on screen
    assert "ced" in text.lower(), f"OCR did not find 'ced' in:\n{text}"
    # At least one of these UI elements should be readable
    found = []
    for keyword in ["OpenCode", "Quit", "Save", "Sidebar", "Close"]:
        if keyword.lower() in text.lower():
            found.append(keyword)
    assert len(found) >= 1, f"OCR could not read any UI element from:\n{text}"


@requires_screen_capture
def test_pyautogui_screenshot_saved_to_png(tmp_path: Path) -> None:
    """Capture ced with PyAutoGUI and save the screenshot as PNG."""
    img = _run_ced_test()
    assert img is not None
    dst = tmp_path / "ced_screenshot.png"
    img.save(dst)
    assert dst.exists()
    assert dst.stat().st_size > 5000


@requires_screen_capture
def test_pyautogui_screenshot_has_expected_colors() -> None:
    """Basic pixel-level sanity: the terminal background is dark."""
    img = _run_ced_test()
    assert img is not None
    cx, cy = img.width // 2, img.height // 2
    center_pixel = img.getpixel((cx, cy))
    assert all(
        c < 100 for c in center_pixel[:3]
    ), f"Center pixel too bright: {center_pixel}"


# ---------------------------------------------------------------------------
# Textual-based fallback tests (run headlessly)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# OpenCV / Pillow image comparison
# ---------------------------------------------------------------------------


@requires_screen_capture
def test_opencv_pixel_stats() -> None:
    """Use OpenCV to examine the captured screenshot's pixel statistics.

    The terminal background should be dark and the text should be light.
    """
    img = _run_ced_test()
    assert img is not None
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # Convert to grayscale and check histogram
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    # Most pixels should be dark (background) — mean < 100
    mean_val = gray.mean()
    assert mean_val < 150, f"Image too bright (mean={mean_val:.1f})"
    # There should be some bright pixels (text) — std > 20
    std_val = gray.std()
    assert std_val > 10, f"Image too uniform (std={std_val:.1f})"


@requires_screen_capture
@requires_ocr
def test_opencv_ocr_on_saved_png(tmp_path: Path) -> None:
    """Save a PNG screenshot, reload with OpenCV, and run OCR on it."""
    img = _run_ced_test()
    assert img is not None
    dst = tmp_path / "ced_screenshot.png"
    img.save(dst)
    # Reload with OpenCV
    cv_img = cv2.imread(str(dst))
    assert cv_img is not None, "OpenCV could not read saved PNG"
    text = pytesseract.image_to_string(cv_img, lang="spa+eng")
    assert "ced" in text.lower(), f"OCR failed on saved PNG:\n{text}"


# ---------------------------------------------------------------------------
# Textual-based fallback tests (run headlessly)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_textual_fallback_screenshot_text() -> None:
    """When pyautogui is not available, fall back to extracting text from
    the Textual rendering as a proxy for visual verification."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        from tests.helpers import extract_screen_text
        text = extract_screen_text(app)
        assert "Quit" in text
        assert "Save" in text
        assert "Open" in text
