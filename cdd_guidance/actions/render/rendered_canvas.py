"""The files a render to a Claude Design canvas saves: into the version of the canvas being prepared in the fidelity's root.

The fidelity declares the canvas as ``design-canvas/{version}/project/canvas.json`` in its root. People edit a published
version, and only the person says when the version after it starts (harness/design_canvas/.context/cdr/0001), so the
render writes into the latest version while it is unpublished, starts the first version of a canvas that has none, and
refuses a published latest version (*PublishedVersion*), leaving the agent to ask the person and start the next one
with ``CanvasVersions.start_next()``.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.actions.render.render_result import SavedFiles
from harness.design_canvas.versions import CanvasVersion, CanvasVersions
from harness.guidance.practice_formats import FormatAdapter, Rendered

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance


class CanvasFileNotRendered(ValueError):
    """A render to a canvas would write over a file in the version that no render of its format wrote, such as a screen
    the agent ported or a story canvas's canvas.json, so nothing is saved."""

    def __init__(self, file: Path) -> None:
        super().__init__(f"{file} was not written by this render's format, so the render does not write over it; move it aside or render into another version")
        self.file = file


class RenderedCanvas:
    """Where a render to a canvas is saved: the canvas versions kept in a fidelity's root, and the format's adapter,
    which says which files already there a render of its format wrote."""

    def __init__(self, versions: CanvasVersions, adapter: FormatAdapter) -> None:
        self._versions = versions
        self._adapter = adapter

    @classmethod
    def of(cls, fidelity: FidelityGuidance, format: str) -> RenderedCanvas:
        """The canvas of the fidelity's root, written in format."""
        return cls(CanvasVersions.in_practice_root(fidelity.session_output.root), fidelity.practice_guidance.formats.adapter(format))

    def save(self, rendered: Rendered) -> SavedFiles:
        """Write each of rendered's files, by its path in the version's folder, into the version being prepared, and
        answer the files. Every file is checked before any is written, so a refused render saves nothing."""
        version = self._version()
        files = {version.folder / path: text for path, text in dict(rendered.content).items()}
        for file, text in files.items():
            self._refuse_writing_over(file, text)
        for file, text in files.items():
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text, encoding="utf-8")
        return SavedFiles(rendered, list(files), [])

    def _version(self) -> CanvasVersion:
        """The version being prepared: the latest while it is unpublished, the first when the canvas has none yet; a
        published latest is refused (*PublishedVersion*), since only the person starts the version after it."""
        if self._versions.latest is None:
            return self._versions.start_next()
        return self._versions.unpublished()

    def _refuse_writing_over(self, file: Path, text: str) -> None:
        if not file.is_file():
            return
        held = file.read_text(encoding="utf-8")
        if held != text and not self._adapter.reads_file(file, held):
            raise CanvasFileNotRendered(file)
