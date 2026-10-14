"""Story rules backed by TypeScript .examples stubs."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mamba import context, description, it

from harness.graph.stories_example_harness import assert_stories_example_pair, assert_stories_ts_pair
from harness.graph.stories_ts_folder_harness import assert_stories_folder_pair


with description("stories TypeScript .examples (faultyAsset.ts)"):
    with context("story-name-captures-system-mechanic"):
        with it("should flag Handle Request and accept Submit Order"):
            assert_stories_example_pair("story-name-captures-system-mechanic")

    with context("plain-english-gwt-steps"):
        with it("should flag camelCase given steps"):
            assert_stories_example_pair("plain-english-gwt-steps")

    with context("right-size-story-nodes"):
        with it("should flag near-duplicate story names"):
            assert_stories_example_pair("right-size-story-nodes")

    with context("four-to-nine-children"):
        with it("should flag too few scenario() calls"):
            assert_stories_example_pair("four-to-nine-children")

    with context("verb-noun-format"):
        with it("should flag CartStuff"):
            assert_stories_example_pair("verb-noun-format")

    with context("gwt-steps-trace-to-domain-operations"):
        with it("should require domain vocabulary in given steps"):
            assert_stories_example_pair("gwt-steps-trace-to-domain-operations")

    with context("vocabulary-traces-to-domain-source"):
        with it("should flag technical story names"):
            assert_stories_ts_pair(
                "vocabulary-traces-to-domain-source",
                'function story(n,f){f()}\nstory("Update DTO", () => {})\n',
                'function story(n,f){f()}\nstory("Submit Order", () => {})\n',
            )


with description("stories TypeScript .examples (folders)"):
    with context("domain-operation-in-the-step"):
        with it("should flag orchestration exports"):
            assert_stories_folder_pair(
                "domain-operation-in-the-step",
                "domain-operation-in-the-step",
                "create-customer.story.shared.ts",
                node_type="Story",
            )

    with context("example-role-names"):
        with it("should require entered/stored/expected exports"):
            assert_stories_folder_pair(
                "example-role-names",
                "example-role-names",
                "tests/onboard/examples/customers.examples.ts",
            )

    with context("kebab-case-paths"):
        with it("should flag camelCase story test file names"):
            folder = _REPO / "practices/stories/model/typescript/.examples/kebab-case-paths"
            fault = (folder / "faulty" / "HandleRequest_story.test.ts").read_text(encoding="utf-8")
            clean = (folder / "repaired" / "submit-order.story.test.js").read_text(encoding="utf-8")
            assert_stories_ts_pair(
                "kebab-case-paths",
                fault,
                clean,
                relative="HandleRequest_story.test.ts",
                clean_relative="submit-order.story.test.js",
            )
