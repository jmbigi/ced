from __future__ import annotations

from ced.commands.registry import Command, CommandRegistry


class TestCommand:
    def test_command_creation(self) -> None:
        def handler() -> None:
            pass

        cmd = Command("app.test", "Test command", handler, "Testing")
        assert cmd.id == "app.test"
        assert cmd.description == "Test command"
        assert cmd.handler is handler
        assert cmd.category == "Testing"


class TestCommandRegistry:
    def test_empty_registry(self) -> None:
        reg = CommandRegistry()
        assert reg.all() == []
        assert reg.get("nonexistent") is None

    def test_register(self) -> None:
        reg = CommandRegistry()
        cmd = Command("test.cmd", "Test", lambda: None, "Test")
        reg.register(cmd)
        assert reg.get("test.cmd") is cmd
        assert len(reg.all()) == 1

    def test_register_duplicate_raises(self) -> None:
        reg = CommandRegistry()
        cmd = Command("test.cmd", "Test", lambda: None)
        reg.register(cmd)
        try:
            reg.register(Command("test.cmd", "Duplicate", lambda: None))
            assert False, "should have raised ValueError"
        except ValueError:
            pass

    def test_register_many(self) -> None:
        reg = CommandRegistry()
        reg.register_many(
            Command("a", "A", lambda: None),
            Command("b", "B", lambda: None),
        )
        assert len(reg.all()) == 2

    def test_execute(self) -> None:
        results: list[str] = []

        def handler() -> None:
            results.append("executed")

        reg = CommandRegistry()
        reg.register(Command("test.exec", "Exec", handler))
        reg.execute("test.exec")
        assert results == ["executed"]

    def test_execute_with_args(self) -> None:
        results: list[str] = []

        def handler(msg: str) -> None:
            results.append(msg)

        reg = CommandRegistry()
        reg.register(Command("test.exec", "Exec", handler))
        reg.execute("test.exec", "hello")
        assert results == ["hello"]

    def test_execute_unknown_raises(self) -> None:
        reg = CommandRegistry()
        try:
            reg.execute("unknown")
            assert False, "should have raised KeyError"
        except KeyError:
            pass

    def test_search_by_id(self) -> None:
        reg = CommandRegistry()
        reg.register(Command("app.save", "Save file", lambda: None, "File"))
        results = reg.search("save")
        assert len(results) >= 1
        cmd, score = results[0]
        assert cmd.id == "app.save"
        assert score > 0.3

    def test_search_by_description(self) -> None:
        reg = CommandRegistry()
        reg.register(Command("app.test", "Find this command", lambda: None))
        results = reg.search("find this")
        assert len(results) >= 1
        assert results[0][0].id == "app.test"

    def test_search_no_match(self) -> None:
        reg = CommandRegistry()
        reg.register(Command("app.save", "Save", lambda: None))
        results = reg.search("zzzzzzz")
        assert results == []

    def test_search_sorted_by_score(self) -> None:
        reg = CommandRegistry()
        reg.register(Command("app.quit", "Quit", lambda: None))
        reg.register(Command("app.save", "Save", lambda: None))
        results = reg.search("save")
        assert results[0][0].id == "app.save"

    def test_undo_redo_commands_registered(self) -> None:
        reg = CommandRegistry()
        undo_called = False
        redo_called = False

        def do_undo() -> None:
            nonlocal undo_called
            undo_called = True

        def do_redo() -> None:
            nonlocal redo_called
            redo_called = True

        reg.register(Command("app.undo", "Undo last change", do_undo, "Edit"))
        reg.register(Command("app.redo", "Redo last undone change", do_redo, "Edit"))

        reg.execute("app.undo")
        assert undo_called is True
        reg.execute("app.redo")
        assert redo_called is True
