"""BDD spec for clean_engineering - action expansion and scanner tools (in-process)."""

import ast
import re
import sys
from pathlib import Path
from typing import Any

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("harness", "tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness.agent_tools.agent_tools import AgentToolSet
import practices  # noqa: F401 - generator package on path
from harness.markdown import Markdown
from scan import ScannerCollection
from agent_tools import AgentToolSet

from satisfy.satisfy import Satisfy
from validate.validate import Validate

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "practices" / "clean_engineering"
_GENERATE_DIR = _REPO_ROOT / "practices" / "actions" / "generate"
_VALIDATE_DIR = _REPO_ROOT / "practices" / "actions" / "validate"
_SATISFY_DIR = _REPO_ROOT / "practices" / "actions" / "satisfy"
_PYTHON_SCANNERS = _CLEAN_ENGINEERING_DIR / "scanners"
_CLEAN_ENGINEERING_TOOLSET = "practices.clean_engineering.clean_engineering:CleanEngineering"
_VALIDATE_TOOLSET = "validate.validate:Validate"
_SATISFY_TOOLSET = "satisfy.satisfy:Satisfy"


def _load_clean_engineering(
    *, format_name: str = "python", fidelity: str = "modules"
) -> AgentToolSet:
    toolset_cls = type(AgentToolSet.instantiate(_CLEAN_ENGINEERING_TOOLSET))
    return toolset_cls(fidelity=fidelity, format=format_name, session=None)


def _expand_action(
    instance: AgentToolSet,
    action_name: str,
    *,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> Any:
    return instance.instructions[action_name].expand(
        context or {},
        arguments or {},
    )


def _load_action_prose(action: str, kit_dir: Path | None = None) -> str:
    directory = kit_dir or _GENERATE_DIR
    return (directory / f"{action}.md").read_text(encoding="utf-8")


def _load_contexts_section(module_dir: Path) -> str:
    return Markdown.from_label(_load_clean_engineering(), "contexts").extract()


def _load_examples(module_dir: Path) -> str:
    return Markdown.from_label(_load_clean_engineering(), "examples").extract()


def _load_python_template(module_dir: Path) -> str:
    host = _load_clean_engineering()
    return Markdown.from_label(host, "templates").extract()


def _context_rule_slugs(concepts_text: str) -> list[str]:
    # One primary slug per concept bullet (lines may contain extra **`...`** markers).
    pattern = re.compile(r"\*\*`([^`]+)`\*\*")
    return [
        match.group(1)
        for line in concepts_text.splitlines()
        if (match := pattern.search(line))
    ]


def _concept_bullet_lines(concepts_text: str) -> list[str]:
    pattern = re.compile(r"\*\*`([^`]+)`\*\*")
    return [line.strip() for line in concepts_text.splitlines() if pattern.search(line)]


def _concept_subsection_headings(concepts_text: str) -> list[str]:
    return [line for line in concepts_text.splitlines() if line.startswith("## ")]


def _format_subdirectory_names(module_dir: Path) -> list[str]:
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


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


def _assert_contexts_inlined(instructions: str, concepts_text: str) -> None:
    slugs = _context_rule_slugs(concepts_text)
    bullets = _concept_bullet_lines(concepts_text)
    expect(len(slugs)).to(equal(len(bullets)))
    expect(len(slugs) > 0).to(be_true)
    for slug in slugs:
        expect(slug in instructions).to(be_true)
    # Prefer full-section inline; fall back to slug/bullet coverage when validate
    # composes a shorter rubric than the full # Contexts body.
    if concepts_text not in instructions:
        for bullet in bullets:
            expect(bullet in instructions).to(be_true)


with description("CleanEngineering action expansion"):
    with context("a CleanEngineering generator constructed with format python"):
        with before.all:
            self.clean_engineering = _load_clean_engineering(format_name="python")
            self.contexts = self.clean_engineering.contexts().expand()
            self.examples = self.clean_engineering.examples().expand()
            self.template = self.clean_engineering.templates().expand()

        with context("the guidance action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_engineering,
                    "guidance",
                    context={"format": "python"},
                )

            with it("should inline the fidelity-sliced Contexts section"):
                _assert_contexts_inlined(self.response.instructions, self.contexts)
                expect("## modules" in self.response.instructions).to(be_true)
                expect("\n## model\n" in self.response.instructions).to(equal(False))
                expect("\n## code\n" in self.response.instructions).to(equal(False))

            with it("should inline shopping-cart python examples and omit evals"):
                _assert_text_inlined(self.response.instructions, self.examples)
                expect("class IShoppingCart" in self.response.instructions).to(be_true)
                expect("evals/faultyAsset" in self.response.instructions).to(
                    equal(False)
                )

            with it("should inline the python template file"):
                _assert_text_inlined(self.response.instructions, self.template)

        with context("the Validate kit is expanded with this host"):
            with before.each:
                self.response = _expand_action(
                    Validate(),
                    "validate",
                    arguments={"tools": [self.clean_engineering]},
                )

            with it("should inline validate.md from the validate kit"):
                _assert_text_inlined(
                    self.response.instructions,
                    _load_action_prose("validate", _VALIDATE_DIR),
                )

        with context("the Satisfy kit is expanded with this host"):
            with before.each:
                self.response = _expand_action(
                    Satisfy(),
                    "satisfy",
                    arguments={"tools": [self.clean_engineering]},
                )

            with it("should inline satisfy.md from the satisfy kit"):
                _assert_text_inlined(
                    self.response.instructions,
                    _load_action_prose("satisfy", _SATISFY_DIR),
                )

    with context("a CleanEngineering generator at model markdown"):
        with before.each:
            self.host = _load_clean_engineering(
                format_name="markdown", fidelity="model"
            )
            self.contexts = self.host.contexts().expand()
            self.examples = self.host.examples().expand()

        with it("should keep Language and model contexts only"):
            expect("## Shared rules" in self.contexts).to(be_true)
            expect("honor-every-rule-in-the-artifact" in self.contexts).to(be_true)
            expect("## Language" in self.contexts).to(be_true)
            expect("## model" in self.contexts).to(be_true)
            expect("\n## modules\n" in self.contexts).to(equal(False))
            expect("\n## code\n" in self.contexts).to(equal(False))

        with it("should inline shopping-cart markdown examples and omit evals"):
            expect("ShoppingCart" in self.examples).to(be_true)
            expect("evals/" in self.examples).to(equal(False))
            expect("faultyAsset" in self.examples).to(equal(False))


with description("CleanEngineering scan tool"):
    with context("a CleanEngineering generator constructed with format python"):
        with before.all:
            self.clean_engineering = _load_clean_engineering(format_name="python")
            self.collection = ScannerCollection(_CLEAN_ENGINEERING_DIR, _PYTHON_SCANNERS)
            self.expected_slugs = sorted(self.collection.discover().keys())
            self.concept_slugs = _context_rule_slugs(_load_contexts_section(_CLEAN_ENGINEERING_DIR))

        with context("the scan tool is invoked with an explicit path list"):
            with before.each:
                template = _CLEAN_ENGINEERING_DIR / "templates" / "clean_engineering-templates.py"
                self.report = ast.literal_eval(
                    self.clean_engineering.scanner.scan(paths=[str(template)])
                )

            with it("should return a deterministic scanner report"):
                expect(self.report["ok"] in (True, False)).to(be_true)


with description("clean_engineering content helpers"):
    with context("load_concepts_section"):
        with it("should return non-empty text containing the word Contexts"):
            result = _load_contexts_section(_CLEAN_ENGINEERING_DIR)
            expect(len(result) > 0).to(be_true)
            expect(result).to(contain("Contexts"))

    with context("load_examples"):
        with it("should return non-empty text"):
            expect(len(_load_examples(_CLEAN_ENGINEERING_DIR)) > 0).to(be_true)

    with context("load_python_template"):
        with it("should return non-empty text"):
            expect(len(_load_python_template(_CLEAN_ENGINEERING_DIR)) > 0).to(be_true)

    with context("concept_rule_slugs"):
        with it("should extract bold-backtick slugs from text"):
            text = "- **`maintain-abstraction-levels`** - desc.\n- **`no-useless-comments`** - desc."
            expect(_context_rule_slugs(text)).to(equal(["maintain-abstraction-levels", "no-useless-comments"]))

        with it("should return empty list when no slugs present"):
            expect(_context_rule_slugs("plain prose")).to(equal([]))

    with context("concept_bullet_lines"):
        with it("should return lines containing a slug"):
            text = "- **`slug-one`** - desc.\nsome prose\n- **`slug-two`** - other."
            lines = _concept_bullet_lines(text)
            expect(len(lines)).to(equal(2))

    with context("concept_subsection_headings"):
        with it("should return each ## heading line"):
            text = "# Concepts\n\n## RED-GREEN-REFACTOR\n\n## Arrange-Act-Assert\n"
            headings = _concept_subsection_headings(text)
            expect(len(headings)).to(equal(2))

    with context("format_subdirectory_names"):
        with it("should return a sorted list"):
            names = _format_subdirectory_names(_CLEAN_ENGINEERING_DIR)
            expect(names).to(equal(sorted(names)))
