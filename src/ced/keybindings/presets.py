from __future__ import annotations

from textual.binding import Binding as TextualBinding

from ced.types import KeybindingPreset

PRESET_DEFINITIONS: dict[str, list[TextualBinding]] = {
    "vscode": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+b", "toggle_sidebar", "Sidebar"),
        TextualBinding("ctrl+grave_accent", "toggle_opencode", "OpenCode"),
        TextualBinding("ctrl+s", "save", "Save"),
        TextualBinding("ctrl+w", "close_tab", "Close Tab"),
        TextualBinding("ctrl+shift+p", "command_palette", "Command Palette"),
        TextualBinding("ctrl+p", "quick_open", "Quick Open"),
        TextualBinding("ctrl+f", "search", "Search"),
        TextualBinding("ctrl+h", "search_replace", "Search & Replace"),
        TextualBinding("ctrl+o", "open_file", "Open File"),
        TextualBinding("ctrl+n", "new_file", "New File"),
        TextualBinding("ctrl+z", "undo", "Undo"),
        TextualBinding("ctrl+y", "redo", "Redo"),
        TextualBinding("ctrl+t", "toggle_terminal", "Terminal"),
        TextualBinding("ctrl+tab", "next_tab", "Next Tab"),
        TextualBinding("ctrl+shift+tab", "prev_tab", "Previous Tab"),
        TextualBinding("ctrl+j", "jump_mode", "Jump"),
    ],
    "nano": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+o", "save", "WriteOut"),
        TextualBinding("ctrl+w", "search", "WhereIs"),
        TextualBinding("ctrl+x", "close_tab", "Exit"),
        TextualBinding("ctrl+g", "help", "Get Help"),
    ],
    "sublime": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+s", "save", "Save"),
        TextualBinding("ctrl+shift+p", "command_palette", "Command Palette"),
        TextualBinding("ctrl+p", "quick_open", "Goto Anything"),
        TextualBinding("ctrl+n", "new_file", "New File"),
        TextualBinding("ctrl+w", "close_tab", "Close Tab"),
        TextualBinding("ctrl+z", "undo", "Undo"),
        TextualBinding("ctrl+y", "redo", "Redo"),
        TextualBinding("ctrl+shift+f", "search", "Find in Files"),
    ],
    "emacs": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+x ctrl+s", "save", "Save"),
        TextualBinding("ctrl+x ctrl+f", "quick_open", "Find File"),
        TextualBinding("ctrl+x ctrl+c", "close_tab", "Close"),
        TextualBinding("ctrl+s", "search", "ISearch Forward"),
        TextualBinding("ctrl+z", "undo", "Undo"),
        TextualBinding("ctrl+y", "redo", "Redo"),
    ],
}


def get_preset(name: KeybindingPreset) -> list[TextualBinding]:
    """Return the keybinding list for the named preset (defaults to vscode)."""
    return PRESET_DEFINITIONS.get(name, PRESET_DEFINITIONS["vscode"])


def list_presets() -> list[str]:
    """Return the names of all available keybinding presets."""
    return list(PRESET_DEFINITIONS.keys())
