"""The test tiers TDD records in a session for the module a fidelity's tests are for, read from the test files and the
folders the fidelity writes under, with what it leaves the agent to decide."""
import json

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices and TDD with the practice catalogue
from space.session import Sessions
from space.session.session_record import MisshapenTestTiersError
from space.session.spec_support.throwaway_project import ThrowawayProject

MODULE = "shop/orders"


def _written(project, path, text="\n"):
    file = project / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")
    return file


with description("the test tiers TDD records for a module's tests") as self:
    with before.each:
        self.throwaway = ThrowawayProject()
        self.project = self.throwaway.root
        _written(self.project, f"{MODULE}/.context/module-context.md", "# shop/orders\n")
        self.session = Sessions(self.project).current()
        self.development = self.session.practice("bdd").guidance.fidelities.called("development")
        self.development.session_output.choose_root(MODULE)

    with after.each:
        self.throwaway.close()

    with context("for BDD development writing under a module's folder, with no test file there yet"):
        with before.each:
            self.said = self.development.supplement_records()

        with it("should record the unit tier for that module, with the test tool of the fidelity's language"):
            expect(self.session.test_tiers.recorded).to(equal({MODULE: {"unit": "mamba"}}))

        with it("should say what the record holds"):
            expect(self.said).to(contain("shop/orders: unit (mamba)"))

        with it("should ask the agent to decide the server and web tiers, which no test file shows, and to record them"):
            expect(self.said).to(contain("cannot tell whether shop/orders", "session.record_test_tier"))

    with context("for files a render saved in the module"):
        with it("should record the server tier for a server story test"):
            self.development.supplement_records([_written(self.project, f"{MODULE}/orders.story.server.spec.py")])
            expect(self.session.test_tiers.of(MODULE)).to(equal({"unit": "mamba", "server": "mamba"}))

        with it("should record the web tier, with playwright, for a browser story test"):
            self.development.supplement_records([_written(self.project, f"{MODULE}/orders.story.ui.spec.ts")])
            expect(self.session.test_tiers.of(MODULE)["web"]).to(equal("playwright"))

        with it("should record nothing for a file that is no test"):
            self.session.test_tiers.record(MODULE, {"unit": "mamba"})
            self.development.supplement_records([_written(self.project, f"{MODULE}/orders.py")])
            expect(self.session.test_tiers.of(MODULE)).to(equal({"unit": "mamba"}))

    with context("for a module whose unit tier is already recorded with another tool"):
        with it("should keep the tool recorded"):
            self.session.test_tiers.record(MODULE, {"unit": "pytest"})
            self.development.supplement_records([_written(self.project, f"{MODULE}/orders_spec.py")])
            expect(self.session.test_tiers.of(MODULE)).to(equal({"unit": "pytest"}))

    with context("for a module whose record already names the server and web tiers"):
        with it("should ask nothing more of that module"):
            self.session.test_tiers.record(MODULE, {"unit": "mamba", "server": "mamba", "web": "playwright"})
            expect(self.development.supplement_records()).not_to(contain("cannot tell whether"))

    with context("for a test file under no module's folder"):
        with before.each:
            self.development.session_output.choose_root("story_tests")
            self.said = self.development.supplement_records([_written(self.project, "story_tests/buy/pay.story.server.spec.py")])

        with it("should record no module"):
            expect(self.session.test_tiers.recorded).to(equal({}))

        with it("should name the file and its tier, and ask the agent to record it for the module it tests"):
            expect(self.said).to(contain("story_tests/buy/pay.story.server.spec.py", "server tier", "session.record_test_tier"))

    with context("for a unit test in a language whose test tool it cannot tell"):
        with before.each:
            self.said = self.development.supplement_records([_written(self.project, f"{MODULE}/orders.spec.ts")])

        with it("should leave the tool unrecorded"):
            expect(self.session.test_tiers.of(MODULE)).to(equal({}))

        with it("should ask the agent to record the tier with the tool the module's tests run with"):
            expect(self.said).to(contain("shop/orders/orders.spec.ts", "test tool"))

    with context("for Clean Engineering code, whose section of the supplement holds no tier rule"):
        with before.each:
            code = self.session.practice("clean_engineering").guidance.fidelities.called("code")
            code.session_output.choose_root(MODULE)
            self.said = code.supplement_records([_written(self.project, f"{MODULE}/orders_spec.py")])

        with it("should say nothing"):
            expect(self.said).to(equal(""))

        with it("should record nothing"):
            expect(self.session.test_tiers.recorded).to(equal({}))

    # The person's answer (2026-11-22): a record for a folder renamed or deleted is reported, and its removal is theirs.
    with context("in a session whose record names a module whose folder is no longer there"):
        with before.each:
            self.session.test_tiers.record("shop/returns", {"unit": "mamba", "server": "mamba"})
            self.said = self.development.supplement_records()

        with it("should report the module and the tiers recorded for it, for the person to remove"):
            expect(self.said).to(contain("shop/returns", "no longer there", "unit (mamba), server (mamba)"))

        with it("should leave the record as it is"):
            expect(self.session.test_tiers.of("shop/returns")).to(equal({"unit": "mamba", "server": "mamba"}))

        with it("should not report a module whose folder is there"):
            expect(self.said).not_to(contain("shop/orders, whose folder"))

    with context("in a session whose record of test tiers is wrongly shaped"):
        with it("should refuse to read it, by name, and record nothing over it"):
            file = self.session.session_file
            held = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {"name": self.session.name}
            _written(self.project, file.relative_to(self.project).as_posix(), json.dumps({**held, "test_tiers": ["unit"]}))
            expect(lambda: self.development.supplement_records()).to(raise_error(MisshapenTestTiersError))
