"""Project ``.context/config.json`` — read/write guidelines and practice folders."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

CONFIG_NAME = "config.json"
_LEGACY_GUIDELINES = "guidelines.config"
_LEGACY_PRACTICE_FOLDERS = "practice-folders.config"


class ContextConfig:
    """One project's ``.context/config.json``."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    @property
    def path(self) -> Path:
        return self.root / ".context" / CONFIG_NAME

    def exists(self) -> bool:
        folder = self.root / ".context"
        return (
            self.path.is_file()
            or (folder / _LEGACY_GUIDELINES).is_file()
            or (folder / _LEGACY_PRACTICE_FOLDERS).is_file()
        )

    def load(self) -> dict[str, Any]:
        if self.path.is_file():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return {}
            return data if isinstance(data, dict) else {}
        return {
            "guidelines": _parse_text_map(
                _read_text(self.root / ".context" / _LEGACY_GUIDELINES)
            ),
            "practice_folders": _parse_text_map(
                _read_text(self.root / ".context" / _LEGACY_PRACTICE_FOLDERS)
            ),
        }

    def save(self, data: Mapping[str, Any]) -> Path:
        folder = self.path.parent
        folder.mkdir(parents=True, exist_ok=True)
        payload = dict(data)
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return self.path

    def update(self, **sections: Any) -> dict[str, Any]:
        data = self.load()
        for key, value in sections.items():
            if value is None:
                data.pop(key, None)
            elif isinstance(value, Mapping) and isinstance(data.get(key), dict):
                merged = dict(data[key])
                merged.update(value)
                data[key] = merged
            else:
                data[key] = value
        self.save(data)
        return data

    def guidelines(self) -> dict[str, str]:
        return _string_map(self.load().get("guidelines"))

    def practice_folders(self) -> dict[str, str]:
        return _string_map(self.load().get("practice_folders"))

    def guideline(self, pattern: str) -> str:
        wanted = pattern.replace("-", "_").casefold()
        for key, value in self.guidelines().items():
            if key.replace("-", "_").casefold() == wanted:
                return value.casefold()
        return ""

    def practice_folder(self, practice: str) -> str | None:
        wanted = practice.replace("-", "_").casefold()
        for key, value in self.practice_folders().items():
            if key.replace("-", "_").casefold() == wanted:
                return value
        return None

    def set_guidelines(self, guidelines: Mapping[str, str] | str) -> dict[str, Any]:
        mapping = (
            _parse_text_map(guidelines)
            if isinstance(guidelines, str)
            else {str(k).strip(): str(v).strip() for k, v in guidelines.items()}
        )
        return self.update(guidelines=mapping)

    def set_practice_folders(self, folders: Mapping[str, str] | str) -> dict[str, Any]:
        mapping = (
            _parse_text_map(folders)
            if isinstance(folders, str)
            else {str(k).strip(): str(v).strip() for k, v in folders.items()}
        )
        return self.update(practice_folders=mapping)


def context_config_path(root: Path | str) -> Path:
    return ContextConfig(root).path


def has_context_config(root: Path | str) -> bool:
    return ContextConfig(root).exists()


def load_context_config(root: Path | str) -> dict[str, Any]:
    return ContextConfig(root).load()


def save_context_config(root: Path | str, data: Mapping[str, Any]) -> Path:
    return ContextConfig(root).save(data)


def guideline_value(root: Path | str, pattern: str) -> str:
    return ContextConfig(root).guideline(pattern)


def practice_folders(root: Path | str) -> dict[str, str]:
    return ContextConfig(root).practice_folders()


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_text_map(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.split("#", 1)[0].strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        name = key.strip()
        item = value.strip()
        if name and item:
            found[name] = item
    return found


def _string_map(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {
        str(key).strip(): str(item).strip()
        for key, item in value.items()
        if str(key).strip() and str(item).strip()
    }
