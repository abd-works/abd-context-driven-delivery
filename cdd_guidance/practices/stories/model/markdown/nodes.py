"""Markdown format story nodes - all seven StoryNode subtypes plus I/O.

Layout produced:

    # Epic 1
    ## Epic 1
    - Story 1
    - Story 2
    ## Epic 2
    # Epic 2

A map's text is read by the reading made for its notation (``map_reading``), and a scenarios file by its own
(``scenario_file``); the nodes here keep only what they were read as.
"""

from __future__ import annotations


import re
from pathlib import Path
from typing import Dict, List, Optional

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryType
from cdd_guidance.practices.stories.model.story_model import Background, StepType, Scenario
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles, path_from, source_at
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks, unlink
from cdd_guidance.practices.stories.model.markdown.map_reading import has_map_structure, is_outline, read_at, read_map
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownStep, step_line, step_lines, strip_backticks, strip_markup
from cdd_guidance.practices.stories.model.markdown.scenario_file import SCENARIO_HEADING, ScenarioFileReading, scenario_sections_in
from cdd_guidance.practices.stories.model.markdown.scenario_parts import HEADING_LINE, STEP_LINE, StorySection
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.model.story_model import Increment

# -- MarkdownIncrement ---------------------------------------------------------

_INCREMENT_H3 = re.compile(r"^###\s+Increment\s+\d+\s*:\s*(.+?)\s*$", re.IGNORECASE)
_ANY_H2 = re.compile(r"^##\s+(?!#)")
_KV_OUTCOME = re.compile(r"^\*\*Outcome\s*:\*\*\s*(.+)$", re.IGNORECASE)
_KV_SLICING = re.compile(r"^\*\*Slicing\s+notes\s*:\*\*\s*(.+)$", re.IGNORECASE)
_KV_STORIES = re.compile(r"^\*\*Stories(?:\s+in\s+this\s+increment)?\s*:?\*\*", re.IGNORECASE)
_KV_DECISION = re.compile(r"^\*\*Decision\s+prompt\s*:\*\*\s*(.+)$", re.IGNORECASE)
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")


