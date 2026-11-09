"""TypeScript nodes: TypeScript, then code, then the story model."""
from __future__ import annotations

from pathlib import Path

from harness.annotations.name import Name

from cdd_guidance.practices.stories.model.brace_story import BraceScenario, BraceStory
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic


class TypeScriptScenario(BraceScenario):
    """A scenario read from a TypeScript story file."""


class TypeScriptStory(BraceStory):
    scenario_type = TypeScriptScenario


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
        return (
            f"/**\n"
            f" * Example domain aggregates for {self.name}.\n"
            f" */\n"
            f"\n"
            f"export interface {noun} {{\n"
            f"  id: string;\n"
            f"  status: 'active' | 'pending' | 'suspended';\n"
            f"  email: string;\n"
            f"  planName?: string;\n"
            f"}}\n"
            f"\n"
            f"export const active{noun}Example: {noun} = {{\n"
            f"  id: 'agg-123',\n"
            f"  status: 'active',\n"
            f"  email: 'active-user@example.com',\n"
            f"  planName: 'Premium Plan',\n"
            f"}};\n"
            f"\n"
            f"export const pending{noun}Example: {noun} = {{\n"
            f"  id: 'agg-456',\n"
            f"  status: 'pending',\n"
            f"  email: 'pending-user@example.com',\n"
            f"}};\n"
            f"\n"
            f"export const suspended{noun}Example: {noun} = {{\n"
            f"  id: 'agg-789',\n"
            f"  status: 'suspended',\n"
            f"  email: 'suspended-user@example.com',\n"
            f"}};\n"
        )


def _story_test_text(tests_root: str) -> str:
    seed = Path(__file__).resolve().parent / "seeds" / "story-test.ts"
    if seed.exists():
        return seed.read_text(encoding="utf-8")
    return (
        "export function story(name: string, build: () => void): void {\n"
        "  describe(name, build);\n"
        "}\n"
    )
