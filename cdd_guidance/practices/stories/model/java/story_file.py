"""Java story file. create and load live on JavaStory."""

from practices.stories.model.java.nodes import JavaStory


def render_story_file(story) -> str:
    return JavaStory.create(story)
