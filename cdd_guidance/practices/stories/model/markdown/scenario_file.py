"""A scenarios markdown file as it is read: its story sections, each holding the scenarios read under it.

A file is read by a *ScenarioFileReading* made for that read, which keeps where the read is (the story section, the
scenario, and the parts in ``scenario_parts``: the background, the examples table, and the realization fence it is in)
so no scenario or story node holds any of it. Each node keeps only what it was read as: a scenario its heading and
lines, a step the line it was read from, so an unchanged node is written back as read.
"""

from __future__ import annotations

import os

import re
from pathlib import Path
from typing import Callable, Dict, List, Optional


from cdd_guidance.practices.stories.model.markdown.links import unlink
from cdd_guidance.practices.stories.model.markdown.markup import ExampleRowLine, MarkdownExample, MarkdownStep, strip_markup
from cdd_guidance.practices.stories.model.markdown.scenario_parts import (
    HEADING_LINE,
    STEP_LINE,
    BackgroundReading,
    ExamplesTable,
    RealizationFence,
    StorySection,
)
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles, source_at
from cdd_guidance.practices.stories.model.story_model import Background, Scenario, StepType

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
SCENARIO_HEADING = re.compile(r"^#+\s+Scenario(?:\s+Outline)?(?:\s+\d+)?\s*[:\-]?\s*(.+?)\s*$", re.IGNORECASE)
_STORY_HEADING = re.compile(r"^#+\s+Story(?!\s+Background\b)\s*[:\-]?\s*(.+?)\s*$", re.IGNORECASE)
_ITALIC_STEP = re.compile(r"^\s*\*(Given|When|Then|And|But)\*\s+(.+?)\s*$", re.IGNORECASE)
_BULLET_STEP = re.compile(r"^\s*[-*]\s+(Given|When|Then|And|But)\b\s*(.+?)\s*$", re.IGNORECASE)
_H1 = re.compile(r"^#\s+(.+)$")
_PHASES = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}
# A Story heading names a file's story only near its top, and its title only on its first lines.
_STORY_HEADING_LINES = 20
_TITLE_LINES = 5
# Each kind of heading a scenarios file has, in the order a line is tested for them.
_HEADINGS = (
    ("story", _STORY_HEADING),
    ("scenario", SCENARIO_HEADING),
    ("tree", re.compile(r"^#\s+(Epic|Sub-epic)\s*:\s*(.+?)\s*$", re.IGNORECASE)),
    ("story-background", re.compile(r"^#+\s+Story Background\b(?:\s*:\s*(.+))?\s*$", re.IGNORECASE)),
    ("background", re.compile(r"^#+\s+Background\b", re.IGNORECASE)),
    ("examples", re.compile(r"^#+\s+Examples\b", re.IGNORECASE)),
    ("heading", re.compile(r"^#+\s+")),
)


def heading_of(raw: str) -> tuple:
    """The kind of heading a line is, with its match; ("", None) for a line that is no heading."""
    return next(((kind, match) for kind, pattern in _HEADINGS for match in [pattern.match(raw)] if match), ("", None))


def inferred_story_name(lines: List[str], path: Path) -> str:
    """The story a file's scenarios belong to before any story heading: a Story heading near the top, else its title,
    else the folder or file it is in."""
    found = _first_match(_STORY_HEADING, lines[:_STORY_HEADING_LINES]) or _first_match(_H1, lines[:_TITLE_LINES])
    return strip_markup(found.group(1)) if found else _named_by_place(path)


def _first_match(pattern: re.Pattern, lines: List[str]) -> Optional[re.Match]:
    return next((match for line in lines for match in [pattern.match(line)] if match), None)


def _named_by_place(path: Path) -> str:
    """The story a scenarios file with no heading naming it belongs to: the folder holding its scenarios folder, else
    the file's own name."""
    parts = path.parts
    if len(parts) >= 2 and parts[-2] == "scenarios":
        return parts[-3].replace("-", " ") if len(parts) >= 3 else ""
    return path.stem.replace("-", " ")


