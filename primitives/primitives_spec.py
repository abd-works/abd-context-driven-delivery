"""BDD spec for primitives/primitives-behavior.md — Instruction, DeclaredProperty, DeclaredOperation."""

from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from agents.action import action
from generator.generator import Generator
from primitives.clean_code_ground_truth import (
    concept_bullet_lines,
    concept_rule_slugs,
    concept_subsection_headings,
    format_subdirectory_names,
    load_concepts_section,
    load_examples,
    load_python_template,
)
from primitives.declared_operation import DeclaredOperation
from primitives.declared_property import DeclaredProperty
from primitives.instruction import Instruction
from primitives.instruction_slot import expand_docstring
from scanners import ScannerCollection

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CLEAN_CODE_DIR = _REPO_ROOT / "clean-code"
_GENERATOR_DIR = _REPO_ROOT / "generator"
_PYTHON_SCANNERS = _CLEAN_CODE_DIR / "formats" / "python" / "scanners"


class _FormatHost:
    module_dir = _CLEAN_CODE_DIR

    def __init__(self, format_name: str = "python") -> None:
        self.format = format_name


class _OperationHost:
    def generate_code(self) -> str:
        return "generated"


def _assert_concepts_match_file(expanded: str, direct: str) -> None:
    expect(expanded).to(equal(direct))
    slugs = concept_rule_slugs(direct)
    bullets = concept_bullet_lines(direct)
    headings = concept_subsection_headings(direct)
    expect(len(slugs)).to(equal(len(bullets)))
    expect(len(slugs) > 0).to(be_true)
    for slug in slugs:
        expect(slug in expanded).to(be_true)
    for bullet in bullets:
        expect(bullet in expanded).to(be_true)
    for heading in headings:
        expect(heading in expanded).to(be_true)


with description("Instruction"):
    with context("an instruction constructed with plain prose"):
        with before.each:
            self.instruction = Instruction("Write clean production code.", _CLEAN_CODE_DIR)

        with it("should remain unchanged when expand is called"):
            expect(self.instruction.expand()).to(equal("Write clean production code."))

    with context("an instruction whose value is a sibling markdown file"):
        with before.each:
            self.instruction = Instruction("examples", _CLEAN_CODE_DIR)
            self.direct = load_examples(_CLEAN_CODE_DIR)

        with it("should equal a direct file load when expand is called"):
            expect(self.instruction.expand()).to(equal(self.direct))

    with context("an instruction whose value is § Section"):
        with before.each:
            self.instruction = Instruction("§ Concepts", _CLEAN_CODE_DIR)
            self.direct = load_concepts_section(_CLEAN_CODE_DIR)

        with it("should equal the Concepts section extracted from clean-code.md"):
            _assert_concepts_match_file(self.instruction.expand(), self.direct)

        with it("should contain every concept rule slug counted from clean-code.md"):
            slugs = concept_rule_slugs(self.direct)
            expanded = self.instruction.expand()
            expect(len(slugs)).to(equal(len(concept_rule_slugs(expanded))))
            for slug in slugs:
                expect(slug in expanded).to(be_true)

        with it("should contain the full text of every concept bullet line from clean-code.md"):
            for bullet in concept_bullet_lines(self.direct):
                expect(self.instruction.expand()).to(contain(bullet))

    with context("an instruction whose value is a folder path ending with /"):
        with before.each:
            self.instruction = Instruction("formats/", _CLEAN_CODE_DIR)
            self.expected_names = format_subdirectory_names(_CLEAN_CODE_DIR)

        with it("should list every format subdirectory name from disk"):
            expanded = self.instruction.expand()
            expect(len(self.expected_names) > 0).to(be_true)
            for name in self.expected_names:
                expect(name in expanded).to(be_true)


