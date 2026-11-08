"""Markdown format story nodes - all seven StoryNode subtypes plus I/O.

Layout produced:

    # Epic 1
    ## Epic 1
    - Story 1
    - Story 2
    ## Epic 2
    # Epic 2
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from cdd_guidance.actions.sketch.discovery_document import DiscoveryDocument
from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraph
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryType
from cdd_guidance.practices.stories.model.story_model import Background, StepType, Scenario, Step
from cdd_guidance.practices.stories.model.source_location import SourceLocation, path_from
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles
from cdd_guidance.practices.stories.model.markdown.links import StoryMapLinks, unlink
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.model.story_model import Increment
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_PATTERN = re.compile(r"^(\s*)-\s+(.+)$")
_NUMBERED_PATTERN = re.compile(r"^(\s*)\d+\.\s+(.+)$")
_OUTLINE_EPIC_PATTERN = re.compile(r"^(?P<indent>\s*)(?:(?P<marks>#{1,6})\s+)?\(E\)\s+(?P<name>.+)$")
_OUTLINE_STORY_PATTERN = re.compile(
    r"^(?P<indent>\s*)(?:(?P<marks>#{1,6})\s+)?\(S(?::(?P<kind>\w+))?\)\s+(?P<name>.+)$"
)


def _outline_depth(match: "re.Match") -> int:
    """Depth of an (E) or (S) outline line: one less than its ``#`` count, top-level epic 0.
    A line with no ``#`` takes its depth from the old four-space indent."""
    marks = match.group("marks")
    if marks:
        return len(marks) - 1
    return len(match.group("indent")) // 4
_OUTLINE_ESTIMATE_PATTERN = re.compile(r"^(\s*)\*\s+(\S.+)$")
# A label is followed by its evidence after a colon, or opens a line and ends its own sentence.
_EVIDENCE_LABEL = re.compile(r"\b(Observed|Inferred|Intended):|^\s*(Observed|Inferred|Intended)\.", re.IGNORECASE)


# -- MarkdownIncrement ---------------------------------------------------------

_INCREMENT_H3 = re.compile(r"^###\s+Increment\s+\d+\s*:\s*(.+?)\s*$", re.IGNORECASE)
_ANY_H2 = re.compile(r"^##\s+(?!#)")
_KV_OUTCOME = re.compile(r"^\*\*Outcome\s*:\*\*\s*(.+)$", re.IGNORECASE)
_KV_SLICING = re.compile(r"^\*\*Slicing\s+notes\s*:\*\*\s*(.+)$", re.IGNORECASE)
_KV_STORIES = re.compile(r"^\*\*Stories(?:\s+in\s+this\s+increment)?\s*:?\*\*", re.IGNORECASE)
_KV_DECISION = re.compile(r"^\*\*Decision\s+prompt\s*:\*\*\s*(.+)$", re.IGNORECASE)
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")


def strip_backticks(text: str) -> str:
    """The text without the backticks wrapped around it."""
    s = text.strip()
    while s.startswith("`") and s.endswith("`") and len(s) >= 2:
        s = s[1:-1].strip()
    return s


def strip_markup(text: str) -> str:
    """The text without its links, backticks, and the emphasis wrapped around it."""
    s = strip_backticks(unlink(text))
    while s.startswith("*") and s.endswith("*") and len(s) >= 2:
        s = strip_backticks(s[1:-1].strip())
    return strip_backticks(s)


class MarkdownIncrement(Increment):
    """Increment leaf node for the Markdown format. Knows how to parse thin-slicing.md."""

    @classmethod
    def from_workspace(cls, root: "Path", stories: Dict[str, "Story"]) -> List["MarkdownIncrement"]:
        """Find thin-slicing markdown in *root* and return parsed increments, each delivering the map's own stories,
        which stories holds by name."""
        root = Path(root).resolve()
        if root.is_file():
            return []
        for name in ("thin-slicing.md", "thin-slice.md", "thin-slices.md", "increments.md"):
            candidate = root / name
            if candidate.exists():
                rel = str(candidate.relative_to(root)).replace("\\", "/")
                return cls.parse(candidate.read_text(encoding="utf-8"), rel, stories)
            for found in root.rglob(name):
                rel = str(found.relative_to(root)).replace("\\", "/")
                return cls.parse(found.read_text(encoding="utf-8"), rel, stories)
        return []

    @classmethod
    def parse(cls, text: str, rel_file: str, stories: Dict[str, "Story"]) -> List["MarkdownIncrement"]:
        """Parse a thin-slicing.md body into a list of MarkdownIncrement nodes; each bullet names a story the map
        holds, which stories holds by name."""
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
                current.source = SourceLocation(rel_file, idx)
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
                    story = stories.get(strip_markup(m.group(1)))
                    if story is not None:
                        current.stories.append(story)
                else:
                    in_stories = False

        if current is not None:
            increments.append(current)
        return increments


# -- MarkdownScenario ----------------------------------------------------------