class ScenarioFiles:
    """The scenarios markdown files under a root, or the root when it is one, each named from base, the folder its
    story map's own file is named from, so every node of one map names its file the same way; from the root when no
    base is given."""

    def __init__(self, root: Path, base: Path | None = None) -> None:
        self.root = Path(root).resolve()
        self._named_from = Path(base).resolve() if base is not None else self.root

    def sections(self, scenario_type: type, on_file: Optional[Callable[[str], None]] = None) -> List[StorySection]:
        """The story sections of every file, each file read once by a reading made for it; on_file hears each file's
        name as it is read."""
        sections: List[StorySection] = []
        for path in self._files():
            rel = self._name_of(path)
            if on_file is not None:
                on_file(rel)
            sections.extend(ScenarioFileReading(path.read_text(encoding="utf-8"), rel, scenario_type).read())
        return sections

    def _files(self) -> List[Path]:
        return [self.root] if self.root.is_file() else StoryMapFiles(self.root).scenario_files_below()

    def _name_of(self, path: Path) -> str:
        return path.name if path == self.root else os.path.relpath(path, self._named_from).replace("\\", "/")


class ScenarioFileReading:
    """One read of a scenarios markdown file: its lines, the story sections it finds, and where in them the read is
    (the line being read, the section, the scenario, and the parts that follow its backgrounds, examples table, and
    realization fence). Made for each read, so the scenarios it reads keep only what they were read as."""

    def __init__(self, text: str, rel: str, scenario_type: type) -> None:
        self.rel = rel
        self.scenario_type = scenario_type
        self.lines = text.splitlines()
        self.kept_lines = text.splitlines(keepends=True)
        self.document_parts: list = []
        self.sections: List[StorySection] = []
        self.tree_heading: Optional[tuple] = None
        self.tree_heading_line = 0
        self.document_examples = None
        self.container = self.document_parts
        self.section: Optional[StorySection] = None
        self.scenario = None
        self.scenario_level = 0
        self.number, self.raw, self.kept = 0, "", ""
        self.story_name = inferred_story_name(self.lines, Path(rel))
        self.backgrounds = BackgroundReading()
        self.examples = ExamplesTable()
        self.fence = RealizationFence()

    def read(self) -> List[StorySection]:
        """The story sections of the file, each holding the scenarios read under it."""
        for number, raw in enumerate(self.lines, start=1):
            self.number, self.raw = number, raw
            self.kept = self.kept_lines[number - 1] if number - 1 < len(self.kept_lines) else raw
            self._read_line()
        self._close_scenario()
        return self.sections

    def _read_line(self) -> None:
        if not self.raw.strip():
            self.backgrounds.blank_line()
            self.container.append(self.kept)
        elif self.fence.accept(self.raw):
            self.container.append(self.kept)
        else:
            kind, match = heading_of(self.raw)
            self._read_heading(kind, match) if kind else self._read_text()

    def _read_heading(self, kind: str, match: re.Match) -> None:
        """A story, scenario, or epic heading opens what it heads; any other heading is a section heading."""
        if kind == "story":
            self._story_heading(match)
        elif kind == "scenario":
            self._scenario_heading(match)
        elif kind == "tree" and self.tree_heading is None and not self.sections:
            self.tree_heading = (match.group(1), strip_markup(match.group(2)), self.kept)
            self.tree_heading_line = self.number
            self.document_parts.append(HEADING_LINE)
        else:
            self._section_heading("heading" if kind == "tree" else kind, match)

    def _story_heading(self, match: re.Match) -> None:
        self._close_scenario()
        self.story_name = strip_markup(match.group(1))
        self.backgrounds.restart(self._open_section(self.story_name, self.kept).background)
        self.examples.heading("story", 0, "")

    def _scenario_heading(self, match: re.Match) -> None:
        self._close_scenario()
        scenario = self.scenario_type(strip_markup(match.group(1)))
        scenario.is_outline = "outline" in self.raw.lower()
        scenario.source = source_at(self.rel, self.number)
        scenario.markdown_heading = (scenario.name, scenario.is_outline, self.kept)
        scenario.markdown_parts = [HEADING_LINE]
        self.scenario = scenario
        self.scenario_level = self._level()[0]
        if self.section is None:
            self._open_section(self.story_name, None)
        self.section.parts.append(scenario)
        self.section.scenarios.append(scenario)
        self.container = scenario.markdown_parts
        self.backgrounds.heading("scenario", "", True)
        self.examples.heading("scenario", 0, "")

    def _open_section(self, name: str, heading: Optional[str]) -> StorySection:
        if not self.sections:
            self.document_examples = self.backgrounds.shared.examples
        section = StorySection(name, heading, self.number, self.rel)
        self.sections.append(section)
        self.document_parts.append(section)
        self.section = section
        self.container = section.parts
        return section

    def _section_heading(self, kind: str, match: re.Match) -> None:
        """A heading above the scenario's own level ends the scenario; then a Story Background, Background, or
        Examples heading opens what it heads, a heading under an Examples heading names a group of its examples, and
        any other heading ends the background and examples being read. The line is kept as written."""
        level, title = self._level()
        if self.scenario is not None and kind != "background" and 0 < level < self.scenario_level:
            self._close_scenario()
            self.container = self.section.parts if self.section is not None else self.document_parts
        if not self.examples.heading(kind, level, title):
            named = (match.group(1) or "background").strip() if kind == "story-background" else ""
            self.backgrounds.heading(kind, named, self.scenario is not None)
        self.container.append(self.kept)

    def _level(self) -> tuple:
        """The line's heading level and its text, as a heading of one to six marks gives them; (0, "") otherwise."""
        heading = HEADING_PATTERN.match(self.raw)
        return (len(heading.group(1)), strip_markup(heading.group(2))) if heading else (0, "")

    def _read_text(self) -> None:
        """A line that is no heading: a step, taken by the background or scenario it belongs to, or text kept as
        written, which may be an example row."""
        match = _ITALIC_STEP.match(self.raw) or _BULLET_STEP.match(self.raw)
        if match is not None:
            self._step_line(match.group(1), unlink(match.group(2)).strip())
            return
        fields = self.examples.row(self.raw)
        self.container.append(self.kept if fields is None else self._record_example(fields))

    def _step_line(self, keyword: str, text: str) -> None:
        background = self.backgrounds.owner_of(keyword)
        owner = background if background is not None else self.scenario
        if owner is None:
            self.container.append(self.kept)
            return
        self._take_step(owner, keyword, text)
        self.container.append((STEP_LINE, owner))
        if owner is self.scenario and keyword.lower() in ("when", "then") and owner.steps:
            self.fence.target = owner.steps[-1]

    def _take_step(self, owner: "Scenario | Background", keyword: str, text: str) -> None:
        """The step this line declares onto owner's steps, read at this line as written: an And or But line continues
        the step before it."""
        steps = list(owner.steps)
        word = keyword.lower()
        previous = steps[-1] if word in ("and", "but") and steps else None
        phase = previous.step_type if previous is not None else _PHASES.get(word, StepType.THEN)
        order = len(previous.ands if previous is not None else steps) + 1
        step = MarkdownStep(text, phase, order)
        step.keyword = word.capitalize()
        step.source = source_at(self.rel, self.number)
        step.read_from(self.kept)
        if previous is not None:
            previous.ands = [*previous.ands, step]
        else:
            steps.append(step)
        owner.steps = steps

    def _record_example(self, fields: Dict[str, str]) -> MarkdownExample:
        """An example row: the scenario's, else the story background's while it is read, else the shared one's. The
        example keeps the row's line and its table's headers, and stands where the line did."""
        value = fields["example"] if set(fields) <= {"example"} else fields
        owner = self.scenario if self.scenario is not None else self.backgrounds.example_owner()
        shared = owner is self.backgrounds.shared
        name = self.examples.label(fields, len(owner.examples) + 1, shared=shared)
        example = MarkdownExample(name, value, ExampleRowLine(self.kept, list(self.examples.headers)))
        example.sequential_order = len(owner.examples) + 1
        owner.examples[name] = example
        return example

    def _close_scenario(self) -> None:
        if self.scenario is None:
            return
        self.backgrounds.give(self.scenario, self.section)
        self.scenario = None
