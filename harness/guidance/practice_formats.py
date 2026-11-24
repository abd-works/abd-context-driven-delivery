"""The formats one practice reads and writes, each through its adapter, and the render that converts between them."""
from __future__ import annotations

import importlib
import inspect
import json
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, Self

from harness.guidance.documents import document_in
from harness.guidance.worked_session import NamedPaths, WorkedSession
from harness.installation.data_class import data_field
from harness.markdown.format import Format, SourceDocument

if TYPE_CHECKING:
    from harness.guidance.declared_outputs import DeclaredOutputs
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance

# Text or data a format's adapter parses: a document's text, a code format's tree of files by path, or nothing.
TextOrData = str | bytes | dict[str, Any] | list[Any] | None


class ObjectModel(Protocol):
    """A practice's object model, which a format's adapter reads from text and renders back to it: it names the kind of
    model it is (``semantic_type``)."""

    def semantic_type(self) -> str:
        """The kind of model this is, such as a story map or a class model."""


# Hears each file a read takes, by its path from the project, as it is read.
OnFile = Callable[[str], None] | None


@dataclass(frozen=True)
class Written:
    """What a format's adapter is handed of the file a render is written to: the file as it is now (``previous``), whose
    layout a drawing keeps and whose own words a document keeps, and the folder the files it links to are in
    (``folder``). A format written as several files, such as story tests in code, is handed each file's text by its
    path. It is the part of a *RenderRequest* an adapter is allowed to see, so no adapter is handed the fidelity."""

    previous: str | dict[str, str] = ""
    folder: Path | None = None


class FormatAdapter:
    """One format's adapter, the one contract every format of every practice meets: it reads text into the practice's
    object model (``parse``), opens a file (``read_file``), renders a model back in its format (``render``), and may
    write a render onto a file already there (``reshape``). Each practice's domain root extends it, so a format that
    cannot be opened, or renders by a shape of its own, cannot be written."""

    def parse(self, text: TextOrData, file: str = "") -> Self:
        """The model text holds; read from file, each node names that file."""
        raise NotImplementedError(f"{type(self).__name__} reads no text")

    def render(self, model: ObjectModel, written: Written = Written()) -> Any:
        """model written in this format, onto the file as written holds it."""
        raise NotImplementedError(f"{type(self).__name__} writes no text")

    def read_file(self, path: Path, project: Path, on_file: OnFile = None) -> Self:
        """The model the file at path holds, its nodes naming the file as a path from project; on_file hears the file
        as it is read. By default, the file's text parsed, then placed in the file (``placed_in``)."""
        file = named_from(project, path)
        if on_file is not None:
            on_file(file)
        text = Path(path).read_text(encoding="utf-8")
        return self.parse(text, file).placed_in(file, text)

    def reads_file(self, file: Path, text: str) -> bool:
        """Whether file, which holds text, is one this format writes: many files share an ending, so each format says
        which of them are its own. A format that says nothing reads none."""
        return False

    def placed_in(self, file: str, text: str) -> Self:
        """This model, read from text, the file called file, holding where it was read; a model that names no file of
        its nodes holds nothing more."""
        return self


    def reshape(self, rendered: str, existing: str) -> Reshaped | None:
        """rendered written onto existing, the text a file holds now, keeping every line it has; none for a format that
        leaves that writing to the Render action."""
        return None

    def document_kept_in(self, text: str) -> SourceDocument | None:
        """The document a file of this format holds hidden, which it was drawn from; none for a format that keeps none,
        as every format but a drawing (``harness.drawio.KeepsDocumentInDrawing``, ``harness.whiteboard.KeepsDocumentOnBoard``)."""
        return None

    def keeping(self, rendered: Any, document: SourceDocument) -> Any:
        """rendered, in this format, keeping document hidden; as it is for a format that keeps no document."""
        return rendered


