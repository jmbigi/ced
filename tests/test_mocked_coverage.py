from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from ced.panels.editor_area import EditorArea
from ced.panels.search_bar import SearchBar
from ced.panels.jump import JumpMode
from ced.panels.palette import CommandPalette
from ced.panels.quick_open import QuickOpen
from ced.panels.file_tree import FileTreePanel
from ced.panels.opencode_panel import OpenCodePanel


# ── EditorArea: open_file existing path (lines 89-94) ───────────────────


def test_editor_open_file_existing() -> None:
    ea = EditorArea()
    ea.buffers.add(Path("/tmp/existing.py"))
    ea._tab_ids.append("tab_existing")
    mock_tabs = MagicMock()
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.open_file(Path("/tmp/existing.py"))
        # Should activate existing tab
        assert mock_tabs.active == "tab_existing"


# ── EditorArea: get_active_editor no active tab (line 129) ──────────────


def test_editor_get_active_no_active() -> None:
    ea = EditorArea()
    mock_tabs = MagicMock()
    mock_tabs.active = ""
    with patch.object(ea, "query_one", return_value=mock_tabs):
        result = ea.get_active_editor()
        assert result is None


def test_editor_get_active_none() -> None:
    ea = EditorArea()
    mock_tabs = MagicMock()
    mock_tabs.active = None
    with patch.object(ea, "query_one", return_value=mock_tabs):
        result = ea.get_active_editor()
        assert result is None


# ── EditorArea: tab_next empty (line 141-142) ─────────────────────────────


def test_editor_tab_next_empty() -> None:
    ea = EditorArea()
    ea._tab_ids = []
    ea.tab_next()  # should not crash


# ── EditorArea: tab_next with unknown active (lines 146-148) ──────────────


def test_editor_tab_next_unknown_active() -> None:
    ea = EditorArea()
    ea._tab_ids = ["tab_a", "tab_b"]
    mock_tabs = MagicMock()
    mock_tabs.active = "tab_unknown"
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.tab_next()  # ValueError caught → i = -1
        # Wraps to first tab
        assert mock_tabs.active == "tab_a"


# ── EditorArea: tab_prev empty (line 152-153) ─────────────────────────────


def test_editor_tab_prev_empty() -> None:
    ea = EditorArea()
    ea._tab_ids = []
    ea.tab_prev()  # should not crash


# ── EditorArea: tab_prev with unknown active (lines 157-159) ──────────────


def test_editor_tab_prev_unknown_active() -> None:
    ea = EditorArea()
    ea._tab_ids = ["tab_a", "tab_b"]
    mock_tabs = MagicMock()
    mock_tabs.active = "tab_unknown"
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.tab_prev()  # ValueError caught → i = 0
        # Goes to last tab
        assert mock_tabs.active == "tab_b"


# ── EditorArea: close_active with empty/untitled (lines 177-179) ──────────


def test_editor_close_active_empty() -> None:
    ea = EditorArea()
    mock_tabs = MagicMock()
    mock_tabs.active = None
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.close_active()  # early return


def test_editor_close_active_untitled() -> None:
    ea = EditorArea()
    mock_tabs = MagicMock()
    mock_tabs.active = "tab_untitled"
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.close_active()  # early return (skip list)


def test_editor_close_active_empty_string() -> None:
    ea = EditorArea()
    mock_tabs = MagicMock()
    mock_tabs.active = ""
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.close_active()  # early return


# ── EditorArea: close_active normal flow (lines 183-203) ────────────────


def test_editor_close_active_normal() -> None:
    ea = EditorArea()
    ea._tab_ids = ["tab_test", "tab_other"]
    ea._editors["test"] = MagicMock()
    ea._editors["other"] = MagicMock()
    ea.buffers.add(Path("/tmp/test.py"))
    ea.buffers.add(Path("/tmp/other.py"))
    mock_tabs = MagicMock()
    mock_tabs.active = "tab_test"
    with patch.object(ea, "query_one", return_value=mock_tabs):
        ea.close_active()
        assert "tab_test" not in ea._tab_ids


# ── SearchBar: button pressed handlers (lines 73-89) ─────────────────────


