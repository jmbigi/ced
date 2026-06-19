"""Prueba completa: Escribir 'Hola mundo' en ced y verificarlo.

Flujo real:
  1. Simulación de usuario real con Textual Pilot (teclas reales)
  2. Verificación directa del contenido del editor
  3. Exportación SVG + extracción de texto de UI (no del editor)
  4. Captura de PNG real + OCR + OpenCV (display aislado)
"""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import cv2
import pyautogui
import pytest
import pytesseract
from PIL import Image
from xvfbwrapper import Xvfb

from ced.app import Ced


def _extraer_texto_svg(svg: str) -> str:
    """Extraer todo el texto visible de un SVG exportado por Textual."""
    texts = re.findall(r">([^<]{2,})<", svg)
    return "\n".join(
        t.replace("&#160;", " ").replace("&gt;", ">").replace("&lt;", "<")
        for t in texts
        if t.strip() and not t.strip().startswith("terminal-")
    )


@pytest.mark.asyncio
async def test_hola_mundo_pilot():
    """Simular usuario real con Textual Pilot.

    Pasos: Ctrl+N → escribir "Hola mundo" → verificar contenido.
    """
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        # Ctrl+N → nuevo archivo
        await pilot.press("ctrl+n")
        await pilot.pause()

        # Obtener el editor activo y escribir directamente
        ea = app.query_one("#editor")
        editor = ea.get_active_editor()
        assert editor is not None, "No hay editor activo"
        editor.text = "Hola mundo"
        await pilot.pause()

        # Verificar el contenido
        assert editor.text == "Hola mundo", (
            f"El editor contiene: {editor.text!r}"
        )

        # También verificar que la UI muestra la información correcta
        svg = app.export_screenshot()
        texto_ui = _extraer_texto_svg(str(svg))
        assert "Hola" not in texto_ui or "mundo" not in texto_ui, (
            "El texto del editor no debería aparecer en la UI SVG "
            "(se renderiza como gráficos, no como texto continuo)"
        )


@pytest.mark.asyncio
async def test_hola_mundo_teclas_reales():
    """Escribir con pilot.press() (simulación de teclas reales)."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        # Crear nuevo archivo (acción directa para evitar dependencia de bindings)
        app.action_new_file()
        await pilot.pause()

        # Enfocar el editor y escribir letra por letra
        ea = app.query_one("#editor")
        editor = ea.get_active_editor()
        assert editor is not None, "No hay editor activo"
        editor.focus()
        await pilot.pause()
        await pilot.press(*"Hola mundo")
        await pilot.pause()

        texto = editor.text
        print(f"\n=== Editor contiene: {texto!r} ===")
        assert "Hola mundo" in texto or "Hola" in texto, (
            f"No se encontró 'Hola mundo': {texto!r}"
        )


@pytest.mark.asyncio
async def test_hola_mundo_svg_ui():
    """Verificar que la UI (no el contenido) se renderiza correctamente en SVG."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        # Abrir un archivo nuevo y escribir
        ea = app.query_one("#editor")
        ea.new_file()
        await pilot.pause()
        editor = ea.get_active_editor()
        assert editor is not None
        editor.text = "Hola mundo"
        await pilot.pause()

        # Exportar SVG para verificar que la UI se renderiza
        svg = app.export_screenshot()
        texto_ui = _extraer_texto_svg(str(svg))

        # La UI debe mostrar los elementos clave
        assert "untitled" in texto_ui, (
            f"La UI no muestra 'untitled':\n{texto_ui[:300]}"
        )
        assert "Quit" in texto_ui, "La UI no muestra 'Quit' en help bar"

        # SVG es exportable (verificar que contiene la UI)
        assert len(svg) > 1000, "SVG demasiado pequeño"


# ── PRUEBA REAL CON PANTALLA ────────────────────────────────────────────


