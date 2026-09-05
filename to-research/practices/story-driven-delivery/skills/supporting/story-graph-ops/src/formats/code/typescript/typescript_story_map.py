"""TypeScriptStoryMap — renders each leaf SubEpic to a `<sub-epic-slug>-stories.ts`
file matching the pml-domain/tests/ shape.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, SubEpic
from src.formats.code.code_story_map import (
    CodeStoryMap,
    to_camel,
    to_kebab,
    to_upper_snake,
)


class TypeScriptStoryMap(CodeStoryMap):
    LEAF_EXTENSION = "-stories.ts"
    LANGUAGE_LINE_COMMENT = "//"

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        depth_up = self._folder_depth_up_to_types(sub_epic, owning_epic)
        relative = "../" * depth_up + "story-types"
        lines: List[str] = [
            f'import type {{ Step, AcceptanceCriterion, Background }} from "{relative}";',
            "",
        ]
        for story in sub_epic.stories:
            lines.extend(self._render_story_block(story))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _folder_depth_up_to_types(self, sub_epic: SubEpic, owning_epic: Epic) -> int:
        # tests-root / epic / [nested sub-epics ...] / leaf.ts — story-types module
        # sits at tests-root. Count sub-epic depth + 1 for the Epic folder.
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
        criteria_arrays = self._render_criteria_arrays(story)
        scenarios = self._render_scenarios(story)
        actor = story.users[0] if story.users else "user"
        return [
            f"export const {constant_name} = {{",
            f"  story: `{self._ts_literal(story.name)}`,",
            f"  actor: `{self._ts_literal(actor)}`,",
            "  domain_terms: [],",
            "  evidence: [],",
            f"  acceptance_criteria: {criteria_arrays},",
            *scenarios,
            "} as const;",
        ]

    def _render_criteria_arrays(self, story: Story) -> str:
        chunks: List[str] = ["["]
        for ac in story.acceptance_criteria:
            chunks.append(
                f'    [{{ when: `{self._ts_literal(ac.text or ac.name)}` }}],'
            )
        chunks.append("  ]")
        return "\n".join(chunks)

    def _render_scenarios(self, story: Story) -> List[str]:
        lines: List[str] = []
        for ac in story.acceptance_criteria:
            slug = self._camel_slug(ac.text or ac.name)
            lines.append(f"  {slug}: {{")
            lines.append(f'    name: `{self._ts_literal(ac.name)}`,')
            lines.append(
                f'    steps: [{{ when: `{self._ts_literal(ac.text or ac.name)}` }}] as const,'
            )
            lines.append("  },")
        return lines

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
            r"export const\s+[A-Z0-9_]+\s*=\s*\{([\s\S]*?)\}\s*as const;",
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

            ac_texts_raw = re.findall(
                r"\{\s*when:\s*`((?:\\`|[^`])*)`\s*\}",
                block,
            )
            ac_texts: List[str] = []
            seen_texts = set()
            for value in ac_texts_raw:
                if value in seen_texts:
                    continue
                seen_texts.add(value)
                ac_texts.append(value)

            for i, text in enumerate(ac_texts, start=1):
                story.acceptance_criteria.append(
                    AcceptanceCriteria(
                        name=f"AC {i}",
                        sequential_order=i,
                        text=self._from_ts_literal(text),
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