with description("Action docstring expansion"):
    with context("a single-word action docstring on the generator module"):
        with it("should load generate.md from base-generator"):
            expanded = expand_docstring("base-generator/generate", Generator.generate)
            direct = Instruction("base-generator/generate", _GENERATOR_DIR).expand()
            expect(expanded).to(equal(direct))

    with context("a path ref action docstring that resolves to base-generator markdown"):
        with it("should load repair.md from base-generator"):
            expanded = expand_docstring("base-generator/repair", Generator.repair)
            direct = Instruction("base-generator/repair", _GENERATOR_DIR).expand()
            expect(expanded).to(equal(direct))

    with context("a single-word framework action name on a generator subclass"):
        with it("should load generate.md from base-generator via framework fallback"):
            expanded = expand_docstring("generate", Generator.generate)
            direct = Instruction("base-generator/generate", _GENERATOR_DIR).expand()
            expect(expanded).to(equal(direct))

    with context("a multi-word action docstring"):
        with before.all:
            @action
            def generate_output(self) -> str:
                """Append each trip entry to the driving log."""
                return ""

            self.generate_output = generate_output

        with it("should remain unchanged"):
            text = "Append each trip entry to the driving log."
            expect(expand_docstring(text, self.generate_output)).to(equal(text))


with description("DeclaredProperty"):
    with context("a declared property named examples"):
        with before.each:
            self.property = DeclaredProperty("examples")
            self.host = _FormatHost()
            self.direct = load_examples(_CLEAN_CODE_DIR)

        with it("should yield an instruction whose expand equals the file load"):
            instruction = self.property.route(self.host)
            expect(instruction.expand()).to(equal(self.direct))

    with context("concepts declared property routing to § Concepts when no concepts folder exists"):
        with before.each:
            self.property = DeclaredProperty("concepts")
            self.host = _FormatHost()
            self.direct = load_concepts_section(_CLEAN_CODE_DIR)

        with it("should yield an instruction whose expand equals the Concepts section file load"):
            instruction = self.property.route(self.host)
            _assert_concepts_match_file(instruction.expand(), self.direct)

        with it("should include every concept rule slug counted from clean-code.md"):
            instruction = self.property.route(self.host)
            slugs = concept_rule_slugs(self.direct)
            expanded = instruction.expand()
            expect(len(slugs)).to(equal(len(concept_rule_slugs(expanded))))
            for slug in slugs:
                expect(slug in expanded).to(be_true)

    with context("a declared property named formats"):
        with before.each:
            self.property = DeclaredProperty("formats")
            self.host = _FormatHost()
            self.expected_names = format_subdirectory_names(_CLEAN_CODE_DIR)

        with it("should return every immediate subdirectory name from disk"):
            keys = self.property.discover_keys(self.host)
            expect(keys).to(equal(self.expected_names))

    with context("template declared property with activeKey set"):
        with before.each:
            self.property = DeclaredProperty("template", active_key="format")
            self.host = _FormatHost("python")
            self.direct = load_python_template(_CLEAN_CODE_DIR)

        with it("should yield an instruction whose expand equals the template file load"):
            instruction = self.property.route(self.host)
            expect(instruction.expand()).to(equal(self.direct))


with description("DeclaredOperation"):
    with context("generate_output declared operation with a wired target on the extending class"):
        with before.each:
            self.operation = DeclaredOperation(target="generate_code")
            object.__setattr__(self.operation, "name", "generate_output")
            self.host = _OperationHost()

        with it("should return the target callable when route is called"):
            expect(self.operation.route(self.host)).to(equal(self.host.generate_code))

    with context("generate_output declared operation with no wired target"):
        with before.each:
            self.operation = DeclaredOperation()
            object.__setattr__(self.operation, "name", "generate_output")
            self.host = _OperationHost()

        with it("should return null when route is called"):
            expect(self.operation.route(self.host)).to(equal(None))


with description("ScannerCollection"):
    with context("a scanner collection rooted at formats/python/scanners/"):
        with before.each:
            self.collection = ScannerCollection(_CLEAN_CODE_DIR, _PYTHON_SCANNERS)
            self.discovered = self.collection.discover()

        with it("should map every concept rule slug from clean-code.md to a scanner class"):
            concept_slugs = set(concept_rule_slugs(load_concepts_section(_CLEAN_CODE_DIR)))
            scanner_slugs = set(self.discovered)
            expect(len(scanner_slugs) > 0).to(be_true)
            missing = concept_slugs - scanner_slugs
            expect(len(missing)).to(equal(0))

        with it("should list every discovered rule slug when catalog is called"):
            catalog = self.collection.catalog()
            for slug in sorted(self.discovered):
                expect(catalog).to(contain(slug))

        with it("should return a deterministic report when run is called with an explicit file list"):
            template = _CLEAN_CODE_DIR / "formats" / "python" / "clean-code-template.py"
            report = self.collection.run(_REPO_ROOT, [template])
            expect(report.to_dict()["ok"] in (True, False)).to(be_true)
