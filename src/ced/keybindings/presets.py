from __future__ import annotations

from typing import Literal

from textual.binding import Binding as TextualBinding

KeybindingPreset = Literal["vscode", "nano", "sublime", "emacs"]

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
        TextualBinding("ctrl+o", "open", "Open File"),
        TextualBinding("ctrl+n", "new_file", "New File"),
        TextualBinding("ctrl+tab", "next_tab", "Next Tab"),
        TextualBinding("ctrl+shift+tab", "prev_tab", "Previous Tab"),
        TextualBinding("ctrl+`", "focus_terminal", "Focus Terminal"),
        TextualBinding("ctrl+j", "toggle_panel", "Toggle Panel"),
        TextualBinding("ctrl+d", "delete_line", "Delete Line"),
        TextualBinding("ctrl+/", "toggle_comment", "Toggle Comment"),
    ],
    "nano": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+o", "save", "WriteOut"),
        TextualBinding("ctrl+w", "search", "WhereIs"),
        TextualBinding("ctrl+k", "delete_line", "Cut Text"),
        TextualBinding("ctrl+u", "paste", "Uncut Text"),
        TextualBinding("ctrl+g", "help", "Get Help"),
        TextualBinding("ctrl+x", "close_tab", "Exit"),
    ],
    "sublime": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+s", "save", "Save"),
        TextualBinding("ctrl+shift+p", "command_palette", "Command Palette"),
        TextualBinding("ctrl+p", "quick_open", "Goto Anything"),
        TextualBinding("ctrl+n", "new_file", "New File"),
        TextualBinding("ctrl+w", "close_tab", "Close Tab"),
        TextualBinding("ctrl+`", "toggle_panel", "Toggle Console"),
        TextualBinding("ctrl+shift+f", "search", "Find in Files"),
    ],
    "emacs": [
        TextualBinding("ctrl+q", "quit", "Quit", priority=True),
        TextualBinding("ctrl+x ctrl+s", "save", "Save"),
        TextualBinding("ctrl+x ctrl+f", "open", "Find File"),
        TextualBinding("ctrl+x ctrl+c", "close_tab", "Close"),
        TextualBinding("ctrl+s", "search", "ISearch Forward"),
        TextualBinding("ctrl+r", "search_backward", "ISearch Backward"),
    ],
}


def get_preset(name: KeybindingPreset) -> list[TextualBinding]:
    return PRESET_DEFINITIONS.get(name, PRESET_DEFINITIONS["vscode"])


def list_presets() -> list[str]:
    return list(PRESET_DEFINITIONS.keys())
