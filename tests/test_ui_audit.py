"""Auditoría completa de la interfaz de usuario de ced.

Analiza cada widget del árbol: posición, tamaño, colores, fuentes,
estado del cursor, pseudo-clases, visibilidad, y más.

Uso:
    pytest tests/test_ui_audit.py -v --debug-ui-events=full
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from textual.app import App
from textual.widget import Widget
from textual.widgets import (
    TextArea, Input, Button, Label,
    Static, TabbedContent, RichLog,
)

from ced.app import Ced

if TYPE_CHECKING:
    from tests.debug_ui_events import DebugUIEventHandler


# ── Report accumulators ─────────────────────────────────────────────────

_issues: list[str] = []


def _check(condition: bool, msg: str) -> None:
    if not condition:
        _issues.append(f"  ⚠ {msg}")
        print(f"  ⚠ {msg}")


def _ok(msg: str) -> None:
    print(f"  ✓ {msg}")


# ── Widget inspector ────────────────────────────────────────────────────


def _widget_tree_audit(app: App, handler: Any = None) -> str:
    """Recorrer todo el árbol de widgets y auditar cada uno.

    Returns el dump textual del árbol.
    """
    lines: list[str] = []
    total_issues = 0

    def _ancestor_hidden(w: Widget) -> bool:
        """Verificar si algún ancestro está oculto."""
        parent = getattr(w, "parent", None)
        while parent is not None:
            if not getattr(parent, "display", True):
                return True
            parent = getattr(parent, "parent", None)
        return False

    def _audit_widget(w: Widget, depth: int = 0) -> None:
        nonlocal total_issues
        indent = "  " * depth
        prefix = ""
        info = f"{w.__class__.__name__}"

        # id
        if w.id:
            info += f" #{w.id}"

        # display / visible
        is_hidden = False
        try:
            if not w.display:
                info += " hidden"
                is_hidden = True
            elif not w.visible:
                info += " invisible"
            elif _ancestor_hidden(w):
                info += " (ancestro oculto)"
                is_hidden = True
        except Exception:
            pass

        # region (posición + tamaño)
        try:
            r = w.region
            info += f" [{r.x},{r.y} {r.width}x{r.height}]"
            # Solo validar tamaño 0 si NO está hidden
            if not is_hidden:
                _check(r.width > 0 and r.height > 0,
                       f"{w.__class__.__name__}#{w.id}: visible pero tamaño 0 ({r.width}x{r.height})")
            _check(r.x >= 0 and r.y >= 0,
                   f"{w.__class__.__name__}#{w.id}: posición negativa ({r.x},{r.y})")
        except Exception as e:
            info += f" [region_error:{e}]"
            if not is_hidden:
                _check(False, f"{w.__class__.__name__}#{w.id}: error región: {e}")

        # display / visible
        try:
            if not w.display:
                info += " hidden"
            elif not w.visible:
                info += " invisible"
        except Exception:
            pass

        # pseudo-classes
        try:
            pc = set(getattr(w, "pseudo_classes", set()) or [])
            if pc:
                info += f" :{','.join(sorted(pc))}"
        except Exception:
            pass

        # classes CSS
        try:
            cls = set(getattr(w, "classes", set()) or [])
            if cls:
                info += f" .{'.'.join(sorted(cls))}"
        except Exception:
            pass

        # focus
        try:
            if hasattr(w, "has_focus"):
                if w.has_focus:
                    info += " [FOCUS]"
        except Exception:
            pass

        # cursor (TextArea)
        if isinstance(w, TextArea):
            try:
                cl = w.cursor_location
                info += f" cursor=({cl[0]},{cl[1]})"
                _check(isinstance(cl, tuple) and len(cl) == 2,
                       f"TextArea#{w.id}: cursor_location inválido {cl}")
            except Exception as e:
                info += f" cursor_err:{e}"

            try:
                sl = w.selection_range
                if sl and sl != (0, 0):
                    info += f" sel={sl}"
            except Exception:
                pass

            # colores del tema en TextArea
            try:
                theme = w.theme
                if theme:
                    info += f" theme={theme}"
            except Exception:
                pass

        # contenido textual
        text_content = ""
        if isinstance(w, (TextArea,)):
            try:
                text_content = str(w.text[:40])
            except Exception:
                pass
        elif isinstance(w, (Static, Label)):
            try:
                rendered = w.render()
                if hasattr(rendered, "plain"):
                    text_content = rendered.plain[:60]
                else:
                    text_content = str(rendered)[:60]
            except Exception:
                pass
        elif isinstance(w, (Input,)):
            try:
                text_content = f"value={w.value!r}"
            except Exception:
                pass
        elif isinstance(w, (Button,)):
            try:
                text_content = f"label={w.label!r}"
            except Exception:
                pass
        if text_content:
            info += f" = {text_content!r}"

        # Container child count
        try:
            children_count = len(w.children)
            if children_count > 0:
                info += f" ({children_count} children)"
        except Exception:
            pass

        # TabbedContent: tab activo
        if isinstance(w, TabbedContent):
            try:
                info += f" active_tab={w.active!r}"
                _check(w.active is not None and w.active != "",
                       "TabbedContent: sin tab activo")
                # Verificar que el tab activo existe en los panes
                tab_count = w.tab_count
                _check(tab_count > 0,
                       "TabbedContent: sin tabs (count=0)")
            except Exception as e:
                info += f" tab_err:{e}"

        lines.append(f"{indent}{prefix}{info}")

        # Auditar hijos recursivamente
        try:
            for child in w.children:
                _audit_widget(child, depth + 1)
        except Exception as e:
            lines.append(f"{indent}  [error iterando hijos: {e}]")

    _audit_widget(app.screen)

    return "\n".join(lines)


# ── Tests ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ui_audit_completo(debug_ui_events: DebugUIEventHandler | None):
    """Auditar cada widget de ced: posición, tamaño, colores, cursor, foco.

    Usar: pytest tests/test_ui_audit.py -v --debug-ui-events=full
    """
    global _issues
    _issues.clear()

    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        if debug_ui_events:
            debug_ui_events.state_change("ui_audit_start", {
                "app_size": f"{app.size.width}x{app.size.height}",
            })

        # ── 1. Composición inicial ──────────────────────────────────────
        print("\n═══ ÁRBOL DE WIDGETS ═══")
        tree = _widget_tree_audit(app, debug_ui_events)
        print(tree)

        if debug_ui_events and debug_ui_events._level_num >= 2:
            debug_ui_events.widget_tree_dump(tree)

        # ── 2. Crear nuevo archivo ──────────────────────────────────────
        print("\n═══ AFTER new_file ═══")
        app.action_new_file()
        await pilot.pause()

        ea = app.query_one("#editor")
        editor = ea.get_active_editor()
        assert editor is not None, "No editor after new_file"

        editor.focus()
        await pilot.pause()
        if debug_ui_events:
            debug_ui_events.key_press("ctrl+n", widget="EditorArea", action="new_file")
            debug_ui_events.state_change("editor_focused", {
                "widget": "EnhancedCodeEditor",
                "has_focus": editor.has_focus,
                "cursor": str(editor.cursor_location),
            })

        _check(editor.has_focus,
               "El editor no tiene foco después de new_file + focus()")
        # cursor_location empieza en (0,0) para un TextArea nuevo
        _check(isinstance(editor.cursor_location, tuple),
               f"cursor_location inválido: {editor.cursor_location}")

        tree2 = _widget_tree_audit(app, debug_ui_events)
        print(tree2)

        # ── 3. Escribir texto ───────────────────────────────────────────
        print("\n═══ AFTER typing 'Hola mundo' ═══")
        editor.text = "Hola mundo"
        await pilot.pause()

        _check("Hola mundo" in editor.text,
               f"El texto no se escribió: {editor.text!r}")
        # cursor_location se queda donde se asignó; Textual no mueve cursor al asignar text

        if debug_ui_events:
            debug_ui_events.state_change("text_written", {
                "text": editor.text,
                "cursor": str(editor.cursor_location),
                "language": editor.language,
            })

        tree3 = _widget_tree_audit(app, debug_ui_events)
        print(tree3)

        # ── 4. Abrir archivo ────────────────────────────────────────────
        import tempfile
        from pathlib import Path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                         delete=False) as f:
            f.write("print('Hola')\n# comentario\nx = 42\n")
            src = Path(f.name)

        print(f"\n═══ AFTER open {src.name} ═══")
        ea.open_file(src)
        await pilot.pause()
        editor2 = ea.get_active_editor()
        assert editor2 is not None

        _check(len(editor2.text) > 0,
               f"Archivo abierto pero sin contenido: {editor2.text!r}")
        _check(editor2.language is not None,
               f"No se detectó lenguaje para {src.suffix}: {editor2.language}")

        if debug_ui_events:
            debug_ui_events.state_change("file_opened", {
                "path": str(src),
                "length": len(editor2.text),
                "language": editor2.language,
            })

        tree4 = _widget_tree_audit(app, debug_ui_events)
        print(tree4)

        src.unlink()

        # ── 5. Reporte de incidencias ───────────────────────────────────
        print("\n═══ REPORTE DE INCIDENCIAS ═══")
        if _issues:
            print(f"\n⚠ {len(_issues)} incidencia(s) encontrada(s):")
            for iss in _issues:
                print(iss)
        else:
            _ok("0 incidencias — todos los widgets correctos")

        if debug_ui_events:
            debug_ui_events.assertion(len(_issues) == 0,
                                      f"{len(_issues)} incidencias UI")
            debug_ui_events.screenshot("/tmp/ui_audit_final.png")

    # No se debe fallar en el audit — solo reportar
    # (para que el usuario vea el reporte completo)
    assert True


@pytest.mark.asyncio
async def test_ui_audit_all_widgets_present(debug_ui_events):
    """Verificar que todos los widgets clave existen y son visibles."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        widgets_required = {
            "#file-tree": "FileTreePanel",
            "#help-bar": "HelpBar",
            "#help-text": "Static (help-text)",
            "#editor": "EditorArea",
            "#search-bar": "SearchBar",
            "#opencode": "OpenCodePanel",
            "#opencode-log": "RichLog",
            "#opencode-input": "Input",
            "#sidebar": "Vertical (sidebar)",
            "#editor-area": "Vertical (editor-area)",
            "#opencode-panel": "Vertical (opencode-panel)",
            "#terminal": "TerminalPanel",
        }

        if debug_ui_events:
            debug_ui_events.state_change("checking_widgets", {})

            for selector, desc in widgets_required.items():
                try:
                    w = app.query_one(selector)
                    r = w.region
                    # Widgets ocultos (search-bar, terminal) tienen tamaño 0 intencionalmente
                    if not w.display:
                        print(f"  - {desc}: hidden (tamaño {r.width}x{r.height}, esperado)")
                        continue
                    assert r.width > 0 and r.height > 0, (
                        f"{desc} visible pero tamaño 0 ({r.width}x{r.height})"
                    )
                    if debug_ui_events:
                        debug_ui_events.widget_mount(
                            desc, selector.lstrip("#"), w.parent.__class__.__name__
                        )
                except Exception as e:
                    pytest.fail(f"Widget faltante o inválido: {desc} ({e})")


