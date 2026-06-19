"""Prueba: Escribir 'Hola mundo' en el editor y verificarlo.

Tres enfoques complementarios:

1. **Textual Pilot** (${''}test_hola_mundo_pilot${''}) — simula teclas reales
   dentro del proceso, verifica el contenido directamente. Rápido y preciso.
   El foco se maneja correctamente porque Pilot opera dentro del árbol de
   widgets de Textual.

2. **Textual Pilot + SVG + OpenCV** (${''}test_hola_mundo_captura_png${''}) —
   igual que el anterior pero además exporta la pantalla a PNG, corre OCR
   sobre la imagen y verifica con OpenCV. La letra en terminal es pequeña
   para Tesseract, pero la imagen PNG demuestra que la UI se renderiza.

3. **PTY write** (${''}test_pty_write_hola_mundo${''}) — escribe al stdin real
   de ced (${'}'}/dev/pts/N) dentro de Konsole en Xvfb. El foco inicial está
   en el panel de archivos (file tree), por lo que el texto aparece allí y
   no en el editor. Este test es útil para verificar la captura de pantalla
   pero NO para probar la edición de texto.

El test que realmente verifica la escritura en el editor es el #1 y #2.
"""

from __future__ import annotations

import io
import os
import re
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

from ced.app import Ced

PNG_PATH = "/tmp/ced_hola_mundo.png"


# ── Test 1: Textual Pilot (rápido, dentro del proceso) ────────────────


@pytest.mark.asyncio
async def test_hola_mundo_pilot():
    """Simular teclas con Textual Pilot. Verificar contenido del editor."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        # Crear archivo nuevo y enfocar editor
        app.action_new_file()
        await pilot.pause()

        ea = app.query_one("#editor")
        editor = ea.get_active_editor()
        assert editor is not None
        editor.focus()
        await pilot.pause()

        # Escribir letra por letra (simula teclas reales)
        for ch in "Hola mundo":
            await pilot.press(ch)
        await pilot.pause()

        # Verificar
        assert "Hola mundo" in editor.text, (
            f"El editor contiene: {editor.text!r}"
        )


# ── Test 2: Pilot + SVG → PNG → OCR + OpenCV ─────────────────────────


@pytest.mark.asyncio
async def test_hola_mundo_captura_png():
    """Escribir con Pilot, exportar PNG, verificar con OCR y OpenCV.

    Este es el test más completo: usa simulación de teclas reales (Pilot),
    captura la pantalla como PNG (SVG → cairosvg), y verifica con OCR +
    OpenCV que la imagen es válida.
    """
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

        # Verificar contenido
        assert "Hola mundo" in editor.text, (
            f"El editor contiene: {editor.text!r}"
        )

        # Exportar SVG y convertir a PNG
        svg = app.export_screenshot()
        import cairosvg
        png_bytes = cairosvg.svg2png(bytestring=str(svg).encode("utf-8"))
        assert len(png_bytes) > 1000, "PNG demasiado pequeño"

        # OCR sobre el PNG
        texto = pytesseract.image_to_string(
            Image.open(io.BytesIO(png_bytes)), lang="spa+eng"
        )
        print(f"\n=== OCR PNG ===\n{texto[:500]}")

        # Verificar con OpenCV
        img = cv2.imdecode(
            np.frombuffer(png_bytes, np.uint8), cv2.IMREAD_GRAYSCALE
        )
        assert img is not None, "OpenCV no pudo decodificar el PNG"
        h, w = img.shape
        assert h > 100 and w > 100, f"Imagen muy pequeña: {w}x{h}"

        media = img.mean()
        desviacion = img.std()
        print(f"  OpenCV: {w}x{h}, media={media:.1f}, std={desviacion:.1f}")
        assert 10 < media < 200, f"Brillo anómalo: media={media:.1f}"
        assert desviacion > 5, f"Contraste muy bajo: std={desviacion:.1f}"


# ── Tests 3: PTY write + screenshot (Xvfb aislado) ────────────────────
# NOTA: El PTY write envía texto al stdin de ced. Como el foco inicial
# está en el file tree, el texto aparece allí, no en el editor.
# Estos tests capturan y verifican la pantalla pero NO demuestran
# escritura en el editor.


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
    if isinstance(text, str):
        with open(pty_path, "w") as pty:
            pty.write(text)
            pty.flush()
    else:
        with open(pty_path, "wb") as pty:
            pty.write(text)
            pty.flush()


def _capture_root(display: str, png_path: str) -> bool:
    r = subprocess.run(
        ["import", "-window", "root", png_path],
        capture_output=True, timeout=10,
        env={**os.environ, "DISPLAY": display},
    )
    return r.returncode == 0 and Path(png_path).stat().st_size > 500


def _find_changed_region(
    before_path: str, after_path: str, threshold: int = 30,
) -> tuple[int, int, int, int] | None:
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


@pytest.mark.visual
class TestPTYCapture:
    """Capturar pantalla en Xvfb y detectar cambios por PTY write.

    NOTA: El texto escrito al PTY aparece en el panel de archivos
    (file tree) porque tiene el foco inicial. Esto es un resultado
    esperado dado que el foco de Textual no se puede cambiar desde
    fuera del proceso.
    """

    @pytest.fixture(autouse=True)
    def _xvfb(self) -> None:
        self.v = Xvfb(width=1280, height=800)
        self.v.start()
        self.display = f":{self.v.new_display}"
        pyautogui.FAILSAFE = False
        yield
        self.v.stop()

    def test_pty_write_captura_pantalla(self) -> None:
        """Escribir al PTY y verificar que la captura de pantalla funciona."""
        env = {**os.environ, "DISPLAY": self.display}
        env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
        proc = subprocess.Popen(
            ["/usr/bin/konsole", "--noclose", "--hide-menubar", "--hide-tabbar",
             "-e", "python3 -m ced"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
        )
        try:
            time.sleep(3)
            pty_path = _find_ced_pty()
            assert pty_path is not None, "No se encontró el PTY de ced"

            antes = "/tmp/pty_antes.png"
            ok = _capture_root(self.display, antes)
            assert ok, "No se pudo capturar antes"

            _write_pty(pty_path, "Hola mundo")
            time.sleep(0.5)

            despues = "/tmp/pty_despues.png"
            ok = _capture_root(self.display, despues)
            assert ok, "No se pudo capturar después"

            region = _find_changed_region(antes, despues)
            assert region is not None, "No se detectaron cambios"
            x, y, w, h = region
            print(f"  Cambio en x={x} y={y} w={w} h={h}")

            img = cv2.imread(despues)
            h_full, w_full = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            media = gray.mean()
            desviacion = gray.std()
            print(f"  Imagen: {w_full}x{h_full}, media={media:.1f}, "
                  f"std={desviacion:.1f}")
            assert 10 < media < 200
            assert desviacion > 5
        finally:
            proc.kill()
            proc.wait()
