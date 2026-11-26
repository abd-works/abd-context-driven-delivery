import json
from pathlib import Path


class UnreadablePromptQueue(ValueError):
    """The queue's file holds something that is not a list of prompts."""

    def __init__(self, path: Path, reason: str) -> None:
        super().__init__(f"The prompt queue at {path} cannot be read: {reason}. It is left as it is.")
        self.path = path


class PromptQueue:
    """The prompts a person queued for later, kept in one file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def prompts(self) -> list[str]:
        if not self._path.exists():
            return []
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as unreadable:
            raise UnreadablePromptQueue(self._path, str(unreadable)) from unreadable

    def add(self, prompt: str) -> list[str]:
        queued = [*self.prompts(), prompt]
        self._path.write_text(json.dumps(queued), encoding="utf-8")
        return queued
