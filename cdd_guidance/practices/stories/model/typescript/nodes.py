"""TypeScript nodes: TypeScript, then code, then the story model."""
from __future__ import annotations

from pathlib import Path

from harness.annotations.name import Name

from cdd_guidance.practices.stories.model.brace_story import BraceScenario, BraceStory
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic
from cdd_guidance.practices.stories.model.typescript.screen_spec_file import ScreenSpecFile, is_screen_spec


# The example aggregates a new TypeScript epic folder starts with, for the aggregate its name names.
_EXAMPLES_TEMPLATE = """\
/**
 * Example domain aggregates for {name}.
 */

export interface {noun} {{
  id: string;
  status: 'active' | 'pending' | 'suspended';
  email: string;
  planName?: string;
}}

export const active{noun}Example: {noun} = {{
  id: 'agg-123',
  status: 'active',
  email: 'active-user@example.com',
  planName: 'Premium Plan',
}};

export const pending{noun}Example: {noun} = {{
  id: 'agg-456',
  status: 'pending',
  email: 'pending-user@example.com',
}};

export const suspended{noun}Example: {noun} = {{
  id: 'agg-789',
  status: 'suspended',
  email: 'suspended-user@example.com',
}};
"""


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
    def examples_file(self) -> tuple:
        """(file name, text) of the example aggregates a new epic folder starts with."""
        noun = self._aggregate_noun()
        return f"{Name(noun).title_slug or 'unnamed'}.examples.ts", self._examples_file(noun)

    def _aggregate_noun(self) -> str:
        """The epic's name without its opening verb: Create Customer names a Customer."""
        words = self.name.split()
        if len(words) > 1 and self.opens_with_verb():
            return Name(" ".join(words[1:])).title_pascal or "Unnamed"
        return self.pascal()

    def _examples_file(self, noun: str) -> str:
        return _EXAMPLES_TEMPLATE.format(noun=noun, name=self.name)


def _story_test_text(tests_root: str) -> str:
    seed = Path(__file__).resolve().parent / "seeds" / "story-test.ts"
    if seed.exists():
        return seed.read_text(encoding="utf-8")
    return (
        "export function story(name: string, build: () => void): void {\n"
        "  describe(name, build);\n"
        "}\n"
    )
