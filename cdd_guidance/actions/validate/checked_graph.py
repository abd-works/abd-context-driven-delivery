"""The graph one validate call checks, and the files it is built from."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.graph.saved_graph import SavedGraph
from harness.graph.violation import Violation
from harness.installation.destination import data_of

from cdd_guidance.actions.validate.report_files import ReportFiles
from cdd_guidance.actions.validate.graph_json_reader import violations_from_graph_json_files


class PathsNotFoundError(FileNotFoundError):
    """Raised when validate is named a path that is not there, or not under the session's root, where the graph reads."""

    def __init__(self, unreadable: list[str], project: Path, session_root: Path) -> None:
        named = "; ".join(f"{path}, read from {project}" for path in unreadable)
        super().__init__(f"validate found no file under the session's root {session_root} at {named}. Name paths from the project's root, or absolute.")


class CheckedGraph:
    """The graph a validate call checks: built from just the files the call names, or from the folders its fidelities
    have written when it names none, and written beside the call's report; or the saved graph or node lists the call
    names. Graph node files are named from the session's root, so every path is kept that way here too.

    It holds the fidelity each listed practice is checked at, which says the format the call checks and where each of
    its formats is written. Validate checks one format of each fidelity, so the declared files of its other formats are
    left out of the report: the formats mirror each other, and judging both reports every finding twice."""

    def __init__(self, session: Any, fidelities: list[Any], edited: list[str] | None, named: bool | str | list[str] | None) -> None:
        self.session = session
        self._fidelities = fidelities
        # The format each fidelity is checked in, read once, so another call changing a fidelity's format mid-way never
        # changes which files this call checks.
        self._formats = [fidelity.format for fidelity in fidelities]
        # What the call names: the files being edited, and a graph (true for the session's saved one, or graph files).
        self._named = named
        self.unchecked_files = self._other_format_files()
        # Read now, so a path that is not there is refused before the call claims any report file.
        self.prefixes = self._prefixes(edited)
        self._built: SavedGraph | None = None
        self.files: list[Path] = []
        self._read_violations: list[Violation] | None = None

    def check_beside(self, reports: ReportFiles) -> list[Path]:
        """The graph files this call checks: a graph built from the prefixes and written where reports keeps the call's
        graph, the session's saved graph when the call names true and no file, or the graph files it names."""
        self.files = self._files(reports)
        return self.files

    def violations(self) -> list[Violation]:
        """The listed practices' violations in the files this call checks: from the graph it built, else from the graph
        files it was named."""
        keys = [fidelity.practice_guidance.key for fidelity in self._fidelities]
        if self._built is not None:
            found = self._built.violations(keys)
        else:
            found = [violation for violation in self._named_violations() if not keys or violation.practice in keys]
        if self.prefixes:
            found = [violation for violation in found if violation.is_under(self.prefixes)]
        return [violation for violation in found if violation.location not in self.unchecked_files]

    def save_at(self, destination: Path) -> None:
        """Keep the graph this call checked at destination, beside a report, so the report's violations stay on their
        nodes: the graph it built, the one graph file it was named, or the violations of the several it was named,
        merged into one node list in the shape ``graph.return_nodes`` answers with."""
        if destination in self.files or not self.files:
            return
        if self._built is not None:
            destination.write_text(self._built.text, encoding="utf-8")
        elif len(self.files) == 1:
            destination.write_bytes(self.files[0].read_bytes())
        else:
            nodes = [self._violating_node(violation) for violation in self._named_violations()]
            destination.write_text(json.dumps(nodes), encoding="utf-8")

    def _named_violations(self) -> list[Violation]:
        """Every violation in the graph files the call names, read once."""
        if self._read_violations is None:
            self._read_violations = violations_from_graph_json_files(self.files)
        return self._read_violations

    def _violating_node(self, violation: Violation) -> dict[str, Any]:
        """One violation as the node it was found on."""
        rule = {"name": violation.rule, "status": "violating", "violations": [data_of(violation)]}
        return {"practice": violation.practice, "node_id": violation.node_id, "rules": [rule]}

    def judged_files(self, on_graph: bool) -> str:
        """Each checked format and its files, for the fidelities judged on this call's graph (on_graph) or on their
        files: a model or code fidelity is judged on the graph when the call checks one."""
        judged = [
            (fidelity, format)
            for fidelity, format in zip(self._fidelities, self._formats)
            if (bool(self.files) and fidelity.is_judged_on_graph) == on_graph
        ]
        return "; ".join(f"{format}: {', '.join(fidelity.output_paths().get(format, []))}" for fidelity, format in judged)

    def _files(self, reports: ReportFiles) -> list[Path]:
        if self.prefixes and self._named in (None, True) and self._fidelities:
            return [self._built_at(reports.graph_file())]
        if self._named is True:
            saved = self.session.root / ".context" / "graph.json"
            return [saved] if saved.is_file() else []
        return self._named_files()

    def _named_files(self) -> list[Path]:
        """The graph files the call names: one path, or several; none for true or nothing."""
        named = self._named
        if not named or named is True:
            return []
        entries = [named] if isinstance(named, str) else named
        return [Path(str(entry).strip()) for entry in entries if str(entry).strip()]

    def _built_at(self, destination: Path) -> Path:
        """Refresh the session's graph with the edited files, read as they are now, keep the nodes read from them as this
        call's graph, and write it at destination for the report; the saved graph stays as it is. Each call writes its
        own file, so calls running at once never read each other's report graph.

        The session's graph holds every practice, because one builds on another (DDD building blocks come from the
        clean engineering classes); the report keeps only the listed guidance's practice."""
        graph = self.session.graph
        graph.refresh(self.prefixes)
        self._built = graph.saved(self.prefixes)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self._built.text, encoding="utf-8")
        return destination

    def _prefixes(self, edited: list[str] | None) -> list[str]:
        """The files the graph is built from, from the session's root: the paths the call names in the checked format,
        else, when it names no graph either, the folders holding what each graph-backed fidelity has written."""
        named = [path for path in self._from_session_root(edited) if path not in self.unchecked_files]
        return named or self._from_session_root(self._written_outputs() if self._named is None else [])

    def _from_session_root(self, paths: list[str] | None) -> list[str]:
        """Each named path as graph node files record it, relative to the session's root.

        A relative path is read from the project's checkout, where the agent works and every path it sees starts. A
        path that is not there, or not under the session's root, is refused: the graph would be built from nothing,
        and its empty report would read as a clean validate."""
        root = self.session.root
        named = [(item, self.session.path_named(item)) for item in paths or []]
        unreadable = [item for item, path in named if not path.exists() or not self._under_root(path)]
        if unreadable:
            raise PathsNotFoundError(unreadable, self.session.repo_path, root)
        return [path.relative_to(root).as_posix() for _, path in named]

    def _other_format_files(self) -> set[str]:
        """The declared files of every format validate does not check, as graph node files record them."""
        others = [
            self.session.path_named(path)
            for fidelity, checked in zip(self._fidelities, self._formats)
            for format, paths in fidelity.output_paths().items()
            if format != checked
            for path in paths
            if "{" not in path
        ]
        return {path.relative_to(self.session.root).as_posix() for path in others if self.session.root in path.parents}

    def _written_outputs(self) -> list[str]:
        """The folders holding what each listed fidelity declares in its checked format and has already written. The
        folder, not the file, because a story map's stories keep their scenarios in files beside it."""
        declared = [path for fidelity, checked in zip(self._fidelities, self._formats) for path in fidelity.output_paths().get(checked, [])]
        found = [self.session.path_named(path) for path in declared if "{" not in path]
        folders = {path.parent if path.is_file() else path for path in found if path.exists()}
        return sorted(str(folder) for folder in folders if self._under_root(folder))

    def _under_root(self, path: Path) -> bool:
        root = self.session.root
        return path == root or root in path.parents
