"""Python story file. create and load live on PythonStory."""

from practices.stories.model.python.nodes import PythonStory


def render_story_file(story) -> str:
    return PythonStory.create(story)