_SCENARIO_H3 = re.compile(
    r"^#+\s+Scenario(?:\s+Outline)?(?:\s+\d+)?\s*[:\-]?\s*(.+?)\s*$", re.IGNORECASE
)
_STORY_H2 = re.compile(r"^#+\s+Story(?!\s+Background\b)\s*[:\-]?\s*(.+?)\s*$", re.IGNORECASE)
_BACKGROUND_H3 = re.compile(r"^#+\s+Background\b", re.IGNORECASE)
_STORY_BACKGROUND_H3 = re.compile(r"^#+\s+Story Background\b(?:\s*:\s*(.+))?\s*$", re.IGNORECASE)
_EXAMPLES_H3 = re.compile(r"^#+\s+Examples\b", re.IGNORECASE)
_ITALIC_STEP = re.compile(r"^\s*\*(Given|When|Then|And|But)\*\s+(.+?)\s*$", re.IGNORECASE)
_BULLET_STEP = re.compile(r"^\s*[-*]\s+(Given|When|Then|And|But)\b\s*(.+?)\s*$", re.IGNORECASE)
_BOLD_TERM = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_VALUE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_STEP_CONTINUATION = re.compile(r"^(And|But)\s+", re.IGNORECASE)
_TABLE_LINE = re.compile(r"^\s*\|(.+)\|\s*$")
_H1 = re.compile(r"^#\s+(.+)$")
_TREE_HEADING = re.compile(r"^#\s+(Epic|Sub-epic)\s*:\s*(.+?)\s*$", re.IGNORECASE)

# Where a parsed scenarios document had a heading or a step line. Every other line is kept as written.
_HEADING_LINE = "heading"
_STEP_LINE = "step"


class _StorySection:
    """The lines of one story: its heading, background, scenarios, and text between them."""

    def __init__(self, name: str, heading: Optional[str]) -> None:
        self.name = name
        self.heading = heading
        self.parts: list = [_HEADING_LINE] if heading is not None else []
        self.background = Background("background", 1)
        self.scenarios: list = []


