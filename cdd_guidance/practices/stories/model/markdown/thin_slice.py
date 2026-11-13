"""The thin slice a markdown story map keeps its increments in (`thin-slice.md` beside it): `### Increment 1: Name`
headings in order, each with its outcome and slicing notes, then the stories it delivers as `- *Story*` bullets.

A thin slice is written back as it was read: every line an edit does not touch stays as written, so one laid out by hand
can be edited through the story map."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from cdd_guidance.practices.stories.model.markdown.map_reading import described
from cdd_guidance.practices.stories.model.markdown.markup import strip_markup
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles, path_from, source_at
from cdd_guidance.practices.stories.model.story_model import Increment, Story, StoryModel

_INCREMENT_H3 = re.compile(r"^###\s+Increment\s+(\d+)\s*:\s*(.+?)\s*$", re.IGNORECASE)
_KV_OUTCOME = re.compile(r"^\*\*Outcome\s*:\*\*\s*(.+)$", re.IGNORECASE)
_KV_SLICING = re.compile(r"^\*\*Slicing\s+notes\s*:\*\*\s*(.+)$", re.IGNORECASE)
_KV_STORIES = re.compile(r"^\*\*Stories(?:\s+in\s+this\s+increment)?\s*:?\*\*", re.IGNORECASE)
_KV_DECISION = re.compile(r"^\*\*Decision\s+prompt\s*:\*\*\s*(.+)$", re.IGNORECASE)
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")
_STORIES_LABEL = "**Stories in this increment:**"
_NEW_THIN_SLICE = ["# Thin slicing", "", "## Increments", ""]


class IncrementLines:
    """The lines one increment was read with: its heading, the lines that describe it (its outcome and slicing notes),
    the label above its stories, each story bullet as written with the story it named (none for a name the story map
    does not hold) and that story's name then, and the lines after them."""

    def __init__(self, heading: str, name: str, number: int) -> None:
        self.heading = heading
        self.said = (name, number)
        self.described: List[str] = []
        self.above: List[str] = []
        self.bullets: List[tuple] = []
        self.below: List[str] = []

    @property
    def description(self) -> str:
        return "\n".join(self.described).strip()


class MarkdownIncrement(Increment):
    """An increment of a thin slice; one read from a thin slice keeps the lines it was read with (``lines``)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lines: Optional[IncrementLines] = None

    def thin_slice_lines(self, number: int) -> List[str]:
        """This increment as the thin slice writes it, numbered number: as read where it is unchanged."""
        heading = f"### Increment {number}: {self.name}"
        if self.lines is None:
            return [heading, *(described(self.description_text) or [""]), _STORIES_LABEL, "", *map(_bullet, self.stories), ""]
        lines = self.lines
        bullets = self._bullets()
        # The first story of an increment read with none sits apart from the label above it.
        apart = [""] if bullets and not lines.bullets and lines.above[-1:] != [""] else []
        kept = lines.heading if lines.said == (self.name, number) else heading
        return [kept, *self._description_lines(), *lines.above, *apart, *bullets, *lines.below]

    def _description_lines(self) -> List[str]:
        """Its description as read while unchanged, else as it says now."""
        if self.description_text == self.lines.description:
            return self.lines.described
        return described(self.description_text) or [""]

    def _bullets(self) -> List[str]:
        """Each bullet as read, its story renamed where the map renamed it, a bullet naming no story of the map kept as
        written; a story added since follows them."""
        delivered = {id(story) for story in self.stories}
        written = [_bullet_as_read(*bullet) for bullet in self.lines.bullets if bullet[1] is None or id(bullet[1]) in delivered]
        shown = {id(story) for _, story, _ in self.lines.bullets}
        return written + [_bullet(story) for story in self.stories if id(story) not in shown]


def _bullet_as_read(raw: str, story: Optional[Story], name: str) -> str:
    """A bullet as it was written, while it names no story of the map or its story keeps the name it was read with."""
    return raw if story is None or story.name == name else _bullet(story)


def _bullet(story: Story) -> str:
    return f"- *{story.name}*"


class ThinSlice:
    """The thin slice file one markdown story map keeps its increments in, with the lines it was read with: those above
    its first increment, the number its first increment carries, and its text then."""

    def __init__(self, path: Path, above: List[str], first_number: int = 1, text: str = "") -> None:
        self.path = path
        self.above = above
        self.first_number = first_number
        self.text_as_read = text

    def text(self, increments: List[MarkdownIncrement]) -> str:
        """The thin slice delivering increments: its lines above them, then each increment in order, one added since
        apart from the one before it."""
        body: List[str] = []
        for index, increment in enumerate(increments):
            if increment.lines is None and body[-1:] not in ([], [""]):
                body.append("")
            body.extend(increment.thin_slice_lines(self.first_number + index))
        return "\n".join([*self.above, *body]).rstrip("\n") + "\n"

    def write(self, increments: List[MarkdownIncrement]) -> List[Path]:
        """Write the thin slice when increments change what it holds; answer the file written, none when unchanged or
        when there is no thin slice yet and nothing to keep in one."""
        text = self.text(increments)
        if text == self.text_as_read or not (increments or self.path.is_file()):
            return []
        self.path.write_text(text, encoding="utf-8")
        self.text_as_read = text
        return [self.path]


def thin_slice_in(folder: Path, story_map: StoryModel, project: Path) -> ThinSlice:
    """The thin slice in folder (``StoryMapFiles.thin_slicing``), its increments read onto story_map, each delivering
    story_map's own stories and naming its file from project; a new `thin-slice.md` in folder when it holds none."""
    found = StoryMapFiles(folder).thin_slicing()
    if found is None:
        return ThinSlice(Path(folder) / "thin-slice.md", list(_NEW_THIN_SLICE))
    text = found.read_text(encoding="utf-8")
    reading = _ThinSliceReading(story_map, path_from(Path(project).resolve(), found))
    for increment in reading.read(text.splitlines()):
        story_map.append_increment(increment)
    return ThinSlice(found, reading.above, reading.first_number, text)


