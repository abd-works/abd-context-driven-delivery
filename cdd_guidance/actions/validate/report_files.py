"""The report files one validate call saves in its session."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from cdd_guidance.actions.validate.graph_json_reader import save_checked_graph


class ReportFiles:
    """The report files a validate call claims in its session, one for each listed guidance's fidelity.

    They are claimed before the graph is built, so the graph the call checks can be written beside its report and a
    report's violations stay on their nodes for as long as the report is kept."""

    def __init__(self, session: Any, fidelities: list[Any]) -> None:
        self._session = session
        self.paths: list[Path] = [self._claimed(fidelity.new_report_path()) for fidelity in fidelities]

    def graph_file(self) -> Path:
        """Where the graph the call builds is written: beside its first report, else a file of its own in the session,
        for a validate that saves no report."""
        if self.paths:
            return self.paths[0].with_suffix(".json")
        folder = Path(self._session.session_path)
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=folder, prefix="edited-graph-", suffix=".json", delete=False) as file:
            return Path(file.name)

    def save(self, report: str, checked_graphs: list[Path]) -> None:
        """Save the report into each claimed file, so the board can link to it, with the graph it checked beside each
        under the same name."""
        for path in self.paths:
            path.write_text(report, encoding="utf-8")
            beside = path.with_suffix(".json")
            if beside not in checked_graphs:
                save_checked_graph(checked_graphs, beside)

    def where(self) -> str:
        """The saved reports, or the session's folder when the call claimed none."""
        return ", ".join(str(path) for path in self.paths) if self.paths else str(Path(self._session.session_path))

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
