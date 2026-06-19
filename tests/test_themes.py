from __future__ import annotations

from ced.themes.manager import list_themes, get_theme_variables, THEMES


class TestThemeManager:
    def test_list_themes(self) -> None:
        themes = list_themes()
        assert "monokai" in themes
        assert "dracula" in themes
        assert "nord" in themes
        assert "catppuccin" in themes
        assert "github-dark" in themes
        assert "solarized-dark" in themes

    def test_get_theme_variables(self) -> None:
        theme = get_theme_variables("monokai")
        assert theme["primary"] == "#a6e22e"
        assert theme["secondary"] == "#f92672"
        assert theme["surface"] == "#272822"

    def test_get_theme_variables_unknown_fallback(self) -> None:
        theme = get_theme_variables("nonexistent")
        assert theme == THEMES["monokai"]

    def test_all_themes_have_required_keys(self) -> None:
        required = {"primary", "secondary", "accent", "surface", "text",
                    "text-muted", "boost", "warning", "error", "success"}
        for name, theme in THEMES.items():
            missing = required - set(theme.keys())
            assert not missing, f"Theme {name!r} missing keys: {missing}"

    def test_detect_dark_mode(self) -> None:
        from ced.themes.manager import detect_dark_mode
        result = detect_dark_mode()
        assert isinstance(result, bool)
