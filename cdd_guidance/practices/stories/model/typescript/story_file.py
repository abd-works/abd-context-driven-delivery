"""TypeScript story file paths. create and load live on TypeScriptStory.

The step library folder is the one setting for where the shared story-test.ts sits:
the file the render writes and the import every story file uses both come from it.
"""


def default_story_test_folder(deploy_root: str) -> str:
    """Step library folder when none is named: the stories workspace root, else the deploy root."""
    root = deploy_root.strip("/")
    if root == "stories" or root.startswith("stories/"):
        return "stories"
    return root


def story_test_import_path(story_test_folder: str) -> str:
    """Stable workspace-root import for story-test."""
    folder = story_test_folder.strip("/")
    return f"{folder}/story-test" if folder else "story-test"


def story_test_file_path(story_test_folder: str) -> str:
    """Filesystem path for the shared story-test.ts seed."""
    return f"{story_test_import_path(story_test_folder)}.ts"


DEFAULT_STORY_TEST_IMPORT = story_test_import_path(default_story_test_folder("tests"))


def render_story_file(story, *, story_test_import_path: str = DEFAULT_STORY_TEST_IMPORT) -> str:
    from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptStory

    return TypeScriptStory.create(story, story_test_import_path=story_test_import_path)
