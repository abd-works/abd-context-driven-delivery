"""A markdown story map as it is read, in either of its notations: headings and bullets (`# Epic`, `## Sub-epic`,
`- Story`), or the outline (`# (E) Epic`, `## (S) actor --> Story`).

Each read is a reading made for it, which keeps where the read is (the line, the epic and sub-epics it is under, the
story it is in) and names on each node the line of the file it was read on, so the map's nodes hold none of it.
"""

from __future__ import annotations

import re
from typing import List, Optional


from cdd_guidance.practices.stories.model.markdown.links import unlink
from cdd_guidance.practices.stories.model.markdown.markup import strip_backticks
from cdd_guidance.practices.stories.model.markdown.scenario_file import HEADING_PATTERN
from cdd_guidance.practices.stories.model.story_map_files import source_at
from cdd_guidance.practices.stories.model.story_model import StoryType

_BULLET_PATTERN = re.compile(r"^(\s*)-\s+(.+)$")
_NUMBERED_PATTERN = re.compile(r"^(\s*)\d+\.\s+(.+)$")
_OUTLINE_EPIC_PATTERN = re.compile(r"^(?P<indent>\s*)(?:(?P<marks>#{1,6})\s+)?\(E\)\s+(?P<name>.+)$")
_OUTLINE_STORY_PATTERN = re.compile(r"^(?P<indent>\s*)(?:(?P<marks>#{1,6})\s+)?\(S(?::(?P<kind>\w+))?\)\s+(?P<name>.+)$")
_OUTLINE_ESTIMATE_PATTERN = re.compile(r"^(\s*)\*\s+(\S.+)$")
# A label is followed by its evidence after a colon, or opens a line and ends its own sentence.
_EVIDENCE_LABEL = re.compile(r"\b(Observed|Inferred|Intended):|^\s*(Observed|Inferred|Intended)\.", re.IGNORECASE)
_DOC_TITLE_PREFIXES = ("story map", "thin slic", "acceptance criteria", "specification by example")
_NON_STORY_SECTIONS = {"context gaps", "validation results"}


def is_outline(lines: List[str]) -> bool:
    """Whether the lines are a story map in the outline notation."""
    return any(_OUTLINE_EPIC_PATTERN.match(line) or _OUTLINE_STORY_PATTERN.match(line) for line in lines)


def has_map_structure(lines: List[str]) -> bool:
    """Whether any line is a heading, bullet, or outline line a story map is made of."""
    patterns = (HEADING_PATTERN, _BULLET_PATTERN, _OUTLINE_EPIC_PATTERN, _OUTLINE_STORY_PATTERN, _OUTLINE_ESTIMATE_PATTERN)
    return any(pattern.match(line) for line in lines for pattern in patterns)


def read_map(format, lines: List[str], file: str):
    """The story map lines write, read by the reading made for their notation, each node naming its line of file."""
    reading = OutlineMapReading if is_outline(lines) else HeadingMapReading
    return reading(format, file).read(lines)


def read_at(node, file: str, line: int) -> None:
    """node was read on line of file, which it names as its source; a map read from text alone names no file."""
    if file and line:
        node.source = source_at(file, line)


def _outline_depth(match: "re.Match") -> int:
    """Depth of an (E) or (S) outline line: one less than its ``#`` count, top-level epic 0. A line with no ``#``
    takes its depth from the old four-space indent."""
    marks = match.group("marks")
    return len(marks) - 1 if marks else len(match.group("indent")) // 4


class MapReading:
    """One read of a story map's text: the format whose epics and stories it makes (format), the map it fills, the
    file it names on each node, the line being read, and the epic and the sub-epics it is under."""

    def __init__(self, format, file: str) -> None:
        self.format = format
        self.file = file
        self.story_map = type(format)()
        self.epic = None
        self.sub_epics: List = []
        self.number, self.raw = 0, ""

    def read(self, lines: List[str]):
        """The story map the lines write, in the notation this reading reads."""
        for self.number, self.raw in enumerate(lines, start=1):
            if self.raw.strip():
                self._read_line()
        return self.story_map

    def _read_line(self) -> None:
        raise NotImplementedError(f"{type(self).__name__} must read a line")

    def _open_epic(self, name: str) -> None:
        """A top-level epic, read on this line."""
        self.epic = self.format.epic_type(name, len(self.story_map.epics) + 1)
        read_at(self.epic, self.file, self.number)
        self.story_map.epics.append(self.epic)
        self.sub_epics = []

    def _open_sub_epic(self, name: str, depth: int) -> None:
        """A sub-epic at depth below the epic, read on this line, under the sub-epic one level above it."""
        while len(self.sub_epics) >= depth:
            self.sub_epics.pop()
        siblings = self.sub_epics[-1].epics if self.sub_epics else self.epic.epics
        sub = self.format.epic_type(name, len(siblings) + 1)
        read_at(sub, self.file, self.number)
        siblings.append(sub)
        self.sub_epics.append(sub)

    def _story(self, name: str, parent, story_type: StoryType = StoryType.USER):
        """A story under parent, read on this line."""
        story = self.format.story_type(name, len(parent.stories) + 1, story_type)
        read_at(story, self.file, self.number)
        parent.stories.append(story)
        return story


