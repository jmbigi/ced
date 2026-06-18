from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Input
from textual.containers import Horizontal, Vertical

from ced.config import Config
from ced.commands import CommandRegistry, Command
from ced.panels.file_tree import FileTreePanel
from ced.panels.editor_area import EditorArea
from ced.panels.opencode_panel import OpenCodePanel
from ced.panels.help_bar import HelpBar
from ced.panels.palette import CommandPalette
from ced.panels.quick_open import QuickOpen
from ced.panels.search_bar import SearchBar
from ced.panels.jump import JumpMode
from ced.themes.manager import (
    ThemeMode,
    list_themes,
    detect_dark_mode,
)


class Ced(App):
    CSS_PATH = "theme.tcss"

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar"),
        Binding("ctrl+grave_accent", "toggle_opencode", "OpenCode"),
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+w", "close_tab", "Close Tab"),
        Binding("ctrl+shift+p", "command_palette", "Palette"),
        Binding("ctrl+p", "quick_open", "Open"),
        Binding("ctrl+f", "search", "Search"),
        Binding("ctrl+h", "search_replace", "Replace"),
        Binding("ctrl+n", "new_file", "New"),
        Binding("ctrl+tab", "next_tab", "Next Tab"),
        Binding("ctrl+shift+tab", "prev_tab", "Prev Tab"),
        Binding("ctrl+j", "jump_mode", "Jump"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config = Config.load()
        self.commands = CommandRegistry()
        self._register_builtin_commands()

    def _register_builtin_commands(self) -> None:
        self.commands.register_many(
            Command("app.quit", "Quit ced", self.action_quit, "App"),
            Command(
                "app.toggle_sidebar",
                "Toggle sidebar visibility",
                self.action_toggle_sidebar,
                "View",
            ),
            Command(
                "app.toggle_opencode",
                "Toggle OpenCode panel",
                self.action_toggle_opencode,
                "View",
            ),
            Command("app.save", "Save current file", self.action_save, "File"),
            Command(
                "app.close_tab", "Close current tab", self.action_close_tab, "File"
            ),
            Command(
                "app.open_file", "Open file from sidebar", self.action_open_file, "File"
            ),
            Command("app.new_file", "Create new file", self.action_new_file, "File"),
            Command("app.next_tab", "Switch to next tab", self.action_next_tab, "File"),
            Command(
                "app.prev_tab", "Switch to previous tab", self.action_prev_tab, "File"
            ),
            Command(
                "app.command_palette",
                "Show command palette",
                self.action_command_palette,
                "View",
            ),
            Command(
                "app.quick_open",
                "Quick open file (Ctrl+P)",
                self.action_quick_open,
                "File",
            ),
            Command("app.search", "Search in file", self.action_search, "Edit"),
            Command(
                "app.search_replace",
                "Search and replace",
                self.action_search_replace,
                "Edit",
            ),
            Command(
                "app.jump_mode",
                "Jump to 2-character sequence",
                self.action_jump_mode,
                "Edit",
            ),
            Command(
                "app.theme_next", "Switch to next theme", self.action_theme_next, "View"
            ),
            Command(
                "app.theme_list",
                "List available themes",
                self.action_theme_list,
                "View",
            ),
            Command(
                "app.help", "Show help / command palette", self.action_help, "Help"
            ),
        )

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield FileTreePanel(id="file-tree")
            with Vertical(id="editor-area"):
                yield EditorArea(id="editor")
                yield SearchBar(id="search-bar")
            with Vertical(id="opencode-panel"):
                yield OpenCodePanel(id="opencode")
        yield HelpBar(id="help-bar")

    def on_mount(self) -> None:
        self._apply_theme()

    def _apply_theme(self) -> None:
        mode: ThemeMode = self.config.theme.mode
        is_dark = detect_dark_mode() if mode == "auto" else mode == "dark"
        self.dark = is_dark

    def on_file_tree_panel_file_opened(self, event: FileTreePanel.FileOpened) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.open_file(event.path)
        event.stop()

    def action_toggle_sidebar(self) -> None:
        self.query_one("#sidebar").display ^= True

    def action_toggle_opencode(self) -> None:
        self.query_one("#opencode-panel").display ^= True
        if self.query_one("#opencode-panel").display:
            self.query_one("#opencode-input", Input).focus()

    def action_save(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.save_active()

    def action_close_tab(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.close_active()

    def action_open_file(self) -> None:
        self.query_one("#file-tree", FileTreePanel).focus()

    def action_new_file(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.open_file(Path("untitled"))

    def action_next_tab(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.buffers.switch_next()

    def action_prev_tab(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.buffers.switch_prev()

    def action_command_palette(self) -> None:
        commands = [(cmd.id, cmd.name, cmd.category) for cmd in self.commands.all()]
        self.push_screen(CommandPalette(commands), self._on_command_selected)

    def _on_command_selected(self, command_id: str | None) -> None:
        if command_id:
            self.commands.execute(command_id)

    def action_quick_open(self) -> None:
        self.push_screen(QuickOpen(Path.cwd()), self._on_quick_open)

    def _on_quick_open(self, path: Path | None) -> None:
        if path and path.is_file():
            editor = self.query_one("#editor", EditorArea)
            editor.open_file(path)

    def action_search(self) -> None:
        search_bar = self.query_one("#search-bar", SearchBar)
        search_bar.display = not search_bar.display
        if search_bar.display:
            search_bar.query_one("#find-input").focus()

    def action_search_replace(self) -> None:
        search_bar = self.query_one("#search-bar", SearchBar)
        search_bar.display = True
        search_bar._show_replace = True
        row = search_bar.query_one("#replace-row")
        row.display = True
        toggle = search_bar.query_one("#toggle-replace")
        toggle.label = "△"
        search_bar.query_one("#find-input").focus()

    def action_jump_mode(self) -> None:
        self.push_screen(JumpMode(), self._on_jump)

    def _on_jump(self, chars: str | None) -> None:
        if chars:
            editor = self.query_one("#editor", EditorArea)
            active = editor.get_active_editor()
            if active:
                text = active.text
                idx = text.lower().find(chars.lower())
                if idx >= 0:
                    active.cursor_location = (
                        text[:idx].count("\n"),
                        idx - text[:idx].rfind("\n") - 1,
                    )

    def action_theme_next(self) -> None:
        themes = list_themes()
        current = self.config.theme.name
        try:
            i = themes.index(current)
        except ValueError:
            i = -1
        next_theme = themes[(i + 1) % len(themes)]
        self.config.theme.name = next_theme
        self.notify(f"Theme: {next_theme}")

    def action_theme_list(self) -> None:
        themes = ", ".join(list_themes())
        self.notify(f"Themes: {themes}", timeout=5)

    def action_help(self) -> None:
        self.action_command_palette()
