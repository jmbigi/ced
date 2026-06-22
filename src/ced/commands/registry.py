from __future__ import annotations

from typing import Callable


class Command:
    """A registered command with id, description, handler, and category."""

    def __init__(
        self,
        id: str,
        description: str,
        handler: Callable[[], None],
        category: str = "App",
    ) -> None:
        self.id = id
        self.description = description
        self.handler = handler
        self.category = category


class CommandRegistry:
    """Registry for commands that can be looked up and executed by id."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a new command. Raises ValueError if id already exists."""
        if command.id in self._commands:
            raise ValueError(f"Command {command.id!r} already registered")
        self._commands[command.id] = command

    def register_many(self, *commands: Command) -> None:
        """Register multiple commands at once."""
        for cmd in commands:
            self.register(cmd)

    def execute(self, id: str) -> None:
        """Execute the command with *id*. Raises KeyError if not found."""
        cmd = self._commands.get(id)
        if cmd is None:
            raise KeyError(f"Unknown command: {id}")
        cmd.handler()

    def get(self, id: str) -> Command | None:
        """Return the command for *id*, or None."""
        return self._commands.get(id)

    def all(self) -> list[Command]:
        """Return all registered commands."""
        return list(self._commands.values())

    def search(self, query: str) -> list[Command]:
        """Fuzzy-search commands by id, description, or category."""
        q = query.lower()
        return [
            cmd
            for cmd in self._commands.values()
            if q in cmd.id.lower()
            or q in cmd.description.lower()
            or q in cmd.category.lower()
        ]
