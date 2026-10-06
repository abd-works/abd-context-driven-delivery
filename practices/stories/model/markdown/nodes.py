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

from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Background, StepType, Scenario, Step
from practices.stories.model.source_location import SourceLocation
from practices.stories.model.story_model import StoryModel
from practices.stories.model.story_model import Increment
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_PATTERN = re.compile(r"^(\s*)-\s+(.+)$")
_NUMBERED_PATTERN = re.compile(r"^(\s*)\d+\.\s+(.+)$")
_OUTLINE_EPIC_PATTERN = re.compile(r"^(\s*)\(E\)\s+(.+)$")
_OUTLINE_STORY_PATTERN = re.compile(r"^(\s*)\(S\)\s+(.+)$")
_OUTLINE_ESTIMATE_PATTERN = re.compile(r"^(\s*)\*\s+(\S.+)$")


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
    def from_workspace(cls, root: "Path") -> List["MarkdownIncrement"]:
        """Find thin-slicing markdown in *root* and return parsed increments."""
        root = Path(root).resolve()
        if root.is_file():
            return []
        for name in ("thin-slicing.md", "thin-slice.md", "thin-slices.md", "increments.md"):
            candidate = root / name
            if candidate.exists():
                rel = str(candidate.relative_to(root)).replace("\\", "/")
                return cls.parse(candidate.read_text(encoding="utf-8"), rel)
            for found in root.rglob(name):
                rel = str(found.relative_to(root)).replace("\\", "/")
                return cls.parse(found.read_text(encoding="utf-8"), rel)
        return []

    @classmethod
    def parse(cls, text: str, rel_file: str, line_offset: int = 0) -> List["MarkdownIncrement"]:
        """Parse a thin-slicing.md body into a list of MarkdownIncrement nodes."""
        increments: List[MarkdownIncrement] = []
        current: Optional[MarkdownIncrement] = None
        in_stories = False

        for idx, raw in enumerate(text.splitlines(), start=1 + line_offset):
            stripped = raw.strip()
            if not stripped:
                continue
            m_inc = _INCREMENT_H3.match(stripped)
            if m_inc:
                if current is not None:
                    increments.append(current)
                current = cls(MarkdownScenario()._strip_markup(m_inc.group(1)), len(increments) + 1)
                current.source = SourceLocation(rel_file, idx)
                in_stories = False
                continue
            if current is None:
                continue
            markup = MarkdownScenario()
            if m := _KV_OUTCOME.match(stripped):
                current.outcome = markup._strip_markup(m.group(1))
                in_stories = False
            elif m := _KV_SLICING.match(stripped):
                current.slicing_notes = markup._strip_markup(m.group(1))
                in_stories = False
            elif m := _KV_DECISION.match(stripped):
                current.decision_prompt = markup._strip_markup(m.group(1))
                in_stories = False
            elif _KV_STORIES.match(stripped):
                in_stories = True
            elif _ANY_H2.match(raw) or _INCREMENT_H3.match(raw):
                in_stories = False
            elif in_stories:
                if m := _BULLET.match(raw):
                    current.stories.append(markup._strip_markup(m.group(1)))
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
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_H1 = re.compile(r"^#\s+(.+)$")


