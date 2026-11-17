import json
import shutil
import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect, have_len, raise_error
from mamba import after, before, context, description, it

from harness.e2e_review.e2e_review import E2eReview, E2eReviewRefused, ScheduledReview

TARGET = "move-work-forward-on-session-board/maintain-tickets"
GIVEN = "Tag Ticket Session › Tag a ticket › 1 Given the ticket pet-visits has no tags"
THEN = "Tag Ticket Session › Tag a ticket › 2 Then pet-visits' card shows the tag billing"


class ReportToolStub:
    """harness/e2e_review/report/ as the toolset sees it: each command it was given, and the changed pairs it answers."""

    def __init__(self, pairs: list[dict] | None = None, refusal: str = "") -> None:
        self.pairs = pairs if pairs is not None else []
        self.refusal = refusal
        self.calls: list[list[str]] = []

    def run(self, script: str, *args: str) -> str:
        self.calls.append([script, *args])
        if self.refusal:
            raise E2eReviewRefused(self.refusal)
        return json.dumps(self.pairs) if args and args[0] == "pairs" else ""


class StarterStub:
    def __init__(self) -> None:
        self.started: list[tuple[list[str], Path, dict]] = []

    def __call__(self, command: list[str], cwd: Path, env: dict, log: Path) -> int:
        self.started.append((command, cwd, env))
        return 4242


def changed(key: str) -> dict:
    return {"key": key, "change": "changed", "changedPercent": 0.93, "ours": "screens/2.png", "theirs": "screens/2.png"}


with description("the end-to-end screen review of a project") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="e2e-review-"))
        (self.project / "story_tests" / TARGET).mkdir(parents=True)
        self.tool = ReportToolStub()
        self.starter = StarterStub()
        self.review = E2eReview(self.project, tool=self.tool, starter=self.starter)
        self.sub_epic = self.project / ".sessions" / "local" / "e2e-test-results" / TARGET

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    def run_folder(self, name: str, rows: list[dict] | None = None) -> Path:
        folder = self.sub_epic / name
        (folder / "screens").mkdir(parents=True, exist_ok=True)
        (folder / "results.json").write_text(json.dumps(rows or [{"key": GIVEN, "step": "Given", "screenshot": "screens/1.png"}]), encoding="utf-8")
        return folder

    with context("that opens a walk by hand"):
        with it("should make the walk's run folder under its sub-epic"):
            walk = self.review.walk(TARGET)
            expect(walk.folder.parent).to(equal(self.sub_epic))

        with it("should name the walk as one"):
            expect(self.review.walk(TARGET).name).to(contain("walk-"))

        with it("should refuse a target that is not an epic and sub-epic"):
            expect(lambda: self.review.walk("maintain-tickets")).to(raise_error(E2eReviewRefused))

        with context("with a step walked and judged"):
            with before.each:
                self.walk = self.review.walk(TARGET)
                (self.walk.folder / "screens" / "1.png").write_bytes(b"png")

            with it("should keep the step's row with its verdict and reason"):
                self.review.record_verdict(str(self.walk.folder), GIVEN, "misses the intent", "The board is empty.", screenshot="screens/1.png")
                expect(self.walk.rows[0]["verdict"]).to(equal("misses the intent"))

            with it("should count the step as missed"):
                self.review.record_verdict(str(self.walk.folder), GIVEN, "misses the intent", "The board is empty.", screenshot="screens/1.png")
                expect(self.walk.missed_steps).to(equal([GIVEN]))

            with it("should replace the step when it is walked again"):
                self.review.record_verdict(str(self.walk.folder), GIVEN, "misses the intent", "Empty.", screenshot="screens/1.png")
                self.review.record_verdict(str(self.walk.folder), GIVEN, "meets the intent", "Shows pet-visits.", screenshot="screens/1.png")
                expect(self.walk.rows).to(have_len(1))

            with it("should refuse a step whose screenshot was not saved"):
                record = lambda: self.review.record_verdict(str(self.walk.folder), GIVEN, "meets the intent", "Fine.", screenshot="screens/9.png")  # noqa: E731
                expect(record).to(raise_error(E2eReviewRefused))

    with context("that runs a sub-epic's browser story tests"):
        with it("should start Playwright's story-ui project on the sub-epic's folder"):
            self.review.run(TARGET)
            expect(self.starter.started[0][0][1:]).to(equal(["playwright", "test", "--project=story-ui", f"story_tests/{TARGET}"]))

        with it("should screenshot into the run folder it answers"):
            run = self.review.run(TARGET)
            expect(self.starter.started[0][2]["E2E_RUN"]).to(equal(run.name))

        with it("should refuse a sub-epic with no story tests"):
            expect(lambda: self.review.run("no-such-epic/no-such-sub-epic")).to(raise_error(E2eReviewRefused))

    with context("with a run compared with the accepted run"):
        with before.each:
            self.run_folder("run-1")
            (self.sub_epic / "baseline.json").write_text(json.dumps({"run": "run-1"}), encoding="utf-8")
            self.run2 = self.run_folder("run-2")
            self.tool.pairs = [changed(THEN)]

        with it("should answer each changed pair with both screenshots' paths"):
            pair = self.review.changed_pairs(f"{TARGET}/run-2")[0]
            expect((pair["theirs"], pair["ours"])).to(equal((str(self.sub_epic / "run-1" / "screens/2.png"), str(self.run2 / "screens/2.png"))))

        with it("should keep the changed steps beside the run"):
            self.review.changed_pairs(f"{TARGET}/run-2")
            expect(self.review.run_of(f"{TARGET}/run-2").changed_steps).to(equal([THEN]))

        with it("should pass a review verdict, with what it cites, to the review"):
            self.review.record_verdict(f"{TARGET}/run-2", THEN, "intended", "Tags are dark now.", cites="commit abc123")
            expect(self.tool.calls[-1]).to(equal(["review.ts", "verdict", str(self.run2), THEN, "intended", "Tags are dark now.", "--cites", "commit abc123"]))

        with it("should refuse a verdict that is none of the six"):
            expect(lambda: self.review.record_verdict(f"{TARGET}/run-2", THEN, "fine", "ok")).to(raise_error(E2eReviewRefused))

        with it("should accept the run as named by the person, and rewrite its report"):
            self.review.accept(f"{TARGET}/run-2", "Jeff")
            expect(self.tool.calls[-2:]).to(equal([["review.ts", "accept", str(self.run2), "--by", "Jeff"], ["report.ts", str(self.run2)]]))

        with it("should pass the review's refusal on"):
            self.tool.refusal = "run-2 has 1 changed step(s) not judged intended"
            expect(lambda: self.review.accept(f"{TARGET}/run-2", "Jeff")).to(raise_error(E2eReviewRefused, "run-2 has 1 changed step(s) not judged intended"))

    with it("should refuse a run it does not have"):
        expect(lambda: self.review.run_of(f"{TARGET}/run-9")).to(raise_error(E2eReviewRefused))

    with context("with no run yet"):
        with it("should have no latest run"):
            expect(self.review.latest()).to(be_none)


