from __future__ import annotations

from textual.widgets import Static


class StatusBar(Static):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._mode_text = "NORMAL"
        self._file_path = ""
        self._language = ""
        self._cursor_position = "Ln 1, Col 1"
        self._modified = False

    @property
    def mode_text(self) -> str:
        return self._mode_text

    @mode_text.setter
    def mode_text(self, value: str) -> None:
        self._mode_text = value
        self._render()

    @property
    def file_path(self) -> str:
        return self._file_path

    @file_path.setter
    def file_path(self, value: str) -> None:
        self._file_path = value
        self._render()

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        self._language = value
        self._render()

    @property
    def cursor_position(self) -> str:
        return self._cursor_position

    @cursor_position.setter
    def cursor_position(self, value: str) -> None:
        self._cursor_position = value
        self._render()

    @property
    def modified(self) -> bool:
        return self._modified

    @modified.setter
    def modified(self, value: bool) -> None:
        self._modified = value
        self._render()

    def _render(self) -> None:
        modified_flag = " ●" if self._modified else ""
        parts = [
            f"[bold]{self._mode_text}[/bold]",
        ]
        if self._file_path:
            parts.append(f"[reverse] {self._file_path}{modified_flag} [/reverse]")
        if self._language:
            parts.append(f"[dim]{self._language}[/dim]")
        if self._cursor_position:
            parts.append(f"[reverse] {self._cursor_position} [/reverse]")
        self.update(" │ ".join(parts))