def test_search_bar_button_close() -> None:
    sb = SearchBar()
    sb.display = True
    btn = MagicMock(id="close-search")
    sb.on_button_pressed(type("Ev", (), {"button": btn})())
    assert sb.display is False


def test_search_bar_button_toggle_replace() -> None:
    sb = SearchBar()
    sb._show_replace = False
    mock_row = MagicMock()
    btn = MagicMock(id="toggle-replace")
    with patch.object(sb, "query_one", return_value=mock_row):
        sb.on_button_pressed(type("Ev", (), {"button": btn})())
        assert sb._show_replace is True


def test_search_bar_button_replace() -> None:
    sb = SearchBar()
    with patch.object(sb, "get_search_text", return_value="find"):
        with patch.object(sb, "get_replace_text", return_value="rep"):
            with patch.object(sb, "post_message") as mock_pm:
                btn = MagicMock(id="replace-btn")
                sb.on_button_pressed(type("Ev", (), {"button": btn})())
                mock_pm.assert_called_once()


def test_search_bar_button_replace_all() -> None:
    sb = SearchBar()
    with patch.object(sb, "get_search_text", return_value="find"):
        with patch.object(sb, "get_replace_text", return_value="rep"):
            with patch.object(sb, "post_message") as mock_pm:
                btn = MagicMock(id="replace-all-btn")
                sb.on_button_pressed(type("Ev", (), {"button": btn})())
                mock_pm.assert_called_once()


def test_search_bar_button_unknown() -> None:
    sb = SearchBar()
    btn = MagicMock(id="nobody")
    sb.on_button_pressed(type("Ev", (), {"button": btn})())  # should not crash


# ── SearchBar: get_text + input_submitted (lines 105, 108, 111-112) ──────


def test_search_bar_get_text() -> None:
    sb = SearchBar()
    inp = MagicMock()
    inp.value = "test_query"
    with patch.object(sb, "query_one", return_value=inp):
        assert sb.get_search_text() == "test_query"


def test_search_bar_get_replace_text() -> None:
    sb = SearchBar()
    inp = MagicMock()
    inp.value = "replace_val"
    with patch.object(sb, "query_one", return_value=inp):
        assert sb.get_replace_text() == "replace_val"


def test_search_bar_input_submitted_find() -> None:
    sb = SearchBar()
    with patch.object(sb, "get_search_text", return_value="q"):
        with patch.object(sb, "post_message") as mock_pm:
            inp = MagicMock(id="find-input")
            sb.on_input_submitted(type("Ev", (), {"input": inp})())
            mock_pm.assert_called_once()


# ── Palette: list/input handlers (lines 75-76, 85-88, 91-93) ─────────────


def test_palette_input_changed_empty() -> None:
    pal = CommandPalette([])
    mock_lv = MagicMock()
    with patch.object(pal, "query_one", return_value=mock_lv):
        pal._all_commands = [("a", "desc", "Cat")]
        with patch.object(pal, "_populate") as mock_p:
            pal.on_input_changed(type("Ev", (), {"value": ""})())
            mock_p.assert_called_once_with(pal._all_commands)


def test_palette_input_changed_filter() -> None:
    pal = CommandPalette([])
    mock_lv = MagicMock()
    with patch.object(pal, "query_one", return_value=mock_lv):
        pal._all_commands = [("app.save", "Save file", "File")]
        with patch.object(pal, "_populate") as mock_p:
            pal.on_input_changed(type("Ev", (), {"value": "save"})())
            mock_p.assert_called_once()


def test_palette_list_selected_no_index() -> None:
    pal = CommandPalette([])
    pal._filtered = [("app.x", "desc", "Cat")]
    mock_lv = MagicMock()
    mock_lv.index = None
    with patch.object(pal, "query_one", return_value=mock_lv):
        with patch.object(pal, "dismiss") as mock_d:
            ev = MagicMock()
            ev.item = MagicMock()  # item is truthy → enters line 86
            pal.on_list_view_selected(ev)
            mock_d.assert_not_called()


def test_palette_list_selected_valid() -> None:
    pal = CommandPalette([])
    pal._filtered = [("app.x", "desc", "Cat")]
    mock_lv = MagicMock()
    mock_lv.index = 0
    with patch.object(pal, "query_one", return_value=mock_lv):
        with patch.object(pal, "dismiss") as mock_d:
            ev = MagicMock()
            ev.item = MagicMock()
            pal.on_list_view_selected(ev)
            mock_d.assert_called_once_with("app.x")


