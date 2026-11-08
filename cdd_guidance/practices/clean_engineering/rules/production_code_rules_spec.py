"""The Clean Engineering graph rules judge production code as it is written: specs, fixtures, and examples are not the
project's code, a value is not a collaborator, and a factory is not a misplaced static."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_false, be_true, equal, expect, have_len
from mamba import context, description, it

from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)
from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    assert_files_rule_pair,
    assert_module_example_pair,
    assert_python_example_pair,
    ce_rule_by_slug,
    practice_from_files,
    practice_from_source,
)


def _hits(slug: str, source: str, filename: str = "example.py") -> list[str]:
    return practice_from_source(source, filename=filename).hits(ce_rule_by_slug(slug))


def _module(folder: str, files: dict[str, str]) -> dict[str, str]:
    tree = {f"{folder}/.context/module-context.md": "# module\n"}
    tree.update({f"{folder}/{name}": text for name, text in files.items()})
    return tree


_CATCHES_EVERYTHING = """
class Probe:
    def run(self, call):
        try:
            return call()
        except Exception:
            return None
"""

_RAISES_ON_EMPTY = """
class Fixture:
    def tree_named(self, name):
        if not name:
            raise ValueError("no name")
        return name
"""

_SUBTOTAL = """
class {name}:
    def subtotal(self, items):
        total = 0
        for item in items:
            if item.counted:
                total += item.{field}
        discount = total // 10
        return total - discount
