"""The files a fidelity declares in its outputs: the patterns alone, and what can be answered from them. Where they are
in a session, and which are there, the session's own output answers (space/session's *WrittenFiles*)."""
from __future__ import annotations

import functools
import re
from pathlib import Path

from harness.markdown.format import Format


_DECLARED_PART = re.compile(r"(\{[^{}/]+\}/?|\*\*/|\*)")


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
        files, or no file in format can be named for it."""
        holding = self._holding(source)
        path = self._path_beside(source, format)
        return f"{holding[0][1].start_of(source)}{path}" if holding and path else ""

    def _holding(self, source: str) -> list[tuple[str, DeclaredFile]]:
        """The declared files source is one of, each with the output that declares it."""
        return [(label, declared) for label, files in self._files.items() for declared in files if declared.pattern.search(source)]

    def _path_beside(self, source: str, format: str) -> str:
        """The declared path of the file written in format for source, with each named part read off source: a file of
        the output that declares source first, then, unless that output is named for what it holds, a file of the
        output named for format."""
        holding = self._holding(source)
        parts: dict[str, str] = {}
        for _, declared in holding:
            parts.update(declared.parts_of(source))
        labels = list(dict.fromkeys(label for label, _ in holding))
        written = Format(format)
        candidates = [declared for label in labels for declared in self._files[label] if declared._is_written_in(written)]
        if all(Format(label).is_offered for label in labels):
            candidates += self._files.get(format, [])
        named = (declared.named_with(parts) for declared in candidates)
        return next((path for path in named if path), "")
