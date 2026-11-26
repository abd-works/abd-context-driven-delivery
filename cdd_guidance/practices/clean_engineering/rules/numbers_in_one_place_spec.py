"""A number a Clean Engineering rule holds is written once, in code: the check reads it there, and the rule's text in
the practice's document is filled from it when the guidance is read. Exploratory testing, shortcoming 8: a limit typed
in the rule's text and again in its check lets validate report a number its rule does not say."""
import sys
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.measures import code_measures
from cdd_guidance.practices.clean_engineering.measures.code_measures import CODE_LINES, PARAMETERS_TAKEN, ChosenTools
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG, rule_numbers
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_source

_FOLDER = Path(__file__).resolve().parents[1]
# Every way a rule's number was typed by hand in the practice's document.
_TYPED_NUMBERS = (
    "35%", "20 statements", "three levels", "0-3 parameters",
    "10 paths", "past ten", "15 or lower", "50 lines", "100 or lower", "30 methods",
    "14 other classes", "at 50 or fewer", "800 lines", "of 20 or higher", "40 or fewer",
)
_MEASURED_LIMIT_RULES = (
    "limit-paths-through-a-function", "keep-functions-readable", "limit-function-lines",
    "limit-class-complexity", "limit-class-methods",
)
_SIX_STATEMENTS = "def total(prices: list) -> int:\n" + "".join(f"    sum_{index} = {index}\n" for index in range(5)) + "    return sum_4\n"
_NESTED_TWICE = "def first(text: list) -> str:\n    for line in text:\n        if line:\n            return line\n    return ''\n"
_FOUR_PARAMETERS = "class Cart:\n    def add(self, sku: str, quantity: int, price: int, note: str) -> None:\n        self.sku = sku\n"
_THREE_PARAMETERS = "class Cart:\n    def add(self, sku: str, quantity: int, price: int) -> None:\n        self.sku = sku\n"


def _rule_text(fidelity: str, slug: str) -> str:
    return next(rule.body for rule in CleanEngineering(fidelity=fidelity).fidelities.current.every_rule if rule.slug == slug)


def _hits(slug: str, fixture) -> list[str]:
    return fixture.hits(BY_SLUG[slug])


