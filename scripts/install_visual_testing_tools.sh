#!/usr/bin/env bash
# Instalar todas las herramientas necesarias para pruebas visuales (PNG + OCR)
# Ejecutar: sudo bash scripts/install_visual_testing_tools.sh

set -euo pipefail

echo "=== Instalando herramientas para pruebas visuales PNG ==="

# Herramientas del sistema
echo "[1/4] Instalando dependencias del sistema..."
apt-get update -qq
apt-get install -y -qq \
    xvfb \
    xterm \
    xdotool \
    imagemagick \
    scrot \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    openbox \
    2>&1 | tail -3

# Herramientas Python
echo "[2/4] Instalando paquetes Python..."
pip install -q \
    pyautogui \
    opencv-python-headless \
    pytesseract \
    Pillow \
    keyboard \
    mouse \
    pygetwindow \
    xvfbwrapper \
    pytest-timeout \
    2>&1 | tail -3

# Verificar instalación
echo "[3/4] Verificando..."
which Xvfb xdotool import scrot tesseract 2>&1 | head -5
python3 -c "
import cv2, pyautogui, pytesseract, PIL
print('OpenCV:', cv2.__version__)
print('PyAutoGUI:', pyautogui.__version__)
print('Tesseract:', pytesseract.__version__)
print('Pillow:', PIL.__version__)
print('✓ Todos los paquetes instalados correctamente')
"

echo "[4/4] Prueba rápida: capturar pantalla virtual con Xvfb..."
Xvfb :99 -screen 0 1280x800x24 &
sleep 1
DISPLAY=:99 xterm -e "echo 'Hola Mundo - ced editor'" &
sleep 2
DISPLAY=:99 import -window root /tmp/test_capture.png
kill %1 2>/dev/null || true
if [ -f /tmp/test_capture.png ]; then
    echo "✓ Captura exitosa: /tmp/test_capture.png ($(stat -c%s /tmp/test_capture.png) bytes)"
    rm -f /tmp/test_capture.png
else
    echo "⚠️ La captura falló, revise la configuración"
fi

echo ""
echo "=== Instalación completada ==="
echo "Ejecute 'python -m pytest tests/test_visual_png.py -v' para probar"
