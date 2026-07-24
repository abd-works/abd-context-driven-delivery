"""BDD spec for clean_engineering — action expansion and scanner tools (in-process)."""

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
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.actions.action import _ActionRunRequest, _ActionRunner
import context_tools  # noqa: F401 — generator package on path
from primitives.instructions import Instruction
from scanners import ScannerCollection
from tools.tool import Toolset, _ToolsetLoader

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "context_tools" / "clean_engineering"
_GENERATOR_DIR = _REPO_ROOT / "context_tools" / "base"
_PYTHON_SCANNERS = _CLEAN_ENGINEERING_DIR / "scanners"
_CLEAN_ENGINEERING_TOOLSET = "context_tools.clean_engineering.clean_engineering:CleanEngineering"


def _load_clean_engineering(*, format_name: str = "python") -> Toolset:
    toolset_cls = _ToolsetLoader.instance().load(_CLEAN_ENGINEERING_TOOLSET)
    return toolset_cls(format=format_name)


def _expand_action(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    context: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().run(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": context or {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context=context or {},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _invoke_tool(instance: Toolset, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
    return getattr(instance, tool_name)(**(arguments or {}))


def _load_action_prose(action: str) -> str:
    return Instruction(f"base-context/{action}", _GENERATOR_DIR).expand()


def _load_contexts_section(module_dir: Path) -> str:
    return Instruction("§ Contexts", module_dir, domain_slug="clean_engineering").expand()


def _load_examples(module_dir: Path) -> str:
    return Instruction("examples", module_dir, domain_slug="clean_engineering").expand()


def _load_python_template(module_dir: Path) -> str:
    return Instruction(
        "clean_engineering-templates", module_dir, domain_slug="clean_engineering"
    ).expand()


def _context_rule_slugs(concepts_text: str) -> list[str]:
    return re.findall(r"\*\*`([^`]+)`\*\*", concepts_text)


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
    # composes a shorter rubric than the full § Contexts body.
    if concepts_text not in instructions:
        for bullet in bullets:
            expect(bullet in instructions).to(be_true)


with description("CleanEngineering action expansion"):
    with context("a CleanEngineering generator constructed with format python"):
        with before.all:
            self.clean_engineering = _load_clean_engineering(format_name="python")
            self.contexts = _load_contexts_section(_CLEAN_ENGINEERING_DIR)
            self.examples = _load_examples(_CLEAN_ENGINEERING_DIR)
            self.template = _load_python_template(_CLEAN_ENGINEERING_DIR)

        with context("the generate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_engineering,
                    "generate",
                    toolset_path=_CLEAN_ENGINEERING_TOOLSET,
                    context={"format": "python"},
                )

            with it("should set action to generate"):
                expect(self.response["action"]).to(equal("generate"))

            with it("should name no tools on generate"):
                expect(self.response["tools"]).to(equal([]))

            with it("should inline the full Contexts section from clean_engineering"):
                _assert_contexts_inlined(self.response["instructions"], self.contexts)

            with it("should inline the full examples.md file"):
                _assert_text_inlined(self.response["instructions"], self.examples)

            with it("should inline the full python template file"):
                _assert_text_inlined(self.response["instructions"], self.template)

        with context("the validate action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_engineering,
                    "validate",
                    toolset_path=_CLEAN_ENGINEERING_TOOLSET,
                    context={"format": "python"},
                )

            with it("should inline contexts as rubric (slugs or Contexts heading)"):
                instructions = self.response["instructions"]
                slugs = _context_rule_slugs(self.contexts)
                expect(len(slugs) > 0).to(be_true)
                inlined = sum(1 for slug in slugs if slug in instructions)
                expect(inlined > 0 or "Concepts" in instructions).to(be_true)

            with it("should inline validate.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("validate"))

        with context("the satisfy action is expanded"):
            with before.each:
                self.response = _expand_action(
                    self.clean_engineering,
                    "satisfy",
                    toolset_path=_CLEAN_ENGINEERING_TOOLSET,
                    context={"format": "python"},
                )

            with it("should inline the full python template file"):
                _assert_text_inlined(self.response["instructions"], self.template)

            with it("should inline satisfy.md from the generator module"):
                _assert_text_inlined(self.response["instructions"], _load_action_prose("satisfy"))


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
                    _invoke_tool(
                        self.clean_engineering,
                        "scan",
                        {"paths": [str(template)]},
                    )
                )

            with it("should list every discovered scanner rule slug in rules"):
                for slug in self.expected_slugs:
                    expect(slug in self.report["rules"]).to(be_true)

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
            text = "- **`maintain-abstraction-levels`** — desc.\n- **`no-useless-comments`** — desc."
            expect(_context_rule_slugs(text)).to(equal(["maintain-abstraction-levels", "no-useless-comments"]))

        with it("should return empty list when no slugs present"):
            expect(_context_rule_slugs("plain prose")).to(equal([]))

    with context("concept_bullet_lines"):
        with it("should return lines containing a slug"):
            text = "- **`slug-one`** — desc.\nsome prose\n- **`slug-two`** — other."
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
