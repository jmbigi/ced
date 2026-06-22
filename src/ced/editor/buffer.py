from __future__ import annotations

from pathlib import Path
from typing import Iterator


class Buffer:
    """Represents an open file buffer with modification tracking."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.is_modified = False

    def mark_modified(self) -> None:
        """Mark this buffer as having unsaved changes."""
        self.is_modified = True

    def mark_saved(self) -> None:
        """Mark this buffer as saved (no unsaved changes)."""
        self.is_modified = False

    @property
    def name(self) -> str:
        """Return the display name (filename or 'untitled')."""
        if self.path:
            return self.path.name
        return "untitled"

    @property
    def directory(self) -> str:
        """Return the parent directory path, or empty string."""
        if self.path:
            return str(self.path.parent)
        return ""

    def __repr__(self) -> str:
        return f"Buffer({self.name}, modified={self.is_modified})"


class BufferManager:
    """Manages a list of open file buffers with an active index."""

    def __init__(self) -> None:
        self._buffers: list[Buffer] = []
        self._active_index: int = -1

    @property
    def active_buffer(self) -> Buffer | None:
        """Return the currently active buffer, or None."""
        if 0 <= self._active_index < len(self._buffers):
            return self._buffers[self._active_index]
        return None

    @property
    def active_index(self) -> int:
        """Return the index of the active buffer."""
        return self._active_index

    @active_index.setter
    def active_index(self, value: int) -> None:
        """Set the active buffer index (clamped to valid range)."""
        if 0 <= value < len(self._buffers):
            self._active_index = value

    @property
    def count(self) -> int:
        """Return the total number of open buffers."""
        return len(self._buffers)

    def __iter__(self) -> Iterator[Buffer]:
        return iter(self._buffers)

    def __getitem__(self, index: int) -> Buffer:
        return self._buffers[index]

    def add(self, path: Path | None = None) -> Buffer:
        """Create and append a new buffer, making it active."""
        buf = Buffer(path)
        self._buffers.append(buf)
        self._active_index = len(self._buffers) - 1
        return buf

    def remove(self, index: int) -> None:
        """Remove the buffer at *index* and adjust active index."""
        if 0 <= index < len(self._buffers):
            self._buffers.pop(index)
            if self._active_index > index:
                self._active_index -= 1
            elif self._active_index >= len(self._buffers):
                self._active_index = max(0, len(self._buffers) - 1)

    def get_by_path(self, path: Path) -> Buffer | None:
        """Find an existing buffer for *path* (resolved), or None."""
        for buf in self._buffers:
            if buf.path and buf.path.resolve() == path.resolve():
                return buf
        return None

    def open(self, path: Path) -> Buffer:
        """Open *path*: return existing buffer or create a new one."""
        existing = self.get_by_path(path)
        if existing:
            self._active_index = self._buffers.index(existing)
            return existing
        buf = self.add(path)
        return buf

    def close_active(self) -> Buffer | None:
        """Close and return the active buffer, or None."""
        if self.active_buffer:
            buf = self.active_buffer
            self.remove(self._active_index)
            return buf
        return None

    def switch_next(self) -> None:
        """Switch to the next buffer (wraps around)."""
        if len(self._buffers) > 0:
            self._active_index = (self._active_index + 1) % len(self._buffers)

    def switch_prev(self) -> None:
        """Switch to the previous buffer (wraps around)."""
        if len(self._buffers) > 0:
            self._active_index = (self._active_index - 1) % len(self._buffers)
