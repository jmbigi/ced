from __future__ import annotations

import shutil
import subprocess

from textual import work
from textual.app import ComposeResult
from textual.widgets import Input, RichLog
from textual.widget import Widget
from textual.containers import Vertical


class OpenCodePanel(Widget):
    """AI assistant panel that interfaces with the OpenCode CLI."""

    DEFAULT_CSS = """
    OpenCodePanel {
        height: 100%;
        border: solid $primary;
        background: $surface;
        display: none;
    }

    #opencode-output {
        height: 1fr;
    }

    #opencode-input {
        dock: bottom;
        margin: 1;
    }
    """

    def __init__(
        self,
        opencode_path: str = "opencode",
        auto_start: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._opencode_path = opencode_path
        self._auto_start = auto_start
        self._available = False

    def compose(self) -> ComposeResult:
        """Yield the output log and input field."""
        with Vertical():
            yield RichLog(id="opencode-output", markup=True, wrap=True, highlight=True)
            yield Input(placeholder="Ask OpenCode...", id="opencode-input")

    def on_mount(self) -> None:
        """Check CLI availability on startup."""
        if self._auto_start:
            self._check_available()

    def _check_available(self) -> None:
        path = shutil.which(self._opencode_path)
        if path:
            self._available = True
            output = self.query_one("#opencode-output", RichLog)
            output.write(f"[green]OpenCode ready ({path})[/green]")
        else:
            self._available = False
            output = self.query_one("#opencode-output", RichLog)
            output.write(
                f"[red]opencode not found at {self._opencode_path!r}.[/red]\n"
                "Install it or set the path in config."
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Send the user's query to the OpenCode CLI."""
        if not self._available:
            self.query_one("#opencode-output", RichLog).write(
                "[red]OpenCode CLI is not available[/red]"
            )
            return
        query = event.value
        if not query:
            return
        inp = self.query_one("#opencode-input", Input)
        inp.value = ""
        output = self.query_one("#opencode-output", RichLog)
        output.write(f"[bold]>>> {query}[/bold]")
        self._run_query(query)

    @work(thread=True, exclusive=True)
    async def _run_query(self, query: str) -> None:
        try:
            result = subprocess.run(
                [self._opencode_path, query],
                capture_output=True, text=True, timeout=60,
            )
            response = result.stdout.strip() or result.stderr.strip()
        except subprocess.TimeoutExpired:
            response = "Query timed out after 60s"
        except FileNotFoundError:
            response = f"opencode CLI not found: {self._opencode_path}"
        except Exception as exc:
            response = f"Error: {exc}"

        self.app.call_from_thread(
            self.query_one("#opencode-output", RichLog).write, response
        )
