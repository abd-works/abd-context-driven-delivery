"""Story files in the brace languages: TypeScript and JavaScript read and spell stories the same way."""
from __future__ import annotations

import posixpath
import re
from typing import List, Optional

from cdd_guidance.practices.stories.model.brace_story_file import BraceStoryFile
from cdd_guidance.practices.stories.model.code_story_model import CodeScenario, CodeStory, CodeStoryModel, StorySyntax, unescaped
from cdd_guidance.practices.stories.model.story_model import Background, Story
from cdd_guidance.practices.stories.model.story_writing import StepClause, StoryFilePlace, StoryWriting, background_examples_line, example_names_of, story_description


class BraceSyntax(StorySyntax):
    """How a brace-language story file writes stories: `story(...)`, `scenario(...)` and `background(...)` calls whose
    callbacks hold `given(...)` step calls. TypeScript and JavaScript read them the same way."""

    _CALL = re.compile(
        r"(?P<kw>\.(?:and|but)|(?<![.\w])(?:given|when|then|but))\(\s*(?P<q>['\"`])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)",
        re.IGNORECASE,
    )
    scenario_pattern = re.compile(r"scenario\(\s*(?P<q>['\"`])(?P<name>(?:\\.|(?!(?P=q)).)*)(?P=q)")
    _BACKGROUND = re.compile(r"background\(\s*(?:(?P<q>['\"])(?P<scope>\w+)(?P=q)\s*,\s*)?")
    import_pattern = re.compile(
        r"import\s*\{(?P<names>[^}]+)\}\s*from\s*['\"][^'\"]*examples[^'\"]*['\"]"
    )
    story_start = re.compile(r"(?=/\*\*\s*\n \* Story:)")
    story_mark = re.compile(r"\*\s*Story:")
    story_name_pattern = re.compile(r"\*\s*Story:\s*(?P<name>.+)")
    _CALL_NAME = re.compile(r"(?i)(?:shareStory|story)\(\s*(['\"])(?P<name>(?:\\.|(?!\1).)*)\1")

    def without_background(self, body: str) -> str:
        """The body with every background call and its callback taken out."""
        while True:
            match = self._BACKGROUND.search(body)
            if match is None:
                return body
            arrow = body.find("=>", match.end())
            brace = body.find("{", arrow if arrow >= 0 else match.end())
            if brace < 0:
                return body[:match.start()] + body[match.end():]
            inner = self._balanced(body, brace)
            body = body[:match.start()] + body[brace + len(inner) + 2:]

    def scenario_blocks(self, content: str) -> List[tuple]:
        blocks = []
        for match in self.scenario_pattern.finditer(content):
            arrow = content.find("=>", match.end())
            brace = content.find("{", arrow if arrow >= 0 else match.end())
            body = self._balanced(content, brace) if brace >= 0 else ""
            blocks.append((match.group("name"), body))
        return blocks

    def backgrounds_in(self, content: str) -> List[Background]:
        found: List[Background] = []
        for match in self._BACKGROUND.finditer(content):
            body = self._background_body(content, match)
            steps = self.steps_in(body) if body is not None else []
            if body is None or (not steps and not match.group("scope")):
                continue
            background = Background(match.group("scope") or "background", len(found) + 1)
            background.steps = [step for step in steps if step.keyword == "Given"]
            background.body = body
            found.append(background)
        return found

    def _background_body(self, content: str, match: re.Match) -> Optional[str]:
        """The code of the background call match opens, outside any scenario in it; None for a call inside a scenario
        or one with no callback."""
        if self._inside_scenario(content, match.start()):
            return None
        arrow = content.find("=>", match.end())
        brace = content.find("{", arrow if arrow >= 0 else match.end())
        return self._outside_scenarios(self._balanced(content, brace)) if brace >= 0 else None

    def _calls_in(self, body: str) -> List[tuple]:
        return [(match.group("kw").lstrip("."), unescaped(match.group("text"))) for match in self._CALL.finditer(body)]

    def _name_in(self, content: str) -> Optional[str]:
        """The name the story's comment gives, else the name its story call is made with."""
        call = self._CALL_NAME.search(content)
        return super()._name_in(content) or (call.group("name") if call else None)

    def _inside_scenario(self, content: str, pos: int) -> bool:
        for match in self.scenario_pattern.finditer(content):
            if match.start() >= pos:
                break
            brace = content.find("{", content.find("=>", match.end()))
            if brace < 0:
                continue
            inner = self._balanced(content, brace)
            if brace <= pos <= brace + len(inner):
                return True
        return False


class BraceScenario(CodeScenario):
    """A scenario read from a brace-language story file: TypeScript and JavaScript read it the same way."""

    syntax = BraceSyntax()

    def read(self, body: str, example_names: List[str] | None = None) -> None:
        self.backgrounds = self.syntax.backgrounds_in(body)
        super().read(self.syntax.without_background(body), example_names)


class BraceStory(CodeStory):
    """A story read from a brace-language story file: TypeScript and JavaScript read it the same way."""

    scenario_type = BraceScenario
    syntax = BraceScenario.syntax


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

    def file_header(self, place: StoryFilePlace) -> List[str]:
        names = example_names_of(place.stories)
        examples = posixpath.relpath(place.examples_folder, place.folder)
        example_import = [f"import {{ {', '.join(names)} }} from \"{examples}\"{self.statement_end}"] if names else []
        return ["/**", f" * Epic: {place.epic.name}", f" * Orders: {place.orders}", " */", "", self.story_test_import(place.folder), *example_import, ""]

    def story_test_import(self, parent: str) -> str:
        """The line that imports the story-test helpers into a story file written in the folder parent."""
        raise NotImplementedError(f"{type(self).__name__} must import its story-test helpers")

    def story_open(self, story: "Story") -> List[str]:
        lines = ["/**", f" * Story: {story.name}", *story_description(story, " * "), " */", ""]
        return lines + background_examples_line(story, "// ") + [f"story({self._quoted(story.name)}, () => {{"]

    def story_background_lines(self, background: "Background") -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
        lines = [f"  background({self._quoted(scope)}, ({{ given }}) => {{"]
        for step in background.steps:
            if step.keyword.lower() == "given":
                lines.extend(self._step_lines(StepClause(step, "given"), "    "))
        return lines + [f"  }}){self.statement_end}"]

    def scenario_background_lines(self, background: "Background", indent: str) -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "background"
        lines = [f"{indent}background({self._quoted(scope)}, ({{ given }}) => {{"]
        for clause in self._clauses(background.steps):
            clause.verb = clause.step.keyword.lower() if clause.step.keyword in ("And", "But") else "given"
            lines.extend(self._step_lines(clause, indent + self.language.indent))
        return lines + [f"{indent}}});"]


class BraceStoryModel(CodeStoryModel):
    """A story tree in a brace language, whose story files BraceStoryFile reads."""

    writing_type = BraceStoryWriting

    def story_file(self, content: str) -> BraceStoryFile:
        return BraceStoryFile(self.language, content)
