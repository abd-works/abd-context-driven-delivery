"""The Clean Engineering graph rules judge production code as it is written: specs, fixtures, and examples are not the
project's code, a value is not a collaborator, and a factory is not a misplaced static."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_above, be_false, be_true, equal, expect, have_len
from mamba import context, description, it

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.model.production_code import ProductionCodeRule, is_spec_file, is_test_code
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)
from cdd_guidance.practices.clean_engineering.rules import RULES
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


# One class that breaks most of the code rules at once: a long operation full of control flow, vague and short
# parameters, an unnamed number, a static helper, a collaborator built in the constructor, and a narrating comment.
_BREAKS_EVERY_RULE = """
class Probe:
    def __init__(self):
        self.repository = Repository()

    @staticmethod
    def check(a, b, data, options, x, y):
        # loop over the items
        total = 0
        for item in data:
            if item:
                for part in item:
                    if part:
                        while part:
                            total += 7919
                            part = None
        try:
            open(a).read()
        except Exception:
            pass
        if not b:
            raise ValueError("empty")
        return total + 1
""" + "".join(f"\n    def op{index}(self):\n        return {index}\n" for index in range(12))

_TEST_FILES = (
    "orders/order_spec.py",
    "orders/order.spec.ts",
    "orders/model/class_channel.feature.py",
    "orders/move-ticket.story.shared.py",
    "orders/story_test.py",
    "orders/session_board_examples.py",
    "orders/session_board_tiers.py",
    "orders/spec_helpers.py",
    "orders/rule_fixture.py",
    "app/test-utils/fixture-repo.ts",
    "tools/ide_toast/watch_notice_spec.js",
    "src/OrderTest.java",
)
_PRODUCTION_FILES = (
    "orders/order.py",
    "bdd/rules/spec_rules.py",
    "bdd/model/spec_source.py",
    "stories/rules/acceptance_tests.py",
    "design_canvas/fixture_bar.py",
    "contest/contest.py",
)


with description("test code"):
    with context("named by the conventions specs and their support follow"):
        with it("should read every one as test code"):
            expect([file for file in _TEST_FILES if not is_test_code(file)]).to(equal([]))

        with it("should read production files whose names only contain a test word as production code"):
            expect([file for file in _PRODUCTION_FILES if is_test_code(file)]).to(equal([]))

        with it("should read a Python feature spec as a spec"):
            expect(is_spec_file("class_channel.feature.py")).to(be_true)

        with it("should not read a story test's shared examples as a spec"):
            expect(is_spec_file("session_board_examples.py")).to(be_false)


with description("the Clean Engineering graph rules"):
    with context("in a graph load, where the schema says which rules each node carries"):
        with it("should carry every rule on each node type the rule judges, so its hits are kept"):
            schema = practice_from_files({"orders/order.py": "class Order:\n    pass\n"}).practice.in_graph.schema.applicable
            missing = sorted(
                f"{rule.slug} on {node_type}" for rule in RULES for node_type in rule.node_types if node_type not in schema.get(rule.slug, [])
            )
            expect(missing).to(equal([]))

        with it("should keep an eliminate-duplication hit on the operation that copies another"):
            source = _SUBTOTAL.format(name="Totals", field="price") + "\n" + _SUBTOTAL.format(name="Backup", field="cost")
            fixture = practice_from_files({"orders/totals.py": source})
            failed = [node.name for node in fixture.context.nodes("Operation") if "eliminate-duplication" in node.rules.failed_slugs]
            expect(failed).to(equal(["subtotal"]))

    with context("every rule that judges one node at a time"):
        with it("should judge production code only, except source-parses, which reports any file that does not parse"):
            own_check = [rule.slug for rule in RULES if type(rule).check not in (PracticeGraphRule.check, ProductionCodeRule.check)]
            expect(own_check).to(equal(["source-parses"]))

    with context("on code that breaks every rule"):
        with it("should find hits in a production file"):
            fixture = practice_from_files({"orders/probe.py": _BREAKS_EVERY_RULE})
            expect(sum(len(fixture.hits(rule)) for rule in RULES)).to(be_above(5))

        with it("should find none in a spec, a feature spec, or a story test's support"):
            for name in ("probe_spec.py", "probe.feature.py", "probe_examples.py", "probe_tiers.py", "probe_test.py"):
                fixture = practice_from_files({f"orders/{name}": _BREAKS_EVERY_RULE})
                expect({rule.slug: fixture.hits(rule) for rule in RULES if fixture.hits(rule)}).to(equal({}))

    with context("on a spec file"):
        with it("should not judge its catch-everything as use-exceptions-properly"):
            expect(_hits("use-exceptions-properly", _CATCHES_EVERYTHING, "probe_spec.py")).to(equal([]))

        with it("should not judge its catch-everything as never-swallow-exceptions"):
            expect(_hits("never-swallow-exceptions", _CATCHES_EVERYTHING, "probe_spec.py")).to(equal([]))

        with it("should not judge its raise on an empty value as errors-out-of-existence"):
            expect(_hits("errors-out-of-existence", _RAISES_ON_EMPTY, "graph_spec.py")).to(equal([]))

        with it("should still judge a raise of a builtin failure on an empty value in a production file"):
            expect(_hits("errors-out-of-existence", _RAISES_ON_EMPTY, "graph.py")).to(have_len(1))

        with it("should accept a raise of a named failure that carries the key nothing has"):
            source = (
                "class Graph:\n    def practice(self, key):\n        practice = self.held.get(key)\n"
                "        if practice is None:\n            raise UnknownPractice(key, tuple(self.held))\n        return practice\n"
            )
            expect(_hits("errors-out-of-existence", source, "graph.py")).to(equal([]))

        with it("should still judge the same code in a production file"):
            expect(_hits("use-exceptions-properly", _CATCHES_EVERYTHING, "probe.py")).to(have_len(1))

    with context("reading a working copy"):
        with it("should skip the _examples and fixtures folders"):
            expect([skips_folder("_examples"), skips_folder("fixtures")]).to(equal([True, True]))

        with it("should skip the catalog-examples and templates folders"):
            expect([skips_folder("catalog-examples"), skips_folder("templates")]).to(equal([True, True]))

        with it("should read no class from a template or a catalog example"):
            tree = {
                "stories/catalog-examples/tactics.py": "class Sample:\n    pass\n",
                "bdd/templates/bdd.py": "from {domain_module} import {cls}\n",
                "bdd/bdd.py": "class Bdd:\n    pass\n",
            }
            fixture = practice_from_files(tree)
            expect(sorted(node.name for node in fixture.context.nodes("OoadClass"))).to(equal(["Bdd"]))

    with context("one-way-deps"):
        with it("should not count an import under if TYPE_CHECKING as a dependency"):
            tree = _module(
                "repo",
                {
                    "repo.py": "from repo.worktree import Worktree\n\n\nclass Repo:\n    def open(self) -> Worktree:\n        return Worktree(self)\n",
                    "worktree.py": (
                        "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from repo.repo import Repo\n\n\n"
                        "class Worktree:\n    def __init__(self, repo: 'Repo') -> None:\n        self.repo = repo\n"
                    ),
                },
            )
            expect(practice_from_files(tree).hits(ce_rule_by_slug("one-way-deps"))).to(equal([]))

        with it("should still count an import in the else branch of if TYPE_CHECKING"):
            tree = _module(
                "repo",
                {
                    "repo.py": "from repo.worktree import Worktree\n\n\nclass Repo:\n    pass\n",
                    "worktree.py": (
                        "import typing\n\nif typing.TYPE_CHECKING:\n    pass\nelse:\n    from repo.repo import Repo\n\n\n"
                        "class Worktree:\n    pass\n"
                    ),
                },
            )
            expect(practice_from_files(tree).hits(ce_rule_by_slug("one-way-deps"))).to(have_len(2))

    with context("use-explicit-dependencies"):
        with it("should accept a failure the constructor raises"):
            source = "class Stopped(Exception):\n    pass\n\n\nclass Call:\n    def __init__(self, tool):\n        if not tool:\n            raise Stopped()\n        self.tool = tool\n"
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should accept a failure it keeps, built from a class that derives from Exception"):
            source = "class Stopped(Exception):\n    pass\n\n\nclass Call:\n    def __init__(self):\n        self.failure = Stopped()\n"
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should accept the default it builds for a parameter a caller may pass"):
            source = (
                "class Repo:\n    def run(self) -> int:\n        return 1\n\n\n"
                "class Board:\n    def __init__(self, repo=None, log=None):\n"
                "        self.repo = repo if repo is not None else Repo()\n        self.log = log or Repo()\n"
            )
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should accept a part it builds from itself"):
            source = "class Children:\n    def add(self, child) -> None:\n        pass\n\n\nclass Node:\n    def __init__(self):\n        self.children = Children(self, 'children')\n"
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should accept a part it builds from its parameters and constants"):
            source = "class Layout:\n    def folder(self) -> str:\n        return ''\n\n\nclass Install:\n    def __init__(self, ide, root):\n        self.layout = Layout(ide)\n        self.claude = Layout('Claude')\n        self.source = Layout(root / NAME)\n"
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should accept an empty collection it fills"):
            source = "class CallGraph(list):\n    def entries(self) -> list:\n        return list(self)\n\n\nclass Step:\n    def __init__(self):\n        self.calls = CallGraph()\n"
            expect(_hits("use-explicit-dependencies", source)).to(equal([]))

        with it("should still flag a collaborator built from something outside the object"):
            source = "from pathlib import Path\n\n\nclass Sessions:\n    def open(self) -> None:\n        pass\n\n\nclass Board:\n    def __init__(self):\n        self.sessions = Sessions(Path.cwd())\n"
            expect(_hits("use-explicit-dependencies", source)).to(have_len(1))

        with it("should accept a TypeScript failure thrown, a default, and a part built from this"):
            source = (
                "export class Board {\n  constructor(repo?: Repo) {\n    if (!repo) { throw new BoardError('no repo'); }\n"
                "    this.repo = repo ?? new Repo();\n    this.children = new Children(this);\n  }\n}\n"
            )
            expect(_hits("use-explicit-dependencies", source, "board.ts")).to(equal([]))

        with it("should still flag a TypeScript collaborator built from nothing"):
            source = "export class Board {\n  constructor() {\n    this.repo = new Repo();\n  }\n}\n"
            expect(_hits("use-explicit-dependencies", source, "board.ts")).to(have_len(1))

    with context("use-explicit-dependencies on its values"):
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

        with it("should accept now and every, which make values of their class"):
            source = (
                "class LogTimestamp:\n    @classmethod\n    def now(cls) -> 'LogTimestamp':\n        return cls()\n\n"
                "    @classmethod\n    def every(cls) -> list['LogTimestamp']:\n        return [cls()]\n"
            )
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

        with it("should accept a folder whose other classes sit in packages of its own"):
            tree = _module("bdd", {"bdd.py": "class Bdd:\n    pass\n"})
            tree["bdd/model/nodes.py"] = "class Spec:\n    pass\n\n\nclass Observation:\n    pass\n"
            tree["bdd/rules/tree_rules.py"] = "class TreeRule:\n    pass\n"
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
