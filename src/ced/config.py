from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

KeybindingPreset = Literal["vscode", "nano", "sublime", "emacs"]


@dataclass
class ThemeConfig:
    mode: Literal["auto", "dark", "light"] = "auto"
    name: str = "monokai"


@dataclass
class EditorConfig:
    tab_size: int = 4
    soft_wrap: bool = False
    line_numbers: bool = True
    indent_guides: bool = True
    font_size: int = 12
    show_minimap: bool = False


@dataclass
class KeybindingConfig:
    preset: KeybindingPreset = "vscode"


@dataclass
class OpenCodeConfig:
    path: str = "opencode"
    auto_start: bool = True


@dataclass
class Config:
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    editor: EditorConfig = field(default_factory=EditorConfig)
    keybindings: KeybindingConfig = field(default_factory=KeybindingConfig)
    opencode: OpenCodeConfig = field(default_factory=OpenCodeConfig)

    @classmethod
    def load(cls) -> "Config":
        cfg = cls()
        paths = [
            Path.home() / ".config" / "ced" / "config.toml",
            Path.cwd() / ".ced" / "config.toml",
        ]
        for p in paths:
            if p.exists():
                with p.open("rb") as f:
                    import tomllib

                    data = tomllib.load(f)
                cfg._merge(data)
        return cfg

    def _merge(self, data: dict) -> None:
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
