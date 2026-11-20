"""The file a render to a diagram or a document saves beside the source it read."""

from __future__ import annotations

from pathlib import Path
from harness.guidance.declared_outputs import DeclaredOutputs
from harness.markdown.format import Format
from harness.whiteboard import BoardLinks, Whiteboard

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
    def from_sources(cls, sources: list[Path], source: Format, format: Format, declared: DeclaredOutputs | None) -> RenderedFile | None:
        """The file a render of sources, written in source, into format saves. For a first source that is one of the
        fidelity's own files, in a session, it is the file the fidelity declares in format for it, where the fidelity
        declares it (``DeclaredOutputs.saved_beside``): one drawing of every module is saved in the root's ``.context``,
        not in the first module's folder. Otherwise it is beside the first source: under the name the fidelity writes
        format to for one of its own files, a sketch, or a folder; else under the first source's own name in format, so
        a render of another file never writes over the fidelity's file. None
        for a format a render does not save, for a source that is data rather than a document, such as a saved graph,
        or when no name can be given to it without writing over a source. An
        empty source file raises *NothingToRender*."""
        if format.group not in SAVED_GROUPS or not sources:
            return None
        first = sources[0]
        empty = next((file for file in sources if file.is_file() and not file.read_text(encoding="utf-8", errors="replace").strip()), None)
        if empty is not None:
            raise NothingToRender(empty)
        # A folder names no one file, so only a file lends its own name; and only a document, a drawing, or code does:
        # a saved graph is read into the fidelity's file, which the agent names for the work it realizes.
        own_name = f"{source.stem_of(first)}{format.extension}" if first.is_file() and (not source or source.is_offered) else ""
        # A file that is neither one the fidelity declares nor a sketch belongs to no file of the fidelity.
        belongs = declared is not None and (first.is_dir() or source.name == _SKETCH or declared.includes(first.as_posix()))
        placed = declared.saved_beside(first, format.name) if belongs and first.is_file() else None
        name = (declared.file_name_beside(first.as_posix(), format.name) if belongs else "") or own_name
        if placed is None and not name:
            return None
        target = placed or (first if first.is_dir() else first.parent) / name
        return None if target in sources else cls(target, format, source)

    def save(self, rendered: dict) -> dict:
        """Write the render into the file, and answer with the file rather than its text, so the agent has nothing to
        place; a whiteboard also answers with its board and the writes that put it there."""
        content = str(rendered["content"])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(content, encoding="utf-8")
        saved: dict = {"format": rendered["format"], "path": str(self.path)}
        if self.format.name == WHITEBOARD:
            saved.update(self._board_writes(content))
        return saved

    def _board_writes(self, content: str) -> dict:
        """The board kept for the file, and the store writes that turn it into the board just saved: against the file as
        it was when a board is kept, since that is what the board last had from it; the whole board for a new one."""
        board = BoardLinks.beside(self.path).of(self.path)
        before = Whiteboard.from_text(self._before) if board and self._before else None
        return {"board": board, "batches": Whiteboard.from_text(content).batches(before)}

