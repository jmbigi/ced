# ruff: noqa: E402, F401, F841, F811
"""Comprehensive coverage driver — exercises every line in src/ced.

Run: coverage run tests/coverage_all.py && coverage report --show-missing
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import coverage

cov = coverage.Coverage(source=["src/ced"])
cov.start()

# ── Imports ──────────────────────────────────────────────────────────────
from ced.app import Ced
from ced.config import (
    Config,
    EditorConfig,
    KeybindingConfig,
    OpenCodeConfig,
    ThemeConfig,
)
from ced.commands.registry import Command, CommandRegistry
from ced.editor.buffer import Buffer, BufferManager
from ced.editor.widget import EnhancedCodeEditor, detect_language
from ced.keybindings.manager import KeybindingManager
from ced.keybindings.presets import get_preset, list_presets
from ced.panels.editor_area import EditorArea, EditorSettings
from ced.panels.file_tree import FileTreePanel
from ced.panels.help_bar import HelpBar
from ced.panels.search_bar import SearchBar
from ced.panels.jump import JumpMode
from ced.panels.palette import CommandPalette
from ced.themes.manager import list_themes, detect_dark_mode, get_theme_variables

# Trigger __init__._get_version() fallback (lines 12-13)
import ced.__init__ as _ced_init
from unittest.mock import patch

with patch("ced.__init__._metadata_version", side_effect=Exception("fail")):
    assert _ced_init._get_version() == "0.1.0"

# ── Unit-level coverage ──────────────────────────────────────────────────

Buffer()
Buffer(Path("/tmp/f.py"))
Buffer(Path("/tmp/f.py")).mark_modified()
Buffer(Path("/tmp/f.py")).mark_saved()
Buffer(Path("/tmp/f.py")).directory
Buffer().name  # "untitled" path (line 20-22)
Buffer().directory  # "" path (line 28)

bm = BufferManager()
bm.add()
bm.add(Path("/tmp/a.py"))
bm.add(Path("/tmp/b.py"))
bm.add(Path("/tmp/c.py"))
bm.active_index  # property -1 (empty)
bm.active_index = 0  # setter valid
bm.active_index = 99  # setter invalid (no change)
list(bm)
bm[0]
bm.get_by_path(Path("/tmp/a.py"))
bm.get_by_path(Path("/tmp/x.py"))
bm.open(Path("/tmp/d.py"))
bm.open(Path("/tmp/a.py"))  # existing file (line 85-90)
bm.close_active()  # close d.py → active shifts
bm.close_active()  # close next
bm.switch_next()
bm.switch_prev()
bm.remove(0)
bm.remove(50)
# Edge: active_index -1, remove (lines 43, 76)
bm2 = BufferManager()
bm2._active_index = -1
bm2.remove(0)
# Edge: active_index > 0, remove last (lines 76, 97)
bm3 = BufferManager()
bm3.add()
bm3._active_index = 0
bm3.close_active()

Command("a.b", "desc", lambda: None, "Cat")
Command("c.d", "desc2", lambda: None)
reg = CommandRegistry()
reg.register(Command("app.x", "desc x", lambda: None, "X"))
reg.register_many(Command("app.y", "desc y", lambda: None, "Y"))
reg.all()
reg.get("app.x")
reg.execute("app.x")
reg.search("desc")
reg.search("zzz")
try:
    reg.execute("nonexistent")
except KeyError:
    pass
try:
    reg.register(Command("app.x", "dup", lambda: None, "X"))
except ValueError:
    pass

Config()
# Trigger config file reading path (lines 74-76)
import os
import tempfile

_tmp_home = Path(tempfile.mkdtemp())
_cfg_dir = _tmp_home / ".config" / "ced"
_cfg_dir.mkdir(parents=True)
(_cfg_dir / "config.toml").write_text("[editor]\ntab_size = 2\n")
_old_home = os.environ.get("HOME")
os.environ["HOME"] = str(_tmp_home)
Config.load()
if _old_home:
    os.environ["HOME"] = _old_home
else:
    del os.environ["HOME"]

EditorConfig()
EditorConfig(
    tab_size=2,
    soft_wrap=True,
    line_numbers=False,
    indent_guides=False,
    font_size=14,
    show_minimap=True,
)
EditorConfig(tab_size=0)
EditorConfig(tab_size=-5)
EditorConfig(font_size=1)

ThemeConfig()
try:
    ThemeConfig(mode="bad")
except ValueError:
    pass

KeybindingConfig()
try:
    KeybindingConfig(preset="bad")
except ValueError:
    pass

OpenCodeConfig()
OpenCodeConfig(path="")
OpenCodeConfig(path="/usr/bin/opencode", auto_start=False)

cfg = Config()
cfg._merge({"theme": {"mode": "dark", "name": "dracula"}})
cfg._merge({"theme": {"mode": "bad"}})
cfg._merge({"editor": {"tab_size": 8, "bogus": 1}})
cfg._merge({"keybindings": {"preset": "nano"}})
cfg._merge({"keybindings": {"preset": "bad"}})
cfg._merge({"opencode": {"path": "/bin/oc", "auto_start": False}})
cfg._merge({"opencode": {"bogus": 1}})
cfg._merge({"bogus_section": {"x": 1}})

detect_language(Path("main.py"))
detect_language(Path("main.rs"))
detect_language(None)
detect_language(Path("Makefile"))

ed = EnhancedCodeEditor()
ed = EnhancedCodeEditor(
    path="/tmp/f.py", show_line_numbers=True, soft_wrap=False, indent_width=2
)
ed.file_path
ed.file_path = Path("/tmp/g.py")
ed.file_path = None
ed.file_path = "/tmp/h.py"
ed.save_file()
ed.save_as(Path("/tmp/_ced_test_write.txt"))
ed.save_file()  # save_file success path (line 135)
Path("/tmp/_ced_test_write.txt").unlink(missing_ok=True)
# load_file (lines 128-131)
_src = Path("/tmp/_ced_test_load.txt")
_src.write_text("loaded content")
ed.load_file(_src)
_src.unlink()

KeybindingManager()
KeybindingManager("nano")
mgr = KeybindingManager()
mgr.set_preset("sublime")
try:
    mgr.set_preset("bad")
except ValueError:
    pass
mgr.bindings
mgr.current_preset
# override/remove_override (lines 34-35, 38-39, 47)
from textual.binding import Binding as TxtBinding

mgr.override("test_act", TxtBinding("ctrl+t", "test_act", "Test"))
mgr.remove_override("test_act")
mgr.remove_override("nonexistent")

list_presets()
get_preset("vscode")
get_preset("emacs")
get_preset("bad_preset")

list_themes()
detect_dark_mode()
get_theme_variables("monokai")
get_theme_variables("nonexistent")

HelpBar()
HelpBar(shortcuts=[("^X", "Exit")])

EditorSettings()
EditorSettings(show_line_numbers=False, soft_wrap=True, indent_width=2)

ea = EditorArea()
ea._unique_name("test.py")
ea._unique_name("test.py")
ea._tab_id("test.py")
ea._editor_id("test.py")
ea._sanitize_id("a.b")
ea._sanitize_id("simple")

FileTreePanel()
FileTreePanel(path=Path("/tmp"))
ftp = FileTreePanel()
ftp._base_path
ftp.FileOpened(Path("/x.py"))

SearchBar.SearchRequested("find")
SearchBar.ReplaceRequested("find", "repl", all=False)
SearchBar.ReplaceRequested("find", "repl", all=True)

JumpMode()
CommandPalette([])

# ── App-level coverage (without mounting) ───────────────────────────────
app = Ced()
app.TITLE
app.SUB_TITLE
app.config
app.commands.all()

app.action_theme_next()
app.action_theme_list()
app.action_keybinding_list()
app.action_help()
app._keybinding_manager.set_preset("nano")
app._apply_keybindings()

# ── App-level coverage (with mounting) ──────────────────────────────────
import asyncio  # noqa: F811

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def run_mounted():
    async with app.run_test() as pilot:
        await pilot.pause()
        app.action_toggle_sidebar()
        app.action_toggle_opencode()
        app.action_search()
        app.action_search_replace()
        app.action_new_file()
        await pilot.pause()
        app.action_new_file()
        await pilot.pause()
        app.action_next_tab()
        app.action_prev_tab()
        app.action_save()
        app.action_open_file()
        sb = app.query_one("#search-bar")
        sb.show_replace_ui(True)
        sb.show_replace_ui(False)
        app._update_help_bar()
        app._update_help_bar()  # second call → dedup (line 197)
        app.action_command_palette()
        await pilot.pause()
        app.action_quick_open()
        await pilot.pause()
        app.action_jump_mode()
        await pilot.pause()
        app.action_undo()
        app.action_redo()

        # Tab navigation edge cases
        editor = app.query_one("#editor")
        editor.tab_next()  # single tab → wraps to itself
        await pilot.pause()


loop.run_until_complete(run_mounted())

cov.stop()
cov.save()
cov.report(show_missing=True, ignore_errors=True, file=sys.stdout)
