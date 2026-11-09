"""The parts a scenarios markdown file's reading keeps while it reads: the story section it is in, the backgrounds and
examples table being read, and the realization fence under a step; and the step a step line declares."""

from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraph
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownStep, step_marks, strip_markup
from cdd_guidance.practices.stories.model.story_model import Background, Step, StepType, Story

_TABLE_LINE = re.compile(r"^\s*\|(.+)\|\s*$")
_PHASES = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}

# Where a read scenarios document had a heading or a step line. Every other line is kept as written.
HEADING_LINE = "heading"
STEP_LINE = "step"


def take_step(owner, keyword: str, text: str, source, read_line: str) -> None:
    """The step a markdown line declares, read at source from read_line, onto owner's steps: an And or But line
    continues the step before it."""
    steps = list(owner.steps)
    word = keyword.lower()
    previous = steps[-1] if word in ("and", "but") and steps else None
    phase = previous.step_type if previous is not None else _PHASES.get(word, StepType.THEN)
    order = len(previous.ands if previous is not None else steps) + 1
    step = MarkdownStep(
        text=text, step_type=phase, sequential_order=order, keyword=word.capitalize(), source=source, read_line=read_line, **step_marks(text)
    )
    if previous is not None:
        previous.ands = [*previous.ands, step]
    else:
        steps.append(step)
    owner.steps = steps


class StorySection:
    """The lines of one story in a scenarios file: its heading, background, scenarios, and text between them. The
    file links its scenarios to their story only by this section's name; once a story takes them, each scenario's story
    is its parent."""

    def __init__(self, name: str, heading: Optional[str], line: int = 0) -> None:
        self.name = name
        self.heading = heading
        # The line of the file the heading is on (line, where the section opens); 0 for a section with no heading.
        self.line, self.parts = (line, [HEADING_LINE]) if heading is not None else (0, [])
        self.background = Background("background", 1)
        self.scenarios: list = []
        # The story's own background (`### Story Background`), which the story that takes this section takes too.
        self.story_backgrounds: Optional[List[Background]] = None

    def names(self, story: Story) -> bool:
        """Whether this section holds story's scenarios: it is headed with the story's name."""
        return self.name.strip() == story.name.strip()


class RealizationFence:
    """A ```realization fence under a When or Then step, read as that step's call graph."""

    def __init__(self) -> None:
        self.target: Optional[Step] = None
        self.lines: List[str] = []
        self.open = False

    def accept(self, raw: str) -> bool:
        """Take the line when it opens, holds, or closes a fence; closing it gives the step its call graph."""
        stripped = raw.strip()
        if self.open:
            if stripped.startswith("```"):
                self._close()
            else:
                self.lines.append(raw.rstrip())
            return True
        if not stripped.startswith("```") or stripped[3:].strip().lower() not in ("", "realization", "call-graph"):
            return False
        self.open, self.lines = True, []
        return True

    def _close(self) -> None:
        body = "\n".join(self.lines)
        if self.target is not None and body.strip():
            self.target.call_graph = CallGraph().read(body)
        self.open, self.lines, self.target = False, [], None


