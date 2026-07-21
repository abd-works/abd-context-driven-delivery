"""Local fenced-YAML helpers for parsing ``python -m tools run`` CLI output.

Owned by agent_bdd — not part of the Tools author seam. Tools authors get
manifest text via ``front_matter`` or the CLI; harnesses parse CLI envelopes here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


def unfence(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def fenced(body: str, *, lang: str = "yaml") -> str:
    return f"```{lang}\n{body.rstrip()}\n```"


def load_fenced(text: str) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML required to parse YAML")
    return yaml.safe_load(unfence(text))


def _serialize_value(raw_value: Any) -> Any:
    if isinstance(raw_value, Path):
        return str(raw_value)
    if isinstance(raw_value, dict):
        return {key: _serialize_value(nested) for key, nested in raw_value.items()}
    if isinstance(raw_value, list):
        return [_serialize_value(element) for element in raw_value]
    return raw_value


def dump_manifest(manifest_data: dict[str, Any]) -> str:
    if yaml is None:
        raise RuntimeError("PyYAML required to render YAML")
    return yaml.safe_dump(
        _serialize_value(manifest_data),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    ).strip()