"""


with description("the Clean Engineering graph rules"):
    with context("on a spec file"):
        with it("should not judge its catch-everything as use-exceptions-properly"):
            expect(_hits("use-exceptions-properly", _CATCHES_EVERYTHING, "probe_spec.py")).to(equal([]))

        with it("should not judge its catch-everything as never-swallow-exceptions"):
            expect(_hits("never-swallow-exceptions", _CATCHES_EVERYTHING, "probe_spec.py")).to(equal([]))

        with it("should not judge its raise on an empty value as errors-out-of-existence"):
            expect(_hits("errors-out-of-existence", _RAISES_ON_EMPTY, "graph_spec.py")).to(equal([]))

        with it("should still judge the same code in a production file"):
            expect(_hits("use-exceptions-properly", _CATCHES_EVERYTHING, "probe.py")).to(have_len(1))

    with context("reading a working copy"):
        with it("should skip the _examples and fixtures folders"):
            expect([skips_folder("_examples"), skips_folder("fixtures")]).to(equal([True, True]))

    with context("use-explicit-dependencies"):
        with it("should accept a constructor that builds a Path"):
            source = "from pathlib import Path\n\n\nclass Store:\n    def __init__(self, root):\n        self.file = Path(root) / 'store.json'\n"
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should accept a constructor that builds a value object of the graph"):
            source = (
                "# <<Value Object>>\nclass Money:\n    def __init__(self, cents: int) -> None:\n        self.cents = cents\n\n\n"
                "class Price:\n    def __init__(self, cents: int) -> None:\n        self.money = Money(cents)\n"
            )
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should still flag a constructor that builds a collaborator"):
            source = "class CartRepository:\n    pass\n\n\nclass Cart:\n    def __init__(self):\n        self._repository = CartRepository()\n"
            expect(_hits("use-explicit-dependencies", source)).to(have_len(1))

    with context("prefer-instance-operations"):
        with it("should accept a classmethod that returns its own class"):
            source = "class ProjectApproach:\n    @classmethod\n    def for_project(cls, root: str) -> 'ProjectApproach':\n        return cls()\n"
            expect(_hits("prefer-instance-operations", source)).to(equal([]))

        with it("should accept a snake_case load_ factory"):
            source = "class Utility:\n    @classmethod\n    def load_all(cls, folder: str):\n        return [cls()]\n"
            expect(_hits("prefer-instance-operations", source)).to(equal([]))

        with it("should accept a static factory that returns a list of its class"):
            source = "class Practice:\n    @staticmethod\n    def every(folder: str) -> list['Practice']:\n        return []\n"
            expect(_hits("prefer-instance-operations", source)).to(equal([]))

        with it("should still flag a staticmethod that returns another type"):
            source = "class Vocabulary:\n    @staticmethod\n    def is_noun(word: str) -> bool:\n        return bool(word)\n"
            expect(_hits("prefer-instance-operations", source)).to(have_len(1))

    with context("use-intention-revealing-names"):
        with it("should allow value in a Python property setter"):
            source = (
                "class Account:\n    @property\n    def email(self) -> str:\n        return self._email\n\n"
                "    @email.setter\n    def email(self, value: str) -> None:\n        self._email = value\n"
            )
            expect(_hits("use-intention-revealing-names", source)).to(equal([]))

        with it("should flag a generic parameter name and accept a named one"):
            assert_python_example_pair("use-intention-revealing-names")

    with context("eliminate-duplication"):
        with it("should flag a near copy whose one line differs"):
            source = _SUBTOTAL.format(name="Totals", field="price") + "\n" + _SUBTOTAL.format(name="Backup", field="cost")
            expect(_hits("eliminate-duplication", source)).to(have_len(1))

        with it("should accept two operations whose long docstrings hold a one-line body"):
            doc = '        """{text}\n\n        One.\n        Two.\n        Three.\n        Four.\n        """\n        return ""\n'
            source = "class Commands:\n    def push(self) -> str:\n" + doc.format(text="Push.") + "\n    def switch(self) -> str:\n" + doc.format(text="Switch.")
            expect(_hits("eliminate-duplication", source)).to(equal([]))

        with it("should accept two operations of different shape"):
            other = "\nclass Names:\n    def joined(self, people):\n        names = []\n        for person in people:\n            names.append(person.name.title())\n        names.sort()\n        return ', '.join(names)\n"
            expect(_hits("eliminate-duplication", _SUBTOTAL.format(name="Totals", field="price") + other)).to(equal([]))

    with context("no-module-per-class"):
        with it("should not count a spec's class as the module's public class"):
            tree = _module("orders", {"order.py": "class Order:\n    pass\n\n\nclass OrderLine:\n    pass\n"})
            tree["orders/order_spec.py"] = "class OrderSpecFixture:\n    pass\n"
            expect(practice_from_files(tree).hits(ce_rule_by_slug("no-module-per-class"))).to(equal([]))

        with it("should accept a folder that holds only the base its nested modules share"):
            tree = _module("builders", {"builder.py": "class Builder:\n    pass\n"})
            tree.update(_module("builders/toolset", {"toolset.py": "class ToolsetBuilder:\n    pass\n\n\nclass Step:\n    pass\n"}))
            tree.update(_module("builders/practice", {"practice.py": "class PracticeBuilder:\n    pass\n\n\nclass Part:\n    pass\n"}))
            expect(practice_from_files(tree).hits(ce_rule_by_slug("no-module-per-class"))).to(equal([]))

    with context("public-seam-only"):
        with it("should flag internal design in a docstring and accept a public one"):
            assert_module_example_pair("public-seam-only")

        with it("should not read the marker it looks for in a string the code holds"):
            tree = _module("rules", {"rules.py": 'MARKER = "## Internal"\n\n\nclass Scanner:\n    def found(self, text: str) -> bool:\n        return MARKER in text\n'})
            expect(practice_from_files(tree).hits(ce_rule_by_slug("public-seam-only"))).to(equal([]))

    with context("one-way-deps"):
        with it("should flag two files of one folder that import each other and accept a one-way import"):
            assert_module_example_pair("one-way-deps")

    with context("deep-module"):
        with it("should flag a module most of whose classes another module imports and accept one public class"):
            assert_module_example_pair("deep-module")


with description("the TypeScript class model"):
    with context("reading a class whose comment says 'class names'"):
        with it("should read only the class the code declares"):
            source = "// Each adapter names its own tools, so this class names none.\nexport class CddConnection {\n  start(): void {}\n}\n"
            model = TypeScriptCleanEngineeringModel().parse(source)
            expect([oclass.name for oclass in model.file_module().classes]).to(equal(["CddConnection"]))

        with it("should read each operation once"):
            source = "// so this class names none.\nexport class CddConnection {\n  start(): void {}\n}\n"
            model = TypeScriptCleanEngineeringModel().parse(source)
            operations = [operation.name for oclass in model.file_module().classes for operation in oclass.operations]
            expect(operations).to(equal(["start"]))

    with context("reading a class name inside a string"):
        with it("should not read it as a class"):
            source = "const note = 'a class Ghost lives here'\nexport class Real {\n}\n"
            model = TypeScriptCleanEngineeringModel().parse(source)
            expect([oclass.name for oclass in model.file_module().classes]).to(equal(["Real"]))
