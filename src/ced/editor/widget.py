from __future__ import annotations

from pathlib import Path

from textual.widgets import TextArea

LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".hxx": "cpp",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hh": "cpp",
    ".cs": "csharp",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
    ".sql": "sql",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".ps1": "powershell",
    ".bat": "bat",
    ".cmd": "bat",
    ".tex": "latex",
    ".csv": "csv",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "ini",
    ".env": "dotenv",
    ".dockerfile": "dockerfile",
    ".lua": "lua",
    ".r": "r",
    ".pl": "perl",
    ".pm": "perl",
    ".vue": "vue",
    ".svelte": "svelte",
    ".astro": "astro",
    ".zig": "zig",
    ".nim": "nim",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hrl": "erlang",
    ".clj": "clojure",
    ".cljs": "clojure",
    ".edn": "clojure",
    ".hs": "haskell",
    ".lhs": "haskell",
    ".ml": "ocaml",
    ".mli": "ocaml",
    ".fs": "fsharp",
    ".fsx": "fsharp",
    ".scala": "scala",
    ".sc": "scala",
    ".dart": "dart",
    ".coffee": "coffeescript",
    ".groovy": "groovy",
    ".gradle": "groovy",
    ".jl": "julia",
    ".cr": "crystal",
    ".mak": "makefile",
    ".cmake": "cmake",
}


def detect_language(path: Path | str | None) -> str | None:
    """Detect tree-sitter language name from a file path's extension."""
    if path is None:
        return None
    p = Path(path)
    return LANGUAGE_MAP.get(p.suffix.lower())


class EnhancedCodeEditor(TextArea):
    """A TextArea subclass with file I/O and automatic language detection."""

    def __init__(
        self,
        path: Path | str | None = None,
        show_line_numbers: bool = True,
        soft_wrap: bool = False,
        indent_width: int = 4,
        *args,
        **kwargs,
    ) -> None:
        self._file_path: Path | None = Path(path) if path else None
        language = detect_language(self._file_path)
        super().__init__(
            *args,
            **kwargs,
            language=language,
            show_line_numbers=show_line_numbers,
            soft_wrap=soft_wrap,
        )
        self.indent_width = indent_width

    @property
    def file_path(self) -> Path | None:
        """Return the path of the currently open file, or None."""
        return self._file_path

    @file_path.setter
    def file_path(self, value: Path | str | None) -> None:
        """Set the file path and update the language mode."""
        self._file_path = Path(value) if value else None
        lang = detect_language(self._file_path)
        if lang:
            self.language = lang

    @staticmethod
    def _resolve_path(path: Path | str) -> Path:
        p = Path(path).resolve()
        return p

    def load_file(self, path: Path | str) -> None:
        """Load file content from *path* into the editor."""
        p = self._resolve_path(path)
        self.file_path = p
        self.text = p.read_text(encoding="utf-8", errors="replace")
        self.history.clear()

    def save_file(self) -> bool:
        """Write editor content to disk. Returns True on success."""
        if self._file_path is None:
            return False
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file_path.write_text(self.text, encoding="utf-8")
        return True

    def save_as(self, path: Path | str) -> None:
        """Write editor content to *path* and update the file path."""
        p = self._resolve_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.text, encoding="utf-8")
        self.file_path = p
