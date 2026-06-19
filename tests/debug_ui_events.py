"""Debug UI Events — Observabilidad en tiempo real para tests de GUI.

Implementación del paradigma RR-81. Captura eventos de UI durante la
ejecución de tests y los serializa a JSON con timestamps de microsegundos.

Niveles:
  - minimal:   clicks + key presses
  - standard:  minimal + state changes + mount/unmount + screen transitions
  - verbose:   standard + stack traces + widget dumps
  - full:      verbose + automatic screenshots + complete widget tree dump
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.nodes import Item


DEBUG_DIR = Path(".debug_ui_events")


# ── Event data ──────────────────────────────────────────────────────────


class UIEvent:
    """Un evento de UI capturado durante la ejecución de un test."""

    __slots__ = (
        "event", "level", "timestamp", "test", "data",
    )

    def __init__(
        self,
        event: str,
        level: str,
        test: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        self.event = event
        self.level = level
        self.timestamp = time.time()
        self.test = test
        self.data = data or {}

    def calc_delta_us(self, previous: float | None = None) -> int:
        """Microsegundos desde un evento anterior."""
        if previous is None:
            return 0
        return int((self.timestamp - previous) * 1_000_000)

    def to_dict(self, previous_timestamp: float | None = None) -> dict:
        d: dict[str, Any] = {
            "event": self.event,
            "level": self.level,
            "timestamp": self.timestamp,
            "delta_us": self.calc_delta_us(previous_timestamp),
            "test": self.test,
            "data": self.data,
        }
        return d


# ── Event handler ───────────────────────────────────────────────────────


class DebugUIEventHandler:
    """Maneja la captura y registro de eventos de UI para un test.

    Uso:
        handler = DebugUIEventHandler("test_name", "standard")
        handler.key_press("ctrl+n", widget="EnhancedCodeEditor")
        handler.state_change("file_opened", {"path": "/tmp/test.py"})
        handler.stop()
        handler.write_log()
    """

    def __init__(
        self,
        test_name: str,
        level: str = "standard",
        worker_id: str = "master",
        output_dir: str | Path = DEBUG_DIR,
    ) -> None:
        self.test_name = test_name
        self.level = level
        self.worker_id = worker_id
        self.output_dir = Path(output_dir)
        self._events: list[UIEvent] = []
        self._last_timestamp: float | None = None
        self._start_time: float | None = None
        self._screenshot_count = 0
        self._active = True

        LEVELS = {"minimal": 0, "standard": 1, "verbose": 2, "full": 3}
        self._level_num = LEVELS.get(level, 1)

    def start(self) -> None:
        """Iniciar captura de eventos."""
        self._start_time = time.time()
        self._events.clear()
        self._screenshot_count = 0
        self._active = True
        self._log("capture_started", "minimal", {
            "level": self.level,
            "time": self._start_time,
        })

    def stop(self) -> None:
        """Detener captura de eventos."""
        if not self._active:
            return
        self._active = False
        self._log("capture_stopped", "minimal", {
            "duration_s": round(time.time() - (self._start_time or 0), 3),
            "event_count": len(self._events),
        })

    def key_press(
        self,
        key: str,
        widget: str = "",
        widget_id: str = "",
        action: str = "",
    ) -> None:
        """Registrar una pulsación de tecla."""
        if not self._active or self._level_num < 0:
            return
        data: dict[str, Any] = {"key": key}
        if widget:
            data["widget"] = widget
        if widget_id:
            data["widget_id"] = widget_id
        if action:
            data["action"] = action
        if self._level_num >= 2:
            data["stack"] = self._capture_stack()
        self._log("key_press", "minimal", data)

    def mouse_click(
        self,
        x: int,
        y: int,
        button: str = "left",
        window: str = "",
    ) -> None:
        """Registrar un click de ratón."""
        if not self._active or self._level_num < 0:
            return
        data: dict[str, Any] = {"x": x, "y": y, "button": button}
        if window:
            data["window"] = window
        if self._level_num >= 2:
            data["stack"] = self._capture_stack()
        self._log("mouse_click", "minimal", data)

    def state_change(self, change_type: str, details: dict[str, Any]) -> None:
        """Registrar un cambio de estado en la aplicación."""
        if not self._active or self._level_num < 1:
            return
        data: dict[str, Any] = {"type": change_type}
        data.update(details)
        self._log("state_change", "standard", data)

    def widget_mount(
        self, widget: str, widget_id: str = "", parent: str = ""
    ) -> None:
        """Registrar montaje de un widget."""
        if not self._active or self._level_num < 1:
            return
        data: dict[str, Any] = {"widget": widget}
        if widget_id:
            data["widget_id"] = widget_id
        if parent:
            data["parent"] = parent
        if self._level_num >= 2:
            data["stack"] = self._capture_stack()
        self._log("widget_mount", "standard", data)

    def widget_unmount(
        self, widget: str, widget_id: str = ""
    ) -> None:
        """Registrar desmontaje de un widget."""
        if not self._active or self._level_num < 1:
            return
        data: dict[str, Any] = {"widget": widget}
        if widget_id:
            data["widget_id"] = widget_id
        if self._level_num >= 2:
            data["stack"] = self._capture_stack()
        self._log("widget_unmount", "standard", data)

    def screen_push(self, screen_name: str, stack_depth: int = 1) -> None:
        """Registrar push de una pantalla modal."""
        if not self._active or self._level_num < 1:
            return
        self._log("screen_push", "standard", {
            "screen": screen_name,
            "stack_depth": stack_depth,
        })

    def screen_pop(self, screen_name: str, stack_depth: int = 0) -> None:
        """Registrar pop de una pantalla modal."""
        if not self._active or self._level_num < 1:
            return
        self._log("screen_pop", "standard", {
            "screen": screen_name,
            "stack_depth": stack_depth,
        })

    def widget_tree_dump(self, tree_text: str) -> None:
        """Registrar dump del árbol de widgets."""
        if not self._active or self._level_num < 2:
            return
        self._log("widget_tree_dump", "verbose", {
            "tree": tree_text,
        })

    def screenshot(self, png_path: str | Path) -> None:
        """Registrar captura de screenshot."""
        if not self._active or self._level_num < 3:
            return
        self._screenshot_count += 1
        self._log("screenshot", "full", {
            "path": str(png_path),
            "index": self._screenshot_count,
        })

    def assertion(self, passed: bool, message: str = "") -> None:
        """Registrar una aserción."""
        if not self._active:
            return
        self._log(
            "assertion" if passed else "assertion_failed",
            "standard" if passed else "minimal",
            {"passed": passed, "message": message},
        )

    def race_condition(
        self,
        condition_type: str,
        details: dict[str, Any],
    ) -> None:
        """Registrar detección de race condition."""
        if not self._active or self._level_num < 1:
            return
        data: dict[str, Any] = {"type": condition_type}
        data.update(details)
        self._log("race_condition", "standard", data)

    def write_log(self) -> None:
        """Escribir el log completo a disco en formato JSON."""
        if not self._events:
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.output_dir / f"{self.test_name}.json"

        previous_ts: float | None = None
        serialized: list[dict] = []
        for ev in self._events:
            d = ev.to_dict(previous_ts)
            serialized.append(d)
            previous_ts = ev.timestamp

        log_data: dict[str, Any] = {
            "test": self.test_name,
            "level": self.level,
            "worker": self.worker_id,
            "event_count": len(serialized),
            "start_time": self._start_time,
            "end_time": time.time(),
            "events": serialized,
        }

        log_path.write_text(
            json.dumps(log_data, indent=2, default=str),
            encoding="utf-8",
        )

    def write_csv(self) -> None:
        """Escribir el log en formato CSV (alternativo)."""
        if not self._events:
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.output_dir / f"{self.test_name}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "delta_us", "event", "level", "data",
            ])
            previous_ts: float | None = None
            for ev in self._events:
                writer.writerow([
                    ev.timestamp,
                    ev.calc_delta_us(previous_ts),
                    ev.event,
                    ev.level,
                    json.dumps(ev.data, default=str),
                ])
                previous_ts = ev.timestamp

    # ── Internal ────────────────────────────────────────────────────────

    def _log(
        self,
        event: str,
        level: str,
        data: dict[str, Any],
    ) -> None:
        """Registrar un evento interno."""
        ev = UIEvent(event, level, self.test_name, data)
        ev.timestamp = time.time()
        self._events.append(ev)
        self._last_timestamp = ev.timestamp

    def _capture_stack(self) -> list[str]:
        """Capturar stack trace simplificado."""
        import traceback
        stack = traceback.extract_stack()
        # Filtrar llamadas internas del framework
        result: list[str] = []
        for frame in stack:
            fn = Path(frame.filename).name
            if any(
                skip in fn
                for skip in (
                    "debug_ui_events", "conftest.py",
                    "textual/", "pytest",
                )
            ):
                continue
            result.append(f"{fn}:{frame.lineno}")
            if len(result) >= 5:
                break
        return result


# ── Factory ─────────────────────────────────────────────────────────────


def create_handler_from_config(
    config: Config,
    test_name: str,
    worker_id: str = "master",
) -> DebugUIEventHandler | None:
    """Crear un DebugUIEventHandler desde la configuración de pytest.

    Retorna None si --debug-ui-events no está activo.
    """
    level = config.getoption("--debug-ui-events", default=None)
    if not level:
        return None
    if level not in ("minimal", "standard", "verbose", "full"):
        level = "standard"
    return DebugUIEventHandler(
        test_name=test_name,
        level=level,
        worker_id=worker_id,
    )
