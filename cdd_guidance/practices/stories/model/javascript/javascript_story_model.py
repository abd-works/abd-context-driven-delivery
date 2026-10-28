"""JavaScriptStoryModel - a story map stored as `*_story.js` files.

Each story file is `story` / `background` / `scenario` / `given` / `when` / `then`.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage
from cdd_guidance.practices.stories.model.brace_story import BraceStoryModel
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel, CodeStoryModelError, example_names_of
from cdd_guidance.practices.stories.model.javascript.nodes import JavaScriptEpic, JavaScriptStory
from cdd_guidance.practices.stories.model.story_model import Epic


class JavaScriptStoryModel(BraceStoryModel):
    LEAF_EXTENSION = "_story.test.js"
    LANGUAGE_LINE_COMMENT = "//"
    epic_type = JavaScriptEpic
    story_type = JavaScriptStory
    language = CodeLanguage.named("javascript")

    def save(self) -> Dict[str, str]:
        # WHY: a tree read from JavaScript already brings its own story-test helper; only a new tree needs the seed.
        seed = {} if self.read_from_code() else {f"{self.tests_root}/story-test.js": _story_test_js()}
        return self.write_epics(seed)

    def file_name(self, epic: Epic) -> str:
        return f"{epic.snake()}_story.test.js"

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        relative = "../" * parent.count("/") + "story-test.js"
        names = example_names_of(list(epic.stories))
        example_import = [f"import {{ {', '.join(names)} }} from \"./examples\";"] if names else []
        return [
            "/**",
            f" * Epic: {epic.name}",
            f" * Orders: {epic.order_path()}",
            " */",
            "",
            f'import {{ background, scenario, story }} from "{relative}";',
            *example_import,
            "",
        ]

    def leaf_files_of(self, tree: Dict[str, str]) -> List[str]:
        return sorted(
            p for p in tree if p.endswith(self.LEAF_EXTENSION) and "/story-test.js" not in p
        )

    def _epic_helper_path(self, epic_root: str, epic: Epic) -> str:
        return f"{epic_root}/{epic.slug()}-helper.js"

    def load(self, external: Dict[str, str]) -> "JavaScriptStoryModel":
        if not isinstance(external, dict):
            raise CodeStoryModelError("JavaScript story map parse expects a path->content dict")
        self.epics.clear()
        # Group *_story.js by epic / sub-epic / story folder
        for path in self._ordered_paths(external):
            content = external[path]
            if not path.endswith(self.LEAF_EXTENSION):
                continue
            parts = path.strip("/").split("/")
            if parts and parts[0] == self.tests_root:
                parts = parts[1:]
            if self.take_sub_epic_file(parts, content, path):
                continue
            # epic / ...subs... / story-folder / file
            if len(parts) < 4:
                continue
            epic_slug = parts[0]
            story_slug = parts[-2]
            sub_slugs = parts[1:-2]
            if not sub_slugs:
                continue

            epic = self.epic_for(epic_slug)
            sub = self.sub_epic_for(epic, sub_slugs)
            sub.append_story(self.story_type.load(content, story_slug))
        return self


def _story_test_js() -> str:
    seed = Path(__file__).resolve().parent / "seeds" / "story-test.js"
    if seed.exists():
        return seed.read_text(encoding="utf-8")
    return (
        'import { before, describe, it } from "node:test";\n\n'
        "export function story(name, build) {\n  describe(name, build);\n}\n"
    )
