from __future__ import annotations

import subprocess

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Input, RichLog
from textual.widget import Widget


class OpenCodePanel(Widget):
    DEFAULT_CSS = """
    OpenCodePanel {
        height: 100%;
        border: solid $primary;
    }

    OpenCodePanel > Vertical {
        height: 100%;
    }

    OpenCodePanel .panel-title {
        background: $accent;
        color: $surface;
        text-style: bold;
        padding: 0 1;
        height: 1;
    }

    OpenCodePanel RichLog {
        height: 1fr;
        padding: 0 1;
    }

    OpenCodePanel Input {
        dock: bottom;
        height: 1;
        margin: 0 1 1 1;
    }
    """

    def __init__(self, opencode_path: str = "opencode", auto_start: bool = True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._opencode_path = opencode_path
        self._auto_start = auto_start

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(" OpenCode AI ", classes="panel-title")
            yield RichLog(id="opencode-log", highlight=True, markup=True)
            yield Input(placeholder="Ask OpenCode...", id="opencode-input")

    def on_mount(self) -> None:
        if self._auto_start:
            self._check_opencode()

    @work(thread=True, exclusive=True)
    def _check_opencode(self) -> None:
        try:
            result = subprocess.run(
                [self._opencode_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self.app.call_from_thread(self._write_log, "[green]OpenCode ready[/green]")
            else:
                self.app.call_from_thread(
                    self._write_log,
                    f"[yellow]OpenCode found but responded: {result.stderr.strip()}[/yellow]",
                )
        except FileNotFoundError:
            self.app.call_from_thread(
                self._write_log,
                "[dim]OpenCode CLI not found. Install with: pip install opencode[/dim]",
            )
        except subprocess.TimeoutExpired:
            self.app.call_from_thread(self._write_log, "[red]OpenCode timed out[/red]")

    def _write_log(self, message: str) -> None:
        self.query_one("#opencode-log", RichLog).write(message)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "opencode-input":
            query = event.value
            if not query.strip():
                return
            event.input.clear()
            self._write_log(f"[bold]You:[/bold] {query}")
            self._query_opencode(query)

    @work(thread=True, exclusive=True)
    def _query_opencode(self, query: str) -> None:
        try:
            result = subprocess.run(
                [self._opencode_path, query], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self.app.call_from_thread(self._write_log, f"[primary]OpenCode:[/primary] {result.stdout.strip()}")
            else:
                self.app.call_from_thread(
                    self._write_log, f"[red]Error:[/red] {result.stderr.strip() or 'no output'}"
                )
        except FileNotFoundError:
            self.app.call_from_thread(self._write_log, "[red]OpenCode CLI not available[/red]")
        except subprocess.TimeoutExpired:
            self.app.call_from_thread(self._write_log, "[red]Request timed out[/red]")
        except Exception as exc:
            self.app.call_from_thread(self._write_log, f"[red]{exc}[/red]")