class MarkdownStep(Step):
    """Step whose text may still carry a markdown And or But prefix."""

    def __init__(self, *args, read_line: Optional[str] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # The keyword, text, and line the step was read with, so an unchanged step is written back as read.
        self.markdown_line: Optional[tuple] = (self.keyword, self.text, read_line) if read_line is not None else None

    def line_as_read(self) -> Optional[str]:
        """The line this step was read from, while its keyword and text are unchanged; otherwise None."""
        if self.markdown_line is None or self.markdown_line[:2] != (self.keyword, self.text):
            return None
        return self.markdown_line[2]

    def display_text(self) -> str:
        """Step text without a leading And or But. The keyword already says which."""
        return _STEP_CONTINUATION.sub("", self.text).strip()

    @classmethod
    def prose(cls, step: Step) -> str:
        if isinstance(step, cls):
            return step.display_text()
        return step.text


class MarkdownScenario(Scenario):
    """Scenario leaf node for the Markdown format. Knows how to parse BDD markdown files."""

    def __init__(self, name: "str | Scenario" = "", sequential_order: int = 0, story_name: str = "") -> None:
        super().__init__(name, sequential_order, story_name)
        # The heading (name, outline, line) and the lines the scenario was read with, so an unchanged scenario is
        # written back as read; None for a scenario not read from a scenarios document.
        self.markdown_heading: Optional[tuple] = None
        self.markdown_parts: Optional[list] = None
        # The story's own background read above this scenario, which the scenario carries to its story.
        self.story_backgrounds: Optional[List[Background]] = None

    @classmethod
    def from_workspace(cls, root: "Path", *, on_file=None) -> List["MarkdownScenario"]:
        """Find all scenario markdown files under *root* and return parsed scenarios."""
        root = Path(root).resolve()
        if root.is_file():
            rel = root.name
            if on_file is not None:
                on_file(rel)
            return cls.parse_file(root, rel)
        scenarios: List["MarkdownScenario"] = []
        seen: set = set()
        for pattern in (
            "**/scenarios/*.md", "**/scenarios/**/*.md", "**/scenarios.md",
            "**/md/*.md", "**/md/**/*.md", "**/*_story.test.md", "**/*_story.spec.md",
            "**/story-scenarios.md", "**/stories/**/*.md",
        ):
            for md in root.glob(pattern):
                rel = str(md.relative_to(root)).replace("\\", "/")
                if rel in seen:
                    continue
                seen.add(rel)
                if on_file is not None:
                    on_file(rel)
                scenarios.extend(cls.parse_file(md, rel))
        return scenarios

    @classmethod
    def parse_file(cls, path: Path, rel: str) -> List["MarkdownScenario"]:
        """Parse a scenarios markdown file into a list of MarkdownScenario nodes."""
        return cls.from_text(path.read_text(encoding="utf-8"), rel)

    @classmethod
    def from_text(cls, text: str, rel: str) -> List["MarkdownScenario"]:
        return cls().parse_text(text, rel)

    def parse_text(self, text: str, rel: str) -> List["MarkdownScenario"]:
        """Parse a scenarios markdown string into a list of MarkdownScenario nodes."""
        self._rel = rel
        self._lines = text.splitlines()
        self._kept_lines = text.splitlines(keepends=True)
        self.document_parts: list = []
        self.sections: List[_StorySection] = []
        self.tree_heading: Optional[tuple] = None
        self.document_examples = None
        self._container = self.document_parts
        self._section: Optional[_StorySection] = None
        self._scenario_level = 0
        self._examples_level = 0
        self._path = Path(rel)
        self._story_name = self._infer_story_name()
        self._shared_background = Background("background", 1)
        self._local_background = None
        self._background_took_step = False
        self._story_level = None
        self._in_story_background = False
        self._assigned_story_background = False
        self._scenarios: List[MarkdownScenario] = []
        self._current: Optional[MarkdownScenario] = None
        self._in_background = False
        self._in_examples = False
        self._example_headers: List[str] = []
        self._example_group = ""
        self._active_phase: Optional[StepType] = None
        self._clause_source: Optional[SourceLocation] = None
        self._clause_keyword = ""
        self._realization_target: Optional[Step] = None
        self._realization_lines: List[str] = []
        self._in_realization_fence = False
        self._parse_document_lines()
        self._flush_current()
        return self._scenarios

    def _parse_document_lines(self) -> None:
        for i, raw in enumerate(self._lines, start=1):
            kept = self._kept_lines[i - 1] if i - 1 < len(self._kept_lines) else raw
            if not raw.strip():
                if self._in_background and self._background_took_step:
                    self._in_background = False
                self._container.append(kept)
                continue
            self._line_index = i
            self._raw_line = raw
            self._kept_line = kept
            if self._accept_realization_fence():
                self._container.append(kept)
                continue
            if self._accept_story_heading():
                continue
            if self._accept_scenario_heading():
                continue
            if self._accept_tree_heading():
                continue
            self._close_scenario_lines()
            if self._accept_section_heading():
                self._container.append(kept)
                continue
            if self._accept_step_line():
                continue
            self._container.append(kept)
            self._accept_example_line()

    def _accept_tree_heading(self) -> bool:
        match = _TREE_HEADING.match(self._raw_line)
        if match is None or self.tree_heading is not None or self.sections:
            return False
        self.tree_heading = (match.group(1), strip_markup(match.group(2)), self._kept_line)
        self.document_parts.append(_HEADING_LINE)
        return True

    def _close_scenario_lines(self) -> None:
        """A heading above the scenario's own level ends the scenario: what follows belongs to the story."""
        heading = _HEADING_PATTERN.match(self._raw_line)
        if heading is None or self._current is None or self._is_reserved_heading():
            return
        if len(heading.group(1)) >= self._scenario_level:
            return
        self._flush_current()
        self._container = self._section.parts if self._section is not None else self.document_parts

    def _open_section(self, name: str, heading: Optional[str]) -> _StorySection:
        if not self.sections:
            self.document_examples = self._shared_background.examples
        section = _StorySection(name, heading)
        self.sections.append(section)
        self.document_parts.append(section)
        self._section = section
        self._container = section.parts
        return section

    def _accept_story_heading(self) -> bool:
        match = _STORY_H2.match(self._raw_line)
        if match is None:
            return False
        self._flush_current()
        self._story_name = strip_markup(match.group(1))
        self._shared_background = self._open_section(self._story_name, self._kept_line).background
        self._local_background = None
        self._background_took_step = False
        self._story_level = None
        self._in_story_background = False
        self._assigned_story_background = False
        self._example_group = ""
        self._in_background = False
        self._in_examples = False
        return True

    def _accept_scenario_heading(self) -> bool:
        match = _SCENARIO_H3.match(self._raw_line)
        if match is None:
            return False
        self._flush_current()
        self._current = type(self)(
            name=strip_markup(match.group(1)),
            story_name=self._story_name,
        )
        self._current.is_outline = "outline" in self._raw_line.lower()
        self._current.source = SourceLocation(self._rel, self._line_index)
        self._current.markdown_heading = (self._current.name, self._current.is_outline, self._kept_line)
        self._current.markdown_parts = [_HEADING_LINE]
        self._scenario_level = len(_HEADING_PATTERN.match(self._raw_line).group(1))
        if self._section is None:
            self._open_section(self._story_name, None)
        self._section.parts.append(self._current)
        self._section.scenarios.append(self._current)
        self._container = self._current.markdown_parts
        self._active_phase = None
        self._in_background = False
        self._in_story_background = False
        self._in_examples = False
        return True

    def _accept_section_heading(self) -> bool:
        story_background = _STORY_BACKGROUND_H3.match(self._raw_line)
        if story_background:
            name = (story_background.group(1) or "background").strip()
            self._story_level = Background(name, 1)
            self._in_story_background = True
            self._in_background = False
            self._in_examples = False
            return True
        if _BACKGROUND_H3.match(self._raw_line):
            return self._begin_background()
        if _EXAMPLES_H3.match(self._raw_line):
            return self._begin_examples()
        if not re.match(r"^#+\s+", self._raw_line):
            return False
        if self._in_examples and not self._is_reserved_heading() and self._heading_level() > self._examples_level:
            return self._begin_example_group()
        self._in_background = False
        self._in_examples = False
        return False

    def _begin_background(self) -> bool:
        self._in_background = True
        self._in_examples = False
        self._background_took_step = False
        if self._current is not None:
            self._local_background = Background("background", 1)
        return True

    def _heading_level(self) -> int:
        heading = _HEADING_PATTERN.match(self._raw_line)
        return len(heading.group(1)) if heading else 0

    def _begin_examples(self) -> bool:
        self._in_examples = True
        self._examples_level = self._heading_level()
        self._in_background = False
        self._example_headers = []
        self._example_group = ""
        return True

    def _begin_example_group(self) -> bool:
        heading = _HEADING_PATTERN.match(self._raw_line)
        self._example_group = strip_markup(heading.group(2)) if heading else ""
        self._example_headers = []
        return True

    def _is_reserved_heading(self) -> bool:
        return bool(
            _SCENARIO_H3.match(self._raw_line)
            or _STORY_H2.match(self._raw_line)
            or _BACKGROUND_H3.match(self._raw_line)
        )

    def _accept_realization_fence(self) -> bool:
        stripped = self._raw_line.strip()
        if self._in_realization_fence:
            if stripped.startswith("```"):
                body = "\n".join(self._realization_lines)
                if self._realization_target is not None and body.strip():
                    self._realization_target.call_graph = CallGraph.parse(body)
                self._in_realization_fence = False
                self._realization_lines = []
                self._realization_target = None
            else:
                self._realization_lines.append(self._raw_line.rstrip())
            return True
        if not stripped.startswith("```"):
            return False
        tag = stripped[3:].strip().lower()
        if tag not in ("", "realization", "call-graph"):
            return False
        self._in_realization_fence = True
        self._realization_lines = []
        return True

    def _accept_step_line(self) -> bool:
        parsed_step = self._parse_step(self._raw_line)
        if parsed_step is None:
            return False
        keyword, step_text = parsed_step
        self._clause_source = SourceLocation(self._rel, self._line_index)
        if self._in_story_background:
            self._consume_story_background(keyword, step_text)
            self._container.append((_STEP_LINE, self._story_level))
            return True
        if self._in_background and keyword.lower() in ("when", "then"):
            self._in_background = False
        if self._in_background:
            self._consume_background(keyword, step_text)
            owner = self._local_background if self._local_background is not None else self._shared_background
            self._container.append((_STEP_LINE, owner))
        elif self._current is not None:
            self._accept_step(keyword, step_text)
            self._container.append((_STEP_LINE, self._current))
            if keyword.lower() in ("when", "then") and self._current.steps:
                self._realization_target = self._current.steps[-1]
        else:
            self._container.append(self._kept_line)
        return True

    def _accept_example_line(self) -> None:
        if not self._in_examples:
            return
        table_line = _TABLE_LINE.match(self._raw_line)
        if table_line is None:
            return
        cells = [c.strip() for c in table_line.group(1).split("|")]
        if not self._example_headers:
            if not all(re.fullmatch(r"-+|:-+:?|:?-+:?", c) for c in cells):
                self._example_headers = [strip_markup(c) for c in cells]
            return
        if all(set(c.strip(":")) <= {"-"} for c in cells):
            return
        fields = dict(zip(self._example_headers, (strip_markup(c) for c in cells)))
        if set(fields) <= {"example", "group"} and fields.get("example"):
            fields = {"example": fields["example"]}
        self._record_example(fields)

    def _record_example(self, fields: dict) -> None:
        if self._example_group:
            fields.setdefault("group", self._example_group)
        if self._current is not None:
            index = len(self._current.examples) + 1
            label = str(fields.get("example") or fields.get("name") or f"example-{index}")
            self._current.examples[label] = fields["example"] if set(fields) <= {"example"} else fields
            return
        if self._in_story_background and self._story_level is not None:
            label = str(fields.get("example") or fields.get("name") or f"example-{len(self._story_level.examples) + 1}")
            self._story_level.examples[label] = fields["example"] if set(fields) <= {"example"} else fields
            return
        index = len(self._shared_background.examples) + 1
        first = str(fields.get(self._example_headers[0], "")).strip("+ ") if self._example_headers else ""
        label = str(fields.get("example") or fields.get("name") or first or self._example_group or f"example-{index}")
        self._shared_background.examples[label] = fields["example"] if set(fields) <= {"example"} else fields

    def _flush_current(self) -> None:
        if self._current is None:
            return
        local = self._local_background
        if local is not None and (local.steps or local.examples):
            if not local.examples and self._shared_background.examples:
                local.examples = self._shared_background.examples.clone(local)
            self._current.backgrounds = [local]
        elif self._shared_background.steps or self._shared_background.examples:
            self._current.backgrounds = [self._shared_background.clone()]
        if (
            self._story_level is not None
            and self._story_level.steps
            and not self._assigned_story_background
        ):
            self._current.story_backgrounds = [self._story_level]
            self._assigned_story_background = True
        self._scenarios.append(self._current)
        self._current = None
        self._local_background = None

    def _parse_step(self, raw: str) -> Optional[tuple[str, str]]:
        match = _ITALIC_STEP.match(raw) or _BULLET_STEP.match(raw)
        if match is None:
            return None
        return (match.group(1), unlink(match.group(2)).strip())

    def make_step(self, text: str, phase: StepType, sequential_order: int) -> MarkdownStep:
        match = _BOLD_TERM.search(text)
        step = MarkdownStep(
            text=text,
            step_type=phase,
            sequential_order=sequential_order,
            keyword=self._clause_keyword,
            concepts=_BOLD_TERM.findall(text),
            values=[v.strip("`").strip() for v in _ITALIC_VALUE.findall(text) if v],
            actor=match.group(1).strip() if match else "",
            source=self._clause_source,
            read_line=self._kept_line,
        )
        return step

    def _take_step(self, steps: List[Step], keyword: str, text: str) -> None:
        word = keyword.lower()
        if word in ("and", "but") and steps:
            previous = steps[-1]
            labeled = word.capitalize()
            self._clause_keyword = labeled
            previous.ands = [
                *previous.ands,
                self.make_step(text, previous.step_type, len(previous.ands) + 1),
            ]
            return
        phase = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}.get(word, StepType.THEN)
        self._clause_keyword = word.capitalize()
        self._active_phase = phase
        steps.append(self.make_step(text, phase, len(steps) + 1))

    def _consume_story_background(self, keyword: str, text: str) -> None:
        if self._story_level is None:
            self._story_level = Background("background", 1)
        steps = list(self._story_level.steps)
        self._take_step(steps, keyword, text)
        self._story_level.steps = steps

    def _consume_background(self, keyword: str, text: str) -> None:
        target = self._local_background if self._local_background is not None else self._shared_background
        steps = list(target.steps)
        self._take_step(steps, keyword, text)
        target.steps = steps
        self._background_took_step = True

    def _accept_step(self, keyword: str, text: str) -> None:
        steps = list(self._current.steps)
        self._take_step(steps, keyword, text)
        self._current.steps = steps

    def _infer_story_name(self) -> str:
        for line in self._lines[:20]:
            match = _STORY_H2.match(line)
            if match:
                return strip_markup(match.group(1))
        for line in self._lines[:5]:
            match = _H1.match(line)
            if match:
                return strip_markup(match.group(1))
        parts = self._path.parts
        if len(parts) >= 2 and parts[-2] == "scenarios":
            return parts[-3].replace("-", " ") if len(parts) >= 3 else ""
        return self._path.stem.replace("-", " ")


