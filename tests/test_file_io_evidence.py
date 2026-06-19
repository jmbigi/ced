from __future__ import annotations

from pathlib import Path

from ced.editor.widget import EnhancedCodeEditor, detect_language
from ced.editor.buffer import Buffer, BufferManager


# ── PRUEBAS DE ESCRITURA/LECTURA DE ARCHIVOS ──────────────────────────
# Cada prueba imprime evidencia visible del resultado.


class TestFileWriteRead:
    """Evidencia: escribir archivos → leer contenido → verificar caracteres."""

    def test_write_then_read_text(self, tmp_path: Path) -> None:
        """Escribir y leer un archivo de texto plano."""
        f = tmp_path / "prueba.txt"
        f.write_text("Hola mundo!\nLinea 2\nLinea 3\n")
        content = f.read_text()
        print(f"\n  Archivo: {f}")
        print(f"  Contenido escrito: {repr(content)}")
        print(f"  Líneas: {content.count(chr(10)) + 1}")
        assert content == "Hola mundo!\nLinea 2\nLinea 3\n"

    def test_write_read_unicode(self, tmp_path: Path) -> None:
        """Caracteres Unicode: acentos, emojis, símbolos."""
        f = tmp_path / "unicode.txt"
        text = "áéíóúñü¡¿€💡\n日本語\nРусский\n"
        f.write_text(text)
        content = f.read_text()
        print(f"\n  Unicode escrito: {repr(text[:60])}...")
        print(f"  Unicode leído:   {repr(content[:60])}...")
        assert content == text

    def test_write_read_empty(self, tmp_path: Path) -> None:
        """Archivo vacío."""
        f = tmp_path / "vacio.txt"
        f.write_text("")
        content = f.read_text()
        print(f"\n  Archivo vacío: tamaño={len(content)} bytes")
        assert len(content) == 0

    def test_write_read_binary(self, tmp_path: Path) -> None:
        """Bytes binarios (no solo texto)."""
        f = tmp_path / "binario.bin"
        data = bytes(range(256))
        f.write_bytes(data)
        read_back = f.read_bytes()
        print(f"\n  Bytes escritos: {len(data)} bytes")
        print(f"  Bytes leídos:   {len(read_back)} bytes")
        print(f"  Coinciden: {data == read_back}")
        assert data == read_back

    def test_write_append(self, tmp_path: Path) -> None:
        """Añadir contenido a un archivo existente."""
        f = tmp_path / "append.txt"
        f.write_text("linea1\n")
        with f.open("a") as fh:
            fh.write("linea2\n")
            fh.write("linea3\n")
        content = f.read_text()
        lines = content.strip().split("\n")
        print(f"\n  Archivo tras append: {len(lines)} líneas")
        for i, line in enumerate(lines, 1):
            print(f"    Línea {i}: {line!r}")
        assert len(lines) == 3

    def test_many_lines(self, tmp_path: Path) -> None:
        """Archivo con 10,000 líneas."""
        f = tmp_path / "muchas_lineas.txt"
        lines = [f"linea_{i}" for i in range(10000)]
        f.write_text("\n".join(lines))
        read_back = f.read_text()
        count = read_back.count("\n") + 1
        print(f"\n  Líneas escritas: {len(lines)}")
        print(f"  Líneas leídas:   {count}")
        assert count == 10000


class TestEnhancedCodeEditorIO:
    """Evidencia: EnhancedCodeEditor carga/guarda archivos correctamente."""

    def test_editor_load_and_read(self, tmp_path: Path) -> None:
        """Cargar archivo en el editor y verificar el texto."""
        src = tmp_path / "codigo.py"
        src.write_text("x = 42\nprint(x)\n")
        editor = EnhancedCodeEditor()
        editor.load_file(src)
        print(f"\n  Archivo: {src}")
        print(f"  Texto en editor: {repr(editor.text)}")
        print(f"  Lenguaje: {editor.language}")
        assert editor.text == "x = 42\nprint(x)\n"
        assert editor.language == "python"
        assert editor.file_path == src

    def test_editor_modify_and_save(self, tmp_path: Path) -> None:
        """Modificar texto en el editor y guardar a disco."""
        dest = tmp_path / "output.txt"
        dest.write_text("")
        editor = EnhancedCodeEditor(path=dest)
        editor.text = "contenido nuevo\nsegunda linea\n"
        result = editor.save_file()
        on_disk = dest.read_text()
        print(f"\n  Texto en editor: {repr(editor.text)}")
        print(f"  Guardado en: {dest}")
        print(f"  En disco:     {repr(on_disk)}")
        print(f"  Resultado save_file: {result}")
        assert result is True
        assert on_disk == "contenido nuevo\nsegunda linea\n"

    def test_editor_save_as(self, tmp_path: Path) -> None:
        """Guardar como — escribe en una ruta nueva."""
        copy = tmp_path / "copia.txt"
        editor = EnhancedCodeEditor()
        editor.text = "texto para copiar"
        editor.save_as(copy)
        on_disk = copy.read_text()
        print(f"\n  Texto original: {repr(editor.text)}")
        print(f"  Guardado como: {copy}")
        print(f"  En disco:      {repr(on_disk)}")
        print(f"  file_path tras save_as: {editor.file_path}")
        assert on_disk == "texto para copiar"
        assert editor.file_path == copy

    def test_editor_save_without_path(self) -> None:
        """save_file() sin file_path → False."""
        editor = EnhancedCodeEditor()
        result = editor.save_file()
        print(f"\n  save_file sin path: {result}")
        assert result is False

    def test_editor_language_auto_detect(self, tmp_path: Path) -> None:
        """Detección automática de lenguaje por extensión."""
        for ext, expected_lang in [
            (".py", "python"),
            (".rs", "rust"),
            (".js", "javascript"),
            (".md", "markdown"),
        ]:
            f = tmp_path / f"archivo{ext}"
            f.write_text("")
            ed = EnhancedCodeEditor(path=f)
            print(f"  {ext:6s} → {ed.language:12s} (esperado: {expected_lang})")
            assert ed.language == expected_lang

    def test_editor_clean_history_on_load(self, tmp_path: Path) -> None:
        """load_file limpia el historial de cambios."""
        src = tmp_path / "historial.txt"
        src.write_text("original")
        editor = EnhancedCodeEditor()
        editor.text = "basura temporal"
        editor.load_file(src)
        print(f"\n  Texto tras load_file: {repr(editor.text)}")
        assert editor.text == "original"


