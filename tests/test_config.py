from __future__ import annotations

from pathlib import Path

from ced.config import (
    Config,
    EditorConfig,
    OpenCodeConfig,
    ThemeConfig,
    KeybindingConfig,
)


def test_config_defaults() -> None:
    cfg = Config()
    assert cfg.theme.mode == "auto"
    assert cfg.theme.name == "monokai"
    assert cfg.editor.tab_size == 4
    assert cfg.editor.soft_wrap is False
    assert cfg.editor.line_numbers is True
    assert cfg.keybindings.preset == "vscode"
    assert cfg.opencode.path == "opencode"
    assert cfg.opencode.auto_start is True


def test_theme_config_invalid_mode() -> None:
    try:
        ThemeConfig(mode="invalid")
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_keybinding_config_invalid_preset() -> None:
    try:
        KeybindingConfig(preset="invalid")
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_config_merge_theme(tmp_path: Path) -> None:
    cfg = Config()
    cfg._merge({"theme": {"mode": "dark", "name": "dracula"}})
    assert cfg.theme.mode == "dark"
    assert cfg.theme.name == "dracula"


def test_config_merge_editor(tmp_path: Path) -> None:
    cfg = Config()
    cfg._merge({"editor": {"tab_size": 8, "soft_wrap": True}})
    assert cfg.editor.tab_size == 8
    assert cfg.editor.soft_wrap is True


def test_config_merge_keybindings(tmp_path: Path) -> None:
    cfg = Config()
    cfg._merge({"keybindings": {"preset": "nano"}})
    assert cfg.keybindings.preset == "nano"


def test_config_merge_opencode(tmp_path: Path) -> None:
    cfg = Config()
    cfg._merge({"opencode": {"path": "/usr/bin/opencode", "auto_start": False}})
    assert cfg.opencode.path == "/usr/bin/opencode"
    assert cfg.opencode.auto_start is False


def test_config_merge_bogus_keys_ignored() -> None:
    cfg = Config()
    cfg._merge({"theme": {"nonexistent": "val"}, "editor": {"bogus": 42}})
    assert cfg.theme.mode == "auto"


def test_config_merge_invalid_mode_fallback() -> None:
    cfg = Config()
    cfg._merge({"theme": {"mode": "invalid"}})
    assert cfg.theme.mode == "auto", "invalid mode should fall back to auto"


def test_config_merge_invalid_preset_fallback() -> None:
    cfg = Config()
    cfg._merge({"keybindings": {"preset": "invalid"}})
    assert cfg.keybindings.preset == "vscode", (
        "invalid preset should fall back to vscode"
    )


def test_config_load_from_file(tmp_path: Path) -> None:
    config_dir = tmp_path / ".config" / "ced"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.toml"
    config_file.write_text(
        '[theme]\nmode = "dark"\nname = "nord"\n\n[editor]\ntab_size = 2\n'
    )

    # Temporarily change home so Config.load reads our file
    import os

    orig_home = os.environ.get("HOME")
    try:
        os.environ["HOME"] = str(tmp_path)
        cfg = Config.load()
        assert cfg.theme.mode == "dark"
        assert cfg.theme.name == "nord"
        assert cfg.editor.tab_size == 2
    finally:
        if orig_home:
            os.environ["HOME"] = orig_home
        else:
            del os.environ["HOME"]


def test_config_load_without_file() -> None:
    cfg = Config.load()
    assert isinstance(cfg, Config)


def test_config_load_skips_bad_toml(tmp_path: Path) -> None:
    config_dir = tmp_path / ".config" / "ced"
    config_dir.mkdir(parents=True)
    bad_file = config_dir / "config.toml"
    bad_file.write_text("{invalid toml content @@@")
    import os
    old = os.environ.get("HOME")
    try:
        os.environ["HOME"] = str(tmp_path)
        cfg = Config.load()
        assert cfg.theme.mode == "auto"
    finally:
        if old:
            os.environ["HOME"] = old
        else:
            del os.environ["HOME"]


def test_editor_config_invalid_tab_size_negative() -> None:
    cfg = EditorConfig(tab_size=-1)
    assert cfg.tab_size == 4


def test_editor_config_invalid_tab_size_zero() -> None:
    cfg = EditorConfig(tab_size=0)
    assert cfg.tab_size == 4


def test_editor_config_invalid_font_size() -> None:
    cfg = EditorConfig(font_size=1)
    assert cfg.font_size == 12


def test_opencode_config_empty_path() -> None:
    cfg = OpenCodeConfig(path="")
    assert cfg.path == "opencode"


def test_merge_editor_clamps_tab_size_zero() -> None:
    cfg = Config()
    cfg._merge({"editor": {"tab_size": 0}})
    assert cfg.editor.tab_size == 4


def test_merge_editor_clamps_tab_size_negative() -> None:
    cfg = Config()
    cfg._merge({"editor": {"tab_size": -5}})
    assert cfg.editor.tab_size == 4


def test_merge_editor_clamps_font_size() -> None:
    cfg = Config()
    cfg._merge({"editor": {"font_size": 1}})
    assert cfg.editor.font_size == 12


def test_merge_opencode_empty_path() -> None:
    cfg = Config()
    cfg._merge({"opencode": {"path": ""}})
    assert cfg.opencode.path == "opencode"
