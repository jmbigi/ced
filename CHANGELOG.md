# Changelog

## [0.2.1] — 2026-06-22

### Added
- `Config._merge()`: re-validación de `tab_size`, `font_size`, `opencode.path` tras merge
- `save_file()`/`save_as()`: creación automática de directorio padre via `mkdir(parents=True)`
- `Config.load()`: tolera TOML inválido o archivo corrupto (catch TOMLDecodeError)
- `_assert_safe_display()`: protección contra ejecución de tests visuales en display real
- Marcardor `@pytest.mark.visual` en todos los tests que usan pyautogui/cv2
- `addopts = "-m 'not visual'"` en pyproject.toml: tests peligrosos no se ejecutan por defecto
- Tests unitarios para i18n (5 tests), merge validation (4 tests), path creation (2 tests)

### Fixed
- `test_opencode_worker_paths`: mi rewrite de opencode_panel.py eliminó `_write_log()` y `_check_opencode()`
- `test_editor_close_active_normal`: solo 1 tab entraba en reset branch y no eliminaba tab
- `test_config.py`: múltiples tests rotos por cambios en config.py (restaurada lógica original)
- `.gitignore`: `__snapshots__/` ignoraba TODOS los baselines; cambiado a `__snapshots__/__new__/`
- `keybindings/manager.py`: mi rewrite usó `get_preset()` que nunca retorna None (fallback a vscode)
- `commands/registry.py`: mi rewrite eliminó `difflib.SequenceMatcher` y `*args, **kwargs` en execute()
- `themes/manager.py`: mi rewrite usó `sys.platform` pero tests parchean `os.name`
- `themes/manager.py`: `THEMES` renombrado a `_THEMES` rompió import en tests
- `version fallback`: `__init__.py` retornaba "0.1.0" en vez de "0.2.0"
- `open_file()`: atrapaba solo `PermissionError`/`FileNotFoundError`, no `IsADirectoryError` (OSError genérico)
- Tests visuales (`test_visual_png.py:145`): `pyautogui.write("def f():\n    pass\n")` se ejecutaba en display real

## [0.2.0] — 2026-06-22

### Added
- CHANGELOG.md y versioning semántico
- Dependencia `pyte` declarada en pyproject.toml
- Archivo `requirements-dev.txt` con dependencias de test versionadas
- Validación de path traversal en open/save de archivos
- Límite de profundidad (`max_depth=15`) en QuickOpen para evitar `os.walk` infinito
- Límite máximo de tabs abiertas (100) para evitar fuga de memoria
- Autosave periódico cada 5 minutos
- Sistema de internacionalización (gettext) con traducción al español
- Tooltips descriptivos en todos los widgets principales
- Graceful degradation en terminal panel (fallback si no hay PTY)
- EVALUACION.md con 30 áreas de evaluación y plan de mejoras
- `CHANGELOG.md` ignorado por .gitignore checks pre-commit

### Fixed
- `pyte` ausente en pyproject.toml causaba `ModuleNotFoundError` en terminal panel
- Tests `test_action_close_tab_modified` usaban `asyncio.run()` incorrectamente
- Test `test_editor_close_active_normal` asumía que 1 tab se elimina (reset branch)
- 14 errores de linter ruff (imports no usados, f-strings, variable muerta)
- RuntimeWarning: `Input.action_submit()` corrutina no await-eada
- RuntimeWarning: `DirectoryTree.watch_path` corrutina no await-eada
- SVG snapshots no-deterministas reemplazados por text-extraction estable

### Changed
- README.md actualizado con troubleshooting, FAQ, y ejemplos de configuración
- App.py: validación de rutas con Path.resolve(), notificaciones más descriptivas
- QuickOpen: `max_depth=15` para evitar recorridos infinitos
- Terminal: imports condicionales para portabilidad Windows/macOS
- EditorArea: comentarios en inglés, límite de tabs

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
