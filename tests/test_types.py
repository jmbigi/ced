from __future__ import annotations

from typing import get_args

from ced.types import KeybindingPreset, ThemeMode


class TestTypes:
    def test_theme_mode_values(self) -> None:
        args = get_args(ThemeMode)
        assert set(args) == {"auto", "dark", "light"}

    def test_keybinding_preset_values(self) -> None:
        args = get_args(KeybindingPreset)
        assert set(args) == {"vscode", "nano", "sublime", "emacs"}

    def test_theme_mode_type(self) -> None:
        t: ThemeMode = "dark"
        assert t == "dark"

    def test_keybinding_preset_type(self) -> None:
        p: KeybindingPreset = "vscode"
        assert p == "vscode"
