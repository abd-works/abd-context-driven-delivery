"""BDD specs for the folds the catalog's code viewer opens an example with."""
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.catalog_generator.source_folds import SourceFolds

_EXAMPLES = Path(__file__).resolve().parents[2] / "cdd_guidance" / "practices"


def _line_of(source: str, fragment: str) -> int:
    return next(number for number, line in enumerate(source.splitlines(), start=1) if fragment in line)


with description("an acceptance test example's folds"):
    with context("with a multi-line step"):
        with it("should fold the step's callback body"):
            expect(SourceFolds("when('go', () => {\n  doIt();\n});\n").steps).to(equal([(1, 3)]))

    with context("with a step on one line"):
        with it("should leave it open"):
            expect(SourceFolds("when('go', () => { doIt(); });\n").steps).to(equal([]))

    with context("with And and But steps"):
        with it("should fold their bodies as steps"):
            source = "then('a', () => {\n  one();\n})\n  .and('b', () => {\n    two();\n  });\n"
            expect(SourceFolds(source).steps).to(equal([(1, 3), (4, 6)]))

    with context("with a template string holding an expression"):
        with it("should not read the expression's braces as the body's"):
            source = "when('go', () => {\n  say(`${name}}`);\n});\n"
            expect(SourceFolds(source).steps).to(equal([(1, 3)]))

    with context("that is the Stories acceptance test example"):
        with before.all:
            self.source = (_EXAMPLES / "stories" / "catalog-examples" / "acceptance_tests.ts").read_text(encoding="utf-8")

        with it("should fold each of its steps"):
            expect(SourceFolds(self.source).steps).to(equal([(5, 7), (8, 10), (11, 16), (17, 19)]))

        with it("should also fold the scaffolding above its story"):
            expect((3, 4) in SourceFolds(self.source).acceptance_test).to(equal(True))

        with it("should fold five ranges in all"):
            expect(len(SourceFolds(self.source).acceptance_test)).to(equal(5))


with description("a DDD tactics example's folds"):
    with before.all:
        self.source = (_EXAMPLES / "ddd" / "catalog-examples" / "tactics.ts").read_text(encoding="utf-8")
        self.starts = {start for start, _end in SourceFolds(self.source).for_example}

    with it("should keep a named aggregate root open"):
        expect(_line_of(self.source, "export class Customer") in self.starts).to(equal(False))

    with it("should fold the root's operations"):
        expect(_line_of(self.source, "confirmIdentity()") in self.starts).to(equal(True))

    with it("should fold another class to its declaration"):
        expect(_line_of(self.source, "export class Identity") in self.starts).to(equal(True))

    with it("should fold a const object to its declaration"):
        expect(_line_of(self.source, "export const CustomerOperation") in self.starts).to(equal(True))

    with it("should fold an interface to its declaration"):
        expect(_line_of(self.source, "export interface AccountCredentialsErrors") in self.starts).to(equal(True))