with description("the scheduled e2e run's screen review") as self:
    with before.each:
        self.checkout = Path(tempfile.mkdtemp(prefix="scheduled-review-"))
        self.tool = ReportToolStub()
        self.prompts: list[str] = []
        self.review = E2eReview(self.checkout, "scheduled", tool=self.tool)
        self.scheduled = ScheduledReview(self.checkout, "run-2", self.review, agent_start=lambda prompt, _: self.prompts.append(prompt))
        self.sub_epic = self.checkout / ".sessions" / "scheduled" / "e2e-test-results" / TARGET

    with after.each:
        shutil.rmtree(self.checkout, ignore_errors=True)

    def run_folder(self, name: str) -> Path:
        folder = self.sub_epic / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "results.json").write_text(json.dumps([{"key": THEN}]), encoding="utf-8")
        return folder

    with context("with a sub-epic that has no accepted run"):
        with before.each:
            self.run_folder("run-2")

        with it("should say there is nothing to compare with"):
            expect(self.scheduled.start()[0]).to(contain("no accepted run yet"))

        with it("should start no review agent"):
            self.scheduled.start()
            expect(self.prompts).to(equal([]))

    with context("with a sub-epic whose screens changed against its accepted run"):
        with before.each:
            self.run_folder("run-1")
            (self.sub_epic / "baseline.json").write_text(json.dumps({"run": "run-1"}), encoding="utf-8")
            self.run2 = self.run_folder("run-2")
            self.tool.pairs = [changed(THEN)]

        with it("should count the changed steps"):
            expect(self.scheduled.start()[0]).to(contain("1 changed step(s)"))

        with it("should write the run's compare report"):
            self.scheduled.start()
            expect(self.tool.calls).to(contain(["report.ts", str(self.run2), "--against", str(self.sub_epic / "run-1")]))

        with it("should start the review agent on the run's folder"):
            self.scheduled.start()
            expect(self.prompts[0]).to(contain(str(self.run2)))

        with it("should tell the agent to change no file and accept nothing"):
            self.scheduled.start()
            expect(self.prompts[0]).to(contain("Change no file and accept nothing"))

        with context("and judged by the agent"):
            with before.each:
                self.scheduled.start()
                (self.run2 / "review.json").write_text(json.dumps({"against": "run-1", "pairs": {THEN: {"verdict": "missed by the tests", "reason": "Red on red."}}}), encoding="utf-8")

            with it("should name the latest run's missed step with its sub-epic"):
                expect(self.review.latest().missed_steps).to(equal([f"{TARGET}: {THEN}"]))

            with it("should leave no step unjudged"):
                expect(self.review.latest().unjudged_steps).to(equal([]))

    with context("with no screen changed"):
        with it("should start no review agent"):
            self.run_folder("run-1")
            (self.sub_epic / "baseline.json").write_text(json.dumps({"run": "run-1"}), encoding="utf-8")
            self.run_folder("run-2")
            self.scheduled.start()
            expect(self.prompts).to(equal([]))
