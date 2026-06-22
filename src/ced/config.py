from __future__ import annotations

import tomllib
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ThemeConfig:
    """Theme configuration: name, mode (auto/dark/light)."""

    mode: str = "auto"

    def __post_init__(self) -> None:
        if self.mode not in ("auto", "dark", "light"):
            raise ValueError(f"Invalid theme mode: {self.mode!r}")


@dataclass
class EditorConfig:
    """Editor configuration: tabs, wrapping, line numbers."""

    tab_size: int = 4
    soft_wrap: bool = False
    line_numbers: bool = True


@dataclass
class KeybindingConfig:
    """Keybinding preset configuration."""

    preset: str = "vscode"

    def __post_init__(self) -> None:
        allowed = {"vscode", "nano", "sublime", "emacs"}
        if self.preset not in allowed:
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
        config = cls()

        global_path = Path.home() / ".config" / "ced" / "config.toml"
        local_path = Path.cwd() / ".ced" / "config.toml"

        for path in (global_path, local_path):
            if path.exists():
                data = tomllib.loads(path.read_text(encoding="utf-8"))
                config._merge(data)
        return config

    def _merge(self, data: dict) -> None:
        """Merge a parsed TOML dict into the current config."""
        if "theme" in data:
            for k, v in data["theme"].items():
                if hasattr(self.theme, k):
                    setattr(self.theme, k, v)

        if "editor" in data:
            for k, v in data["editor"].items():
                if hasattr(self.editor, k):
                    setattr(self.editor, k, v)

        if "keybindings" in data:
            for k, v in data["keybindings"].items():
                if hasattr(self.keybindings, k):
                    setattr(self.keybindings, k, v)

        if "opencode" in data:
            for k, v in data["opencode"].items():
                if hasattr(self.opencode, k):
                    setattr(self.opencode, k, v)