class ExamplesTable:
    """The examples tables under an Examples heading: its heading level, the header row of the table being read, and
    the group heading above it."""

    def __init__(self) -> None:
        self.open = False
        self.level = 0
        self.headers: List[str] = []
        self.group = ""

    def heading(self, kind: str, level: int, title: str) -> bool:
        """A heading of kind at level: an Examples heading opens a table, a heading deeper than it names a group of
        its examples (title), and any other heading ends the table, a story's dropping its group too. True when the
        heading named a group."""
        if kind == "examples":
            self.open, self.level, self.headers, self.group = True, level, [], ""
            return False
        if kind == "heading" and self.open and level > self.level:
            self.group, self.headers = title, []
            return True
        self.open = False
        self.group = "" if kind == "story" else self.group
        return False

    def row(self, raw: str) -> Optional[dict]:
        """The example a table line gives, by header, with its group; none for a line that is no example row."""
        table_line = _TABLE_LINE.match(raw) if self.open else None
        if table_line is None:
            return None
        cells = [cell.strip() for cell in table_line.group(1).split("|")]
        if not self.headers:
            self._take_headers(cells)
            return None
        if all(set(cell.strip(":")) <= {"-"} for cell in cells):
            return None
        return self._fields(cells)

    def _take_headers(self, cells: List[str]) -> None:
        """The table's header row; a separator row read before any header names none."""
        if not all(re.fullmatch(r"-+|:-+:?|:?-+:?", cell) for cell in cells):
            self.headers = [strip_markup(cell) for cell in cells]

    def _fields(self, cells: List[str]) -> dict:
        """One example row by header: its example alone when that is all it names, and its group."""
        fields = dict(zip(self.headers, (strip_markup(cell) for cell in cells)))
        if set(fields) <= {"example", "group"} and fields.get("example"):
            fields = {"example": fields["example"]}
        if self.group:
            fields.setdefault("group", self.group)
        return fields

    def label(self, fields: dict, index: int, shared: bool) -> str:
        """The name an example row is kept under: its example or name column, else, for an example the story's
        scenarios share, its first column or its group, else its place."""
        first = str(fields.get(self.headers[0], "")).strip("+ ") if shared and self.headers else ""
        return str(fields.get("example") or fields.get("name") or first or (self.group if shared else "") or f"example-{index}")


class BackgroundReading:
    """The backgrounds a scenarios file's lines declare for the story being read: the story's own (`Story
    Background`), the one its scenarios share (a Background above them), and a scenario's own (a Background under its
    heading); and which of them the lines being read belong to."""

    def __init__(self) -> None:
        self.shared = Background("background", 1)
        self.local: Optional[Background] = None
        self.story: Optional[Background] = None
        self.took_step = False
        self.open = False
        self.story_open = False

    def restart(self, shared: Background) -> None:
        """A new story section: its shared background, and none of the story before it."""
        self.shared, self.local, self.story = shared, None, None
        self.took_step = self.open = self.story_open = False

    def heading(self, kind: str, name: str, in_scenario: bool) -> None:
        """A heading of kind: a Story Background (called name) opens the story's own; a Background opens a scenario's
        own under its heading, else the one its story's scenarios share; a scenario heading ends both; any other
        heading ends the background being read, while the story's own stays open."""
        if kind == "story-background":
            self.story, self.story_open, self.open = Background(name, 1), True, False
        elif kind == "background":
            self.open, self.took_step = True, False
            self.local = Background("background", 1) if in_scenario else self.local
        else:
            self.open = False
            self.story_open = self.story_open and kind != "scenario"

    def blank_line(self) -> None:
        if self.open and self.took_step:
            self.open = False

    def owner_of(self, keyword: str) -> Optional[Background]:
        """The background a step line with keyword belongs to; none when it belongs to the scenario. A When or Then
        line ends a background."""
        if self.story_open:
            if self.story is None:
                self.story = Background("background", 1)
            return self.story
        if self.open and keyword.lower() in ("when", "then"):
            self.open = False
        if not self.open:
            return None
        self.took_step = True
        return self.local if self.local is not None else self.shared

    def example_owner(self) -> Background:
        """The background an example row outside any scenario belongs to: the story's own while it is being read."""
        return self.story if self.story_open and self.story is not None else self.shared

    def give(self, scenario, section: StorySection) -> None:
        """The scenario's background (its own, else a copy of the shared one), and the story's own to its section."""
        backgrounds = self._scenario_backgrounds()
        if backgrounds:
            scenario.backgrounds = backgrounds
        if self.story is not None and self.story.steps and section.story_backgrounds is None:
            section.story_backgrounds = [self.story]
        self.local = None

    def _scenario_backgrounds(self) -> List[Background]:
        """The scenario's own background, taking the shared examples when it has none; else a copy of the shared one
        when it holds anything; else none."""
        local = self.local
        if local is not None and (local.steps or local.examples):
            if not local.examples and self.shared.examples:
                local.examples = self.shared.examples.clone(local)
            return [local]
        return [self.shared.clone()] if self.shared.steps or self.shared.examples else []
