"""Markdown format story nodes — all seven StoryNode subtypes plus I/O.

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

from stories.src.stories.model.nodes import Epic, Story, StoryType, SubEpic
from stories.src.stories.model.scenario import Clause, Interaction, Phase, Scenario
from stories.src.stories.model.source_location import SourceLocation
from stories.src.stories.model.story_map import StoryMap
from stories.src.stories.model.thin_slice import Increment
from stories.src.stories.model.update_report import UpdateReport

_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
_BULLET_PATTERN = re.compile(r"^(\s*)-\s+(.+)$")
_OUTLINE_EPIC_PATTERN = re.compile(r"^(\s*)\(E\)\s+(.+)$")
_OUTLINE_STORY_PATTERN = re.compile(r"^(\s*)\(S\)\s+(.+)$")
_OUTLINE_ESTIMATE_PATTERN = re.compile(r"^(\s*)\*\s+(\S.+)$")


def _strip_backticks(text: str) -> str:
    s = text.strip()
    while s.startswith("`") and s.endswith("`") and len(s) >= 2:
        s = s[1:-1].strip()
    return s


def _strip_markup(text: str) -> str:
    s = _strip_backticks(text)
    while s.startswith("*") and s.endswith("*") and len(s) >= 2:
        s = _strip_backticks(s[1:-1].strip())
    return _strip_backticks(s)


def _split_outline_story(raw_text: str) -> tuple[str, str]:
    if "-->" not in raw_text:
        return "", _strip_backticks(raw_text)
    actor_part, story_part = raw_text.split("-->", 1)
    return _strip_backticks(actor_part), _strip_backticks(story_part)


# ── MarkdownIncrement ─────────────────────────────────────────────────────────

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
                current = cls(_strip_markup(m_inc.group(1)), len(increments) + 1)
                current.source = SourceLocation(rel_file, idx)
                in_stories = False
                continue
            if current is None:
                continue
            if m := _KV_OUTCOME.match(stripped):
                current.outcome = _strip_markup(m.group(1))
                in_stories = False
            elif m := _KV_SLICING.match(stripped):
                current.slicing_notes = _strip_markup(m.group(1))
                in_stories = False
            elif m := _KV_DECISION.match(stripped):
                current.decision_prompt = _strip_markup(m.group(1))
                in_stories = False
            elif _KV_STORIES.match(stripped):
                in_stories = True
            elif _ANY_H2.match(raw) or _INCREMENT_H3.match(raw):
                in_stories = False
            elif in_stories:
                if m := _BULLET.match(raw):
                    current.stories.append(_strip_markup(m.group(1)))
                else:
                    in_stories = False

        if current is not None:
            increments.append(current)
        return increments


# ── MarkdownScenario ──────────────────────────────────────────────────────────

_SCENARIO_H3 = re.compile(
    r"^###\s+Scenario(?:\s+Outline)?(?:\s+\d+)?\s*:\s*(.+?)\s*$", re.IGNORECASE
)
_STORY_H2 = re.compile(r"^##\s+Story\s*:\s*(.+?)\s*$", re.IGNORECASE)
_BACKGROUND_H3 = re.compile(r"^###\s+Background\b", re.IGNORECASE)
_EXAMPLES_H3 = re.compile(r"^#{3,4}\s+Examples\b", re.IGNORECASE)
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
        scenarios: List["MarkdownScenario"] = []
        seen: set = set()
        for pattern in (
            "**/scenarios/*.md", "**/scenarios/**/*.md", "**/scenarios.md",
            "**/md/*.md", "**/md/**/*.md",
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
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        story_name = cls._infer_story_name(path, lines)

        background: List[Clause] = []
        scenarios: List[MarkdownScenario] = []
        builder: Optional[_ScenarioBuilder] = None
        in_background = False
        in_examples = False
        example_headers: List[str] = []
        background_phase: Optional[Phase] = None

        def flush():
            nonlocal builder
            if builder is not None:
                scenarios.append(builder.build(background))
                builder = None

        for i, raw in enumerate(lines, start=1):
            if not raw.strip():
                continue
            m_scen = _SCENARIO_H3.match(raw)
            if m_scen:
                flush()
                builder = _ScenarioBuilder(
                    cls, _strip_markup(m_scen.group(1)), story_name,
                    is_outline="outline" in raw.lower(),
                    source=SourceLocation(rel, i),
                )
                in_background = False
                in_examples = False
                continue
            if _BACKGROUND_H3.match(raw):
                in_background = True
                in_examples = False
                background_phase = None
                continue
            if _EXAMPLES_H3.match(raw):
                in_examples = True
                in_background = False
                example_headers = []
                continue
            if re.match(r"^###\s+", raw):
                in_background = False
                in_examples = False
            parsed_step = _parse_step(raw)
            if parsed_step:
                keyword, step_text = parsed_step
                src = SourceLocation(rel, i)
                if in_background:
                    background_phase = _consume_background(
                        keyword, step_text, src, background, background_phase
                    )
                elif builder:
                    builder.accept(keyword, step_text, src)
                continue
            if in_examples and builder:
                row_match = _TABLE_ROW.match(raw)
                if row_match:
                    cells = [c.strip() for c in row_match.group(1).split("|")]
                    if not example_headers:
                        if not all(re.fullmatch(r"-+|:-+:?|:?-+:?", c) for c in cells):
                            example_headers = [_strip_markup(c) for c in cells]
                        continue
                    if all(set(c.strip(":")) <= {"-"} for c in cells):
                        continue
                    row = dict(zip(example_headers, (_strip_markup(c) for c in cells)))
                    builder._scenario.example_rows.append(row)

        flush()
        return scenarios

    @staticmethod
    def _infer_story_name(path: Path, lines: List[str]) -> str:
        for line in lines[:20]:
            m = _STORY_H2.match(line)
            if m:
                return _strip_markup(m.group(1))
        for line in lines[:5]:
            m = _H1.match(line)
            if m:
                return _strip_markup(m.group(1))
        parts = path.parts
        if len(parts) >= 2 and parts[-2] == "scenarios":
            return parts[-3].replace("-", " ") if len(parts) >= 3 else ""
        return path.stem.replace("-", " ")


class _ScenarioBuilder:
    def __init__(self, cls, name: str, story_name: str,
                 is_outline: bool, source: SourceLocation) -> None:
        self._cls = cls
        self._scenario = cls(name=name, story_name=story_name)
        self._scenario.is_outline = is_outline
        self._scenario.source = source
        self._active_phase: Optional[Phase] = None
        self._active_interaction: Optional[Interaction] = None

    def accept(self, keyword: str, text: str, source: SourceLocation) -> None:
        kw = keyword.lower()
        if kw == "given":
            self._scenario.given.append(_make_clause(text, Phase.GIVEN, source, False))
            self._active_phase = Phase.GIVEN
            self._active_interaction = None
        elif kw == "when":
            self._active_interaction = Interaction()
            self._scenario.interactions.append(self._active_interaction)
            self._active_interaction.when.append(_make_clause(text, Phase.WHEN, source, False))
            self._active_phase = Phase.WHEN
        elif kw == "then":
            if self._active_interaction is None:
                self._active_interaction = Interaction()
                self._scenario.interactions.append(self._active_interaction)
            self._active_interaction.then.append(_make_clause(text, Phase.THEN, source, False))
            self._active_phase = Phase.THEN
        elif kw in ("and", "but"):
            self._accept_continuation(kw, text, source)

    def _accept_continuation(self, kw: str, text: str, source: SourceLocation) -> None:
        prefixed = f"{kw.capitalize()} {text}"
        if self._active_phase is Phase.GIVEN:
            self._scenario.given.append(_make_clause(prefixed, Phase.GIVEN, source, True))
        elif self._active_phase is Phase.WHEN and self._active_interaction:
            self._active_interaction.when.append(_make_clause(prefixed, Phase.WHEN, source, True))
        elif self._active_phase is Phase.THEN and self._active_interaction:
            self._active_interaction.then.append(_make_clause(prefixed, Phase.THEN, source, True))

    def build(self, background: List[Clause]) -> "MarkdownScenario":
        self._scenario.background = list(background)
        return self._scenario


def _make_clause(text: str, phase: Phase, source: SourceLocation, is_continuation: bool) -> Clause:
    return Clause(
        text=text, phase=phase, is_continuation=is_continuation,
        concepts=_BOLD_TERM.findall(text),
        values=[v.strip("`").strip() for v in _ITALIC_VALUE.findall(text) if v],
        actor=(_BOLD_TERM.search(text) or type("", (), {"group": lambda s, n: ""})()).group(1).strip() if _BOLD_TERM.search(text) else "",
        source=source,
    )


def _parse_step(raw: str) -> Optional[tuple[str, str]]:
    m = _ITALIC_STEP.match(raw) or _BULLET_STEP.match(raw)
    return (m.group(1), m.group(2).strip()) if m else None


def _consume_background(keyword: str, text: str, source: SourceLocation,
                        background: List[Clause], current_phase: Optional[Phase]) -> Optional[Phase]:
    kw = keyword.lower()
    if kw == "given":
        background.append(_make_clause(text, Phase.GIVEN, source, False))
        return Phase.GIVEN
    if kw in ("and", "but"):
        phase = current_phase or Phase.GIVEN
        background.append(_make_clause(f"{kw.capitalize()} {text}", phase, source, True))
        return phase
    phase = Phase.WHEN if kw == "when" else Phase.THEN
    background.append(_make_clause(text, phase, source, False))
    return phase


# ── Leaf node types ───────────────────────────────────────────────────────────

class MarkdownStory(Story):
    def create_child_scenario(self, source: Scenario) -> MarkdownScenario:
        return MarkdownScenario(source.name, source.sequential_order, source.story_name)


class MarkdownSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "MarkdownSubEpic":
        return MarkdownSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> MarkdownStory:
        return MarkdownStory(source.name, source.sequential_order, source.story_type)


class MarkdownEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> MarkdownSubEpic:
        return MarkdownSubEpic(source.name, source.sequential_order)


# ── Root node + I/O ───────────────────────────────────────────────────────────

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

    def create_child_epic(self, source: MarkdownEpic) -> MarkdownEpic:
        return MarkdownEpic(source.name, source.sequential_order)

    def create_child_increment(self, source: Increment) -> MarkdownIncrement:
        return MarkdownIncrement(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: "Path") -> Optional["MarkdownStoryMap"]:
        """Find story-map.md files under *root*, merge, and return; None if absent."""
        root = Path(root).resolve()
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
            rel = str(md_path.relative_to(root)).replace("\\", "/")
            merged.attach_source_locations(text, rel)
            if not getattr(merged, "source", None):
                from stories.src.stories.model.source_location import SourceLocation as _SL
                merged.source = _SL(rel, 1)
        return merged if merged.epics else None

    # ── Uniform Callable Surface ──────────────────────────────────────────────

    def render(self, story_map: "MarkdownStoryMap", previous: Optional[str] = None) -> str:
        if self._should_render_outline(story_map, previous):
            return self._render_outline(story_map)
        lines: List[str] = []
        for epic in story_map.epics:
            self._render_epic(epic, lines, depth=1)
        return "\n".join(lines)

    @staticmethod
    def _should_render_outline(story_map: "MarkdownStoryMap", previous: Optional[str]) -> bool:
        if previous and MarkdownStoryMap()._contains_outline_structure(previous.splitlines()):
            return True
        for epic in story_map.epics:
            if getattr(epic, "estimate", ""):
                return True
            for sub in epic.sub_epics:
                if MarkdownStoryMap._sub_tree_has_outline_signal(sub):
                    return True
        return False

    @staticmethod
    def _sub_tree_has_outline_signal(sub: MarkdownSubEpic) -> bool:
        if getattr(sub, "estimate", ""):
            return True
        for nested in sub.sub_epics:
            if MarkdownStoryMap._sub_tree_has_outline_signal(nested):
                return True
        return False

    def _render_outline(self, story_map: "MarkdownStoryMap") -> str:
        lines: List[str] = []
        for epic in story_map.epics:
            lines.append(f"(E) {_strip_backticks(epic.name)}")
            if getattr(epic, "estimate", ""):
                lines.append(f"    * {epic.estimate}")
            self._render_outline_sub_epics(epic.sub_epics, lines, indent=4)
        return "\n".join(lines)

    def _render_outline_sub_epics(
        self, subs: List[MarkdownSubEpic], lines: List[str], indent: int
    ) -> None:
        pad = " " * indent
        story_pad = " " * (indent + 4)
        for sub in subs:
            lines.append(f"{pad}(E) {_strip_backticks(sub.name)}")
            for story in sub.stories:
                actor = story.users[0] if story.users else ""
                name = _strip_backticks(story.name)
                if actor:
                    lines.append(f"{story_pad}(S) {_strip_backticks(actor)} --> {name}")
                else:
                    lines.append(f"{story_pad}(S) --> {name}")
            if getattr(sub, "estimate", ""):
                lines.append(f"{story_pad}* {sub.estimate}")
            self._render_outline_sub_epics(sub.sub_epics, lines, indent + 4)

    def parse(self, text: str) -> "MarkdownStoryMap":
        if not isinstance(text, str) or text.strip() == "":
            return MarkdownStoryMap()
        lines = text.splitlines()
        self._guard_has_structure(lines)
        if self._contains_outline_structure(lines):
            return self._parse_outline_lines(lines)
        return self._parse_lines(lines)

    def sync(self, text: str, canonical: "MarkdownStoryMap") -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    # ── Source location stamping ──────────────────────────────────────────────

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
                name = _strip_backticks(m_epic_out.group(2))
                if indent == 0:
                    if epic_index < len(self.epics):
                        self.epics[epic_index].source = SourceLocation(rel_file, i)
                        epic_index += 1
                else:
                    self._stamp_sub_epic(name, SourceLocation(rel_file, i))
                continue
            if m_story_out:
                name = _strip_backticks(m_story_out.group(2).split("-->", 1)[-1] if "-->" in m_story_out.group(2) else m_story_out.group(2))
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

    # ── render helpers ────────────────────────────────────────────────────────

    def _render_epic(self, epic: MarkdownEpic, lines: List[str], depth: int) -> None:
        lines.append(f"{'#' * depth} {epic.name}")
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

    # ── parse helpers ─────────────────────────────────────────────────────────

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
        story_map = MarkdownStoryMap()
        current_epic: Optional[MarkdownEpic] = None
        current_sub_epic_stack: List[MarkdownSubEpic] = []
        epic_heading_depth: Optional[int] = None
        ignored_heading_depth: Optional[int] = None

        for raw in lines:
            if not raw.strip():
                continue
            heading = _HEADING_PATTERN.match(raw)
            bullet = _BULLET_PATTERN.match(raw)

            if ignored_heading_depth is not None:
                if heading is None:
                    continue
                if len(heading.group(1)) > ignored_heading_depth:
                    continue
                ignored_heading_depth = None

            if heading:
                depth = len(heading.group(1))
                name = heading.group(2).strip()
                if self._is_document_title(name):
                    continue
                if self._is_non_story_section_heading(name):
                    ignored_heading_depth = depth
                    continue
                if name.lower().startswith("story:"):
                    story_name = name.split(":", 1)[1].strip() or name
                    parent = self._ensure_sub_epic(story_map, current_epic, current_sub_epic_stack)
                    parent.stories.append(MarkdownStory(story_name, len(parent.stories) + 1, StoryType.USER))
                    continue
                if depth == 1 or current_epic is None or (epic_heading_depth is not None and depth <= epic_heading_depth):
                    if epic_heading_depth is None:
                        epic_heading_depth = depth
                    current_epic = MarkdownEpic(name, len(story_map.epics) + 1)
                    story_map.epics.append(current_epic)
                    current_sub_epic_stack = []
                    continue
                if current_epic is not None:
                    if epic_heading_depth is None:
                        epic_heading_depth = 1
                    relative_depth = max(depth - epic_heading_depth, 1)
                    if relative_depth >= 2:
                        parent = self._ensure_sub_epic(story_map, current_epic, current_sub_epic_stack)
                        parent.stories.append(MarkdownStory(name, len(parent.stories) + 1, StoryType.USER))
                    else:
                        while len(current_sub_epic_stack) >= relative_depth:
                            current_sub_epic_stack.pop()
                        parent_children = current_sub_epic_stack[-1].sub_epics if current_sub_epic_stack else current_epic.sub_epics
                        sub = MarkdownSubEpic(name, len(parent_children) + 1)
                        parent_children.append(sub)
                        current_sub_epic_stack.append(sub)
                continue

            if bullet:
                indent = len(bullet.group(1)) // 2
                if indent == 0 and current_epic is not None:
                    parent = self._ensure_sub_epic(story_map, current_epic, current_sub_epic_stack)
                    parent.stories.append(MarkdownStory(bullet.group(2).strip(), len(parent.stories) + 1, StoryType.USER))

        return story_map

    def _is_document_title(self, name: str) -> bool:
        lower = name.lower()
        return any(lower.startswith(p) for p in _DOC_TITLE_PREFIXES)

    def _is_non_story_section_heading(self, name: str) -> bool:
        return name.lower() in {"context gaps", "validation results"}

    def _ensure_sub_epic(self, story_map: "MarkdownStoryMap", current_epic: Optional[MarkdownEpic],
                         stack: List[MarkdownSubEpic]) -> MarkdownSubEpic:
        if stack:
            return stack[-1]
        if current_epic is None:
            current_epic = MarkdownEpic("Imported", len(story_map.epics) + 1)
            story_map.epics.append(current_epic)
        sub = MarkdownSubEpic(current_epic.name, len(current_epic.sub_epics) + 1)
        current_epic.sub_epics.append(sub)
        stack.append(sub)
        return sub

    def _parse_outline_lines(self, lines: List[str]) -> "MarkdownStoryMap":
        story_map = MarkdownStoryMap()
        current_epic: Optional[MarkdownEpic] = None
        stack: List[MarkdownSubEpic] = []

        for raw in lines:
            if not raw.strip():
                continue
            m = _OUTLINE_EPIC_PATTERN.match(raw)
            if m:
                indent = len(m.group(1)) // 4
                name = _strip_backticks(m.group(2))
                if indent <= 0:
                    current_epic = MarkdownEpic(name, len(story_map.epics) + 1)
                    story_map.epics.append(current_epic)
                    stack = []
                elif current_epic:
                    while len(stack) >= indent:
                        stack.pop()
                    parent_children = stack[-1].sub_epics if stack else current_epic.sub_epics
                    sub = MarkdownSubEpic(name, len(parent_children) + 1)
                    parent_children.append(sub)
                    stack.append(sub)
                continue
            m = _OUTLINE_STORY_PATTERN.match(raw)
            if m and stack:
                actor, story_name = _split_outline_story(m.group(2))
                story = MarkdownStory(story_name, len(stack[-1].stories) + 1, StoryType.USER)
                if actor:
                    story.users = [actor]
                stack[-1].stories.append(story)
                continue
            m = _OUTLINE_ESTIMATE_PATTERN.match(raw)
            if m:
                estimate = m.group(2).strip()
                if stack:
                    stack[-1].estimate = estimate
                elif current_epic is not None:
                    current_epic.estimate = estimate

        return story_map
