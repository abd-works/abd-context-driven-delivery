"""JavaScriptStoryModel - a story map stored as `*_story.js` files.

Each story file is `story` / `background` / `scenario` / `given` / `when` / `then`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from cdd_guidance.practices.clean_engineering.model.code_body import JAVASCRIPT
from cdd_guidance.practices.stories.model.brace_story import BraceStoryModel
from cdd_guidance.practices.stories.model.javascript.nodes import JavaScriptEpic, JavaScriptStory
from cdd_guidance.practices.stories.model.story_model import Epic


class JavaScriptStoryModel(BraceStoryModel):
    LEAF_EXTENSION = "_story.test.js"
    story_file_suffixes = (LEAF_EXTENSION,)
    epic_type = JavaScriptEpic
    story_type = JavaScriptStory
    language = JAVASCRIPT

    def save(self) -> Dict[str, str]:
        # WHY: a tree read from JavaScript already brings its own story-test helper; only a new tree needs the seed.
        seed = {} if self.read_from_code() else {f"{self.tests_root}/story-test.js": _story_test_js()}
        return self.write_epics(seed)

    def file_name(self, epic: Epic) -> str:
        return f"{epic.snake()}_story.test.js"

    def story_test_import(self, parent: str) -> str:
        relative = "../" * parent.count("/") + "story-test.js"
        return f'import {{ background, scenario, story }} from "{relative}";'


def _story_test_js() -> str:
    seed = Path(__file__).resolve().parent / "seeds" / "story-test.js"
    if seed.exists():
        return seed.read_text(encoding="utf-8")
    return (
        'import { before, describe, it } from "node:test";\n\n'
        "export function story(name, build) {\n  describe(name, build);\n}\n"
    )