def step_lines(step: Step) -> List[str]:
    """A step and the steps chained onto it as markdown lines, with its realization fence when it has a call graph."""
    lines = [f"*{step.keyword}* {MarkdownStep.prose(step)}"]
    for extra in step.ands:
        lines.append(f"*{extra.keyword}* {MarkdownStep.prose(extra)}")
    if getattr(step, "call_graph", None):
        lines.extend(["", "```realization", step.call_graph.block(), "```"])
    return lines


def example_table_lines(examples) -> List[str]:
    """Examples as markdown tables under an Examples heading: one table per group and set of columns."""
    if not examples:
        return []
    buckets: List[tuple] = []
    index: dict = {}
    for name, example in examples.items():
        cells = dict(example.cells())
        cells.setdefault("example", name)
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


def scenario_lines(scenario: Scenario) -> List[str]:
    """One scenario as markdown: its heading, its own backgrounds, its steps in Given, When, Then order, and its
    examples table."""
    kind = "Scenario Outline" if getattr(scenario, "is_outline", False) else "Scenario"
    lines = [f"### {kind}: {scenario.name}", ""]
    for background in scenario.backgrounds:
        if background.steps:
            lines.extend(["### Background", ""])
            lines.extend(line for step in background.steps for line in step_lines(step))
            lines.append("")
    lines.extend(line for step in scenario.steps_in(StepType.GIVEN) for line in step_lines(step))
    for when_steps, then_steps in scenario.when_then_runs():
        lines.extend(line for step in [*when_steps, *then_steps] for line in step_lines(step))
    records = scenario.examples.table()
    if records:
        headers = list(records[0].keys())
        lines.extend(["", "### Examples", "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"])
        lines.extend("| " + " | ".join(str(record.get(header, "")) for header in headers) + " |" for record in records)
    lines.append("")
    return lines