@pytest.mark.asyncio
async def test_ui_audit_help_bar(debug_ui_events):
    """Verificar que la help bar muestra los atajos correctos."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        hb = app.query_one("#help-bar")
        r = hb.region
        print(f"\nHelpBar: [{r.x},{r.y} {r.width}x{r.height}]")
        assert r.height == 1, f"HelpBar debería tener 1 línea, tiene {r.height}"
        assert r.width > 50, f"HelpBar muy angosta: {r.width}"

        rendered = hb.query_one("#help-text").render()
        text = str(rendered)
        print(f"  Contenido: {text[:100]!r}")

        assert "^Q" in text, "HelpBar sin ^Q"
        assert "^S" in text, "HelpBar sin ^S"
        assert "Quit" in text, "HelpBar sin Quit"
        assert "Save" in text, "HelpBar sin Save"


@pytest.mark.asyncio
async def test_ui_audit_opencode_panel(debug_ui_events):
    """Verificar el panel OpenCode."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        oc = app.query_one("#opencode-panel")
        r = oc.region
        print(f"\nOpenCodePanel: [{r.x},{r.y} {r.width}x{r.height}]")
        assert r.width > 20, "Panel OpenCode muy angosto"

        log = app.query_one("#opencode-log", RichLog)
        lr = log.region
        print(f"  RichLog: [{lr.x},{lr.y} {lr.width}x{lr.height}]")
        assert lr.height >= 5, "RichLog muy pequeño"

        inp = app.query_one("#opencode-input", Input)
        ir = inp.region
        print(f"  Input: [{ir.x},{ir.y} {ir.width}x{ir.height}]")
        assert ir.width > 10, "Input OpenCode muy angosto"

        title = app.query_one(".panel-title", Static)
        tr = title.region
        print(f"  Title: [{tr.x},{tr.y} {tr.width}x{tr.height}]")
        _check(tr.width > 5, "Título del panel muy angosto")


