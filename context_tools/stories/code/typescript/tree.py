"""TypeScript tree - `{story}.{tier}.ts` under epic / sub-epic (no story folder)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

from context_tools.stories.code.code_story_map import to_kebab
from context_tools.stories.code.typescript.story_file import (
    render_story_file,
    render_test_helper_file,
)
from context_tools.stories.story_model.nodes import Epic, Story, SubEpic
from context_tools.stories.story_model.story_map import StoryMap

TEMPLATES_DIR = Path(__file__).resolve().parent / "seeds"

DEFAULT_TIERS: Sequence[str] = ("front-end", "back-end")

_GIVENS = (
    "export async function given(_name: string): Promise<void> {\n"
    "  // reusable seeds for this folder\n"
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


def _ensure_fixtures(folder: str, tree: Dict[str, str]) -> None:
    tree.setdefault(f"{folder}/givens.ts", _GIVENS)
    tree.setdefault(f"{folder}/examples/.keep", "")


def _render_epic(
    epic: Epic, *, root: str, tree: Dict[str, str], tiers: Sequence[str]
) -> None:
    epic_folder = f"{root}/{to_kebab(epic.name)}"
    _ensure_fixtures(epic_folder, tree)
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
    _ensure_fixtures(folder, tree)
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
    relative_test = "../" * depth + "story-test"
    slug = to_kebab(story.name)
    gwt = render_story_file(story, relative_story_test_path=relative_test)
    for tier in tiers:
        helper = render_test_helper_file(story, tier=tier, same_file=True)
        tree[f"{folder}/{slug}.{tier}.ts"] = gwt + helper


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
