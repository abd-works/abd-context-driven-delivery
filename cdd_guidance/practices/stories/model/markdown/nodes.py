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
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryType
from cdd_guidance.practices.stories.model.story_model import Background, StepType, Scenario
from cdd_guidance.practices.stories.model.story_map_files import STORY_FILE_SUFFIXES, StoryMapFiles, path_from, source_at
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks, unlink
from cdd_guidance.practices.stories.model.markdown.map_reading import OutlineLines, ReplacedOutline, described, has_map_structure, is_outline, read_at, read_map
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownExample, MarkdownStep, step_line, step_lines, strip_backticks
from cdd_guidance.practices.stories.model.markdown.scenario_file import SCENARIO_HEADING, ScenarioFileReading, ScenarioFiles
from cdd_guidance.practices.stories.model.markdown.read_lines import HeadingLine, HeldLines, ReadLine, ReadScenarioDocument, written_lines
from cdd_guidance.practices.stories.model.markdown.scenario_parts import StorySection
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.model.markdown.thin_slice import MarkdownIncrement, ThinSlice
from harness.guidance.practice_formats import OnFile, Written

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_model import Examples, Step, StoryNode

# The heading a sketch writes its Stories section under, which tells a sketch from a story map already written.
_SKETCH_SECTION = "## stories:"
# Markdown has six heading levels; an outline nested deeper writes its headings at the sixth.
_DEEPEST_HEADING = 6
# The heading level a story's scenarios section writes its backgrounds, scenarios and Examples at, and a heading at or
# below it.
_SECTION_TOP = 3
_SECTION_HEADING = re.compile(r"^(#{3,6}) (.*)$")


# How a story's own scenarios file ends, after the story's name in snake case.
_SCENARIOS_FILE_SUFFIX = STORY_FILE_SUFFIXES[0]


class MarkdownScenario(Scenario):
    """Scenario leaf node for the Markdown format; a scenarios file is read into these by ScenarioFileReading."""

    def __init__(self, name: "str | Scenario" = "", sequential_order: int = 0) -> None:
        super().__init__(name, sequential_order)
        # The lines the scenario was read with, its heading first, so an unchanged scenario is written back as read;
        # None for a scenario not read from a scenarios document.
        self.read_lines: Optional[List[ReadLine]] = None

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
        if self.read_lines is None:
            return "\n".join(self.lines())
        return written_lines(self.read_lines)

    def heading_written(self, read: HeadingLine) -> str:
        """Its heading as read while it says the same name and kind, else written anew at the level read."""
        if read.said == (self.name, self.is_outline):
            return read.text
        return f"{self.heading(read.text.split(' ', 1)[0])}\n"


def _example_tables(examples: "Examples") -> List[tuple]:
    """The examples as tables, in the order each first appears: (group, headers, each example's cells), one per group
    and set of columns. A row that names its example in a column of its own keeps its columns as written, and its
    group is the heading above its table, not a column."""
    tables: Dict[tuple, tuple] = {}
    for name, example in examples.items():
        cells = example.cells()
        group = str(cells.pop("group", None) or "")
        if not example.is_named_by_its_row:
            cells = {"example": name, **cells}
        tables.setdefault((group, tuple(cells.keys())), (group, tuple(cells.keys()), []))[2].append(cells)
    return list(tables.values())


