import json
from pathlib import Path


class PromptQueue:
    """The prompts a person queued for later, kept in one file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def prompts(self) -> list[str]:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def add(self, prompt: str) -> list[str]:
        queued = [*self.prompts(), prompt]
        self._path.write_text(json.dumps(queued), encoding="utf-8")
        return queued
