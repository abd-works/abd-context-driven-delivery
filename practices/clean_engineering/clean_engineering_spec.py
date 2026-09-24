"""BDD spec for clean_engineering - action expansion (in-process)."""

import re
import sys
from pathlib import Path
from typing import Any

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness.agent_tools.agent_tools import AgentToolSet
import practices  # noqa: F401 - generator package on path
from harness.markdown import Markdown

from satisfy.satisfy import Satisfy
from validate.validate import Validate

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "practices" / "clean_engineering"
_GENERATE_DIR = _REPO_ROOT / "practices" / "actions" / "generate"
_VALIDATE_DIR = _REPO_ROOT / "practices" / "actions" / "validate"
_SATISFY_DIR = _REPO_ROOT / "practices" / "actions" / "satisfy"
_CLEAN_ENGINEERING_TOOLSET = "practices.clean_engineering.clean_engineering:CleanEngineering"
_VALIDATE_TOOLSET = "validate.validate:Validate"
_SATISFY_TOOLSET = "satisfy.satisfy:Satisfy"


class CleanEngineeringKit:
    def __init__(self) -> None:
        self.format_name = "python"
        self.fidelity = "modules"
        self.action_name = "guidance"
        self.context: dict[str, Any] = {}
        self.arguments: dict[str, Any] = {}
        self.kit_dir = _GENERATE_DIR

    def load(self) -> AgentToolSet:
        toolset_cls = type(AgentToolSet.instantiate(_CLEAN_ENGINEERING_TOOLSET))
        return toolset_cls(fidelity=self.fidelity, format=self.format_name)

    def expand(self, instance: AgentToolSet) -> Any:
        return instance.instructions[self.action_name].expand(self.context, self.arguments)

    def action_prose(self) -> str:
        return (self.kit_dir / f"{self.action_name}.md").read_text(encoding="utf-8")

    def contexts_section(self) -> str:
        return Markdown.from_label(self.load(), "overview").extract()

    def examples(self) -> str:
        return Markdown.from_label(self.load(), "examples").extract()

    def python_template(self) -> str:
        return Markdown.from_label(self.load(), "templates").extract()

    def context_rule_slugs(self, concepts_text: str) -> list[str]:
        pattern = re.compile(r"\*\*`([^`]+)`\*\*")
        return [
            match.group(1)
            for line in concepts_text.splitlines()
            if (match := pattern.search(line))
        ]

    def concept_bullet_lines(self, concepts_text: str) -> list[str]:
        pattern = re.compile(r"\*\*`([^`]+)`\*\*")
        return [line.strip() for line in concepts_text.splitlines() if pattern.search(line)]

    def concept_subsection_headings(self, concepts_text: str) -> list[str]:
        return [line for line in concepts_text.splitlines() if line.startswith("## ")]

    def format_subdirectory_names(self, module_dir: Path) -> list[str]:
        formats = module_dir / "formats"
        if not formats.is_dir():
            templates = module_dir / "templates"
            if templates.is_dir():
                return sorted(
                    p.stem.replace("clean_engineering-templates", "python")
                    for p in templates.iterdir()
                    if p.suffix == ".py"
                )
            return []
        return sorted(p.name for p in formats.iterdir() if p.is_dir())

    def assert_text_inlined(self, instructions: str, source: str) -> None:
        expect(source in instructions).to(be_true)

    def assert_contexts_inlined(self, instructions: str, concepts_text: str) -> None:
        slugs = self.context_rule_slugs(concepts_text)
        bullets = self.concept_bullet_lines(concepts_text)
        expect(len(slugs)).to(equal(len(bullets)))
        expect(len(slugs) > 0).to(be_true)
        for slug in slugs:
            expect(slug in instructions).to(be_true)
        if concepts_text not in instructions:
            for bullet in bullets:
                expect(bullet in instructions).to(be_true)


