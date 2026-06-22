from __future__ import annotations

from textual.binding import Binding

from ced.keybindings.presets import get_preset


class KeybindingManager:
    """Manages keybinding presets with support for custom overrides.

    Allows switching between presets (vscode, nano, sublime, emacs)
    and overriding individual bindings at runtime.
    """

    def __init__(self, preset_name: str = "vscode") -> None:
        self._current_preset = preset_name
        self._overrides: dict[str, Binding] = {}
        self._bindings: list[Binding] = []

    @property
    def current_preset(self) -> str:
        """Return the active preset name."""
        return self._current_preset

    @property
    def bindings(self) -> list[Binding]:
        """Return the current list of bindings (preset + overrides)."""
        return self._bindings

    def set_preset(self, name: str) -> None:
        """Switch to a different keybinding preset."""
        preset = get_preset(name)
        if preset is None:
            raise ValueError(f"Unknown preset: {name!r}")
        self._current_preset = name
        merged = list(preset)
        for action, override in self._overrides.items():
            for i, b in enumerate(merged):
                if b.action == action:
                    merged[i] = override
                    break
            else:
                merged.append(override)
        self._bindings = merged

    def override(self, action: str, binding: Binding) -> None:
        """Override a specific action's keybinding."""
        self._overrides[action] = binding
        self.set_preset(self._current_preset)

    def remove_override(self, action: str) -> None:
        """Remove a custom override for *action*."""
        self._overrides.pop(action, None)
        self.set_preset(self._current_preset)
