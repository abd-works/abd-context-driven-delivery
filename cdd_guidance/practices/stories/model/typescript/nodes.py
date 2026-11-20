"""TypeScript nodes: TypeScript, then code, then the story model."""
from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.stories.model.brace_story import BraceScenario, BraceStory
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic
from cdd_guidance.practices.stories.model.typescript.screen_spec_file import ScreenSpecFile, is_screen_spec


class TypeScriptScenario(BraceScenario):
    """A scenario read from a TypeScript story file."""


class TypeScriptStory(BraceStory):
    scenario_type = TypeScriptScenario

    @classmethod
    def load_all(cls, content: str) -> list:
        """Every story in one story file: a screen spec's, one for each `test.describe`; any other's, from its `story`
        blocks."""
        if is_screen_spec(content):
            return ScreenSpecFile(content).stories(cls)
        return super().load_all(content)


class TypeScriptEpic(CodeEpic):
    """An epic or sub-epic whose stories a TypeScript story file holds."""


def _story_test_text(tests_root: str) -> str:
    seed = Path(__file__).resolve().parent / "seeds" / "story-test.ts"
    if seed.exists():
        return seed.read_text(encoding="utf-8")
    return (
        "export function story(name: string, build: () => void): void {\n"
        "  describe(name, build);\n"
        "}\n"
    )
