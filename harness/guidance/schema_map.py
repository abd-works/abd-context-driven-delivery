"""Map schema node types to practice fidelity names from ``model/schema.yaml``.

Fidelity names must match ``### {name}`` sections under ``## Fidelities`` in the
practice markdown (``{practice}.md``).
"""

from __future__ import annotations

import re
from pathlib import Path

_NODE_HEADER = re.compile(r"^([A-Za-z]\w*):\s*$")
_FIDELITY_PROP = re.compile(r"^  fidelity:\s*([A-Za-z0-9_-]+)\s*$")
_FIDELITY_LIST = re.compile(r"^\s+- fidelity:\s*([A-Za-z0-9_-]+)\s*$")
_FIDELITY_SECTION = re.compile(r"^### ([A-Za-z0-9_-]+)\s*$")


def node_fidelities(schema_text: str) -> dict[str, str]:
    """Return each schema node key mapped to its ``fidelity`` value."""
    mapping: dict[str, str] = {}
    current: str | None = None
    for line in schema_text.splitlines():
        header = _NODE_HEADER.match(line)
        if header:
            current = header.group(1)
            continue
        if current is None:
            continue
        prop = _FIDELITY_PROP.match(line) or _FIDELITY_LIST.match(line)
        if prop:
            mapping[current] = prop.group(1)
            current = None
    return mapping


def fidelity_sections(practice_markdown: str) -> frozenset[str]:
    """Fidelity entry names declared under ``## Fidelities`` in practice markdown."""
    names: list[str] = []
    in_fidelities = False
    for line in practice_markdown.splitlines():
        stripped = line.strip()
        if stripped == "## Fidelities":
            in_fidelities = True
            continue
        if in_fidelities and line.startswith("## ") and not line.startswith("### "):
            break
        if in_fidelities:
            match = _FIDELITY_SECTION.match(line)
            if match:
                names.append(match.group(1))
    return frozenset(names)


def schema_fidelity_path(practice_module_dir: Path) -> Path:
    return practice_module_dir / "model" / "schema.yaml"


def load_node_fidelities(practice_module_dir: Path) -> dict[str, str]:
    path = schema_fidelity_path(practice_module_dir)
    if not path.is_file():
        return {}
    return node_fidelities(path.read_text(encoding="utf-8"))


def fidelity_for_node(schema_text: str, node_key: str) -> str | None:
    return node_fidelities(schema_text).get(node_key)


def validate_schema_fidelities(
    schema_text: str, practice_markdown: str
) -> list[str]:
    """Errors when a node fidelity is missing or not declared in practice markdown."""
    errors: list[str] = []
    declared = fidelity_sections(practice_markdown)
    mapping = node_fidelities(schema_text)
    if not mapping:
        errors.append("schema defines no node fidelity entries")
        return errors
    for node, fidelity in sorted(mapping.items()):
        if fidelity not in declared:
            errors.append(
                f"{node} maps to fidelity {fidelity!r}, "
                f"which is not under ## Fidelities (have {sorted(declared)!r})"
            )
    return errors
