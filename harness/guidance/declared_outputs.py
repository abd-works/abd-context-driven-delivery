"""The files a fidelity declares in its outputs: the patterns alone, and what can be answered from them. Where they are
in a session, and which are there, the session's own output answers (space/session's *WrittenFiles*)."""
from __future__ import annotations

import functools
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from harness.annotations.name import Name
from harness.markdown.format import Format


_DECLARED_PART = re.compile(r"(\{[^{}/]+\}/?|\*\*/|\*)")
# A named part of a declared path, such as ``{scope}`` in ``.context/{scope}-bdd-realization.md``.
_NAMED_PART = re.compile(r"\{([^{}/]+)\}")
# What a name or a pattern fills in a declared path's part.
_FILLED_IN = re.compile(r"[{*?]")
# The one wildcard a declared file name can hold the name of its source in, as ``**/*View.tsx`` does.
_ONE_NAME = "*"
# The folder a document about the folder holding it sits in, such as ``src/ordering/.context/ordering-model.md``.
_CONTEXT_FOLDER = ".context"


class DeclaredFile:
    """A file a fidelity declares in its outputs, such as ``{bounded_context}/{aggregate}/{aggregate}.ts``, as a
    pattern that matches the end of a path. A named folder matches folders at any depth and a named part of a file name
    matches within it; a name used twice must be the same text both times, and ``**/`` and ``*`` keep their glob
    meaning."""

    def __init__(self, declared: str) -> None:
        self._declared = declared

    @functools.cached_property
    def glob(self) -> str:
        """The declared path as the glob a file search reads, which finds every file the pattern can match: a named
        folder is ``**/`` and a named part of a file name is ``*``. A path with no named parts stays the plain path."""
        folders = re.sub(r"\{[^{}/]+\}/", "**/", self._declared)
        return re.sub(r"\{[^{}/]+\}", "*", folders)

    @property
    def is_named(self) -> bool:
        """Whether the declared path has a named part, such as ``{module}``, which a path matching it fills."""
        return bool(_NAMED_PART.search(self._declared))

    @property
    def names_one_path(self) -> bool:
        """Whether the declared path is one plain path, with no named parts or wildcards."""
        return "*" not in self.glob

    @functools.cached_property
    def pattern(self) -> re.Pattern[str]:
        """The pattern, made once."""
        named: set[str] = set()
        parts = [self._part(token, named) for token in _DECLARED_PART.split(self._declared) if token]
        return re.compile(r"(?:^|/)" + "".join(parts) + "$", re.I)

    def parts_of(self, path: str) -> dict[str, str]:
        """The named parts path gives this declared path, such as ``{"module": "harness"}`` for
        ``harness/.context/harness-model.md`` against ``{module}/.context/{module}-model.md``; none when path is not one
        of its files."""
        found = self.pattern.search(path)
        return {name: value for name, value in found.groupdict().items() if value} if found is not None else {}

    def named_with(self, parts: dict[str, str]) -> str:
        """The declared path with each named part written as parts gives it; empty when parts leaves one out, or the
        path is a glob, which names no one file."""
        if "*" in self._declared:
            return ""
        missing = [token for token in re.findall(r"\{([^{}/]+)\}", self._declared) if self._group(token) not in parts]
        if missing:
            return ""
        return re.sub(r"\{([^{}/]+)\}", lambda token: parts[self._group(token.group(1))], self._declared)

    @property
    def fixed_folder(self) -> str:
        """The folders the declared path names outright before its first part a name or a pattern fills in, such as
        ``story_tests`` for ``story_tests/{epic}/{sub-epic}/...``: a file's own folder when nothing is filled in, a
        declared folder itself, and ``.`` for a file the root holds."""
        parts = PurePosixPath(self._declared).parts
        filled = next((index for index, part in enumerate(parts) if _FILLED_IN.search(part)), None)
        if filled is not None:
            return PurePosixPath(*parts[:filled]).as_posix() if filled else "."
        return PurePosixPath(self._declared).as_posix() if self._declared.endswith("/") else PurePosixPath(self._declared).parent.as_posix()

    def own_name_of(self, source: Path) -> str | None:
        """The source's own name, read off this declared path: ``Cart`` for ``CartView.tsx`` against
        ``**/*View.tsx``, ``cart`` for ``cart_spec.py`` against ``**/*_spec.py``, and ``bookshop`` for
        ``.context/bookshop-bdd-realization.md`` against ``.context/{scope}-bdd-realization.md``. None when it does not
        name source, or leaves where the name ends unsaid."""
        before, found, after = PurePosixPath(self._declared).name.partition(_ONE_NAME)
        if found and _ONE_NAME not in after and self._says_where_name_ends(before, after):
            named = re.fullmatch(re.escape(before) + "(.+)" + re.escape(after), source.name)
            if named is not None:
                return named.group(1)
        parts = set(self.parts_of(source.as_posix()).values()) if _NAMED_PART.search(self._declared) and not self._declared.endswith("/") else set()
        return parts.pop() if len(parts) == 1 else None

    def file_name_with(self, name: str) -> str:
        """The declared file name with name where its one wildcard is, such as ``CartView.jsx`` for ``**/*View.jsx``;
        empty when the declared name does not say how a name joins it, as ``*spec.ts`` does not."""
        before, found, after = PurePosixPath(self._declared).name.partition(_ONE_NAME)
        return f"{before}{name}{after}" if found and _ONE_NAME not in after and self._says_where_name_ends(before, after) else ""

    def filled_with(self, names: list[str]) -> str:
        """The declared path with its named parts filled with names in the order they come, so
        ``{bounded_context}/{aggregate}/{aggregate}.py`` with ``ordering`` and ``cart`` is ``ordering/cart/cart.py``;
        empty when names fill too few or too many parts, or the path is a glob, which names no one file."""
        parts = list(dict.fromkeys(_NAMED_PART.findall(self._declared)))
        if not parts or len(parts) != len(names) or _ONE_NAME in self._declared:
            return ""
        filled = dict(zip(parts, names))
        return _NAMED_PART.sub(lambda part: filled[part.group(1)], self._declared)

    def _says_where_name_ends(self, before: str, after: str) -> bool:
        """Whether a declared file name says where the name in it ends: what follows the name starts with a mark or a
        capital, as ``_spec.py``, ``.spec.ts`` and ``View.jsx`` do. ``*spec.ts`` does not: ``cartspec.ts`` and
        ``cart.spec.ts`` both fit it."""
        return bool(before) or (bool(after) and not (after[0].islower() or after[0].isdigit()))

    def _is_written_in(self, format: Format) -> bool:
        """Whether the declared path ends with format's extension, such as ``.drawio``: an output named for what it
        holds, such as the thin slice, declares one file for each format it is written in."""
        return bool(format.extension) and self._declared.endswith(format.extension)

    def start_of(self, path: str) -> str:
        """What path holds before this declared path starts in it, such as ``docs/`` for ``docs/.context/story-map.md``
        against ``.context/story-map.md``; empty when the declared path takes the whole of path, or path is not one of
        its files."""
        found = self.pattern.search(path)
        if found is None:
            return ""
        return path[: found.start() + (1 if found.group(0).startswith("/") else 0)]

    def folder_holding(self, path: str) -> tuple[str, dict[str, str]] | None:
        """Where this declared folder, such as Clean Engineering's ``{module}/``, starts in path, and the named parts it
        reads off the folders holding path, each named folder taking as few folders as it can: ``src/ordering/cart.py``
        is in module ``ordering``, starting at ``src/``. None for a declared file, or a path in no such folder."""
        if not self._declared.endswith("/"):
            return None
        folders = PurePosixPath(path).parent.parts
        for first in range(len(folders) - 1, -1, -1):
            found = self.pattern.match("/".join(folders[first:]) + "/")
            if found is not None:
                start = "/".join(folders[:first]).replace("//", "/")
                return (f"{start}/" if start else ""), {name: value for name, value in found.groupdict().items() if value}
        return None

    def _group(self, name: str) -> str:
        """The name a named part goes by in the pattern: a name such as ``sub-epic`` is no group name as it is written."""
        return re.sub(r"\W", "_", name)

    def _part(self, token: str, named: set[str]) -> str:
        """The pattern for one part; ``named`` holds the names earlier parts of the same path used."""
        if token == "**/":
            return r"(?:[^/]+/)*"
        if token == "*":
            return r"[^/]*"
        if not token.startswith("{"):
            return re.escape(token)
        name = self._group(token.strip("{}/"))
        folder = "/" if token.endswith("/") else ""
        if name in named:
            return f"(?P={name}){folder}"
        named.add(name)
        return f"(?P<{name}>[^/]+(?:/[^/]+)*)/" if folder else f"(?P<{name}>[^/]+)"


