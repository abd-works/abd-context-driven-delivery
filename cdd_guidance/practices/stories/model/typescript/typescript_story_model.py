"""TypeScriptStoryModel - runnable `{story_snake}_story.test.ts` under epic / sub-epic / story."""

from __future__ import annotations

from typing import Dict, List, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage
from cdd_guidance.practices.stories.model.brace_story import BraceStoryModel
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModelError, example_names_of
from cdd_guidance.practices.stories.model.story_model import Epic, StoryModel
from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptEpic, TypeScriptStory, _story_test_text
from cdd_guidance.practices.stories.model.typescript.story_file import (
    default_story_test_folder,
    story_test_file_path,
    story_test_import_path,
)

_SKIP_NAMES = frozenset({"story-test.ts", "givens.ts"})


_STORY_TEST_SUFFIX = "_story.test.ts"


class TypeScriptStoryModel(BraceStoryModel):
    LEAF_EXTENSION = ".ts"
    LANGUAGE_LINE_COMMENT = "//"
    epic_type = TypeScriptEpic
    story_type = TypeScriptStory
    language = CodeLanguage.named("typescript")

    def __init__(
        self,
        source: "StoryModel | str | None" = None,
        tests_root: str | None = None,
        story_test_folder: str | None = None,
    ):
        super().__init__(source, tests_root)
        folder = default_story_test_folder(self.tests_root) if story_test_folder is None else story_test_folder
        self._story_test_folder = folder.strip("/")

    @property
    def story_test_folder(self) -> str:
        """Step library folder: where story-test.ts sits and where story files import it from."""
        return self._story_test_folder

    def save(self) -> Dict[str, str]:
        # WHY: a tree read from TypeScript already brings its own story-test helper; only a new tree needs the seed.
        seed_path = story_test_file_path(self._story_test_folder)
        seed = {} if self.read_from_code() else {seed_path: _story_test_text(self.tests_root)}
        return self.write_epics(seed)

    def _copy_of(self, canonical: StoryModel) -> "TypeScriptStoryModel":
        return type(self)(canonical, tests_root=self.tests_root, story_test_folder=self._story_test_folder)

    def file_name(self, epic: Epic) -> str:
        return f"{epic.snake()}_story.test.ts"

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        names = example_names_of(list(epic.stories))
        example_import = [f"import {{ {', '.join(names)} }} from \"./examples\";"] if names else []
        return [
            "/**",
            f" * Epic: {epic.name}",
            f" * Orders: {epic.order_path()}",
            " */",
            "",
            f'import {{ scenario, story }} from "{story_test_import_path(self._story_test_folder)}";',
            *example_import,
            "",
        ]

    def folder_files(self, epic: Epic, folder: str, files: Dict[str, str]) -> None:
        """A new epic folder starts with example aggregates; a folder read from code already has its own."""
        if self.read_from_code():
            return
        name, text = epic.examples_file()
        files.setdefault(f"{folder}/examples/{name}", text)

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(p for p in tree if self.is_story_file(p))

    def is_story_file(self, path: str) -> bool:
        """A story test file (not an examples file) that this model reads a story from."""
        name = path.replace("\\", "/").rsplit("/", 1)[-1]
        if name in _SKIP_NAMES or name.endswith("-helper.ts"):
            return False
        if "/examples/" in path.replace("\\", "/"):
            return False
        return (
            name.endswith(_STORY_TEST_SUFFIX)
            or name.endswith("_story.spec.ts")
            or name.endswith(".story.shared.ts")
        )

    def _story_slug_from_filename(self, name: str) -> str | None:
        suffix = _STORY_TEST_SUFFIX if name.endswith(_STORY_TEST_SUFFIX) else "_story.spec.ts"
        if not name.endswith(suffix):
            return None
        stem = name[: -len(suffix)]
        return stem.replace("_", "-")

    def load(self, external: Dict[str, str], *, on_file=None) -> "TypeScriptStoryModel":
        if not isinstance(external, dict):
            raise CodeStoryModelError("TypeScript story map parse expects a path->content dict")
        self.epics.clear()
        seen: set[tuple[str, ...]] = set()
        ordered = self._ordered_paths(external)
        leaves = [path for path in ordered if self.is_story_file(path)]
        total = len(leaves)
        with self.batch_schema_sync():
            self._read_leaves(external, leaves, seen, on_file, total)
        return self

    def _read_leaves(self, external, leaves, seen, on_file, total: int) -> None:
        for index, path in enumerate(leaves, start=1):
            if on_file is not None:
                on_file(f"{index}/{total} · {path}")
            content = external[path]
            parts = path.strip("/").replace("\\", "/").split("/")
            stripped = self.strip_tests_root_prefix(parts)
            if stripped is None:
                continue
            parts = stripped
            if self.take_sub_epic_file(parts, content, path):
                continue
            if len(parts) < 3:
                continue
            filename = parts[-1]
            story_slug = self._story_slug_from_filename(filename)
            if not story_slug:
                continue
            epic_slug, sub_slugs = parts[0], parts[1:-1]
            if sub_slugs and sub_slugs[-1] == story_slug:
                sub_slugs = sub_slugs[:-1]
            if not sub_slugs:
                continue
            key = (epic_slug, *sub_slugs, story_slug)
            if key in seen:
                continue
            seen.add(key)
            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
