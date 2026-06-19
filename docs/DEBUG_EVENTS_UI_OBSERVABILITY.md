# Debug UI Events — Observabilidad para Testing de GUI

**Paradigma RR-81 (mandatorio DeepPilot).** Transforma ejecución opaca de
tests gráficos en diagnóstico transparente en tiempo real.

## Índice

1. [Fundamento](#1-fundamento)
2. [Niveles de depuración](#2-niveles-de-depuración)
3. [Activación](#3-activación)
4. [Formato de salida](#4-formato-de-salida)
5. [Captura de eventos](#5-captura-de-eventos)
6. [Widget dumps](#6-widget-dumps)
7. [Screenshots automáticos](#7-screenshots-automáticos)
8. [Race condition detection](#8-race-condition-detection)
9. [Reconstrucción visual desde logs](#9-reconstrucción-visual-desde-logs)
10. [Integración con tests existentes](#10-integración-con-tests-existentes)
11. [Referencia rápida](#11-referencia-rápida)

---

## 1. Fundamento

Los tests de interfaz gráfica son inherentemente opacos: una aserción
falla pero no se sabe en qué estado quedó la UI, qué eventos se
dispararon, ni qué widgets estaban visibles.

`--debug-ui-events` resuelve esto inyectando hooks de observabilidad en
el loop de eventos de Textual antes de cada test. Cada pulsación de
tecla, click, cambio de estado, montaje/desmontaje de widget y
transición de pantalla queda registrado con timestamp de microsegundos.

Cuando un test falla, el log contiene la secuencia completa de eventos
que llevaron al fallo, más screenshots automáticos del estado final de
la UI.

---

## 2. Niveles de depuración

| Nivel | Flag | Eventos capturados |
|-------|------|-------------------|
| **minimal** | `--debug-ui-events=minimal` | Solo clicks y key presses |
| **standard** | `--debug-ui-events=standard` | minimal + cambios de estado + montaje/desmontaje |
| **verbose** | `--debug-ui-events=verbose` | standard + stack traces + widget dumps |
| **full** | `--debug-ui-events=full` | verbose + screenshots automáticos + dump completo |

Por defecto es `standard`. En CI se recomienda `full`.

---

## 3. Activación

### 3.1 Línea de comandos

```bash
# Nivel básico
pytest tests/ --debug-ui-events=minimal

# Nivel completo (recomendado en CI)
pytest tests/ --debug-ui-events=full

# Solo tests visuales
pytest tests/test_hola_mundo.py -v --debug-ui-events=verbose
```

### 3.2 Variable de entorno

```bash
export CED_DEBUG_UI_EVENTS=full
pytest tests/
```

### 3.3 Configuración en pyproject.toml

```toml
[tool.pytest.ini_options]
addopts = "--debug-ui-events=full"
```

---

## 4. Formato de salida

Cada evento se escribe como una línea JSON en `stderr` con el siguiente
formato:

```json
{
  "event": "key_press",
  "level": "minimal",
  "timestamp": 1712345678.123456,
  "delta_us": 123,
  "test": "test_hola_mundo_pilot",
  "data": {
    "key": "ctrl+n",
    "widget": "EnhancedCodeEditor",
    "widget_id": "editor_untitled"
  }
}
```

### Campos comunes

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `event` | str | Nombre del evento |
| `level` | str | Nivel: minimal/standard/verbose/full |
| `timestamp` | float | Unix timestamp con microsegundos |
| `delta_us` | int | Microsegundos desde el evento anterior |
| `test` | str | Nombre del test actual |
| `data` | dict | Datos específicos del evento |

---

## 5. Captura de eventos

### 5.1 Key presses (minimal+)

Se captura toda pulsación de tecla enviada a través de `pilot.press()`,
incluyendo teclas combinadas (Ctrl+N, Shift+Tab, etc.).

```json
{
  "event": "key_press",
  "level": "minimal",
  "timestamp": 1712345678.123456,
  "data": {
    "key": "ctrl+n",
    "action": "new_file",
    "widget": "EnhancedCodeEditor",
    "widget_id": "editor_untitled"
  }
}
```

### 5.2 Mouse clicks (minimal+)

Cada click simulado con `pyautogui` o `xdotool`.

```json
{
  "event": "mouse_click",
  "level": "minimal",
  "timestamp": 1712345678.223456,
  "data": {
    "x": 455,
    "y": 150,
    "button": "left",
    "window": "ced"
  }
}
```

### 5.3 State changes (standard+)

Cambios en el estado de la aplicación: apertura/cierre de archivos,
cambio de tabs, toggle de sidebar, cambio de tema.

```json
{
  "event": "state_change",
  "level": "standard",
  "timestamp": 1712345678.323456,
  "data": {
    "type": "file_opened",
    "path": "/tmp/test.py",
    "buffer_count": 2
  }
}
```

### 5.4 Mount/unmount (standard+)

Montaje y desmontaje de widgets en el árbol.

```json
{
  "event": "widget_mount",
  "level": "standard",
  "timestamp": 1712345678.423456,
  "data": {
    "widget": "TabPane",
    "widget_id": "tab_test_py",
    "parent": "TabbedContent"
  }
}
```

### 5.5 Screen transitions (standard+)

Pushes y pops de pantallas modales (CommandPalette, QuickOpen, JumpMode,
ConfirmScreen).

```json
{
  "event": "screen_push",
  "level": "standard",
  "timestamp": 1712345678.523456,
  "data": {
    "screen": "CommandPalette",
    "stack_depth": 2
  }
}
```

### 5.6 Stack traces (verbose+)

En cada evento se incluye un stack trace resumido que indica qué línea
del test generó el evento.

```json
{
  "event": "key_press",
  "level": "verbose",
  "timestamp": 1712345678.123456,
  "data": {
    "key": "ctrl+n",
    "stack": [
      "test_hola_mundo_pilot:45",
      "pilot.press:230"
    ]
  }
}
```

---

## 6. Widget dumps (verbose+)

Al iniciar y finalizar cada test, y en cada aserción, se genera un dump
del árbol de widgets con su estado: posición, visibilidad, foco, clases
CSS y pseudo-classes.

Formato:

```
Screen: Ced [120x40]
  Horizontal #layout [120x40]
    Vertical #sidebar [28x40] visible=True
      FileTreePanel #file-tree [28x39] focus=True
    Vertical #editor-area [62x40] visible=True
      EditorArea #editor [62x39]
        TabbedContent [62x39]
          TabPane #tab_untitled [62x39]
            EnhancedCodeEditor #editor_untitled [62x38]
    Vertical #opencode-panel [30x40] visible=True
      OpenCodePanel #opencode [30x39]
        Static .panel-title [30x1] = " OpenCode AI "
        RichLog #opencode-log [30x22]
        Input #opencode-input [30x1]
  HelpBar #help-bar [120x1] visible=True
    Static #help-text [120x1] = "^Q Quit  ^S Save..."
```

---

## 7. Screenshots automáticos (full)

En nivel `full` se captura automáticamente:

1. **Antes de cada test**: screenshot del estado inicial
2. **Después de cada test**: screenshot del estado final
3. **En cada aserción fallida**: screenshot del momento exacto del fallo
4. **Cada 50 eventos**: screenshot intermedio

Los screenshots se guardan en `.debug_ui_events/` con nombre:
```
test_name__event_count__timestamp.png
```

---

## 8. Race condition detection

El sistema detecta automáticamente:

- **Eventos fuera de orden**: timestamps que indican que eventos se
  procesaron en orden incorrecto
- **Múltiples screens activos**: cuando el stack de screens tiene más
  de una pantalla en un estado inesperado
- **Widgets montados pero no visibles**: widgets en el árbol con
  `display=False` que deberían estar visibles
- **Timeout de eventos**: si un evento esperado no ocurre dentro de
  un período (por defecto 5s)

```json
{
  "event": "race_condition",
  "level": "standard",
  "timestamp": 1712345678.823456,
  "data": {
    "type": "out_of_order_events",
    "expected": "key_press",
    "received": "screen_pop",
    "sequence": ["key_press", "key_press", "screen_pop"]
  }
}
```

---

## 9. Reconstrucción visual desde logs

El log en formato JSON puede ser procesado con la herramienta
`scripts/replay_ui_events.py` para reconstruir visualmente la sesión:

```bash
# Reproducir un log completo
python scripts/replay_ui_events.py .debug_ui_events/test_hola_mundo.json

# Generar video de la sesión (requiere ffmpeg)
python scripts/replay_ui_events.py .debug_ui_events/test_hola_mundo.json --video
```

La reconstrucción muestra:
- Ventana de terminal con la UI en cada paso
- Timeline de eventos sincronizada
- Widget tree en cada punto
- Diferencia visual entre cada paso

---

## 10. Integración con tests existentes

### 10.1 Tests asyncio con Textual Pilot

Los tests que usan `pilot.press()` ya capturan eventos automáticamente.
No requieren cambios.

```python
@pytest.mark.asyncio
async def test_hola_mundo_pilot(debug_ui_events):
    app = Ced()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_new_file()
        await pilot.pause()
        for ch in "Hola mundo":
            await pilot.press(ch)
        # Todos los key_press quedan registrados en el log
```

### 10.2 Tests visuales con Xvfb

Los tests que usan Xvfb + pyautogui también son soportados:

```python
@pytest.mark.visual
class TestVisualPNG:
    def test_captura_pantalla(self, debug_ui_events):
        # Los eventos de pyautogui y xdotool se registran
        pyautogui.click(x=400, y=200)
        pyautogui.write("Hola mundo")
```

### 10.3 Assertions con captura automática

Cuando una aserción falla en nivel `full`, se captura screenshot
automático y dump del árbol de widgets:

```python
class TestWithAutoCapture:
    def test_algo(self, debug_ui_events):
        # Si esto falla, se captura screenshot + widget dump
        assert False, "Fallo intencional"
        # Archivos generados:
        #   .debug_ui_events/test_algo__assert__1712345678.png
        #   .debug_ui_events/test_algo__assert__1712345678_widgets.txt
```

---

## 11. Implementación

El sistema se compone de tres módulos:

### 11.1 `tests/conftest.py`

Añade el flag `--debug-ui-events` a pytest e inyecta el fixture
`debug_ui_events` en todos los tests.

### 11.2 `tests/debug_ui_events.py`

Contiene la clase `DebugUIEventHandler` que:

- Se suscribe al bus de eventos de Textual
- Serializa cada evento a JSON con timestamp
- Detecta race conditions
- Gestiona screenshots automáticos
- Escribe el log a archivo

### 11.3 `tests/helpers.py`

Se extiende con las funciones:

- `capture_svg()` — ya existente
- `capture_png()` — ya existente
- `widget_tree_dump()` — nueva: serializa el árbol de widgets
- `format_event_json()` — nueva: formatea evento para log

---

## 12. Referencia rápida

```bash
# Ejecutar con depuración completa
pytest tests/test_hola_mundo.py -v --debug-ui-events=full

# Ver logs generados
cat .debug_ui_events/test_hola_mundo_pilot.json

# Nivel mínimo (solo teclas y clicks)
pytest tests/test_hola_mundo.py --debug-ui-events=minimal

# Con variable de entorno
CED_DEBUG_UI_EVENTS=verbose pytest tests/test_hola_mundo.py

# En CI (recomendado)
pytest tests/ --debug-ui-events=full --tb=long
```

---

## Apéndice A: Estructura de directorios

Los logs se generan en `.debug_ui_events/` dentro del directorio raíz
del proyecto:

```
.ced/
.debug_ui_events/
├── test_hola_mundo_pilot.json
├── test_hola_mundo_pilot__001__1712345678.png
├── test_hola_mundo_pilot__002__1712345680.png
├── test_hola_mundo_pilot__003__1712345682.png
├── test_vision_svg_shows_help_bar.json
└── test_vision_svg_shows_help_bar__001__1712345690.png
```

---

## Apéndice B: Código de ejemplo del fixture

El fixture `debug_ui_events` se define en `conftest.py`:

```python
@pytest.fixture
def debug_ui_events(request, worker_id):
    """Fixture que activa la observabilidad UI para el test actual.
    Se inyecta automáticamente si --debug-ui-events está activo.
    """
    level = request.config.getoption("--debug-ui-events")
    if not level:
        yield None
        return
    handler = DebugUIEventHandler(
        test_name=request.node.name,
        level=level,
        worker_id=worker_id,
    )
    handler.start()
    yield handler
    handler.stop()
    handler.write_log()
```

---

## Apéndice C: Integración con DeepPilot

Este sistema es mandatorio en todo proyecto con interfaz gráfica según
la especificación RR-81 de DeepPilot. DeepPilot debe:

1. Proponer este paradigma activamente
2. Generar tests con soporte nativo de `--debug-ui-events`
3. Capturar eventos Qt/Tkinter/GTK/Electron (según corresponda)
4. Incluir timestamps de microsegundos en todos los eventos
5. Detectar race conditions automáticamente
6. Permitir reconstrucción visual desde logs
7. Documentar el sistema en este archivo (mínimo 473 líneas)
