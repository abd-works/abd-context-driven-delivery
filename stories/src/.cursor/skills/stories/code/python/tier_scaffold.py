"""Python tier scaffolder — ONE write-once file per (story, tier).

For each Story with attached scenarios, emits a single file per declared tier:

    test_<story_slug>_<tier>.py    — imports the spec constant, defines the
                                     TierImpl class, and invokes
                                     `run_scenario(...)` for every scenario

The `test_` prefix keeps pytest auto-discovery working. Class + wiring live
together — no second `<story_slug>_<tier>.py` companion file.

Write-once: caller passes an `existing_tree` set and this module filters out
any path already present so hand-authored bodies never get clobbered.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Sequence

from stories.src.stories.code.code_story_map import to_kebab
from stories.src.stories.model.nodes import Epic, Story, SubEpic
from stories.src.stories.model.story_map import StoryMap


def scaffold_py_tier_tree(
    story_map: StoryMap,
    tiers: Sequence[str],
    *,
    tests_root: str = "tests",
    existing_tree: Dict[str, str] | None = None,
) -> Dict[str, str]:
    existing = existing_tree or {}
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    for epic in getattr(story_map, "epics", []) or []:
        _scaffold_epic(epic, tiers=tiers, root=root, tree=tree, existing=existing)

    return {path: body for path, body in tree.items() if path not in existing}


def _scaffold_epic(
    epic: Epic, *, tiers: Sequence[str], root: str,
    tree: Dict[str, str], existing: Dict[str, str],
) -> None:
    epic_slug = to_kebab(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _scaffold_sub_epic(
            sub, tiers=tiers, parent=f"{root}/{epic_slug}",
            tree=tree, existing=existing,
        )


def _scaffold_sub_epic(
    sub: SubEpic, *, tiers: Sequence[str], parent: str,
    tree: Dict[str, str], existing: Dict[str, str],
) -> None:
    sub_slug = to_kebab(sub.name)
    folder = f"{parent}/{sub_slug}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub_epic(
            nested, tiers=tiers, parent=folder, tree=tree, existing=existing,
        )
    for story in getattr(sub, "stories", []) or []:
        _scaffold_story(
            story, tiers=tiers, parent=folder, tree=tree, existing=existing,
        )


def _scaffold_story(
    story: Story, *, tiers: Sequence[str], parent: str,
    tree: Dict[str, str], existing: Dict[str, str],
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug_kebab = to_kebab(story.name)
    story_slug_snake = story_slug_kebab.replace("-", "_")
    story_folder = f"{parent}/{story_slug_kebab}"
    for tier in tiers:
        tree[f"{story_folder}/test_{story_slug_snake}_{tier}.py"] = _render_tier_file(
            story, tier=tier,
        )


def _render_tier_file(story: Story, *, tier: str) -> str:
    """One file per (story, tier): TierImpl class + `run_scenario(...)` wiring.

    `test_` prefix keeps pytest discovery working; the class is defined in the
    same module and referenced directly by the wiring lines at the bottom.
    """
    story_slug_snake = to_kebab(story.name).replace("-", "_")
    class_name = f"{_pascal(story.name)}{_pascal(tier)}"
    constant = _screaming_snake(story.name)

    scenarios = list(getattr(story, "scenarios", []) or [])
    given_clauses: List[str] = []
    when_clauses: List[str] = []
    then_clauses: List[str] = []
    for scenario in scenarios:
        given_clauses.extend(c.text for c in scenario.given)
        for interaction in scenario.interactions:
            when_clauses.extend(c.text for c in interaction.when)
            then_clauses.extend(c.text for c in interaction.then)

    given_clauses = _dedupe_ordered(given_clauses)
    when_clauses = _dedupe_ordered(when_clauses)
    then_clauses = _dedupe_ordered(then_clauses)

    lines: List[str] = []
    lines.append(f'"""{tier.capitalize()}-tier runner for {story.name}."""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from typing import Any, Dict")
    lines.append("")
    lines.append(f"from {story_slug_snake}_stories import {constant}")
    lines.append("from story_runner import run_scenario")
    lines.append("")
    lines.append("")
    lines.append(f"class {class_name}:")
    lines.append(
        f'    """{tier.capitalize()}-tier TierImpl for {story.name}. '
        f'Write-once — the pipeline scaffolds keys; you own the bodies."""'
    )
    lines.append("")
    lines.append("    def __init__(self) -> None:")
    lines.append("        self._state: Dict[str, Any] = {}")
    lines.append("")
    lines.append("        self.given: Dict[str, Any] = {")
    for clause in given_clauses:
        lines.append(f"            {_py_string(clause)}: self._given_{_slug(clause)},")
    lines.append("        }")
    lines.append("")
    lines.append("        self.when: Dict[str, Any] = {")
    for clause in when_clauses:
        lines.append(f"            {_py_string(clause)}: self._when_{_slug(clause)},")
    lines.append("        }")
    lines.append("")
    lines.append("        self.then: Dict[str, Any] = {")
    for clause in then_clauses:
        lines.append(f"            {_py_string(clause)}: self._then_{_slug(clause)},")
    lines.append("        }")
    lines.append("")

    for clause in given_clauses:
        lines.append(f"    def _given_{_slug(clause)}(self) -> None:")
        lines.append(f"        \"\"\"{tier}-tier setup: {_short(clause)}\"\"\"")
        lines.append("        raise NotImplementedError")
        lines.append("")

    for clause in when_clauses:
        lines.append(f"    def _when_{_slug(clause)}(self) -> None:")
        lines.append(f"        \"\"\"{tier}-tier action: {_short(clause)}\"\"\"")
        lines.append("        raise NotImplementedError")
        lines.append("")

    for clause in then_clauses:
        lines.append(f"    def _then_{_slug(clause)}(self) -> None:")
        lines.append(f"        \"\"\"{tier}-tier assertion: {_short(clause)}\"\"\"")
        lines.append("        raise NotImplementedError")
        lines.append("")

    lines.append("    def cleanup(self) -> None:")
    lines.append("        self._state.clear()")
    lines.append("")
    lines.append("")
    for scenario in scenarios:
        key = _snake(scenario.name)
        lines.append(
            f"run_scenario({constant}[\"story\"], {constant}[\"{key}\"], "
            f"lambda: {class_name}())"
        )
    lines.append("")
    return "\n".join(lines)


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _py_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _dedupe_ordered(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _short(text: str, limit: int = 70) -> str:
    stripped = re.sub(r"\s+", " ", text).strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 1] + "\u2026"


def _slug(text: str) -> str:
    cleaned = _strip_md_emphasis(text)
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", cleaned) if w]
    return "_".join(p.lower() for p in parts)[:80] or "step"


def _snake(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "_".join(p.lower() for p in parts) or "scenario"


def _screaming_snake(name: str) -> str:
    return _snake(name).upper() or "STORY"


def _pascal(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "".join(w[:1].upper() + w[1:].lower() for w in parts) or "Story"
