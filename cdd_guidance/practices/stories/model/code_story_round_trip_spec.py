"""Mamba spec: a story map written as story tests in each language reads back as the same map.

Every code adapter carries epics, stories held by any epic, each story's kind and actor, its background, and its
scenarios with their steps."""

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.java.java_story_model import JavaStoryModel
from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel


def _read_back(adapter_type) -> list:
    files = adapter_type().render(round_trip_story_map())
    return outline(adapter_type().load(files), with_scenarios=True)


with description("a story map written as story tests") as self:
    with before.each:
        self.expected = outline(round_trip_story_map(), with_scenarios=True)

    with context("in Python"):
        with it("should read back every epic, story, kind, actor, background, and scenario"):
            expect(_read_back(PythonStoryModel)).to(equal(self.expected))

    with context("in TypeScript"):
        with it("should read back every epic, story, kind, actor, background, and scenario"):
            expect(_read_back(TypeScriptStoryModel)).to(equal(self.expected))

    with context("in JavaScript"):
        with it("should read back every epic, story, kind, actor, background, and scenario"):
            expect(_read_back(JavaScriptStoryModel)).to(equal(self.expected))

    with context("in Java"):
        with it("should read back every epic, story, kind, actor, background, and scenario"):
            expect(_read_back(JavaStoryModel)).to(equal(self.expected))
