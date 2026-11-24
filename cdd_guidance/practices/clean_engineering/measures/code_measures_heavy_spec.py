"""The code measures taken with the real tools, lizard and radon, on real files: each limit rule against its failing
and its repaired example, code in each language, and a validate in a session whose project chose the tools.

Heavy: every example runs the outside measuring tool, which needs the ``measures`` dependency group installed
(``pip install -e ".[measures]"``). The rules one object decides, with the tool stood in for, are in
code_measures_spec.py."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect  # noqa: E402
from mamba import after, before, context, description, it  # noqa: E402

import cdd_guidance.actions  # noqa: E402, F401 - registers the actions with the action catalogue
import cdd_guidance.practices  # noqa: E402, F401 - registers the practices with the practice catalogue
from cdd_guidance.actions.validate.validate import Validate  # noqa: E402
from cdd_guidance.actions.validate.validate_examples import working_in  # noqa: E402
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG  # noqa: E402
from cdd_guidance.practices.clean_engineering.rules.rule_examples import (  # noqa: E402
    MEASURES_CHOSEN,
    example_asset_paths,
    measured,
    measured_example_pair,
    measured_module_example_pair,
    practice_from_files,
)
from space.session.spec_support.throwaway_project import ThrowawayProject  # noqa: E402

_PATHS = "limit-paths-through-a-function"
# The same eleven branches as the Python example, written in each brace language.
_BRANCHES = "".join(f'    if (kind === "{name}") return {index};\n' for index, name in enumerate("abcdefghijk", start=1))
_TYPESCRIPT = f"export class Catalogue {{\n  priceOf(kind: string): number {{\n{_BRANCHES}    return 0;\n  }}\n}}\n"
_JAVASCRIPT = f"export class Catalogue {{\n  priceOf(kind) {{\n{_BRANCHES}    return 0;\n  }}\n}}\n"
_SIX_PARAMETERS = (
    'class Parcel:\n    """A parcel on its way to a customer."""\n\n'
    "    def send(self, street: str, town: str, postcode: str, country: str, carrier: str, insured: bool) -> str:\n"
    '        return f"{street} {town} {postcode} {country} {carrier} {insured}"\n'
)


def _measures_of(fixture, kind: str, name: str, measures: list[str]) -> dict:
    node = next(found for found in fixture.practice.reading.in_graph.nodes(kind) if found.name == name)
    return {measure: node.get_fact(measure) for measure in measures if node.has_fact(measure)}


def _validated(chosen: bool) -> str:
    """The report of a validate at the code fidelity of a file with a six-parameter function, in a project that chose
    the measuring tools, or one that chose none."""
    throwaway = ThrowawayProject()
    folder = Path(tempfile.mkdtemp(prefix="cdd-code-measures-"))
    written = {"src/parcels/parcel.py": _SIX_PARAMETERS, **({".context/config.json": json.dumps({"code_measures": {}})} if chosen else {})}
    for relative, text in written.items():
        (folder / relative).parent.mkdir(parents=True, exist_ok=True)
        (folder / relative).write_text(text, encoding="utf-8")
    try:
        return Validate(session=working_in(throwaway, folder, folder)).validate(guidance=["clean-engineering-code"], paths=["src/parcels/parcel.py"])
    finally:
        throwaway.close()
        shutil.rmtree(folder, ignore_errors=True)


with description("the code measures the real tools take") as self:
    with context("of a rule's failing example and its repaired example"):
        with it("should report a function with more paths through it than the limit, and pass the repaired one"):
            measured_example_pair(_PATHS).check()

        with it("should report a function whose readability score is over the limit, and pass the repaired one"):
            measured_example_pair("keep-functions-readable").check()

        with it("should report a function with more lines of code than the limit, and pass the repaired one"):
            measured_example_pair("limit-function-lines").check()

        with it("should report a class whose total complexity is over the limit, and pass the repaired one"):
            measured_example_pair("limit-class-complexity").check()

        with it("should report a class with more methods than the limit, and pass the repaired one"):
            measured_example_pair("limit-class-methods").check()

        with it("should report a class with a group of methods sharing no data with the rest, and pass the repaired one"):
            measured_example_pair("keep-class-methods-sharing-data").check()

        with it("should report a class that depends on more classes than the limit, and pass the repaired one"):
            measured_example_pair("limit-class-coupling").check()

        with it("should report a class one call into which sets off more methods than the limit, and pass the repaired one"):
            measured_example_pair("limit-class-response").check()

        with it("should report a module whose longest file has more lines of code than its project's limit, and pass the repaired one"):
            measured_module_example_pair("limit-module-file-lines").check()

        with it("should report a module with a file whose maintainability index is under the limit, and pass the repaired one"):
            measured_module_example_pair("keep-module-files-maintainable").check()

        with it("should report a module whose classes' average total complexity is over the limit, and pass the repaired one"):
            measured_module_example_pair("limit-average-class-complexity").check()

        with it("should report a module more modules import than its project's limit, and pass the repaired one"):
            measured_module_example_pair("limit-modules-importing").check()

        with it("should report a module that repeats a block of code from another module's file, and pass the repaired one"):
            measured_module_example_pair("limit-copied-code-blocks").check()

    with context("of Python code"):
        with before.all:
            source = example_asset_paths(_PATHS)[0].read_text(encoding="utf-8")
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "catalogue/catalogue.py": source}))

        with it("should keep a function's paths and readability score, as lizard counts them, on its node"):
            kept = _measures_of(self.fixture, "Operation", "price_of", ["paths_through", "readability_score"])
            expect(kept).to(equal({"paths_through": 12, "readability_score": 11}))

        with it("should keep a class's total complexity, the paths through its methods added up, on its node"):
            expect(_measures_of(self.fixture, "OoadClass", "Catalogue", ["total_complexity"])).to(equal({"total_complexity": 12}))

    with context("of TypeScript code"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "catalogue/catalogue.ts": _TYPESCRIPT}))

        with it("should keep the paths through a function, as lizard counts them"):
            expect(_measures_of(self.fixture, "Operation", "priceOf", ["paths_through"])).to(equal({"paths_through": 12}))

        with it("should report the function past the limit"):
            expect(self.fixture.hits(BY_SLUG[_PATHS])).to(contain(contain("Function 'priceOf' has 12 paths through it (cyclomatic complexity), over the limit of 10.")))

        with it("should keep the class's total complexity, the paths through its methods added up"):
            expect(_measures_of(self.fixture, "OoadClass", "Catalogue", ["total_complexity"])).to(equal({"total_complexity": 12}))

    with context("of JavaScript code"):
        with before.all:
            self.fixture = measured(practice_from_files({**MEASURES_CHOSEN, "catalogue/catalogue.js": _JAVASCRIPT}))

        with it("should keep the paths through a function, as lizard counts them"):
            expect(_measures_of(self.fixture, "Operation", "priceOf", ["paths_through"])).to(equal({"paths_through": 12}))

        with it("should report the function past the limit"):
            expect(self.fixture.hits(BY_SLUG[_PATHS])).to(contain(contain("Function 'priceOf' has 12 paths through it (cyclomatic complexity), over the limit of 10.")))

    with context("by a validate at the code fidelity, in a session"):
        with before.all:
            self.report = _validated(chosen=True)

        with it("should report the function past its limit in the validation report, beside the other rules"):
            expect(self.report).to(contain("limit-operation-parameters", "takes 6 parameters (maximum 3, excluding self)"))

        with it("should name the file the function is in"):
            expect(self.report).to(contain("[src/parcels/parcel.py]("))
