"""Mistake turn then correction turn — one process each, from _req_* yaml."""
from __future__ import annotations

from pathlib import Path

from context_tools.clean_engineering.clean_engineering import CleanEngineering

SESSION = "workflow-package"
PATH = "utilities/git"
CLI = Path("utilities/git/_cli.py")
INIT = Path("utilities/git/__init__.py")
INTRODUCING = "b3ba7ec2e82b887c5a8208ef712d60e5932bc881"

ORIGINAL_PUBLIC_CLI = '''\
class GitConnectError(RuntimeError):
class GhConnectError(RuntimeError):
class DirtyBranchSwitchError(RuntimeError):
class TicketNotFoundError(LookupError):
def find_git_root(start: str | Path) -> Path | None:
def parse_issue_number(ticket: str) -> int:
def format_github_issue_trailer(owner: str, repo: str, number: int) -> str:
def format_commit_message(subject: str, trailers: dict[str, str]) -> str:
def run_git(root: Path, *args: str) -> str:
def run_gh(*args: str) -> str:
'''


def main() -> None:
    ce = CleanEngineering(
        fidelity="modules", path=PATH, session=SESSION, workspace="."
    )
    ce.workspace.open(ce)

    ce.begin_turn(action="mistake")
    eid = ce.record_mistake(
        artifact=PATH,
        rule="deep-module",
        wrong=(
            "_cli.py exposed ~20+ public helpers and exceptions at module top level "
            "(~86% public symbols). deep-module requires at most 40% public; internal "
            "git/gh subprocess adapters must stay private with a narrow __init__ re-export seam."
        ),
        original=ORIGINAL_PUBLIC_CLI,
        introducing_commit=INTRODUCING,
        tool="clean_engineering",
        fidelity="modules",
    )
    ce.finish_turn(
        prompt="log mistake — deep-module violation on utilities/git/_cli.py",
        result=f"entry_id={eid}",
        context=SESSION,
    )

    improved = (
        f"--- {CLI.as_posix()} ---\n"
        f"{CLI.read_text(encoding='utf-8')}\n\n"
        f"--- {INIT.as_posix()} ---\n"
        f"{INIT.read_text(encoding='utf-8')}"
    )

    ce.begin_turn(action="correction")
    ce.record_correction(
        entry_id=eid,
        improved=improved,
        how=(
            "Prefix _cli internals with _; re-export public seam via __init__.py "
            "only (exceptions + find_git_root + format_* + parse_issue_number)."
        ),
        status="fixed",
    )
    ce.finish_turn(
        prompt="log correction — deep-module _cli privatization",
        result=f"entry_id={eid} fixed",
        context=SESSION,
    )
    print(eid)


if __name__ == "__main__":
    main()