# -- Leaf node types -----------------------------------------------------------

class MarkdownStory(Story):
    def __init__(self, name: "str | Story", sequential_order: int = 0, story_type: StoryType = StoryType.USER) -> None:
        super().__init__(name, sequential_order, story_type)
        # The heading (name, line) and the lines the story was read with in a scenarios document, so an unchanged
        # story is written back as read; None for a story read from anywhere else.
        self.markdown_heading: Optional[tuple] = None
        self.markdown_parts: Optional[list] = None

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
            lines.extend(scenario_lines(scenario))
        return lines

    def _shared_examples(self):
        """The examples the first of this story's scenarios with a background that holds any shares."""
        return next((background.examples for scenario in self.scenarios for background in scenario.backgrounds if background.examples), {})

    def load_scenarios(self, root, scenarios=None) -> None:
        name = self.name.strip()
        took_examples = False
        seen = set()
        found = scenarios if scenarios is not None else MarkdownScenario.from_workspace(root)
        for scenario in found:
            if (scenario.story_name or "").strip() != name:
                continue
            carried = scenario.story_backgrounds
            scenario = scenario.clone()
            if carried is not None:
                scenario.story_backgrounds = carried
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
            if carried and not any(background.steps for background in self.backgrounds):
                if not self.backgrounds:
                    self.backgrounds = list(carried)
                else:
                    self.backgrounds[0].steps = list(carried[0].steps)
            if took_examples:
                continue
            took_examples = self._take_background_examples(scenario)

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

    def _load_scenarios(self, scenarios) -> None:
        for child in self.epics:
            child._load_scenarios(scenarios)
        for story in self.stories:
            story.load_scenarios(None, scenarios)


# -- Root node + I/O -----------------------------------------------------------

_DOC_TITLE_PREFIXES = ("story map", "thin slic", "acceptance criteria", "specification by example")


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


class _StepLines:
    """Writes the step lines of one section. Each step line stands where its step was read; a step
    unchanged on the model keeps its line, and steps added on the model follow the owner's last line."""

    def __init__(self, parts: list) -> None:
        self._pending: Dict[int, list] = {}
        self._left: Dict[int, int] = {}
        for part in parts:
            if isinstance(part, tuple) and part[0] == _STEP_LINE:
                self._left[id(part[1])] = self._left.get(id(part[1]), 0) + 1

    @staticmethod
    def steps_of(owner) -> list:
        pending = []
        for step in owner.steps:
            pending.append((step, False))
            pending.extend((extra, True) for extra in step.ands)
        return pending

    def write(self, part) -> str:
        if not (isinstance(part, tuple) and part[0] == _STEP_LINE):
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
        return f"{indent}*{step.keyword}* {MarkdownStep.prose(step)}  \n"


class MarkdownParseError(Exception):
    """Raised when a document is not a valid Markdown story map."""


