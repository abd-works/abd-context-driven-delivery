"""The metrics group the explorer tree shows under a function, a class and a module: the facts a limit rule reads for
that node type, each with its plain-English name, its value and its limit. The outside tool, lizard, is stood in for."""
from expects import be_false, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.measures.code_measures import LEAST_MAINTAINABILITY, LONGEST_FILE_LINES, PATHS_THROUGH, READABILITY_SCORE, TOTAL_COMPLEXITY
from cdd_guidance.practices.clean_engineering.measures.measuring_tools import MeasuringTool
from cdd_guidance.practices.clean_engineering.rules.rule_examples import MEASURES_CHOSEN, measured, practice_from_files
from harness.graph.node_filter import Filter, FilterChoices

_CART = '''class Cart:
    """A customer's cart."""

    def __init__(self, lines: list[int], owner: str) -> None:
        self._lines = lines
        self._owner = owner

    def total(self, discount: int) -> int:
        return sum(self._lines) - discount

    def is_empty(self) -> bool:
        return not self._lines

    def greeting(self) -> str:
        return f"Hello {self._owner}"
'''


# shop is a module, a folder that owns a module card; shop/pricing is a package inside it.
_SHOP_CARD = {"shop/.context/module-context.md": "# shop\n*Cart* is what a customer fills.\n\n- **Seam (terms):** Cart\n\n## Constraint\n\nUse Cart only.\n"}
_PRICE = "class Price:\n    def of(self, cents: int) -> int:\n        return cents\n"


class StandInLizard(MeasuringTool):
    """Lizard, stood in for: every function has 14 paths and a readability score of 3, every class a total of 40, and
    every module's longest file 120 lines of code."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {
            PATHS_THROUGH.name: lambda measured: 14,
            READABILITY_SCORE.name: lambda measured: 3,
            TOTAL_COMPLEXITY.name: lambda measured: 40,
            LONGEST_FILE_LINES.name: lambda measured: 120,
        }


class StandInRadon(MeasuringTool):
    """Radon, stood in for: every module's least maintainable file has a maintainability index of 12."""

    name = "radon"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {LEAST_MAINTAINABILITY.name: lambda measured: 12}


def _tree_of(files: dict[str, str]):
    """The graph of files once their measures are kept and the explorer tree is built again, as a refresh leaves it."""
    fixture = measured(practice_from_files(files), {"lizard": StandInLizard, "radon": StandInRadon})
    graph = fixture.practice.reading.graph
    graph.practices.rebuild_trees()
    return fixture, graph


def _node(fixture, kind: str, name: str):
    return next(found for found in fixture.practice.reading.in_graph.nodes(kind) if found.name == name)


def _group_under(graph, node) -> list[str]:
    """The names of the entries in node's metrics group; none when node has no such group."""
    groups = [child for child in graph.explorer_branch(node.node_id).children if getattr(child, "name", "") == "metrics"]
    return [leaf.name for group in groups for leaf in graph.explorer_branch(group.node_id).children]


with description("the metrics group of a node in the explorer tree") as self:
    with context("in a project that holds its code to limits"):
        with before.all:
            self.fixture, self.graph = _tree_of({**MEASURES_CHOSEN, **_SHOP_CARD, "shop/cart.py": _CART, "shop/pricing/price.py": _PRICE})

        with it("should list, under a function, each fact a limit rule reads, with its plain name, its value and its limit"):
            expect(_group_under(self.graph, _node(self.fixture, "Operation", "total"))).to(equal([
                "paths through a function (cyclomatic complexity): 14, limit 10, past the limit",
                "readability score of a function (cognitive complexity; higher is harder to read): 3, limit 15",
                "lines in a function: 2, limit 50",
                "parameters a function takes: 1, limit 3",
            ]))

        with it("should list, under a class, its total complexity, its methods, its coupling, the methods one call into it can set off, and its groups of methods sharing no data"):
            expect(_group_under(self.graph, _node(self.fixture, "OoadClass", "Cart"))).to(equal([
                "total complexity of a class (the paths through all its methods, added up): 40, limit 100",
                "methods in a class: 4, limit 30",
                "classes a class depends on (coupling between objects): 0, limit 14",
                "methods one call into a class can set off (response for a class): 4, limit 50",
                "groups of methods in a class that share no data with one another (lack of cohesion): 2, limit 1, past the limit",
            ]))

        with it("should list, under a module, its import loops, the modules it imports with no limit, then the modules that import it, its longest file, its least maintainable file, its average class complexity and its copied blocks, each with its limit"):
            expect(_group_under(self.graph, _node(self.fixture, "Module", "shop"))).to(equal([
                "loops of modules importing one another that a module is part of: 0, limit 0",
                "modules a module imports (outgoing coupling): 0",
                "modules that import a module (incoming coupling): 0, limit 40",
                "lines of code in a module's longest file: 120, limit 800",
                "maintainability index of a module's least maintainable file (0 to 100; higher is easier to change): 12, limit 20 or higher, past the limit",
                "average total complexity of a module's classes: 40, limit 15, past the limit",
                "blocks of code a module repeats from another file: 0, limit 0",
            ]))

        with it("should mark no metric that has no limit as past it"):
            unlimited = [metric for metric in self.fixture.practice.reading.metrics_of(_node(self.fixture, "Module", "shop")) if metric.limit is None]
            expect([metric.is_past_limit for metric in unlimited]).to(equal([False]))

        with it("should give a package, which is part of its module, no group"):
            expect(_group_under(self.graph, _node(self.fixture, "Package", "pricing"))).to(equal([]))

        with it("should give a node with no such fact no group"):
            expect(_group_under(self.graph, _node(self.fixture, "Parameter", "discount"))).to(equal([]))

        with it("should offer the group in the filter, where the relationship kinds are offered"):
            expect(FilterChoices(self.graph, ["clean_engineering"], ["Operation"]).relationships).to(contain("metrics"))

        with it("should keep a node that has metrics when the filter chooses the group"):
            expect(Filter(self.graph, {"relationships": ["metrics"]}).matches(_node(self.fixture, "Operation", "total"))).to(be_true)

        with it("should leave out a node that has none when the filter chooses the group"):
            expect(Filter(self.graph, {"relationships": ["metrics"]}).matches(_node(self.fixture, "Parameter", "discount"))).to(be_false)

    with context("in a project whose config has no code measures section"):
        with before.all:
            self.fixture, self.graph = _tree_of({"shop/cart.py": _CART})

        with it("should give no node a group, since the project holds its code to no limit"):
            expect(_group_under(self.graph, _node(self.fixture, "Operation", "total"))).to(equal([]))

        with it("should not offer the group in the filter"):
            expect(FilterChoices(self.graph, ["clean_engineering"], ["Operation"]).relationships).not_to(contain("metrics"))