def example_table_lines(examples: "Examples") -> List[str]:
    """Examples as markdown tables under an Examples heading: one table per group and set of columns."""
    if not examples:
        return []
    lines = ["### Examples", ""]
    for group, headers, entries in _example_tables(examples):
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
        # The lines the story was read with in a scenarios document, its heading first when it has one, so an
        # unchanged story is written back as read; None for a story read from anywhere else.
        self.read_lines: Optional[List[ReadLine]] = None
        # The lines it was read with in an outline story map; None for a story read from anywhere else.
        self.outline: Optional[OutlineLines] = None

    def document_text(self) -> str:
        """This story in a scenarios document: each line as it was read, with its heading, steps, and scenarios
        written anew where the model changed them; a story not read from a document is written as its heading, then its
        section as its own scenarios file writes it."""
        if self.read_lines is None:
            return "\n".join([f"# Story: {self.name}", "", *self._scenario_section_lines()]).rstrip() + "\n"
        held = [line.node for line in self.read_lines if isinstance(line, HeldLines)]
        out = [written_lines(self.read_lines, self.scenarios)]
        out.extend(self._as_markdown(scenario).document_text() for scenario in self.scenarios if not any(scenario is node for node in held))
        return "".join(out)

    def heading_written(self, read: HeadingLine) -> str:
        """Its heading as read while it says the same name, else written anew."""
        return read.text if read.said == self.name else f"# Story: {self.name}\n"

    def _as_markdown(self, scenario: Scenario) -> MarkdownScenario:
        """The scenario as markdown writes it: itself when it is one, else a markdown copy of it."""
        return scenario if isinstance(scenario, MarkdownScenario) else MarkdownScenario(scenario)

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
        heading = f"{'#' * min(level, _DEEPEST_HEADING)} {self.story_type.outline_mark} {actor}--> {self.label(links)}"
        lines = _outlined(self, heading)
        if not self.scenarios and not self.backgrounds:
            return lines
        section = "\n".join(self._scenario_section_lines()).rstrip()
        return lines + [""] + [self._nested_under(level, line) for line in section.splitlines()]

    def _nested_under(self, level: int, line: str) -> str:
        """A line of this story's scenarios section under its outline heading at level: a heading of the section moves
        down with it, a group of examples staying below its Examples heading; any other line stays as it is."""
        heading = _SECTION_HEADING.match(line)
        if heading is None:
            return line
        marks = len(heading.group(1)) + level + 1 - _SECTION_TOP
        return f"{'#' * min(marks, _DEEPEST_HEADING)} {heading.group(2)}"

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
                key = self._scenario_key(scenario)
                if key in seen:
                    continue
                seen.add(key)
                self.scenarios.append(scenario)
                if not took_examples:
                    took_examples = self._take_background_examples(scenario)

    def _scenario_key(self, scenario: Scenario) -> tuple:
        """What makes a scenario read twice the same one: its name and every step's keyword and text."""
        steps = tuple((step.keyword, step.text, tuple((extra.keyword, extra.text) for extra in step.ands)) for step in scenario.steps)
        return (scenario.name, steps)

    def _take_story_backgrounds(self, carried: Optional[List[Background]]) -> None:
        """The story's own background a section read, unless this story already has background steps."""
        if not carried or any(background.steps for background in self.backgrounds):
            return
        if not self.backgrounds:
            self.backgrounds = list(carried)
        else:
            self.backgrounds[0].steps = list(carried[0].steps)

    def _take_background_examples(self, scenario: Scenario) -> bool:
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


def _outlined(node: "StoryNode", heading: Optional[str]) -> List[str]:
    """node's heading line and the lines under it, holding its description: as it was read in an outline where nothing
    changed them; heading is none for the story map, whose lines above its first epic have none."""
    if node.outline is not None:
        return node.outline.written(node, heading)
    return [*([heading] if heading is not None else []), *described(node.description_text)]


class MarkdownEpic(Epic):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # The lines it was read with in an outline story map; None for an epic read from anywhere else.
        self.outline: Optional[OutlineLines] = None

    def heading_written(self, read: HeadingLine) -> str:
        """The heading of the scenarios document that names this epic, as read while it names it, else anew."""
        level, name = read.said
        return read.text if name == self.name else f"# {level}: {self.name}\n"

    def outline_lines(self, level: int, links: Optional[StoryMapLinks]) -> List[str]:
        """This epic as outline headings at level, every heading at column 0 so it has an anchor to link to: its
        description, its estimate (after its stories for a sub-epic), its stories, then its sub-epics one level
        deeper."""
        lines = _outlined(self, f"{'#' * min(level, _DEEPEST_HEADING)} (E) {strip_backticks(self.name)}")
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


class MarkdownParseError(Exception):
    """Raised when a document is not a valid Markdown story map."""


