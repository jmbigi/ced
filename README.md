# ced — Terminal Code Editor

**ced** is a modern, non-modal terminal code editor for programmers who work in the terminal. Built with Python + Textual, it runs on Linux, macOS, and Windows.

## Philosophy

- **Non-modal** — never forced into vim modes. Every action is one Ctrl+ key away or visible in the help bar.
- **VS Code spirit, terminal form** — file tree sidebar, editor tabs, command palette, quick open, multi-keybinding presets.
- **Plug and play** — `pip install .` + `ced` opens an editor. No configuration required.
- **AI-ready** — the OpenCode panel is designed for integrated AI assistance via the OpenCode CLI.
- **Safe, modern, advanced, robust** — editing modes that protect your data, resist crashes, and provide a smooth, professional editing experience in any terminal environment.

## Features

| Feature | Status |
|---------|--------|
| File tree sidebar (DirectoryTree) | Done |
| Editor with syntax highlighting (TextArea + tree-sitter, 40+ languages) | Done |
| Auto language detection from file extension | Done |
| Tabbed multi-file editing with open/save/close | Done |
| Open file from sidebar click | Done |
| Save file (Ctrl+S), Close tab (Ctrl+W) | Done |
| Quick Open file finder (Ctrl+P) — fuzzy file search | Done |
| Search in file (Ctrl+F) | Done |
| Search & Replace (Ctrl+H) | Done |
| Command palette (Ctrl+Shift+P) | Done |
| Jump Mode (Ctrl+J) — 2-character navigation | Done |
| Undo (Ctrl+Z) / Redo (Ctrl+Y) | Done |
| New file (Ctrl+N) | Done |
| Switch theme at runtime (via command palette) | Done |
| Switch keybinding preset at runtime (via command palette) | Done |
| Keybinding presets: VS Code, nano, Sublime, Emacs | Done |
| Help bar with visible shortcuts | Done |
| Toggle sidebar (Ctrl+B) | Done |
| Toggle OpenCode AI panel (Ctrl+`) | Done |
| Theme presets: Monokai, Dracula, Nord, Catppuccin, GitHub Dark, Solarized | Done |
| Auto dark/light mode detection | Done |
| Config via TOML (global + project-local) | Done |

## Install

### From source
```bash
git clone https://github.com/your/repo
cd ced
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Unix:
source .venv/bin/activate
pip install -e .
```

### Launch
```bash
ced
# or
python -m ced
```

## Keybindings (VS Code preset)

| Key | Action |
|-----|--------|
| Ctrl+Q | Quit |
| Ctrl+S | Save |
| Ctrl+W | Close tab |
| Ctrl+P | Quick Open (fuzzy file search) |
| Ctrl+Shift+P | Command palette |
| Ctrl+B | Toggle sidebar |
| Ctrl+` | Toggle OpenCode AI panel |
| Ctrl+F | Search in file |
| Ctrl+H | Search & replace |
| Ctrl+N | New file |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+J | Jump Mode (type 2 chars to navigate) |
| Ctrl+Tab | Next tab |
| Ctrl+Shift+Tab | Previous tab |

## Keybinding Presets

Switch presets at runtime from the command palette (`Ctrl+Shift+P`):

| Preset | Distinctive keys |
|--------|-----------------|
| **VS Code** (default) | Ctrl+S save, Ctrl+P open, Ctrl+` panel |
| **nano** | Ctrl+O writeout, Ctrl+W search, Ctrl+X exit |
| **Sublime** | Ctrl+Shift+P palette, Ctrl+P goto, Ctrl+Z undo |
| **Emacs** | Ctrl+X Ctrl+S save, Ctrl+X Ctrl+F find |

## Themes

6 built-in theme presets:

| Theme | Description |
|-------|-------------|
| **Monokai** (default) | Dark, high contrast, green/pink accents |
| **Dracula** | Dark, purple/green/pink |
| **Nord** | Dark blue/gray, muted |
| **Catppuccin** | Dark purple/blue, soft |
| **GitHub Dark** | Dark blue, GitHub-inspired |
| **Solarized Dark** | Dark green/brown |

Auto-detects terminal dark/light mode on startup. Switch themes via command palette.

## OpenCode AI Panel

The right-side panel (Ctrl+`) integrates with the OpenCode CLI for AI-powered code assistance. If `opencode` is installed and on your PATH, you can type questions and get AI responses directly in the terminal.

## Configuration

ced reads two TOML config files, merged (project overrides global):

| Path | Scope |
|------|-------|
| `~/.config/ced/config.toml` | Global (all projects) |
| `.ced/config.toml` | Per-project |

### Full config reference
```toml
[theme]
mode = "auto"      # "auto", "dark", or "light"
name = "monokai"   # theme preset name

[editor]
tab_size = 4
soft_wrap = false
line_numbers = true
indent_guides = true
font_size = 12
show_minimap = false

[keybindings]
preset = "vscode"  # "vscode", "nano", "sublime", or "emacs"

[opencode]
path = "opencode"  # OpenCode CLI path
auto_start = true  # check CLI availability on startup
```

> Fields `indent_guides`, `font_size`, and `show_minimap` in `[editor]` are stored in the config for forward compatibility but are not yet wired to the editor widget — they will be activated in a future release.

## Project Layout

```
src/ced/
├── __init__.py          # Package init (exports Ced, Config, __version__)
├── __main__.py          # Entry point: python -m ced
├── app.py               # Main App class (Ced) — 15 bindings, 21 commands
├── config.py            # TOML config: dataclass + global/project merge
├── theme.tcss           # External CSS stylesheet
├── types.py             # Shared type aliases (ThemeMode, KeybindingPreset)
├── commands/
│   └── registry.py      # Command dataclass + CommandRegistry (fuzzy search)
├── editor/
│   ├── widget.py        # EnhancedCodeEditor (TextArea + auto language + load/save)
│   └── buffer.py        # Buffer + BufferManager (multi-file tabs)
├── keybindings/
│   ├── manager.py       # KeybindingManager (preset switching with overrides)
│   └── presets.py       # 4 presets: VS Code, nano, Sublime, Emacs
├── panels/
│   ├── file_tree.py     # FileTreePanel (DirectoryTree + file selected event)
│   ├── editor_area.py   # EditorArea (TabbedContent + editor management)
│   ├── opencode_panel.py # OpenCode AI panel (CLI integration)
│   ├── help_bar.py      # HelpBar (bottom bar with visible shortcuts)
│   ├── palette.py       # CommandPalette (modal screen, fuzzy filter)
│   ├── quick_open.py    # QuickOpen (file finder with os.walk)
│   ├── search_bar.py    # SearchBar (find + replace widget)
│   └── jump.py          # JumpMode (2-character navigation)
├── themes/
│   └── manager.py       # Theme definitions + auto dark/light detection
```

## Tech Stack
- **Python** 3.11+
- **Textual** 8.x — terminal UI framework
- **tree-sitter** (via Textual) — syntax highlighting
- **tomllib** (stdlib) — config parsing
- **OpenCode** CLI (optional) — AI integration

## License
AGPLv3. See [LICENSE](LICENSE) for details.