class DeclaredOutputs:
    """The files one fidelity declares, made from its ``outputs`` (each format it writes, with its file, pattern, or
    folder) and made again when they change: declarations only, so whether a path is one of them, and the name a render
    of one of them gets, are answered from the patterns alone. The fidelity holds it (``fidelity.declared``); the
    session's output asks it which found files the fidelity declares and where they go in the session."""

    def __init__(self, outputs: dict[str, str | list[str]]) -> None:
        self.outputs = dict(outputs)

    def paths_in(self, format: str) -> list[str]:
        """The paths the fidelity declares in format, a declaration of one path or of several read the same way."""
        names = self.outputs.get(format, [])
        return [names] if isinstance(names, str) else list(names)

    def declared_files(self, format: str) -> list[DeclaredFile]:
        """The files the fidelity declares in format; a declared folder names no file."""
        return self._files.get(format, [])

    def formats_written_in(self, output: str) -> list[Format]:
        """The format each file of output is written in, by its extension, once each: what an output named for what
        it holds, such as the story map's ``thin_slice``, is written as (markdown, a drawing, a whiteboard)."""
        extensions = (PurePosixPath(path).suffix for path in self.paths_in(output) if path and not path.endswith("/"))
        return list(dict.fromkeys(Format.from_extension(extension) for extension in extensions if extension))

    @functools.cached_property
    def _files(self) -> dict[str, list[DeclaredFile]]:
        """The files each format of its outputs declares, by format."""
        return {label: [DeclaredFile(name) for name in self.paths_in(label) if name and not name.endswith("/")] for label in self.outputs}

    def code_folders(self) -> list[str]:
        """The code formats the fidelity writes as a folder for each module, such as Clean Engineering's ``{module}/``:
        each code format one of whose declared paths is a folder. A file it declares in that folder beside it, such as
        ``{module}/{module}.py``, says where a render writes."""
        return [label for label in self.outputs if Format(label).is_code and any(name.endswith("/") for name in self.paths_in(label))]

    def includes(self, path: str, format: str = "") -> bool:
        """Whether path, written from the project's root or absolute, is a file one of the outputs names, in format when
        one is named: a declared file such as ``{bounded_context}/{aggregate}/{aggregate}.ts`` matches the end of a
        path. A declared folder names no file."""
        held = self._files
        chosen = held.get(format, []) if format else [declared for files in held.values() for declared in files]
        return any(declared.pattern.search(path) for declared in chosen)

    def file_name_beside(self, source: str, format: str) -> str:
        """The name of the file the fidelity writes format to, for the source file at source, written from the project's
        root or absolute: the name of the file it declares in format, with each named part read off source where another
        file it declares matches it, so ``harness/.context/harness-model.md`` names ``harness-model.drawio``. A source
        declared in an output named for what it holds, such as the story map's ``thin_slice``, names the file that same
        output declares in format, ``thin-slice.drawio``, never the file of another output. Empty when none of its
        files in format can be named so."""
        return self._path_beside(source, format).rsplit("/", 1)[-1]

    def file_beside(self, source: str, format: str) -> str:
        """The path of the file the fidelity writes format to for the source file at source, one of its own files,
        written from the same place source is: the path it declares in format (``file_name_beside``), starting where
        source's own declared path starts, so ``docs/.context/story-map.md`` places ``docs/.context/story-map.drawio``.
        A declared path that takes the whole of source, such as ``{module}/.context/module-context.md``, places the file
        from the fidelity's root: one ``.context/modules.drawio`` for every module. Empty when source is none of its
        files, or no file in format can be named for it. A code file in a folder the fidelity declares for its code,
        such as ``src/ordering/cart.py`` against ``{module}/``, is one of its files, in the module its folder names."""
        holding = self._holding(source)
        path = self._path_beside(source, format)
        return f"{holding[0][1]}{path}" if holding and path else ""

    def is_in_code_folder(self, source: str) -> bool:
        """Whether source is a code file in a folder the fidelity declares for code in source's own format."""
        return bool(self._held_in_code_folders(source))

    def _holding(self, source: str) -> list[tuple[str, str, dict[str, str]]]:
        """The outputs source is one of, each with where its declared path starts in source and the named parts it reads
        off source: the declared files source matches, else the code folders that hold it."""
        files = [(label, declared.start_of(source), declared.parts_of(source)) for label, files in self._files.items() for declared in files if declared.pattern.search(source)]
        return files or self._held_in_code_folders(source)

    def _held_in_code_folders(self, source: str) -> list[tuple[str, str, dict[str, str]]]:
        """The code formats whose declared folder holds source, a file in that format, each with where the folder
        starts in source and the named parts it reads off it (``DeclaredFile.folder_holding``)."""
        labels = [label for label in self.code_folders() if source.endswith(Format(label).extension)]
        held = ((label, DeclaredFile(name).folder_holding(source)) for label in labels for name in self.paths_in(label))
        return [(label, *found) for label, found in held if found is not None]

    def _path_beside(self, source: str, format: str) -> str:
        """The declared path of the file written in format for source, with each named part read off source: a file of
        the output that declares source first, then, unless that output is named for what it holds, a file of the
        output named for format."""
        holding = self._holding(source)
        parts: dict[str, str] = {}
        for _, _, read in holding:
            parts.update(read)
        labels = list(dict.fromkeys(label for label, _, _ in holding))
        written = Format(format)
        candidates = [declared for label in labels for declared in self._files[label] if declared._is_written_in(written)]
        if all(Format(label).is_offered for label in labels):
            candidates += self._files.get(format, [])
        named = (declared.named_with(parts) for declared in candidates)
        return next((path for path in named if path), "")

    @functools.cached_property
    def placement(self) -> RenderPlacement:
        """Where a render of the fidelity's files, or of others, is saved, as its declared paths place it."""
        return RenderPlacement(self)


