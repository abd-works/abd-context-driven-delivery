"""Mamba spec: a story test in any language reads back the story's own name."""

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.stories.model.java.nodes import JavaStory
from cdd_guidance.practices.stories.model.javascript.nodes import JavaScriptStory
from cdd_guidance.practices.stories.model.python.nodes import PythonStory
from cdd_guidance.practices.stories.model.story_model import Story
from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptStory

_LANGUAGES = (TypeScriptStory, JavaScriptStory, PythonStory, JavaStory)


def _read_back(story_type, name: str) -> str:
    story = Story(name, 1)
    story.actors = ["Customer"]
    return story_type.load_all(story_type.create(story))[0].name


with description("a story test written in each language") as self:
    with it("should read back a story name that ends in a parenthetical"):
        names = [_read_back(story_type, "Pay Bill (By Card)") for story_type in _LANGUAGES]
        expect(names).to(equal(["Pay Bill (By Card)"] * len(_LANGUAGES)))

    with it("should read back a story name without the tier-neutral marker"):
        names = [_read_back(story_type, "Pay Bill (tier-neutral)") for story_type in _LANGUAGES]
        expect(names).to(equal(["Pay Bill"] * len(_LANGUAGES)))