class HeadingMapReading(MapReading):
    """A story map written as headings and bullets: `#` epics, deeper headings sub-epics, `-` stories, and their
    scenarios as indented or numbered lines below them."""

    def __init__(self, format, file: str) -> None:
        super().__init__(format, file)
        self.story = None
        self.epic_heading_depth: Optional[int] = None
        self.ignored_heading_depth: Optional[int] = None

    def _read_line(self) -> None:
        if not self._skips_ignored_section():
            self._accept_heading() or self._accept_bullet() or self._accept_numbered()

    def _skips_ignored_section(self) -> bool:
        """Whether this line sits in a section that holds no stories, such as the context gaps."""
        if self.ignored_heading_depth is None:
            return False
        heading = HEADING_PATTERN.match(self.raw)
        if heading is None or len(heading.group(1)) > self.ignored_heading_depth:
            return True
        self.ignored_heading_depth = None
        return False

    def _accept_heading(self) -> bool:
        heading = HEADING_PATTERN.match(self.raw)
        if heading is None:
            return False
        depth, name = len(heading.group(1)), heading.group(2).strip()
        if any(name.lower().startswith(prefix) for prefix in _DOC_TITLE_PREFIXES):
            return True
        if name.lower() in _NON_STORY_SECTIONS:
            self.ignored_heading_depth = depth
        elif name.lower().startswith("story:"):
            self._named_story(name.split(":", 1)[1].strip() or name)
        elif self._is_epic_heading(depth):
            self.epic_heading_depth = depth if self.epic_heading_depth is None else self.epic_heading_depth
            self._open_epic(name)
            self.story = None
        elif self.epic is not None:
            self._accept_nested_heading(name, depth)
        return True

    def _is_epic_heading(self, depth: int) -> bool:
        return self.epic is None or depth == 1 or (self.epic_heading_depth is not None and depth <= self.epic_heading_depth)

    def _accept_nested_heading(self, name: str, depth: int) -> None:
        if self.epic_heading_depth is None:
            self.epic_heading_depth = 1
        relative_depth = max(depth - self.epic_heading_depth, 1)
        if relative_depth >= 2:
            self._named_story(name)
            return
        self._open_sub_epic(name, relative_depth)
        self.story = None

    def _named_story(self, name: str) -> None:
        self.story = self._story(name, self._holding_sub_epic())

    def _listed_scenario(self, text: str) -> None:
        """A scenario listed under the story being read."""
        scenario = self.format.story_type.scenario_type(text, len(self.story.scenarios) + 1)
        read_at(scenario, self.file, self.number)
        self.story.scenarios.append(scenario)

    def _accept_bullet(self) -> bool:
        bullet = _BULLET_PATTERN.match(self.raw)
        if bullet is None:
            return False
        indent, text = len(bullet.group(1)) // 2, bullet.group(2).strip()
        if indent == 0 and self.epic is not None:
            self._named_story(text)
        elif indent >= 1 and self.story is not None:
            self._listed_scenario(text)
        return True

    def _accept_numbered(self) -> bool:
        numbered = _NUMBERED_PATTERN.match(self.raw)
        if numbered is None or self.story is None:
            return False
        self._listed_scenario(re.sub(r"^\*\*(WHEN|THEN|AND|BUT)\*\*\s*", "", numbered.group(2).strip(), flags=re.IGNORECASE))
        return True

    def _holding_sub_epic(self):
        """The sub-epic a story read now sits under: the innermost one open, else one named for the epic, made the
        first time a story needs it; an epic called Imported holds stories read before any epic."""
        if self.sub_epics:
            return self.sub_epics[-1]
        if self.epic is None:
            self.epic = self.format.epic_type("Imported", len(self.story_map.epics) + 1)
            self.story_map.epics.append(self.epic)
        sub = self.format.epic_type(self.epic.name, len(self.epic.epics) + 1)
        self.epic.epics.append(sub)
        self.sub_epics.append(sub)
        return sub


