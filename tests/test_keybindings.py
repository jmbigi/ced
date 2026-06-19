from __future__ import annotations

from ced.keybindings.presets import get_preset, list_presets
from ced.keybindings.manager import KeybindingManager


class TestPresets:
    def test_list_presets(self) -> None:
        presets = list_presets()
        assert "vscode" in presets
        assert "nano" in presets
        assert "sublime" in presets
        assert "emacs" in presets

    def test_get_vscode_preset(self) -> None:
        bindings = get_preset("vscode")
        actions = {b.action for b in bindings}
        assert "quit" in actions
        assert "save" in actions
        assert "search" in actions

    def test_get_nano_preset(self) -> None:
        bindings = get_preset("nano")
        actions = {b.action for b in bindings}
        assert "quit" in actions
        assert "save" in actions
        assert "search" in actions

    def test_get_sublime_preset(self) -> None:
        bindings = get_preset("sublime")
        actions = {b.action for b in bindings}
        assert "command_palette" in actions
        assert "quick_open" in actions

    def test_get_emacs_preset(self) -> None:
        bindings = get_preset("emacs")
        actions = {b.action for b in bindings}
        assert "save" in actions

    def test_get_unknown_preset_fallback(self) -> None:
        bindings = get_preset("unknown")
        assert len(bindings) > 0

    def test_all_presets_have_quit(self) -> None:
        for name in list_presets():
            bindings = get_preset(name)
            actions = {b.action for b in bindings}
            assert "quit" in actions, f"Preset {name!r} missing quit binding"


class TestKeybindingManager:
    def test_default_preset(self) -> None:
        mgr = KeybindingManager()
        assert mgr.current_preset == "vscode"

    def test_set_preset(self) -> None:
        mgr = KeybindingManager()
        mgr.set_preset("nano")
        assert mgr.current_preset == "nano"
        actions = {b.action for b in mgr.bindings}
        assert "save" in actions

    def test_set_invalid_preset_raises(self) -> None:
        mgr = KeybindingManager()
        try:
            mgr.set_preset("invalid")
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_override(self) -> None:
        mgr = KeybindingManager()
        from textual.binding import Binding
        custom = Binding("ctrl+y", "test_action", "Test")
        mgr.override("test_action", custom)
        actions = {b.action for b in mgr.bindings}
        assert "test_action" in actions

    def test_remove_override(self) -> None:
        mgr = KeybindingManager()
        from textual.binding import Binding
        custom = Binding("ctrl+y", "test_action", "Test")
        mgr.override("test_action", custom)
        mgr.remove_override("test_action")
        actions = {b.action for b in mgr.bindings}
        assert "test_action" not in actions


