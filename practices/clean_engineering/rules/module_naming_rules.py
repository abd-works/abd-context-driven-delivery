"""Module naming and shape rules backed by folder + module-context scans."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule

_VERB_MODULE = re.compile(
    r"(^|/)(manage|process|handle|run|execute|build|create|update|delete|get|set)[-_]",
    re.I,
)
_BAD_SUFFIX = re.compile(r"(Model|Runtime|Service|Manager|Helper|Util|Utils|Processor)$")
_IS_A = re.compile(r"\*is a type of\*", re.I)
_CHILD_PARENT = re.compile(r"^\s*#{1,6}\s+\S.+\s+:\s+\S", re.MULTILINE)


class DomainNounsOnly(PracticeGraphRule):
    slug = "domain-nouns-only"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        name = (node.name or "").strip()
        if not name:
            return []
        if _VERB_MODULE.search(name.replace(".", "/")):
            return [f"Module {name!r} reads like an action verb path, not a domain noun."]
        leaf = name.split(".")[-1]
        if _BAD_SUFFIX.search(leaf):
            return [f"Module {name!r} uses technical suffix {leaf!r}; use a domain noun."]
        return []


class NoModulePerClass(PracticeGraphRule):
    slug = "no-module-per-class"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        folder = context.module_folder(node)
        if folder is None or not folder.is_dir():
            return []
        hits: list[str] = []
        hits.extend(_context_subtype_violations(folder, node.name))
        class_count = _count_top_level_classes(folder)
        if class_count == 1:
            py_files = [p for p in folder.glob("*.py") if not p.name.startswith("_")]
            if len(py_files) <= 1:
                hits.append(
                    f"Module {node.name!r} exposes a single class in one file; "
                    "group cohesive classes or merge into an existing module."
                )
        return hits[:1]


def _context_subtype_violations(folder: Path, module_name: str) -> list[str]:
    marker = folder / ".context" / "module-context.md"
    if not marker.is_file():
        return []
    try:
        content = marker.read_text(encoding="utf-8")
    except OSError:
        return []
    if _IS_A.search(content):
        return [
            f"Module {module_name!r} module-context uses '*is a type of*'; "
            "generalisation belongs in model, not modules fidelity."
        ]
    if _CHILD_PARENT.search(content):
        return [
            f"Module {module_name!r} module-context uses 'Child : Parent'; "
            "use model fidelity for generalisation."
        ]
    return []


def _count_top_level_classes(folder: Path) -> int:
    total = 0
    for path in folder.glob("*.py"):
        if path.name.startswith("_") or path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        total += sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    return total
