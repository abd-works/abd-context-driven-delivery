"""TypeScript tree - `{story}.{tier}.ts` under epic / sub-epic (no story folder)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

from context_tools.stories.code.code_story_map import to_kebab, to_snake, to_pascal
from context_tools.stories.code.typescript.story_file import (
    render_story_file,
    render_test_helper_file,
)
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap

TEMPLATES_DIR = Path(__file__).resolve().parent / "seeds"

DEFAULT_TIERS: Sequence[str] = ("front-end", "back-end")

_GIVENS = (
    "/**\n"
    " * Reusable Given steps for this folder.\n"
    " * Labels match the prose used in story files; bodies live here once.\n"
    " */\n"
    "\n"
    "/** Given: a prospect with a created account */\n"
    "export async function aProspectWithACreatedAccount(): Promise<void> {\n"
    "  // TODO: implement reusable given seed\n"
    "}\n"
)

_EXAMPLES = (
    "/**\n"
    " * Example domain fixtures for this folder.\n"
    " */\n"
    "export const validCredentialsExample = {\n"
    "  email: 'user@example.com',\n"
    "  password: 'Password123!',\n"
    "}\n"
)


def render_ts_tree(
    story_map: StoryMap,
    *,
    tests_root: str = "tests",
    include_shared: bool = True,
    tiers: Sequence[str] | None = None,
) -> Dict[str, str]:
    tree: Dict[str, str] = {}
    root = tests_root.strip("/") or "tests"
    seam_tiers = tuple(tiers) if tiers else DEFAULT_TIERS
    if include_shared:
        test_path = TEMPLATES_DIR / "story-test.ts"
        if test_path.exists():
            tree[f"{root}/story-test.ts"] = test_path.read_text(encoding="utf-8")
        else:
            tree[f"{root}/story-test.ts"] = _default_story_test()
    for epic in getattr(story_map, "epics", []) or []:
        _render_epic(epic, root=root, tree=tree, tiers=seam_tiers)
    return tree


def _extract_aggregate_noun(name: str) -> str:
    pascal = to_pascal(name)
    for verb in ("Create", "Get", "Manage", "Settle", "Enter", "Know", "Complete", "Query", "Submit", "View", "Store", "Update", "Delete", "Place"):
        if pascal.startswith(verb) and len(pascal) > len(verb):
            pascal = pascal[len(verb):]
    return pascal


def _render_examples_file(node_name: str, agg_noun: str) -> str:
    agg_camel = agg_noun[:1].lower() + agg_noun[1:]
    return (
        f"/**\n"
        f" * Example domain aggregates and reusable steps for {node_name}.\n"
        f" */\n"
        f"\n"
        f"export interface {agg_noun} {{\n"
        f"  id: string;\n"
        f"  status: 'active' | 'pending' | 'suspended';\n"
        f"  email: string;\n"
        f"  planName?: string;\n"
        f"}}\n"
        f"\n"
        f"// Example aggregates (aggs) that the steps refer to\n"
        f"export const active{agg_noun}Example: {agg_noun} = {{\n"
        f"  id: 'agg-123',\n"
        f"  status: 'active',\n"
        f"  email: 'active-user@example.com',\n"
        f"  planName: 'Premium Plan',\n"
        f"}};\n"
        f"\n"
        f"export const pending{agg_noun}Example: {agg_noun} = {{\n"
        f"  id: 'agg-456',\n"
        f"  status: 'pending',\n"
        f"  email: 'pending-user@example.com',\n"
        f"}};\n"
        f"\n"
        f"export const suspended{agg_noun}Example: {agg_noun} = {{\n"
        f"  id: 'agg-789',\n"
        f"  status: 'suspended',\n"
        f"  email: 'suspended-user@example.com',\n"
        f"}};\n"
        f"\n"
        f"/**\n"
        f" * Reusable Given step referring to the aggregate examples\n"
        f" */\n"
        f"export async function givenA{agg_noun}Exists({agg_camel}: {agg_noun}): Promise<void> {{\n"
        f"  // TODO: implement reusable given step using the aggregate example\n"
        f"}}\n"
        f"\n"
        f"/**\n"
        f" * Reusable When step referring to the aggregate examples\n"
        f" */\n"
        f"export async function whenTheUserInteractsWithA{agg_noun}({agg_camel}: {agg_noun}): Promise<void> {{\n"
        f"  // TODO: implement reusable when step using the aggregate example\n"
        f"}}\n"
        f"\n"
        f"/**\n"
        f" * Reusable Then step referring to the aggregate examples\n"
        f" */\n"
        f"export async function thenThe{agg_noun}IsUpdated({agg_camel}: {agg_noun}): Promise<void> {{\n"
        f"  // TODO: implement reusable then step using the aggregate example\n"
        f"}}\n"
    )


def _ensure_fixtures(node: Epic | SubEpic, folder: str, tree: Dict[str, str]) -> None:
    agg_noun = _extract_aggregate_noun(node.name)
    agg_kebab = to_kebab(agg_noun)
    examples_content = _render_examples_file(node.name, agg_noun)

    tree.setdefault(f"{folder}/givens.ts", _GIVENS)
    tree.setdefault(f"{folder}/examples/{agg_kebab}.examples.ts", examples_content)


def _render_epic(
    epic: Epic, *, root: str, tree: Dict[str, str], tiers: Sequence[str]
) -> None:
    epic_folder = f"{root}/{to_kebab(epic.name)}"
    _ensure_fixtures(epic, epic_folder, tree)
    for sub in getattr(epic, "sub_epics", []) or []:
        _render_sub_epic(sub, parent=epic_folder, depth=2, tree=tree, tiers=tiers)


def _render_sub_epic(
    sub: SubEpic,
    *,
    parent: str,
    depth: int,
    tree: Dict[str, str],
    tiers: Sequence[str],
) -> None:
    folder = f"{parent}/{to_kebab(sub.name)}"
    _ensure_fixtures(sub, folder, tree)
    for nested in getattr(sub, "sub_epics", []) or []:
        _render_sub_epic(
            nested, parent=folder, depth=depth + 1, tree=tree, tiers=tiers
        )
    for story in getattr(sub, "stories", []) or []:
        if not story.scenarios:
            continue
        _render_story(story, folder=folder, depth=depth, tree=tree, tiers=tiers)


def _render_story(
    story: Story,
    *,
    folder: str,
    depth: int,
    tree: Dict[str, str],
    tiers: Sequence[str],
) -> None:
    slug = to_kebab(story.name)
    story_snake = to_snake(story.name)
    story_folder = f"{folder}/{slug}"
    relative_test = "../" * (depth + 1) + "story-test"
    gwt = render_story_file(story, relative_story_test_path=relative_test)
    tree[f"{story_folder}/{story_snake}_story.ts"] = gwt


def _default_story_test() -> str:
    return (
        "export function story(name: string, build: () => void): void {\n"
        "  describe(name, build);\n"
        "}\n\n"
        "export function scenario(\n"
        "  name: string,\n"
        "  build: (steps: {\n"
        "    given: (s: string, fn: () => void) => void;\n"
        "    when: (s: string, fn: () => void) => void;\n"
        "    then: (s: string, fn: () => void) => void;\n"
        "  }) => void,\n"
        "): void {\n"
        "  describe(name, () => {\n"
        "    const givens: Array<() => void> = [];\n"
        "    const whens: Array<() => void> = [];\n"
        "    const thens: Array<{ step: string; fn: () => void }> = [];\n"
        "    build({\n"
        "      given: (_s, fn) => givens.push(fn),\n"
        "      when: (_s, fn) => whens.push(fn),\n"
        "      then: (s, fn) => thens.push({ step: s, fn }),\n"
        "    });\n"
        "    beforeAll(() => {\n"
        "      for (const g of givens) g();\n"
        "      for (const w of whens) w();\n"
        "    });\n"
        "    thens.forEach(({ step, fn }, i) => {\n"
        "      it(i === 0 ? `Then ${step}` : step, fn);\n"
        "    });\n"
        "  });\n"
        "}\n"
    )
