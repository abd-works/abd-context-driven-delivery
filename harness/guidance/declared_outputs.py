"""The files a fidelity declares in its outputs, and where they are in the session its practice works in."""
from __future__ import annotations

import functools
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance


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

    def _part(self, token: str, named: set[str]) -> str:
        """The pattern for one part; ``named`` holds the names earlier parts of the same path used."""
        if token == "**/":
            return r"(?:[^/]+/)*"
        if token == "*":
            return r"[^/]*"
        if not token.startswith("{"):
            return re.escape(token)
        name = re.sub(r"\W", "_", token.strip("{}/"))
        folder = "/" if token.endswith("/") else ""
        if name in named:
            return f"(?P={name}){folder}"
        named.add(name)
        return f"(?P<{name}>[^/]+(?:/[^/]+)*)/" if folder else f"(?P<{name}>[^/]+)"


class DeclaredOutputs:
    """The files one fidelity declares, made from its ``outputs`` (each format it writes, with its file, pattern, or
    folder) and made again when they change: whether a path is one of them, and, in the session the fidelity's practice
    works in, where they are and which of them exist. The fidelity holds it (``fidelity.declared``); the session output
    asks it which found files the fidelity declares."""

    def __init__(self, fidelity: FidelityGuidance, outputs: dict[str, str | list[str]]) -> None:
        self._fidelity = fidelity
        self.outputs = dict(outputs)

    @functools.cached_property
    def _files(self) -> dict[str, list[DeclaredFile]]:
        """The files each format of its outputs declares, by format."""
        return {
            label: [DeclaredFile(name) for name in ([names] if isinstance(names, str) else names) if name and not name.endswith("/")]
            for label, names in self.outputs.items()
        }

    def includes(self, path: str, format: str = "") -> bool:
        """Whether path, written from the project's root or absolute, is a file one of the outputs names, in format when
        one is named: a declared file such as ``{bounded_context}/{aggregate}/{aggregate}.ts`` matches the end of a
        path. A declared folder names no file."""
        held = self._files
        chosen = held.get(format, []) if format else [declared for files in held.values() for declared in files]
        return any(declared.pattern.search(path) for declared in chosen)

    def output_paths(self) -> dict[str, list[str]]:
        """Where the fidelity writes each format in the session its practice works in: its declared paths under the
        practice's root there. None when its practice works in no session."""
        session_output = self._fidelity.session_output
        return session_output.written.output_paths() if session_output is not None else {}

    def files(self) -> dict[str, list]:
        """The files the fidelity declares, by format, in the session its practice works in, each with its path from the
        project and whether it exists; none when its practice works in no session."""
        session_output = self._fidelity.session_output
        return session_output.written.files() if session_output is not None else {}

    def has_output(self) -> bool:
        """Whether a file the fidelity declares is already in the session its practice works in, such as one a person
        wrote; false when its practice works in no session."""
        session_output = self._fidelity.session_output
        return session_output is not None and session_output.written.has_output()

    def files_to_review(self) -> dict[str, list]:
        """The files a person reviews for the fidelity, by format: its own, or those of the fidelities of its practice it
        reviews files of, in the order it names them, each file once."""
        practice = self._fidelity.practice_guidance
        if not self._fidelity.reviews_files_of or practice is None:
            return self.files()
        reviewed: dict[str, list] = {}
        for name in self._fidelity.reviews_files_of:
            fidelity = practice.fidelities.entries.get(name)
            for label, entries in (fidelity.declared.files() if fidelity is not None else {}).items():
                known = {entry.path for entry in reviewed.get(label, [])}
                reviewed.setdefault(label, []).extend(entry for entry in entries if entry.path not in known)
        return reviewed
