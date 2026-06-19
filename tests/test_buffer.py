from __future__ import annotations

from pathlib import Path

from ced.editor.buffer import Buffer, BufferManager


class TestBuffer:
    def test_buffer_defaults(self) -> None:
        b = Buffer()
        assert b.path is None
        assert b.is_modified is False
        assert b.name == "untitled"
        assert b.directory == ""

    def test_buffer_with_path(self) -> None:
        b = Buffer(Path("/home/user/project/main.py"))
        assert b.name == "main.py"
        assert b.directory == "/home/user/project"

    def test_buffer_mark_modified(self) -> None:
        b = Buffer()
        b.mark_modified()
        assert b.is_modified is True

    def test_buffer_mark_saved(self) -> None:
        b = Buffer()
        b.mark_modified()
        b.mark_saved()
        assert b.is_modified is False

    def test_buffer_repr(self) -> None:
        b = Buffer(Path("f.py"))
        assert repr(b) == "Buffer(f.py, modified=False)"
        b.mark_modified()
        assert repr(b) == "Buffer(f.py, modified=True)"


class TestBufferManager:
    def test_empty_manager(self) -> None:
        bm = BufferManager()
        assert bm.count == 0
        assert bm.active_buffer is None
        assert bm.active_index == -1

    def test_add_buffer(self) -> None:
        bm = BufferManager()
        buf = bm.add(Path("f.py"))
        assert bm.count == 1
        assert bm.active_buffer is buf
        assert bm.active_index == 0

    def test_add_untitled_buffer(self) -> None:
        bm = BufferManager()
        buf = bm.add()
        assert buf.name == "untitled"

    def test_remove_buffer(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.remove(0)
        assert bm.count == 1
        assert bm.active_buffer is not None
        assert bm.active_buffer.name == "b.py"

    def test_remove_last_buffer(self) -> None:
        bm = BufferManager()
        bm.add()
        bm.remove(0)
        assert bm.count == 0
        assert bm.active_buffer is None

    def test_remove_out_of_range(self) -> None:
        bm = BufferManager()
        bm.remove(5)
        assert bm.count == 0

    def test_remove_before_active_decrements_index(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        assert bm.active_index == 2
        bm.remove(0)
        assert bm.count == 2
        assert bm.active_index == 1
        assert bm.active_buffer is not None
        assert bm.active_buffer.name == "c.py"

    def test_remove_after_active_keeps_index(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        bm.active_index = 0
        bm.remove(2)
        assert bm.count == 2
        assert bm.active_index == 0
        assert bm.active_buffer is not None
        assert bm.active_buffer.name == "a.py"

    def test_remove_active_not_last_shifts_next_into_place(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        bm.active_index = 1
        bm.remove(1)
        assert bm.count == 2
        assert bm.active_index == 1
        assert bm.active_buffer is not None
        assert bm.active_buffer.name == "c.py"

    def test_open_new_file(self) -> None:
        bm = BufferManager()
        buf = bm.open(Path("/a/b.py"))
        assert buf.name == "b.py"
        assert bm.count == 1

    def test_open_existing_file(self) -> None:
        bm = BufferManager()
        buf1 = bm.open(Path("/a/b.py"))
        bm.open(Path("/a/c.py"))
        buf2 = bm.open(Path("/a/b.py"))
        assert buf1 is buf2
        assert bm.count == 2, "should not duplicate"
        assert bm.active_index == 0, "should switch to existing"

    def test_get_by_path(self) -> None:
        bm = BufferManager()
        bm.open(Path("/a/b.py"))
        found = bm.get_by_path(Path("/a/b.py"))
        assert found is not None
        assert found.name == "b.py"

    def test_get_by_path_nonexistent(self) -> None:
        bm = BufferManager()
        assert bm.get_by_path(Path("/x.py")) is None

    def test_close_active(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        closed = bm.close_active()
        assert closed is not None
        assert closed.name == "b.py"
        assert bm.count == 1

    def test_close_active_empty(self) -> None:
        bm = BufferManager()
        assert bm.close_active() is None

    def test_switch_next(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.add(Path("c.py"))
        assert bm.active_index == 2
        bm.switch_next()
        assert bm.active_index == 0
        bm.switch_next()
        assert bm.active_index == 1

    def test_switch_prev(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.active_index = 0
        bm.switch_prev()
        assert bm.active_index == 1
        bm.switch_prev()
        assert bm.active_index == 0

    def test_switch_on_empty(self) -> None:
        bm = BufferManager()
        bm.switch_next()
        assert bm.active_buffer is None
        bm.switch_prev()
        assert bm.active_buffer is None

    def test_active_index_setter_valid(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        bm.active_index = 0
        assert bm.active_buffer is not None
        assert bm.active_buffer.name == "a.py"

    def test_active_index_setter_invalid(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.active_index = 10
        assert bm.active_index == 0, "should not change"

    def test_iteration(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        bm.add(Path("b.py"))
        names = [b.name for b in bm]
        assert names == ["a.py", "b.py"]

    def test_getitem(self) -> None:
        bm = BufferManager()
        bm.add(Path("a.py"))
        assert bm[0].name == "a.py"
