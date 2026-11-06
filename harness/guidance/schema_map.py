"""Map schema node types to practice fidelity names from ``model/schema.yaml``.

Fidelity names must match ``### {name}`` sections under ``## Fidelities`` in the
practice markdown (``{practice}.md``).
"""

from __future__ import annotations

import re
from pathlib import Path

from harness.guidance.schema import Schema

_FIDELITY_SECTION = re.compile(r"^### ([A-Za-z0-9_-]+)\s*$")


def node_fidelities(schema_text: str) -> dict[str, str]:
    """Return each schema node key mapped to the fidelity that creates it."""
    return Schema(schema_text).fidelities()


def fidelity_sections(practice_markdown: str) -> frozenset[str]:
    """Fidelity entry names declared under ``## Fidelities`` in practice markdown."""
    return frozenset(fidelity_order(practice_markdown))


def fidelity_order(practice_markdown: str) -> list[str]:
    """Fidelity names in the order ``## Fidelities`` declares them, lowest fidelity first."""
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
    return names


def schema_fidelity_path(practice_module_dir: Path) -> Path:
    return practice_module_dir / "model" / "schema.yaml"


def load_node_fidelities(practice_module_dir: Path) -> dict[str, list[str]]:
    """Each schema node key mapped to the fidelity that creates it and every higher fidelity of the practice.

    A node created at a low fidelity also belongs to the higher ones: they build it out rather than replace it.
    """
    path = schema_fidelity_path(practice_module_dir)
    markdown = practice_module_dir / f"{practice_module_dir.name}.md"
    if not path.is_file() or not markdown.is_file():
        return {}
    order = fidelity_order(markdown.read_text(encoding="utf-8"))
    created = Schema.load(path).fidelities()
    return {node: order[order.index(fidelity):] for node, fidelity in created.items() if fidelity in order}


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
