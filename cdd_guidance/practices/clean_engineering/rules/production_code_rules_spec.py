"""The Clean Engineering graph rules judge production code as it is written: specs, fixtures, and examples are not the
project's code, a value is not a collaborator, and a factory is not a misplaced static."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_above, be_false, be_true, equal, expect, have_len
from mamba import before, context, description, it

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.model.production_code import is_spec_file, is_test_code
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)
from cdd_guidance.practices.clean_engineering.rules import RULES
from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    ce_rule_by_slug,
    module_example_pair,
    practice_from_files,
    practice_from_source,
    python_example_pair,
    rule_pair,
)


def _fixture(source: str, filename: str = "example.py"):
    return practice_from_source(source, filename=filename)


def _hits(slug: str, fixture) -> list[str]:
    return fixture.hits(ce_rule_by_slug(slug))


def _every_rule_hits(fixture) -> dict[str, list[str]]:
    """Each rule's hits in the fixture, by the rule's slug."""
    return {rule.slug: fixture.hits(rule) for rule in RULES}


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


# Each fixture builds a graph, so every context builds its fixtures once, before its examples, which only run the rules.
with description("the Clean Engineering graph rules"):
    with context("in a graph load, where the schema says which rules each node carries"):
        with before.all:
            source = _SUBTOTAL.format(name="Totals", field="price") + "\n" + _SUBTOTAL.format(name="Backup", field="cost")
            self.fixture = practice_from_files({"orders/totals.py": source})

        with it("should keep an eliminate-duplication hit on the operation that copies another"):
            failed = [node.name for node in self.fixture.context.nodes("Operation") if "eliminate-duplication" in node.rules.failed_slugs]
            expect(failed).to(equal(["subtotal"]))

    with context("every rule that judges one node at a time"):
        with it("should judge production code only, except source-parses, which reports any file that does not parse"):
            own_check = [rule.slug for rule in RULES if type(rule).check not in (PracticeGraphRule.check, ProductionCodeRule.check)]
            expect(own_check).to(equal(["source-parses"]))

    with context("on code that breaks every rule"):
        # Each rule's hits are read once per file: reading them runs every rule over the file again.
        with before.all:
            self.production = _every_rule_hits(practice_from_files({"orders/probe.py": _BREAKS_EVERY_RULE}))
            self.test_support = [
                _every_rule_hits(practice_from_files({f"orders/{name}": _BREAKS_EVERY_RULE}))
                for name in ("probe_spec.py", "probe.feature.py", "probe_examples.py", "probe_tiers.py", "probe_test.py")
            ]

        with it("should find hits in a production file"):
            expect(sum(len(hits) for hits in self.production.values())).to(be_above(5))

        with it("should find none in a spec, a feature spec, or a story test's support"):
            for found in self.test_support:
                expect({slug: hits for slug, hits in found.items() if hits}).to(equal({}))

    with context("on a spec file"):
        with before.all:
            self.catching_spec = _fixture(_CATCHES_EVERYTHING, "probe_spec.py")
            self.raising_spec = _fixture(_RAISES_ON_EMPTY, "graph_spec.py")
            self.raising_production = _fixture(_RAISES_ON_EMPTY, "graph.py")
            self.named_with_key = _fixture(
                "class Graph:\n    def practice(self, key):\n        practice = self.held.get(key)\n"
                "        if practice is None:\n            raise UnknownPractice(key, tuple(self.held))\n        return practice\n",
                "graph.py",
            )
            self.named_no_arguments = _fixture(
                "class Repo:\n    def commit(self, paths):\n        if not paths:\n"
                "            raise CommitPathsRequiredError()\n        return self.git.commit(paths)\n",
                "repo.py",
            )
            self.named_with_message = _fixture(
                "class Repo:\n    def commit(self, paths):\n        if not paths:\n"
                "            raise CommitPathsRequiredError('paths missing')\n        return self.git.commit(paths)\n",
                "repo.py",
            )
            self.builtin_with_message = _fixture(
                "class Repo:\n    def commit(self, paths):\n        if not paths:\n"
                "            raise ValueError('paths missing')\n        return self.git.commit(paths)\n",
                "repo.py",
            )
            self.catching_production = _fixture(_CATCHES_EVERYTHING, "probe.py")

        with it("should not judge its catch-everything as use-exceptions-properly"):
            expect(_hits("use-exceptions-properly", self.catching_spec)).to(equal([]))

        with it("should not judge its catch-everything as never-swallow-exceptions"):
            expect(_hits("never-swallow-exceptions", self.catching_spec)).to(equal([]))

        with it("should not judge its raise on an empty value as errors-out-of-existence"):
            expect(_hits("errors-out-of-existence", self.raising_spec)).to(equal([]))

        with it("should still judge a raise of a builtin failure on an empty value in a production file"):
            expect(_hits("errors-out-of-existence", self.raising_production)).to(have_len(1))

        with it("should accept a raise of a named failure that carries the key nothing has"):
            expect(_hits("errors-out-of-existence", self.named_with_key)).to(equal([]))

        with it("should accept a raise of a named failure the program declares, with no arguments"):
            expect(_hits("errors-out-of-existence", self.named_no_arguments)).to(equal([]))

        with it("should accept a named failure whose message says what is missing"):
            expect(_hits("errors-out-of-existence", self.named_with_message)).to(equal([]))

        with it("should still judge a builtin failure whose message says what is missing"):
            expect(_hits("errors-out-of-existence", self.builtin_with_message)).to(have_len(1))

        with it("should still judge the same code in a production file"):
            expect(_hits("use-exceptions-properly", self.catching_production)).to(have_len(1))

    with context("reading a working copy"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "stories/catalog-examples/tactics.py": "class Sample:\n    pass\n",
                    "bdd/templates/bdd.py": "from {domain_module} import {cls}\n",
                    "bdd/bdd.py": "class Bdd:\n    pass\n",
                }
            )

        with it("should skip the _examples and fixtures folders"):
            expect([skips_folder("_examples"), skips_folder("fixtures")]).to(equal([True, True]))

        with it("should skip the catalog-examples and templates folders"):
            expect([skips_folder("catalog-examples"), skips_folder("templates")]).to(equal([True, True]))

        with it("should read no class from a template or a catalog example"):
            expect(sorted(node.name for node in self.fixture.context.nodes("OoadClass"))).to(equal(["Bdd"]))

    with context("one-way-deps"):
        with before.all:
            self.type_checking = practice_from_files(
                _module(
                    "repo",
                    {
                        "repo.py": "from repo.worktree import Worktree\n\n\nclass Repo:\n    def open(self) -> Worktree:\n        return Worktree(self)\n",
                        "worktree.py": (
                            "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from repo.repo import Repo\n\n\n"
                            "class Worktree:\n    def __init__(self, repo: 'Repo') -> None:\n        self.repo = repo\n"
                        ),
                    },
                )
            )
            self.else_branch = practice_from_files(
                _module(
                    "repo",
                    {
                        "repo.py": "from repo.worktree import Worktree\n\n\nclass Repo:\n    pass\n",
                        "worktree.py": (
                            "import typing\n\nif typing.TYPE_CHECKING:\n    pass\nelse:\n    from repo.repo import Repo\n\n\n"
                            "class Worktree:\n    pass\n"
                        ),
                    },
                )
            )
            board_page = "import { BoardStore } from './board-store';\n\nexport class BoardPage {\n  store = new BoardStore();\n}\n"
            self.import_type = practice_from_files(
                _module(
                    "board",
                    {
                        "board-page.ts": board_page,
                        "board-store.ts": "import type { BoardPage } from './board-page';\n\nexport class BoardStore {\n  page?: BoardPage;\n}\n",
                    },
                )
            )
            self.every_name_type = practice_from_files(
                _module(
                    "board",
                    {
                        "board-page.ts": board_page,
                        "board-store.ts": "import { type BoardPage, type PageId } from './board-page';\n\nexport class BoardStore {\n  page?: BoardPage;\n}\n",
                    },
                )
            )
            self.value_beside_type = practice_from_files(
                _module(
                    "board",
                    {
                        "board-page.ts": board_page,
                        "board-store.ts": "import { type PageId, BoardPage } from './board-page';\n\nexport class BoardStore {\n  page = new BoardPage();\n}\n",
                    },
                )
            )
            self.example_pair = module_example_pair("one-way-deps")

        with it("should not count an import under if TYPE_CHECKING as a dependency"):
            expect(_hits("one-way-deps", self.type_checking)).to(equal([]))

        with it("should still count an import in the else branch of if TYPE_CHECKING"):
            expect(_hits("one-way-deps", self.else_branch)).to(have_len(2))

        with it("should not count a TypeScript import type as a dependency"):
            expect(_hits("one-way-deps", self.import_type)).to(equal([]))

        with it("should not count a TypeScript import whose every name is marked type"):
            expect(_hits("one-way-deps", self.every_name_type)).to(equal([]))

        with it("should still count a TypeScript import that takes a value beside a type"):
            expect(_hits("one-way-deps", self.value_beside_type)).to(have_len(2))

        with it("should flag two files of one folder that import each other and accept a one-way import"):
            self.example_pair.check()

    with context("use-explicit-dependencies"):
        with before.all:
            self.raised = _fixture(
                "class Stopped(Exception):\n    pass\n\n\nclass Call:\n    def __init__(self, tool):\n        if not tool:\n            raise Stopped()\n        self.tool = tool\n"
            )
            self.kept_failure = _fixture(
                "class Stopped(Exception):\n    pass\n\n\nclass Call:\n    def __init__(self):\n        self.failure = Stopped()\n"
            )
            self.default = _fixture(
                "class Repo:\n    def run(self) -> int:\n        return 1\n\n\n"
                "class Board:\n    def __init__(self, repo=None, log=None):\n"
                "        self.repo = repo if repo is not None else Repo()\n        self.log = log or Repo()\n"
            )
            self.own_part = _fixture(
                "class Children:\n    def add(self, child) -> None:\n        pass\n\n\nclass Node:\n    def __init__(self):\n        self.children = Children(self, 'children')\n"
            )
            self.parameter_part = _fixture(
                "class Layout:\n    def folder(self) -> str:\n        return ''\n\n\nclass Install:\n    def __init__(self, ide, root):\n        self.layout = Layout(ide)\n        self.claude = Layout('Claude')\n        self.source = Layout(root / NAME)\n"
            )
            self.empty_collection = _fixture(
                "class CallGraph(list):\n    def entries(self) -> list:\n        return list(self)\n\n\nclass Step:\n    def __init__(self):\n        self.calls = CallGraph()\n"
            )
            self.outside = _fixture(
                "from pathlib import Path\n\n\nclass Sessions:\n    def open(self) -> None:\n        pass\n\n\nclass Board:\n    def __init__(self):\n        self.sessions = Sessions(Path.cwd())\n"
            )
            self.typescript_accepted = _fixture(
                "export class Board {\n  constructor(repo?: Repo) {\n    if (!repo) { throw new BoardError('no repo'); }\n"
                "    this.repo = repo ?? new Repo();\n    this.children = new Children(this);\n  }\n}\n",
                "board.ts",
            )
            self.typescript_from_nothing = _fixture(
                "export class Board {\n  constructor() {\n    this.repo = new Repo();\n  }\n}\n", "board.ts"
            )

        with it("should accept a failure the constructor raises"):
            expect(_hits("use-explicit-dependencies", self.raised)).to(equal([]))

        with it("should accept a failure it keeps, built from a class that derives from Exception"):
            expect(_hits("use-explicit-dependencies", self.kept_failure)).to(equal([]))

        with it("should accept the default it builds for a parameter a caller may pass"):
            expect(_hits("use-explicit-dependencies", self.default)).to(equal([]))

        with it("should accept a part it builds from itself"):
            expect(_hits("use-explicit-dependencies", self.own_part)).to(equal([]))

        with it("should accept a part it builds from its parameters and constants"):
            expect(_hits("use-explicit-dependencies", self.parameter_part)).to(equal([]))

        with it("should accept an empty collection it fills"):
            expect(_hits("use-explicit-dependencies", self.empty_collection)).to(equal([]))

        with it("should still flag a collaborator built from something outside the object"):
            expect(_hits("use-explicit-dependencies", self.outside)).to(have_len(1))

        with it("should accept a TypeScript failure thrown, a default, and a part built from this"):
            expect(_hits("use-explicit-dependencies", self.typescript_accepted)).to(equal([]))

        with it("should still flag a TypeScript collaborator built from nothing"):
            expect(_hits("use-explicit-dependencies", self.typescript_from_nothing)).to(have_len(1))

    with context("hide-inner-details"):
        with before.all:
            self.own_private = _fixture("class Cart:\n    def total(self) -> int:\n        return sum(self._lines) + len(type(self).__name__)\n")
            self.other_private = _fixture("class Cart:\n    def total(self, order) -> int:\n        return sum(order._lines)\n")
            self.off_a_local = _fixture("class Cart:\n    def total(self) -> int:\n        order = self.orders.last()\n        return sum(order._lines)\n")
            self.classmethod_own = _fixture("class Catalogue:\n    @classmethod\n    def keys(cls) -> tuple:\n        return tuple(cls._registered())\n")
            self.dunder = _fixture("class Catalogue:\n    def fields(self, other) -> dict:\n        return dict(other.__dict__)\n")
            self.copied_field = _fixture("class Plan:\n    def copy_from(self, other: 'Plan') -> None:\n        self._tier = other._tier\n")
            self.class_field = _fixture(
                "class Catalogue:\n    _runner = None\n\n    @staticmethod\n    def run_with(runner) -> None:\n        Catalogue._runner = runner\n"
            )
            self.own_class_parameter = _fixture("class Plan:\n    def outranks(self, other: 'Plan') -> bool:\n        return self.rank > other._rank\n")
            self.comparison = _fixture("class Paths:\n    def __eq__(self, other) -> bool:\n        return self.keys == other._keys\n")
            self.made_instance = _fixture(
                "class Card:\n    @classmethod\n    def read(cls, text: str) -> 'Card':\n        card = cls()\n        card._fill(text)\n        return card\n"
            )
            self.built_instance = _fixture(
                "class Map:\n    def copy_of(self) -> 'Map':\n        copy = Map()\n        copy._place(self.screens)\n        return copy\n"
            )
            self.own_children = _fixture(
                "class Epic:\n    epics: list['Epic']\n\n    def stamp(self) -> None:\n        for child in self.epics:\n            child._stamp()\n"
            )
            self.other_class_parameter = _fixture("class Cart:\n    def total(self, order: 'Order') -> int:\n        return sum(order._lines)\n")
            self.typescript_own_parameter = _fixture(
                "export class Money {\n  equals(other: Money): boolean {\n    return this.cents === other._cents;\n  }\n}\n", "money.ts"
            )
            self.typescript_built = _fixture(
                "export class Money {\n  doubled(): Money {\n    const copy = new Money();\n    copy._cents = 2;\n    return copy;\n  }\n}\n",
                "money.ts",
            )
            self.typescript_other_parameter = _fixture(
                "export class Money {\n  add(order: Order): number {\n    return order._cents;\n  }\n}\n", "money.ts"
            )
            self.reaching = _every_rule_hits(practice_from_source("class Cart:\n    def total(self, order) -> int:\n        return sum(order._lines)\n"))
            self.asking = _every_rule_hits(practice_from_source("class Cart:\n    def total(self, order) -> int:\n        return sum(order.lines)\n"))

        with it("should accept an operation that reads its own private fields"):
            expect(_hits("hide-inner-details", self.own_private)).to(equal([]))

        with it("should flag an operation that reads another object's private field"):
            expect(_hits("hide-inner-details", self.other_private)).to(have_len(1))

        with it("should flag a private field read off a local as well as off a parameter"):
            expect(_hits("hide-inner-details", self.off_a_local)).to(have_len(1))

        with it("should accept a classmethod that reads its own class's private members"):
            expect(_hits("hide-inner-details", self.classmethod_own)).to(equal([]))

        with it("should accept reading a dunder of another object"):
            expect(_hits("hide-inner-details", self.dunder)).to(equal([]))

        with it("should accept copying a parameter's private field into the same field of this object"):
            expect(_hits("hide-inner-details", self.copied_field)).to(equal([]))

        with it("should accept a class reaching its own private class field by its name"):
            expect(_hits("hide-inner-details", self.class_field)).to(equal([]))

        with it("should accept a parameter typed as its own class"):
            expect(_hits("hide-inner-details", self.own_class_parameter)).to(equal([]))

        with it("should accept the other operand of a comparison dunder"):
            expect(_hits("hide-inner-details", self.comparison)).to(equal([]))

        with it("should accept an instance its classmethod has just made"):
            expect(_hits("hide-inner-details", self.made_instance)).to(equal([]))

        with it("should accept an instance of its own class it builds"):
            expect(_hits("hide-inner-details", self.built_instance)).to(equal([]))

        with it("should accept a loop over children it declares of its own class"):
            expect(_hits("hide-inner-details", self.own_children)).to(equal([]))

        with it("should still flag a parameter typed as another class"):
            expect(_hits("hide-inner-details", self.other_class_parameter)).to(have_len(1))

        with it("should accept a TypeScript parameter typed as its own class"):
            expect(_hits("hide-inner-details", self.typescript_own_parameter)).to(equal([]))

        with it("should accept a TypeScript instance of its own class it builds"):
            expect(_hits("hide-inner-details", self.typescript_built)).to(equal([]))

        with it("should still flag a TypeScript parameter typed as another class"):
            expect(_hits("hide-inner-details", self.typescript_other_parameter)).to(have_len(1))

        with it("should be the one rule that reports the reach"):
            expect([rule.slug for rule in RULES if self.reaching[rule.slug] != self.asking[rule.slug]]).to(equal(["hide-inner-details"]))

    with context("use-explicit-dependencies on its values"):
        with before.all:
            self.path = _fixture("from pathlib import Path\n\n\nclass Store:\n    def __init__(self, root):\n        self.file = Path(root) / 'store.json'\n")
            self.value_object = _fixture(
                "# <<Value Object>>\nclass Money:\n    def __init__(self, cents: int) -> None:\n        self.cents = cents\n\n\n"
                "class Price:\n    def __init__(self, cents: int) -> None:\n        self.money = Money(cents)\n"
            )
            self.collaborator = _fixture(
                "class CartRepository:\n    pass\n\n\nclass Cart:\n    def __init__(self):\n        self._repository = CartRepository()\n"
            )

        with it("should accept a constructor that builds a Path"):
            expect(_hits("use-explicit-dependencies", self.path)).to(equal([]))

        with it("should accept a constructor that builds a value object of the graph"):
            expect(_hits("use-explicit-dependencies", self.value_object)).to(equal([]))

        with it("should still flag a constructor that builds a collaborator"):
            expect(_hits("use-explicit-dependencies", self.collaborator)).to(have_len(1))

    with context("prefer-instance-operations"):
        with before.all:
            self.own_class = _fixture(
                "class ProjectApproach:\n    @classmethod\n    def for_project(cls, root: str) -> 'ProjectApproach':\n        return cls()\n"
            )
            self.load_factory = _fixture("class Utility:\n    @classmethod\n    def load_all(cls, folder: str):\n        return [cls()]\n")
            self.list_factory = _fixture("class Practice:\n    @staticmethod\n    def every(folder: str) -> list['Practice']:\n        return []\n")
            self.now_and_every = _fixture(
                "class LogTimestamp:\n    @classmethod\n    def now(cls) -> 'LogTimestamp':\n        return cls()\n\n"
                "    @classmethod\n    def every(cls) -> list['LogTimestamp']:\n        return [cls()]\n"
            )
            self.other_type = _fixture("class Vocabulary:\n    @staticmethod\n    def is_noun(word: str) -> bool:\n        return bool(word)\n")

        with it("should accept a classmethod that returns its own class"):
            expect(_hits("prefer-instance-operations", self.own_class)).to(equal([]))

        with it("should accept a snake_case load_ factory"):
            expect(_hits("prefer-instance-operations", self.load_factory)).to(equal([]))

        with it("should accept a static factory that returns a list of its class"):
            expect(_hits("prefer-instance-operations", self.list_factory)).to(equal([]))

        with it("should accept now and every, which make values of their class"):
            expect(_hits("prefer-instance-operations", self.now_and_every)).to(equal([]))

        with it("should still flag a staticmethod that returns another type"):
            expect(_hits("prefer-instance-operations", self.other_type)).to(have_len(1))

    with context("use-intention-revealing-names"):
        with before.all:
            self.setter = _fixture(
                "class Account:\n    @property\n    def email(self) -> str:\n        return self._email\n\n"
                "    @email.setter\n    def email(self, value: str) -> None:\n        self._email = value\n"
            )
            self.example_pair = python_example_pair("use-intention-revealing-names")

        with it("should allow value in a Python property setter"):
            expect(_hits("use-intention-revealing-names", self.setter)).to(equal([]))

        with it("should flag a generic parameter name and accept a named one"):
            self.example_pair.check()

    with context("eliminate-duplication"):
        with before.all:
            self.near_copy = _fixture(_SUBTOTAL.format(name="Totals", field="price") + "\n" + _SUBTOTAL.format(name="Backup", field="cost"))
            doc = '        """{text}\n\n        One.\n        Two.\n        Three.\n        Four.\n        """\n        return ""\n'
            self.docstrings = _fixture(
                "class Commands:\n    def push(self) -> str:\n" + doc.format(text="Push.") + "\n    def switch(self) -> str:\n" + doc.format(text="Switch.")
            )
            self.one_expression = _fixture(
                "class FrontMatter:\n    def of_file(self, path) -> str:\n"
                "        return path.read_text(encoding='utf-8') if path.is_file() and path.suffix == '.md' else ''\n\n\n"
                "class Schema:\n    def loaded(self, path) -> str:\n"
                "        return path.read_text(encoding='utf-8') if path.is_file() and path.suffix == '.md' else ''\n"
            )
            three = (
                "class Daemon:\n    def pin_from(self, checkout) -> str:\n        self.home.install(checkout, CONNECT_SCRIPT)\n"
                "        self.home.pin(checkout)\n        return self._status(self.restart())\n\n"
                "    def serve_checkout(self, checkout) -> str:\n        self.home.install(checkout, CONNECT_SCRIPT)\n"
                "        self.home.serve_from(checkout)\n        return self._status(self.restart())\n"
            )
            four = three.replace("        self.home.pin(checkout)\n", "        self.home.pin(checkout)\n        self.home.forget(checkout)\n").replace(
                "        self.home.serve_from(checkout)\n", "        self.home.serve_from(checkout)\n        self.home.forget(checkout)\n"
            )
            self.four_statements, self.three_statements = _fixture(four), _fixture(three)
            configured = "(Pattern):\n    def __init__(self) -> None:\n        super().__init__(\n            format='typescript',\n            default_workspace_folder='harness',\n        )\n"
            copied = "(Pattern):\n    def __init__(self, folder) -> None:\n        super().__init__(\n            format='typescript',\n            default_workspace_folder=folder,\n        )\n"
            self.configured_pair = rule_pair(
                "eliminate-duplication",
                "class WebAccess" + copied + "\n\nclass ClaudeMod" + copied,
                "class WebAccess" + configured + "\n\nclass ClaudeMod" + configured,
            )
            other = "\nclass Names:\n    def joined(self, people):\n        names = []\n        for person in people:\n            names.append(person.name.title())\n        names.sort()\n        return ', '.join(names)\n"
            self.different_shape = _fixture(_SUBTOTAL.format(name="Totals", field="price") + other)

        with it("should flag a near copy whose one line differs"):
            expect(_hits("eliminate-duplication", self.near_copy)).to(have_len(1))

        with it("should accept two operations whose long docstrings hold a one-line body"):
            expect(_hits("eliminate-duplication", self.docstrings)).to(equal([]))

        with it("should accept two one-expression bodies that read alike"):
            expect(_hits("eliminate-duplication", self.one_expression)).to(equal([]))

        with it("should flag a four-statement near copy and accept two three-statement bodies that differ in their one job"):
            expect([len(_hits("eliminate-duplication", self.four_statements)), len(_hits("eliminate-duplication", self.three_statements))]).to(
                equal([1, 0])
            )

        with it("should flag a copied body and accept two classes that each configure their base with literal values"):
            self.configured_pair.check()

        with it("should accept two operations of different shape"):
            expect(_hits("eliminate-duplication", self.different_shape)).to(equal([]))

    with context("no-module-per-class"):
        with before.all:
            tree = _module("orders", {"order.py": "class Order:\n    pass\n\n\nclass OrderLine:\n    pass\n"})
            tree["orders/order_spec.py"] = "class OrderSpecFixture:\n    pass\n"
            self.spec_class = practice_from_files(tree)
            tree = _module("bdd", {"bdd.py": "class Bdd:\n    pass\n"})
            tree["bdd/model/nodes.py"] = "class Spec:\n    pass\n\n\nclass Observation:\n    pass\n"
            tree["bdd/rules/tree_rules.py"] = "class TreeRule:\n    pass\n"
            self.nested_packages = practice_from_files(tree)
            tree = _module("builders", {"builder.py": "class Builder:\n    pass\n"})
            tree.update(_module("builders/toolset", {"toolset.py": "class ToolsetBuilder:\n    pass\n\n\nclass Step:\n    pass\n"}))
            tree.update(_module("builders/practice", {"practice.py": "class PracticeBuilder:\n    pass\n\n\nclass Part:\n    pass\n"}))
            self.shared_base = practice_from_files(tree)

        with it("should not count a spec's class as the module's public class"):
            expect(_hits("no-module-per-class", self.spec_class)).to(equal([]))

        with it("should accept a folder whose other classes sit in packages of its own"):
            expect(_hits("no-module-per-class", self.nested_packages)).to(equal([]))

        with it("should accept a folder that holds only the base its nested modules share"):
            expect(_hits("no-module-per-class", self.shared_base)).to(equal([]))

    with context("public-seam-only"):
        with before.all:
            self.example_pair = module_example_pair("public-seam-only")
            self.marker_in_string = practice_from_files(
                _module("rules", {"rules.py": 'MARKER = "## Internal"\n\n\nclass Scanner:\n    def found(self, text: str) -> bool:\n        return MARKER in text\n'})
            )

        with it("should flag internal design in a docstring and accept a public one"):
            self.example_pair.check()

        with it("should not read the marker it looks for in a string the code holds"):
            expect(_hits("public-seam-only", self.marker_in_string)).to(equal([]))

    with context("deep-module"):
        with before.all:
            self.example_pair = module_example_pair("deep-module")

        with it("should flag a module most of whose classes another module imports and accept one public class"):
            self.example_pair.check()



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
