"""The ways a project reaches code other than by a call or an import, as its ``.context/config.json`` names them under
``code_reach``: the operations and classes each way reaches, which every rule that asks whether code is used reads. A
project that names none reaches code only by calls and imports. Each project is read once, through the real
working-copy build, for the examples that look at it."""

import json

from expects import equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.source_code.code_reach import CodeReach
from harness.graph.rule_fixture import RuleFixture

# The project's ways of reaching code, one of each kind, as its config names them.
_WAYS = {
    "publishing_decorators": ["agent_tool", "agent_toolset"],
    "registries": ["CATALOGUE.register"],
    "scanned_bases": ["GraphOverlay"],
    "entry_points": ["*.py:main"],
    "naming_conventions": ["^on_"],
    "generated_adapters": ["adapters/*.py"],
}
# Code reached each way, beside a helper of each class that nothing reaches.
_SHOP = """
from tools import agent_tool, agent_toolset


@agent_toolset
class Shop:
    @agent_tool
    def open_shop(self):
        return "open"

    def on_close(self):
        return "closed"

    def tidy(self):
        return 0


def main():
    return Shop().open_shop()
"""
_PRACTICES = """
class Practice:
    def instructions(self):
        ...


class Bookshop(Practice):
    def instructions(self):
        return "sell books"

    def price(self):
        return 1


class Leftover:
    def unused(self):
        return 0


CATALOGUE.register(Bookshop)
"""
_OVERLAYS = """
class GraphOverlay:
    def read(self, graph):
        ...


class OrdersOverlay(GraphOverlay):
    def read(self, graph):
        return graph

    def tally(self):
        return 0
"""
_ADAPTER = """
class OrdersClient:
    def orders(self):
        return []
"""
_FILES = {"shop.py": _SHOP, "practices.py": _PRACTICES, "overlays.py": _OVERLAYS, "adapters/orders_client.py": _ADAPTER}


def _reached(files: dict[str, str]) -> tuple[list[str], list[str]]:
    """The names of the operations and the classes the project's ways reach, read from files."""
    fixture = RuleFixture(CleanEngineering, files)
    reading = fixture.practice.reading
    reach = CodeReach.from_graph(reading.graph)
    operations = reach.operations(reading.in_graph.nodes("Operation"))
    classes = reach.classes(reading.in_graph.nodes("OoadClass"))
    return sorted(node.name for node in operations), sorted(node.name for node in classes)


with description("the ways a project reaches code") as self:
    with context("that its config names"):
        with before.all:
            self.operations, self.classes = _reached({**_FILES, ".context/config.json": json.dumps({"code_reach": _WAYS})})

        with it("should reach the operation each way names, and none of the helpers beside them"):
            expect(self.operations).to(equal(["instructions", "main", "on_close", "open_shop", "orders", "read"]))

        with it("should reach the class each way names, and not the class nothing reaches"):
            expect(self.classes).to(equal(["Bookshop", "OrdersClient", "OrdersOverlay", "Shop"]))

    with context("that its config does not name"):
        with before.all:
            self.operations, self.classes = _reached(_FILES)

        with it("should reach no operation, since the project reaches code only by calls and imports"):
            expect(self.operations).to(equal([]))

        with it("should reach no class"):
            expect(self.classes).to(equal([]))
