"""TypeScript tier scaffolder — emits ONE write-once file per (story, tier).

For each Story with attached scenarios, emits a single file per declared tier:

    <story-slug>-<tier>.test.ts   — imports the spec constant, defines the
                                    tier class implementing TierImpl<S>, and
                                    invokes `runScenario(...)` for every
                                    scenario under this story

The `.test.ts` suffix keeps test-runner auto-discovery working (vitest/jest
glob `**/*.test.ts`) while collapsing what used to be a class file + a wiring
file into a single unit. Cross-tier reuse imports the class from this file
directly — no lower-tier stub file needed.

WRITE-ONCE POLICY. This module produces files ONLY when the target path is
absent from `existing_tree`. Once a tier file exists, the pipeline hands
ownership to the human/AI — subsequent runs never modify it. If the story
gains a new step, TypeScript's `TierImpl<S>` mapped type flags the tier
class at compile time; the human reconciles.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Sequence

from stories.src.stories.code.code_story_map import to_kebab
from stories.src.stories.model.nodes import Epic, Story, SubEpic
from stories.src.stories.model.story_map import StoryMap


def scaffold_ts_tier_tree(
    story_map: StoryMap,
    tiers: Sequence[str],
    *,
    tests_root: str = "tests",
    existing_tree: Dict[str, str] | None = None,
    tier_extensions: Dict[str, str] | None = None,
) -> Dict[str, str]:
    """Return `{path: content}` for every tier file that should exist.

    - `tier_extensions` maps a tier slug to its file extension (without the
      dot). Defaults to `"ts"` for every tier. Pass `{"client": "tsx"}` when
      the client tier renders React so scaffolded files land with the correct
      extension for JSX support.
    - `existing_tree`: any path already present is filtered out so the caller
      can safely merge without clobbering hand-authored code.
    """
    existing = existing_tree or {}
    extensions = {"": "ts", **(tier_extensions or {})}
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"

    for epic in getattr(story_map, "epics", []) or []:
        _scaffold_epic(
            epic, tiers=tiers, extensions=extensions, root=root,
            tree=tree, existing=existing,
        )

    return {path: body for path, body in tree.items() if path not in existing}


def _scaffold_epic(
    epic: Epic, *, tiers: Sequence[str], extensions: Dict[str, str], root: str,
    tree: Dict[str, str], existing: Dict[str, str],
) -> None:
    epic_slug = to_kebab(epic.name)
    for sub in getattr(epic, "sub_epics", []) or []:
        _scaffold_sub_epic(
            sub, tiers=tiers, extensions=extensions,
            parent=f"{root}/{epic_slug}", depth=2,
            tree=tree, existing=existing,
        )


def _scaffold_sub_epic(
    sub: SubEpic, *, tiers: Sequence[str], extensions: Dict[str, str],
    parent: str, depth: int,
    tree: Dict[str, str], existing: Dict[str, str],
) -> None:
    sub_slug = to_kebab(sub.name)
    folder = f"{parent}/{sub_slug}"
    for nested in getattr(sub, "sub_epics", []) or []:
        _scaffold_sub_epic(
            nested, tiers=tiers, extensions=extensions,
            parent=folder, depth=depth + 1,
            tree=tree, existing=existing,
        )
    for story in getattr(sub, "stories", []) or []:
        _scaffold_story(
            story, tiers=tiers, extensions=extensions,
            parent=folder, depth=depth + 1,
            tree=tree, existing=existing,
        )


def _scaffold_story(
    story: Story, *, tiers: Sequence[str], extensions: Dict[str, str],
    parent: str, depth: int,
    tree: Dict[str, str], existing: Dict[str, str],
) -> None:
    if not getattr(story, "scenarios", None):
        return
    story_slug = to_kebab(story.name)
    story_folder = f"{parent}/{story_slug}"
    relative_types_path = "../" * depth + "story-types"
    relative_runner_path = "../" * depth + "story-runner"
    for tier in tiers:
        ext = extensions.get(tier, extensions.get("", "ts"))
        tier_path = f"{story_folder}/{story_slug}-{tier}.test.{ext}"
        tree[tier_path] = _render_tier_file(
            story,
            tier=tier,
            relative_types_path=relative_types_path,
            relative_runner_path=relative_runner_path,
        )


def _render_tier_file(
    story: Story,
    *,
    tier: str,
    relative_types_path: str,
    relative_runner_path: str,
) -> str:
    """Render one collapsed tier file: class + `runScenario(...)` wiring.

    Test-runner discovery keys off the `.test.ts` filename; the class is a
    plain `export` inside the same file, so cross-tier reuse imports it from
    this file directly.
    """
    constant = _pascal(story.name)
    class_name = f"{constant}{_pascal(tier)}"
    story_slug = to_kebab(story.name)
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

    # `type S` unions every scenario constant so `TierImpl<S>` gathers keys
    # from every scenario, not just the first one.
    scenario_types = (
        " | ".join(f"typeof {constant}.{_camel(sc.name)}" for sc in scenarios)
        or f"typeof {constant}.mainFlow"
    )

    lines: List[str] = []
    lines.append(f"import type {{ TierImpl }} from '{relative_types_path}'")
    lines.append(f"import {{ runScenario }} from '{relative_runner_path}'")
    lines.append(f"import {{ {constant} }} from './{story_slug}-stories'")
    lines.append("")
    lines.append(f"type S = {scenario_types}")
    lines.append("")
    lines.append(f"export class {class_name} implements TierImpl<S> {{")
    lines.append("  given = {")
    for clause in given_clauses:
        lines.append(f"    {_ts_string(clause)}: async () => {{")
        lines.append(f"      // TODO: {tier}-tier setup for {_short(clause)}")
        lines.append("    },")
    lines.append("  }")
    lines.append("")
    lines.append("  when = {")
    for clause in when_clauses:
        lines.append(f"    {_ts_string(clause)}: async () => {{")
        lines.append(f"      // TODO: {tier}-tier action for {_short(clause)}")
        lines.append("    },")
    lines.append("  }")
    lines.append("")
    lines.append("  then = {")
    for clause in then_clauses:
        lines.append(f"    {_ts_string(clause)}: async () => {{")
        lines.append(f"      // TODO: {tier}-tier assertion for {_short(clause)}")
        lines.append("    },")
    lines.append("  }")
    lines.append("")
    lines.append("  async cleanup(): Promise<void> {")
    lines.append(f"    // TODO: reset any state seeded by the {tier} tier")
    lines.append("  }")
    lines.append("}")
    lines.append("")
    for scenario in scenarios:
        key = _camel(scenario.name)
        lines.append(
            f"runScenario({constant}.story, {constant}.{key}, "
            f"() => new {class_name}())"
        )
    lines.append("")
    return "\n".join(lines)


def _dedupe_ordered(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _ts_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _short(text: str, limit: int = 60) -> str:
    stripped = re.sub(r"\s+", " ", text).strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 1] + "\u2026"


def _pascal(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "".join(w[:1].upper() + w[1:] for w in parts) or "Story"


def _camel(name: str) -> str:
    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    if not words:
        return "scenario"
    head = words[0][:1].lower() + words[0][1:]
    tail = "".join(w[:1].upper() + w[1:] for w in words[1:])
    return head + tail