class TestBufferManagerPersistence:
    """Evidencia: BufferManager gestiona buffers con paths correctos."""

    def test_buffer_path_tracking(self, tmp_path: Path) -> None:
        """Buffer recuerda su path después de open."""
        bm = BufferManager()
        buf = bm.open(tmp_path / "a.py")
        print(f"\n  Buffer abierto: {buf}")
        print(f"  Buffer.name: {buf.name}")
        print(f"  Buffer.path: {buf.path}")
        assert buf.name == "a.py"
        assert buf.path == tmp_path / "a.py"

    def test_buffer_get_by_path(self, tmp_path: Path) -> None:
        """Buscar buffer por path."""
        bm = BufferManager()
        bm.open(tmp_path / "x.py")
        found = bm.get_by_path(tmp_path / "x.py")
        print(f"\n  Buffer buscado por path: {found}")
        assert found is not None
        assert found.name == "x.py"

    def test_buffer_modified_flag(self) -> None:
        """Flag de modificación."""
        b = Buffer()
        assert b.is_modified is False
        b.mark_modified()
        print(f"\n  Buffer tras mark_modified: is_modified={b.is_modified}")
        assert b.is_modified is True
        b.mark_saved()
        print(f"  Buffer tras mark_saved:   is_modified={b.is_modified}")
        assert b.is_modified is False

    def test_buffer_directory(self) -> None:
        """Directorio del buffer."""
        b = Buffer(Path("/home/user/project/main.py"))
        print(f"\n  Buffer.directory: {b.directory}")
        assert b.directory == "/home/user/project"
        b2 = Buffer()
        print(f"  Buffer sin path:  directory='{b2.directory}'")
        assert b2.directory == ""


class TestCharacterInput:
    """Evidencia: se pueden ingresar caracteres en el editor."""

    def test_insert_characters(self) -> None:
        """Insertar caracteres uno por uno."""
        editor = EnhancedCodeEditor()
        texto = ""
        for ch in "Hola Mundo 123!@#":
            texto += ch
        editor.text = texto
        print(f"\n  Caracteres insertados: {len(texto)}")
        print(f"  Texto final: {repr(editor.text)}")
        assert editor.text == "Hola Mundo 123!@#"

    def test_insert_multiline(self) -> None:
        """Insertar múltiples líneas."""
        editor = EnhancedCodeEditor()
        editor.text = "linea1\nlinea2\nlinea3"
        lines = editor.text.split("\n")
        print(f"\n  Líneas: {len(lines)}")
        for i, line in enumerate(lines, 1):
            print(f"    Línea {i}: {line!r}")
        assert len(lines) == 3
        assert editor.text.count("\n") == 2

    def test_large_text(self) -> None:
        """10,000 caracteres en el editor."""
        editor = EnhancedCodeEditor()
        editor.text = "a" * 10000
        print(f"\n  Longitud del texto: {len(editor.text)}")
        assert len(editor.text) == 10000

    def test_unicode_characters(self) -> None:
        """Caracteres Unicode en el editor."""
        editor = EnhancedCodeEditor()
        text = "áéíóúñü€💡日本語"
        editor.text = text
        print(f"\n  Unicode en editor: {repr(editor.text)}")
        assert editor.text == text
        assert len(editor.text) == len(text)


class TestDetectLanguage:
    """Evidencia: detección de lenguaje por extensión de archivo."""

    def test_all_extensions_mapped(self) -> None:
        """Cada extensión conocida devuelve un lenguaje."""
        from ced.editor.widget import LANGUAGE_MAP

        for ext, lang in LANGUAGE_MAP.items():
            detected = detect_language(Path(f"archivo{ext}"))
            print(f"  {ext:10s} → {detected}")
            assert detected == lang, f"{ext} → esperado {lang}, obtenido {detected}"

    def test_unknown_extension_returns_none(self) -> None:
        """Extensión desconocida devuelve None."""
        lang = detect_language(Path("archivo.xyz"))
        print(f"\n  Extensión .xyz → {lang}")
        assert lang is None

    def test_no_extension_returns_none(self) -> None:
        """Archivo sin extensión devuelve None."""
        lang = detect_language(Path("Makefile"))
        print(f"\n  Sin extensión → {lang}")
        assert lang is None
