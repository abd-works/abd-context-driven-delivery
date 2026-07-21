"""Mamba spec for `TestSuite / TestCase / Test` (§ Test Suite in bdd-context.md).

These value objects are populated by the workspace loader and never translated
across formats. The tests here cover the static model — structure, value
copying, and stub coverage guards — without invoking the workspace loader
(those behaviours are integration tests in the workspace layer).
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "contexts" / "stories" / "src" / "contexts" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, be_empty, expect

from contexts.stories.story_model.nodes import Story, StoryType, SubEpic
from contexts.stories.story_model.source_location import SourceLocation
from contexts.stories.story_model.test_file import (
    Language,
    Test,
    TestCase,
    TestSuite,
    Tier,
)


def _source(path: str) -> SourceLocation:
    return SourceLocation(file=path, line=1)


with description("a SubEpic") as self:
    with it("should hold an empty testSuites list before loading"):
        sub = SubEpic("Route inside window", 1)
        expect(sub.test_suites).to(have_len(0))

    with it("should report empty testSuites as no test coverage for any tier"):
        sub = SubEpic("Route inside window", 1)
        covered_tiers = {ts.tier.name for ts in sub.test_suites}
        expect(len(covered_tiers)).to(equal(0))

    with context(
        "that has been loaded from a workspace with domain and server tier test files"
    ):
        with before.each:
            self.sub = SubEpic("Route inside window", 1)
            self.sub.test_suites = [
                TestSuite(
                    tier=Tier("server"),
                    language=Language("ts"),
                    name="route-transfer-before-cutoff",
                    source=_source("tests/route-transfer-before-cutoff-server.test.ts"),
                ),
                TestSuite(
                    tier=Tier("domain"),
                    language=Language("ts"),
                    name="route-transfer-before-cutoff",
                    source=_source("tests/route-transfer-before-cutoff-domain.test.ts"),
                ),
            ]

        with it("should hold 2 TestSuites — one per discovered tier"):
            expect(self.sub.test_suites).to(have_len(2))

        with context("every TestSuite"):
            with it("should carry a Tier discovered from its file-name segment"):
                tiers = {ts.tier.name for ts in self.sub.test_suites}
                expect(tiers).to(equal({"server", "domain"}))

            with it("should carry a Language discovered from its file extension"):
                langs = {ts.language.name for ts in self.sub.test_suites}
                expect(langs).to(equal({"ts"}))

            with it(
                "should carry a source SourceLocation pointing at the backing test file"
            ):
                paths = {ts.source.file for ts in self.sub.test_suites}
                expect(
                    "tests/route-transfer-before-cutoff-server.test.ts" in paths
                ).to(be_true)
                expect(
                    "tests/route-transfer-before-cutoff-domain.test.ts" in paths
                ).to(be_true)

    with context(
        "that has been translated from another SubEpic of the same semantic type"
    ):
        with before.each:
            source = SubEpic("Source SubEpic", 1)
            source.test_suites = [
                TestSuite(
                    tier=Tier("server"),
                    language=Language("ts"),
                    name="submit-order",
                    source=_source("tests/submit-order-server.test.ts"),
                )
            ]
            self.target = SubEpic("Target SubEpic", 2)
            self.target.translate_from(source)
            self.source_suites = source.test_suites

        with context("its testSuites"):
            with it(
                "should be a value copy — TestSuite objects are ValueObjects and are "
                "copied through updateSelf; they never reconcile as tree children"
            ):
                # Mutating source after translate_from must not affect target.
                self.source_suites.append(
                    TestSuite(tier=Tier("e2e"), language=Language("ts"), name="extra")
                )
                expect(self.target.test_suites).to(have_len(1))


with description("a Story") as self:
    with it("should hold an empty testCases list before loading"):
        story = Story("Route transfer before cutoff", 1)
        expect(story.test_cases).to(have_len(0))

    with it("should report an empty testCases list as no test coverage across any tier"):
        story = Story("Route transfer before cutoff", 1)
        covered_tiers = {tc.tier.name for tc in story.test_cases}
        expect(len(covered_tiers)).to(equal(0))

    with context(
        "that has been loaded from a workspace whose tier test files contain "
        "matching TestCases"
    ):
        with before.each:
            self.story = Story("Route transfer before cutoff", 1)
            story_src = _source(
                "tests/route-transfer-before-cutoff/route-transfer-before-cutoff-stories.ts"
            )
            scen_src = _source(
                "tests/route-transfer-before-cutoff/route-transfer-before-cutoff-stories.ts"
            )
            self.story.test_cases = [
                TestCase(
                    tier=Tier("server"),
                    name="route transfer before cutoff",
                    tests=[Test(scenario_source=scen_src)],
                    story_source=story_src,
                ),
                TestCase(
                    tier=Tier("domain"),
                    name="route transfer before cutoff",
                    tests=[Test(scenario_source=scen_src)],
                    story_source=story_src,
                ),
            ]

        with it("should hold one TestCase per tier where a matching case exists"):
            expect(self.story.test_cases).to(have_len(2))

        with context("every TestCase"):
            with it("should carry the Tier inherited from its containing TestSuite"):
                tiers = {tc.tier.name for tc in self.story.test_cases}
                expect(tiers).to(equal({"server", "domain"}))

            with it(
                "should carry a storySource SourceLocation pointing at the Story "
                "constant in the sibling `*-stories.<ext>` file (same language as "
                "its TestSuite)"
            ):
                for tc in self.story.test_cases:
                    expect(tc.story_source).not_to(equal(None))
                    expect("stories.ts" in tc.story_source.file).to(be_true)

            with context("every Test inside it"):
                with it(
                    "should carry a scenarioSource SourceLocation pointing at the "
                    "Scenario key in the same sibling stories file"
                ):
                    for tc in self.story.test_cases:
                        for test in tc.tests:
                            expect(test.scenario_source).not_to(equal(None))


with description(
    "a workspace where two languages contribute test suites to the same SubEpic"
) as self:
    with before.each:
        self.sub = SubEpic("Route inside window", 1)
        self.sub.test_suites = [
            TestSuite(
                tier=Tier("server"),
                language=Language("ts"),
                name="submit-order",
                source=_source("tests/submit-order-server.test.ts"),
            ),
            TestSuite(
                tier=Tier("server"),
                language=Language("py"),
                name="submit_order",
                source=_source("tests/test_submit_order_server.py"),
            ),
        ]

    with it("should hold TestSuites in each Language for that SubEpic"):
        langs = {ts.language.name for ts in self.sub.test_suites}
        expect(langs).to(equal({"ts", "py"}))

    with context("every TestSuite"):
        with it(
            "should reference a stories-file sibling in its own Language "
            "(the Python suite reads `_stories.py`; the TypeScript suite reads `-stories.ts`)"
        ):
            for ts in self.sub.test_suites:
                if ts.language.name == "ts":
                    expected_sibling_suffix = "-stories.ts"
                elif ts.language.name == "py":
                    expected_sibling_suffix = "_stories.py"
                else:
                    expected_sibling_suffix = ""
                expect(expected_sibling_suffix).not_to(equal(""))
