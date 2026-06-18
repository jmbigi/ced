from __future__ import annotations

from typing import Literal

ThemeMode = Literal["auto", "dark", "light"]

THEMES: dict[str, dict[str, str]] = {
    "monokai": {
        "primary": "#a6e22e",
        "secondary": "#f92672",
        "accent": "#66d9ef",
        "surface": "#272822",
        "text": "#f8f8f2",
        "text-muted": "#75715e",
        "boost": "#3e3d32",
        "warning": "#e6db74",
        "error": "#f92672",
        "success": "#a6e22e",
    },
    "dracula": {
        "primary": "#bd93f9",
        "secondary": "#ff79c6",
        "accent": "#50fa7b",
        "surface": "#282a36",
        "text": "#f8f8f2",
        "text-muted": "#6272a4",
        "boost": "#44475a",
        "warning": "#f1fa8c",
        "error": "#ff5555",
        "success": "#50fa7b",
    },
    "nord": {
        "primary": "#88c0d0",
        "secondary": "#bf616a",
        "accent": "#a3be8c",
        "surface": "#2e3440",
        "text": "#eceff4",
        "text-muted": "#4c566a",
        "boost": "#3b4252",
        "warning": "#ebcb8b",
        "error": "#bf616a",
        "success": "#a3be8c",
    },
    "catppuccin": {
        "primary": "#89b4fa",
        "secondary": "#f38ba8",
        "accent": "#a6e3a1",
        "surface": "#1e1e2e",
        "text": "#cdd6f4",
        "text-muted": "#6c7086",
        "boost": "#313244",
        "warning": "#f9e2af",
        "error": "#f38ba8",
        "success": "#a6e3a1",
    },
    "github-dark": {
        "primary": "#58a6ff",
        "secondary": "#f78166",
        "accent": "#3fb950",
        "surface": "#0d1117",
        "text": "#c9d1d9",
        "text-muted": "#8b949e",
        "boost": "#161b22",
        "warning": "#d29922",
        "error": "#f85149",
        "success": "#3fb950",
    },
    "solarized-dark": {
        "primary": "#268bd2",
        "secondary": "#dc322f",
        "accent": "#859900",
        "surface": "#002b36",
        "text": "#839496",
        "text-muted": "#586e75",
        "boost": "#073642",
        "warning": "#b58900",
        "error": "#dc322f",
        "success": "#859900",
    },
}


def list_themes() -> list[str]:
    return list(THEMES.keys())


def detect_dark_mode() -> bool:
    try:
        import os

        if os.name == "nt":
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        elif os.environ.get("COLORFGBG"):
            bg = os.environ["COLORFGBG"].split(";")[-1]
            return int(bg) < 8
        return True
    except Exception:
        return True


def get_theme_variables(theme_name: str) -> dict[str, str]:
    return THEMES.get(theme_name, THEMES["monokai"])
