from __future__ import annotations

from textual.binding import Binding as TextualBinding

from ced.keybindings.presets import (
    KeybindingPreset,
    get_preset,
    list_presets,
)


class KeybindingManager:
    def __init__(self, preset_name: KeybindingPreset = "vscode") -> None:
        self._current_preset: KeybindingPreset = preset_name
        self._bindings: list[TextualBinding] = []
        self._custom_overrides: dict[str, TextualBinding] = {}
        self._update_bindings()

    @property
    def current_preset(self) -> KeybindingPreset:
        return self._current_preset

    @property
    def bindings(self) -> list[TextualBinding]:
        return list(self._bindings)

    def set_preset(self, name: KeybindingPreset) -> None:
        if name not in list_presets():
            raise ValueError(f"Unknown preset: {name!r}")
        self._current_preset = name
        self._update_bindings()

    def override(self, action: str, binding: TextualBinding) -> None:
        self._custom_overrides[action] = binding
        self._update_bindings()

    def remove_override(self, action: str) -> None:
        self._custom_overrides.pop(action, None)
        self._update_bindings()

    def get_presets_list(self) -> list[str]:
        return list_presets()

    def _update_bindings(self) -> None:
        preset_bindings = get_preset(self._current_preset)
        binding_map: dict[str, TextualBinding] = {}
        for b in preset_bindings:
            binding_map[b.action] = b
        for action, b in self._custom_overrides.items():
            binding_map[action] = b
        self._bindings = list(binding_map.values())
