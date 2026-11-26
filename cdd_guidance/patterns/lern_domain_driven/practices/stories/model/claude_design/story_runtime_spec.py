"""Mamba spec for the story runtime contract the canvas fixtures need: the project's step library must give a host
the scenario's Whens and what its steps bound, and its repositories file the in-memory repositories, or the fixtures
build stops and names what is missing."""

import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import contain, equal, expect, raise_error, be_true

from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures
from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.story_runtime import (
    StoryRuntimeContract,
    StoryRuntimeMissing,
)


def write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


REPOSITORIES = "export function domainRepositories() { return {}; }\n"


with description("the story runtime contract of the LERN canvas fixtures") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.contract = StoryRuntimeContract(self.root)

    with after.each:
        self.folder.cleanup()

    with context("a workspace whose step library is the LERN pattern's story runtime"):
        with before.each:
            write(self.root, "test-utils/story-test/story-test.ts", StoryRuntimeContract.template().read_text(encoding="utf-8"))
            write(self.root, "test-utils/story-test/repositories.ts", REPOSITORIES)

        with it("finds nothing missing"):
            expect(self.contract.missing()).to(equal([]))

        with it("lets the fixtures build go on"):
            self.contract.check()

    with context("a workspace with no step library"):
        with it("names the missing story-test.ts and the template that holds the runtime"):
            expect(lambda: self.contract.check()).to(raise_error(StoryRuntimeMissing))
            message = self._message()
            expect(message).to(contain("test-utils/story-test/story-test.ts"))
            expect(message).to(contain(StoryRuntimeContract.template().as_posix()))

    with context("a step library whose host is not given the scenario's Whens"):
        with before.each:
            write(self.root, "test-utils/story-test/story-test.ts", (
                "export function installStoryHost(next) { host = next; }\n"
                "export function storyBindings() { return {}; }\n"
                "export function withStory(name, bindings) {}\n"
                "host.it(step, async () => { await fn(); });\n"))
            write(self.root, "test-utils/story-test/repositories.ts", REPOSITORIES)

        with it("names the Whens, so a fixture never silently skips the scenario's actions"):
            expect(self.contract.missing()).to(equal(["story-test.ts: the host's it(name, fn, steps) is not given { whens }, "
                                                      "so the canvas cannot replay a scenario's actions"]))

    with context("a step library without storyBindings"):
        with before.each:
            write(self.root, "test-utils/story-test/story-test.ts", (
                "export function installStoryHost(next) { host = next; }\n"
                "export function withStory(name, bindings) {}\n"
                "host.it(step, async () => {}, { whens: precedingWhens });\n"))
            write(self.root, "test-utils/story-test/repositories.ts", REPOSITORIES)

        with it("names the missing export"):
            expect(self.contract.missing()).to(equal(["story-test.ts: no export storyBindings"]))

    with context("a repositories file without the in-memory repositories"):
        with before.each:
            write(self.root, "test-utils/story-test/story-test.ts", StoryRuntimeContract.template().read_text(encoding="utf-8"))
            write(self.root, "test-utils/story-test/repositories.ts", "export function nodeRepositories() { return {}; }\n")

        with it("names domainRepositories"):
            expect(self.contract.missing()).to(equal(["repositories.ts: no export domainRepositories"]))

    with context("the fixtures build on a workspace without the runtime"):
        with it("stops before it bundles anything"):
            fixtures = LernCanvasFixtures(self.root)
            out = self.root / "out" / "canvas-fixtures.js"
            expect(lambda: fixtures.build(["Choose Plan"], out)).to(raise_error(StoryRuntimeMissing))
            expect((self.root / LernCanvasFixtures.work_folder).exists()).to(equal(False))

    with context("the template the pattern ships"):
        with it("sits in the LERN pattern's templates, at the step library folder"):
            expect(StoryRuntimeContract.template().as_posix().endswith(
                "lern_domain_driven/templates/test-utils/story-test/story-test.ts")).to(be_true)

    def _message(self) -> str:
        try:
            self.contract.check()
        except StoryRuntimeMissing as problem:
            return str(problem)
        return ""
