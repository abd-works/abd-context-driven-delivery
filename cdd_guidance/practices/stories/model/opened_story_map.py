"""The file a story map was opened from in a session, and how an edit writes the map back: its own file, then each
format chosen for the fidelity that declares the file, beside it."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance.practice_formats import RenderRequest
from harness.markdown.format import Format

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from space.session.session import Session

    from cdd_guidance.practices.stories.model.story_model import StoryModel, StoryNode


class StoryMapEditRefused(Exception):
    """An edit the story map will not save: the node cannot take it, or writing the map would change its file beyond
    the edit."""

    def __init__(self, node: StoryNode, operation: str, reason: str) -> None:
        super().__init__(f"{operation} on {node.name} refused: {reason}")
        self.node = node
        self.operation = operation
        self.reason = reason


class OpenedStoryMap:
    """*OpenedStoryMap* is where one story map was read from in a session: the map, the file, the session's Stories
    practice that reads and writes it, and the session that names the file's fidelity and refreshes its graph. It owns
    the writes of that file and of the files rendered beside it.

    A map is edited only while its file reads back exactly as its format writes it: a story map and a scenarios file
    are read by themselves and written back with every line an edit does not touch, so a map laid out by hand is
    edited too, while an acceptance-test file, which is merged onto its story map, is opened to be read. ``refusal``
    says why an edit is refused."""

    def __init__(self, story_map: StoryModel, path: Path, session: Session) -> None:
        self._story_map = story_map
        self._path = Path(path).resolve()
        self._session = session
        # The session's own Stories practice, the one its graph holds, reads and writes the file.
        self._stories = session.graph.practices.of(type(story_map).practice_kind())
        # The map as its own format writes it before any edit: a save writes the file only while the file still reads so.
        self._read_back = self._rendered(self.own_format)

    @property
    def file(self) -> str:
        """The file, as a path from the project."""
        return self._session.from_project(self._path)

    @property
    def fidelity(self) -> FidelityGuidance:
        """The fidelity of the session's Stories practice that declares the file: the story map for story-map.md,
        scenarios for a scenario file, acceptance tests for a story test."""
        return next(fidelity for fidelity in self._stories.fidelities if fidelity.declares(self.file))

    @property
    def own_format(self) -> Format:
        """The format the file is written in, which reads its extension."""
        return Format(self._stories.formats.reading(self._path))

    @property
    def refusal(self) -> str:
        """Why an edit is not saved; empty when it is: the file must read back exactly as its format writes the map, so
        saving changes nothing but the edit."""
        if self._read_back.strip() == self._path.read_text(encoding="utf-8").strip():
            return ""
        return f"saving would rewrite {self.file}, a {self.fidelity.name} file, beyond the edit: its text is not laid out as {self.own_format} writes a story map"

    def write(self) -> list[Path]:
        """Write the map to its own file, then to each other format chosen for its fidelity, beside it with that format's
        extension; refresh the session's graph with the files written. An edit its own format would not read back, such
        as a scenario on a story map, is refused before anything is written."""
        own = self._rendered(self.own_format)
        if not self._reads_back(own):
            raise StoryMapEditRefused(self._story_map, "save", f"{self.file} would not keep the edit: {self.own_format} does not read it back")
        written = [self._write(self.own_format, self._path)]
        if self._story_map.slicing is not None:
            written += self._story_map.slicing.write(self._story_map.increments)
        for chosen in self.fidelity.session_output.chosen_formats:
            if Format(chosen) != self.own_format:
                written.append(self._write(Format(chosen), self._path.with_suffix(Format(chosen).extension)))
        self._session.graph.refresh([str(path) for path in written])
        self._read_back = own
        return written

    @property
    def session_stories(self) -> list[str]:
        """The stories the session names: the part of the map its ticket covers."""
        return self._session.stories

    def acceptance_tests_of(self, story) -> list[str]:
        """The acceptance-test files the session's Stories practice declares that hold story, as paths from the
        project."""
        return [file for file, names in self._acceptance_tests.items() if story.name in names]

    @functools.cached_property
    def _acceptance_tests(self) -> dict[str, list[str]]:
        """The session's story tests with the stories each holds, read once for the map."""
        return self._stories.story_tests(self._session.repo_path)

    def _write(self, format: Format, path: Path) -> Path:
        path.write_text(self._rendered(format, path), encoding="utf-8")
        return path

    def _reads_back(self, text: str) -> bool:
        """Whether text, as its own format reads it, holds the map's nodes and is written as text again."""
        model = self._stories.formats.parse(self.own_format, text)
        again = self._stories.formats.render(RenderRequest(self.own_format, model, previous=text))["content"]
        return _nodes_held(model) == _nodes_held(self._story_map) and again.strip() == text.strip()

    def _rendered(self, format: Format, path: Path | None = None) -> str:
        """The map as format writes it, over the file at path as it is now; a format that writes several files, as code
        does, writes none here, so its text reads back as nothing."""
        target = path or self._path
        previous = target.read_text(encoding="utf-8") if target.is_file() else ""
        content = self._stories.formats.render(RenderRequest(format, self._story_map, previous=previous))["content"]
        return content if isinstance(content, str) else ""


def _nodes_held(story_map: StoryModel) -> list[tuple]:
    """Every epic, story, scenario and step under story_map's epics, as its kind and name, in map order: what a file must
    read back as for an edit to be kept."""
    held: list[tuple] = []
    pending = list(reversed(story_map.epics))
    while pending:
        node = pending.pop()
        held.append((node.semantic_type(), node.name))
        pending.extend(reversed(node.parts))
    return held
