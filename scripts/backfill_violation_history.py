"""Rebuild a session's violation history from its saved validation reports alone.

    python scripts/backfill_violation_history.py .sessions/<session> --checkout <checkout> --branch <branch>

Each report's run is stamped with the commit its branch had when the report was written, the last commit before the time
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

from space.repo.repo import Repo  # noqa: E402
from space.session.violation_history import SHORT_SHA, VIOLATION_HISTORY_FILE, ValidationRun, ViolationHistory  # noqa: E402

_REPORTS_FOLDER = "validation-reports"


def main() -> int:
    arguments = _arguments()
    session = Path(arguments.session).resolve()
    reports = sorted((session / _REPORTS_FOLDER).glob("*.md"))
    history = ViolationHistory(session / VIOLATION_HISTORY_FILE)
    history.rebuild(reports, _commits(reports, arguments))
    counts = Counter(event["event"] for event in history.events)
    verdicts = Counter(f"{event['verdict']}{'' if event['matched'] else ' (judge only)'}" for event in history.events if event["event"] == "judged")
    print(f"{history.file}: {dict(counts)}; judged {dict(verdicts)}")
    return 0


def _commits(reports: list[Path], arguments: argparse.Namespace) -> dict[str, str]:
    """The commit the branch had when each report's run started; none without a checkout to ask."""
    if not arguments.checkout:
        return {}
    git = Repo.of_project(Path(arguments.checkout)).git
    return {report.name: git.run("log", "-1", "--format=%H", f"--before={ValidationRun(report, [], []).at}", arguments.branch)[:SHORT_SHA] for report in reports}


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session", help="the session's folder, such as .sessions/version-1-refactoring")
    parser.add_argument("--checkout", default="", help="the checkout whose git log names each run's commit")
    parser.add_argument("--branch", default="HEAD", help="the branch the session's work was on")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
