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


from pathlib import Path
from typing import Dict, List, Optional

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryType
from cdd_guidance.practices.stories.model.story_model import Background, StepType, Scenario
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles, path_from, source_at
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks, unlink
from cdd_guidance.practices.stories.model.markdown.map_reading import OutlineLines, described, has_map_structure, is_outline, read_at, read_map
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownExample, MarkdownStep, step_line, step_lines, strip_backticks
from cdd_guidance.practices.stories.model.markdown.scenario_file import SCENARIO_HEADING, ScenarioFileReading, scenario_sections_in
from cdd_guidance.practices.stories.model.markdown.scenario_parts import HEADING_LINE, STEP_LINE, StorySection
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.model.markdown.thin_slice import MarkdownIncrement, thin_slice_in


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
        steps = _SectionLines(parts)
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
        # The lines it was read with in an outline story map; None for a story read from anywhere else.
        self.outline: Optional[OutlineLines] = None

    def document_text(self) -> str:
        """This story in a scenarios document: each line as it was read, with its heading, steps, and scenarios
        written anew where the model changed them; a story not read from a document is written as its heading, then its
        section as its own scenarios file writes it."""
        parts = self.markdown_parts
        if parts is None:
            return "\n".join([f"# Story: {self.name}", "", *self._scenario_section_lines()]).rstrip() + "\n"
        name, heading = self.markdown_heading or ("", None)
        out: List[str] = []
        steps = _SectionLines(parts)
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
        heading = f"{'#' * min(level, 6)} {self.story_type.outline_mark} {actor}--> {self.label(links)}"
        lines = _outlined(self, heading)
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


def _outlined(node, heading: Optional[str]) -> List[str]:
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

    def outline_lines(self, level: int, links: Optional[StoryMapLinks]) -> List[str]:
        """This epic as outline headings at level, every heading at column 0 so it has an anchor to link to: its
        description, its estimate (after its stories for a sub-epic), its stories, then its sub-epics one level
        deeper."""
        lines = _outlined(self, f"{'#' * min(level, 6)} (E) {strip_backticks(self.name)}")
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


class _SectionLines:
    """Writes the step and example lines of one section. Each step line stands where its step was read; a step
    unchanged on the model keeps its line, and steps added on the model follow the owner's last line. Each example row
    stands where its example was read, as the example now says it."""

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
        if isinstance(part, MarkdownExample):
            return part.line()
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
    increment_type = MarkdownIncrement

    def __init__(self, source: Optional[StoryModel] = None) -> None:
        super().__init__(source)
        # The scenarios document this map was read from, kept so rendering it writes each unchanged line back;
        # None for a map read from a story map.
        self.scenario_document: Optional[_ScenarioDocument] = None
        # The lines before its first epic, when it was read from an outline story map; None for a map read otherwise.
        self.outline: Optional[OutlineLines] = None

    def opened_from(self, path: "Path", project: "Path") -> "MarkdownStoryModel":
        """The story map the markdown file at path holds by itself, each node naming the file from project, and, for a
        story map, the increments of the thin slice beside it: the map an edit writes back to path. A scenarios file
        keeps its own lines and no increments."""
        path = Path(path).resolve()
        file = path_from(Path(project).resolve(), path)
        text = path.read_text(encoding="utf-8")
        story_map = self.parse(text, file)
        story_map.source_texts[file] = text
        if story_map.scenario_document is None:
            story_map.slicing = thin_slice_in(path.parent, story_map, project)
        return story_map


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
        if not self.increments and StoryMapFiles(root).thin_slicing() is not None:
            self.slicing = thin_slice_in(root, self, root)

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
        return self._map_text(story_map, links, previous)

    def _map_text(self, story_map: "MarkdownStoryModel", links: Optional[StoryMapLinks], previous: Optional[str]) -> str:
        """story_map as headings and bullets, or as an outline: with the lines it was read with above its first epic,
        else, at discovery, inside the story map document."""
        if not self._should_render_outline(story_map, previous) and not self._is_discovery_story_map(story_map):
            return "\n".join(line for epic in story_map.epics for line in epic.heading_lines(1, links))
        body = "\n".join(line for epic in story_map.epics for line in epic.outline_lines(1, links))
        if story_map.outline is not None and story_map.outline.lines:
            # A map read with lines above its first epic is written back with them, as it was laid out.
            return "\n".join([*_outlined(story_map, None), body]) + "\n"
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
        if not self._looks_like_scenario_document(text.splitlines()) and not is_outline(text.splitlines()):
            # An outline keeps the links in its prose; its reading takes them off the names it reads.
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
        steps = _SectionLines(document.parts)
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
