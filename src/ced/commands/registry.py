from __future__ import annotations
from typing import Callable, Any
from dataclasses import dataclass
import difflib


@dataclass
class Command:
    """A registered command with id, description, handler, and category.

    The handler can accept arbitrary positional and keyword arguments
    passed through from :meth:`CommandRegistry.execute`.
    """

    id: str
    description: str
    handler: Callable[..., None]
    category: str = "General"


class CommandRegistry:
    """Registry for commands that can be looked up and executed by id.

    Supports fuzzy search via difflib.SequenceMatcher.
    """

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

    def execute(self, id: str, *args: Any, **kwargs: Any) -> None:
        """Execute the command with *id* passing *args* and **kwargs to its handler."""
        if id not in self._commands:
            raise KeyError(f"Unknown command: {id}")
        self._commands[id].handler(*args, **kwargs)

    def get(self, id: str) -> Command | None:
        """Return the command for *id*, or None."""
        return self._commands.get(id)

    def all(self) -> list[Command]:
        """Return all registered commands."""
        return list(self._commands.values())

    def search(self, query: str) -> list[tuple[Command, float]]:
        """Fuzzy-search commands by id or description using difflib.

        Returns (Command, score) tuples sorted by descending score,
        filtering out results below 0.3 similarity.
        """
        query = query.lower()
        results: list[tuple[Command, float]] = []
        for cmd in self._commands.values():
            score = max(
                difflib.SequenceMatcher(None, query, cmd.id.lower()).ratio(),
                difflib.SequenceMatcher(
                    None, query, cmd.description.lower()
                ).ratio(),
            )
            if score > 0.3:
                results.append((cmd, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results
