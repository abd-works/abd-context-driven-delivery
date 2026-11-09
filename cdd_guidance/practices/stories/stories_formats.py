"""Stories' formats: story tests in code are read as files beside the story map that names them."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from harness.guidance.practice_formats import PracticeFormats, RenderRequest


class PracticeOutsideSession(Exception):
    """Raised when a practice is asked to read files by path but works in no session that names their project."""


class StoriesFormats(PracticeFormats):
    """The formats Stories reads and writes. A story test in code carries its epic and sub-epic only in its folders,
    under the story map that names them, so a render from code files reads them as files beside that map, not as one
    run of text; and the TypeScript format is made with the folder of the step library its story tests import."""

    @property
    def adapter_settings(self) -> dict[str, Any]:
        """The folder tests are written under, and the step library folder a pattern names for the TypeScript format."""
        return {**super().adapter_settings, "story_test_folder": self._practice.story_test_folder}

    def read(self, paths: list[str] | str, request: RenderRequest) -> Any:
        """The story map in the files at paths when they are code: the story tests, merged onto the story maps beside
        them. Paths and node paths are named from the project, as every path in a session is."""
        if not request.source_format.is_code:
            return super().read(paths, request)
        named = [Path(entry) for entry in ([paths] if isinstance(paths, str) else paths)]
        project = self._project_of(named)
        entries = [project / entry for entry in named]
        files = [found for entry in entries for found in (sorted(entry.rglob("*")) if entry.is_dir() else [entry])]
        return self._practice.read_files([path for path in files if path.is_file()], project)

    def _project_of(self, named: list[Path]) -> Path:
        """The folder paths are named from: the repository of the session the practice works in. The MCP host serves
        every project from its own folder, so a practice in no session, as a script makes one, takes only absolute
        paths and names its files from the folder those paths share."""
        session = self._practice.session
        if session is not None:
            return session.repo_path
        if not named or not all(path.is_absolute() for path in named):
            raise PracticeOutsideSession(
                f"{type(self._practice).__name__} works in no session, so it has no project to read {[str(path) for path in named]} from"
            )
        shared = Path(os.path.commonpath([str(path) for path in named]))
        return shared if shared.is_dir() else shared.parent