with description("CleanEngineering action expansion"):
    with context("a CleanEngineering generator constructed with format python"):
        with before.all:
            kit = CleanEngineeringKit()
            kit.format_name = "python"
            self.kit = kit
            self.clean_engineering = kit.load()
            self.contexts = self.clean_engineering.scoped_markdown()
            self.examples = self.clean_engineering.examples().expand()
            self.template = self.clean_engineering.templates().expand()

        with context("the guidance action is expanded"):
            with before.each:
                self.kit.action_name = "guidance"
                self.kit.context = {"format": "python"}
                self.response = self.kit.expand(self.clean_engineering)

            with it("should inline the fidelity-sliced Contexts section"):
                self.kit.assert_contexts_inlined(self.response.instructions, self.contexts)
                expect("## modules" in self.response.instructions).to(be_true)
                expect("\n## model\n" in self.response.instructions).to(equal(False))
                expect("\n## code\n" in self.response.instructions).to(equal(False))

            with it("should inline shopping-cart python examples and omit evals"):
                self.kit.assert_text_inlined(self.response.instructions, self.examples)
                expect("class IShoppingCart" in self.response.instructions).to(be_true)
                expect("evals/faultyAsset" in self.response.instructions).to(
                    equal(False)
                )

            with it("should inline the python template file"):
                self.kit.assert_text_inlined(self.response.instructions, self.template)

        with context("the Validate kit is expanded with this Guidance"):
            with before.each:
                self.kit.action_name = "validate"
                self.kit.arguments = {"guidance": [self.clean_engineering]}
                self.response = self.kit.expand(Validate())

            with it("should inline validate.md from the validate kit"):
                self.kit.kit_dir = _VALIDATE_DIR
                self.kit.assert_text_inlined(
                    self.response.instructions,
                    self.kit.action_prose(),
                )

        with context("the Satisfy kit is expanded with this Guidance"):
            with before.each:
                self.kit.action_name = "satisfy"
                self.kit.arguments = {"guidance": [self.clean_engineering]}
                self.response = self.kit.expand(Satisfy())

            with it("should inline satisfy.md from the satisfy kit"):
                self.kit.kit_dir = _SATISFY_DIR
                self.kit.assert_text_inlined(
                    self.response.instructions,
                    self.kit.action_prose(),
                )

    with context("a CleanEngineering generator at model markdown"):
        with before.each:
            kit = CleanEngineeringKit()
            kit.format_name = "markdown"
            kit.fidelity = "model"
            self.practice = kit.load()
            self.contexts = self.practice.scoped_markdown()
            self.examples = self.practice.examples().expand()

        with it("should keep Language and model contexts only"):
            expect("## Shared rules" in self.contexts).to(be_true)
            expect("honor-every-rule-in-the-artifact" in self.contexts).to(be_true)
            expect("## Language" in self.contexts).to(be_true)
            expect("### model" in self.contexts).to(be_true)
            expect("\n### modules\n" in self.contexts).to(equal(False))
            expect("\n### code\n" in self.contexts).to(equal(False))

        with it("should inline shopping-cart markdown examples and omit evals"):
            expect("ShoppingCart" in self.examples).to(be_true)
            expect("evals/" in self.examples).to(equal(False))
            expect("faultyAsset" in self.examples).to(equal(False))


with description("clean_engineering content helpers"):
    with context("load_concepts_section"):
        with it("should return non-empty text containing the word Contexts"):
            result = CleanEngineeringKit().contexts_section()
            expect(len(result) > 0).to(be_true)
            expect(result).to(contain("Contexts"))

    with context("load_examples"):
        with it("should return non-empty text"):
            expect(len(CleanEngineeringKit().examples()) > 0).to(be_true)

    with context("load_python_template"):
        with it("should return non-empty text"):
            expect(len(CleanEngineeringKit().python_template()) > 0).to(be_true)

    with context("concept_rule_slugs"):
        with it("should extract bold-backtick slugs from text"):
            text = "- **`maintain-abstraction-levels`** - desc.\n- **`no-useless-comments`** - desc."
            expect(CleanEngineeringKit().context_rule_slugs(text)).to(equal(["maintain-abstraction-levels", "no-useless-comments"]))

        with it("should return empty list when no slugs present"):
            expect(CleanEngineeringKit().context_rule_slugs("plain prose")).to(equal([]))

    with context("concept_bullet_lines"):
        with it("should return lines containing a slug"):
            text = "- **`slug-one`** - desc.\nsome prose\n- **`slug-two`** - other."
            lines = CleanEngineeringKit().concept_bullet_lines(text)
            expect(len(lines)).to(equal(2))

    with context("concept_subsection_headings"):
        with it("should return each ## heading line"):
            text = "# Concepts\n\n## RED-GREEN-REFACTOR\n\n## Arrange-Act-Assert\n"
            headings = CleanEngineeringKit().concept_subsection_headings(text)
            expect(len(headings)).to(equal(2))

    with context("format_subdirectory_names"):
        with it("should return a sorted list"):
            names = CleanEngineeringKit().format_subdirectory_names(_CLEAN_ENGINEERING_DIR)
            expect(names).to(equal(sorted(names)))
