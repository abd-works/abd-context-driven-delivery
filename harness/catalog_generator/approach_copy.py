"""The approach page's copy, read from hand-editable markdown (``markdown/cdd-approach.md``)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from harness.catalog_generator.stage_columns import STAGE_COLUMNS
from harness.guidance.stages import STAGES, StageScope
from harness.name.name import Name

APPROACH_MARKDOWN = Path(__file__).resolve().parent / "markdown" / "cdd-approach.md"
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_SETTING = re.compile(r"^([a-z_]+):\s*(.*)$")
_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_DEFAULT_PRINCIPLES_HEADING = "Context Driven Delivery Practices"


@dataclass(frozen=True)
class StageCopy:
    """One stage the approach page walks through: its chips, its paragraphs, the example it names, and the scope its
    shape draws. A CDD stage's scope is the approach's own; a stage of the page alone, such as Context or Validate,
    gives its scope in its settings."""

    id: str
    title: str = ""
    items: tuple[str, ...] = ()
    paras: tuple[str, ...] = ()
    example: str = ""
    scope: StageScope | None = None


@dataclass(frozen=True)
class PrincipleCopy:
    """One principle of the approach: its bullets, its caption, and the kind of board drawn under it (``windows``,
    ``descriptions``, ``spec``, or ``tickets``)."""

    slug: str
    title: str
    kind: str = "tickets"
    bullets: tuple[str, ...] = ()
    caption: str = ""


@dataclass(frozen=True)
class ApproachCopy:
    subhead: str
    principles_heading: str
    library_heading: str
    stages: tuple[StageCopy, ...]
    principles: tuple[PrincipleCopy, ...]

    @classmethod
    def load(cls, path: str | Path = APPROACH_MARKDOWN) -> ApproachCopy:
        return _ApproachMarkdown(Path(path).read_text(encoding="utf-8")).copy()

    @property
    def board_stages(self) -> dict[str, StageCopy]:
        """The stages the catalog board has a column for, by the column's key."""
        columns = ((STAGE_COLUMNS.of(stage.id), stage) for stage in self.stages)
        return {column.key: stage for column, stage in columns if column is not None}


class _ApproachMarkdown:
    """The approach markdown: an intro (the subhead), then ``## Stages``, a ``##`` section of principles, and
    ``## Library``. Each stage and principle is a ``###`` heading whose first lines are ``name: value`` settings."""

    def __init__(self, text: str) -> None:
        self._text = text

    def copy(self) -> ApproachCopy:
        intro, *sections = re.split(r"(?m)^## ", self._text)
        stages: tuple[StageCopy, ...] = ()
        principles: tuple[PrincipleCopy, ...] = ()
        principles_heading, library_heading = _DEFAULT_PRINCIPLES_HEADING, ""
        for section in sections:
            title, _, body = section.partition("\n")
            title = title.strip()
            if title == "Stages":
                stages = tuple(self._stage(name, rest) for name, rest in self._entries(body))
            elif title == "Library":
                library_heading = body.strip()
            else:
                principles_heading = title
                principles = tuple(self._principle(name, rest) for name, rest in self._entries(body))
        subhead = re.sub(r"(?m)^#\s+Approach\s*", "", intro).strip()
        return ApproachCopy(subhead, principles_heading, library_heading, stages, principles)

    def _stage(self, title: str, text: str) -> StageCopy:
        settings, remainder = self._settings(text)
        stage_id = settings.get("id", Name(title).title_slug)
        return StageCopy(
            id=stage_id,
            title=title,
            items=tuple(item.strip() for item in settings.get("items", "").split("|") if item.strip()),
            paras=tuple(paragraph.strip() for paragraph in _PARAGRAPH_BREAK.split(remainder) if paragraph.strip()),
            example=settings.get("example", ""),
            scope=self._scope(stage_id, settings, title),
        )

    def _scope(self, stage_id: str, settings: dict[str, str], title: str) -> StageScope:
        stage = STAGES.of(stage_id)
        if stage is not None:
            return stage.scope
        return StageScope(
            settings.get("shape", "square"), settings.get("scope_name", title), settings.get("scope_width", ""), ""
        )

    def _principle(self, title: str, text: str) -> PrincipleCopy:
        settings, remainder = self._settings(text)
        bullets = tuple(line.strip()[2:].strip() for line in remainder.splitlines() if line.strip().startswith("- "))
        caption = "\n".join(line for line in remainder.splitlines() if not line.strip().startswith("- ")).strip()
        return PrincipleCopy(
            slug=settings.get("slug", Name(title).title_slug),
            title=title,
            kind=settings.get("kind", "tickets"),
            bullets=bullets,
            caption=_LINK.sub(r'<a href="\2">\1</a>', caption) if caption else "",
        )

    def _entries(self, body: str) -> list[tuple[str, str]]:
        """Each ``###`` entry of a section: its heading and the text under it."""
        entries = []
        for chunk in re.split(r"(?m)^### ", body):
            if chunk.strip():
                title, _, rest = chunk.partition("\n")
                entries.append((title.strip(), rest))
        return entries

    def _settings(self, text: str) -> tuple[dict[str, str], str]:
        """The ``name: value`` lines that open an entry, and the text after them."""
        settings: dict[str, str] = {}
        lines = text.splitlines()
        index = 0
        while index < len(lines):
            stripped = lines[index].strip()
            if not stripped:
                index += 1
                if settings:
                    break
                continue
            setting = _SETTING.match(stripped)
            if not setting:
                break
            settings[setting.group(1)] = setting.group(2).strip()
            index += 1
        return settings, "\n".join(lines[index:]).strip()
