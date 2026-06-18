from __future__ import annotations

from pathlib import Path
from typing import Iterator


class Buffer:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.is_modified = False
        self.is_new = True

    @property
    def name(self) -> str:
        if self.path:
            return self.path.name
        return "untitled"

    @property
    def directory(self) -> str:
        if self.path:
            return str(self.path.parent)
        return ""

    def __repr__(self) -> str:
        return f"Buffer({self.name}, modified={self.is_modified})"


class BufferManager:
    def __init__(self) -> None:
        self._buffers: list[Buffer] = []
        self._active_index: int = -1

    @property
    def active_buffer(self) -> Buffer | None:
        if 0 <= self._active_index < len(self._buffers):
            return self._buffers[self._active_index]
        return None

    @property
    def active_index(self) -> int:
        return self._active_index

    @active_index.setter
    def active_index(self, value: int) -> None:
        if 0 <= value < len(self._buffers):
            self._active_index = value

    @property
    def count(self) -> int:
        return len(self._buffers)

    def __iter__(self) -> Iterator[Buffer]:
        return iter(self._buffers)

    def __getitem__(self, index: int) -> Buffer:
        return self._buffers[index]

    def add(self, path: Path | None = None) -> Buffer:
        buf = Buffer(path)
        self._buffers.append(buf)
        self._active_index = len(self._buffers) - 1
        return buf

    def remove(self, index: int) -> None:
        if 0 <= index < len(self._buffers):
            self._buffers.pop(index)
            if self._active_index >= len(self._buffers):
                self._active_index = max(0, len(self._buffers) - 1)

    def get_by_path(self, path: Path) -> Buffer | None:
        for buf in self._buffers:
            if buf.path and buf.path.resolve() == path.resolve():
                return buf
        return None

    def open(self, path: Path) -> Buffer:
        existing = self.get_by_path(path)
        if existing:
            self._active_index = self._buffers.index(existing)
            return existing
        buf = self.add(path)
        buf.is_new = False
        return buf

    def close_active(self) -> Buffer | None:
        if self.active_buffer:
            buf = self.active_buffer
            self.remove(self._active_index)
            return buf
        return None

    def switch_next(self) -> None:
        if len(self._buffers) > 0:
            self._active_index = (self._active_index + 1) % len(self._buffers)

    def switch_prev(self) -> None:
        if len(self._buffers) > 0:
            self._active_index = (self._active_index - 1) % len(self._buffers)
