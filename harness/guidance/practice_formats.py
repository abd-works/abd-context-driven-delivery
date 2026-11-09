"""The formats one practice reads and writes, each through its adapter, and the render that converts between them."""
from __future__ import annotations

import importlib
import inspect
import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.guidance.documents import document_in
from harness.markdown.format import Format

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance


@dataclass(frozen=True)
class RenderRequest:
    """One render: the format to write, the content to render and the format it is in, the target file as it is now,
    the folder the files it links to are in, and the fidelity the render works at. The formats are made once, when the
    request is. Practices are shared between the calls of a session, so the request, not the practice, carries what one
    call renders at: its fidelity names the Clean Engineering companion that writes a practice's code, and the format
    content is in when the call names none."""

    format: Format
    content: Any = ""
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

    def keeping_sketch_wording(self) -> RenderRequest:
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

    def __contains__(self, format: object) -> bool:
        return Format(str(format)) in self._named

    def __iter__(self) -> Iterator[Format]:
        return iter(self._named)

    def __len__(self) -> int:
        return len(self._named)

    @property
    def supported(self) -> frozenset[Format]:
        """The formats its adapters read and write; none for a practice that has no adapters of its own."""
        return frozenset(self._named)

    def check(self) -> None:
        """Raise ValueError for a format the practice works in but does not write: one its adapters do not read, or,
        for a practice with no adapters, one no fidelity names as its default."""
        practice = self._practice
        format = practice.format
        supported = self.supported
        if not supported and format:
            supported = frozenset(child.default_format for child in practice.fidelities if child.default_format)
        if supported and format and format not in supported:
            raise ValueError(f"Unsupported format {format!r}. Choose from: {sorted(supported)}")

    def adapter_class(self, format: str) -> Any:
        """The adapter of format as the practice names it, imported once; raises ValueError for a format it has none
        for."""
        format = Format(format)
        if format not in self._named:
            raise ValueError(f"Unsupported format {str(format)!r}. Choose from: {sorted(self._named)}")
        if format not in self._classes:
            named = self._named[format]
            self._classes[format] = getattr(importlib.import_module(named[0]), named[1]) if isinstance(named, tuple) else named
        return self._classes[format]

    def adapter(self, format: str) -> Any:
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

    def for_file(self, file: Path) -> Any:
        """A new model of the format that reads file (``reading``). Raises ValueError when none of them reads it."""
        name = self.reading(file)
        if name is None:
            raise ValueError(f"No {type(self._practice).__name__} format reads {file.name}")
        return self.adapter_class(name)()

    @property
    def suffixes(self) -> frozenset[str]:
        """Every file extension one of these formats reads, such as ``.py`` and ``.ts``: the files the practice's graph
        reading reads, the same table ``for_file`` picks a format from."""
        return frozenset(suffix for name in self._named for suffix in getattr(self.adapter_class(name), "suffixes", ()))

    def read(self, paths: list[str] | str, request: RenderRequest) -> Any:
        """What request converts from the files at paths: their text, one after another, read from the project of the
        session the practice works in. Formats that read their files another way, such as Stories' story tests, read
        them themselves."""
        return document_in(self._practice.session, "", paths)

    def render(self, request: RenderRequest) -> dict:
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
        return {"format": request.format, "content": self._call_render(target, self.model_for(target, model), request.keeping_sketch_wording())}

    def parse(self, format: Format, content: Any) -> Any:
        """The model format's adapter reads from content. A model that says it holds only classes, such as a DDD map
        with no aggregate in it, is read by the formats of the practice this one extends, through that practice's own
        adapter."""
        parsed = self.adapter(format).parse(self._incoming(format, content))
        extended = self._practice.extended
        if extended is not None and getattr(parsed, "holds_classes_only", False):
            return extended.formats.parse(format, content)
        return parsed

    def model_for(self, target: Any, model: Any) -> Any:
        """The object model in the form target renders; formats that read another practice's model convert it here."""
        return model

    def _companion_render(self, request: RenderRequest, source: Format) -> dict:
        companion = request.companion
        owner = companion.practice_guidance if companion is not None else None
        if owner is None or owner.formats is self:
            return {"format": source or request.format, "content": request.content}
        return owner.formats.render(replace(request, fidelity=companion))

    def _object_model(self, content: Any, source: Format) -> Any:
        """content as an object model: itself when it is one; read from text or data in source; or, for guidance, read
        from the code of the session it works in."""
        if self._is_object_model(content):
            return content
        if not _is_text_or_data(content):
            return self._model_of_code(content, source)
        if not source:
            raise ValueError("source format is not set")
        return self.parse(source, content)

    def _is_object_model(self, content: Any) -> bool:
        return not _is_text_or_data(content) and callable(getattr(content, "semantic_type", None))

    def _model_of_code(self, guidance: Any, source: Format) -> Any:
        """The model guidance's own code holds, read by the adapter of a code format from the session guidance works
        in; an empty model of a format that is not code."""
        format = source or guidance.format or self._practice.format
        if not format.is_code:
            return self.parse(format, "")
        adapter = self.adapter(format)
        return adapter.parse(self._code_of(guidance.session, adapter))

    def _code_of(self, session: Any, adapter: Any) -> dict[str, str]:
        """The files of adapter's kind in the session's root, by path from that root, which the session finds and reads;
        none in no session, or for an adapter that names no file ending."""
        extension = getattr(adapter, "LEAF_EXTENSION", "") or ""
        if not extension or session is None:
            return {}
        root = session.work_root
        found = session.session_files.find(f"{root.as_posix()}/**/*{extension}")
        return {path.relative_to(root).as_posix(): session.document_named("", [str(path)]) for path in found}

    def _call_render(self, target: Any, parsed: Any, request: RenderRequest) -> Any:
        """Ask target to render parsed, giving it the previous file and the linked files' folder when it takes them."""
        try:
            parameters = inspect.signature(target.render).parameters
        except (TypeError, ValueError):
            return target.render(parsed)
        kwargs: dict[str, Any] = {}
        if "previous" in parameters:
            kwargs["previous"] = request.previous or None
        if request.folder and "workspace" in parameters:
            kwargs["workspace"] = request.folder
        return target.render(parsed, **kwargs)

    def _made_adapter(self, format: Format) -> Any:
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

    def _takes_no_arguments(self, operation: Any) -> bool:
        required = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        return all(
            parameter.default is not inspect.Parameter.empty or parameter.kind not in required
            for parameter in inspect.signature(operation).parameters.values()
        )

    def _incoming(self, format: Format, content: Any) -> Any:
        """content as format's adapter reads it: a code format reads a tree of files, so JSON text of one is read."""
        if format.is_code and isinstance(content, str) and content.strip()[:1] in ("{", "["):
            return json.loads(content)
        return content


def _is_text_or_data(content: Any) -> bool:
    """Whether content is text or data an adapter parses, rather than an object model or guidance."""
    return content is None or isinstance(content, (str, bytes, dict, list))