def named_from(project: Path, path: Path) -> str:
    """path as a path from project, with forward slashes; as given when it is not under project."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(Path(project).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


PREVIEW_LENGTH = 40
"""How much of a render's content its ``repr`` shows: enough to tell two renders apart in a failing spec's message."""


class Rendered:
    """What a format's adapter and a fidelity answer for a render: the content in the format written. It writes itself
    as the two fields a render has always answered, ``format`` and ``content``. A render that placed the cells of the
    drawing it is saved onto itself says so (``layout_kept``); only a render drawn in the server does, so it is not
    written with the two fields a worker process answers."""

    def __init__(self, format: Format, content: Any, layout_kept: bool = False) -> None:
        self._format = Format(format)
        self._content = content
        self._layout_kept = layout_kept

    @property
    def layout_kept(self) -> bool:
        """Whether the render already placed each cell of the drawing it is saved onto, where that drawing had it or
        moved over to make room for a cell it added, so the save leaves each where the render put it."""
        return self._layout_kept

    @property
    @data_field
    def format(self) -> Format:
        return self._format

    @property
    @data_field
    def content(self) -> Any:
        """The text written; for a format written as several files, each file's text by its path."""
        return self._content

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Rendered:
        """A render as its two fields wrote it, such as the answer a render's worker process writes."""
        return cls(Format(data["format"]), data["content"])

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Rendered) and (self._format, self._content) == (other._format, other._content)

    def __repr__(self) -> str:
        return f"Rendered({self._format!r}, {str(self._content)[:PREVIEW_LENGTH]!r})"


class KeptMark:
    """What marks a member kept in a file though its model no longer holds it. Every format that writes a render onto a
    file already there, and the Render action, write these words and read them back, so a later render leaves the
    member be: the one definition of the words, of the test that a member is marked already, and of the marking line
    that names a member and says what to do with it."""

    WORDS = "no longer in the model"

    def marks(self, lines: Iterable[str] | str) -> bool:
        """Whether lines, the lines above a member or its text, say it is no longer in the model."""
        return self.WORDS in lines if isinstance(lines, str) else any(self.WORDS in line for line in lines)

    def line_for(self, member: str, then: str) -> str:
        """The marking line a reshaper writes above member, saying it is no longer in the model and what to do: then."""
        return f"---- {self.WORDS}: {member}. {then} ----"


KEPT_MARK = KeptMark()
"""The one mark every format and the Render action write and read."""


@dataclass(frozen=True)
class Reshaped:
    """A rendered shape written onto the text a file already holds, as a format's adapter answers it from
    ``reshape(rendered, existing)``: the text to save, which holds every line existing held, the members only the
    existing file holds, kept in the text and marked as no longer in the model (``Cart.empty``), the members only the
    render holds, added empty (``Cart.add_line``), the members whose opening line the render writes otherwise, and how
    many lines were set apart below the text, where a file whose members a render cannot place keeps what only it held.
    A format with no ``reshape`` leaves the writing to the Render action."""

    text: str
    kept: list[str]
    added: list[str]
    # Each member both hold whose opening line the render writes otherwise than the file, with the render's line
    # (``Cart.total``: ``def total(self, tax: int) -> int:``); the file's own line stays in the text.
    changed: dict[str, str] = field(default_factory=dict)
    # The lines kept below the text under one line saying they are no longer in the model.
    set_apart: int = 0

    @property
    def left_to_move(self) -> list[str]:
        """What waits in the text for a person or an agent to move: each member kept, then, when lines were set apart,
        how many."""
        return [*self.kept, *([f"{self.set_apart} line(s) set apart"] if self.set_apart else [])]


