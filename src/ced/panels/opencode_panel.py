from __future__ import annotations

import subprocess

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

    def __init__(self, opencode_path: str = "opencode", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._opencode_path = opencode_path

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(" OpenCode AI ", classes="panel-title")
            yield RichLog(id="opencode-log", highlight=True, markup=True)
            yield Input(placeholder="Ask OpenCode...", id="opencode-input")

    def on_mount(self) -> None:
        self._check_opencode()

    def _check_opencode(self) -> None:
        log = self.query_one("#opencode-log", RichLog)
        try:
            result = subprocess.run(
                [self._opencode_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                log.write("[green]OpenCode ready[/green]")
            else:
                log.write(
                    f"[yellow]OpenCode found but responded: {result.stderr.strip()}[/yellow]"
                )
        except FileNotFoundError:
            log.write(
                "[dim]OpenCode CLI not found. Install with: pip install opencode[/dim]"
            )
        except subprocess.TimeoutExpired:
            log.write("[red]OpenCode timed out[/red]")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "opencode-input":
            query = event.value
            if not query.strip():
                return
            event.input.clear()
            log = self.query_one("#opencode-log", RichLog)
            log.write(f"[bold]You:[/bold] {query}")
            self._query_opencode(query, log)

    def _query_opencode(self, query: str, log: RichLog) -> None:
        try:
            result = subprocess.run(
                [self._opencode_path, query], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                log.write(f"[primary]OpenCode:[/primary] {result.stdout.strip()}")
            else:
                log.write(f"[red]Error:[/red] {result.stderr.strip() or 'no output'}")
        except FileNotFoundError:
            log.write("[red]OpenCode CLI not available[/red]")
        except subprocess.TimeoutExpired:
            log.write("[red]Request timed out[/red]")
        except Exception as exc:
            log.write(f"[red]{exc}[/red]")
