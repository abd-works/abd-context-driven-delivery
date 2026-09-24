"""Fenced-YAML helpers for serializing in-process spec invoke responses."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


class YamlFence:
    """Fence, unfence, and dump YAML mappings for spec invoke responses."""

    def __init__(self, lang: str = "yaml") -> None:
        self._lang = lang

    def unfence(self, text: str) -> str:
        lines = text.strip().splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)

    def fenced(self, body: str) -> str:
        return f"```{self._lang}\n{body.rstrip()}\n```"

    def load_fenced(self, text: str) -> Any:
        if yaml is None:
            raise RuntimeError("PyYAML required to parse YAML")
        return yaml.safe_load(self.unfence(text))

    def serialize_value(self, raw_value: Any) -> Any:
        if isinstance(raw_value, Path):
            return str(raw_value)
        if isinstance(raw_value, dict):
            return {key: self.serialize_value(nested) for key, nested in raw_value.items()}
        if isinstance(raw_value, list):
            return [self.serialize_value(element) for element in raw_value]
        return raw_value

    def dump_manifest(self, manifest_data: dict[str, Any]) -> str:
        if yaml is None:
            raise RuntimeError("PyYAML required to render YAML")
        return yaml.safe_dump(
            self.serialize_value(manifest_data),
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        ).strip()


def load_fenced(text: str) -> Any:
    return YamlFence().load_fenced(text)
