"""The file a story map was opened from in a session, and how an edit writes the map back: its own file, then each
format chosen for the fidelity that declares the file, beside it."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.guidance.practice_formats import RenderRequest
from harness.markdown.format import Format

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance

    from cdd_guidance.practices.stories.model.story_model import StoryModel


class StoryMapEditRefused(Exception):
    """An edit the story map will not save: the node cannot take it, or writing the map would change its file beyond
    the edit."""

    def __init__(self, node: Any, operation: str, reason: str) -> None:
        super().__init__(f"{operation} on {getattr(node, 'name', node)} refused: {reason}")
        self.node = node
        self.operation = operation
        self.reason = reason


class OpenedStoryMap:
    """*OpenedStoryMap* is where one story map was read from in a session: the file, the session's Stories practice that
    reads and writes it, and the session that names the file's fidelity and refreshes its graph. It owns the writes of
    that file and of the files rendered beside it.

    A map is edited only while its file reads back exactly as its format writes it: a scenario or an acceptance-test
    file, which the map is merged onto, is opened to be read, and a hand-laid map would lose the text around it.
    ``refusal`` says why an edit is refused."""

    def __init__(self, path: Path, stories: PracticeGuidance, session: Any) -> None:
        self._path = Path(path).resolve()
        self._stories = stories
        self._session = session
        self._read_back = ""

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

    def keep_read_back(self, model: StoryModel) -> None:
        """Keep the map as its own format writes it now, before any edit: a save writes the file only while the file
        still reads that way."""
        self._read_back = self._rendered(model, self.own_format)

    @property
    def refusal(self) -> str:
        """Why an edit is not saved; empty when it is: the file must read back exactly as its format writes the map, so
        saving changes nothing but the edit."""
        if self._read_back.strip() == self._path.read_text(encoding="utf-8").strip():
            return ""
        return f"saving would rewrite {self.file}, a {self.fidelity.name} file, beyond the edit: its text is not laid out as {self.own_format} writes a story map"

    def write(self, model: StoryModel) -> list[Path]:
        """Write model to its own file, then to each other format chosen for its fidelity, beside it with that format's
        extension; refresh the session's graph with the files written. An edit its own format would not read back, such
        as a scenario on a story map, is refused before anything is written."""
        own = self._rendered(model, self.own_format)
        if self._read_again(own).strip() != own.strip():
            raise StoryMapEditRefused(model, "save", f"{self.file} would not keep the edit: {self.own_format} does not read it back")
        written = [self._write(model, self.own_format, self._path)]
        for chosen in self.fidelity.session_output.chosen_formats:
            if Format(chosen) != self.own_format:
                written.append(self._write(model, Format(chosen), self._path.with_suffix(Format(chosen).extension)))
        self._session.graph.refresh([str(path) for path in written])
        self.keep_read_back(model)
        return written

    def _write(self, model: StoryModel, format: Format, path: Path) -> Path:
        path.write_text(self._rendered(model, format, path), encoding="utf-8")
        return path

    def _read_again(self, text: str) -> str:
        """text as its own format reads it and writes it again."""
        model = self._stories.formats.parse(self.own_format, text)
        return self._stories.formats.render(RenderRequest(self.own_format, model, previous=text))["content"]

    def _rendered(self, model: StoryModel, format: Format, path: Path | None = None) -> str:
        """model as format writes it, over the file at path as it is now; a format that writes several files, as code
        does, writes none here, so its text reads back as nothing."""
        target = path or self._path
        previous = target.read_text(encoding="utf-8") if target.is_file() else ""
        content = self._stories.formats.render(RenderRequest(format, model, previous=previous))["content"]
        return content if isinstance(content, str) else ""
