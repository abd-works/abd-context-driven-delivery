"""TypeScript story file paths. create and load live on TypeScriptStory."""

from practices.stories.model.typescript.nodes import TypeScriptStory


def story_test_import_path(deploy_root: str) -> str:
    """Stable workspace-root import for story-test."""
    root = deploy_root.strip("/")
    if root == "stories" or root.startswith("stories/"):
        return "stories/story-test"
    return f"{root}/story-test" if root else "story-test"


def story_test_file_path(deploy_root: str) -> str:
    """Filesystem path for the shared story-test.ts seed."""
    return f"{story_test_import_path(deploy_root)}.ts"


def render_story_file(story, *, story_test_import_path: str = "tests/story-test") -> str:
    return TypeScriptStory.create(story, story_test_import_path=story_test_import_path)