def test_palette_input_submitted_no_index() -> None:
    pal = CommandPalette([])
    pal._filtered = [("app.x", "desc", "Cat")]
    mock_lv = MagicMock()
    mock_lv.index = None
    with patch.object(pal, "query_one", return_value=mock_lv):
        with patch.object(pal, "dismiss") as mock_d:
            inp = MagicMock()
            inp.id = "palette-input"
            pal.on_input_submitted(type("Ev", (), {"input": inp, "value": ""})())
            mock_d.assert_not_called()


def test_palette_input_submitted_valid() -> None:
    pal = CommandPalette([])
    pal._filtered = [("app.x", "desc", "Cat")]
    mock_lv = MagicMock()
    mock_lv.index = 0
    with patch.object(pal, "query_one", return_value=mock_lv):
        with patch.object(pal, "dismiss") as mock_d:
            inp = MagicMock()
            inp.id = "palette-input"
            pal.on_input_submitted(type("Ev", (), {"input": inp, "value": ""})())
            mock_d.assert_called_once_with("app.x")


# ── JumpMode: key handlers (lines 58-73) ─────────────────────────────────


def _make_jm():
    jm = JumpMode()
    patch.object(jm, "_update_display").start()
    return jm


def test_jump_key_escape() -> None:
    jm = _make_jm()
    with patch.object(jm, "dismiss") as mock_d:
        jm.key_escape()
        mock_d.assert_called_once_with(None)


def test_jump_key_backspace() -> None:
    jm = _make_jm()
    jm._buffer = "ab"
    jm.key_backspace()
    assert jm._buffer == "a"


def test_jump_key_press_second_char() -> None:
    jm = _make_jm()
    jm._buffer = "a"
    mock_key = MagicMock()
    mock_key.character = "b"
    with patch.object(jm, "dismiss") as mock_d:
        jm.key_press(mock_key)
        mock_d.assert_called_once_with("ab")


def test_jump_key_press_first_char() -> None:
    jm = _make_jm()
    jm._buffer = ""
    mock_key = MagicMock()
    mock_key.character = "x"
    with patch.object(jm, "dismiss") as mock_d:
        jm.key_press(mock_key)
        mock_d.assert_not_called()
        assert jm._buffer == "x"


# ── JumpMode: key_press with None character (line 60) ─────────────────────


def test_jump_key_press_none_char() -> None:
    jm = _make_jm()
    mock_key = MagicMock()
    mock_key.character = None
    jm.key_press(mock_key)  # early return at line 60
    assert jm._buffer == ""


# ── EditorArea: save_active OSError (lines 177-179) ─────────────────────


def test_editor_save_active_oserror() -> None:
    ea = EditorArea()
    mock_editor = MagicMock()
    mock_editor.file_path = Path("/tmp/test.py")
    mock_editor.save_file.side_effect = OSError("disk full")
    with patch.object(ea, "get_active_editor", return_value=mock_editor):
        with patch.object(ea, "notify") as mock_n:
            result = ea.save_active()
            assert result is False
            mock_n.assert_called_once()


# ── QuickOpen: _populate with file outside root (lines 85-86) ──────────


def test_quick_open_populate_outside_root() -> None:
    qo = QuickOpen(Path("/root/path"))
    mock_lv = MagicMock()
    with patch.object(qo, "query_one", return_value=mock_lv):
        qo._populate([Path("/outside/file.py")])
        # relative_to raises ValueError → falls back to fp
        mock_lv.append.assert_called_once()


# ── QuickOpen: handlers (lines 71-72, 85-86, 99-100, 109-112, 115-118) ──


def test_quick_open_input_changed_empty() -> None:
    qo = QuickOpen(Path.cwd())
    mock_lv = MagicMock()
    with patch.object(qo, "query_one", return_value=mock_lv):
        qo._all_files = [Path("/a.py")]
        with patch.object(qo, "_populate") as mock_p:
            qo.on_input_changed(type("Ev", (), {"value": ""})())
            mock_p.assert_called_once_with(qo._all_files)