class MarkdownStep(Step):
    """Step whose text may still carry a markdown And or But prefix."""

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

    @classmethod
    def from_workspace(cls, root: "Path") -> List["MarkdownScenario"]:
        """Find all scenario markdown files under *root* and return parsed scenarios."""
        root = Path(root).resolve()
        if root.is_file():
            return cls.parse_file(root, root.name)
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
        self._parse_document_lines()
        self._flush_current()
        return self._scenarios

    def _parse_document_lines(self) -> None:
        for i, raw in enumerate(self._lines, start=1):
            if not raw.strip():
                if self._in_background and self._background_took_step:
                    self._in_background = False
                continue
            self._line_index = i
            self._raw_line = raw
            if self._accept_story_heading():
                continue
            if self._accept_scenario_heading():
                continue
            if self._accept_section_heading():
                continue
            if self._accept_step_line():
                continue
            self._accept_example_row()

    def _accept_story_heading(self) -> bool:
        match = _STORY_H2.match(self._raw_line)
        if match is None:
            return False
        self._flush_current()
        self._story_name = self._strip_markup(match.group(1))
        self._shared_background = Background("background", 1)
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
            name=self._strip_markup(match.group(1)),
            story_name=self._story_name,
        )
        self._current.is_outline = "outline" in self._raw_line.lower()
        self._current.source = SourceLocation(self._rel, self._line_index)
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
        if self._in_examples and not self._is_reserved_heading():
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

    def _begin_examples(self) -> bool:
        self._in_examples = True
        self._in_background = False
        self._example_headers = []
        self._example_group = ""
        return True

    def _begin_example_group(self) -> bool:
        heading = _HEADING_PATTERN.match(self._raw_line)
        self._example_group = self._strip_markup(heading.group(2)) if heading else ""
        self._example_headers = []
        return True

    def _is_reserved_heading(self) -> bool:
        return bool(
            _SCENARIO_H3.match(self._raw_line)
            or _STORY_H2.match(self._raw_line)
            or _BACKGROUND_H3.match(self._raw_line)
        )

    def _accept_step_line(self) -> bool:
        parsed_step = self._parse_step(self._raw_line)
        if parsed_step is None:
            return False
        keyword, step_text = parsed_step
        self._clause_source = SourceLocation(self._rel, self._line_index)
        if self._in_story_background:
            self._consume_story_background(keyword, step_text)
            return True
        if self._in_background and keyword.lower() in ("when", "then"):
            self._in_background = False
        if self._in_background:
            self._consume_background(keyword, step_text)
        elif self._current is not None:
            self._accept_step(keyword, step_text)
        return True

    def _accept_example_row(self) -> None:
        if not self._in_examples:
            return
        row_match = _TABLE_ROW.match(self._raw_line)
        if row_match is None:
            return
        cells = [c.strip() for c in row_match.group(1).split("|")]
        if not self._example_headers:
            if not all(re.fullmatch(r"-+|:-+:?|:?-+:?", c) for c in cells):
                self._example_headers = [self._strip_markup(c) for c in cells]
            return
        if all(set(c.strip(":")) <= {"-"} for c in cells):
            return
        row = dict(zip(self._example_headers, (self._strip_markup(c) for c in cells)))
        if set(row) <= {"example", "group"} and row.get("example"):
            row = {"example": row["example"]}
        self._record_example_row(row)

    def _record_example_row(self, row: dict) -> None:
        if self._example_group:
            row.setdefault("group", self._example_group)
        if self._current is not None:
            index = len(self._current.examples) + 1
            label = str(row.get("example") or row.get("name") or f"example-{index}")
            self._current.examples[label] = row["example"] if set(row) <= {"example"} else row
            return
        index = len(self._shared_background.examples) + 1
        label = str(row.get("example") or row.get("name") or self._example_group or f"example-{index}")
        self._shared_background.examples[label] = row["example"] if set(row) <= {"example"} else row

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

    def strip_backticks(self, text: str) -> str:
        s = text.strip()
        while s.startswith("`") and s.endswith("`") and len(s) >= 2:
            s = s[1:-1].strip()
        return s

    def _strip_markup(self, text: str) -> str:
        s = self.strip_backticks(text)
        while s.startswith("*") and s.endswith("*") and len(s) >= 2:
            s = self.strip_backticks(s[1:-1].strip())
        return self.strip_backticks(s)

    def _parse_step(self, raw: str) -> Optional[tuple[str, str]]:
        match = _ITALIC_STEP.match(raw) or _BULLET_STEP.match(raw)
        if match is None:
            return None
        return (match.group(1), match.group(2).strip())

    def make_step(self, text: str, phase: StepType, sequential_order: int) -> MarkdownStep:
        match = _BOLD_TERM.search(text)
        return MarkdownStep(
            text=text,
            step_type=phase,
            sequential_order=sequential_order,
            keyword=self._clause_keyword,
            concepts=_BOLD_TERM.findall(text),
            values=[v.strip("`").strip() for v in _ITALIC_VALUE.findall(text) if v],
            actor=match.group(1).strip() if match else "",
            source=self._clause_source,
        )

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

    @classmethod
    def render_scenarios(cls, scenarios: List["MarkdownScenario"], *, story_name: str = "", story_backgrounds=None) -> str:
        """Emit markdown matching scenario templates (GWT + examples tables)."""
        lines: List[str] = []
        if story_name:
            lines.append(f"## Story: {story_name}")
            lines.append("")
        lines.extend(cls._render_example_tables(cls._shared_examples(scenarios)))
        for background in story_backgrounds or []:
            if not background.steps:
                continue
            lines.append(f"### Story Background: {background.name}")
            lines.append("")
            for step in background.steps:
                lines.extend(cls._step_lines(step))
            lines.append("")
        for sc in scenarios:
            kind = "Scenario Outline" if getattr(sc, "is_outline", False) else "Scenario"
            lines.append(f"### {kind}: {sc.name}")
            lines.append("")
            for background in sc.backgrounds:
                if not background.steps:
                    continue
                lines.append("### Background")
                lines.append("")
                for step in background.steps:
                    lines.extend(cls._step_lines(step))
                lines.append("")
            for step in sc.steps_in(StepType.GIVEN):
                lines.extend(cls._step_lines(step))
            for when_steps, then_steps in sc.when_then_runs():
                for step in when_steps:
                    lines.extend(cls._step_lines(step))
                for step in then_steps:
                    lines.extend(cls._step_lines(step))
            rows = sc.examples.table()
            if rows:
                lines.append("")
                lines.append("### Examples")
                lines.append("")
                headers = list(rows[0].keys())
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join("---" for _ in headers) + " |")
                for row in rows:
                    lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    @classmethod
    def _shared_examples(cls, scenarios: List["MarkdownScenario"]):
        for scenario in scenarios:
            for background in scenario.backgrounds:
                if background.examples:
                    return background.examples
        return {}

    @classmethod
    def _render_example_tables(cls, examples) -> List[str]:
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
            slot = index.get(key)
            if slot is None:
                index[key] = len(buckets)
                buckets.append((group, headers, []))
                slot = index[key]
            buckets[slot][2].append(cells)
        lines = ["### Examples", ""]
        for group, headers, rows in buckets:
            if group:
                lines.append(f"#### {group}")
                lines.append("")
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for cells in rows:
                values = [str(cells.get(header, "")).replace("|", "/") for header in headers]
                lines.append("| " + " | ".join(values) + " |")
            lines.append("")
        return lines

    @classmethod
    def _step_lines(cls, step: Step) -> List[str]:
        lines = [f"*{step.keyword}* {MarkdownStep.prose(step)}"]
        for extra in step.ands:
            lines.append(f"*{extra.keyword}* {MarkdownStep.prose(extra)}")
        return lines

    def _infer_story_name(self) -> str:
        for line in self._lines[:20]:
            match = _STORY_H2.match(line)
            if match:
                return self._strip_markup(match.group(1))
        for line in self._lines[:5]:
            match = _H1.match(line)
            if match:
                return self._strip_markup(match.group(1))
        parts = self._path.parts
        if len(parts) >= 2 and parts[-2] == "scenarios":
            return parts[-3].replace("-", " ") if len(parts) >= 3 else ""
        return self._path.stem.replace("-", " ")


