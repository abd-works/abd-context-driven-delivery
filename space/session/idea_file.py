"""An idea file: one markdown file holding an idea, its `# ` heading and the text under it."""

from __future__ import annotations

import re
from pathlib import Path

_HEADING = "# "
_STORY = re.compile(r"^#+\s*Story:\s*(.+?)\s*$")
_NO_OVERLAYS = re.compile(r"^\s*\**overlays:?\**:?\s*none\b", re.IGNORECASE)


class IdeaFile:
    """One markdown file holding an idea: a backlog item's file in `.sessions/_backlog/`, or the `<name>.md` a ticket's
    session folder keeps, the item's file moved there when it was started. Its heading names the idea; the text under it
    says what the idea is. A missing file reads as no heading and no text."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.is_file()

    @property
    def heading(self) -> str:
        """Its first `# ` heading; empty when it has none."""
        return next((line[len(_HEADING):].strip() for line in self._lines if line.startswith(_HEADING)), "")

    @property
    def text(self) -> str:
        """Its content after its heading, or all of it when it has none."""
        lines = self._lines
        heading_at = next((index for index, line in enumerate(lines) if line.startswith(_HEADING)), None)
        body = lines if heading_at is None else lines[heading_at + 1 :]
        return "\n".join(body).strip()

    @property
    def stories(self) -> list[str]:
        """The stories it names under its `Story:` headings, in order: the stories its work is about."""
        return [story for story, _ in self._story_sections()]

    @property
    def stories_without_overlays(self) -> list[str]:
        """The stories whose section says `Overlays: none`: the ones the session's pattern overlays do not apply to."""
        return [story for story, lines in self._story_sections() if any(_NO_OVERLAYS.match(line) for line in lines)]

    def _story_sections(self) -> list[tuple[str, list[str]]]:
        """Each `Story:` heading's name and the lines under it, up to the next heading."""
        sections: list[tuple[str, list[str]]] = []
        for line in self._lines:
            story = _STORY.match(line)
            if story:
                sections.append((story.group(1), []))
            elif line.startswith("#"):
                sections.append(("", []))
            elif sections:
                sections[-1][1].append(line)
        return [(story, lines) for story, lines in sections if story]

    def write(self, heading: str, text: str) -> None:
        """Write the whole file: heading, when there is one, then text under it."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        headed = f"{_HEADING}{heading}\n\n{text}" if heading else text
        self._path.write_text(headed.rstrip() + "\n", encoding="utf-8")

    def rewrite_text(self, text: str) -> None:
        """Replace the text under its heading, keeping the heading."""
        self.write(self.heading, text)

    @property
    def _lines(self) -> list[str]:
        return self._path.read_text(encoding="utf-8").splitlines() if self.exists() else []