def test_quick_open_input_changed_filter() -> None:
    qo = QuickOpen(Path.cwd())
    mock_lv = MagicMock()
    with patch.object(qo, "query_one", return_value=mock_lv):
        qo._all_files = [Path("/a.py"), Path("/b.txt")]
        with patch.object(qo, "_populate") as mock_p:
            qo.on_input_changed(type("Ev", (), {"value": "a"})())
            mock_p.assert_called_once()


def test_quick_open_list_selected_no_index() -> None:
    qo = QuickOpen(Path.cwd())
    qo._filtered = [Path("/a.py")]
    mock_lv = MagicMock()
    mock_lv.index = None
    with patch.object(qo, "query_one", return_value=mock_lv):
        with patch.object(qo, "dismiss") as mock_d:
            qo.on_list_view_selected(type("Ev", (), {"list_view": MagicMock()})())
            mock_d.assert_not_called()


def test_quick_open_list_selected_valid() -> None:
    qo = QuickOpen(Path.cwd())
    qo._filtered = [Path("/a.py")]
    mock_lv = MagicMock()
    mock_lv.index = 0
    with patch.object(qo, "query_one", return_value=mock_lv):
        with patch.object(qo, "dismiss") as mock_d:
            qo.on_list_view_selected(type("Ev", (), {"list_view": MagicMock()})())
            mock_d.assert_called_once_with(Path("/a.py"))


def test_quick_open_input_submitted_valid() -> None:
    qo = QuickOpen(Path.cwd())
    qo._filtered = [Path("/a.py")]
    mock_lv = MagicMock()
    mock_lv.index = 0
    with patch.object(qo, "query_one", return_value=mock_lv):
        with patch.object(qo, "dismiss") as mock_d:
            inp = MagicMock()
            inp.id = "quick-input"
            qo.on_input_submitted(type("Ev", (), {"input": inp, "value": "a"})())
            mock_d.assert_called_once()


def test_quick_open_escape() -> None:
    qo = QuickOpen(Path.cwd())
    with patch.object(qo, "dismiss") as mock_d:
        qo.key_escape()
        mock_d.assert_called_once_with(None)


# ── FileTreePanel: refresh_tree + file_selected (lines 23-32) ────────────


def test_file_tree_refresh() -> None:
    ftp = FileTreePanel(path=Path.cwd())
    with patch.object(ftp, "reload"):
        ftp.refresh_tree(Path.cwd())
    assert ftp.path == Path.cwd()


def test_file_tree_refresh_default_path() -> None:
    ftp = FileTreePanel(path=Path.cwd())
    with patch.object(ftp, "reload"):
        ftp.refresh_tree()
    assert ftp.path == Path.cwd()


def test_file_tree_file_selected_is_file(tmp_path: Path) -> None:
    src = tmp_path / "select_me.py"
    src.write_text("")
    ftp = FileTreePanel(path=tmp_path)
    with patch.object(ftp, "post_message") as mock_pm:
        from textual.widgets import DirectoryTree

        node = MagicMock()
        ev = DirectoryTree.FileSelected(node=node, path=src)
        ftp.on_directory_tree_file_selected(ev)
        mock_pm.assert_called_once()


def test_file_tree_file_selected_not_file(tmp_path: Path) -> None:
    ftp = FileTreePanel(path=tmp_path)
    with patch.object(ftp, "post_message") as mock_pm:
        from textual.widgets import DirectoryTree

        node = MagicMock()
        ev = DirectoryTree.FileSelected(node=node, path=tmp_path)
        ftp.on_directory_tree_file_selected(ev)
        mock_pm.assert_not_called()


def test_file_tree_file_opened_message() -> None:
    msg = FileTreePanel.FileOpened(Path("/test.py"))
    assert msg.path == Path("/test.py")


# ── OpenCodePanel: worker methods (lines 90-121) ─────────────────────────


def test_opencode_panel_init_default() -> None:
    ocp = OpenCodePanel()
    assert ocp._opencode_path == "opencode"
    assert ocp._auto_start is True


def test_opencode_panel_custom_path() -> None:
    ocp = OpenCodePanel(opencode_path="/usr/bin/oc", auto_start=False)
    assert ocp._opencode_path == "/usr/bin/oc"
    assert ocp._auto_start is False
