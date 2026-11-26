"""A judge's verdict read from what the judge agent wrote: alone on a line, or wrapped in the judge's prose."""

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.agent_bdd.agent_bdd_common import JudgeResult

with description("a judge's verdict"):
    with context("alone on its own line"):
        with it("should read the verdict and its reason"):
            verdict = JudgeResult.from_stdout('Checked the output.\n{"verdict": "PASS", "reason": "names the order"}\n')
            expect((verdict.verdict, verdict.reason)).to(equal(("PASS", "names the order")))

    with context("wrapped in the judge's prose"):
        with it("should read the verdict from inside the sentence"):
            verdict = JudgeResult.from_stdout(
                'My answer is {"verdict": "FAIL", "reason": "no total shown"} after reading it twice.')
            expect((verdict.verdict, verdict.reason)).to(equal(("FAIL", "no total shown")))

        with it("should prefer a pass the judge wrote after an earlier fail"):
            verdict = JudgeResult.from_stdout(
                'First {"verdict": "FAIL", "reason": "draft"} then, on reflection, {"verdict": "PASS", "reason": "ok"}.')
            expect(verdict.verdict).to(equal("PASS"))

        with it("should keep the time the judge took"):
            verdict = JudgeResult.from_stdout('So: {"verdict": "PASS", "reason": "ok"}.', elapsed_seconds=4.5)
            expect(verdict.elapsed_seconds).to(equal(4.5))

    with context("with no verdict anywhere"):
        with it("should answer an error that quotes the output"):
            verdict = JudgeResult.from_stdout("I could not decide.")
            expect(verdict.verdict).to(equal("ERROR"))
