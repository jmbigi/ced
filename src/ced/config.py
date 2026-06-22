from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from ced.types import KeybindingPreset, ThemeMode

VALID_THEME_MODES: set[str] = {"auto", "dark", "light"}
VALID_KEYBINDING_PRESETS: set[str] = {"vscode", "nano", "sublime", "emacs"}


@dataclass
class ThemeConfig:
    """Theme configuration: name, mode (auto/dark/light)."""

    mode: ThemeMode = "auto"
    name: str = "monokai"

    def __post_init__(self) -> None:
        if self.mode not in VALID_THEME_MODES:
            raise ValueError(f"Invalid theme mode: {self.mode!r}")


@dataclass
class EditorConfig:
    """Editor configuration: tabs, wrapping, line numbers, font."""

    tab_size: int = 4
    soft_wrap: bool = False
    line_numbers: bool = True
    indent_guides: bool = True
    font_size: int = 12
    show_minimap: bool = False

    def __post_init__(self) -> None:
        if self.tab_size < 1:
            self.tab_size = 4
        if self.font_size < 8:
            self.font_size = 12


@dataclass
class KeybindingConfig:
    """Keybinding preset configuration."""

    preset: KeybindingPreset = "vscode"

    def __post_init__(self) -> None:
        if self.preset not in VALID_KEYBINDING_PRESETS:
            raise ValueError(f"Invalid keybinding preset: {self.preset!r}")


@dataclass
class OpenCodeConfig:
    """OpenCode CLI integration configuration."""

    path: str = "opencode"
    auto_start: bool = True

    def __post_init__(self) -> None:
        if not self.path:
            self.path = "opencode"


@dataclass
class Config:
    """Aggregate configuration loaded from TOML files.

    Merges global (~/.config/ced/config.toml) and project-local
    (.ced/config.toml) sources, with project-local taking precedence.
    """

    theme: ThemeConfig = field(default_factory=ThemeConfig)
    editor: EditorConfig = field(default_factory=EditorConfig)
    keybindings: KeybindingConfig = field(default_factory=KeybindingConfig)
    opencode: OpenCodeConfig = field(default_factory=OpenCodeConfig)

    @classmethod
    def load(cls) -> Config:
        """Load and merge configuration from both config files."""
        cfg = cls()
        paths = [
            Path.home() / ".config" / "ced" / "config.toml",
            Path.cwd() / ".ced" / "config.toml",
        ]
        for p in paths:
            if p.exists():
                with p.open("rb") as f:
                    data = tomllib.load(f)
                cfg._merge(data)
        return cfg

    def _merge(self, data: dict) -> None:
        """Merge a parsed TOML dict into the current config.

        After setting values from each section, re-applies validation
        (clamping, fallback defaults) so invalid TOML values are corrected.
        """
        if "theme" in data:
            for k, v in data["theme"].items():
                if hasattr(self.theme, k):
                    setattr(self.theme, k, v)
        if self.theme.mode not in VALID_THEME_MODES:
            self.theme.mode = "auto"
        if "editor" in data:
            for k, v in data["editor"].items():
                if hasattr(self.editor, k):
                    setattr(self.editor, k, v)
            if self.editor.tab_size < 1:
                self.editor.tab_size = 4
            if self.editor.font_size < 8:
                self.editor.font_size = 12
        if "keybindings" in data:
            for k, v in data["keybindings"].items():
                if hasattr(self.keybindings, k):
                    setattr(self.keybindings, k, v)
        if self.keybindings.preset not in VALID_KEYBINDING_PRESETS:
            self.keybindings.preset = "vscode"
        if "opencode" in data:
            for k, v in data["opencode"].items():
                if hasattr(self.opencode, k):
                    setattr(self.opencode, k, v)
            if not self.opencode.path:
                self.opencode.path = "opencode"
