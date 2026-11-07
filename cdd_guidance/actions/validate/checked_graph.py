"""The graph one validate call checks, and the files it is built from."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.graph.violation import Violation
from harness.guidance.practice_catalogue import PracticeCatalogue

from cdd_guidance.actions.project_paths import PathsFromProject
from cdd_guidance.actions.validate.report_files import ReportFiles
from cdd_guidance.actions.validate.graph_json_reader import (
    filter_violations_by_path_prefix,
    load_graph_json_paths,
    violations_from_graph_json_files,
)

# What validate checks for each listed guidance: the guidance, and its fidelity's declared files by format.
CheckedOutputs = list[tuple[Any, dict[str, list[str]]]]


class PathsNotFoundError(FileNotFoundError):
    """Raised when validate is named a path that is not there, or not under the session's root, where the graph reads."""

    def __init__(self, unreadable: list[str], project: Path, session_root: Path) -> None:
        named = "; ".join(f"{path}, read from {project}" for path in unreadable)
        super().__init__(f"validate found no file under the session's root {session_root} at {named}. Name paths from the project's root, or absolute.")


class CheckedGraph(PathsFromProject):
    """The graph a validate call checks: built from just the files the call names, or from the folders its fidelities
    have written when it names none, and written beside the call's report; or the saved graph or node lists the call
    names. Graph node files are named from the session's root, so every path is kept that way here too.

    Validate checks one format of each fidelity, so the declared files of its other formats are left out of the
    report: the formats mirror each other, and judging both reports every finding twice."""

    def __init__(self, session: Any, checked: CheckedOutputs, practices: list[str]) -> None:
        self.session = session
        self._checked = checked
        # The catalogue key of each listed practice, such as clean_engineering; a report keeps only their hits.
        self._practices = practices
        self.unchecked_files = self._other_format_files()

    def prefixes(self, paths: list[str] | None, graph: bool | str | list[str] | None) -> list[str]:
        """The files the graph is built from, from the session's root: the paths the call names in the checked format,
        else, when it names no graph either, the folders holding what each graph-backed fidelity has written."""
        named = [path for path in self._from_session_root(paths) if path not in self.unchecked_files]
        return named or self._from_session_root(self._written_outputs() if graph is None else [])

    def paths(self, graph: bool | str | list[str] | None, prefixes: list[str], reports: ReportFiles) -> list[Path]:
        """The graph files this call checks: a graph built from prefixes and written where reports keeps the call's
        graph, the session's saved graph when graph is true and no file is named, or the graph files graph names."""
        if prefixes and graph in (None, True) and self._practices:
            return [self._built_from(prefixes, reports.graph_file())]
        if graph is True:
            saved = self.session.root / ".context" / "graph.json"
            return [saved] if saved.is_file() else []
        return load_graph_json_paths(graph)

    def violations(self, paths: list[Path], prefixes: list[str]) -> list[Violation]:
        """The listed practices' violations in the files this call checks."""
        found = violations_from_graph_json_files(paths, self._practices or None)
        found = filter_violations_by_path_prefix(found, prefixes)
        return [violation for violation in found if violation.location not in self.unchecked_files]

    def _built_from(self, edited: list[str], destination: Path) -> Path:
        """Build the graph from just the edited files and write it at destination; the saved graph stays as it is. Each
        call writes its own file, so calls running at once never read each other's graph.

        Every graph practice loads, because one builds on another (DDD building blocks come from the clean engineering
        classes); the report keeps only the listed guidance's practice."""
        from harness.graph.graph import Graph

        graph = Graph()
        graph.load_files(str(self.session.root), list(PracticeCatalogue.keys()), edited)
        graph.write_json(str(destination))
        return destination

    def _from_session_root(self, paths: list[str] | None) -> list[str]:
        """Each named path as graph node files record it, relative to the session's root.

        A relative path is read from the project's checkout, where the agent works and every path it sees starts. A
        path that is not there, or not under the session's root, is refused: the graph would be built from nothing,
        and its empty report would read as a clean validate."""
        root = self.session.root
        named = [(item, self._from_project(item)) for item in paths or []]
        unreadable = [item for item, path in named if not path.exists() or not self._under_root(path)]
        if unreadable:
            raise PathsNotFoundError(unreadable, self.session.repo_from_session(), root)
        return [path.relative_to(root).as_posix() for _, path in named]

    def _other_format_files(self) -> set[str]:
        """The declared files of every format validate does not check, as graph node files record them."""
        others = [self._from_project(path) for item, outputs in self._checked for format, paths in outputs.items() if format != item.format for path in paths if "{" not in path]
        return {path.relative_to(self.session.root).as_posix() for path in others if self.session.root in path.parents}

    def _written_outputs(self) -> list[str]:
        """The folders holding what each listed graph-backed guidance's fidelity declares in its checked format and has
        already written. The folder, not the file, because a story map's stories keep their scenarios in files beside
        it."""
        if not self._practices:
            return []
        declared = [path for item, outputs in self._checked for path in outputs.get(item.format, [])]
        found = [self._from_project(path) for path in declared if "{" not in path]
        folders = {path.parent if path.is_file() else path for path in found if path.exists()}
        return sorted(str(folder) for folder in folders if self._under_root(folder))

    def _under_root(self, path: Path) -> bool:
        root = self.session.root
        return path == root or root in path.parents
