"""TypeScript nodes: TypeScript, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from pathlib import Path

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, StepType, Story


class TypeScriptScenario(CodeScenario):
    _CALL = re.compile(
        r"(?P<kw>\.(?:and|but)|(?<![.\w])(?:given|when|then))\(\s*(?P<q>['\"])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)",
        re.IGNORECASE,
    )
    _SCENARIO = re.compile(r"scenario\(\s*(?P<q>['\"])(?P<name>(?:\\.|(?!(?P=q)).)*)(?P=q)")
    _BACKGROUND = re.compile(r"background\(\s*(?:(?P<q>['\"])(?P<scope>\w+)(?P=q)\s*,\s*)?")
    _IMPORT = re.compile(
        r"import\s*\{(?P<names>[^}]+)\}\s*from\s*['\"][^'\"]*examples[^'\"]*['\"]"
    )

    def calls_in(self, body: str) -> List[tuple]:
        return [(match.group("kw").lstrip("."), match.group("text")) for match in self._CALL.finditer(body)]

    @classmethod
    def scenario_blocks(cls, content: str) -> List[tuple]:
        blocks = []
        for match in cls._SCENARIO.finditer(content):
            arrow = content.find("=>", match.end())
            brace = content.find("{", arrow if arrow >= 0 else match.end())
            body = cls.balanced(content, brace) if brace >= 0 else ""
            blocks.append((match.group("name"), body))
        return blocks

    @classmethod
    def backgrounds_in(cls, content: str) -> List[Background]:
        found: List[Background] = []
        for match in cls._BACKGROUND.finditer(content):
            arrow = content.find("=>", match.end())
            brace = content.find("{", arrow if arrow >= 0 else match.end())
            if brace < 0:
                continue
            body = cls.outside_scenarios(cls.balanced(content, brace))
            steps = cls.steps_from(cls(name="").calls_in(body))
            if not steps and not match.group("scope"):
                continue
            background = Background(match.group("scope") or "background", len(found) + 1)
            background.steps = [step for step in steps if step.keyword == "Given"]
            found.append(background)
        return found

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        names: List[str] = []
        for match in cls._IMPORT.finditer(content):
            for part in match.group("names").split(","):
                name = part.strip().split(" as ")[-1].strip()
                if name:
                    names.append(name)
        return names

    @classmethod
    def create(cls, scenario) -> List[str]:
        lines = [f"  scenario({_ts_string(scenario.name)}, ({{ given, when, then }}) => {{"]
        for step in scenario.steps_in(StepType.GIVEN):
            lines.extend(_ts_call("    ", "given", step))
        for when_steps, then_steps in scenario.when_then_runs():
            if when_steps:
                lines.extend(_ts_call("    ", "when", when_steps[0]))
                for step in when_steps[1:]:
                    lines.extend(_ts_call("      ", ".and", step))
            if then_steps:
                lines.extend(_ts_call("    ", "then", then_steps[0]))
                for step in then_steps[1:]:
                    lines.extend(_ts_call("      ", ".and", step))
        lines.append("  });")
        lines.append("")
        return lines


def _ts_call(indent: str, verb: str, step) -> List[str]:
    lines = [
        f"{indent}{verb}({_ts_string(step.text)}, () => {{",
        f"{indent}  // TODO: implement step",
        f"{indent}}})",
    ]
    for extra in step.ands:
        join = ".but" if extra.keyword == "But" else ".and"
        lines.extend([
            f"{indent}  {join}({_ts_string(extra.text)}, () => {{",
            f"{indent}    // TODO: implement step",
            f"{indent}  }})",
        ])
    lines[-1] += ";"
    return lines


def _ts_string(value: str) -> str:
    cleaned = re.sub(r"`([^`]+)`", r"\1", value)
    cleaned = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


class TypeScriptStory(CodeStory):
    scenario_type = TypeScriptScenario

    @classmethod
    def load_all(cls, content: str) -> List["TypeScriptStory"]:
        chunks = re.split(r"(?=/\*\*\s*\n \* Story:)", content)
        stories = [cls.load(chunk, "") for chunk in chunks if "Story:" in chunk or "story(" in chunk]
        return stories or [cls.load(content, "")]

    @classmethod
    def load(cls, content: str, story_slug: str) -> "TypeScriptStory":
        name_match = re.search(r"\*\s*Story:\s*(.+)", content)
        story_name = name_match.group(1).strip() if name_match else story_slug.replace("-", " ").title()
        if name_match is None:
            call = re.search(r"story\(\s*(['\"])((?:\\.|(?!\1).)*)\1", content)
            if call:
                story_name = call.group(2)
        story_name = re.sub(r"\s*\([^)]*\)\.?\s*$", "", story_name).strip()
        story = cls(story_name, 1)
        actor_match = re.search(r"\*\s*Actor:\s*(.+)", content)
        if actor_match:
            story.actors = [actor_match.group(1).strip()]
        story.fill(content)
        return story

    @classmethod
    def story_text(cls, story: Story) -> str:
        actor = (story.actors[0] if story.actors else "").strip()
        lines: List[str] = ["/**", f" * Story: {story.name}"]
        if actor:
            lines.append(f" * Actor: {actor}")
        lines.extend([" */", "", f"story({_ts_string(story.name)}, () => {{"])
        if not story.scenarios:
            lines.append("  // TODO: add main-flow scenario")
        for scenario in story.scenarios:
            lines.extend(TypeScriptScenario.create(scenario))
        lines.append("});")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def create(cls, story: Story, story_test_import_path: str = "tests/story-test", **kwargs) -> str:
        return "\n".join([
            f'import {{ scenario, story }} from "{story_test_import_path}";',
            "",
            cls.story_text(story),
        ])


_GIVENS = (
    "/**\n"
    " * Reusable Given steps for this folder.\n"
    " * Labels match the prose used in story files; bodies live here once.\n"
    " */\n"
    "\n"
    "/** Given: a prospect with a created account */\n"
    "export async function aProspectWithACreatedAccount(): Promise<void> {\n"
    "  // TODO: implement reusable given seed\n"
    "}\n"
)


class TypeScriptEpic(CodeEpic):
    def _write_stories(self, parent: str, files: dict, tests_root: str) -> None:
        from practices.stories.model.typescript.story_file import story_test_import_path

        stories = self._file_stories()
        if not stories:
            return
        import_path = story_test_import_path(tests_root)
        blocks = "\n".join(TypeScriptStory.story_text(story) for story in stories)
        files[f"{parent}/{self.snake()}_story.test.ts"] = "\n".join([
            "/**",
            f" * Epic: {self.name}",
            " */",
            "",
            f'import {{ scenario, story }} from "{import_path}";',
            "",
            blocks,
        ])

    def _write_folder(self, folder: str, files: dict, tests_root: str) -> None:
        files.setdefault(f"{folder}/givens.ts", _GIVENS)
        noun = self._aggregate_noun()
        kebab = CodeEpic(noun).slug()
        files.setdefault(f"{folder}/examples/{kebab}.examples.ts", self._examples_file(noun))

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
