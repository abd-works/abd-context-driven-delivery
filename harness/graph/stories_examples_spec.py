"""Story rules backed by TypeScript .examples stubs."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mamba import context, description, it

from harness.graph.stories_example_harness import assert_stories_example_pair


with description("stories TypeScript .examples"):
    with context("story-name-captures-system-mechanic"):
        with it("should flag Handle Request and accept Submit Order"):
            assert_stories_example_pair("story-name-captures-system-mechanic")

    with context("plain-english-gwt-steps"):
        with it("should flag camelCase given steps"):
            assert_stories_example_pair("plain-english-gwt-steps")

    with context("right-size-story-nodes"):
        with it("should flag near-duplicate story names"):
            assert_stories_example_pair("right-size-story-nodes")
