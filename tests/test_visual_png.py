from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import cv2
import pyautogui
import pytest
import pytesseract
from PIL import Image
from xvfbwrapper import Xvfb

TERMINAL = "/usr/bin/konsole"


def _ocr_file(png: Path) -> str:
    return pytesseract.image_to_string(Image.open(png))


def _import_root(png_path: str | Path, display: str) -> None:
    subprocess.run(
        ["import", "-window", "root", str(png_path)],
        capture_output=True,
        timeout=10,
        env={**os.environ, "DISPLAY": display},
    )


def _launch_ced(display: str) -> subprocess.Popen:
    env = {**os.environ, "DISPLAY": display}
    env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    return subprocess.Popen(
        [TERMINAL, "--noclose", "--hide-menubar", "--hide-tabbar",
         "-e", "python3 -m ced"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )


def _search_ced_window(display: str) -> str | None:
    """Search for the konsole window hosting ced.

    The window name contains 'ced' (from 'python3 -m ced').
    """
    r = subprocess.run(
        ["xdotool", "search", "--name", "ced"],
        capture_output=True,
        text=True,
        timeout=5,
        env={**os.environ, "DISPLAY": display},
    )
    if r.stdout.strip():
        return r.stdout.strip().split()[0]
    r = subprocess.run(
        ["xdotool", "search", "--class", "konsole"],
        capture_output=True,
        text=True,
        timeout=5,
        env={**os.environ, "DISPLAY": display},
    )
    if r.stdout.strip():
        return r.stdout.strip().split()[0]
    return None


def _activate_ced_window(display: str) -> str | None:
    """Find, activate and return the ced window ID, or None."""
    win_id = _search_ced_window(display)
    if win_id is None:
        return None
    subprocess.run(
        ["xdotool", "windowactivate", "--sync", win_id],
        capture_output=True,
        timeout=5,
        env={**os.environ, "DISPLAY": display},
    )
    time.sleep(0.3)
    return win_id


def _capture_ced_window(display: str, png_path: str | Path) -> bool:
    """Wait for ced window, capture it, return True if content captured."""
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        win_id = _search_ced_window(display)
        if win_id is not None:
            time.sleep(2)
            _activate_ced_window(display)
            subprocess.run(
                ["import", "-window", win_id, str(png_path)],
                capture_output=True,
                timeout=10,
                env={**os.environ, "DISPLAY": display},
            )
            return True
        time.sleep(0.5)
    return False


@pytest.mark.visual
class TestVisualPNG:
    @pytest.fixture(autouse=True)
    def _xvfb(self) -> None:
        self.v = Xvfb(width=1280, height=800)
        self.v.start()
        self.display = f":{self.v.new_display}"
        pyautogui.FAILSAFE = False
        yield
        self.v.stop()

    def test_1_screenshot_has_content(self) -> None:
        proc = _launch_ced(self.display)
        ok = _capture_ced_window(self.display, "/tmp/ced_1.png")
        try:
            assert ok, "Window did not appear"
            img = cv2.imread("/tmp/ced_1.png")
            assert img is not None
            assert img.mean() > 5, f"mean={img.mean():.1f}"
        finally:
            proc.kill()
            proc.wait()

    def test_2_valid_png_dimensions(self) -> None:
        proc = _launch_ced(self.display)
        ok = _capture_ced_window(self.display, "/tmp/ced_2.png")
        try:
            assert ok
            img = cv2.imread("/tmp/ced_2.png")
            h, w, c = img.shape
            assert h > 200 and w > 200 and c in (3, 4)
        finally:
            proc.kill()
            proc.wait()

    def test_3_keyboard_simulation(self) -> None:
        proc = _launch_ced(self.display)
        try:
            _capture_ced_window(self.display, "/tmp/ced_3_before.png")
            _activate_ced_window(self.display)
            pyautogui.hotkey("ctrl", "n")
            time.sleep(0.5)
            pyautogui.write("def f():\n    pass\n")
            time.sleep(0.5)
        finally:
            proc.kill()
            proc.wait()

    def test_4_mouse_click_simulation(self) -> None:
        proc = _launch_ced(self.display)
        try:
            _capture_ced_window(self.display, "/tmp/ced_4.png")
            _activate_ced_window(self.display)
            pyautogui.click(x=200, y=200)
            time.sleep(0.5)
            pyautogui.write("clicked\n")
            time.sleep(0.3)
        finally:
            proc.kill()
            proc.wait()

    def test_5_opencv_edge_detection(self) -> None:
        proc = _launch_ced(self.display)
        ok = _capture_ced_window(self.display, "/tmp/ced_5.png")
        try:
            assert ok
            img = cv2.imread("/tmp/ced_5.png", cv2.IMREAD_GRAYSCALE)
            blurred = cv2.GaussianBlur(img, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            non_zero = cv2.countNonZero(edges)
            assert non_zero > 500, f"edges={non_zero}"
        finally:
            proc.kill()
            proc.wait()