class _ThinSliceReading:
    """One read of a thin slice's lines onto a story map: the lines above its first increment, the increments read, and
    whether the stories of the last one are being read."""

    def __init__(self, story_map: "StoryModel", file: str) -> None:
        self.story_map = story_map
        self.file = file
        self.above: List[str] = []
        self.first_number = 1
        self.increments: List[MarkdownIncrement] = []
        self.in_stories = False

    def read(self, lines: List[str]) -> List[MarkdownIncrement]:
        for number, raw in enumerate(lines, start=1):
            heading = _INCREMENT_H3.match(raw.strip())
            if heading is not None:
                self._open(raw, heading, number)
            elif self.increments:
                self._read_line(raw, self.increments[-1])
            else:
                self.above.append(raw)
        self._close()
        return self.increments

    def _open(self, raw: str, heading: "re.Match", number: int) -> None:
        """An increment, headed on this line; the one before it is read to its end."""
        self._close()
        if not self.increments:
            self.first_number = int(heading.group(1))
        name = strip_markup(heading.group(2))
        increment = MarkdownIncrement(name, len(self.increments) + 1)
        increment.source = source_at(self.file, number)
        increment.lines = IncrementLines(raw, name, self.first_number + len(self.increments))
        self.increments.append(increment)
        self.in_stories = False

    def _close(self) -> None:
        """Give the increment read last the description its lines hold."""
        if self.increments:
            self.increments[-1].description_text = self.increments[-1].lines.description

    def _read_line(self, raw: str, increment: MarkdownIncrement) -> None:
        lines = increment.lines
        bullet = _BULLET.match(raw) if self.in_stories else None
        if bullet is not None:
            self._read_bullet(raw, bullet.group(1), increment)
        elif lines.bullets:
            self.in_stories = False
            lines.below.append(raw)
        elif self.in_stories and not raw.strip():
            lines.above.append(raw)
        else:
            self.in_stories = _read_field(raw.strip(), increment)
            (lines.above if self.in_stories or lines.above else lines.described).append(raw)

    def _read_bullet(self, raw: str, named: str, increment: MarkdownIncrement) -> None:
        """A story bullet: the increment delivers the map's story of that name; a name the map lacks is kept as written."""
        found = self.story_map.stories_named([strip_markup(named)])
        increment.lines.bullets.append((raw, found[0] if found else None, found[0].name if found else ""))
        increment.stories = [*increment.stories, *found]



def _read_field(stripped: str, increment: MarkdownIncrement) -> bool:
    """Keep the outcome, slicing notes or decision prompt the line gives increment; true when the line is the label its
    stories follow."""
    if match := _KV_OUTCOME.match(stripped):
        increment.outcome = strip_markup(match.group(1))
    elif match := _KV_SLICING.match(stripped):
        increment.slicing_notes = strip_markup(match.group(1))
    elif match := _KV_DECISION.match(stripped):
        increment.decision_prompt = strip_markup(match.group(1))
    return bool(_KV_STORIES.match(stripped))
