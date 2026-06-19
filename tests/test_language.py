from __future__ import annotations

from pathlib import Path

from ced.editor.widget import detect_language, LANGUAGE_MAP


class TestDetectLanguage:
    def test_none_path(self) -> None:
        assert detect_language(None) is None

    def test_python(self) -> None:
        assert detect_language("file.py") == "python"
        assert detect_language(Path("main.py")) == "python"

    def test_javascript(self) -> None:
        assert detect_language("app.js") == "javascript"
        assert detect_language("app.jsx") == "jsx"

    def test_typescript(self) -> None:
        assert detect_language("app.ts") == "typescript"
        assert detect_language("app.tsx") == "tsx"

    def test_rust(self) -> None:
        assert detect_language("main.rs") == "rust"

    def test_go(self) -> None:
        assert detect_language("main.go") == "go"

    def test_c_cpp(self) -> None:
        assert detect_language("file.c") == "c"
        assert detect_language("file.h") == "c"
        assert detect_language("file.cpp") == "cpp"
        assert detect_language("file.hpp") == "cpp"
        assert detect_language("file.cc") == "cpp"
        assert detect_language("file.cxx") == "cpp"
        assert detect_language("file.hxx") == "cpp"

    def test_csharp(self) -> None:
        assert detect_language("file.cs") == "csharp"

    def test_html_css(self) -> None:
        assert detect_language("index.html") == "html"
        assert detect_language("style.css") == "css"
        assert detect_language("style.scss") == "scss"
        assert detect_language("style.less") == "less"

    def test_json_yaml_toml(self) -> None:
        assert detect_language("data.json") == "json"
        assert detect_language("config.yaml") == "yaml"
        assert detect_language("config.yml") == "yaml"
        assert detect_language("config.toml") == "toml"

    def test_markdown(self) -> None:
        assert detect_language("readme.md") == "markdown"

    def test_shell(self) -> None:
        assert detect_language("script.sh") == "bash"
        assert detect_language("script.bash") == "bash"
        assert detect_language("script.zsh") == "bash"

    def test_unknown_extension(self) -> None:
        assert detect_language("file.xyz") is None

    def test_no_extension(self) -> None:
        assert detect_language("Makefile") is None

    def test_case_insensitive(self) -> None:
        assert detect_language("Main.PY") == "python"
        assert detect_language("APP.JS") == "javascript"

    def test_all_mapped_extensions(self) -> None:
        for ext, lang in LANGUAGE_MAP.items():
            result = detect_language(f"file{ext}")
            assert result == lang, f"Extension {ext} should map to {lang}, got {result}"
