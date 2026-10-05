"""TypeScript nodes: TypeScript, then code, then the story model."""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from pathlib import Path

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, StepType, Story


class TypeScriptScenario(CodeScenario):
    _CALL = re.compile(
        r"(?P<kw>\.(?:and|but)|(?<![.\w])(?:given|when|then|but))\(\s*(?P<q>['\"])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)",
        re.IGNORECASE,
    )
    _SCENARIO = re.compile(r"scenario\(\s*(?P<q>['\"])(?P<name>(?:\\.|(?!(?P=q)).)*)(?P=q)")
    _BACKGROUND = re.compile(r"background\(\s*(?:(?P<q>['\"])(?P<scope>\w+)(?P=q)\s*,\s*)?")
    _IMPORT = re.compile(
        r"import\s*\{(?P<names>[^}]+)\}\s*from\s*['\"][^'\"]*examples[^'\"]*['\"]"
    )

    def read(self, body: str, example_names: List[str] | None = None) -> None:
        self.backgrounds = self.backgrounds_in(body)
        super().read(self.without_background(body), example_names)

    @classmethod
    def without_background(cls, body: str) -> str:
        while True:
            match = cls._BACKGROUND.search(body)
            if match is None:
                return body
            arrow = body.find("=>", match.end())
            brace = body.find("{", arrow if arrow >= 0 else match.end())
            if brace < 0:
                return body[:match.start()] + body[match.end():]
            inner = cls.balanced(body, brace)
            body = body[:match.start()] + body[brace + len(inner) + 2:]

    def calls_in(self, body: str) -> List[tuple]:
        return [(match.group("kw").lstrip("."), _unescape(match.group("text"))) for match in self._CALL.finditer(body)]

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
            if cls._inside_scenario(content, match.start()):
                continue
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
    def _inside_scenario(cls, content: str, pos: int) -> bool:
        for match in cls._SCENARIO.finditer(content):
            if match.start() >= pos:
                break
            brace = content.find("{", content.find("=>", match.end()))
            if brace < 0:
                continue
            inner = cls.balanced(content, brace)
            if brace <= pos <= brace + len(inner):
                return True
        return False

    @classmethod
    def example_names(cls, content: str) -> List[str]:
        names: List[str] = []
        for match in cls._IMPORT.finditer(content):
            for part in match.group("names").split(","):
                name = part.strip().split(" as ")[-1].strip()
                if name and name not in names:
                    names.append(name)
        for match in re.finditer(r"examples:\s*(.+)", content):
            for part in match.group(1).split(","):
                name = part.strip()
                if name and name not in names:
                    names.append(name)
        return names

    @classmethod
    def create(cls, scenario) -> List[str]:
        lines = [f"  scenario({_ts_string(scenario.name)}, ({{ given, when, then }}) => {{"]
        for background in scenario.backgrounds:
            scope = background.name if re.fullmatch(r"\w+", background.name or "") else "background"
            lines.append(f"    background('{scope}', ({{ given }}) => {{")
            for lead, continuations in cls._clauses(background.steps):
                lines.extend(_ts_call("      ", _lead_verb(lead, "given"), lead, continuations))
            lines.append("    });")
        if scenario.examples:
            lines.append("    // examples: " + ", ".join(scenario.examples))
        for lead, continuations in cls._clauses(scenario.steps):
            lines.extend(_ts_call("    ", _lead_verb(lead, lead.keyword.lower()), lead, continuations))
        lines.append("  });")
        lines.append("")
        return lines

    @classmethod
    def _clauses(cls, steps) -> List[Tuple[object, List[object]]]:
        """A step repeating the previous step's phase continues that clause, so the
        fluent surface chains it rather than opening a second given/when/then."""
        clauses: List[Tuple[object, List[object]]] = []
        for step in steps:
            if clauses and step.step_type == clauses[-1][0].step_type:
                clauses[-1][1].append(step)
                continue
            clauses.append((step, []))
        return clauses


def _lead_verb(step, fallback: str) -> str:
    if step.keyword == "But":
        return "but"
    if step.keyword == "And":
        return "and"
    return fallback


def _chain_verb(step) -> str:
    return ".but" if step.keyword == "But" else ".and"


def _ts_call(indent: str, verb: str, step, continuations: Optional[List] = None) -> List[str]:
    lines = [
        f"{indent}{verb}({_ts_string(step.text)}, () => {{",
        f"{indent}  // TODO: implement step",
        f"{indent}}})",
    ]
    for extra in [*step.ands, *(continuations or [])]:
        lines.extend([
            f"{indent}  {_chain_verb(extra)}({_ts_string(extra.text)}, () => {{",
            f"{indent}    // TODO: implement step",
            f"{indent}  }})",
        ])
    lines[-1] += ";"
    return lines


def _example_names(stories) -> List[str]:
    names = []
    for story in stories:
        for scenario in story.scenarios:
            for name in scenario.examples:
                if name not in names:
                    names.append(name)
    return names


def _unescape(value: str) -> str:
    return value.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def _ts_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


class TypeScriptStory(CodeStory):
    scenario_type = TypeScriptScenario

    @classmethod
    def load_all(cls, content: str) -> List["TypeScriptStory"]:
        comment_chunks = re.split(r"(?=/\*\*\s*\n \* Story:)", content)
        named = [chunk for chunk in comment_chunks if re.search(r"\*\s*Story:", chunk)]
        if named and content.count("story(") <= len(named):
            stories = [cls.load(chunk, "") for chunk in comment_chunks if "Story:" in chunk or "story(" in chunk]
            return stories or [cls.load(content, "")]
        calls = list(re.finditer(r"(?m)^story\(", content))
        if len(calls) <= 1:
            return [cls.load(content, "")]
        stories = []
        for index, match in enumerate(calls):
            end = calls[index + 1].start() if index + 1 < len(calls) else len(content)
            stories.append(cls.load(content[match.start():end], ""))
        return stories

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
        lines.extend([" */", ""])
        example_line = CodeStory.background_example_line(story, "// ")
        if example_line:
            lines.append(example_line)
        lines.append(f"story({_ts_string(story.name)}, () => {{")
        for background in story.backgrounds:
            scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
            lines.append(f"  background('{scope}', ({{ given }}) => {{")
            for step in background.steps:
                if step.keyword.lower() == "given":
                    lines.extend(_ts_call("    ", "given", step))
            lines.append("  });")
            lines.append("")
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
        example_names = _example_names(stories)
        example_import = (
            [f"import {{ {', '.join(example_names)} }} from \"./examples\";", ""]
            if example_names else []
        )
        files[f"{parent}/{self.snake()}_story.test.ts"] = "\n".join([
            "/**",
            f" * Epic: {self.name}",
            f" * Orders: {self.order_path()}",
            " */",
            "",
            f'import {{ scenario, story }} from "{import_path}";',
            *example_import,
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
