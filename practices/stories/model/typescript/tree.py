"""TypeScript tree - `{story_snake}_story.test.ts` under epic / sub-epic / story."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

from practices.stories.model.code_story_map import to_kebab, to_snake, to_pascal
from practices.stories.model.typescript.story_file import (
    render_story_file,
    story_test_file_path,
    story_test_import_path,
)
from practices.stories.model.nodes import Epic, Story, SubEpic
from practices.stories.model.story_map import StoryMap

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


class TypeScriptTree:
    def _path_join(self, *parts: str) -> str:
        return "/".join(p.strip("/") for p in parts if p and p.strip("/"))

    def render(
        self,
        story_map: StoryMap,
        tests_root: str | None = None,
        include_shared: bool = True,
        tiers: Sequence[str] | None = None,
    ) -> Dict[str, str]:
        self._tree: Dict[str, str] = {}
        self._deploy_root = (tests_root if tests_root is not None else "tests").strip("/")
        self._tiers = tuple(tiers) if tiers else DEFAULT_TIERS
        self._folder = self._deploy_root
        if include_shared:
            test_path = TEMPLATES_DIR / "story-test.ts"
            story_test = (
                test_path.read_text(encoding="utf-8")
                if test_path.exists()
                else self._default_story_test()
            )
            self._tree[story_test_file_path(self._deploy_root)] = story_test
        for epic in getattr(story_map, "epics", []) or []:
            self._render_epic(epic)
        return self._tree

    def _extract_aggregate_noun(self, name: str) -> str:
        pascal = to_pascal(name)
        for verb in (
            "Create", "Get", "Manage", "Settle", "Enter", "Know", "Complete",
            "Query", "Submit", "View", "Store", "Update", "Delete", "Place",
        ):
            if pascal.startswith(verb) and len(pascal) > len(verb):
                pascal = pascal[len(verb):]
        return pascal

    def _render_examples_file(self, node_name: str, agg_noun: str) -> str:
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

    def _ensure_fixtures(self, node: Epic | SubEpic) -> None:
        agg_noun = self._extract_aggregate_noun(node.name)
        agg_kebab = to_kebab(agg_noun)
        examples_content = self._render_examples_file(node.name, agg_noun)
        self._tree.setdefault(self._path_join(self._folder, "givens.ts"), _GIVENS)
        self._tree.setdefault(
            self._path_join(self._folder, "examples", f"{agg_kebab}.examples.ts"),
            examples_content,
        )

    def _render_epic(self, epic: Epic) -> None:
        self._folder = self._path_join(self._deploy_root, to_kebab(epic.name))
        self._ensure_fixtures(epic)
        epic_folder = self._folder
        for sub in getattr(epic, "sub_epics", []) or []:
            self._folder = epic_folder
            self._render_sub_epic(sub)

    def _render_sub_epic(self, sub: SubEpic) -> None:
        self._folder = self._path_join(self._folder, to_kebab(sub.name))
        self._ensure_fixtures(sub)
        folder = self._folder
        for nested in getattr(sub, "sub_epics", []) or []:
            self._folder = folder
            self._render_sub_epic(nested)
        for story in getattr(sub, "stories", []) or []:
            if not story.scenarios:
                continue
            self._folder = folder
            self._render_story(story)

    def _render_story(self, story: Story) -> None:
        slug = to_kebab(story.name)
        story_snake = to_snake(story.name)
        story_folder = self._path_join(self._folder, slug)
        import_path = story_test_import_path(self._deploy_root)
        gwt = render_story_file(story, story_test_import_path=import_path)
        self._tree[f"{story_folder}/{story_snake}_story.test.ts"] = gwt

    def _default_story_test(self) -> str:
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


def render_ts_tree(
    story_map: StoryMap,
    *,
    tests_root: str | None = None,
    include_shared: bool = True,
    tiers: Sequence[str] | None = None,
) -> Dict[str, str]:
    return TypeScriptTree().render(
        story_map,
        tests_root=tests_root,
        include_shared=include_shared,
        tiers=tiers,
    )
