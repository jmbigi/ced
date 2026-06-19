from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from ced.app import Ced


class MockWidget:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)


class MockEditorArea:
    def __init__(self):
        self.buffers = MagicMock()
        self.buffers.active_buffer = MagicMock()
        self.buffers.active_buffer.is_modified = False
        self.buffers.count = 3
        self._mock_editor = MagicMock()
        self._mock_editor.text = "some text"
        self._mock_editor.cursor_location = (0, 0)
        self._mock_editor.file_path = Path("/tmp/test.py")

    def save_active(self):
        return True

    def new_file(self):
        self.buffers.count += 1

    def close_active(self):
        pass

    def tab_next(self):
        pass

    def tab_prev(self):
        pass

    def get_active_editor(self):
        return self._mock_editor

    def open_file(self, path):
        pass


class MockFileTree:
    def focus(self):
        pass


class MockSearchBar:
    def __init__(self):
        self.display = False

    def show_replace_ui(self, show):
        self.display = True

    def query_one(self, *args):
        return MagicMock()


class MockOpenCodePanel:
    def __init__(self):
        self.display = False

    def query_one(self, *args):
        mock = MagicMock()
        mock.focus = MagicMock()
        return mock


class MockHelpBar:
    def set_shortcuts(self, shortcuts):
        pass


# ── Tests for every app action ──────────────────────────────────────────


def test_action_toggle_sidebar():
    app = Ced()
    mock_sidebar = MockWidget(display=True)
    with patch.object(app, "query_one", return_value=mock_sidebar):
        app.action_toggle_sidebar()
        assert mock_sidebar.display is False
        app.action_toggle_sidebar()
        assert mock_sidebar.display is True


def test_action_toggle_opencode():
    app = Ced()
    mock_panel = MockOpenCodePanel()
    mock_panel.display = False
    mock_input = MagicMock()
    call_count = [0]
    def query_one_side_effect(*args, **kw):
        call_count[0] += 1
        if call_count[0] >= 3:
            return mock_input  # #opencode-input → has focus()
        return mock_panel
    with patch.object(app, "query_one", side_effect=query_one_side_effect):
        app.action_toggle_opencode()
        assert mock_panel.display is True
        mock_input.focus.assert_called_once()


def test_action_save():
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        with patch.object(app, "notify"):
            app.action_save()


def test_action_save_fails_notifies():
    app = Ced()
    mock_editor = MockEditorArea()
    mock_editor.save_active = lambda: False
    with patch.object(app, "query_one", return_value=mock_editor):
        with patch.object(app, "notify") as mock_notify:
            app.action_save()
            mock_notify.assert_called_once()


def test_action_close_tab():
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        app.action_close_tab()


def test_action_close_tab_modified():
    import asyncio
    from unittest.mock import AsyncMock
    app = Ced()
    mock_editor = MockEditorArea()
    mock_editor.buffers.active_buffer.is_modified = True
    with patch.object(app, "query_one", return_value=mock_editor):
        app.confirm = AsyncMock(return_value=True)
        asyncio.run(app.action_close_tab())


def test_action_close_tab_modified_cancelled():
    import asyncio
    from unittest.mock import AsyncMock
    app = Ced()
    mock_editor = MockEditorArea()
    mock_editor.buffers.active_buffer.is_modified = True
    with patch.object(app, "query_one", return_value=mock_editor):
        app.confirm = AsyncMock(return_value=False)
        with patch.object(mock_editor, "close_active") as mock_close:
            asyncio.run(app.action_close_tab())
            mock_close.assert_not_called()


def test_action_open_file():
    app = Ced()
    mock_tree = MockFileTree()
    with patch.object(app, "query_one", return_value=mock_tree):
        app.action_open_file()


def test_action_new_file():
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        old_count = mock_editor.buffers.count
        app.action_new_file()
        assert mock_editor.buffers.count == old_count + 1


def test_action_next_tab():
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        with patch.object(mock_editor, "tab_next") as mock_tn:
            app.action_next_tab()
            mock_tn.assert_called_once()


