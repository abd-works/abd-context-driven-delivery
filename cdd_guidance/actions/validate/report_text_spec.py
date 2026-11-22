"""BDD spec — a validation report links each graph hit to its file."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, expect
from mamba import before, context, description, it

from harness.graph.location import Location
from harness.graph.violation import FoundBy, FoundOn, Violation
from space.session import Session, Sessions
from cdd_guidance.actions.validate.report_text import ReportText


class _CheckedGraph:
    """The graph a validate checked, as a report reads it: the session it was checked in, its violations, the files it
    was read from, nothing held beside them, no named path it read no node from, and the violations a person accepted,
    which it leaves out."""

    def __init__(self, session: Session, violations: list[Violation], accepted: list[Violation] | None = None) -> None:
        self.session = session
        self._violations = violations
        self._accepted = accepted or []
        self.files = [Path("graph.json")]
        self.held_beside: list[str] = []
        self.edited: list[str] = []
        self.unread: list[str] = []

    def violations(self) -> list[Violation]:
        return list(self._violations)

    def accepted(self) -> list[Violation]:
        return list(self._accepted)


with description("a validation report"):
    with context("with a session report folder under the workspace"):
        with before.each:
            self.temp = tempfile.TemporaryDirectory()
            self.root = Path(self.temp.name)
            self.session_dir = self.root / ".sessions" / "LERN alignment"
            self.session_dir.mkdir(parents=True)
            source = self.root / "src" / "customer" / "account" / "account.ts"
            source.parent.mkdir(parents=True)
            source.write_text("\n" * 286 + "export function credentialsFailure() {}\n", encoding="utf-8")
            self.violations = [
                Violation(
                    FoundBy("limit-operation-parameters", found_on=FoundOn(subject="Operation `credentialsFailure`")),
                    "takes 4 parameters.",
                    Location("src/customer/account/account.ts", 287),
                )
            ]

        with it("should link each finding to its file by absolute path and line"):
            session = Sessions(self.root).named("main")
            session.workpath = self.root
            session.work_folder = self.session_dir
            report_md = ReportText([], _CheckedGraph(session, self.violations)).for_judge()
            report_path = self.session_dir / "validate-clean-engineering-code-src.md"
            report_path.write_text(report_md, encoding="utf-8")
            account = (self.root / "src/customer/account/account.ts").resolve()
            expect(report_md).to(
                contain(f"[src/customer/account/account.ts]({account}#L287)")
            )
            expect(report_md).not_to(contain("vscode://"))
            expect(report_md).not_to(contain("file://"))

        with it("should say how many accepted violations it leaves out and the file that keeps them"):
            session = Sessions(self.root).named("main")
            session.workpath = self.root
            session.work_folder = self.session_dir
            report_md = ReportText([], _CheckedGraph(session, [], self.violations)).for_saving()
            expect(report_md).to(contain("**Accepted violations left out:** 1. A person accepted them as they are, in `.context/violations-accepted.json`"))

        with context("with a candidate a rule that requires a judge listed beside a violation"):
            with before.each:
                session = Sessions(self.root).named("main")
                session.workpath = self.root
                session.work_folder = self.session_dir
                candidate = Violation(
                    FoundBy("when-names-intent-not-interface-gesture", found_on=FoundOn(subject="When `presses the mark`"), requires_judge=True),
                    "names a gesture.",
                    Location("src/customer/account/account.ts", 12),
                )
                self.report = ReportText([], _CheckedGraph(session, [*self.violations, candidate])).for_saving()

            with it("should count the violation alone as a graph violation"):
                expect(self.report).to(contain("**Total graph violations:** 1\n"))

            with it("should count the candidate apart, as one for the judge to read"):
                expect(self.report).to(contain("**Candidates for the judge to read:** 1. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it."))

            with it("should list the candidate as a candidate, not as an error"):
                expect(self.report).to(contain("- [?] **CANDIDATE** **[graph rule]** - "))

            with it("should head the candidate's rule with its candidates, not with graph violations"):
                expect(self.report).to(contain("**Candidates for the judge to read:** 1\n"))
