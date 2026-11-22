"""One fidelity a validate call checks: the format it checks, the files of that format and of the others, and the
report it saves."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance.declared_outputs import DeclaredFile
from harness.guidance.guidance import FidelityGuidance

if TYPE_CHECKING:
    from space.session.session import Session
    from space.session.validation.validation_report import ValidationReport


class CheckedFidelity:
    """One fidelity a validate call checks, at the format it checks: read once, so another call changing the
    fidelity's format mid-way never changes which files this call checks. Validate checks one format of each fidelity,
    so the declared files of its other formats are left out of the report: the formats mirror each other, and judging
    both reports every finding twice. Graph node files are named from the session's root, so every path is kept that
    way here too."""

    def __init__(self, session: Session, fidelity: FidelityGuidance) -> None:
        self._session = session
        self._fidelity = fidelity
        self._format = fidelity.format

    @property
    def fidelity(self) -> FidelityGuidance:
        return self._fidelity

    @property
    def format(self) -> str:
        return self._format

    @cached_property
    def report(self) -> ValidationReport:
        """The report this call saves for the fidelity, claimed in the session on first read: the call claims it once it
        has refused any path that is not there, and before it builds the graph, so the graph can be built beside it."""
        return self._fidelity.session_output.validation_reports.new()

    @cached_property
    def checked_files(self) -> set[str]:
        """The declared files of the format the call checks."""
        return self._declared_files(in_checked_format=True)

    @cached_property
    def other_format_files(self) -> set[str]:
        """The declared files of every format the call does not check."""
        return self._declared_files(in_checked_format=False)

    @property
    def written_folders(self) -> list[str]:
        """The folders holding what the fidelity declares in its checked format and has already written. The folder,
        not the file, because a story map's stories keep their scenarios in files beside it."""
        declared = self._output_paths.get(self._format, [])
        found = [path for named in declared for path in self._written_at(named)]
        folders = {path.parent if path.is_file() else path for path in found if path.exists()}
        return sorted(str(folder) for folder in folders if self._session.session_files.in_root(folder))

    def judged_files(self, edited: list[str]) -> str:
        """The checked format and its files: the files the call names (edited) when it names any, else the ones the
        fidelity writes in that format."""
        return f"{self._format}: {', '.join(edited or self._output_paths.get(self._format, []))}"

    @property
    def _output_paths(self) -> dict[str, list[str]]:
        return self._fidelity.session_output.written.output_paths()

    def _declared_files(self, in_checked_format: bool) -> set[str]:
        """The declared files of the format validate checks (in_checked_format), or of every format it does not check,
        as graph node files record them. A declared path that names no one file is left out."""
        session = self._session
        declared = [
            session.paths.path_named(path)
            for format, paths in self._output_paths.items()
            if (format == self._format) == in_checked_format
            for path in paths
            if DeclaredFile(path).names_one_path
        ]
        return {session.session_files.from_root(path) for path in declared if path.exists() and session.session_files.in_root(path)}

    def _written_at(self, declared: str) -> list[Path]:
        """Where a declared path is written: the path itself, or, for one with a named part, such as ``src/{module}/``,
        each folder that part can name, which are the folders in the folder above it. A folder whose name opens with a
        dot holds no written output, such as ``.git`` or ``.sessions``."""
        above, named_part, _ = declared.partition("{")
        if not named_part:
            return [self._session.paths.path_named(declared)]
        path = self._session.paths.path_named(above)
        if not above.endswith("/"):
            # The named part is in a file's name, so the files are in the folder itself.
            return [path.parent]
        if not path.is_dir():
            return []
        return [folder for folder in sorted(path.iterdir()) if folder.is_dir() and not folder.name.startswith(".")]