with description("a number a Clean Engineering rule holds") as self:
    with context("as the code holds it"):
        with it("should name the share of a module's methods its seam may hold"):
            expect(rule_numbers.MOST_SEAM_SHARE).to(equal(0.35))

        with it("should name the most statements and nested levels an operation has"):
            expect((rule_numbers.MOST_STATEMENTS, rule_numbers.MOST_NESTED_LEVELS)).to(equal((20, 3)))

        with it("should name the most parameters an operation takes among the shipped limits, which a project's config may change"):
            expect(code_measures.SHIPPED_LIMITS[PARAMETERS_TAKEN.name]).to(equal(3))

    with context("in the practice's own files"):
        with it("should not be typed in the practice's document, which carries a marker for it"):
            written = (_FOLDER / "clean_engineering.md").read_text(encoding="utf-8")
            expect([number for number in _TYPED_NUMBERS if number in written]).to(equal([]))

        with it("should not be typed in a check, which reads the named value"):
            checks = ("practice_wide_rules.py", "operation_checks.py", "limit_operation_parameters.py", "rule_numbers.py")
            written = "\n".join((_FOLDER / "rules" / check).read_text(encoding="utf-8") for check in checks)
            expect([typed for typed in ("limit = 20", "limit = 3", "PARAMETERS = 3") if typed in written]).to(equal([]))

    with context("as the guidance is read"):
        with it("should write the seam's share into deep-module"):
            expect(_rule_text("modules", "deep-module")).to(contain("at most **35%** of a module's methods"))

        with it("should write the most statements into keep-operations-small-focused"):
            expect(_rule_text("code", "keep-operations-small-focused")).to(contain("20 statements or fewer"))

        with it("should write the most nested levels into simplify-control-flow"):
            expect(_rule_text("code", "simplify-control-flow")).to(contain("Do not nest more than 3 levels"))

        with it("should write the most parameters into limit-operation-parameters"):
            expect(_rule_text("model", "limit-operation-parameters")).to(contain("Prefer 0-3 parameters"))

        with it("should write each measured limit's shipped value into its rule"):
            texts = [_rule_text("code", slug) for slug in _MEASURED_LIMIT_RULES]
            said = ("to 10 paths", "at 15 or lower", "to 50 lines", "at 100 or lower", "to 30 methods")
            expect([words in text for words, text in zip(said, texts)]).to(equal([True] * 5))

        with it("should say above the measured limits that the project's config may set another"):
            expect(CleanEngineering(fidelity="code").fidelities.current.section_text("rules")).to(contain("a project sets its own"))

        with it("should leave no marker unfilled in the rules of any fidelity"):
            fidelities = [CleanEngineering(fidelity=fidelity).fidelities.current for fidelity in ("modules", "model", "code")]
            expect([rule.slug for fidelity in fidelities for rule in fidelity.every_rule if "{{" in rule.body]).to(equal([]))

    with context("that is changed in code, in that one place"):
        with before.all:
            self.six_statements = practice_from_source(_SIX_STATEMENTS)
            self.nested_twice = practice_from_source(_NESTED_TWICE)

        with before.each:
            self.changes = [
                mock.patch.object(rule_numbers, "MOST_STATEMENTS", 5),
                mock.patch.object(rule_numbers, "MOST_NESTED_LEVELS", 1),
                mock.patch.object(rule_numbers, "MOST_SEAM_SHARE", 0.5),
                mock.patch.dict(code_measures.SHIPPED_LIMITS, {CODE_LINES.name: 40, PARAMETERS_TAKEN.name: 4}),
            ]
            for change in self.changes:
                change.start()

        with after.each:
            for change in self.changes:
                change.stop()

        with it("should change the statements the check allows"):
            expect(_hits("keep-operations-small-focused", self.six_statements)).to(equal(["Operation 'total' is 6 statements (max 5)."]))

        with it("should change the nested levels the check allows"):
            expect(_hits("simplify-control-flow", self.nested_twice)).to(equal(["Operation 'first' nests control flow 2 levels deep (max 1)."]))

        with it("should change the parameters the check allows"):
            expect(_hits("limit-operation-parameters", practice_from_source(_FOUR_PARAMETERS))).to(equal([]))

        with it("should change the share of a module's methods the deep-module check allows"):
            expect(BY_SLUG["deep-module"].allowed_seam(10)).to(equal(5))

        with it("should change the limit a project that sets none of its own is held to"):
            expect(ChosenTools({}).limit(CODE_LINES)).to(equal(40))

        with it("should change each rule's text"):
            texts = (
                _rule_text("code", "keep-operations-small-focused"), _rule_text("code", "simplify-control-flow"),
                _rule_text("model", "limit-operation-parameters"), _rule_text("modules", "deep-module"), _rule_text("code", "limit-function-lines"),
            )
            said = ("5 statements or fewer", "more than 1 levels", "Prefer 0-4 parameters", "**50%**", "to 40 lines")
            expect([words in text for words, text in zip(said, texts)]).to(equal([True] * 5))

    with context("that is left as shipped"):
        with before.all:
            self.four_parameters = practice_from_source(_FOUR_PARAMETERS)
            self.three_parameters = practice_from_source(_THREE_PARAMETERS)

        with it("should report an operation over the most parameters"):
            expect(_hits("limit-operation-parameters", self.four_parameters)).to(equal(["Operation 'add' takes 4 parameters (maximum 3, excluding self)."]))

        with it("should pass an operation at the most parameters"):
            expect(_hits("limit-operation-parameters", self.three_parameters)).to(equal([]))
