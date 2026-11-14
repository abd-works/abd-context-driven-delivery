"""Story rules backed by TypeScript story-test examples, read the way a build reads story tests."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.rules.rule_examples import assert_stories_example_pair, stories_fixture

_EXAMPLES = _REPO / "cdd_guidance/practices/stories/model/typescript/_examples"


with description("a Stories rule example") as self:
    with context("that holds a story test with a scenario"):
        # Read once; the examples only look at the graph.
        with before.all:
            self.graph = stories_fixture(_EXAMPLES / "plain-english-gwt-steps" / "faulty").practice.reading.in_graph

        with it("should read the scenario the story test names, as a build reads it"):
            expect([node.name for node in self.graph.nodes("Scenario")]).to(equal(["a customer submits an order"]))

        with it("should read the story under the epic its folder names"):
            expect([node.name for node in self.graph.nodes("Epic")]).to(equal(["Submit Orders"]))


with description("stories TypeScript story-test examples") as self:
    with context("story-name-captures-system-mechanic"):
        with it("should flag Handle Request and accept Submit Order"):
            assert_stories_example_pair("story-name-captures-system-mechanic")

    with context("plain-english-gwt-steps"):
        with it("should flag camelCase given steps"):
            assert_stories_example_pair("plain-english-gwt-steps")

    with context("right-size-story-nodes"):
        with it("should flag near-duplicate story names"):
            assert_stories_example_pair("right-size-story-nodes")

    with context("verb-noun-format"):
        with it("should flag CartStuff"):
            assert_stories_example_pair("verb-noun-format")

    with context("gwt-steps-trace-to-domain-operations"):
        with it("should require domain vocabulary in given steps"):
            assert_stories_example_pair("gwt-steps-trace-to-domain-operations")

    with context("example-role-names"):
        with it("should require entered/stored/expected exports"):
            assert_stories_example_pair("example-role-names")

    with context("kebab-case-paths"):
        with it("should flag camelCase story test file names"):
            assert_stories_example_pair("kebab-case-paths")

    with context("vocabulary-traces-to-domain-source"):
        # The executable name check was retired in 49bec82f; the rule is a prompt the agent judges.
        with it("should apply to stories as a prompt rule with no executable check"):
            from cdd_guidance.practices.stories.rules import BY_SLUG
            from harness.graph.schema_rules import PracticeSchema
            from harness.guidance.practice_catalogue import PracticeCatalogue

            expect("vocabulary-traces-to-domain-source" in BY_SLUG).to(equal(False))
            expect(PracticeSchema(PracticeCatalogue.create("stories")).slugs_for("Story")).to(contain("vocabulary-traces-to-domain-source"))
