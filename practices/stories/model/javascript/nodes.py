"""JavaScript nodes: JavaScript, then code, then the story model."""
from __future__ import annotations

import re
from typing import List

from practices.stories.model.code_story_model import CodeEpic, CodeScenario, CodeStory
from practices.stories.model.story_model import Background, StepType, Story


class JavaScriptScenario(CodeScenario):
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
        lines = [f"    scenario({_js_string(scenario.name)}, ({{ given, when, then }}) => {{"]
        for step in scenario.steps_in(StepType.GIVEN):
            lines.append("      " + _js_chain("given", step) + ";")
        for when_steps, then_steps in scenario.when_then_runs():
            if when_steps:
                line = _js_chain("when", when_steps[0])
                for step in when_steps[1:]:
                    line += _js_chain(".and", step)
                lines.append("      " + line + ";")
            if then_steps:
                line = _js_chain("then", then_steps[0])
                for step in then_steps[1:]:
                    line += _js_chain(".and", step)
                lines.append("      " + line + ";")
        lines.append("    });")
        return lines


def _js_chain(verb: str, step) -> str:
    call = f"{verb}({_js_string(step.text)}, () => {{}})"
    for extra in step.ands:
        join = ".but" if extra.keyword == "But" else ".and"
        call += f"{join}({_js_string(extra.text)}, () => {{}})"
    return call


def _js_string(value: str) -> str:
    cleaned = re.sub(r"`([^`]+)`", r"\1", value)
    cleaned = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
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
            f"story({_js_string(story.name)}, () => {{",
            "  background('each', ({ given }) => {",
        ])
        for background in story.backgrounds:
            for step in background.steps:
                lines.append(f"    given({_js_string(step.text)}, () => {{}});")
        if not story.scenarios:
            lines.append("    // TODO: add main-flow scenario")
        for scenario in story.scenarios:
            lines.extend(JavaScriptScenario.create(scenario))
        lines.append("  });")
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
    def _file_stories(self):
        return [story for story in self.stories if story.scenarios]

    def _write_stories(self, parent: str, files: dict, tests_root: str) -> None:
        stories = self._file_stories()
        if not stories:
            return
        relative = "../" * parent.count("/") + "story-test.js"
        blocks = "\n".join(JavaScriptStory.story_text(story) for story in stories)
        files[f"{parent}/{self.snake()}_story.test.js"] = "\n".join([
            "/**",
            f" * Epic: {self.name}",
            " */",
            "",
            f'import {{ background, scenario, story }} from "{relative}";',
            "",
            blocks,
        ])