class ExistingText:
    """The text a file holds before a render is written onto it: the check that the text to save loses none of its
    lines, written once for every reshaper, and the lines only it holds set apart below a rendered shape that cannot
    place them."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.lines = text.splitlines()

    def lines_not_in(self, text: str) -> list[str]:
        """Each line this text holds, blank lines aside, that text has nowhere: the lines a render would lose."""
        held = text.splitlines()
        return [line for line in self.lines if line.strip() and not any(line.strip() in kept for kept in held)]

    def set_apart_below(self, rendered: str, comment: str) -> Reshaped:
        """The rendered shape, then the lines only this text holds as comments under one line saying so; lines an
        earlier render set apart are carried over as they are, so a second render changes nothing."""
        marked = next((index for index, line in enumerate(self.lines) if KEPT_MARK.marks(line)), len(self.lines))
        carried = self.lines[marked + 1:]
        unplaced = ExistingText("\n".join(self.lines[:marked])).lines_not_in(rendered)
        apart = carried + [f"{comment} {line}" for line in unplaced]
        if not apart:
            return Reshaped(rendered, [], [])
        heading = f"{comment} ---- {KeptMark.WORDS}: the lines below were in this file and the render did not write them. Move each into the member it belongs to, then delete it. ----"
        return Reshaped("\n".join([*rendered.splitlines(), "", heading, *apart]) + "\n", [], [], set_apart=len(apart))


class OutlinedMember:
    """One member of a file a reshaper outlines, such as a class, an operation, a describe block, or a component's
    hook: its name, where the comments above it start (``lead``), where its own lines start and end, and its indent.
    Each reshaper reads its own language into it; the record and the marker are what they share."""

    def __init__(self, name: str, lead: int, start: int, end: int, indent: str = "") -> None:
        self.name = name
        self.lead = lead
        self.start = start
        self.end = end
        self.indent = indent


def lead_of(lines: list[str], start: int, indent: str, marks: tuple[str, ...], floor: int = 0) -> int:
    """The first of the lines written directly above the line at start, at indent, that open with one of marks, such as
    a comment or a decorator, going no higher than floor; start when none are: where an *OutlinedMember*'s lead is."""
    lead = start
    while lead > floor and lines[lead - 1].startswith(indent) and lines[lead - 1][len(indent):].startswith(marks):
        lead -= 1
    return lead


# What a render converts: text or data in a source format, an object model, or the practice itself, whose own model is
# read from the code of the session it works in.
type RenderContent = TextOrData | ObjectModel | PracticeGuidance


class NoFormatReads(ValueError):
    """A practice was asked for the model of a file none of its formats reads, such as a ``.png`` for Clean
    Engineering. Callers pick files by ``suffixes``, so a file outside them is a broken call."""

    def __init__(self, practice: PracticeGuidance, file: Path) -> None:
        super().__init__(f"No {type(practice).__name__} format reads {file.name}")
        self.file = file


class SourceFormatNotSet(ValueError):
    """A render was asked to read text or data with no format named for it, and the fidelity it works at works in
    none, so nothing says which adapter reads it."""

    def __init__(self, practice: PracticeGuidance) -> None:
        super().__init__(f"source format is not set for {type(practice).__name__}")
        self.practice = practice


@dataclass(frozen=True)
class RenderRequest:
    """One render: the format to write, the content to render and the format it is in, the target file as it is now,
    the folder the files it links to are in, and the fidelity the render works at. The formats are made once, when the
    request is. Practices are shared between the calls of a session, so the request, not the practice, carries what one
    call renders at: its fidelity names the Clean Engineering companion that writes a practice's code, and the format
    content is in when the call names none."""

    format: Format
    content: RenderContent = ""
    source: Format = Format()
    previous: str = ""
    folder: str = ""
    fidelity: FidelityGuidance | None = None

    @property
    def source_format(self) -> Format:
        """The format content is in: the one the call names, else the one the fidelity it works at works in."""
        return self.source or (self.fidelity.format if self.fidelity is not None else Format())

    @property
    def companion(self) -> FidelityGuidance | None:
        """The Clean Engineering fidelity that accompanies the fidelity this render works at; none when it has none."""
        return self.fidelity.clean_engineering if self.fidelity is not None else None

    @property
    def written(self) -> Written:
        """What the adapter that writes this render is handed: the target file as it is now and the folder the files it
        links to are in."""
        return Written(self.previous, Path(self.folder) if self.folder else None)

    @classmethod
    def from_files(cls, fidelity: FidelityGuidance, format: str, paths: NamedPaths, source: str | None = None, previous: str = "") -> RenderRequest:
        """The render of the files at paths into format at fidelity, with what it converts read from them, read from the
        project of the session its practice works in, in source, else in the format the fidelity works in. previous is
        the target file as it is now, whose layout a diagram keeps. A renderer that links to other files, such as a
        story map linking to each story's file, finds them in the folder the first path is, or sits in."""
        folder = _folder_holding(paths, fidelity.practice_guidance.session)
        request = cls(Format(format), source=Format(source), previous=previous, folder=folder, fidelity=fidelity)
        return replace(request, content=fidelity.practice_guidance.formats.read(paths, request))

    def render(self) -> Rendered:
        """What this request renders to, through the formats of its fidelity's practice."""
        if self.fidelity is None:
            raise ValueError("a render request renders at a fidelity, and this one names none")
        return self.fidelity.practice_guidance.formats.render(self)

    def _keeping_sketch_wording(self) -> RenderRequest:
        """This request, keeping a sketch's own wording when it renders a sketch to a document format: the sketch is the
        file as it is now. Code is never read from a sketch, so a render to code keeps the request as it is."""
        content = self.content
        from_sketch = self.source == "sketch" and isinstance(content, str) and content.strip()
        if not from_sketch or self.format.is_code:
            return self
        return replace(self, previous=self.previous or content)