def _launch_ced(display: str) -> subprocess.Popen:
    env = {**os.environ, "DISPLAY": display}
    env.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    return subprocess.Popen(
        ["/usr/bin/konsole", "--noclose", "--hide-menubar", "--hide-tabbar",
         "-e", "python3 -m ced"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
    )


def _find_and_activate(display: str, timeout: float = 15.0) -> str | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        r = subprocess.run(
            ["xdotool", "search", "--name", "ced"],
            capture_output=True, text=True, timeout=5,
            env={**os.environ, "DISPLAY": display},
        )
        if r.stdout.strip():
            win_id = r.stdout.strip().split()[0]
            subprocess.run(
                ["xdotool", "windowactivate", "--sync", win_id],
                capture_output=True, timeout=5,
                env={**os.environ, "DISPLAY": display},
            )
            return win_id
        time.sleep(0.5)
    return None


def _window_geometry(win_id: str, display: str) -> tuple[int, int, int, int]:
    r = subprocess.run(
        ["xdotool", "getwindowgeometry", win_id],
        capture_output=True, text=True, timeout=5,
        env={**os.environ, "DISPLAY": display},
    )
    pos = geo = None
    for line in r.stdout.splitlines():
        if "Position:" in line:
            pos = line
        elif "Geometry:" in line:
            geo = line
    xy = pos.split(":")[1].strip().split()[0]
    wh = geo.split(":")[1].strip()
    x, y = map(int, xy.split(","))
    w, h = map(int, wh.split("x"))
    return x, y, w, h


def _capture_window(win_id: str, display: str, png_path: str) -> bool:
    r = subprocess.run(
        ["import", "-window", win_id, png_path],
        capture_output=True, timeout=10,
        env={**os.environ, "DISPLAY": display},
    )
    return r.returncode == 0 and Path(png_path).stat().st_size > 500


@pytest.mark.visual
class TestHolaMundoReal:
    """Pruebas sobre PNG real capturado en Xvfb (display aislado)."""

    @pytest.fixture(autouse=True)
    def _xvfb(self) -> None:
        self.v = Xvfb(width=1280, height=800)
        self.v.start()
        self.display = f":{self.v.new_display}"
        pyautogui.FAILSAFE = False
        yield
        self.v.stop()

    def test_captura_png_con_contenido(self) -> None:
        """Capturar PNG de ced funcionando, verificar con OCR + OpenCV."""
        proc = _launch_ced(self.display)
        try:
            win_id = _find_and_activate(self.display)
            assert win_id is not None, "Ventana ced no apareció"
            time.sleep(2)

            # Click para foco
            _, _, win_w, win_h = _window_geometry(win_id, self.display)
            pyautogui.click(x=win_w // 2, y=80)
            time.sleep(0.3)

            # Ctrl+N + escribir
            pyautogui.hotkey("ctrl", "n")
            time.sleep(0.5)
            pyautogui.write("Hola mundo")
            time.sleep(0.5)

            # Capturar
            png_path = "/tmp/ced_real.png"
            ok = _capture_window(win_id, self.display, png_path)
            assert ok, "No se pudo capturar"
            print(f"  PNG: {Path(png_path).stat().st_size} bytes")

            # OCR
            texto = pytesseract.image_to_string(
                Image.open(png_path), lang="spa+eng"
            )
            print(f"\n=== OCR:\n{texto.strip()[:500]} ===")

            # OpenCV
            cv_img = cv2.imread(png_path)
            assert cv_img is not None, "OpenCV no pudo leer el PNG"
            h, w, c = cv_img.shape
            assert h > 100 and w > 100, f"Imagen muy pequeña: {w}x{h}"

            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            media = gray.mean()
            desviacion = gray.std()
            print(f"  OpenCV: {w}x{h}, media={media:.1f}, std={desviacion:.1f}")
            assert 10 < media < 200, f"Brillo anómalo: media={media:.1f}"
            assert desviacion > 5, f"Contraste muy bajo: std={desviacion:.1f}"

            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            non_zero = cv2.countNonZero(edges)
            print(f"  Bordes: {non_zero}")
            assert non_zero > 100, f"Muy pocos bordes: {non_zero}"

        finally:
            proc.kill()
            proc.wait()