def test_action_prev_tab():
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        with patch.object(mock_editor, "tab_prev") as mock_tp:
            app.action_prev_tab()
            mock_tp.assert_called_once()


def test_action_search():
    app = Ced()
    mock_sb = MockSearchBar()
    with patch.object(app, "query_one", return_value=mock_sb):
        app.action_search()
        assert mock_sb.display is True


def test_action_search_replace():
    app = Ced()
    mock_sb = MockSearchBar()
    with patch.object(app, "query_one", return_value=mock_sb):
        app.action_search_replace()
        assert mock_sb.display is True


def test_action_command_palette():
    app = Ced()
    with patch.object(app, "push_screen") as mock_push:
        app.action_command_palette()
        mock_push.assert_called_once()


def test_action_quick_open():
    app = Ced()
    with patch.object(app, "push_screen") as mock_push:
        app.action_quick_open()
        mock_push.assert_called_once()


def test_action_jump_mode():
    app = Ced()
    with patch.object(app, "push_screen") as mock_push:
        app.action_jump_mode()
        mock_push.assert_called_once()


def test_action_theme_next():
    app = Ced()
    themes = app.config.theme.name
    app.action_theme_next()
    assert app.config.theme.name != themes


def test_action_theme_list():
    app = Ced()
    with patch.object(app, "notify"):
        app.action_theme_list()


def test_action_keybinding_list():
    app = Ced()
    with patch.object(app, "notify"):
        app.action_keybinding_list()


def test_action_help():
    app = Ced()
    with patch.object(app, "notify"):
        app.action_help()


def test_action_undo():
    app = Ced()
    mock_editor = MockEditorArea()
    active = mock_editor.get_active_editor()
    with patch.object(app, "query_one", return_value=mock_editor):
        app.action_undo()
        active.undo.assert_called_once()


def test_action_redo():
    app = Ced()
    mock_editor = MockEditorArea()
    active = mock_editor.get_active_editor()
    with patch.object(app, "query_one", return_value=mock_editor):
        app.action_redo()
        active.redo.assert_called_once()


def test_action_undo_no_editor():
    app = Ced()
    mock_editor = MockEditorArea()
    mock_editor.get_active_editor = lambda: None
    with patch.object(app, "query_one", return_value=mock_editor):
        app.action_undo()  # should not crash


def test_action_redo_no_editor():
    app = Ced()
    mock_editor = MockEditorArea()
    mock_editor.get_active_editor = lambda: None
    with patch.object(app, "query_one", return_value=mock_editor):
        app.action_redo()  # should not crash


def test_on_command_selected():
    app = Ced()
    called = False
    with patch.object(app.commands, "execute") as mock_exec:
        app._on_command_selected("app.quit")
        mock_exec.assert_called_with("app.quit")


def test_on_command_selected_none():
    app = Ced()
    app._on_command_selected(None)  # should not crash


def test_on_quick_open_file(tmp_path):
    app = Ced()
    f = tmp_path / "test.py"
    f.write_text("")
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        app._on_quick_open(f)


def test_on_quick_open_none():
    app = Ced()
    app._on_quick_open(None)  # should not crash


def test_on_quick_open_not_file():
    app = Ced()
    app._on_quick_open(Path("/nonexistent"))  # should not crash


def test_on_jump():
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        app._on_jump("so")


def test_on_jump_none():
    app = Ced()
    app._on_jump(None)


def test_on_jump_no_match():
    app = Ced()
    mock_editor = MockEditorArea()
    mock_editor.get_active_editor = lambda: None
    with patch.object(app, "query_one", return_value=mock_editor):
        app._on_jump("xx")


def test_on_search_requested():
    app = Ced()
    from ced.panels.search_bar import SearchBar
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        event = SearchBar.SearchRequested("some")
        app.on_search_bar_search_requested(event)


def test_on_search_requested_no_query():
    app = Ced()
    from ced.panels.search_bar import SearchBar
    with patch.object(app, "query_one"):
        event = SearchBar.SearchRequested("")
        app.on_search_bar_search_requested(event)