class OutlineLines:
    """The lines a node of an outline story map was read with: the line that heads it, and the lines under it up to the
    next outline line, which hold its description. A node written back unchanged is written as read, so a story map
    laid out by hand keeps every line an edit does not touch."""

    def __init__(self, heading: str = "") -> None:
        self.heading = heading
        self.lines: List[str] = []
        self.description = ""

    def read_from(self, node) -> None:
        """Give node the description its lines hold, and keep that description as read."""
        self.description = "\n".join(self.lines).strip()
        node.description_text = self.description

    def written(self, node, heading: Optional[str]) -> List[str]:
        """The heading, as read while it says what heading says, the links it was written with aside; then the lines
        under it, as read while node's description is unchanged, else its description between blank lines. No heading
        for the story map, which has none."""
        under = self.lines if node.description_text == self.description else described(node.description_text)
        if heading is None:
            return under
        return [self.heading if unlink(self.heading).strip() == heading else heading, *under]


def described(description: str) -> List[str]:
    """A description as the lines under a heading: between blank lines, none when there is none."""
    return ["", *description.splitlines(), ""] if description.strip() else []


class OutlineMapReading(MapReading):
    """A story map written as an outline: `(E)` epics and `(S)` stories, nested by their `#` marks, each story's
    evidence labels below it, and an epic's estimate as a `*` line. The lines under a heading are the description of
    the epic or story it heads, and the lines before the first epic the story map's own; each node keeps the lines it
    was read with (``outline``)."""

    def __init__(self, format, file: str) -> None:
        super().__init__(format, file)
        self.story = None
        self.described = self.story_map
        self.story_map.outline = OutlineLines()

    def read(self, lines: List[str]):
        """The story map the lines write, every line kept by the node it is under, blank lines too."""
        for self.number, self.raw in enumerate(lines, start=1):
            self._read_line()
        for node in [self.story_map, *self.story_map.every_epic(), *self.story_map.every_story()]:
            node.outline.read_from(node)
        return self.story_map

    def _read_line(self) -> None:
        under = self.described
        if (self._accept_epic() or self._accept_story()) and self.described is not under:
            self.described.outline = OutlineLines(self.raw)
        elif self.described is under and not self._accept_estimate():
            self.described.outline.lines.append(self.raw)
            self._accept_evidence()

    def _open_epic(self, name: str) -> None:
        super()._open_epic(name)
        self.described = self.epic

    def _open_sub_epic(self, name: str, depth: int) -> None:
        super()._open_sub_epic(name, depth)
        self.described = self.sub_epics[-1]

    def _story(self, name: str, parent, story_type: StoryType = StoryType.USER):
        self.described = super()._story(name, parent, story_type)
        return self.described

    def _accept_epic(self) -> bool:
        match = _OUTLINE_EPIC_PATTERN.match(self.raw)
        if match is None:
            return False
        depth, name = _outline_depth(match), strip_backticks(unlink(match.group("name")))
        self.story = None
        if depth <= 0:
            self._open_epic(name)
        elif self.epic is not None:
            self._open_sub_epic(name, depth)
        return True

    def _accept_story(self) -> bool:
        match = _OUTLINE_STORY_PATTERN.match(self.raw)
        if match is None or self.epic is None:
            return False
        parent_depth = _outline_depth(match) - 1
        if match.group("marks") or parent_depth <= 0:
            while len(self.sub_epics) > max(parent_depth, 0):
                self.sub_epics.pop()
        actor, name = self._actor_and_name(match.group("name"))
        self.story = self._story(name, self.sub_epics[-1] if self.sub_epics else self.epic, StoryType.from_mark(match.group("kind")))
        if actor:
            self.story.actors = [actor]
        return True

    def _accept_evidence(self) -> None:
        """Record the Observed, Inferred, or Intended labels written in the lines under a story heading."""
        if self.story is None:
            return
        evidence = self.story.evidence
        for label in (with_evidence or ending for with_evidence, ending in _EVIDENCE_LABEL.findall(self.raw)):
            if label.lower() not in evidence:
                evidence.append(label.lower())

    def _actor_and_name(self, raw_text: str) -> tuple[str, str]:
        raw_text = unlink(raw_text)
        if "-->" not in raw_text:
            return "", strip_backticks(raw_text)
        actor, name = raw_text.split("-->", 1)
        return strip_backticks(actor), strip_backticks(name)

    def _accept_estimate(self) -> bool:
        match = _OUTLINE_ESTIMATE_PATTERN.match(self.raw)
        if match is None:
            return False
        holder = self.sub_epics[-1] if self.sub_epics else self.epic
        if holder is not None:
            holder.estimate = match.group(2).strip()
        return True