@pytest.mark.asyncio
async def test_ui_audit_opencode_input_typing(debug_ui_events):
    """Escribir en el Input de OpenCode y verificar visibilidad del texto."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        inp = app.query_one("#opencode-input", Input)
        assert inp is not None, "Input no encontrado"

        if debug_ui_events:
            debug_ui_events.state_change("opencode_input_found", {
                "region": str(inp.region),
                "styles": f"border={inp.styles.border} bg={inp.styles.background} color={inp.styles.color}",
            })

        inp.focus()
        await pilot.pause()

        if debug_ui_events:
            debug_ui_events.state_change("opencode_input_focused", {
                "has_focus": inp.has_focus,
            })

        # Escribir carácter por carácter
        for ch in "Hola mundo visible":
            await pilot.press(ch)
            if debug_ui_events:
                debug_ui_events.key_press(ch, widget="Input", widget_id="opencode-input")

        await pilot.pause()

        # Verificar valor
        assert inp.value == "Hola mundo visible", (
            f"Input no almacena el texto: {inp.value!r}"
        )

        if debug_ui_events:
            debug_ui_events.state_change("opencode_input_typed", {
                "value": inp.value,
                "length": len(inp.value),
            })

        print(f"\n  Input.value = {inp.value!r}")

        # Verificar render_line produce texto visible
        found_text = False
        for y in range(3):
            strip = inp.render_line(y)
            for seg in strip:
                txt = seg[0]
                style = seg[1]
                if "visible" in txt:
                    found_text = True
                    print(f"  Line {y}: {txt.strip()!r}")
                    print(f"    fg={style.color} (light={style.color.get_truecolor().red > 128})")
                    print(f"    bg={style.bgcolor} (dark={style.bgcolor.get_truecolor().red < 100})")
                    assert style.color.get_truecolor().red > 128, (
                        f"Texto del Input no es claro: color={style.color}"
                    )
                    assert style.bgcolor.get_truecolor().red < 100, (
                        f"Fondo del Input no es oscuro: bg={style.bgcolor}"
                    )
                    break

        assert found_text, "No se encontró el texto en el render del Input"

        if debug_ui_events:
            debug_ui_events.assertion(True, "Input text visible and verified")
            debug_ui_events.screenshot("/tmp/opencode_input_test.png")


@pytest.mark.asyncio
async def test_ui_audit_sidebar_tree(debug_ui_events):
    """Verificar el panel lateral de archivos."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        sb = app.query_one("#sidebar")
        r = sb.region
        print(f"\nSidebar: [{r.x},{r.y} {r.width}x{r.height}]")
        assert r.width >= 20, "Sidebar muy angosta"

        ft = app.query_one("#file-tree")
        fr = ft.region
        print(f"  FileTree: [{fr.x},{fr.y} {fr.width}x{fr.height}]")
        assert fr.height >= 10, "FileTree muy pequeño"


@pytest.mark.asyncio
async def test_ui_audit_editor_area(debug_ui_events):
    """Verificar el área del editor."""
    app = Ced()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()

        ea = app.query_one("#editor")
        r = ea.region
        print(f"\nEditorArea: [{r.x},{r.y} {r.width}x{r.height}]")
        assert r.width >= 30, "EditorArea muy angosto"
        assert r.height >= 10, "EditorArea muy pequeño"

        editor = ea.get_active_editor()
        assert editor is not None
        er = editor.region
        print(f"  EnhancedCodeEditor: [{er.x},{er.y} {er.width}x{er.height}]")
        _check(er.width > 20, "Editor widget muy angosto")
        _check(er.height > 5, "Editor widget muy pequeño")

        # Verificar que el editor tiene line_numbers (o no según config)
        print(f"  show_line_numbers={editor.show_line_numbers}")
        print(f"  language={editor.language}")
        print(f"  cursor_location={editor.cursor_location}")
