"""Load custom project rulesets from a working folder."""
from __future__ import annotations

import os
from pathlib import Path

_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".codeql",
    "__pycache__",
    "dist",
    ".venv",
    "venv",
}
_INDEX: dict[str, dict[str, list[Path]]] = {}


def load_project_rules(root, practice, fidelities) -> list:
    """Rules tagged project, including fidelity folders under the practice ruleset."""
    from harness.guidance.rule import RulesCollection
    from harness.knowledge_graph.model.graph_rules import GraphRule

    folder = _folder(root)
    practice_name = str(practice or "").strip()
    if folder is None or not practice_name:
        return []
    loaded: list = []
    seen: set[Path] = set()
    names = [str(name) for name in (fidelities or [])]
    for rules_dir in _indexed_rules(folder).get(practice_name, []):
        loaded.extend(
            _rules_from(
                rules_dir / "rules.md",
                practice_name,
                None,
                seen,
                RulesCollection,
                GraphRule,
            )
        )
        for fidelity in names:
            for child_name in _fidelity_folders(fidelity):
                loaded.extend(
                    _rules_from(
                        rules_dir / child_name / "rules.md",
                        practice_name,
                        fidelity,
                        seen,
                        RulesCollection,
                        GraphRule,
                    )
                )
    return loaded


def _folder(root) -> Path | None:
    if root is None:
        return None
    text = str(root).strip()
    if not text or text == ".":
        return None
    folder = Path(text)
    if not folder.is_dir():
        return None
    return folder


def _indexed_rules(root: Path) -> dict[str, list[Path]]:
    key = str(root.resolve())
    cached = _INDEX.get(key)
    if cached is not None:
        return cached
    found: dict[str, list[Path]] = {}

    def consider(folder: Path) -> None:
        rules_root = folder / ".context" / "rules"
        if not rules_root.is_dir():
            return
        for child in rules_root.iterdir():
            if child.is_dir():
                found.setdefault(child.name, []).append(child)

    consider(root)
    for dirpath, dirnames, _filenames in os.walk(root, onerror=lambda _error: None):
        current = Path(dirpath)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in _SKIP_DIRS and name != ".context"
        ]
        if current == root:
            continue
        consider(current)
    _INDEX[key] = found
    return found


def _fidelity_folders(fidelity: str) -> list[str]:
    names: list[str] = []
    for candidate in (
        fidelity,
        fidelity.replace("_", "-"),
        fidelity.replace("-", "_"),
    ):
        if candidate and candidate not in names:
            names.append(candidate)
    return names


def _rules_from(path: Path, practice: str, fidelity: str | None, seen: set[Path], collection_type, graph_rule):
    if not path.is_file():
        return []
    resolved = path.resolve()
    if resolved in seen:
        return []
    seen.add(resolved)
    text = path.read_text(encoding="utf-8")
    collection = collection_type.from_markdown(text, fidelity=fidelity)
    codeql = path.parent / "codeql"
    shared = fidelity is None
    return [
        graph_rule(
            rule,
            practice=practice,
            shared=shared,
            tag="project",
            query_pack=codeql,
        )
        for rule in collection
    ]
