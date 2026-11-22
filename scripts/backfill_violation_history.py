"""Rebuild a session's violation history from its saved validation reports alone.

    python scripts/backfill_violation_history.py .sessions/<session> --checkout <checkout> --branch <branch>

The session is read from the project its folder is in, and each report through the fidelity it validated. Each report's run is stamped with the commit its branch had when the report was written, the last commit before the time
its name ends with (``git log -1 --before``); without ``--checkout``, the runs are stamped with no commit. The history is
written again from the reports, oldest first: ``violation-history.jsonl`` in the session's folder.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import cdd_guidance.practices  # noqa: E402,F401 - registers the practices with the practice catalogue
from space.repo.repo import Repo  # noqa: E402
from space.session.sessions import Sessions  # noqa: E402
from space.session.validation.validation_report import ValidationReport  # noqa: E402
from space.session.validation.violation_history import SHORT_SHA, FoundLine, JudgedLine  # noqa: E402


def main() -> int:
    arguments = _arguments()
    folder = Path(arguments.session).resolve()
    session = Sessions.of_project(folder.parents[1]).named(folder.name)
    if session is None:
        raise SystemExit(f"no session called {folder.name} in {folder.parents[1]}")
    outputs = [output for practice in session.own_practices.values() for output in practice.fidelity_outputs]
    reports = [report for output in outputs for report in output.validation_reports.listed()]
    history = session.folder.violation_history
    history.rebuild(reports, _commits(reports, arguments))
    lines = history.lines
    counts = Counter(line.event for line in lines)
    verdicts = Counter(f"{line.verdict}{'' if line.matched else ' (judge only)'}" for line in lines if isinstance(line, JudgedLine))
    print(f"{history.file}: {dict(counts)}; found {sum(isinstance(line, FoundLine) for line in lines)}; judged {dict(verdicts)}")
    return 0


def _commits(reports: list[ValidationReport], arguments: argparse.Namespace) -> dict[str, str]:
    """The commit the branch had when each report's run started; none without a checkout to ask."""
    if not arguments.checkout:
        return {}
    git = Repo.of_project(Path(arguments.checkout)).git
    return {report.name: git.run("log", "-1", "--format=%H", f"--before={report.made_at}", arguments.branch)[:SHORT_SHA] for report in reports}


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session", help="the session's folder, such as .sessions/version-1-refactoring")
    parser.add_argument("--checkout", default="", help="the checkout whose git log names each run's commit")
    parser.add_argument("--branch", default="HEAD", help="the branch the session's work was on")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