@dataclass(frozen=True)
class RenderPlace:
    """Where one piece of a render is saved: the path, named from the fidelity's root when ``from_root``, else as it
    is, beside the render's source or where the source's own declared path starts."""

    path: str
    from_root: bool = True

    def under(self, root: Path) -> Path:
        """The file at this place, for a fidelity whose root is root."""
        return root / self.path if self.from_root else Path(self.path)


class RenderPlacement:
    """Where a render is saved, as one fidelity's declared paths answer it from the patterns alone: the name a drawing
    or a document of a source gets, and the file each piece of rendered code goes to. Where the fidelity has written a
    file in the session is the session's own output to answer (``WrittenOutput.saved_beside``)."""

    # The format a sketch is written in: a sketch is no file its fidelity declares, yet it renders to the fidelity's
    # own file.
    SKETCH = "sketch"

    def __init__(self, declared: DeclaredOutputs) -> None:
        self._declared = declared

    def owns(self, first: Path, source: Format) -> bool:
        """Whether a render of first, written in source, writes one of the fidelity's own files: first is a folder, a
        sketch, a file the fidelity declares, or a code file in a folder it declares for its code."""
        written = first.as_posix()
        return first.is_dir() or source.name == self.SKETCH or self._declared.includes(written) or self._declared.is_in_code_folder(written)

    def name_beside(self, first: Path, source: Format, format: Format) -> str:
        """The name of the file a render of first into format is saved under beside it: the name the fidelity writes
        format to for one of its own files, a sketch, or a folder; else first's own name in format, so a render of
        another file never writes over the fidelity's file. Empty when neither names it: a folder lends no name, a
        source that is data, such as a saved graph, lends none, and neither does one of the fidelity's own files when
        the fidelity writes format as one file for each named part (``writes_by_section``), such as one card file for
        each module: those files are where it goes, never a file named after the source."""
        declared = self._declared.file_name_beside(first.as_posix(), format.name) if self.owns(first, source) else ""
        if not declared and self.writes_by_section(first, format):
            return ""
        own = f"{source.stem_of(first)}{format.extension}" if first.is_file() and (not source or source.is_offered) else ""
        return declared or own

    def writes_by_section(self, first: Path, format: Format) -> bool:
        """Whether a render of first, one of the fidelity's own files, into format is saved as one file for each
        section of it: the fidelity declares format only at paths with a named part, such as the modules fidelity's
        ``{module}/.context/module-context.md``, which nothing in the path of first, such as ``.context/modules.drawio``,
        fills."""
        declared = self._declared.declared_files(format.name)
        own = first.is_file() and self._declared.includes(first.as_posix()) and not self._declared.includes(first.as_posix(), format.name)
        return own and bool(declared) and all(file.is_named for file in declared) and not self._declared.file_name_beside(first.as_posix(), format.name)

    def beside_itself(self, first: Path, source: Format, format: Format) -> Path:
        """The file a render of a source no fidelity's file is named for saves: beside the source, under the source's
        own name in format, without what its own format's files end with, so ``design/cart-sketch.md`` saves
        ``design/cart.md``; for a folder, in the folder under the folder's name."""
        if first.is_dir():
            return first / f"{first.name}{format.extension}"
        return first.parent / f"{source.stem_of(first)}{format.extension}"

    def own_name_of(self, source: Path) -> str | None:
        """The source's own name, read off the first declared file that names it (``DeclaredFile.own_name_of``)."""
        files = (declared for label in self._declared.outputs for declared in self._declared.declared_files(label))
        return next((name for name in (declared.own_name_of(source) for declared in files) if name), None)

    def declares(self, path: str, format: Format) -> bool:
        """Whether path, under the fidelity's root, is a file the fidelity declares in format."""
        return self._declared.includes(path, format.name)

    def paths_in(self, format: Format) -> list[str]:
        """The paths the fidelity declares in format, as it writes them, which a refusal names."""
        return self._declared.paths_in(format.name)

    def section_place(self, names: list[str], format: Format) -> RenderPlace | None:
        """The file a section of rendered code named by names goes to: the first file declared in format whose named
        parts names fill, in order; none when no declared file has a part for each name."""
        filled = (declared.filled_with(names) for declared in self._declared.declared_files(format.name))
        found = next((path for path in filled if path), "")
        return RenderPlace(found) if found else None

    def counterpart_of(self, source: Path, format: Format) -> RenderPlace | None:
        """The file declared in format for the named parts the source's declared path reads off it, where the source's
        declared path starts: ``catalogue/book/book.py`` for ``catalogue/book/book.ts`` against
        ``{bounded_context}/{aggregate}/{aggregate}.ts``. None when no declared path with named parts names the source,
        or format declares none those parts fill."""
        written = source.as_posix()
        for declared in (declared for label in self._declared.outputs for declared in self._declared.declared_files(label) if declared.is_named):
            parts = declared.parts_of(written)
            filled = (other.named_with(parts) for other in self._declared.declared_files(format.name)) if parts else iter(())
            found = next((path for path in filled if path), "")
            if found:
                start = declared.start_of(written)
                return RenderPlace(f"{start}{found}", from_root=not start)
        return None

    def named_for(self, source: Path, name: str, format: Format) -> RenderPlace | None:
        """The file one piece rendered from source goes to when source names it: beside source, at the first file
        declared in format with one named part, filled with name. None for no name, or when format declares no such
        file."""
        if not name:
            return None
        filled = (declared.filled_with([Name(name).snake]) for declared in self._declared.declared_files(format.name))
        found = next((path for path in filled if path), "")
        return RenderPlace((source.parent / found).as_posix(), from_root=False) if found else None

    def beside_source(self, source: Path, format: Format) -> RenderPlace | None:
        """The file one text rendered from source goes to: beside source, or beside the ``.context`` folder a document
        sits in, under the first name declared in format that says how the source's own name joins it, such as
        ``CartView.jsx`` for ``**/*View.jsx``. None when no declared file names the source, or none says how its name
        joins."""
        name = self.own_name_of(source)
        if name is None:
            return None
        folder = source.parent.parent if source.parent.name == _CONTEXT_FOLDER else source.parent
        named = (declared.file_name_with(name) for declared in self._declared.declared_files(format.name))
        found = next((file_name for file_name in named if file_name), "")
        return RenderPlace((folder / found).as_posix(), from_root=False) if found else None

    def scoped_paths(self, format: Format) -> list[str]:
        """The paths declared in format with one named part, which a scope names: ``.context/{scope}-bdd-realization.md``."""
        return [path for path in self.paths_in(format) if len(set(_NAMED_PART.findall(path))) == 1]

    def place_for_scope(self, scope: str, format: Format) -> RenderPlace | None:
        """The file a document of scope, such as what a saved graph was read from, is saved at: the first path
        declared in format with one named part, filled with scope; none when format declares no such path."""
        declared = self.scoped_paths(format)
        return RenderPlace(_NAMED_PART.sub(scope, declared[0])) if declared else None
