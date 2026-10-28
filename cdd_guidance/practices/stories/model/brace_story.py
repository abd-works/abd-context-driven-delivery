"""Story files in the brace languages: TypeScript and JavaScript read and spell stories the same way."""
from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import WrittenBlock
from cdd_guidance.practices.stories.model.brace_story_reader import BraceStoryReader
from cdd_guidance.practices.stories.model.code_story_model import CodeScenario, CodeStoryModel, StepClause, example_names_of
from cdd_guidance.practices.stories.model.story_model import Background, Scenario, Step, Story


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

    def calls_in(self, body: str) -> List[tuple]:
        return [(match.group("kw").lstrip("."), unescape(match.group("text"))) for match in self._CALL.finditer(body)]

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




def unescape(value: str) -> str:
    return value.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


class BraceStoryModel(CodeStoryModel):
    """A story tree in a brace language. TypeScript and JavaScript spell every block the same way."""

    statement_end = ";"

    def read_code(self, content: str, stories: List[Story], path: str) -> Optional[WrittenBlock]:
        return BraceStoryReader(self.language, content, unescape).read(stories, path)

    def clauses(self, steps: List[Step]) -> List[StepClause]:
        """A step repeating the previous step's phase continues that clause, so the
        fluent surface chains it rather than opening a second given/when/then."""
        clauses: List[StepClause] = []
        for step in steps:
            if clauses and step.step_type == clauses[-1][0].step_type:
                clauses[-1][2].append(step)
                continue
            clauses.append((step, self._lead_verb(step, step.keyword.lower()), []))
        return clauses

    def story_open(self, story: Story) -> List[str]:
        actor = (story.actors[0] if story.actors else "").strip()
        lines: List[str] = ["/**", f" * Story: {story.name}"]
        if actor:
            lines.append(f" * Actor: {actor}")
        lines.extend([" */", ""])
        example_line = self.story_type.background_example_line(story, "// ")
        if example_line:
            lines.append(example_line)
        return lines + [f"story({quoted(story.name)}, () => {{"]

    def story_close(self) -> List[str]:
        return ["});"]

    def story_background_lines(self, background: Background) -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "each"
        lines = [f"  background('{scope}', ({{ given }}) => {{"]
        for step in background.steps:
            if step.keyword.lower() == "given":
                lines.extend(self.step_lines((step, "given", []), "    "))
        return lines + ["  });"]

    def no_scenarios_lines(self) -> List[str]:
        return ["  // TODO: add main-flow scenario"]

    def scenario_open(self, scenario: Scenario, indent: str) -> List[str]:
        return [f"{indent}scenario({quoted(scenario.name)}, ({{ given, when, then }}) => {{"]

    def scenario_close(self, indent: str) -> List[str]:
        return [f"{indent}}});"]

    def scenario_background_lines(self, background: Background, indent: str) -> List[str]:
        scope = background.name if re.fullmatch(r"\w+", background.name or "") else "background"
        lines = [f"{indent}background('{scope}', ({{ given }}) => {{"]
        for lead, _verb, continuations in self.clauses(background.steps):
            lines.extend(self.step_lines((lead, self._lead_verb(lead, "given"), continuations), indent + self.language.indent))
        return lines + [f"{indent}}});"]

    def step_open(self, verb: str, step: Step, indent: str) -> str:
        return f"{indent}{verb}({quoted(step.text)}, {self._callback(step)}"

    def step_close(self, indent: str) -> str:
        return f"{indent}}})"

    def and_open(self, step: Step, indent: str) -> str:
        chain = ".but" if step.keyword == "But" else ".and"
        return f"{indent}  {chain}({quoted(step.text)}, {self._callback(step)}"

    def and_body_indent(self, indent: str) -> str:
        return indent + self.language.indent * 2

    def and_close(self, indent: str) -> str:
        return f"{indent}  }})"

    def step_placeholder(self) -> str:
        return self.language.comment("TODO: implement step")

    def _callback(self, step: Step) -> str:
        """The step's callback opening; async when its body awaits."""
        return "async () => {" if step.body.mentions("await") else "() => {"

    def _lead_verb(self, step: Step, fallback: str) -> str:
        if step.keyword == "But":
            return "but"
        if step.keyword == "And":
            return "and"
        return fallback
