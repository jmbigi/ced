from __future__ import annotations

import asyncio
import re
import signal
import sys
from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingsMap
from textual.widgets import Input
from textual.containers import Horizontal, Vertical

from ced.config import Config
from ced.commands import CommandRegistry, Command
from ced.i18n import _, setup_i18n
from ced.panels.file_tree import FileTreePanel
from ced.panels.editor_area import EditorArea, EditorSettings
from ced.panels.opencode_panel import OpenCodePanel
from ced.panels.help_bar import HelpBar
from ced.panels.palette import CommandPalette
from ced.panels.quick_open import QuickOpen
from ced.panels.search_bar import SearchBar

from ced.panels.jump import JumpMode
from ced.panels.terminal import TerminalPanel
from ced.panels.confirm import ConfirmScreen, QuitConfirmScreen

from textual.theme import Theme

from ced.keybindings.manager import KeybindingManager
from ced.keybindings.presets import list_presets as list_keybinding_presets
from ced.types import ThemeMode
from ced.themes.manager import (
    list_themes,
    detect_dark_mode,
    get_theme_variables,
)


class Ced(App):
    """Main terminal code editor application."""

    TITLE = "ced"
    SUB_TITLE = "Terminal Code Editor"

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
        Binding("ctrl+t", "toggle_terminal", "Terminal"),
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+y", "redo", "Redo"),
    ]

    def __init__(self) -> None:
        super().__init__()
        setup_i18n()
        self.config = Config.load()
        self.commands = CommandRegistry()
        self._keybinding_manager = KeybindingManager(self.config.keybindings.preset)
        self._apply_keybindings()
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
            Command(
                "app.keybinding_next",
                "Switch to next keybinding preset",
                self.action_keybinding_next,
                "Preferences",
            ),
            Command(
                "app.keybinding_list",
                "List available keybinding presets",
                self.action_keybinding_list,
                "Preferences",
            ),
            Command("app.undo", "Undo last change", self.action_undo, "Edit"),
            Command("app.redo", "Redo last undone change", self.action_redo, "Edit"),
            Command(
                "app.toggle_terminal",
                "Toggle terminal panel (Ctrl+T)",
                self.action_toggle_terminal,
                "View",
            ),
        )

    def compose(self) -> ComposeResult:
        """Build the widget layout: sidebar, editor area, opencode panel, help bar."""
        with Horizontal():
            with Vertical(id="sidebar"):
                yield FileTreePanel(id="file-tree", tooltip="File tree sidebar (Ctrl+B)")
            with Vertical(id="editor-area"):
                yield EditorArea(
                    editor_settings=EditorSettings(
                        show_line_numbers=self.config.editor.line_numbers,
                        soft_wrap=self.config.editor.soft_wrap,
                        indent_width=self.config.editor.tab_size,
                    ),
                    id="editor",
                    tooltip="Code editor (Ctrl+N new file, Ctrl+S save)",
                )
                yield SearchBar(id="search-bar", tooltip="Search in file (Ctrl+F)")
                yield TerminalPanel(id="terminal", tooltip="Terminal panel (Ctrl+T)")
            with Vertical(id="opencode-panel"):
                yield OpenCodePanel(
                    opencode_path=self.config.opencode.path,
                    auto_start=self.config.opencode.auto_start,
                    id="opencode",
                    tooltip="OpenCode AI assistant (Ctrl+`)",
                )
        yield HelpBar(id="help-bar", tooltip="Keyboard shortcut bar")

    def _update_help_bar(self) -> None:
        key_map = {
            "ctrl+q": "^Q",
            "ctrl+s": "^S",
            "ctrl+p": "^P",
            "ctrl+f": "^F",
            "ctrl+b": "^B",
            "ctrl+n": "^N",
            "ctrl+w": "^W",
            "ctrl+h": "^H",
            "ctrl+j": "^J",
            "ctrl+o": "^O",
            "ctrl+x": "^X",
            "ctrl+g": "^G",
            "ctrl+t": "^T",
            "ctrl+z": "^Z",
            "ctrl+y": "^Y",
            "ctrl+grave_accent": "GRV",
            "ctrl+shift+tab": "S-TAB",
            "ctrl+tab": "TAB",
            "ctrl+shift+p": "S-P",
            "ctrl+shift+f": "S-F",
            "ctrl+x ctrl+s": "C-x C-s",
            "ctrl+x ctrl+f": "C-x C-f",
            "ctrl+x ctrl+c": "C-x C-c",
        }
        shortcuts = []
        seen = set()
        for b in self._keybinding_manager.bindings:
            if b.action in seen or b.action.endswith(("_list", "_next")):
                continue
            seen.add(b.action)
            display = key_map.get(b.key, b.key.upper().replace("control", "C"))
            shortcuts.append((display, b.description))
        self.query_one("#help-bar", HelpBar).set_shortcuts(shortcuts)

    def _apply_keybindings(self) -> None:
        self.__class__._merged_bindings = BindingsMap(self._keybinding_manager.bindings)
        if self._is_mounted:
            self.refresh_bindings()

    AUTOSAVE_INTERVAL = 300

    def on_mount(self) -> None:
        """Apply theme, update help bar, start autosave, and register SIGHUP handler."""
        self._apply_theme()
        self._update_help_bar()
        self.set_interval(self.AUTOSAVE_INTERVAL, self._autosave)
        if sys.platform != "win32":
            try:
                loop = asyncio.get_running_loop()
                loop.add_signal_handler(signal.SIGHUP, self.emergency_save_and_exit)
            except (ValueError, NotImplementedError):
                pass

    def _autosave(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        for buf in editor.buffers:
            if buf.is_modified:
                editor.save_all_modified()
                break

    def _apply_theme(self) -> None:
        mode: ThemeMode = self.config.theme.mode
        is_dark = detect_dark_mode() if mode == "auto" else mode == "dark"
        self.dark = is_dark
        theme_vars = get_theme_variables(self.config.theme.name)
        theme = Theme(
            name=self.config.theme.name,
            primary=theme_vars["primary"],
            secondary=theme_vars["secondary"],
            accent=theme_vars["accent"],
            foreground=theme_vars["text"],
            background=theme_vars["surface"],
            surface=theme_vars["surface"],
            boost=theme_vars["boost"],
            warning=theme_vars["warning"],
            error=theme_vars["error"],
            success=theme_vars["success"],
            dark=is_dark,
            variables={
                "text-muted": theme_vars["text-muted"],
                "input-cursor-background": theme_vars["primary"],
                "input-cursor-foreground": theme_vars["surface"],
                "input-cursor-text-style": "reverse",
            },
        )
        self.register_theme(theme)
        self.theme = self.config.theme.name

    def on_file_tree_panel_file_opened(self, event: FileTreePanel.FileOpened) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.open_file(event.path)
        event.stop()

    def action_quit(self) -> None:
        """Quit the application, prompting to save modified files."""
        editor = self.query_one("#editor", EditorArea)
        modified = [buf for buf in editor.buffers if buf.is_modified]
        if not modified:
            self.exit()
            return

        names = [buf.name for buf in modified]

        def _on_quit(result: str | None) -> None:
            if result == "save":
                editor.save_all_modified()
                self.exit()
            elif result == "discard":
                self.exit()

        self.push_screen(QuitConfirmScreen(names), _on_quit)

    def emergency_save_and_exit(self) -> None:
        """Save all modified buffers to disk and exit (called on SIGHUP)."""
        editor = self.query_one("#editor", EditorArea)
        recovery_dir = Path.home() / ".local" / "share" / "ced" / "recovery"
        recovery_dir.mkdir(parents=True, exist_ok=True)
        for i, buf in enumerate(editor.buffers):
            if not buf.is_modified:
                continue
            if i >= len(editor._tab_ids):
                continue
            name = editor._tab_ids[i].removeprefix("tab_")
            ed = editor._editors.get(name)
            if ed is None:
                continue
            if ed.file_path:
                try:
                    ed.save_file()
                    buf.mark_saved()
                except OSError:
                    pass
            else:
                try:
                    (recovery_dir / f"{name}.txt").write_text(
                        ed.text, encoding="utf-8"
                    )
                except OSError:
                    pass
        self.exit()

    def action_toggle_sidebar(self) -> None:
        self.query_one("#sidebar").display ^= True

    def action_toggle_terminal(self) -> None:
        self.query_one("#terminal").display ^= True
        if self.query_one("#terminal").display:
            self.query_one("#terminal").focus()

    def action_toggle_opencode(self) -> None:
        self.query_one("#opencode-panel").display ^= True
        if self.query_one("#opencode-panel").display:
            self.query_one("#opencode-input", Input).focus()

    def action_save(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        if not editor.save_active():
            active = editor.get_active_editor()
            if active and active.file_path:
                self.notify(
                    f"Cannot save {active.file_path.name}: permission denied",
                    severity="error", timeout=5,
                )
            else:
                self.notify(
                    _("Cannot save: file has no path. Use Ctrl+Shift+S to save as."),
                    severity="warning", timeout=5,
                )

    def action_close_tab(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        buf = editor.buffers.active_buffer
        if buf and buf.is_modified:

            def _on_confirm(result: bool) -> None:
                if result:
                    editor.close_active()

            self.push_screen(
                ConfirmScreen(
                    f"'{buf.name}' has unsaved changes. Close anyway?",
                    title="Unsaved Changes",
                ),
                _on_confirm,
            )
        else:
            editor.close_active()

    def action_open_file(self) -> None:
        self.query_one("#file-tree", FileTreePanel).focus()

    def action_new_file(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.new_file()

    def action_next_tab(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.tab_next()

    def action_prev_tab(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        editor.tab_prev()

    def action_undo(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        active = editor.get_active_editor()
        if active:
            active.undo()

    def action_redo(self) -> None:
        editor = self.query_one("#editor", EditorArea)
        active = editor.get_active_editor()
        if active:
            active.redo()

    def action_command_palette(self) -> None:
        commands = [
            (cmd.id, cmd.description, cmd.category) for cmd in self.commands.all()
        ]
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

    def on_search_bar_search_requested(self, event: SearchBar.SearchRequested) -> None:
        event.stop()
        editor = self.query_one("#editor", EditorArea)
        active = editor.get_active_editor()
        if active and event.query:
            text = active.text.lower()
            idx = text.find(event.query.lower())
            if idx >= 0:
                line = text[:idx].count("\n")
                col = idx - text[:idx].rfind("\n") - 1
                active.cursor_location = (line, col)

    def on_search_bar_replace_requested(
        self, event: SearchBar.ReplaceRequested
    ) -> None:
        event.stop()
        editor = self.query_one("#editor", EditorArea)
        active = editor.get_active_editor()
        if active and event.find:
            if event.all:
                pattern = re.compile(re.escape(event.find), re.IGNORECASE)
                active.text = pattern.sub(event.replace, active.text)
            else:
                idx = active.text.lower().find(event.find.lower())
                if idx >= 0:
                    before = active.text[:idx]
                    after = active.text[idx + len(event.find) :]
                    active.text = before + event.replace + after
                    line = before.count("\n")
                    col = idx - before.rfind("\n") - 1
                    active.cursor_location = (line, col + len(event.replace))

    def action_search(self) -> None:
        search_bar = self.query_one("#search-bar", SearchBar)
        search_bar.display = not search_bar.display
        if search_bar.display:
            search_bar.query_one("#find-input").focus()

    def action_search_replace(self) -> None:
        search_bar = self.query_one("#search-bar", SearchBar)
        search_bar.display = True
        search_bar.show_replace_ui(True)
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
        self._apply_theme()
        self.notify(f"{_('Theme:')} {next_theme}")

    def action_theme_list(self) -> None:
        themes = ", ".join(list_themes())
        self.notify(f"{_('Themes:')} {themes}", timeout=5)

    def action_keybinding_next(self) -> None:
        presets = list_keybinding_presets()
        current = self._keybinding_manager.current_preset
        try:
            i = presets.index(current)
        except ValueError:
            i = -1
        next_preset = presets[(i + 1) % len(presets)]
        self._keybinding_manager.set_preset(next_preset)
        self.config.keybindings.preset = next_preset
        self._apply_keybindings()
        self._update_help_bar()
        self.notify(f"{_('Keybindings:')} {next_preset}")

    def action_keybinding_list(self) -> None:
        presets = ", ".join(list_keybinding_presets())
        self.notify(f"Presets: {presets}", timeout=5)

    def action_help(self) -> None:
        shortcuts = "\n".join(
            f"  {b.key}  {b.description}"
            for b in self._keybinding_manager.bindings
            if not b.action.endswith("_list") and not b.action.endswith("_next")
        )
        self.notify(
            f"[bold]ced keybindings:[/bold]\n{shortcuts}",
            timeout=10,
        )
