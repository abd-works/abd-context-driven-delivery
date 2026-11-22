"""The report files one validate call saves in its session."""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from harness.graph.saved_graph import GRAPH_FILE_NAME
from harness.installation.context_config import CONTEXT_FOLDER
from space.session.validation.validation_report import ValidationReport

if TYPE_CHECKING:
    from cdd_guidance.actions.validate.checked_fidelity import CheckedFidelity
    from space.session.session import Session

# Where, in the session's work folder, the whole graph a call builds is written for its judge to read: a graph of its own for
# each report, ignored by git as every saved graph is (``graph.json``), and only the latest of each fidelity kept.
_CHECKED_GRAPHS_FOLDER = "checked-graphs"


class ReportFiles:
    """The report files a validate call claims in its session, one *ValidationReport* for each fidelity it checks.

    They are claimed when the call is made, before the graph is built, so the graph the call checks can be built for
    its judge, and the report's violations, with the nodes they were found on, saved beside it for as long as the
    report is kept."""

    def __init__(self, session: Session, checked: list[CheckedFidelity]) -> None:
        self._session = session
        self._reports: list[ValidationReport] = [fidelity.report for fidelity in checked]

    @property
    def reports(self) -> list[ValidationReport]:
        return list(self._reports)

    def graph_file(self) -> Path:
        """Where the whole graph the call builds is written, for its judge to read: a file of its first report's own in
        the session's checked graphs, else a file of its own in the session, for a validate that saves no report."""
        folder = Path(self._session.work_folder)
        if self._reports:
            graph = self._checked_graphs / self._reports[0].file.stem / GRAPH_FILE_NAME
            graph.parent.mkdir(parents=True, exist_ok=True)
            return graph
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=folder, prefix="edited-graph-", suffix=".json", delete=False) as file:
            return Path(file.name)

    def save(self, text: str) -> None:
        """Write text into each claimed report, so the board can link to it, and remove the whole graphs built for the
        earlier reports of its fidelity."""
        for report in self._reports:
            report.write(text)
            self._drop_older_checked_graphs(report)

    def where(self) -> str:
        """The saved reports, or the session's work folder when the call claimed none."""
        return ", ".join(str(report.file) for report in self._reports) if self._reports else str(Path(self._session.work_folder))

    @property
    def _checked_graphs(self) -> Path:
        return Path(self._session.work_folder) / CONTEXT_FOLDER / _CHECKED_GRAPHS_FOLDER

    def _drop_older_checked_graphs(self, report: ValidationReport) -> None:
        """Remove the whole graphs built for the earlier reports of report's fidelity: their judges have judged them,
        and each runs to a hundred megabytes for a whole repository."""
        folders = self._checked_graphs.glob(f"{report.fidelity.slug}-*") if self._checked_graphs.is_dir() else []
        for folder in folders:
            # Each folder is named as the report it was built for, whose own file may be gone.
            if folder.is_dir() and report.is_newer_than(ValidationReport(folder.with_suffix(".md"), report.fidelity)):
                shutil.rmtree(folder, onexc=self._writable_then_retried)

    def _writable_then_retried(self, remove: Callable[[str], Any], path: str, error: BaseException) -> None:
        """Delete path again once it may be written: Windows refuses to delete a file or folder marked read-only, and an
        earlier checked graph can carry that mark, which would fail the whole validate."""
        if not isinstance(error, PermissionError):
            raise error
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        remove(path)
