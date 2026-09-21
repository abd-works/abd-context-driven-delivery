"""Load guidance rules from practice markdown — no practice class bootstrap."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

from .graph_rules import GraphRule, FIDELITY_NODE_SCOPE, GRAPH_EVALUATED_RULES, _all_types_for_practice

_REPO = Path(__file__).resolve().parents[3]

PRACTICE_MARKDOWN: dict[str, Path] = {
    "stories": _REPO / "practices/stories/stories.md",
    "clean_engineering": _REPO / "practices/clean_engineering/clean_engineering.md",
    "ddd": _REPO / "practices/ddd/ddd.md",
    "bdd": _REPO / "practices/bdd/bdd.md",
}

_RULE_BULLET = re.compile(
    r"^-\s+\*\*`([^`]+)`\*\*\s*[—:-]\s*(.+)$",
)


def load_graph_rules_from_markdown() -> List[GraphRule]:
    rules: List[GraphRule] = []
    for practice, path in PRACTICE_MARKDOWN.items():
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        shared_section = _section(text, "## Shared rules", "## Fidelities")
        if shared_section:
            rules.extend(_parse_section(shared_section, practice=practice, fidelity=None, shared=True))
        for fidelity, body in _fidelity_sections(text):
            rule_section = _section(body, "#### Rules", "#### ", stop_at_same_level=True)
            if rule_section:
                rules.extend(
                    _parse_section(rule_section, practice=practice, fidelity=fidelity, shared=False)
                )
    return rules


def _parse_section(
    section: str,
    *,
    practice: str,
    fidelity: Optional[str],
    shared: bool,
) -> List[GraphRule]:
    scopes = FIDELITY_NODE_SCOPE.get(practice, {})
    applies = set(scopes.get(fidelity or "", set()))
    if shared:
        applies = _all_types_for_practice(practice)
    out: List[GraphRule] = []
    for line in section.splitlines():
        m = _RULE_BULLET.match(line.strip())
        if not m:
            continue
        slug, body = m.group(1).strip(), m.group(2).strip()
        out.append(
            GraphRule(
                slug=slug,
                body=body,
                practice=practice,
                fidelity=fidelity,
                shared=shared,
                applies_to=applies,
                inherits_to_children=shared,
                graph_evaluated=slug in GRAPH_EVALUATED_RULES,
            )
        )
    return out


def _section(
    text: str,
    start_heading: str,
    end_heading: str,
    *,
    stop_at_same_level: bool = False,
) -> str:
    start = text.find(start_heading)
    if start < 0:
        return ""
    start = text.find("\n", start)
    if start < 0:
        return ""
    rest = text[start + 1 :]
    end = len(rest)
    level = start_heading.count("#")
    for line in rest.splitlines():
        if not line.startswith("#"):
            continue
        line_level = len(line) - len(line.lstrip("#"))
        if stop_at_same_level and line_level <= level and line.strip().startswith(end_heading.strip("#").split()[0] if "#" in end_heading else end_heading):
            break
        if line.strip().startswith(end_heading):
            end = rest.find(line)
            break
    return rest[:end].strip()


def _fidelity_sections(text: str) -> List[Tuple[str, str]]:
    parts: List[Tuple[str, str]] = []
    in_fidelities = False
    current_name = ""
    current_lines: List[str] = []
    for line in text.splitlines():
        if line.strip() == "## Fidelities":
            in_fidelities = True
            continue
        if in_fidelities and line.startswith("## ") and not line.startswith("### "):
            break
        if in_fidelities and line.startswith("### "):
            if current_name:
                parts.append((current_name, "\n".join(current_lines)))
            current_name = line.replace("###", "").strip()
            current_lines = []
            continue
        if in_fidelities and current_name:
            current_lines.append(line)
    if current_name:
        parts.append((current_name, "\n".join(current_lines)))
    return parts
