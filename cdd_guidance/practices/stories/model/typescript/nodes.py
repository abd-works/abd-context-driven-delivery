"""TypeScript nodes: TypeScript, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from pathlib import Path

from cdd_guidance.practices.stories.model.brace_story import BraceScenario
from cdd_guidance.practices.stories.model.code_story_model import CodeEpic, CodeStory
from cdd_guidance.practices.stories.model.story_model import Story
from cdd_guidance.practices.stories.model.typescript.story_file import DEFAULT_STORY_TEST_IMPORT


class TypeScriptScenario(BraceScenario):
    """A scenario read from a TypeScript story file."""


class TypeScriptStory(CodeStory):
    scenario_type = TypeScriptScenario

    @classmethod
    def load_all(cls, content: str) -> List["TypeScriptStory"]:
        comment_chunks = re.split(r"(?=/\*\*\s*\n \* Story:)", content)
        named = [chunk for chunk in comment_chunks if re.search(r"\*\s*Story:", chunk)]
        if named and len(re.findall(r"(?i)story\(", content)) <= len(named):
            imports = "\n".join(match.group(0) for match in cls.scenario_type._IMPORT.finditer(content))
            stories = [
                cls.load(f"{imports}\n{chunk}", "")
                for chunk in comment_chunks
                if "Story:" in chunk or re.search(r"(?i)story\(", chunk)
            ]
            return stories or [cls.load(content, "")]
        calls = list(re.finditer(r"(?im)^[ \t]*(?:shareStory|story)\(", content))
        if len(calls) <= 1:
            return [cls.load(content, "")]
        stories = []
        preamble = content[: calls[0].start()]
        for index, match in enumerate(calls):
            end = calls[index + 1].start() if index + 1 < len(calls) else len(content)
            stories.append(cls.load(preamble + content[match.start() : end], ""))
        return stories

    @classmethod
    def load(cls, content: str, story_slug: str) -> "TypeScriptStory":
        name_match = re.search(r"\*\s*Story:\s*(.+)", content)
        story_name = name_match.group(1).strip() if name_match else story_slug.replace("-", " ").title()
        if name_match is None:
            call = re.search(
                r"(?i)(?:shareStory|story)\(\s*(['\"])((?:\\.|(?!\1).)*)\1",
                content,
            )
            if call:
                story_name = call.group(2)
        story_name = re.sub(r"\s*\([^)]*\)\.?\s*$", "", story_name).strip()
        story = cls(story_name, 1)
        actor_match = re.search(r"\*\s*Actor:\s*(.+)", content)
        if actor_match:
            story.actors = [actor_match.group(1).strip()]
        evidence_match = re.search(r"\*\s*Evidence:\s*([A-Za-z][A-Za-z ,-]*)", content)
        if evidence_match:
            story.evidence = [part.strip() for part in evidence_match.group(1).split(",") if part.strip()]
        story.fill(content)
        return story

    @classmethod
    def create(cls, story: Story, story_test_import_path: str = DEFAULT_STORY_TEST_IMPORT, **kwargs) -> str:
        from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

        return "\n".join([
            f'import {{ scenario, story }} from "{story_test_import_path}";',
            "",
            TypeScriptStoryModel().story_text(cls(story)),
        ])


class TypeScriptEpic(CodeEpic):
    def examples_file(self) -> tuple:
        """(file name, text) of the example aggregates a new epic folder starts with."""
        noun = self._aggregate_noun()
        return f"{CodeEpic(noun).slug()}.examples.ts", self._examples_file(noun)

    def _aggregate_noun(self) -> str:
        pascal = self.pascal()
        for verb in (
            "Create", "Get", "Manage", "Settle", "Enter", "Know", "Complete",
            "Query", "Submit", "View", "Store", "Update", "Delete", "Place",
        ):
            if pascal.startswith(verb) and len(pascal) > len(verb):
                return pascal[len(verb):]
        return pascal

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
