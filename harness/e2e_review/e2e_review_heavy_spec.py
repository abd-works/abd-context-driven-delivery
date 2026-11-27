"""Heavy spec: the e2e review's report tool run for real, through Node and npm, from a folder that holds no packages, as
a runtime pinned from a checkout does, since git keeps no node_modules.

Found by the hardening regression run (bolt-5): on the dev lane every e2e-review tool was refused with only
"Node.js v24.19.0", the last line Node printed as it failed to find tsx."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.e2e_review.e2e_review import REPORT_TOOL, E2eReviewRefused, ReportTool


def _copy_without_packages() -> Path:
    """The report tool's folder copied, its node_modules left out."""
    folder = Path(tempfile.mkdtemp(prefix="cdd-e2e-report-")) / "report"
    shutil.copytree(REPORT_TOOL, folder, ignore=shutil.ignore_patterns("node_modules"))
    return folder


def _run_of_one_step() -> Path:
    """A sub-epic's run folder whose results.json holds one step, with no screenshot."""
    run = Path(tempfile.mkdtemp(prefix="cdd-e2e-runs-")) / "an-epic" / "a-sub-epic" / "run-1"
    run.mkdir(parents=True)
    step = {"key": "A Story › A Scenario › 1 Given a step", "step": "Given a step", "screenshot": "", "by": "run by a test", "result": "passed"}
    (run / "results.json").write_text(json.dumps([step]), encoding="utf-8")
    return run


with description("the e2e review's report tool") as self:
    with context("in a folder that holds no packages"):
        with before.all:
            self.folder = _copy_without_packages()
            self.run = _run_of_one_step()
            self.summary = json.loads(ReportTool(self.folder).run("review.ts", "summary", str(self.run)))

        with after.all:
            shutil.rmtree(self.folder.parent, ignore_errors=True)
            shutil.rmtree(self.run.parent.parent.parent, ignore_errors=True)

        with it("should answer the run's summary"):
            expect(self.summary["steps"]).to(equal(1))

        with it("should leave its packages installed for the next command"):
            expect((self.folder / "node_modules").is_dir()).to(be_true)

    with context("with a command that fails"):
        with it("should be refused with the line that names the error, not Node's version"):
            expect(lambda: ReportTool(REPORT_TOOL).run("no-such-script.ts")).to(raise_error(E2eReviewRefused, contain("rror")))
