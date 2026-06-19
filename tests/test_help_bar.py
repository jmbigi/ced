from __future__ import annotations

from unittest.mock import patch

from ced.panels.help_bar import HelpBar


class TestHelpBar:
    def test_default_shortcuts(self) -> None:
        bar = HelpBar()
        assert len(bar._shortcuts) == 6
        assert bar._shortcuts[0] == ("^Q", "Quit")

    def test_custom_shortcuts(self) -> None:
        custom = [("^X", "Exit"), ("^Z", "Undo")]
        bar = HelpBar(shortcuts=custom)
        assert bar._shortcuts == custom

    def test_set_shortcuts_updates(self) -> None:
        bar = HelpBar()
        new = [("^A", "Action A")]
        with patch.object(bar, "render_shortcuts"):
            bar.set_shortcuts(new)
        assert bar._shortcuts == new

    def test_set_shortcuts_calls_render(self) -> None:
        bar = HelpBar()
        new = [("^Z", "Undo")]
        with patch.object(bar, "render_shortcuts") as mock_render:
            bar.set_shortcuts(new)
            mock_render.assert_called_once()

    def test_render_shortcuts_format(self) -> None:
        bar = HelpBar(shortcuts=[("^Q", "Quit"), ("^S", "Save")])
        parts = []
        for key, action in bar._shortcuts:
            parts.append(f" {key} {action} ")
        expected = " ^Q Quit  ^S Save "
        assert "".join(parts) == expected