class MarkdownIncrement(Increment):
    """Increment leaf node for the Markdown format. Knows how to parse thin-slicing.md."""

    @classmethod
    def from_workspace(cls, root: "Path", story_map: "StoryModel") -> List["MarkdownIncrement"]:
        """The increments of the thin-slicing markdown *root* holds (``StoryMapFiles.thin_slicing``), each delivering
        story_map's own stories; none when it holds none."""
        root = Path(root).resolve()
        found = None if root.is_file() else StoryMapFiles(root).thin_slicing()
        if found is None:
            return []
        return cls.parse(found.read_text(encoding="utf-8"), found.relative_to(root).as_posix(), story_map)

    @classmethod
    def parse(cls, text: str, rel_file: str, story_map: "StoryModel") -> List["MarkdownIncrement"]:
        """Parse a thin-slicing.md body into a list of MarkdownIncrement nodes; each bullet names one of story_map's
        stories, which the increment delivers."""
        increments: List[MarkdownIncrement] = []
        current: Optional[MarkdownIncrement] = None
        in_stories = False

        for idx, raw in enumerate(text.splitlines(), start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            m_inc = _INCREMENT_H3.match(stripped)
            if m_inc:
                if current is not None:
                    increments.append(current)
                current = cls(strip_markup(m_inc.group(1)), len(increments) + 1)
                current.source = source_at(rel_file, idx)
                in_stories = False
                continue
            if current is None:
                continue
            if m := _KV_OUTCOME.match(stripped):
                current.outcome = strip_markup(m.group(1))
                in_stories = False
            elif m := _KV_SLICING.match(stripped):
                current.slicing_notes = strip_markup(m.group(1))
                in_stories = False
            elif m := _KV_DECISION.match(stripped):
                current.decision_prompt = strip_markup(m.group(1))
                in_stories = False
            elif _KV_STORIES.match(stripped):
                in_stories = True
            elif _ANY_H2.match(raw) or _INCREMENT_H3.match(raw):
                in_stories = False
            elif in_stories:
                if m := _BULLET.match(raw):
                    current.stories.extend(story_map.stories_named([strip_markup(m.group(1))]))
                else:
                    in_stories = False

        if current is not None:
            increments.append(current)
        return increments


class MarkdownScenario(Scenario):
    """Scenario leaf node for the Markdown format; a scenarios file is read into these by ScenarioFileReading."""

    def __init__(self, name: "str | Scenario" = "", sequential_order: int = 0) -> None:
        super().__init__(name, sequential_order)
        # The heading (name, outline, line) and the lines the scenario was read with, so an unchanged scenario is
        # written back as read; None for a scenario not read from a scenarios document.
        self.markdown_heading: Optional[tuple] = None
        self.markdown_parts: Optional[list] = None

    def heading(self, marks: str) -> str:
        """`### Scenario: name`, or `### Scenario Outline: name` for an outline, at the heading level marks gives."""
        kind = "Scenario Outline" if self.is_outline else "Scenario"
        return f"{marks} {kind}: {self.name}"

    def lines(self) -> List[str]:
        """This scenario as markdown: its heading, its own backgrounds, its steps in Given, When, Then order, and its
        examples table."""
        lines = [self.heading("###"), ""]
        for background in self.backgrounds:
            if background.steps:
                lines.extend(["### Background", ""])
                lines.extend(line for step in background.steps for line in step_lines(step))
                lines.append("")
        lines.extend(line for step in self.steps_in(StepType.GIVEN) for line in step_lines(step))
        for when_steps, then_steps in self.when_then_runs():
            lines.extend(line for step in [*when_steps, *then_steps] for line in step_lines(step))
        if self.examples:
            lines.append("")
        lines.extend(example_table_lines(self.examples))
        return lines if lines[-1] == "" else lines + [""]

    def document_text(self) -> str:
        """This scenario in a scenarios document: each line as it was read, with its heading and steps written anew
        where the model changed them; a scenario not read from a document is written whole, as ``lines`` writes it."""
        parts = self.markdown_parts
        if parts is None:
            return "\n".join(self.lines())
        name, is_outline, heading = self.markdown_heading or ("", False, None)
        out: List[str] = []
        steps = _StepLines(parts)
        for part in parts:
            if part != HEADING_LINE:
                out.append(steps.write(part))
            elif heading is not None and (name, is_outline) == (self.name, self.is_outline):
                out.append(heading)
            else:
                out.append(f"{self.heading(heading.split(' ', 1)[0] if heading else '####')}\n")
        return "".join(out)


def example_table_lines(examples) -> List[str]:
    """Examples as markdown tables under an Examples heading: one table per group and set of columns."""
    if not examples:
        return []
    buckets: List[tuple] = []
    index: dict = {}
    for name, example in examples.items():
        cells = {"example": name, **example.cells()}
        headers = tuple(cells.keys())
        group = str(cells.get("group") or "")
        key = (group, headers)
        if key not in index:
            index[key] = len(buckets)
            buckets.append((group, headers, []))
        buckets[index[key]][2].append(cells)
    lines = ["### Examples", ""]
    for group, headers, entries in buckets:
        if group:
            lines.extend([f"#### {group}", ""])
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for cells in entries:
            values = [str(cells.get(header, "")).replace("|", "/") for header in headers]
            lines.append("| " + " | ".join(values) + " |")
        lines.append("")
    return lines


# -- Leaf node types -----------------------------------------------------------

class MarkdownStory(Story):
    scenario_type = MarkdownScenario

    def __init__(self, name: "str | Story", sequential_order: int = 0, story_type: StoryType = StoryType.USER) -> None:
        super().__init__(name, sequential_order, story_type)
        # The heading (name, line) and the lines the story was read with in a scenarios document, so an unchanged
        # story is written back as read; None for a story read from anywhere else.
        self.markdown_heading: Optional[tuple] = None
        self.markdown_parts: Optional[list] = None

    def document_text(self) -> str:
        """This story in a scenarios document: each line as it was read, with its heading, steps, and scenarios
        written anew where the model changed them; a story not read from a document is written as its heading, then its
        section as its own scenarios file writes it."""
        parts = self.markdown_parts
        if parts is None:
            return "\n".join([f"# Story: {self.name}", "", *self._scenario_section_lines()]).rstrip() + "\n"
        name, heading = self.markdown_heading or ("", None)
        out: List[str] = []
        steps = _StepLines(parts)
        for part in parts:
            if part == HEADING_LINE:
                out.append(heading if heading is not None and name == self.name else f"# Story: {self.name}\n")
            elif isinstance(part, Scenario):
                if any(scenario is part for scenario in self.scenarios):
                    out.append(_markdown_scenario(part).document_text())
            else:
                out.append(steps.write(part))
        for scenario in self.scenarios:
            if not any(scenario is part for part in parts):
                out.append(_markdown_scenario(scenario).document_text())
        return "".join(out)

    def scenarios_text(self) -> str:
        """This story's own scenarios file: its heading, the examples its scenarios share, its backgrounds, then its
        scenarios."""
        lines = [f"## Story: {self.name}", ""] if self.name else []
        lines.extend(self._scenario_section_lines())
        return "\n".join(lines).rstrip() + "\n"

    def outline_lines(self, level: int, links: Optional[StoryMapLinks]) -> List[str]:
        """This story as an outline heading at level, linked to its own file when links name one, with its
        backgrounds and scenarios one heading level below."""
        actor = f"{strip_backticks(self.actors[0])} " if self.actors else ""
        lines = [f"{'#' * min(level, 6)} {self.story_type.outline_mark} {actor}--> {self.label(links)}"]
        if not self.scenarios and not self.backgrounds:
            return lines
        marks = "#" * min(level + 1, 6)
        section = "\n".join(self._scenario_section_lines()).rstrip()
        return lines + [""] + [f"{marks} {line[4:]}" if line.startswith("### ") else line for line in section.splitlines()]

    def label(self, links: Optional[StoryMapLinks]) -> str:
        """The story's name, linked to its own file when links name one."""
        name = strip_backticks(self.name)
        target = links.story_file(self) if links is not None else ""
        return f"[{name}]({target})" if target else name

    def _scenario_section_lines(self) -> List[str]:
        lines = example_table_lines(self._shared_examples())
        for background in self.backgrounds:
            if not background.steps:
                continue
            lines.extend([f"### Story Background: {background.name}", ""])
            lines.extend(line for step in background.steps for line in step_lines(step))
            lines.append("")
            # The story background's own examples sit in its section, so they read back onto the story.
            lines.extend(example_table_lines(background.examples))
        for scenario in self.scenarios:
            lines.extend(scenario.lines())
        return lines

    def _shared_examples(self):
        """The examples the first of this story's scenarios with a background that holds any shares."""
        return next((background.examples for scenario in self.scenarios for background in scenario.backgrounds if background.examples), {})

    def load_scenarios(self, sections: List[StorySection]) -> None:
        """Take a copy of each scenario of the sections headed with this story's name, once each, with the story's
        own background and the examples the first scenario's background shares."""
        took_examples = False
        seen = set()
        for section in (section for section in sections if section.names(self)):
            self._take_story_backgrounds(section.story_backgrounds)
            for scenario in section.scenarios:
                scenario = scenario.clone()
                key = (
                    scenario.name,
                    tuple(
                        (step.keyword, step.text, tuple((extra.keyword, extra.text) for extra in step.ands))
                        for step in scenario.steps
                    ),
                )
                if key in seen:
                    continue
                seen.add(key)
                self.scenarios.append(scenario)
                if not took_examples:
                    took_examples = self._take_background_examples(scenario)

    def _take_story_backgrounds(self, carried: Optional[List[Background]]) -> None:
        """The story's own background a section read, unless this story already has background steps."""
        if not carried or any(background.steps for background in self.backgrounds):
            return
        if not self.backgrounds:
            self.backgrounds = list(carried)
        else:
            self.backgrounds[0].steps = list(carried[0].steps)

    def _take_background_examples(self, scenario) -> bool:
        took = False
        for background in scenario.backgrounds:
            if not background.examples:
                continue
            if not self.backgrounds:
                self.backgrounds.append(Background("background", 1))
            for example_name, example in background.examples.items():
                self.backgrounds[0].examples[example_name] = example
            took = True
        return took


class MarkdownEpic(Epic):
    def outline_lines(self, level: int, links: Optional[StoryMapLinks]) -> List[str]:
        """This epic as outline headings at level, every heading at column 0 so it has an anchor to link to: its
        estimate (after its stories for a sub-epic), its stories, then its sub-epics one level deeper."""
        lines = [f"{'#' * min(level, 6)} (E) {strip_backticks(self.name)}"]
        estimate = [f"* {self.estimate}"] if self.estimate else []
        stories = [line for story in self.stories for line in story.outline_lines(level + 1, links)]
        lines.extend([*estimate, *stories] if level == 1 else [*stories, *estimate])
        lines.extend(line for child in self.epics for line in child.outline_lines(level + 1, links))
        return lines

    def heading_lines(self, depth: int, links: Optional[StoryMapLinks]) -> List[str]:
        """This epic as a heading at depth, its nested epics below it, then its stories as bullets with their
        scenarios beneath. A top epic's own stories have no place in headings."""
        lines = [f"{'#' * depth} {self.name}"]
        lines.extend(line for nested in self.epics for line in nested.heading_lines(depth + 1, links))
        if depth == 1:
            return lines
        for story in self.stories:
            lines.append(f"- {story.label(links)}")
            lines.extend(f"  - {scenario.name}" for scenario in story.scenarios)
        return lines


# -- Root node + I/O -----------------------------------------------------------


class _ScenarioDocument:
    """A scenarios document as it was read: its lines, and the epic or sub-epic its stories are on."""

    def __init__(self, parts: list, holder: MarkdownEpic, tree_heading: Optional[tuple]) -> None:
        self.parts = parts
        self.holder = holder
        self.tree_heading = tree_heading

    def heading_line(self) -> str:
        level, name, line = self.tree_heading
        if name == self.holder.name:
            return line
        return f"# {level}: {self.holder.name}\n"


def _markdown_scenario(scenario: Scenario) -> MarkdownScenario:
    """The scenario as markdown writes it: itself when it is one, else a markdown copy of it."""
    return scenario if isinstance(scenario, MarkdownScenario) else MarkdownScenario(scenario)


class _StepLines:
    """Writes the step lines of one section. Each step line stands where its step was read; a step
    unchanged on the model keeps its line, and steps added on the model follow the owner's last line."""

    def __init__(self, parts: list) -> None:
        self._pending: Dict[int, list] = {}
        self._left: Dict[int, int] = {}
        for part in parts:
            if isinstance(part, tuple) and part[0] == STEP_LINE:
                self._left[id(part[1])] = self._left.get(id(part[1]), 0) + 1

    @staticmethod
    def steps_of(owner) -> list:
        pending = []
        for step in owner.steps:
            pending.append((step, False))
            pending.extend((extra, True) for extra in step.ands)
        return pending

    def write(self, part) -> str:
        if not (isinstance(part, tuple) and part[0] == STEP_LINE):
            return part
        owner = part[1]
        pending = self._pending.setdefault(id(owner), self.steps_of(owner))
        self._left[id(owner)] -= 1
        if self._left[id(owner)] > 0:
            return self.line(*pending.pop(0)) if pending else ""
        written = "".join(self.line(*entry) for entry in pending)
        pending.clear()
        return written

    @staticmethod
    def line(step, continuation: bool) -> str:
        as_read = step.line_as_read() if isinstance(step, MarkdownStep) else None
        if as_read is not None:
            return as_read
        indent = "  " if continuation else ""
        return f"{indent}{step_line(step)}  \n"


class MarkdownParseError(Exception):
    """Raised when a document is not a valid Markdown story map."""


class MarkdownStoryModel(StoryModel):
    """Markdown story-map I/O. render writes a story map as story-map.md text; parse reads that text into a new map,
    each node naming the line it was read on when the text came from a file."""

    suffixes = (".md",)
    epic_type = MarkdownEpic
    story_type = MarkdownStory

    def __init__(self, source: Optional[StoryModel] = None) -> None:
        super().__init__(source)
        # The scenarios document this map was read from, kept so rendering it writes each unchanged line back;
        # None for a map read from a story map.
        self.scenario_document: Optional[_ScenarioDocument] = None

    @classmethod
    def from_workspace(cls, root: "Path", *, on_file=None, project: Optional["Path"] = None) -> Optional["MarkdownStoryModel"]:
        """The story map in the file *root*, or the markdown story maps *root* holds (``StoryMapFiles.markdown_below``),
        merged; None if absent.

        Each node names its file as a path from *project*, so a rule hit points at the file a reader opens;
        without *project* the path is from *root*, or from the folder holding *root* when it is a file.
        """
        root = Path(root).resolve()
        candidates = [root] if root.is_file() else StoryMapFiles(root).markdown_below()
        if not candidates:
            return None
        merged = cls()
        base = Path(project).resolve() if project is not None else (root.parent if root.is_file() else root)
        with merged.batch_schema_sync():
            merged._read_workspace(root, candidates, base, on_file)
        if not merged.epics:
            return None
        return merged

    def _read_workspace(self, root, candidates, base, on_file=None) -> None:
        for md_path in candidates:
            rel = path_from(base, md_path)
            if on_file is not None:
                on_file(rel)
            text = md_path.read_text(encoding="utf-8")
            try:
                parsed = self.parse(text, rel)
            except MarkdownParseError as err:
                raise MarkdownParseError(f"{md_path}: {err}") from err
            self.source_texts[rel] = text
            for epic in parsed.epics:
                self.epics.append(epic)
            if not self.has_source_file:
                self.source = source_at(rel, 1)
        if not self.epics:
            return
        workspace = root.parent if root.is_file() else root
        self._attach_markdown(workspace, on_file=on_file)

    def _attach_markdown(self, root, on_file=None) -> None:
        sections = scenario_sections_in(root, MarkdownScenario, on_file=on_file)
        for story in self.every_story():
            story.load_scenarios(sections)
        if self.increments:
            return
        for increment in MarkdownIncrement.from_workspace(root, self):
            self.increments.append(increment)

    # -- Uniform Callable Surface ----------------------------------------------

    def save(self) -> str:
        return self.render(self)

    def render(
        self,
        canonical: StoryModel,
        previous: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> str:
        """Write canonical, copied into a markdown map when it is in another format. In a *workspace* folder, each
        story that has its own markdown file there links to it; a story with no file stays plain text."""
        story_map = canonical if isinstance(canonical, MarkdownStoryModel) else self.copy_of(canonical)
        document = story_map.scenario_document
        if document is not None:
            return self._render_scenario_document(document)
        links = StoryMapLinks.from_workspace(story_map, workspace) if workspace else None
        if not self._should_render_outline(story_map, previous) and not self._is_discovery_story_map(story_map):
            return "\n".join(line for epic in story_map.epics for line in epic.heading_lines(1, links))
        body = "\n".join(line for epic in story_map.epics for line in epic.outline_lines(1, links))
        if self._is_discovery_story_map(story_map):
            return self._wrap_story_map_document(body, previous)
        return body

    def _should_render_outline(self, story_map: "MarkdownStoryModel", previous: Optional[str]) -> bool:
        """Outline notation is for documents already written that way, or that carry estimates,
        actors, or epics three deep, which headings and bullets cannot hold. An epic with sub-epics
        renders as headings."""
        if previous and is_outline(previous.splitlines()):
            return True
        # Headings put a top-level epic's own stories nowhere, so a map with any is written as an outline.
        if any(epic.stories for epic in story_map.epics):
            return True
        return any(
            self._sub_tree_has_outline_signal(epic) for epic in story_map.epics
        )

    def _sub_tree_has_outline_signal(self, sub: MarkdownEpic) -> bool:
        if getattr(sub, "estimate", ""):
            return True
        if any(story.actors for story in sub.stories):
            return True
        if any(nested.epics for nested in sub.epics):
            return True
        for nested in sub.epics:
            if self._sub_tree_has_outline_signal(nested):
                return True
        return False

    def _is_discovery_story_map(self, story_map: "MarkdownStoryModel") -> bool:
        return not any(story.scenarios or story.backgrounds for story in story_map.every_story())

    def _wrap_story_map_document(self, body: str, previous: Optional[str]) -> str:
        document = DiscoveryDocument("story-map", "Story Map", previous or "")
        scope = [
            "---",
            "",
            "## Scope boundary",
            "",
            "**In scope:** see sketch increments and detailed themes",
            "**Out of scope:** themes not yet moved to specification",
            "",
        ]
        return "\n".join(document.lines(body) + scope)

    def parse(self, text: str, file: str = "") -> "MarkdownStoryModel":
        """The story map text writes. Read from file, each epic, sub-epic, story, and scenario names the line it was
        read on, as it is read."""
        if not isinstance(text, str) or text.strip() == "":
            return MarkdownStoryModel()
        if not self._looks_like_scenario_document(text.splitlines()):
            text = unlink(text)
        lines = text.splitlines()
        if self._looks_like_scenario_document(lines):
            return scenario_document_map(text, file)
        if not has_map_structure(lines):
            raise MarkdownParseError("Not a valid Markdown story map: no recognised structure found")
        return read_map(self, lines, file)

    def _looks_like_scenario_document(self, lines: List[str]) -> bool:
        if is_outline(lines):
            return False
        has_scenario = any(SCENARIO_HEADING.match(line) for line in lines)
        has_clause = any(line.strip().startswith(("*Given*", "*When*", "*Then*")) for line in lines)
        return has_scenario and has_clause

    def _render_scenario_document(self, document: "_ScenarioDocument") -> str:
        out: List[str] = []
        steps = _StepLines(document.parts)
        for part in document.parts:
            if part == HEADING_LINE:
                out.append(document.heading_line())
            elif isinstance(part, MarkdownStory):
                if any(story is part for story in document.holder.stories):
                    out.append(part.document_text())
            else:
                out.append(steps.write(part))
        for story in document.holder.stories:
            if not any(story is part for part in document.parts):
                out.append((story if isinstance(story, MarkdownStory) else MarkdownStory(story)).document_text())
        return "".join(out)


def scenario_document_map(text: str, file: str) -> MarkdownStoryModel:
    """Stories with their backgrounds and scenarios. The document keeps every line in place,
    so rendering it writes it back; a heading or step changed on the model is written anew."""
    reading = ScenarioFileReading(text, file or "story-scenarios.md", MarkdownScenario)
    reading.read()
    story_map = MarkdownStoryModel()
    level, name = (reading.tree_heading or ("sub-epic", "Scenarios"))[:2]
    epic = MarkdownEpic(name if level.lower() == "epic" else "Stories", 1)
    holder = epic if level.lower() == "epic" else MarkdownEpic(name, 1)
    read_at(epic, file, reading.tree_heading_line)
    read_at(holder, file, reading.tree_heading_line)
    if reading.document_examples is not None:
        holder.examples = reading.document_examples.clone(holder)
    parts = []
    for part in reading.document_parts:
        if isinstance(part, StorySection):
            part = _story_from_section(part, len(holder.stories) + 1, file)
            holder.stories.append(part)
        parts.append(part)
    if not holder.stories:
        return story_map
    if holder is not epic:
        epic.epics.append(holder)
    story_map.epics.append(epic)
    story_map.scenario_document = _ScenarioDocument(parts, holder, reading.tree_heading)
    return story_map

def _story_from_section(section: StorySection, order: int, file: str) -> MarkdownStory:
    story = MarkdownStory(section.name, order, StoryType.USER)
    read_at(story, file, section.line)
    if section.background.steps:
        story.backgrounds = [section.background]
    for scenario in section.scenarios:
        story.scenarios.append(scenario)
    story.markdown_heading = (section.name, section.heading)
    story.markdown_parts = section.parts
    return story