class MarkdownStoryModel(StoryModel):
    """Markdown story-map I/O. render writes a story map as story-map.md text; parse reads that text into a new map,
    each node naming the line it was read on when the text came from a file."""

    suffixes = (".md",)
    epic_type = MarkdownEpic
    story_type = MarkdownStory
    increment_type = MarkdownIncrement

    def __init__(self, source: Optional[StoryModel] = None) -> None:
        super().__init__(source)
        # The scenarios document this map was read from, kept so rendering it writes each unchanged line back;
        # None for a map read from a story map.
        self.scenario_document: Optional[ReadScenarioDocument] = None
        # The lines before its first epic, when it was read from an outline story map; None for a map read otherwise.
        self.outline: Optional[OutlineLines] = None

    def opened_from(self, path: "Path", project: "Path") -> "MarkdownStoryModel":
        """The story map the markdown file at path holds by itself, each node naming the file from project, and, for a
        story map, the increments of the thin slice beside it: the map an edit writes back to path. A scenarios file
        keeps its own lines and no increments."""
        path = Path(path).resolve()
        story_map = self._parsed_file(path.read_text(encoding="utf-8"), path_from(Path(project).resolve(), path))
        if story_map.scenario_document is None:
            story_map.slicing = ThinSlice.from_folder(path.parent, story_map, project)
        return story_map


    def read_file(self, path: "Path", project: "Path", on_file: OnFile = None) -> "MarkdownStoryModel":
        """The story map in the markdown file at path, with the scenarios files and the thin slice beside it, each node
        naming its file as a path from project, so a rule hit points at the file a reader opens; empty when the file
        holds no epic."""
        return self._read_at(Path(path), project, on_file)

    def read_folder(self, folder: "Path", project: "Path", on_file: OnFile = None) -> Optional["MarkdownStoryModel"]:
        """The markdown story maps folder holds (``StoryMapFiles.markdown_below``), merged, with the scenarios files
        and the thin slice beside them, each node naming its file as a path from project; none when it holds none."""
        merged = self._read_at(Path(folder), project, on_file)
        return merged if merged.epics else None

    def _read_at(self, root: "Path", project: "Path", on_file: OnFile) -> "MarkdownStoryModel":
        merged = type(self)()
        with merged.batch_schema_sync():
            merged._read_workspace(Path(root).resolve(), Path(project).resolve(), on_file)
        return merged

    def _read_workspace(self, root: Path, base: Path, on_file: Optional[Callable[[str], None]]) -> None:
        """The story map in the file root, or the markdown story maps root holds, each node naming its file from base,
        then the scenarios and thin slice beside them."""
        for md_path in [root] if root.is_file() else StoryMapFiles(root).markdown_below():
            rel = path_from(base, md_path)
            if on_file is not None:
                on_file(rel)
            self._take_map(self._parsed_file(md_path.read_text(encoding="utf-8"), rel), rel)
        if not self.epics:
            return
        workspace = root.parent if root.is_file() else root
        self._attach_markdown(workspace, on_file=on_file, base=base)

    def _parsed_file(self, text: str, file: str) -> "MarkdownStoryModel":
        """The map text, the markdown file called file, holds, each node naming file, keeping text as one of its
        sources. Text that does not read is a MarkdownParseError naming the file."""
        try:
            parsed = self.parse(text, file)
        except MarkdownParseError as err:
            raise MarkdownParseError(f"{file}: {err}") from err
        parsed.sources.add(file, text)
        return parsed

    def _take_map(self, parsed: "MarkdownStoryModel", file: str) -> None:
        """Take parsed's epics and sources onto this map, which names file as its own when it names none yet."""
        self.sources.take(parsed.sources)
        for epic in list(parsed.epics):
            self.epics.append(epic)
        if not self.has_source_file:
            self.source = source_at(file, 1)

    def _attach_markdown(self, root: Path, on_file: Optional[Callable[[str], None]] = None, base: Optional[Path] = None) -> None:
        sections = ScenarioFiles(root, base).sections(MarkdownScenario, on_file)
        placed = self.descendants.stories()
        for story in placed:
            story.load_scenarios(sections)
        self._keep_unplaced([section for section in sections if not any(section.names(story) for story in placed)])
        if not self.increments and StoryMapFiles(root).thin_slicing() is not None:
            self.slicing = ThinSlice.from_folder(root, self, root)

    def _keep_unplaced(self, sections: List[StorySection]) -> None:
        """Keep the story each of sections specifies as one this map does not hold, once for each name, with the
        scenarios of every section headed with that name, read where the first of them stands in its scenarios file. A
        section with no scenarios specifies nothing, so it keeps no story."""
        for section in sections:
            if not section.scenarios or any(section.names(story) for story in self.unplaced_stories):
                continue
            story = self.story_type(section.name.strip(), len(self.unplaced_stories) + 1)
            story.source = source_at(section.file, section.line)
            story.load_scenarios(sections)
            self.unplaced_stories.append(story)

    # -- Uniform Callable Surface ----------------------------------------------

    def save(self) -> str:
        return self.render(self)

    def scenarios_files(self, folder: str) -> Dict[str, str]:
        """The scenarios file of each story that has scenarios, by its path under folder, as the scenarios fidelity
        declares it: named for the story, in the folder of the sub-epic that holds it, or of the epic when the epic
        holds it itself (``{folder}/{epic}/{sub-epic}/{story_snake}_story.test.md``)."""
        files: Dict[str, str] = {}
        pending = [(epic, f"{folder}/{epic.slug}") for epic in self.epics]
        while pending:
            epic, epic_folder = pending.pop(0)
            for story in epic.stories:
                if story.scenarios:
                    files[f"{epic_folder}/{story.slug.replace('-', '_')}{_SCENARIOS_FILE_SUFFIX}"] = story.scenarios_text()
            pending.extend((child, f"{epic_folder}/{child.slug}") for child in epic.epics)
        return files

    def render(self, canonical: StoryModel, written: Written = Written()) -> str:
        """Write canonical, copied into a markdown map when it is in another format. Written in a folder, each story
        that has its own markdown file there links to it; a story with no file stays plain text."""
        story_map = canonical if isinstance(canonical, MarkdownStoryModel) else self.copy_of(canonical)
        document = story_map.scenario_document
        if document is not None:
            return document.text()
        previous = written.previous or None
        links = StoryMapLinks(story_map, str(written.folder)) if written.folder is not None else None
        replaced = self._replaced_outline(previous)
        if replaced is not None:
            replaced.lend_to(story_map)
        return self._map_text(story_map, links, previous)

    def _map_text(self, story_map: "MarkdownStoryModel", links: Optional[StoryMapLinks], previous: Optional[str]) -> str:
        """story_map as headings and bullets, or as an outline: with the lines it was read with above its first epic,
        else, at discovery, inside the story map document."""
        if not self._should_render_outline(story_map, previous) and not self._is_discovery_story_map(story_map):
            return "\n".join(line for epic in story_map.epics for line in epic.heading_lines(1, links))
        body = "\n".join(line for epic in story_map.epics for line in epic.outline_lines(1, links))
        if story_map.outline is not None and story_map.outline.lines:
            # A map read with lines above its first epic is written back with them, as it was laid out; a map read from
            # a format that holds no title, such as a drawing, has the lines of the file it replaces.
            return "\n".join([*_outlined(story_map, None), body]) + "\n"
        if self._is_discovery_story_map(story_map):
            return self._wrap_story_map_document(body, previous)
        return body

    def _replaced_outline(self, previous: Optional[str]) -> Optional[ReplacedOutline]:
        """The outline story map this render writes over, whose words a format that holds none, such as a drawing, gets
        back; none when it replaces no file, a sketch, or a map in another notation."""
        if not previous or _SKETCH_SECTION in previous.lower() or not is_outline(previous.splitlines()):
            return None
        return ReplacedOutline(MarkdownStoryModel().parse(previous))

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
        return not any(story.scenarios or story.backgrounds for story in story_map.descendants.stories())

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
        if not self._looks_like_scenario_document(text.splitlines()) and not is_outline(text.splitlines()):
            # An outline keeps the links in its prose; its reading takes them off the names it reads.
            text = unlink(text)
        lines = text.splitlines()
        if self._looks_like_scenario_document(lines):
            return self._scenario_document_map(text, file)
        if not has_map_structure(lines):
            raise MarkdownParseError("Not a valid Markdown story map: no recognised structure found")
        return read_map(self, lines, file)

    def _looks_like_scenario_document(self, lines: List[str]) -> bool:
        if is_outline(lines):
            return False
        has_scenario = any(SCENARIO_HEADING.match(line) for line in lines)
        has_clause = any(line.strip().startswith(("*Given*", "*When*", "*Then*")) for line in lines)
        return has_scenario and has_clause

    def _scenario_document_map(self, text: str, file: str) -> "MarkdownStoryModel":
        """Stories with their backgrounds and scenarios. The document keeps every line in place,
        so rendering it writes it back; a heading or step changed on the model is written anew."""
        reading = ScenarioFileReading(text, file or "story-scenarios.md", MarkdownScenario)
        reading.read()
        story_map = MarkdownStoryModel()
        level, name = reading.tree_heading.said if reading.tree_heading is not None else ("sub-epic", "Scenarios")
        epic = MarkdownEpic(name if level.lower() == "epic" else "Stories", 1)
        holder = epic if level.lower() == "epic" else MarkdownEpic(name, 1)
        read_at(epic, file, reading.tree_heading_line)
        read_at(holder, file, reading.tree_heading_line)
        if reading.document_examples is not None:
            holder.examples = reading.document_examples.clone(holder)
        for line in reading.document_lines:
            self._take_section(line, holder, file)
        if not holder.stories:
            return story_map
        if holder is not epic:
            epic.epics.append(holder)
        story_map.epics.append(epic)
        if reading.tree_heading is not None:
            reading.tree_heading.node = holder
        story_map.scenario_document = ReadScenarioDocument(reading.document_lines, holder, reading.tree_heading, MarkdownStory)
        return story_map

    def _take_section(self, line: ReadLine, holder: MarkdownEpic, file: str) -> None:
        """A story section of a scenarios document becomes a story on holder, which the document then holds in its
        place, read with the section's lines and named by its heading."""
        if not isinstance(line, HeldLines) or not isinstance(line.node, StorySection):
            return
        section = line.node
        story = MarkdownStory(section.name, len(holder.stories) + 1, StoryType.USER)
        read_at(story, file, section.line)
        if section.background.steps:
            story.backgrounds = [section.background]
        for scenario in section.scenarios:
            story.scenarios.append(scenario)
        if section.heading_line is not None:
            section.heading_line.node = story
        story.read_lines = section.lines
        holder.stories.append(story)
        line.node = story
