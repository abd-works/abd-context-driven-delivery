"""The file a render to a diagram or a document saves beside the source it read."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.actions.render.kept_document import KeptDocument
from cdd_guidance.actions.render.render_result import KeptMember, Migration, SavedBoard, SavedFile
from harness.guidance.practice_formats import Rendered
from cdd_guidance.actions.render.rendered_code import RenderHasNoDeclaredPlace
from harness.graph.saved_graph import SavedGraph
from harness.guidance.declared_outputs import RenderPlacement
from harness.guidance.worked_session import WrittenOutput
from harness.markdown.format import Format
from harness.whiteboard import Whiteboard

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance

# The format a whiteboard file is written in, which goes on its board in Claude once written.
WHITEBOARD = "whiteboard"
# The groups of formats a render saves itself: a draw.io file or a whiteboard, and markdown. Code goes into the module it
# belongs to, which only the agent knows, so a render to code answers with the code.
SAVED_GROUPS = ("diagram", "markdown")
# The format a sketch is written in: a sketch is no file its fidelity declares, yet it renders to the fidelity's own file.
_SKETCH = "sketch"


class NothingToRender(ValueError):
    """A render was asked to save the file made from a source that holds no text: the file it would save holds
    nothing either, and written over a drawing or a document a person made, it loses their work."""

    def __init__(self, source: Path) -> None:
        super().__init__(f"{source} is empty, so there is nothing to render from it; name the file that holds the content")
        self.source = source


class RenderedFile:
    """The file one render saves: where the fidelity declares the format for a source that is one of its own files, in
    a session; else beside the source, under the name the fidelity writes the format to, or the source's own name in
    the format. It reads the file as it is before the render, so a diagram keeps
    the layout people gave it and a document keeps the words its source does not hold, and it writes the render there. A whiteboard saved this way also answers with the writes
    that put it on its board in Claude."""

    def __init__(self, path: Path, format: Format, source: Format = Format()) -> None:
        self.path = path
        self.format = format
        # The format the render reads, which says whether a document already there is handed to the render.
        self._source = source
        # What the file held before the render, which a diagram keeps the layout of and a whiteboard's writes are made
        # against.
        self._before = path.read_text(encoding="utf-8") if path.is_file() else ""

    @property
    def previous(self) -> str:
        """The file as it was, which the render keeps what people gave of: a diagram's layout, and a document's own
        words that its source does not hold, such as a story map's title and scope when it is written back from its
        drawing. None for a document rendered from a sketch, which is written from the sketch alone, so the sketch's
        wording is never lost to the document it replaces."""
        return "" if self._source.name == _SKETCH and self.format.group != "diagram" else self._before

    @classmethod
    def from_sources(cls, sources: list[Path], source: Format, format: Format, placement: RenderPlacement, written: WrittenOutput | None = None) -> RenderedFile | None:
        """The file a render of sources, written in source, into format saves. For a first source that is one of the
        fidelity's own files, in a session, it is the file the fidelity declares in format for it, where the fidelity
        declares it (``WrittenOutput.saved_beside``, what the fidelity has written in the session): one drawing of every
        module is saved in the root's ``.context``, not in the first module's folder. Otherwise it is beside the first
        source, under the name placement gives it (``RenderPlacement.name_beside``). None for a format a render does
        not save, for a source that is data rather than a document, such as a saved graph, or when no name can be
        given to it without writing over a source. An empty source file raises *NothingToRender*."""
        if format.group not in SAVED_GROUPS or not sources:
            return None
        first = sources[0]
        empty = next((file for file in sources if file.is_file() and not file.read_text(encoding="utf-8", errors="replace").strip()), None)
        if empty is not None:
            raise NothingToRender(empty)
        placed = written.saved_beside(first, format.name) if written is not None and placement.owns(first, source) and first.is_file() else None
        name = placement.name_beside(first, source, format)
        if placed is None and not name:
            return None
        target = placed or (first if first.is_dir() else first.parent) / name
        return None if target in sources else cls(target, format, source)

    @classmethod
    def from_graph(cls, graph_file: Path, fidelity: FidelityGuidance, format: Format) -> RenderedFile:
        """The file a render of a saved graph into a document saves: the path the fidelity declares for format, its one
        named part, such as the realization's ``{scope}``, named for what the graph was read from
        (``SavedGraph.scope_name``). A graph that holds no file of the practice names no scope, and a fidelity that
        declares no such path names no file: both are refused with *RenderHasNoDeclaredPlace*."""
        placement = fidelity.declared.placement
        piece = f"a document from the saved graph {graph_file.name}"
        if not placement.scoped_paths(format) or not fidelity.session_output.roots:
            raise RenderHasNoDeclaredPlace(piece, format, placement.paths_in(format), "none of them names one file with one named part, in a session")
        root = fidelity.session_output.root
        scope = SavedGraph.from_file(graph_file).scope_name(fidelity.practice_guidance.key, placement, root)
        if not scope:
            raise RenderHasNoDeclaredPlace(piece, format, placement.scoped_paths(format), f"the graph holds no file of {fidelity.practice_guidance.key}, so nothing names what fills its named part")
        return cls(placement.place_for_scope(scope, format).under(root), format, Format("graph"))

    def save(self, rendered: Rendered) -> SavedFile:
        """Write the render into the file, and answer with the file rather than its text, so the agent has nothing to
        place; a whiteboard also answers with its board and the writes that put it there. What only the file already
        there held is put back first (*KeptDocument*), and named in the answer as ``migrate``, each with the file, for
        whoever decides where it belongs."""
        kept = KeptDocument(self.format).onto(self._before, str(rendered.content))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(kept.text, encoding="utf-8")
        migrate: list[Migration] = [KeptMember(self.path, each) for each in kept.left_to_move]
        if self.format.name != WHITEBOARD:
            return SavedFile(rendered, self.path, migrate)
        board = Whiteboard.links_beside(self.path).of(self.path.name) or ""
        return SavedBoard(rendered, self.path, migrate, board, self._board_writes(board, kept.text))

    def _board_writes(self, board: str, content: str) -> list:
        """The store writes that turn the board kept for the file into the board just saved: against the file as it was
        when a board is kept, since that is what the board last had from it; the whole board for a new one."""
        before = Whiteboard.from_text(self._before) if board and self._before else None
        return Whiteboard.from_text(content).batches(before)