class MarkdownStoryModel(StoryModel):
    """Markdown story-map I/O. render writes a story map as story-map.md text; parse reads that text into a new map.
    attach_source_locations stamps SourceLocation onto nodes after parsing.
    """

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
                parsed = type(self)().parse(text)
            except MarkdownParseError as err:
                raise MarkdownParseError(f"{md_path}: {err}") from err
            # Stamp before merging: a second file's headings would otherwise land on the first file's epics.
            parsed.attach_source_locations(text, rel)
            self.source_texts[rel] = text
            for epic in parsed.epics:
                self.epics.append(epic)
            if not self.has_source_file:
                self.source = SourceLocation(rel, 1)
        if not self.epics:
            return
        workspace = root.parent if root.is_file() else root
        self._attach_markdown(workspace, on_file=on_file)

    def _attach_markdown(self, root, on_file=None) -> None:
        scenarios = MarkdownScenario.from_workspace(root, on_file=on_file)
        for epic in self.epics:
            epic._load_scenarios(scenarios)
        if self.increments:
            return
        stories = {story.name: story for story in self.every_story()}
        for increment in MarkdownIncrement.from_workspace(root, stories):
            self.increments.append(increment)

    # -- Uniform Callable Surface ----------------------------------------------

    def save(self) -> str:
        return self.render(self)

    def render(
        self,
        story_map: "MarkdownStoryModel",
        previous: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> str:
        """Write the story map, copied into a markdown map when it is in another format. In a *workspace* folder,
        each story that has its own markdown file there links to it; a story with no file stays plain text."""
        if not isinstance(story_map, MarkdownStoryModel):
            story_map = type(self)(story_map)
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
        if previous and self._contains_outline_structure(previous.splitlines()):
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

    def parse(self, text: str) -> "MarkdownStoryModel":
        if not isinstance(text, str) or text.strip() == "":
            return MarkdownStoryModel()
        if not self._looks_like_scenario_document(text.splitlines()):
            text = unlink(text)
        lines = text.splitlines()
        if self._looks_like_scenario_document(lines):
            return self._parse_scenario_document(text)
        self._guard_has_structure(lines)
        if self._contains_outline_structure(lines):
            return self._parse_outline_lines(lines)
        return self._parse_lines(lines)

    def _looks_like_scenario_document(self, lines: List[str]) -> bool:
        if self._contains_outline_structure(lines):
            return False
        has_scenario = any(_SCENARIO_H3.match(line) for line in lines)
        has_clause = any(
            line.strip().startswith("*Given*")
            or line.strip().startswith("*When*")
            or line.strip().startswith("*Then*")
            for line in lines
        )
        return has_scenario and has_clause

    def _parse_scenario_document(self, text: str) -> "MarkdownStoryModel":
        """Stories with their backgrounds and scenarios. The document keeps every line in place,
        so rendering it writes it back; a heading or step changed on the model is written anew."""
        parser = MarkdownScenario()
        parser.parse_text(text, "story-scenarios.md")
        story_map = MarkdownStoryModel()
        level, name = (parser.tree_heading or ("sub-epic", "Scenarios"))[:2]
        epic = MarkdownEpic(name if level.lower() == "epic" else "Stories", 1)
        holder = epic if level.lower() == "epic" else MarkdownEpic(name, 1)
        if parser.document_examples is not None:
            holder.examples = parser.document_examples.clone(holder)
        parts = []
        for part in parser.document_parts:
            if isinstance(part, _StorySection):
                part = self._story_from_section(part, len(holder.stories) + 1)
                holder.stories.append(part)
            parts.append(part)
        if not holder.stories:
            return story_map
        if holder is not epic:
            epic.epics.append(holder)
        story_map.epics.append(epic)
        story_map.scenario_document = _ScenarioDocument(parts, holder, parser.tree_heading)
        return story_map

    def _story_from_section(self, section: _StorySection, order: int) -> MarkdownStory:
        story = MarkdownStory(section.name, order, StoryType.USER)
        if section.background.steps:
            story.backgrounds = [section.background]
        for scenario in section.scenarios:
            story.scenarios.append(scenario)
        story.markdown_heading = (section.name, section.heading)
        story.markdown_parts = section.parts
        return story

    def _render_scenario_document(self, document: "_ScenarioDocument") -> str:
        out: List[str] = []
        steps = _StepLines(document.parts)
        for part in document.parts:
            if part == _HEADING_LINE:
                out.append(document.heading_line())
            elif isinstance(part, MarkdownStory):
                if any(story is part for story in document.holder.stories):
                    out.append(self._render_story(part))
            else:
                out.append(steps.write(part))
        for story in document.holder.stories:
            if not any(story is part for part in document.parts):
                out.append(self._render_story(story))
        return "".join(out)

    def _render_story(self, story) -> str:
        parts = story.markdown_parts if isinstance(story, MarkdownStory) else None
        if parts is None:
            parts = [_HEADING_LINE, "\n"]
            for background in story.backgrounds:
                parts.extend(["### Background\n", "\n"])
                parts.extend((_STEP_LINE, background) for _ in _StepLines.steps_of(background))
                parts.append("\n")
        name, heading = story.markdown_heading if isinstance(story, MarkdownStory) and story.markdown_heading else ("", None)
        out: List[str] = []
        steps = _StepLines(parts)
        for part in parts:
            if part == _HEADING_LINE:
                out.append(heading if heading is not None and name == story.name else f"# Story: {story.name}\n")
            elif isinstance(part, Scenario):
                if any(scenario is part for scenario in story.scenarios):
                    out.append(self._render_scenario(part))
            else:
                out.append(steps.write(part))
        for scenario in story.scenarios:
            if not any(scenario is part for part in parts):
                out.append(self._render_scenario(scenario))
        return "".join(out)

    def _render_scenario(self, scenario) -> str:
        parts = scenario.markdown_parts if isinstance(scenario, MarkdownScenario) else None
        if parts is None:
            parts = [_HEADING_LINE, "\n"]
            parts.extend((_STEP_LINE, scenario) for _ in _StepLines.steps_of(scenario))
            parts.append("\n")
        read = scenario.markdown_heading if isinstance(scenario, MarkdownScenario) else None
        name, is_outline, heading = read or ("", False, None)
        out: List[str] = []
        steps = _StepLines(parts)
        for part in parts:
            if part != _HEADING_LINE:
                out.append(steps.write(part))
            elif heading is not None and (name, is_outline) == (scenario.name, scenario.is_outline):
                out.append(heading)
            else:
                marks = heading.split(" ", 1)[0] if heading else "####"
                kind = "Scenario Outline" if scenario.is_outline else "Scenario"
                out.append(f"{marks} {kind}: {scenario.name}\n")
        return "".join(out)

    # -- Source location stamping ----------------------------------------------

    def attach_source_locations(self, text: str, rel_file: str) -> None:
        """Stamp SourceLocation onto each Epic/Epic/Story from the markdown text."""
        lines = unlink(text).splitlines()
        is_outline = any(
            _OUTLINE_EPIC_PATTERN.match(l) or _OUTLINE_STORY_PATTERN.match(l) for l in lines
        )
        epic_index = 0
        for i, raw in enumerate(lines, start=1):
            if not raw.strip():
                continue
            m_epic_out = _OUTLINE_EPIC_PATTERN.match(raw)
            m_story_out = _OUTLINE_STORY_PATTERN.match(raw)
            m_heading = _HEADING_PATTERN.match(raw)
            m_bullet = _BULLET_PATTERN.match(raw)

            if m_epic_out:
                indent = _outline_depth(m_epic_out)
                name = strip_backticks(m_epic_out.group("name"))
                if indent == 0:
                    if epic_index < len(self.epics):
                        self.epics[epic_index].source = SourceLocation(rel_file, i)
                        epic_index += 1
                else:
                    self._stamp_sub_epic(name, SourceLocation(rel_file, i))
                continue
            if m_story_out:
                story_text = m_story_out.group("name")
                name = strip_backticks(story_text.split("-->", 1)[-1] if "-->" in story_text else story_text)
                self._stamp_story(name, SourceLocation(rel_file, i))
                continue
            if is_outline:
                continue
            if m_heading:
                depth = len(m_heading.group(1))
                name = m_heading.group(2).strip()
                if any(name.lower().startswith(p) for p in _DOC_TITLE_PREFIXES):
                    continue
                if depth == 1 and epic_index < len(self.epics):
                    self.epics[epic_index].source = SourceLocation(rel_file, i)
                    epic_index += 1
                elif depth >= 2:
                    self._stamp_sub_epic(name, SourceLocation(rel_file, i))
                continue
            if m_bullet:
                self._stamp_story(m_bullet.group(2).strip(), SourceLocation(rel_file, i))

    def _stamp_sub_epic(self, name: str, loc: SourceLocation) -> None:
        for epic in self.epics:
            if epic._stamp_epic(name, loc):
                return

    def _stamp_story(self, name: str, loc: SourceLocation) -> None:
        for epic in self.epics:
            if epic._stamp_story(name, loc):
                return

    # -- parse helpers ---------------------------------------------------------

    def _guard_has_structure(self, lines: List[str]) -> None:
        for line in lines:
            if (
                _HEADING_PATTERN.match(line) or _BULLET_PATTERN.match(line)
                or _OUTLINE_EPIC_PATTERN.match(line) or _OUTLINE_STORY_PATTERN.match(line)
                or _OUTLINE_ESTIMATE_PATTERN.match(line)
            ):
                return
        raise MarkdownParseError("Not a valid Markdown story map: no recognised structure found")

    def _contains_outline_structure(self, lines: List[str]) -> bool:
        return any(
            _OUTLINE_EPIC_PATTERN.match(l) or _OUTLINE_STORY_PATTERN.match(l)
            for l in lines
        )

    def _parse_lines(self, lines: List[str]) -> "MarkdownStoryModel":
        self._story_map = MarkdownStoryModel()
        self._current_epic: Optional[MarkdownEpic] = None
        self._sub_epic_stack: List[MarkdownEpic] = []
        self._current_story: Optional[MarkdownStory] = None
        self._epic_heading_depth: Optional[int] = None
        self._ignored_heading_depth: Optional[int] = None
        for raw in lines:
            if not raw.strip():
                continue
            self._raw_line = raw
            if self._skip_ignored_section():
                continue
            if self._accept_map_heading():
                continue
            if self._accept_map_bullet():
                continue
            if self._accept_map_numbered():
                continue
        return self._story_map

    def _skip_ignored_section(self) -> bool:
        heading = _HEADING_PATTERN.match(self._raw_line)
        if self._ignored_heading_depth is None:
            return False
        if heading is None:
            return True
        if len(heading.group(1)) > self._ignored_heading_depth:
            return True
        self._ignored_heading_depth = None
        return False

    def _accept_map_heading(self) -> bool:
        heading = _HEADING_PATTERN.match(self._raw_line)
        if heading is None:
            return False
        depth = len(heading.group(1))
        name = heading.group(2).strip()
        if self._is_document_title(name):
            return True
        if self._is_non_story_section_heading(name):
            self._ignored_heading_depth = depth
            return True
        if name.lower().startswith("story:"):
            self._append_named_story(name.split(":", 1)[1].strip() or name)
            return True
        if self._is_epic_heading(depth):
            self._begin_epic(name, depth)
            return True
        if self._current_epic is not None:
            self._accept_nested_heading(name, depth)
        return True

    def _is_epic_heading(self, depth: int) -> bool:
        if self._current_epic is None:
            return True
        if depth == 1:
            return True
        if self._epic_heading_depth is not None and depth <= self._epic_heading_depth:
            return True
        return False

    def _begin_epic(self, name: str, depth: int) -> None:
        if self._epic_heading_depth is None:
            self._epic_heading_depth = depth
        self._current_epic = MarkdownEpic(name, len(self._story_map.epics) + 1)
        self._story_map.epics.append(self._current_epic)
        self._sub_epic_stack = []
        self._current_story = None

    def _accept_nested_heading(self, name: str, depth: int) -> None:
        if self._epic_heading_depth is None:
            self._epic_heading_depth = 1
        relative_depth = max(depth - self._epic_heading_depth, 1)
        if relative_depth >= 2:
            self._append_named_story(name)
            return
        while len(self._sub_epic_stack) >= relative_depth:
            self._sub_epic_stack.pop()
        parent_children = (
            self._sub_epic_stack[-1].epics
            if self._sub_epic_stack
            else self._current_epic.epics
        )
        sub = MarkdownEpic(name, len(parent_children) + 1)
        parent_children.append(sub)
        self._sub_epic_stack.append(sub)
        self._current_story = None

    def _append_named_story(self, story_name: str) -> None:
        parent = self._ensure_sub_epic()
        self._current_story = MarkdownStory(story_name, len(parent.stories) + 1, StoryType.USER)
        parent.stories.append(self._current_story)

    def _accept_map_bullet(self) -> bool:
        bullet = _BULLET_PATTERN.match(self._raw_line)
        if bullet is None:
            return False
        indent = len(bullet.group(1)) // 2
        text = bullet.group(2).strip()
        if indent == 0 and self._current_epic is not None:
            self._append_named_story(text)
            return True
        if indent >= 1 and self._current_story is not None:
            self._current_story.scenarios.append(
                MarkdownScenario(text, len(self._current_story.scenarios) + 1, self._current_story.name)
            )
        return True

    def _accept_map_numbered(self) -> bool:
        numbered = _NUMBERED_PATTERN.match(self._raw_line)
        if numbered is None or self._current_story is None:
            return False
        text = numbered.group(2).strip()
        text = re.sub(r"^\*\*(WHEN|THEN|AND|BUT)\*\*\s*", "", text, flags=re.IGNORECASE)
        self._current_story.scenarios.append(
            MarkdownScenario(text, len(self._current_story.scenarios) + 1, self._current_story.name)
        )
        return True

    def _is_document_title(self, name: str) -> bool:
        lower = name.lower()
        return any(lower.startswith(p) for p in _DOC_TITLE_PREFIXES)

    def _is_non_story_section_heading(self, name: str) -> bool:
        return name.lower() in {"context gaps", "validation results"}

    def _ensure_sub_epic(self) -> MarkdownEpic:
        if self._sub_epic_stack:
            return self._sub_epic_stack[-1]
        if self._current_epic is None:
            self._current_epic = MarkdownEpic("Imported", len(self._story_map.epics) + 1)
            self._story_map.epics.append(self._current_epic)
        sub = MarkdownEpic(self._current_epic.name, len(self._current_epic.epics) + 1)
        self._current_epic.epics.append(sub)
        self._sub_epic_stack.append(sub)
        return sub

    def _parse_outline_lines(self, lines: List[str]) -> "MarkdownStoryModel":
        self._story_map = MarkdownStoryModel()
        self._current_epic = None
        self._sub_epic_stack = []
        self._current_outline_story: Optional[MarkdownStory] = None
        for raw in lines:
            if not raw.strip():
                continue
            self._raw_line = raw
            if self._accept_outline_epic():
                continue
            if self._accept_outline_story():
                continue
            if self._accept_outline_estimate():
                continue
            self._accept_outline_evidence()
        return self._story_map

    def _accept_outline_epic(self) -> bool:
        match = _OUTLINE_EPIC_PATTERN.match(self._raw_line)
        if match is None:
            return False
        indent = _outline_depth(match)
        name = strip_backticks(match.group("name"))
        self._current_outline_story = None
        if indent <= 0:
            self._current_epic = MarkdownEpic(name, len(self._story_map.epics) + 1)
            self._story_map.epics.append(self._current_epic)
            self._sub_epic_stack = []
            return True
        if self._current_epic is None:
            return True
        while len(self._sub_epic_stack) >= indent:
            self._sub_epic_stack.pop()
        parent_children = (
            self._sub_epic_stack[-1].epics
            if self._sub_epic_stack
            else self._current_epic.epics
        )
        sub = MarkdownEpic(name, len(parent_children) + 1)
        parent_children.append(sub)
        self._sub_epic_stack.append(sub)
        return True

    def _accept_outline_story(self) -> bool:
        match = _OUTLINE_STORY_PATTERN.match(self._raw_line)
        if match is None or self._current_epic is None:
            return False
        parent_depth = _outline_depth(match) - 1
        if match.group("marks") or parent_depth <= 0:
            while len(self._sub_epic_stack) > max(parent_depth, 0):
                self._sub_epic_stack.pop()
        parent = self._sub_epic_stack[-1] if self._sub_epic_stack else self._current_epic
        actor, story_name = self._split_outline_story(match.group("name"))
        story = MarkdownStory(story_name, len(parent.stories) + 1, StoryType.from_mark(match.group("kind")))
        if actor:
            story.actors = [actor]
        parent.stories.append(story)
        self._current_outline_story = story
        return True

    def _accept_outline_evidence(self) -> None:
        """Record the Observed, Inferred, or Intended labels written in the lines under a story heading."""
        if self._current_outline_story is None:
            return
        evidence = self._current_outline_story.evidence
        for label in (with_evidence or ending for with_evidence, ending in _EVIDENCE_LABEL.findall(self._raw_line)):
            if label.lower() not in evidence:
                evidence.append(label.lower())

    def _split_outline_story(self, raw_text: str) -> tuple[str, str]:
        if "-->" not in raw_text:
            return "", strip_backticks(raw_text)
        actor_part, story_part = raw_text.split("-->", 1)
        return strip_backticks(actor_part), strip_backticks(story_part)

    def _accept_outline_estimate(self) -> bool:
        match = _OUTLINE_ESTIMATE_PATTERN.match(self._raw_line)
        if match is None:
            return False
        estimate = match.group(2).strip()
        if self._sub_epic_stack:
            self._sub_epic_stack[-1].estimate = estimate
            return True
        if self._current_epic is not None:
            self._current_epic.estimate = estimate
        return True
