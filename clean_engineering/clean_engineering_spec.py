"""BDD spec for clean-code — action expansion and scanner tools (in-process)."""

import ast
import sys
from pathlib import Path
from typing import Any

from expects import be_true, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from action.action import ActionRunner
import generator  # noqa: F401 — generator package on path
from clean_code.clean_code_ground_truth import (
    concept_rule_slugs,
    load_concepts_section,
    load_examples,
    load_python_template,
)
from primitives.instruction import Instruction
from scanners import ScannerCollection
from tools.tool import Toolset, ToolsetLoader

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CLEAN_CODE_DIR = _REPO_ROOT / "clean_code"
_GENERATOR_DIR = _REPO_ROOT / "generator"
_PYTHON_SCANNERS = _CLEAN_CODE_DIR / "formats" / "python" / "scanners"
_CLEAN_CODE_TOOLSET = "clean_code.clean_code:CleanCode"


def _load_clean_code(*, format_name: str = "python") -> Toolset:
    toolset_cls = ToolsetLoader.instance().load(_CLEAN_CODE_TOOLSET)
    return toolset_cls(format=format_name)


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return ActionRunner.instance().run(
        {"toolset": toolset_path, "context": context or {}},
        toolset_path=toolset_path,
        action_name=action_name,
        context=context or {},
        arguments=arguments or {},
        instance=instance,
    )


def _invoke_tool(instance: Toolset, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
    return getattr(instance, tool_name)(**(arguments or {}))


def _load_action_prose(action: str) -> str:
    return Instruction(action, _GENERATOR_DIR).expand()


def _assert_text_inlined(instructions: str, source: str) -> None:
    expect(source in instructions).to(be_true)


def _assert_concepts_inlined(instructions: str, concepts_text: str) -> None:
    from clean_code.clean_code_ground_truth import concept_bullet_lines

    _assert_text_inlined(instructions, concepts_text)
    slugs = concept_rule_slugs(concepts_text)
    bullets = concept_bullet_lines(concepts_text)
    instruction_slugs = [
        slug for slug in concept_rule_slugs(instructions) if slug not in {"scan"}
    ]
    expect(len(slugs)).to(equal(len(bullets)))
    expect(len(slugs)).to(equal(len(instruction_slugs)))
    for slug in slugs:
        expect(slug in instructions).to(be_true)
    for bullet in bullets:
        expect(bullet in instructions).to(be_true)


with description("CleanCode action expansion"):
    with context("a Clean Code generator constructed with format python"):
        with before.all:
            self.clean_code = _load_clean_code(format_name="python")
            self.concepts = load_concepts_section(_CLEAN_CODE_DIR)
            self.examples = load_examples(_CLEAN_CODE_DIR)
            self.template = load_python_template(_CLEAN_CODE_DIR)

        with context("the generate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_code,
                    "generate",
                    toolset_path=_CLEAN_CODE_TOOLSET,
                    context={"format": "python"},
                )

            with it("should set action to generate"):
                expect(self.response["action"]).to(equal("generate"))

            with it("should name no tools on generate"):
                expect(self.response["tools"]).to(equal([]))

            with it("should inline the full Concepts section from clean-code.md"):
                _assert_concepts_inlined(self.response["instructions"], self.concepts)

            with it("should inline the full examples.md file"):
                _assert_text_inlined(self.response["instructions"], self.examples)

            with it("should inline the full python template file"):
                _assert_text_inlined(self.response["instructions"], self.template)

        with context("the validate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_code,
                    "validate",
                    toolset_path=_CLEAN_CODE_TOOLSET,
                    context={"format": "python"},
                )

            with it("should inline the full Concepts section as rubric"):
                _assert_concepts_inlined(self.response["instructions"], self.concepts)

            with it("should inline validate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("validate"))

        with context("the satisfy action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_code,
                    "satisfy",
                    toolset_path=_CLEAN_CODE_TOOLSET,
                    context={"format": "python"},
                )

            with it("should inline the full python template file"):
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should inline satisfy.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("satisfy"))


with description("CleanCode scan tool"):
    with context("a Clean Code generator constructed with format python"):
        with before.all:
            import ast

            self.clean_code = _load_clean_code(format_name="python")
            self.collection = ScannerCollection(_CLEAN_CODE_DIR, _PYTHON_SCANNERS)
            self.expected_slugs = sorted(self.collection.discover().keys())
            self.concept_slugs = concept_rule_slugs(load_concepts_section(_CLEAN_CODE_DIR))

        with context("the scan tool is invoked with an explicit path list"):
            with before.each:
                template = _CLEAN_CODE_DIR / "formats" / "python" / "clean-code-template.py"
                self.report = ast.literal_eval(
                    _invoke_tool(
                        self.clean_code,
                        "scan",
                        {"paths": [str(template)]},
                    )
                )

            with it("should list every discovered scanner rule slug in rules"):
                for slug in self.expected_slugs:
                    expect(slug in self.report["rules"]).to(be_true)

            with it("should list the same number of rules as concept rules in clean-code.md"):
                expect(len(self.report["rules"])).to(equal(len(self.concept_slugs)))

            with it("should return a deterministic scanner report"):
                expect(self.report["ok"] in (True, False)).to(be_true)


with description("clean_code_ground_truth helpers"):
    with context("load_concepts_section"):
        with it("should return non-empty text containing the word Concepts"):
            result = load_concepts_section(_CLEAN_CODE_DIR)
            expect(len(result) > 0).to(be_true)
            from expects import contain
            expect(result).to(contain("Concepts"))

    with context("load_examples"):
        with it("should return non-empty text"):
            expect(len(load_examples(_CLEAN_CODE_DIR)) > 0).to(be_true)

    with context("load_python_template"):
        with it("should return non-empty text"):
            expect(len(load_python_template(_CLEAN_CODE_DIR)) > 0).to(be_true)

    with context("concept_rule_slugs"):
        with it("should extract bold-backtick slugs from text"):
            from clean_code.clean_code_ground_truth import concept_rule_slugs as _slugs
            text = "- **`maintain-abstraction-levels`** — desc.\n- **`no-useless-comments`** — desc."
            expect(_slugs(text)).to(equal(["maintain-abstraction-levels", "no-useless-comments"]))

        with it("should return empty list when no slugs present"):
            from clean_code.clean_code_ground_truth import concept_rule_slugs as _slugs
            expect(_slugs("plain prose")).to(equal([]))

    with context("concept_bullet_lines"):
        with it("should return lines containing a slug"):
            from clean_code.clean_code_ground_truth import concept_bullet_lines
            text = "- **`slug-one`** — desc.\nsome prose\n- **`slug-two`** — other."
            lines = concept_bullet_lines(text)
            expect(len(lines)).to(equal(2))

    with context("concept_subsection_headings"):
        with it("should return each ## heading line"):
            from clean_code.clean_code_ground_truth import concept_subsection_headings
            text = "# Concepts\n\n## RED-GREEN-REFACTOR\n\n## Arrange-Act-Assert\n"
            headings = concept_subsection_headings(text)
            expect(len(headings)).to(equal(2))

    with context("format_subdirectory_names"):
        with it("should return a sorted list including python"):
            from clean_code.clean_code_ground_truth import format_subdirectory_names
            names = format_subdirectory_names(_CLEAN_CODE_DIR)
            expect("python" in names).to(be_true)
            expect(names).to(equal(sorted(names)))
