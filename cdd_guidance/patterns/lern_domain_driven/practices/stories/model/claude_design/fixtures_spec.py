"""Mamba spec for LERN canvas fixtures: the bundle entry imports every shared story and replays the named stories."""

import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import contain, equal, expect

from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures


with description("LERN canvas fixtures") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        (root / "tests" / "select-plan").mkdir(parents=True)
        (root / "tests" / "select-plan" / "select_plan.story.shared.ts").write_text("// shared story", encoding="utf-8")
        (root / "tests" / "select-plan" / "select_plan.story.domain.spec.ts").write_text("// domain tier", encoding="utf-8")
        (root / "tests" / "select-plan" / "examples").mkdir()
        (root / "tests" / "select-plan" / "examples" / "catalog.examples.ts").write_text("export const ace = 1;", encoding="utf-8")
        self.fixtures = LernCanvasFixtures(root)

    with after.each:
        self.folder.cleanup()

    with context("a workspace with one shared story file"):
        with it("finds only the shared story files"):
            expect([path.name for path in self.fixtures.shared_story_files()]).to(equal(["select_plan.story.shared.ts"]))

        with it("imports the shared story from the entry's folder, without its .ts ending"):
            expect(self.fixtures.entry(["Choose Plan"])).to(contain("import '../../tests/select-plan/select_plan.story.shared';"))

        with it("reaches the story runtime and the domain repositories through the story-test folder"):
            entry = self.fixtures.entry(["Choose Plan"])
            expect(entry).to(contain("from '../../test-utils/story-test/story-test'"))
            expect(entry).to(contain("from '../../test-utils/story-test/repositories'"))

        with it("replays the named stories"):
            expect(self.fixtures.entry(["Choose Plan", "Create Customer"])).to(contain('["Choose Plan", "Create Customer"]'))

        with it("exposes every example fixture module to the screens"):
            entry = self.fixtures.entry(["Choose Plan"])
            expect(entry).to(contain("import * as examples0 from '../../tests/select-plan/examples/catalog.examples';"))
            expect(entry).to(contain("Object.assign({}, examples0)"))

        with it("gives screens no seed pastes when the workspace has no seed overlay"):
            expect(self.fixtures.entry(["Choose Plan"])).to(contain("const seedPastes = (): unknown[] => [];"))

        with it("resets the other test state it is given with the repositories"):
            fixtures = LernCanvasFixtures(self.fixtures.workspace, resettables=["src/payment/payment#paymentGateway"])
            entry = fixtures.entry(["Choose Plan"])
            expect(entry).to(contain("import { paymentGateway as resettable0 } from '../../src/payment/payment';"))
            expect(entry).to(contain("const RESETTABLES: unknown[] = [resettable0];"))
