"""Mamba spec: a story test in any language reads back the story's own name."""

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.stories.model.java.java_story_model import JavaStoryModel
from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.story_model import Story
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

_LANGUAGES = (TypeScriptStoryModel, JavaScriptStoryModel, PythonStoryModel, JavaStoryModel)


def _read_back(model_type, name: str) -> str:
    story = Story(name, 1)
    story.actors = ["Customer"]
    model = model_type()
    return model.story_type.load_all(model.writing.story_text(model.story_type(story)))[0].name


with description("a story test written in each language") as self:
    with it("should read back a story name that ends in a parenthetical"):
        names = [_read_back(model_type, "Pay Bill (By Card)") for model_type in _LANGUAGES]
        expect(names).to(equal(["Pay Bill (By Card)"] * len(_LANGUAGES)))

    with it("should read back a story name without the tier-neutral marker"):
        names = [_read_back(model_type, "Pay Bill (tier-neutral)") for model_type in _LANGUAGES]
        expect(names).to(equal(["Pay Bill"] * len(_LANGUAGES)))