class PracticeFormats:
    """The formats one practice reads and writes, each through the adapter the practice was made with. It makes each
    adapter once and keeps it, picks the format that reads a file, and turns a RenderRequest into output. A practice
    with no adapters of its own has the Clean Engineering companion of the fidelity a render works at render for it.

    A practice whose formats read or convert in a way of their own, such as DDD's map that writes itself into a class
    model, names its own kind of formats (``PracticeGuidance.formats_type``)."""

    def __init__(self, practice: PracticeGuidance, adapters: dict[str, Any]) -> None:
        self._practice = practice
        # Each adapter as the practice names it: its class, or the module and class name it is imported from on first use.
        self._named = {Format(name): adapter for name, adapter in adapters.items()}
        self._classes: dict[Format, Any] = {}
        self._made: dict[Format, Any] = {}

    def __contains__(self, format: str) -> bool:
        return Format(str(format)) in self._named

    def __iter__(self) -> Iterator[Format]:
        return iter(self._named)

    def __len__(self) -> int:
        return len(self._named)

    @property
    def supported(self) -> frozenset[Format]:
        """The formats its adapters read and write; none for a practice that has no adapters of its own."""
        return frozenset(self._named)

    def lacking(self, declared: DeclaredOutputs) -> list[str]:
        """What these formats lack of the outputs a fidelity declares, each named, such as ``drawio: no adapter``: a
        declared format with no adapter, or with an adapter that reads no text or writes none. An output named for
        what it holds, such as the story map's ``thin_slice``, is asked for the format of each of its files
        (``thin_slice (whiteboard): no adapter``). A fidelity that declares a format nothing reads and writes offers a
        person a choice that answers nothing, so the gap is named before anyone picks it."""
        found: list[str] = []
        for output in declared.outputs:
            if output in self or Format(output).is_offered:
                found += [f"{output}: {gap}" for gap in self._gaps_of(Format(output))]
            else:
                found += [f"{output} ({format}): {gap}" for format in declared.formats_written_in(output) for gap in self._gaps_of(format)]
        return found

    def _gaps_of(self, format: Format) -> list[str]:
        """What the adapter of format cannot do: nothing is there, it reads no text, or it writes none."""
        if format not in self:
            return ["no adapter"]
        adapter = self.adapter_class(format)
        made_as = adapter if inspect.isclass(adapter) else type(adapter)
        reads = getattr(made_as, "parse", FormatAdapter.parse) is not FormatAdapter.parse
        writes = getattr(made_as, "render", FormatAdapter.render) is not FormatAdapter.render
        return [gap for gap, held in (("its adapter reads no text", reads), ("its adapter writes no text", writes)) if not held]

    def adapter_class(self, format: str) -> type[FormatAdapter] | FormatAdapter:
        """The adapter of format as the practice names it, imported once; raises ValueError for a format it has none
        for."""
        format = Format(format)
        if format not in self._named:
            raise ValueError(f"Unsupported format {str(format)!r}. Choose from: {sorted(self._named)}")
        if format not in self._classes:
            named = self._named[format]
            self._classes[format] = getattr(importlib.import_module(named[0]), named[1]) if isinstance(named, tuple) else named
        return self._classes[format]

    def adapter(self, format: str) -> FormatAdapter:
        """The adapter of format, made once on first use and kept: every render and every read through it uses the
        same one."""
        format = Format(format)
        if format not in self._made:
            self._made[format] = self._made_adapter(format)
        return self._made[format]

    @property
    def adapter_settings(self) -> dict[str, Any]:
        """What an adapter's constructor is handed when it takes it: the folder the practice writes its tests under."""
        return {"tests_root": self._practice.default_workspace_folder}

    def reading(self, file: Path) -> Format | None:
        """The format whose adapter reads the file's extension, such as ``python`` for ``cart_spec.py``; none when none
        does. A format whose adapter names no ``suffixes`` reads no file by its extension."""
        suffix = file.suffix.lower()
        return next((name for name in self._named if suffix in getattr(self.adapter_class(name), "suffixes", ())), None)

    def reading_with(self, file: Path, others: Iterable[PracticeGuidance]) -> Format | None:
        """The format that reads the file among these formats, else among the formats of others in their order: a
        Stories acceptance test in ``.ts`` is read by no Stories format, but by another practice's TypeScript model.
        None when no practice reads it. The graph names a node's file language by it, and the catalog an example's."""
        found = (practice.formats.reading(file) for practice in others)
        return self.reading(file) or next((name for name in found if name is not None), None)

    def for_file(self, file: Path) -> FormatAdapter:
        """A new model of the format that reads file (``reading``). Raises *NoFormatReads* when none of them reads it."""
        name = self.reading(file)
        if name is None:
            raise NoFormatReads(self._practice, file)
        return self.adapter_class(name)()

    @property
    def suffixes(self) -> frozenset[str]:
        """Every file extension one of these formats reads, such as ``.py`` and ``.ts``: the files the practice's graph
        reading reads, the same table ``for_file`` picks a format from."""
        return frozenset(suffix for name in self._named for suffix in getattr(self.adapter_class(name), "suffixes", ()))

    def read(self, paths: NamedPaths, request: RenderRequest) -> RenderContent:
        """What request converts from the files at paths: their text, one after another, read from the project of the
        session the practice works in. Formats that read their files another way, such as Stories' story tests, read
        them themselves."""
        return document_in(self._practice.session, "", paths)

    def render(self, request: RenderRequest) -> Rendered:
        """What request renders to; a request with no content renders the practice's own model. With no adapters of its
        own, the practice has the Clean Engineering companion of the fidelity the request works at render it, at that
        companion fidelity."""
        if request.content in ("", None):
            request = replace(request, content=self._practice)
        source = request.source_format or self._practice.format
        if not self._named:
            return self._companion_render(request, source)
        model = self._object_model(request.content, source)
        target = self.adapter(request.format)
        drawn_from = self._document_drawn_from(request.content, source)
        written = request._keeping_sketch_wording().written
        if drawn_from is not None and drawn_from.format == request.format and not written.previous:
            written = replace(written, previous=drawn_from.text)
        rendered = target.render(self.model_for(target, model), written)
        kept = drawn_from or self._document_of(request.content, source)
        return Rendered(request.format, target.keeping(rendered, kept) if kept is not None else rendered)

    def _document_drawn_from(self, content: RenderContent, source: Format) -> SourceDocument | None:
        """The document content, a drawing in source, keeps hidden, which it was drawn from: a render back into that
        document's format writes over it, as the file it replaces, so the words the drawing cannot show come back; none
        for content that is no drawing, or keeps no document."""
        if not isinstance(content, str) or source not in self:
            return None
        return self.adapter(source).document_kept_in(content)

    def _document_of(self, content: RenderContent, source: Format) -> SourceDocument | None:
        """content as the document a drawing rendered from it keeps: text in source; none for an object model, guidance,
        or the files of a code format."""
        if not isinstance(content, str) or not content.strip() or not source:
            return None
        return SourceDocument(source, content)

    def parse(self, format: Format, content: TextOrData) -> ObjectModel:
        """The model format's adapter reads from content. A model that says it holds only classes, such as a DDD map
        with no aggregate in it, is read by the formats of the practice this one extends, through that practice's own
        adapter."""
        parsed = self.adapter(format).parse(self._incoming(format, content))
        extended = self._practice.working_set.extended
        if extended is not None and getattr(parsed, "holds_classes_only", False):
            return extended.formats.parse(format, content)
        return parsed

    def model_for(self, target: FormatAdapter, model: ObjectModel) -> ObjectModel:
        """The object model in the form target renders; formats that read another practice's model convert it here."""
        return model

    def _companion_render(self, request: RenderRequest, source: Format) -> Rendered:
        companion = request.companion
        owner = companion.practice_guidance if companion is not None else None
        if owner is None or owner.formats is self:
            return Rendered(source or request.format, request.content)
        return owner.formats.render(replace(request, fidelity=companion))

    def _object_model(self, content: RenderContent, source: Format) -> ObjectModel:
        """content as an object model: itself when it is one; read from text or data in source; or, for guidance, read
        from the code of the session it works in."""
        if self._is_object_model(content):
            return content
        if not self._is_text_or_data(content):
            return self._model_of_code(content, source)
        if not source:
            raise SourceFormatNotSet(self._practice)
        return self.parse(source, content)

    def _is_object_model(self, content: RenderContent) -> bool:
        return not self._is_text_or_data(content) and callable(getattr(content, "semantic_type", None))

    def _is_text_or_data(self, content: RenderContent) -> bool:
        """Whether content is text or data an adapter parses, rather than an object model or guidance."""
        return content is None or isinstance(content, (str, bytes, dict, list))

    def _model_of_code(self, guidance: PracticeGuidance, source: Format) -> ObjectModel:
        """The model guidance's own code holds, read by the adapter of a code format from the session guidance works
        in; an empty model of a format that is not code."""
        format = source or guidance.format or self._practice.format
        if not format.is_code:
            return self.parse(format, "")
        adapter = self.adapter(format)
        return adapter.parse(self._code_of(guidance.session, adapter))

    def _code_of(self, session: WorkedSession | None, adapter: FormatAdapter) -> dict[str, str]:
        """The files of adapter's kind in the session's root, by path from that root, which the session finds and reads;
        none in no session, or for an adapter that names no file ending."""
        extension = getattr(adapter, "LEAF_EXTENSION", "") or ""
        if not extension or session is None:
            return {}
        root = session.work_root
        found = session.session_files.find(f"{root.as_posix()}/**/*{extension}")
        return {path.relative_to(root).as_posix(): session.paths.document_named("", [str(path)]) for path in found}

    def _made_adapter(self, format: Format) -> FormatAdapter:
        """The format's adapter, made the way its class says: through its own ``create``, with the settings its
        constructor takes (``adapter_settings``), or bare. An adapter whose constructor needs more is used as its class,
        whose operations read and write the format."""
        adapter = self.adapter_class(format)
        if not inspect.isclass(adapter):
            return adapter
        create = getattr(adapter, "create", None)
        if callable(create) and self._takes_no_arguments(create):
            return create()
        taken = inspect.signature(adapter).parameters
        settings = {name: value for name, value in self.adapter_settings.items() if name in taken}
        if settings:
            return adapter(**settings)
        return adapter() if self._takes_no_arguments(adapter) else adapter

    def _takes_no_arguments(self, operation: Callable[..., object]) -> bool:
        required = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        return all(
            parameter.default is not inspect.Parameter.empty or parameter.kind not in required
            for parameter in inspect.signature(operation).parameters.values()
        )

    def _incoming(self, format: Format, content: TextOrData) -> TextOrData:
        """content as format's adapter reads it: a code format reads a tree of files, so JSON text of one is read."""
        if format.is_code and isinstance(content, str) and content.strip()[:1] in ("{", "["):
            return json.loads(content)
        return content


def _folder_holding(paths: NamedPaths, session: WorkedSession | None) -> str:
    """The folder the files at paths sit in, where a renderer finds the files they link to: the first path when it is a
    folder, else its parent. A path is read from the project of session, as the files are, so a path named from the
    project's root never finds the folder of that name in whatever folder the process runs in."""
    first = paths[0] if isinstance(paths, (list, tuple)) and paths else paths
    if not first or not isinstance(first, str):
        return ""
    path = session.paths.path_named(first) if session is not None else Path(first)
    if path.is_dir():
        return str(path)
    return str(path.parent) if path.parent.is_dir() else ""
