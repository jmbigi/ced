# Changelog

## [0.2.0] — 2026-06-22

### Added
- CHANGELOG.md y versioning semántico
- Dependencia `pyte` declarada en pyproject.toml
- Archivo `requirements-dev.txt` con dependencias de test versionadas
- Normalización SVG para snapshots deterministas (CSS class ordering)
- Validación de path traversal en open/save de archivos
- Límite de profundidad (`max_depth=15`) en QuickOpen para evitar `os.walk` infinito
- Límite máximo de tabs abiertas (100) para evitar fuga de memoria
- Autosave periódico cada 5 minutos para buffers modificados sin path
- `CHANGELOG.md` ignorado por .gitignore checks pre-commit

### Fixed
- `pyte` ausente en pyproject.toml causaba `ModuleNotFoundError` en terminal panel
- Tests `test_action_close_tab_modified` usaban `asyncio.run()` incorrectamente
- Test `test_editor_close_active_normal` asumía que 1 tab se elimina (reset branch)
- 14 errores de linter ruff (imports no usados, f-strings, variable muerta)
- RuntimeWarning: `Input.action_submit()` corrutina no await-eada
- RuntimeWarning: `DirectoryTree.watch_path` corrutina no await-eada

### Changed
- `normalize_svg()` ahora ordena CSS rules por contenido para snapshots estables
- README.md actualizado con troubleshooting, FAQ, y ejemplos de configuración
- App.py: validación de rutas en `open_file` y `save_file`
- QuickOpen: `max_depth=15` y exclusión de directorios del sistema

## [0.1.0] — 2026-06-18

### Added
- Release inicial: editor de código en terminal con Python + Textual
- Editor con syntax highlighting (tree-sitter, 40+ lenguajes)
- File tree sidebar (DirectoryTree)
- Multi-tab editing con open/save/close
- Quick Open file finder (Ctrl+P)
- Search & Replace (Ctrl+F / Ctrl+H)
- Command palette (Ctrl+Shift+P)
- Jump Mode (Ctrl+J)
- 4 keybinding presets: VS Code, nano, Sublime, Emacs
- 6 themes: Monokai, Dracula, Nord, Catppuccin, GitHub Dark, Solarized Dark
- OpenCode AI panel (integración CLI)
- Terminal panel (PTY fork)
- Confirmación de salida con archivos modificados
- Emergency save en SIGHUP
- Configuración TOML (global + project-local)
- Sistema de observabilidad UI (RR-81) con 4 niveles de debug
- 482 tests, 100% cobertura
- CI/CD con GitHub Actions (3.11/3.12/3.13)
- PyInstaller spec para build Windows
- Lecciones aprendidas documentadas en español
