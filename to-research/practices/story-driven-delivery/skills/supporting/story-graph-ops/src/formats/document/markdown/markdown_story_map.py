"""MarkdownStoryMap — renders a StoryMap to Markdown and parses it back.

Layout produced:

    # Epic 1
    ## SubEpic 1
    - Story 1
      - AC 1 text
      - AC 2 text
    - Story 2
    ## SubEpic 2
    # Epic 2

`sync(text, canonical)` parses text into a StoryMap and calls
`canonical.translate_from(parsed)` — the returned UpdateReport lists every add,
remove, rename, reorder, and move applied to the document.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.core.stories.update_report import UpdateReport


class MarkdownParseError(Exception):
    """Raised when a document is not a valid Markdown story map."""


_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_PATTERN = re.compile(r"^(\s*)-\s+(.+)$")
_OUTLINE_EPIC_PATTERN = re.compile(r"^(\s*)\(E\)\s+(.+)$")
_OUTLINE_STORY_PATTERN = re.compile(r"^(\s*)\(S\)\s+(.+)$")
_NUMBERED_ITEM_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)$")


class MarkdownStoryMap:
    """Adapter between a canonical StoryMap and Markdown text.

    Implements the Uniform Callable Surface (see src/architecture-context.md).
    `previous` is accepted for parity and ignored — Markdown documents have no
    hand-written regions to preserve.
    """

    def render(self, story_map: StoryMap, previous: Optional[str] = None) -> str:
        lines: List[str] = []
        for epic in story_map.epics:
            self._render_epic(epic, lines, depth=1)
        return "\n".join(lines)

    def parse(self, text: str) -> StoryMap:
        if not isinstance(text, str) or text.strip() == "":
            # An empty document is a valid empty story map.
            return StoryMap()

        lines = text.splitlines()
        self._guard_has_structure(lines)
        if self._contains_outline_structure(lines):
            return self._parse_outline_lines(lines)
        return self._parse_lines(lines)

    def sync(self, text: str, canonical: StoryMap) -> UpdateReport:
        parsed = self.parse(text)
        return canonical.translate_from(parsed)

    def _render_epic(self, epic: Epic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {epic.name}")
        for sub_epic in epic.sub_epics:
            self._render_sub_epic(sub_epic, lines, depth=depth + 1)

    def _render_sub_epic(self, sub_epic: SubEpic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {sub_epic.name}")
        for nested in sub_epic.sub_epics:
            self._render_sub_epic(nested, lines, depth=depth + 1)
        for story in sub_epic.stories:
            self._render_story(story, lines, indent=0)

    def _render_story(self, story: Story, lines: List[str], indent: int) -> None:
        lines.append(f"{'  ' * indent}- {story.name}")
        for ac in story.acceptance_criteria:
            lines.append(f"{'  ' * (indent + 1)}- {ac.text or ac.name}")

    def _guard_has_structure(self, lines: List[str]) -> None:
        # WHY: rich markdown docs can contain metadata/prose lines before/after
        # the structure we care about. We ignore those lines and require only
        # that at least one recognised structural marker exists.
        for line in lines:
            if (
                _HEADING_PATTERN.match(line)
                or _BULLET_PATTERN.match(line)
                or _OUTLINE_EPIC_PATTERN.match(line)
                or _OUTLINE_STORY_PATTERN.match(line)
            ):
                return
        raise MarkdownParseError(
            "Not a valid Markdown story map: no recognised structure found"
        )

    def _contains_outline_structure(self, lines: List[str]) -> bool:
        return any(
            _OUTLINE_EPIC_PATTERN.match(line) or _OUTLINE_STORY_PATTERN.match(line)
            for line in lines
        )

    def _parse_lines(self, lines: List[str]) -> StoryMap:
        story_map = StoryMap()
        current_epic: Epic | None = None
        current_sub_epic_stack: List[SubEpic] = []
        current_story: Story | None = None
        epic_heading_depth: int | None = None
        ignored_heading_depth: int | None = None

        for raw in lines:
            if not raw.strip():
                continue
            heading = _HEADING_PATTERN.match(raw)
            bullet = _BULLET_PATTERN.match(raw)
            numbered = _NUMBERED_ITEM_PATTERN.match(raw)

            if ignored_heading_depth is not None:
                if heading is None:
                    continue
                depth = len(heading.group(1))
                if depth > ignored_heading_depth:
                    continue
                ignored_heading_depth = None

            if heading:
                depth = len(heading.group(1))
                name = heading.group(2).strip()
                if self._is_document_title(name):
                    current_story = None
                    continue
                if self._is_non_story_section_heading(name):
                    current_story = None
                    ignored_heading_depth = depth
                    continue

                if name.lower().startswith("story:"):
                    story_name = name.split(":", 1)[1].strip() or name
                    parent_sub_epic = self._ensure_sub_epic_for_story(
                        story_map, current_epic, current_sub_epic_stack
                    )
                    current_story = Story(
                        story_name,
                        len(parent_sub_epic.stories) + 1,
                        StoryType.USER,
                    )
                    parent_sub_epic.stories.append(current_story)
                    continue

                if (
                    depth == 1
                    or current_epic is None
                    or (epic_heading_depth is not None and depth <= epic_heading_depth)
                ):
                    if epic_heading_depth is None:
                        epic_heading_depth = depth
                    current_epic = Epic(name, len(story_map.epics) + 1)
                    story_map.epics.append(current_epic)
                    current_sub_epic_stack = []
                    current_story = None
                    continue

                if current_epic is not None:
                    if epic_heading_depth is None:
                        epic_heading_depth = 1
                    relative_depth = max(depth - epic_heading_depth, 1)

                    # WHY: rich docs commonly encode stories as deeper headings
                    # (e.g. `#### View ...`) while standard story-map markdown
                    # uses bullet stories. Treat heading depth >= 2 as story.
                    if relative_depth >= 2:
                        parent_sub_epic = self._ensure_sub_epic_for_story(
                            story_map, current_epic, current_sub_epic_stack
                        )
                        current_story = Story(
                            name,
                            len(parent_sub_epic.stories) + 1,
                            StoryType.USER,
                        )
                        parent_sub_epic.stories.append(current_story)
                    else:
                        while len(current_sub_epic_stack) >= relative_depth:
                            current_sub_epic_stack.pop()
                        parent_children = (
                            current_sub_epic_stack[-1].sub_epics
                            if current_sub_epic_stack
                            else current_epic.sub_epics
                        )
                        sub_epic = SubEpic(name, len(parent_children) + 1)
                        parent_children.append(sub_epic)
                        current_sub_epic_stack.append(sub_epic)
                        current_story = None
                continue

            if bullet:
                indent = len(bullet.group(1)) // 2
                content = bullet.group(2).strip()
                if indent == 0:
                    if current_epic is None:
                        # WHY: tolerate non-story-map bullets in rich docs.
                        continue
                    parent_sub_epic = self._ensure_sub_epic_for_story(
                        story_map, current_epic, current_sub_epic_stack
                    )
                    current_story = Story(
                        content,
                        len(parent_sub_epic.stories) + 1,
                        StoryType.USER,
                    )
                    parent_sub_epic.stories.append(current_story)
                elif current_story is not None:
                    order = len(current_story.acceptance_criteria) + 1
                    current_story.acceptance_criteria.append(
                        AcceptanceCriteria(
                            name=f"AC {order}", sequential_order=order, text=content
                        )
                    )
                continue

            if numbered and current_story is not None:
                order = len(current_story.acceptance_criteria) + 1
                current_story.acceptance_criteria.append(
                    AcceptanceCriteria(
                        name=f"AC {order}",
                        sequential_order=order,
                        text=numbered.group(2).strip(),
                    )
                )
                continue

            # WHY: tolerate prose/metadata lines interleaved with story-map
            # structure in source docs.
            continue

        return story_map

    def _is_document_title(self, heading_text: str) -> bool:
        lower = heading_text.lower()
        return (
            lower.startswith("story map")
            or lower.startswith("acceptance criteria")
            or lower.startswith("specification by example")
        )

    def _is_non_story_section_heading(self, heading_text: str) -> bool:
        lower = heading_text.lower()
        return lower in {"context gaps", "validation results"}

    def _ensure_sub_epic_for_story(
        self,
        story_map: StoryMap,
        current_epic: Epic | None,
        current_sub_epic_stack: List[SubEpic],
    ) -> SubEpic:
        if current_sub_epic_stack:
            return current_sub_epic_stack[-1]

        if current_epic is None:
            current_epic = Epic("Imported", len(story_map.epics) + 1)
            story_map.epics.append(current_epic)

        sub_epic = SubEpic(current_epic.name, len(current_epic.sub_epics) + 1)
        current_epic.sub_epics.append(sub_epic)
        current_sub_epic_stack.append(sub_epic)
        return sub_epic

    def _parse_outline_lines(self, lines: List[str]) -> StoryMap:
        # WHY: support the compact "(E)/(S)" story-map notation used in docs
        # like pml-my/docs/stories/story-map/story-map.md.
        story_map = StoryMap()
        current_epic: Epic | None = None
        current_sub_epic_stack: List[SubEpic] = []

        for raw in lines:
            if not raw.strip():
                continue

            epic_match = _OUTLINE_EPIC_PATTERN.match(raw)
            if epic_match:
                indent = len(epic_match.group(1)) // 4
                name = epic_match.group(2).strip()
                if indent <= 0:
                    current_epic = Epic(name, len(story_map.epics) + 1)
                    story_map.epics.append(current_epic)
                    current_sub_epic_stack = []
                elif current_epic is not None:
                    while len(current_sub_epic_stack) >= indent:
                        current_sub_epic_stack.pop()
                    parent_children = (
                        current_sub_epic_stack[-1].sub_epics
                        if current_sub_epic_stack
                        else current_epic.sub_epics
                    )
                    sub_epic = SubEpic(name, len(parent_children) + 1)
                    parent_children.append(sub_epic)
                    current_sub_epic_stack.append(sub_epic)
                continue

            story_match = _OUTLINE_STORY_PATTERN.match(raw)
            if story_match and current_sub_epic_stack:
                story_text = story_match.group(2).strip()
                if "-->" in story_text:
                    story_text = story_text.split("-->", 1)[1].strip()
                parent_sub_epic = current_sub_epic_stack[-1]
                parent_sub_epic.stories.append(
                    Story(story_text, len(parent_sub_epic.stories) + 1, StoryType.USER)
                )
                continue

            # Non-structural lines are ignored in tolerant mode.
            continue

        return story_map
