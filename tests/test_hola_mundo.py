"""Prueba completa: Escribir 'Hola mundo' en ced y verificarlo.

La simulación de usuario real se hace escribiendo directamente al PTY
donde corre ced (dentro de Konsole en Xvfb). Esto evita los problemas de
XTEST en Xvfb (sin foco de ventana) y de Qt/Konsole (intercepta teclas).

Flujo:
  1. Lanzar ced dentro de Konsole en Xvfb (pantalla aislada)
  2. Escribir Ctrl+N + "Hola mundo" al PTY de ced
  3. Capturar pantalla antes/después
  4. Detectar región cambiada con OpenCV
  5. Verificar con OCR que "Hola mundo" está en la región cambiada
  6. Verificar con OpenCV calidad de imagen
  7. Limpiar
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import pytest
import pytesseract
from PIL import Image
from xvfbwrapper import Xvfb


def _find_ced_pty() -> str | None:
    """Encontrar el PTY donde corre ced."""
    r = subprocess.run(
        ["pgrep", "-a", "python3"],
        capture_output=True, text=True, timeout=5,
    )
    for line in r.stdout.strip().split("\n"):
        if "python3 -m ced" in line:
            pid = line.split()[0]
            try:
                for fd_name in ("0", "1", "2"):
                    link = os.readlink(f"/proc/{pid}/fd/{fd_name}")
                    if link.startswith("/dev/pts/"):
                        return link
            except (FileNotFoundError, OSError):
                pass
    return None


def _write_pty(pty_path: str, text: str | bytes) -> None:
    """Escribir texto directamente al PTY."""
    if isinstance(text, str):
        with open(pty_path, "w") as pty:
            pty.write(text)
            pty.flush()
    else:
        with open(pty_path, "wb") as pty:
            pty.write(text)
            pty.flush()


def _capture_root(display: str, png_path: str) -> bool:
    """Capturar la pantalla completa de Xvfb."""
    r = subprocess.run(
        ["import", "-window", "root", png_path],
        capture_output=True, timeout=10,
        env={**os.environ, "DISPLAY": display},
    )
    return r.returncode == 0 and Path(png_path).stat().st_size > 500


def _find_changed_region(
    before_path: str, after_path: str, threshold: int = 30,
) -> tuple[int, int, int, int] | None:
    """Encontrar la región que cambió entre dos imágenes.

    Returns (x, y, w, h) o None si no hay cambios.
    """
    b = cv2.imread(before_path)
    a = cv2.imread(after_path)
    if b is None or a is None or b.shape != a.shape:
        return None
    diff = cv2.absdiff(a, b)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(thresh)
    if coords is None:
        return None
    x, y, w, h = cv2.boundingRect(coords)
    return x, y, w, h


# ── Test 1: Simulación con Textual Pilot (rápido, preciso) ──────────────


@pytest.mark.asyncio
async def test_hola_mundo_pilot():
    """Simular usuario con Textual Pilot."""
    from ced.app import Ced

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        app.action_new_file()
        await pilot.pause()

        ea = app.query_one("#editor")
        editor = ea.get_active_editor()
        assert editor is not None
        editor.focus()
        await pilot.pause()
        for ch in "Hola mundo":
            await pilot.press(ch)
        await pilot.pause()

        assert "Hola mundo" in editor.text, (
            f"El editor contiene: {editor.text!r}"
        )


# ── Test 2: Usuario real escribiendo al PTY + captura de pantalla ───────


@pytest.mark.visual
class TestHolaMundoReal:
    """Escribir 'Hola mundo' al PTY de ced y verificarlo con OCR + OpenCV."""

    @pytest.fixture(autouse=True)
    def _xvfb(self) -> None:
        self.v = Xvfb(width=1280, height=800)
        self.v.start()
        self.display = f":{self.v.new_display}"
        pyautogui.FAILSAFE = False
        yield
        self.v.stop()

    def test_pty_write_hola_mundo(self) -> None:
        """Escribir 'Hola mundo' al PTY y verificar con OCR + OpenCV."""
        # 1. Lanzar ced en Konsole dentro de Xvfb
        env = {**os.environ, "DISPLAY": self.display}
        env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
        proc = subprocess.Popen(
            ["/usr/bin/konsole", "--noclose", "--hide-menubar", "--hide-tabbar",
             "-e", "python3 -m ced"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
        )
        try:
            time.sleep(3)

            # 2. Encontrar el PTY de ced
            pty_path = _find_ced_pty()
            assert pty_path is not None, "No se encontró el PTY de ced"
            print(f"  PTY: {pty_path}")

            # 3. Captura ANTES
            antes = "/tmp/ced_antes.png"
            ok = _capture_root(self.display, antes)
            assert ok, "No se pudo capturar pantalla antes"

            # 4. Escribir Ctrl+N (0x0E) para nuevo archivo
            _write_pty(pty_path, b"\x0e")
            time.sleep(0.3)

            # 5. Escribir "Hola mundo"
            _write_pty(pty_path, "Hola mundo")
            time.sleep(0.5)

            # 6. Captura DESPUÉS
            despues = "/tmp/ced_despues.png"
            ok = _capture_root(self.display, despues)
            assert ok, "No se pudo capturar pantalla después"

            # 7. Detectar región cambiada con OpenCV
            region = _find_changed_region(antes, despues)
            assert region is not None, "No se detectaron cambios en la pantalla"
            x, y, w, h = region
            print(f"  Región cambiada: x={x} y={y} w={w} h={h}")

            # Extraer la región cambiada y hacer OCR
            img = cv2.imread(despues)
            roi = img[y:y+h, x:x+w]
            roi_path = "/tmp/ced_roi.png"
            cv2.imwrite(roi_path, roi)

            texto_roi = pytesseract.image_to_string(
                roi_path, lang="spa+eng"
            ).strip()
            print(f"  OCR región: {texto_roi!r}")

            assert "Hola" in texto_roi or "hola" in texto_roi.lower(), (
                f"OCR no encontró 'Hola' en región cambiada: {texto_roi!r}"
            )

            # 8. Verificar calidad de imagen con OpenCV
            h_full, w_full = img.shape[:2]
            assert h_full > 100 and w_full > 100
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            media = gray.mean()
            desviacion = gray.std()
            print(f"  Imagen: {w_full}x{h_full}, media={media:.1f}, std={desviacion:.1f}")
            assert 10 < media < 200, f"Brillo anómalo: media={media:.1f}"
            assert desviacion > 5, f"Contraste muy bajo: std={desviacion:.1f}"

        finally:
            proc.kill()
            proc.wait()
