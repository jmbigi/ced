from __future__ import annotations
from typing import Callable, Any
from dataclasses import dataclass
import difflib


@dataclass
class Command:
    id: str
    description: str
    handler: Callable[..., None]
    category: str = "General"


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        if command.id in self._commands:
            raise ValueError(f"Command {command.id!r} already registered")
        self._commands[command.id] = command

    def register_many(self, *commands: Command) -> None:
        for cmd in commands:
            self.register(cmd)

    def execute(self, id: str, *args: Any, **kwargs: Any) -> None:
        if id not in self._commands:
            raise KeyError(f"Unknown command: {id}")
        self._commands[id].handler(*args, **kwargs)

    def get(self, id: str) -> Command | None:
        return self._commands.get(id)

    def all(self) -> list[Command]:
        return list(self._commands.values())

    def search(self, query: str) -> list[tuple[Command, float]]:
        query = query.lower()
        results: list[tuple[Command, float]] = []
        for cmd in self._commands.values():
            score = max(
                difflib.SequenceMatcher(None, query, cmd.id.lower()).ratio(),
                difflib.SequenceMatcher(None, query, cmd.description.lower()).ratio(),
            )
            if score > 0.3:
                results.append((cmd, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results
