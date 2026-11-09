"""Story files in the brace languages: TypeScript and JavaScript read and spell stories the same way."""
from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.stories.model.brace_story_file import BraceStoryFile
from cdd_guidance.practices.stories.model.code_story_model import CodeScenario, CodeStory, CodeStoryModel, unescaped
from cdd_guidance.practices.stories.model.story_model import Background, Epic, Story
from cdd_guidance.practices.stories.model.story_writing import StoryWriting, background_examples_line, example_names_of, story_description


class BraceScenario(CodeScenario):
    """A scenario read from a brace-language story file: TypeScript and JavaScript read it the same way."""

    _CALL = re.compile(
        r"(?P<kw>\.(?:and|but)|(?<![.\w])(?:given|when|then|but))\(\s*(?P<q>['\"`])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)",
        re.IGNORECASE,
    )
    _SCENARIO = re.compile(r"scenario\(\s*(?P<q>['\"`])(?P<name>(?:\\.|(?!(?P=q)).)*)(?P=q)")
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

    @classmethod
    def calls_in(cls, body: str) -> List[tuple]:
        return [(match.group("kw").lstrip("."), unescaped(match.group("text"))) for match in cls._CALL.finditer(body)]

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
            steps = cls.steps_from(cls.calls_in(body))
            if not steps and not match.group("scope"):
                continue
            background = Background(match.group("scope") or "background", len(found) + 1)
            background.steps = [step for step in steps if step.keyword == "Given"]
            background.body = body
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


class BraceStory(CodeStory):
    """A story read from a brace-language story file: TypeScript and JavaScript read it the same way."""

    scenario_type = BraceScenario
    _STORY_START = re.compile(r"(?=/\*\*\s*\n \* Story:)")
    _STORY_MARK = re.compile(r"\*\s*Story:")
    _NAME = re.compile(r"\*\s*Story:\s*(?P<name>.+)")
    _CALL_NAME = re.compile(r"(?i)(?:shareStory|story)\(\s*(['\"])(?P<name>(?:\\.|(?!\1).)*)\1")

    @classmethod
    def name_in(cls, content: str) -> Optional[str]:
        """The name the story's comment gives, else the name its story call is made with."""
        call = cls._CALL_NAME.search(content)
        return super().name_in(content) or (call.group("name") if call else None)





class BraceStoryWriting(StoryWriting):
    """How TypeScript and JavaScript write stories: `story(...)`, `scenario(...)`, and `given(...)` calls whose
    callbacks hold the code, a step repeating its phase chained onto the one before it. The two differ only in the line
    that imports the story-test helpers (`story_test_import`)."""

    statement_end = ";"
    story_closing = ["});"]
    no_scenarios = ["  // TODO: add main-flow scenario"]
    placeholder = "// TODO: implement step"
    scenario_opening = "{indent}scenario({name}, ({{ given, when, then }}) => {{"
    scenario_closing = "{indent}}});"
    step_opening = "{indent}{verb}({text}, {callback}"
    step_closing = "{indent}}})"
    and_opening = "{indent}  {verb}({text}, {callback}"
    and_closing = "{indent}  }})"
    and_verbs = (".and", ".but")
    and_body_depth = 2
    chains_repeated_phase = True

    def file_header(self, epic: Epic, parent: str) -> List[str]:
        names = example_names_of(list(epic.stories))
        example_import = [f"import {{ {', '.join(names)} }} from \"./examples\"{self.statement_end}"] if names else []
        return ["/**", f" * Epic: {epic.name}", f" * Orders: {epic.order_path()}", " */", "", self.story_test_import(parent), *example_import, ""]

    def story_test_import(self, parent: str) -> str:
        """The line that imports the story-test helpers into a story file written under parent."""
        raise NotImplementedError(f"{type(self).__name__} must import its story-test helpers")

    def story_open(self, story: "Story") -> List[str]:
        lines = ["/**", f" * Story: {story.name}", *story_description(story, " * "), " */", ""]
        return lines + background_examples_line(story, "// ") + [f"story({self.quoted(story.name)}, () => {{"]

    def story_background_lines(self, background: "Background") -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
        lines = [f"  background({self.quoted(scope)}, ({{ given }}) => {{"]
        for step in background.steps:
            if step.keyword.lower() == "given":
                lines.extend(self.step_lines((step, "given", []), "    "))
        return lines + [f"  }}){self.statement_end}"]

    def scenario_background_lines(self, background: "Background", indent: str) -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "background"
        lines = [f"{indent}background({self.quoted(scope)}, ({{ given }}) => {{"]
        for lead, _verb, continuations in self.clauses(background.steps):
            verb = lead.keyword.lower() if lead.keyword in ("And", "But") else "given"
            lines.extend(self.step_lines((lead, verb, continuations), indent + self.language.indent))
        return lines + [f"{indent}}});"]


class BraceStoryModel(CodeStoryModel):
    """A story tree in a brace language, whose story files BraceStoryFile reads."""

    writing_type = BraceStoryWriting

    def story_file(self, content: str) -> BraceStoryFile:
        return BraceStoryFile(self.language, content)
