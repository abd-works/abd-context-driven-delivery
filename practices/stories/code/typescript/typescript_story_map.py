"""TypeScriptStoryMap — renders each leaf SubEpic to a `<sub-epic-slug>-stories.ts`
file matching the reference-architecture spec-file shape.

Output shape (per evals/03-exploration/expected/ts/):

  export const STORY_UPPER_SNAKE = {
    story:       `Story name`,
    actor:       `actor`,
    domainTerms: [],
    evidence:    [],
    scenarioKeyCamelCase: {
      name:         `Scenario name`,
      given:        [`clause...`] as const,
      interactions: [{ when: [`...`] as const, then: [`...`] as const }] as const,
    },
  } as const satisfies Story
"""

from __future__ import annotations

import re
from typing import List, Optional

from stories.story_model.nodes import Story, SubEpic
from stories.story_model.scenario import Clause, Interaction, Scenario
from stories.code.typescript.nodes import (
    TypeScriptEpic,
    TypeScriptStoryMap as _TypeScriptStoryMap,
    TypeScriptSubEpic,
)
from stories.code.code_story_map import (
    CodeStoryMap,
    to_camel,
    to_kebab,
    to_upper_snake,
)


class TypeScriptStoryMap(CodeStoryMap):

    def _make_story_map(self) -> _TypeScriptStoryMap:
        return _TypeScriptStoryMap()

    def _make_epic(self, name: str, order: int) -> TypeScriptEpic:
        return TypeScriptEpic(name, order)

    def _make_sub_epic(self, name: str, order: int) -> TypeScriptSubEpic:
        return TypeScriptSubEpic(name, order)

    LEAF_EXTENSION = "-stories.ts"
    LANGUAGE_LINE_COMMENT = "//"

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        depth_up = self._folder_depth_up_to_types(sub_epic, owning_epic)
        relative = "../" * depth_up + "story-types"
        lines: List[str] = [
            f'import type {{ Story }} from "{relative}";',
            "",
        ]
        for story in sub_epic.stories:
            lines.extend(self._render_story_block(story))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _folder_depth_up_to_types(self, sub_epic: SubEpic, owning_epic: Epic) -> int:
        return 1 + self._sub_epic_depth(sub_epic, owning_epic.sub_epics, 1)

    def _sub_epic_depth(
        self, target: SubEpic, siblings: List[SubEpic], current: int
    ) -> int:
        for sibling in siblings:
            if sibling is target:
                return current
            inner = self._sub_epic_depth(target, sibling.sub_epics, current + 1)
            if inner is not None:
                return inner
        return None  # type: ignore[return-value]

    def _render_story_block(self, story: Story) -> List[str]:
        constant_name = to_upper_snake(story.name)
        actor = story.users[0] if story.users else "user"
        domain_terms = ", ".join(
            f"`{self._ts_literal(t)}`" for t in story.domain_terms
        )
        evidence = ", ".join(
            f"`{self._ts_literal(e)}`" for e in story.evidence
        )
        lines = [
            f"export const {constant_name} = {{",
            f"  story: `{self._ts_literal(story.name)}`,",
            f"  actor: `{self._ts_literal(actor)}`,",
            f"  domainTerms: [{domain_terms}],",
            f"  evidence: [{evidence}],",
        ]
        for scenario in story.scenarios:
            lines.extend(self._render_scenario_property(scenario))
        lines.append("} as const satisfies Story")
        return lines

    def _render_scenario_property(self, scenario: Scenario) -> List[str]:
        key = self._camel_slug(scenario.name)
        given_items = ", ".join(
            f"`{self._ts_literal(c.text)}`" for c in scenario.given
        ) if scenario.given else ""
        interactions_lines: List[str] = []
        for interaction in scenario.interactions:
            when_items = ", ".join(
                f"`{self._ts_literal(c.text)}`" for c in interaction.when
            )
            then_items = ", ".join(
                f"`{self._ts_literal(c.text)}`" for c in interaction.then
            )
            interactions_lines.append(
                f"    {{ when: [{when_items}] as const, then: [{then_items}] as const }}"
            )
        interactions_str = (
            "[\n" + ",\n".join(interactions_lines) + "\n  ] as const"
            if interactions_lines
            else "[]"
        )
        return [
            f"  {key}: {{",
            f"    name: `{self._ts_literal(scenario.name)}`,",
            f"    given: [{given_items}] as const,",
            f"    interactions: {interactions_str},",
            "  },",
        ]

    def _camel_slug(self, text: str) -> str:
        words = re.split(r"[^0-9A-Za-z]+", text)
        words = [w for w in words if w][:10]
        if not words:
            return "scenario"
        return to_camel(" ".join(words))

    def _hydrate_leaf_sub_epic_from_content(
        self, current_sub_epic: SubEpic, file_name: str, content: str
    ) -> None:
        if not file_name.endswith(self.LEAF_EXTENSION):
            return
        if current_sub_epic.stories:
            return

        story_blocks = re.findall(
            r"export const\s+[A-Z0-9_]+\s*=\s*\{([\s\S]*?)\}\s*as const(?:\s+satisfies\s+Story)?[;\n]",
            content,
        )
        for block in story_blocks:
            story_name_match = re.search(r"story:\s*`((?:\\`|[^`])*)`", block)
            if not story_name_match:
                continue
            story = Story(
                self._from_ts_literal(story_name_match.group(1)),
                len(current_sub_epic.stories) + 1,
            )

            actor_match = re.search(r"actor:\s*`((?:\\`|[^`])*)`", block)
            if actor_match:
                story.users = [self._from_ts_literal(actor_match.group(1))]

            # Parse scenario keys — each is a camelCase key with a nested { name: `...` } block
            scenario_blocks = re.findall(
                r"(\w+):\s*\{\s*name:\s*`((?:\\`|[^`])*)`",
                block,
            )
            reserved_keys = {"story", "actor", "domainTerms", "evidence"}
            for i, (key, name_text) in enumerate(scenario_blocks, start=1):
                if key in reserved_keys:
                    continue
                story.scenarios.append(
                    Scenario(
                        name=self._from_ts_literal(name_text),
                        sequential_order=i,
                    )
                )

            current_sub_epic.stories.append(story)

    def _ts_literal(self, text: str) -> str:
        return (
            text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("${", "\\${")
        )

    def _from_ts_literal(self, text: str) -> str:
        return (
            text.replace("\\${", "${")
            .replace("\\`", "`")
            .replace("\\\\", "\\")
        )
