from __future__ import annotations

import os
import sys

_THEMES: dict[str, dict[str, str]] = {
    "monokai": {
        "primary": "#a6e22e",
        "secondary": "#f92672",
        "accent": "#e6db74",
        "text": "#f8f8f2",
        "text-muted": "#75715e",
        "surface": "#272822",
        "background": "#1b1c17",
        "boost": "#3e3d32",
        "warning": "#e6db74",
        "error": "#f92672",
        "success": "#a6e22e",
    },
    "dracula": {
        "primary": "#bd93f9",
        "secondary": "#ff79c6",
        "accent": "#50fa7b",
        "text": "#f8f8f2",
        "text-muted": "#6272a4",
        "surface": "#282a36",
        "background": "#1c1d26",
        "boost": "#3a3c4a",
        "warning": "#f1fa8c",
        "error": "#ff5555",
        "success": "#50fa7b",
    },
    "nord": {
        "primary": "#88c0d0",
        "secondary": "#bf616a",
        "accent": "#a3be8c",
        "text": "#e5e9f0",
        "text-muted": "#616e88",
        "surface": "#2e3440",
        "background": "#232832",
        "boost": "#3b4252",
        "warning": "#ebcb8b",
        "error": "#bf616a",
        "success": "#a3be8c",
    },
    "catppuccin": {
        "primary": "#89b4fa",
        "secondary": "#f38ba8",
        "accent": "#a6e3a1",
        "text": "#cdd6f4",
        "text-muted": "#6c7086",
        "surface": "#313244",
        "background": "#252636",
        "boost": "#45475a",
        "warning": "#f9e2af",
        "error": "#f38ba8",
        "success": "#a6e3a1",
    },
    "github-dark": {
        "primary": "#58a6ff",
        "secondary": "#f78166",
        "accent": "#3fb950",
        "text": "#e6edf3",
        "text-muted": "#848d97",
        "surface": "#161b22",
        "background": "#0d1117",
        "boost": "#21262d",
        "warning": "#d29922",
        "error": "#f85149",
        "success": "#3fb950",
    },
    "solarized-dark": {
        "primary": "#268bd2",
        "secondary": "#dc322f",
        "accent": "#859900",
        "text": "#93a1a1",
        "text-muted": "#657b83",
        "surface": "#073642",
        "background": "#002b36",
        "boost": "#094454",
        "warning": "#b58900",
        "error": "#dc322f",
        "success": "#859900",
    },
}


def list_themes() -> list[str]:
    """Return the names of all available built-in themes."""
    return list(_THEMES.keys())


def detect_dark_mode() -> bool:
    """Detect if the terminal is in dark mode.

    Checks the COLORFGBG environment variable (Linux/macOS) or the
    Windows registry.  Returns True if dark mode is detected.
    """
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return True
    color = os.environ.get("COLORFGBG", "")
    return "15;0" in color or not color


def get_theme_variables(name: str) -> dict[str, str]:
    """Return the color variables for the given theme name.

    Falls back to monokai if *name* is not found.
    """
    return _THEMES.get(name, _THEMES["monokai"])