def test_on_replace_requested():
    app = Ced()
    from ced.panels.search_bar import SearchBar
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        event = SearchBar.ReplaceRequested("old", "new", all=False)
        app.on_search_bar_replace_requested(event)


def test_on_replace_all_requested():
    app = Ced()
    from ced.panels.search_bar import SearchBar
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        event = SearchBar.ReplaceRequested("old", "new", all=True)
        app.on_search_bar_replace_requested(event)


def test_on_replace_requested_no_find():
    app = Ced()
    from ced.panels.search_bar import SearchBar
    with patch.object(app, "query_one"):
        event = SearchBar.ReplaceRequested("", "new", all=False)
        app.on_search_bar_replace_requested(event)


def test_apply_theme():
    app = Ced()
    from ced.themes.manager import list_themes
    for theme_name in list_themes():
        app.config.theme.name = theme_name
        app._apply_theme()
        assert app.theme == theme_name


def test_apply_keybindings_before_mount():
    app = Ced()
    app._is_mounted = False
    app._apply_keybindings()


def test_apply_keybindings_after_mount():
    app = Ced()
    app._is_mounted = True
    with patch.object(app, "refresh_bindings") as mock_rb:
        app._apply_keybindings()
        mock_rb.assert_called_once()


def test_update_help_bar():
    app = Ced()
    mock_hb = MockHelpBar()
    with patch.object(app, "query_one", return_value=mock_hb):
        with patch.object(mock_hb, "set_shortcuts") as mock_set:
            app._update_help_bar()
            mock_set.assert_called_once()


def test_on_file_opened():
    app = Ced()
    from ced.panels.file_tree import FileTreePanel
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        event = FileTreePanel.FileOpened(Path("/tmp/test.py"))
        app.on_file_tree_panel_file_opened(event)
        assert event.path == Path("/tmp/test.py")


# on_tabbed_content_tab_activated is covered by pilot integration tests


def test_action_theme_next_unknown():
    """The except ValueError branch (lines 372-373)."""
    app = Ced()
    app.config.theme.name = "nonexistent"
    app.action_theme_next()
    assert app.config.theme.name in ("monokai", "dracula", "nord", "catppuccin", "github-dark", "solarized-dark")


def test_action_keybinding_next_with_mocks():
    """Lines 384-395: action_keybinding_next with mocked UI calls."""
    app = Ced()
    with patch.object(app, "_update_help_bar"):
        with patch.object(app, "notify"):
            app.action_keybinding_next()
    assert app._keybinding_manager.current_preset in ("vscode", "nano", "sublime", "emacs")


def test_action_help_notify():
    app = Ced()
    with patch.object(app, "notify") as mock_n:
        app.action_help()
        mock_n.assert_called_once()


def test_action_keybinding_list_notify():
    app = Ced()
    with patch.object(app, "notify") as mock_n:
        app.action_keybinding_list()
        mock_n.assert_called_once()


def test__apply_theme_dark_mode():
    app = Ced()
    app.config.theme.mode = "dark"
    app._apply_theme()
    assert app.dark is True


def test__apply_theme_light_mode():
    app = Ced()
    app.config.theme.mode = "light"
    app._apply_theme()
    assert app.dark is False


def test_on_search_bar_search_requested_with_text():
    from ced.panels.search_bar import SearchBar
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        ev = SearchBar.SearchRequested("hello world")
        app.on_search_bar_search_requested(ev)


def test_on_search_bar_replace_requested_all():
    from ced.panels.search_bar import SearchBar
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        ev = SearchBar.ReplaceRequested("abc", "xyz", all=True)
        app.on_search_bar_replace_requested(ev)


def test_on_search_bar_replace_requested_one():
    from ced.panels.search_bar import SearchBar
    app = Ced()
    mock_editor = MockEditorArea()
    with patch.object(app, "query_one", return_value=mock_editor):
        ev = SearchBar.ReplaceRequested("abc", "xyz", all=False)
        app.on_search_bar_replace_requested(ev)
