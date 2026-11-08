"""Project ``.context/config.json`` — read/write guidelines and practice folders."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

CONTEXT_FOLDER = ".context"
CONFIG_NAME = "config.json"


class MalformedContextConfigError(ValueError):
    """Raised when ``.context/config.json`` cannot be read as a JSON object. Nothing is written over it, so the
    project's guidelines and practice folders stay in the file until someone repairs it."""

    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        super().__init__(f"{path} is not a readable JSON object ({reason}); repair it before CDD changes it")


class ContextConfig:
    """One project's ``.context/config.json``: the guidelines that apply to it, each ``enabled`` or ``disabled``, and
    the folder each practice writes in. Names are matched without regard to case or to ``-`` against ``_``, so
    ``mern-domain-driven`` and ``mern_domain_driven`` name one guideline."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    @property
    def path(self) -> Path:
        return self.root / CONTEXT_FOLDER / CONFIG_NAME

    def exists(self) -> bool:
        return self.path.is_file()

    def load(self) -> dict[str, Any]:
        """The whole configuration; empty when the project has none. Raises ``MalformedContextConfigError`` when
        ``config.json`` is unreadable, so ``update`` never saves a partial configuration over the project's file."""
        if not self.path.is_file():
            return {}
        try:
            configuration = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MalformedContextConfigError(self.path, str(exc)) from exc
        if not isinstance(configuration, dict):
            raise MalformedContextConfigError(self.path, f"the top level is a {type(configuration).__name__}")
        return configuration

    def save(self, configuration: Mapping[str, Any]) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(dict(configuration), indent=2) + "\n", encoding="utf-8")
        return self.path

    def update(self, **sections: Any) -> dict[str, Any]:
        configuration = self.load()
        for key, value in sections.items():
            if value is None:
                configuration.pop(key, None)
            elif isinstance(value, Mapping) and isinstance(configuration.get(key), dict):
                configuration[key] = {**configuration[key], **value}
            else:
                configuration[key] = value
        self.save(configuration)
        return configuration

    def guideline(self, pattern: str) -> str:
        """Whether the guideline named pattern is ``enabled`` or ``disabled``; empty when the project names none."""
        return (self._value_named("guidelines", pattern) or "").casefold()

    def practice_folder(self, practice: str) -> str | None:
        return self._value_named("practice_folders", practice)

    def _value_named(self, section: str, name: str) -> str | None:
        wanted = self._match_key(name)
        return next((value for key, value in self._names_to_values(section).items() if self._match_key(key) == wanted), None)

    def _match_key(self, name: str) -> str:
        return name.replace("-", "_").casefold()

    def _names_to_values(self, section: str) -> dict[str, str]:
        value = self.load().get(section)
        if not isinstance(value, Mapping):
            return {}
        found = ((str(name).strip(), str(given).strip()) for name, given in value.items())
        return {name: given for name, given in found if name and given}
