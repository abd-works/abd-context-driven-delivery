"""The report files one validate call saves in its session."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.saved_graph import GRAPH_FILE_NAME
from harness.guidance.guidance import FidelityGuidance

if TYPE_CHECKING:
    from cdd_guidance.actions.validate.checked_graph import CheckedGraph
    from space.session.session import Session

# Where, in the session's folder, the whole graph a call builds is written for its judge to read: a graph of its own for
# each report, ignored by git as every saved graph is (``graph.json``), and only the latest of each fidelity kept.
_CONTEXT_FOLDER = ".context"
_CHECKED_GRAPHS_FOLDER = "checked-graphs"


class ReportFiles:
    """The report files a validate call claims in its session, one for each listed guidance's fidelity.

    They are claimed before the graph is built, so the graph the call checks can be built for its judge, and the
    report's violations, with the nodes they were found on, saved beside it for as long as the report is kept. Saving
    them records the run in the session's violation history."""

    def __init__(self, session: Session, fidelities: list[FidelityGuidance]) -> None:
        self._session = session
        self._claimed_for = [(fidelity, self._claimed(fidelity.session_output.validation_reports.new_path())) for fidelity in fidelities]
        self.paths: list[Path] = [path for _, path in self._claimed_for]

    def graph_file(self) -> Path:
        """Where the whole graph the call builds is written, for its judge to read: a file of its first report's own in
        the session's checked graphs, else a file of its own in the session, for a validate that saves no report."""
        folder = Path(self._session.session_path)
        if self.paths:
            graph = self._checked_graphs / self.paths[0].stem / GRAPH_FILE_NAME
            graph.parent.mkdir(parents=True, exist_ok=True)
            return graph
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=folder, prefix="edited-graph-", suffix=".json", delete=False) as file:
            return Path(file.name)

    def save(self, report: str, graph: CheckedGraph) -> None:
        """Save the report into each claimed file, so the board can link to it, with the violations of the graph the
        call checked (its *CheckedGraph*) kept beside each under the same name, and record each in the session's
        violation history: the hits its fidelity's practice found in the files the call checked."""
        history = self._session.folder.violation_history
        for fidelity, path in self._claimed_for:
            path.write_text(report, encoding="utf-8")
            graph.save_at(path.with_suffix(".json"))
            history.record(path, graph.violations_of(fidelity), graph.prefixes)
            self._drop_older_checked_graphs(path)

    def where(self) -> str:
        """The saved reports, or the session's folder when the call claimed none."""
        return ", ".join(str(path) for path in self.paths) if self.paths else str(Path(self._session.session_path))

    @property
    def _checked_graphs(self) -> Path:
        return Path(self._session.session_path) / _CONTEXT_FOLDER / _CHECKED_GRAPHS_FOLDER

    def _drop_older_checked_graphs(self, report: Path) -> None:
        """Remove the whole graphs built for the earlier reports of report's fidelity: their judges have judged them, and
        each runs to a hundred megabytes for a whole repository."""
        fidelity = report.stem.rsplit("-", 1)[0]
        folders = self._checked_graphs.glob(f"{fidelity}-*") if self._checked_graphs.is_dir() else []
        for folder in folders:
            if folder.is_dir() and folder.name.rsplit("-", 1)[0] == fidelity and folder.name < report.stem:
                shutil.rmtree(folder)

    def _claimed(self, dated: Path) -> Path:
        """Create the report file under a name no other call holds. A report's name is dated to the second, so a call
        in the same second as another takes the next number (``…T034343_2.md``); the date stays where the board reads
        it, and the names still sort by time."""
        path, number = dated, 1
        while not self._created(path):
            number += 1
            path = dated.with_name(f"{dated.stem}_{number}{dated.suffix}")
        return path

    def _created(self, path: Path) -> bool:
        """Create path as an empty file; false when another call already holds that name."""
        try:
            path.touch(exist_ok=False)
        except FileExistsError:
            return False
        return True
