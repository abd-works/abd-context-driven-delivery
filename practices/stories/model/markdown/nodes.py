"""Markdown format story nodes - all seven StoryNode subtypes plus I/O.

Layout produced:

    # Epic 1
    ## SubEpic 1
    - Story 1
    - Story 2
    ## SubEpic 2
    # Epic 2
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from practices.stories.model.markdown.example_factories import (
    parse_md_factory_line,
    render_md_factory_line,
)
from practices.stories.model.example import Example
from practices.stories.model.nodes import Epic, Story, StoryType, SubEpic
from practices.stories.model.scenario import Clause, Interaction, Phase, Scenario
from practices.stories.model.source_location import SourceLocation
from practices.stories.model.story_map import StoryMap
from practices.stories.model.thin_slice import Increment
from practices.stories.model.update_report import UpdateReport

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
_STORY_H2 = re.compile(r"^#+\s+Story\s*[:\-]?\s*(.+?)\s*$", re.IGNORECASE)
_BACKGROUND_H3 = re.compile(r"^#+\s+Background\b", re.IGNORECASE)
_EXAMPLES_H3 = re.compile(r"^#+\s+Examples\b", re.IGNORECASE)
_ITALIC_STEP = re.compile(r"^\s*\*(Given|When|Then|And|But)\*\s+(.+?)\s*$", re.IGNORECASE)
_BULLET_STEP = re.compile(r"^\s*[-*]\s+(Given|When|Then|And|But)\b\s*(.+?)\s*$", re.IGNORECASE)
_BOLD_TERM = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_VALUE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_H1 = re.compile(r"^#\s+(.+)$")


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
            "**/md/*.md", "**/md/**/*.md", "**/*_story.test.md", "**/story-scenarios.md", "**/stories/**/*.md",
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
        self._background: List[Clause] = []
        self._scenarios: List[MarkdownScenario] = []
        self._builder: Optional[_ScenarioBuilder] = None
        self._in_background = False
        self._in_examples = False
        self._example_headers: List[str] = []
        self._example_group = ""
        self._story_examples: List[Example] = []
        self._background_phase: Optional[Phase] = None
        self._clause_source: Optional[SourceLocation] = None
        self._clause_is_continuation = False
        self._clause_keyword = ""
        self._parse_document_lines()
        self._flush_builder()
        self._attach_story_examples()
        return self._scenarios

    def _parse_document_lines(self) -> None:
        for i, raw in enumerate(self._lines, start=1):
            if not raw.strip():
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
        self._flush_builder()
        self._attach_story_examples()
        self._story_name = self._strip_markup(match.group(1))
        self._background = []
        self._story_examples = []
        self._example_group = ""
        self._in_background = False
        self._in_examples = False
        return True

    def _accept_scenario_heading(self) -> bool:
        match = _SCENARIO_H3.match(self._raw_line)
        if match is None:
            return False
        self._flush_builder()
        self._builder = _ScenarioBuilder(
            self,
            self._strip_markup(match.group(1)),
            self._story_name,
            is_outline="outline" in self._raw_line.lower(),
            source=SourceLocation(self._rel, self._line_index),
        )
        self._in_background = False
        self._in_examples = False
        return True

    def _accept_section_heading(self) -> bool:
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
        self._background_phase = None
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
        if self._in_background:
            self._consume_background(keyword, step_text)
        elif self._builder:
            self._builder.accept(keyword, step_text)
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
        self._record_example_row(row)

    def _record_example_row(self, row: dict) -> None:
        if self._example_group:
            row.setdefault("group", self._example_group)
        if self._builder:
            self._builder.append_example_row(row)
            return
        index = len(self._story_examples) + 1
        label = str(
            row.get("example") or row.get("name") or self._example_group or f"example-{index}"
        )
        self._story_examples.append(Example(label, index, row, scope="story"))

    def _flush_builder(self) -> None:
        if self._builder is None:
            return
        self._scenarios.append(self._builder.build(self._background))
        self._builder = None

    def _attach_story_examples(self) -> None:
        if not self._story_examples:
            return
        for scenario in self._scenarios:
            if (scenario.story_name or "").strip() != (self._story_name or "").strip():
                continue
            existing = list(getattr(scenario, "story_examples", []) or [])
            scenario.story_examples = existing + list(self._story_examples)
            return

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

    def begin_clause(self, is_continuation: bool, keyword: str) -> None:
        self._clause_is_continuation = is_continuation
        self._clause_keyword = keyword

    def make_clause(self, text: str, phase: Phase) -> Clause:
        return self._make_clause(text, phase)

    def _make_clause(self, text: str, phase: Phase) -> Clause:
        match = _BOLD_TERM.search(text)
        return Clause(
            text=text,
            phase=phase,
            is_continuation=self._clause_is_continuation,
            keyword=self._clause_keyword,
            concepts=_BOLD_TERM.findall(text),
            values=[v.strip("`").strip() for v in _ITALIC_VALUE.findall(text) if v],
            actor=match.group(1).strip() if match else "",
            source=self._clause_source,
        )

    def _consume_background(self, keyword: str, text: str) -> None:
        kw = keyword.lower()
        if kw == "given":
            self._clause_is_continuation = False
            self._clause_keyword = "Given"
            self._background.append(self._make_clause(text, Phase.GIVEN))
            self._background_phase = Phase.GIVEN
            return
        if kw in ("and", "but"):
            phase = self._background_phase or Phase.GIVEN
            labeled = kw.capitalize()
            self._clause_is_continuation = True
            self._clause_keyword = labeled
            self._background.append(self._make_clause(f"{labeled} {text}", phase))
            return
        phase = Phase.WHEN if kw == "when" else Phase.THEN
        labeled = "When" if kw == "when" else "Then"
        self._clause_is_continuation = False
        self._clause_keyword = labeled
        self._background.append(self._make_clause(text, phase))
        self._background_phase = phase

    @classmethod
    def render_scenarios(cls, scenarios: List["MarkdownScenario"], *, story_name: str = "") -> str:
        """Emit markdown matching scenario templates (GWT + examples tables)."""
        lines: List[str] = []
        if story_name:
            lines.append(f"## Story: {story_name}")
            lines.append("")
        for sc in scenarios:
            kind = "Scenario Outline" if getattr(sc, "is_outline", False) else "Scenario"
            lines.append(f"### {kind}: {sc.name}")
            lines.append("")
            for clause in getattr(sc, "background", None) or []:
                lines.append(f"*{clause.phase.value.capitalize()}* {clause.text}")
            for clause in sc.given:
                kw = "Given" if clause is sc.given[0] else "And"
                lines.append(f"*{kw}* {clause.text}")
            for interaction in sc.interactions:
                for i, clause in enumerate(interaction.when):
                    kw = "When" if i == 0 else "And"
                    lines.append(f"*{kw}* {clause.text}")
                for i, clause in enumerate(interaction.then):
                    kw = "Then" if i == 0 else "And"
                    lines.append(f"*{kw}* {clause.text}")
            rows = list(getattr(sc, "example_rows", None) or [])
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


class _ScenarioBuilder:
    def __init__(
        self,
        parser: MarkdownScenario,
        name: str,
        story_name: str,
        is_outline: bool,
        source: SourceLocation,
    ) -> None:
        self._parser = parser
        self._scenario = type(parser)(name=name, story_name=story_name)
        self._scenario.is_outline = is_outline
        self._scenario.source = source
        self._active_phase: Optional[Phase] = None
        self._active_interaction: Optional[Interaction] = None

    def accept(self, keyword: str, text: str) -> None:
        kw = keyword.lower()
        if kw == "given":
            self._parser.begin_clause(False, "Given")
            self._scenario.given.append(self._make_clause(text, Phase.GIVEN))
            self._active_phase = Phase.GIVEN
            self._active_interaction = None
            return
        if kw == "when":
            self._start_when(text)
            return
        if kw == "then":
            self._append_then(text)
            return
        if kw in ("and", "but"):
            self._accept_continuation(kw, text)

    def append_example_row(self, row: dict) -> None:
        self._scenario.example_rows.append(row)

    def _start_when(self, text: str) -> None:
        self._active_interaction = Interaction()
        self._scenario.interactions.append(self._active_interaction)
        self._parser.begin_clause(False, "When")
        self._active_interaction.when.append(self._make_clause(text, Phase.WHEN))
        self._active_phase = Phase.WHEN

    def _append_then(self, text: str) -> None:
        if self._active_interaction is None:
            self._active_interaction = Interaction()
            self._scenario.interactions.append(self._active_interaction)
        self._parser.begin_clause(False, "Then")
        self._active_interaction.then.append(self._make_clause(text, Phase.THEN))
        self._active_phase = Phase.THEN

    def _accept_continuation(self, kw: str, text: str) -> None:
        keyword = kw.capitalize()
        prefixed = f"{keyword} {text}"
        self._parser.begin_clause(True, keyword)
        if self._active_phase is Phase.GIVEN:
            self._scenario.given.append(self._make_clause(prefixed, Phase.GIVEN))
            return
        if self._active_phase is Phase.WHEN and self._active_interaction:
            self._active_interaction.when.append(self._make_clause(prefixed, Phase.WHEN))
            return
        if self._active_phase is Phase.THEN and self._active_interaction:
            self._active_interaction.then.append(self._make_clause(prefixed, Phase.THEN))

    def _make_clause(self, text: str, phase: Phase) -> Clause:
        return self._parser.make_clause(text, phase)

    def build(self, background: List[Clause]) -> "MarkdownScenario":
        self._scenario.background = list(background)
        self._scenario.sync_tree_from_legacy()
        return self._scenario


# -- Leaf node types -----------------------------------------------------------

class MarkdownStory(Story):
    def load_scenario(self, source: Scenario) -> MarkdownScenario:
        return MarkdownScenario(source.name, source.sequential_order, source.story_name)


class MarkdownSubEpic(SubEpic):
    def load_sub_epic(self, source: SubEpic) -> "MarkdownSubEpic":
        return MarkdownSubEpic(source.name, source.sequential_order)

    def load_story(self, source: Story) -> MarkdownStory:
        return MarkdownStory(source.name, source.sequential_order, source.story_type)


class MarkdownEpic(Epic):
    def load_sub_epic(self, source: SubEpic) -> MarkdownSubEpic:
        return MarkdownSubEpic(source.name, source.sequential_order)


# -- Root node + I/O -----------------------------------------------------------

_DOC_TITLE_PREFIXES = ("story map", "thin slic", "acceptance criteria", "specification by example")
_OUTLINE_EPIC_RE = re.compile(r"^(\s*)\(E\)\s+(.+)$")
_OUTLINE_STORY_RE = re.compile(r"^(\s*)\(S\)\s+(.+)$")
_OUTLINE_ESTIMATE_RE = re.compile(r"^(\s*)\*\s+(\S.+)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_RE = re.compile(r"^(\s*)-\s+(.+)$")


class MarkdownParseError(Exception):
    """Raised when a document is not a valid Markdown story map."""


class MarkdownStoryMap(StoryMap):
    """Markdown story-map I/O. IS the format-typed tree root.

    parse / render / sync implement the Uniform Callable Surface.
    attach_source_locations stamps SourceLocation onto nodes after parsing.
    """

    def load_epic(self, source: MarkdownEpic) -> MarkdownEpic:
        return MarkdownEpic(source.name, source.sequential_order)

    def load_increment(self, source: Increment) -> MarkdownIncrement:
        return MarkdownIncrement(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: "Path") -> Optional["MarkdownStoryMap"]:
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
        return merged if merged.epics else None

    # -- Uniform Callable Surface ----------------------------------------------

    def render(self, story_map: "MarkdownStoryMap", previous: Optional[str] = None) -> str:
        if self._should_render_outline(story_map, previous):
            return self._render_outline(story_map)
        lines: List[str] = []
        for epic in story_map.epics:
            self._render_epic(epic, lines, depth=1)
        return "\n".join(lines)

    def _should_render_outline(self, story_map: "MarkdownStoryMap", previous: Optional[str]) -> bool:
        if previous and self._contains_outline_structure(previous.splitlines()):
            return True
        for epic in story_map.epics:
            if getattr(epic, "estimate", ""):
                return True
            for sub in epic.sub_epics:
                if self._sub_tree_has_outline_signal(sub):
                    return True
        return False

    def _sub_tree_has_outline_signal(self, sub: MarkdownSubEpic) -> bool:
        if getattr(sub, "estimate", ""):
            return True
        for nested in sub.sub_epics:
            if self._sub_tree_has_outline_signal(nested):
                return True
        return False

    def strip_backticks(self, text: str) -> str:
        return MarkdownScenario().strip_backticks(text)

    def _render_outline(self, story_map: "MarkdownStoryMap") -> str:
        self._outline_lines: List[str] = []
        self._outline_indent = 4
        for epic in story_map.epics:
            self._outline_lines.append(f"(E) {self.strip_backticks(epic.name)}")
            factory_line = render_md_factory_line(epic.collected_example_factories())
            if factory_line:
                self._outline_lines.append(f"    {factory_line}")
            if getattr(epic, "estimate", ""):
                self._outline_lines.append(f"    * {epic.estimate}")
            self._render_outline_sub_epics(epic.sub_epics)
        return "\n".join(self._outline_lines)

    def _render_outline_sub_epics(self, subs: List[MarkdownSubEpic]) -> None:
        pad = " " * self._outline_indent
        story_pad = " " * (self._outline_indent + 4)
        for sub in subs:
            self._outline_lines.append(f"{pad}(E) {self.strip_backticks(sub.name)}")
            self._render_outline_stories(sub, story_pad)
            if getattr(sub, "estimate", ""):
                self._outline_lines.append(f"{story_pad}* {sub.estimate}")
            self._outline_indent += 4
            self._render_outline_sub_epics(sub.sub_epics)
            self._outline_indent -= 4

    def _render_outline_stories(self, sub: MarkdownSubEpic, story_pad: str) -> None:
        for story in sub.stories:
            actor = story.users[0] if story.users else ""
            name = self.strip_backticks(story.name)
            if actor:
                actor_name = self.strip_backticks(actor)
                self._outline_lines.append(f"{story_pad}(S) {actor_name} --> {name}")
                continue
            self._outline_lines.append(f"{story_pad}(S) --> {name}")

    def parse(self, text: str) -> "MarkdownStoryMap":
        if not isinstance(text, str) or text.strip() == "":
            return MarkdownStoryMap()
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

    def _parse_scenario_document(self, text: str) -> "MarkdownStoryMap":
        scenarios = MarkdownScenario.from_text(text, "story-scenarios.md")
        story_map = MarkdownStoryMap()
        stories: dict[str, MarkdownStory] = {}
        epic = MarkdownEpic("Stories", 1)
        sub = MarkdownSubEpic("Scenarios", 1)
        for scenario in scenarios:
            name = (scenario.story_name or "Story").strip()
            story = stories.get(name)
            if story is None:
                story = MarkdownStory(name, len(stories) + 1, StoryType.USER)
                stories[name] = story
                sub.stories.append(story)
            story.scenarios.append(scenario)
        if stories:
            epic.sub_epics.append(sub)
            story_map.epics.append(epic)
        return story_map

    def sync(self, text: str, canonical: "MarkdownStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # -- Source location stamping ----------------------------------------------

    def attach_source_locations(self, text: str, rel_file: str) -> None:
        """Stamp SourceLocation onto each Epic/SubEpic/Story from the markdown text."""
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
        for sub in self.all_sub_epics():
            if sub.name == name and not getattr(sub, "source", None):
                sub.source = loc
                return

    def _stamp_story(self, name: str, loc: SourceLocation) -> None:
        for story in self.all_stories():
            if story.name == name and not getattr(story, "source", None):
                story.source = loc
                return

    # -- render helpers --------------------------------------------------------

    def _render_epic(self, epic: MarkdownEpic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {epic.name}")
        factory_line = render_md_factory_line(epic.collected_example_factories())
        if factory_line:
            lines.append(factory_line)
        for sub in epic.sub_epics:
            self._render_sub_epic(sub, lines, depth + 1)

    def _render_sub_epic(self, sub: MarkdownSubEpic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {sub.name}")
        for nested in sub.sub_epics:
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

    def _parse_lines(self, lines: List[str]) -> "MarkdownStoryMap":
        self._story_map = MarkdownStoryMap()
        self._current_epic: Optional[MarkdownEpic] = None
        self._sub_epic_stack: List[MarkdownSubEpic] = []
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
            self._accept_map_factory_line()
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
            self._sub_epic_stack[-1].sub_epics
            if self._sub_epic_stack
            else self._current_epic.sub_epics
        )
        sub = MarkdownSubEpic(name, len(parent_children) + 1)
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

    def _accept_map_factory_line(self) -> None:
        factories = parse_md_factory_line(self._raw_line.strip())
        if not factories or self._current_epic is None:
            return
        for factory in factories:
            if factory not in self._current_epic.example_factories:
                self._current_epic.example_factories.append(factory)

    def _is_document_title(self, name: str) -> bool:
        lower = name.lower()
        return any(lower.startswith(p) for p in _DOC_TITLE_PREFIXES)

    def _is_non_story_section_heading(self, name: str) -> bool:
        return name.lower() in {"context gaps", "validation results"}

    def _ensure_sub_epic(self) -> MarkdownSubEpic:
        if self._sub_epic_stack:
            return self._sub_epic_stack[-1]
        if self._current_epic is None:
            self._current_epic = MarkdownEpic("Imported", len(self._story_map.epics) + 1)
            self._story_map.epics.append(self._current_epic)
        sub = MarkdownSubEpic(self._current_epic.name, len(self._current_epic.sub_epics) + 1)
        self._current_epic.sub_epics.append(sub)
        self._sub_epic_stack.append(sub)
        return sub

    def _parse_outline_lines(self, lines: List[str]) -> "MarkdownStoryMap":
        self._story_map = MarkdownStoryMap()
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
            self._accept_map_factory_line()
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
            self._sub_epic_stack[-1].sub_epics
            if self._sub_epic_stack
            else self._current_epic.sub_epics
        )
        sub = MarkdownSubEpic(name, len(parent_children) + 1)
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
            story.users = [actor]
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
