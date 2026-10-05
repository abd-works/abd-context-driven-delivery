"""JavaScript nodes: JavaScript, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, StepType, Story


class JavaScriptScenario(CodeScenario):
    _CALL = re.compile(
        r"(?P<kw>\.(?:and|but)|(?<![.\w])(?:given|when|then|but))\(\s*(?P<q>['\"])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)",
        re.IGNORECASE,
    )
    _SCENARIO = re.compile(r"scenario\(\s*(?P<q>['\"])(?P<name>(?:\\.|(?!(?P=q)).)*)(?P=q)")
    _BACKGROUND = re.compile(r"background\(\s*(?:(?P<q>['\"])(?P<scope>\w+)(?P=q)\s*,\s*)?")
    _IMPORT = re.compile(
        r"import\s*\{(?P<names>[^}]+)\}\s*from\s*['\"][^'\"]*examples[^'\"]*['\"]"
    )

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
        lines = [f"    scenario({_js_string(scenario.name)}, ({{ given, when, then }}) => {{"]
        lines.extend(CodeScenario.background_lines(scenario, "      // "))
        if scenario.examples:
            lines.append("      // examples: " + ", ".join(scenario.examples))
        for step in scenario.steps:
            lines.append("      " + _js_chain(_lead_verb(step, step.keyword.lower()), step) + ";")
        lines.append("    });")
        return lines


def _example_names(stories) -> List[str]:
    names = []
    for story in stories:
        for scenario in story.scenarios:
            for name in scenario.examples:
                if name not in names:
                    names.append(name)
    return names


def _lead_verb(step, fallback: str) -> str:
    if step.keyword == "But":
        return "but"
    if step.keyword == "And":
        return "and"
    return fallback


def _chain_verb(step) -> str:
    return ".but" if step.keyword == "But" else ".and"


def _js_chain(verb: str, step) -> str:
    call = f"{verb}({_js_string(step.text)}, () => {{}})"
    for extra in step.ands:
        join = ".but" if extra.keyword == "But" else ".and"
        call += f"{join}({_js_string(extra.text)}, () => {{}})"
    return call


def _unescape(value: str) -> str:
    return value.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def _js_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


class JavaScriptStory(CodeStory):
    scenario_type = JavaScriptScenario

    @classmethod
    def load_all(cls, content: str) -> List["JavaScriptStory"]:
        chunks = re.split(r"(?=/\*\*\s*\n \* Story:)", content)
        stories = [cls.load(chunk, "") for chunk in chunks if "Story:" in chunk or "story(" in chunk]
        return stories or [cls.load(content, "")]

    @classmethod
    def load(cls, content: str, story_slug: str) -> "JavaScriptStory":
        name_match = re.search(r"story\(\s*(['\"])((?:\\.|(?!\1).)*)\1", content)
        story_name = name_match.group(2) if name_match else story_slug.replace("-", " ").title()
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
        lines.extend([
            " */",
            "",
        ])
        example_line = CodeStory.background_example_line(story, "// ")
        if example_line:
            lines.append(example_line)
        lines.append(f"story({_js_string(story.name)}, () => {{")
        if story.backgrounds:
            scope = story.backgrounds[0].name if re.fullmatch(r"\w+", story.backgrounds[0].name or "") else "each"
            lines.append(f"  background('{scope}', ({{ given }}) => {{")
            for background in story.backgrounds:
                for step in background.steps:
                    if step.keyword == "Given":
                        lines.append("    " + _js_chain("given", step) + ";")
            lines.append("  });")
        if not story.scenarios:
            lines.append("    // TODO: add main-flow scenario")
        for scenario in story.scenarios:
            lines.extend(JavaScriptScenario.create(scenario))
        lines.append("});")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def create(
        cls,
        story: Story,
        relative_story_test_path: str = "../../story-test.js",
        relative_types_path: str | None = None,
        **kwargs,
    ) -> str:
        import_path = relative_types_path or relative_story_test_path
        return "\n".join([
            f'import {{ background, scenario, story }} from "{import_path}";',
            "",
            cls.story_text(story),
        ])


class JavaScriptEpic(CodeEpic):
    def _write_stories(self, parent: str, files: dict, tests_root: str) -> None:
        stories = self._file_stories()
        if not stories:
            return
        relative = "../" * parent.count("/") + "story-test.js"
        blocks = "\n".join(JavaScriptStory.story_text(story) for story in stories)
        names = _example_names(stories)
        example_import = (
            [f"import {{ {', '.join(names)} }} from \"./examples\";", ""]
            if names else []
        )
        files[f"{parent}/{self.snake()}_story.test.js"] = "\n".join([
            "/**",
            f" * Epic: {self.name}",
            f" * Orders: {self.order_path()}",
            " */",
            "",
            f'import {{ background, scenario, story }} from "{relative}";',
            *example_import,
            "",
            blocks,
        ])
