"""JavaScript story file. create and load live on JavaScriptStory."""

from practices.stories.model.javascript.nodes import JavaScriptStory


def render_story_file(story, **kwargs) -> str:
    return JavaScriptStory.create(story, **kwargs)