# -- Leaf node types -----------------------------------------------------------

class MarkdownStory(Story):
    def load_scenario(self, source: Scenario) -> MarkdownScenario:
        return MarkdownScenario(source.name, source.sequential_order, source.story_name)

    def load_scenarios(self, root) -> None:
        name = self.name.strip()
        took_examples = False
        seen = set()
        for scenario in MarkdownScenario.from_workspace(root):
            if (scenario.story_name or "").strip() != name:
                continue
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
            carried = getattr(scenario, "story_backgrounds", None)
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
    def load_epic(self, source: Epic) -> "MarkdownEpic":
        return MarkdownEpic(source.name, source.sequential_order)

    def load_story(self, source: Story) -> MarkdownStory:
        return MarkdownStory(source.name, source.sequential_order, source.story_type)

    def _load_scenarios(self, root) -> None:
        for child in self.epics:
            child._load_scenarios(root)
        for story in self.stories:
            story.load_scenarios(root)


# -- Root node + I/O -----------------------------------------------------------

_DOC_TITLE_PREFIXES = ("story map", "thin slic", "acceptance criteria", "specification by example")
_OUTLINE_EPIC_RE = re.compile(r"^(\s*)\(E\)\s+(.+)$")
_OUTLINE_STORY_RE = re.compile(r"^(\s*)\(S\)\s+(.+)$")
_OUTLINE_ESTIMATE_RE = re.compile(r"^(\s*)\*\s+(\S.+)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_RE = re.compile(r"^(\s*)-\s+(.+)$")


class MarkdownParseError(Exception):
    """Raised when a document is not a valid Markdown story map."""


class MarkdownStoryModel(StoryModel):
    epic_type = MarkdownEpic
    story_type = MarkdownStory
    """Markdown story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    attach_source_locations stamps SourceLocation onto nodes after parsing.
    """

    def load_epic(self, source: MarkdownEpic) -> MarkdownEpic:
        return MarkdownEpic(source.name, source.sequential_order)

    def load_increment(self, source: Increment) -> MarkdownIncrement:
        return MarkdownIncrement(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: "Path") -> Optional["MarkdownStoryModel"]:
        """Find story-map.md files under *root*, merge, and return; None if absent."""
        root = Path(root).resolve()
        if root.is_file():
            candidates = [root]
        else:
            candidates = (
                [root / "story-map.md"] if (root / "story-map.md").exists()
                else list(root.rglob("story-map.md"))
            )
        if not candidates:
            return None
        merged = cls()
        for md_path in candidates:
            text = md_path.read_text(encoding="utf-8")
            try:
                parsed = cls().parse(text)
            except MarkdownParseError:
                continue
            for epic in parsed.epics:
                merged.epics.append(epic)
            if root.is_file():
                rel = root.name
            else:
                rel = str(md_path.relative_to(root)).replace("\\", "/")
            merged.attach_source_locations(text, rel)
            if not getattr(merged, "source", None):
                from practices.stories.model.source_location import SourceLocation as _SL
                merged.source = _SL(rel, 1)
        if not merged.epics:
            return None
        workspace = root.parent if root.is_file() else root
        merged._attach_markdown(workspace)
        return merged

    def _attach_markdown(self, root) -> None:
        for epic in self.epics:
            epic._load_scenarios(root)
        if self.increments:
            return
        for increment in MarkdownIncrement.from_workspace(root):
            self.increments.append(increment)

    # -- Uniform Callable Surface ----------------------------------------------

    def save(self) -> str:
        return self.render(self)

    def render(self, story_map: "MarkdownStoryModel", previous: Optional[str] = None) -> str:
        if self._should_render_outline(story_map, previous) or self._is_discovery_story_map(
            story_map
        ):
            body = self._render_outline(story_map)
            if self._is_discovery_story_map(story_map):
                return self._wrap_story_map_document(body, previous)
            return body
        lines: List[str] = []
        for epic in story_map.epics:
            self._render_epic(epic, lines, depth=1)
        return "\n".join(lines)

    def _should_render_outline(self, story_map: "MarkdownStoryModel", previous: Optional[str]) -> bool:
        """Outline notation is for documents already written that way, or that carry
        estimates. Nesting on its own renders as deeper headings."""
        if previous and self._contains_outline_structure(previous.splitlines()):
            return True
        return any(
            self._sub_tree_has_outline_signal(epic) for epic in story_map.epics
        )

    def _sub_tree_has_outline_signal(self, sub: MarkdownEpic) -> bool:
        if getattr(sub, "estimate", ""):
            return True
        for nested in sub.epics:
            if self._sub_tree_has_outline_signal(nested):
                return True
        return False

    def strip_backticks(self, text: str) -> str:
        return MarkdownScenario().strip_backticks(text)

    def _is_discovery_story_map(self, story_map: "MarkdownStoryModel") -> bool:
        return not self._tree_has_scenarios(story_map)

    def _tree_has_scenarios(self, epic_or_map) -> bool:
        epics = epic_or_map.epics if hasattr(epic_or_map, "epics") else []
        stories = epic_or_map.stories if hasattr(epic_or_map, "stories") else []
        for story in stories:
            if story.scenarios or story.backgrounds:
                return True
        for epic in epics:
            if self._tree_has_scenarios(epic):
                return True
        return False

    def _wrap_story_map_document(self, body: str, previous: Optional[str]) -> str:
        title, sources = self._sketch_metadata(previous or "")
        return "\n".join(
            [
                "---",
                "fidelity: [discovery]",
                "artifact: [story-map]",
                "format: md",
                "---",
                "",
                f"# Story Map — {title}",
                "",
                f"**Sources / context:** {sources}",
                "",
                "---",
                "",
                body.rstrip(),
                "",
                "---",
                "",
                "## Scope boundary",
                "",
                "**In scope:** see sketch increments and detailed themes",
                "**Out of scope:** themes not yet moved to specification",
                "",
            ]
        )

    def _sketch_metadata(self, text: str) -> tuple[str, str]:
        title = "Product / Feature Name"
        sources = "see engagement sketch"
        sketch_suffix = re.compile(r"\s+sketch\s*$", re.IGNORECASE)
        trailing_separator = re.compile(r"[\s\-–—\u20ac\u201d]+$")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                raw = stripped[2:].strip()
                title = sketch_suffix.sub("", raw).strip()
                title = trailing_separator.sub("", title).strip() or title
            if stripped.lower().startswith("source:"):
                sources = stripped.split(":", 1)[1].strip()
            if stripped.lower().startswith("## stories:"):
                break
        return title, sources

    def _render_outline(self, story_map: "MarkdownStoryModel") -> str:
        self._outline_lines: List[str] = []
        self._outline_indent = 4
        for epic in story_map.epics:
            self._outline_lines.append(f"(E) {self.strip_backticks(epic.name)}")
            if getattr(epic, "estimate", ""):
                self._outline_lines.append(f"    * {epic.estimate}")
            self._render_outline_stories(epic, "    ")
            self._render_outline_epics(epic.epics)
        return "\n".join(self._outline_lines)

    def _render_outline_epics(self, subs: List[MarkdownEpic]) -> None:
        pad = " " * self._outline_indent
        story_pad = " " * (self._outline_indent + 4)
        for sub in subs:
            self._outline_lines.append(f"{pad}(E) {self.strip_backticks(sub.name)}")
            self._render_outline_stories(sub, story_pad)
            if getattr(sub, "estimate", ""):
                self._outline_lines.append(f"{story_pad}* {sub.estimate}")
            self._outline_indent += 4
            self._render_outline_epics(sub.epics)
            self._outline_indent -= 4

    def _render_outline_stories(self, sub: MarkdownEpic, story_pad: str) -> None:
        for story in sub.stories:
            actor = story.actors[0] if story.actors else ""
            name = self.strip_backticks(story.name)
            if actor:
                actor_name = self.strip_backticks(actor)
                self._outline_lines.append(f"{story_pad}(S) {actor_name} --> {name}")
                continue
            self._outline_lines.append(f"{story_pad}(S) --> {name}")

    def parse(self, text: str) -> "MarkdownStoryModel":
        if not isinstance(text, str) or text.strip() == "":
            return MarkdownStoryModel()
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
        scenarios = MarkdownScenario.from_text(text, "story-scenarios.md")
        story_map = MarkdownStoryModel()
        stories: dict[str, MarkdownStory] = {}
        epic = MarkdownEpic("Stories", 1)
        sub = MarkdownEpic("Scenarios", 1)
        for scenario in scenarios:
            name = (scenario.story_name or "Story").strip()
            story = stories.get(name)
            if story is None:
                story = MarkdownStory(name, len(stories) + 1, StoryType.USER)
                stories[name] = story
                sub.stories.append(story)
            story.scenarios.append(scenario)
        if stories:
            epic.epics.append(sub)
            story_map.epics.append(epic)
        return story_map

    # -- Source location stamping ----------------------------------------------

    def attach_source_locations(self, text: str, rel_file: str) -> None:
        """Stamp SourceLocation onto each Epic/Epic/Story from the markdown text."""
        lines = text.splitlines()
        is_outline = any(
            _OUTLINE_EPIC_RE.match(l) or _OUTLINE_STORY_RE.match(l) for l in lines
        )
        epic_index = 0
        for i, raw in enumerate(lines, start=1):
            if not raw.strip():
                continue
            m_epic_out = _OUTLINE_EPIC_RE.match(raw)
            m_story_out = _OUTLINE_STORY_RE.match(raw)
            m_heading = _HEADING_RE.match(raw)
            m_bullet = _BULLET_RE.match(raw)

            if m_epic_out:
                indent = len(m_epic_out.group(1)) // 4
                name = self.strip_backticks(m_epic_out.group(2))
                if indent == 0:
                    if epic_index < len(self.epics):
                        self.epics[epic_index].source = SourceLocation(rel_file, i)
                        epic_index += 1
                else:
                    self._stamp_sub_epic(name, SourceLocation(rel_file, i))
                continue
            if m_story_out:
                name = self.strip_backticks(m_story_out.group(2).split("-->", 1)[-1] if "-->" in m_story_out.group(2) else m_story_out.group(2))
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

    # -- render helpers --------------------------------------------------------

    def _render_epic(self, epic: MarkdownEpic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {epic.name}")
        for sub in epic.epics:
            self._render_sub_epic(sub, lines, depth + 1)

    def _render_sub_epic(self, sub: MarkdownEpic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {sub.name}")
        for nested in sub.epics:
            self._render_sub_epic(nested, lines, depth + 1)
        for story in sub.stories:
            lines.append(f"- {story.name}")
            for scenario in story.scenarios:
                lines.append(f"  - {scenario.name}")

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
        return self._story_map

    def _accept_outline_epic(self) -> bool:
        match = _OUTLINE_EPIC_PATTERN.match(self._raw_line)
        if match is None:
            return False
        indent = len(match.group(1)) // 4
        name = self.strip_backticks(match.group(2))
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
        if not self._sub_epic_stack:
            self._ensure_sub_epic()
        actor, story_name = self._split_outline_story(match.group(2))
        story = MarkdownStory(story_name, len(self._sub_epic_stack[-1].stories) + 1, StoryType.USER)
        if actor:
            story.actors = [actor]
        self._sub_epic_stack[-1].stories.append(story)
        return True

    def _split_outline_story(self, raw_text: str) -> tuple[str, str]:
        if "-->" not in raw_text:
            return "", self.strip_backticks(raw_text)
        actor_part, story_part = raw_text.split("-->", 1)
        return self.strip_backticks(actor_part), self.strip_backticks(story_part)

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
