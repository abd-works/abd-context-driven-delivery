"""rules.py — rule discovery helpers for the enforce capability."""
from __future__ import annotations

from pathlib import Path


def infer_rule(file: Path, rules_dir: Path) -> str | None:
    """Infer rule name from file path.

    If the file lives inside <rules_dir>/…/rules/<rule-name>/…, return <rule-name>.
    Returns None if no 'rules' segment is found in the relative path.
    """
    try:
        rel = file.resolve().relative_to(rules_dir.resolve())
    except ValueError:
        return None
    parts = rel.parts
    for i, seg in enumerate(parts[:-1]):
        if seg == "rules":
            return parts[i + 1]
    return None
