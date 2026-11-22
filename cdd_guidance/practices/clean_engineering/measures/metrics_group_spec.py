"""The metrics group the explorer tree shows under a function, a class and a module: the facts a limit rule reads for
that node type, each with its plain-English name, its value and its limit. The outside tools are stood in for."""
from expects import be_false, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.measures.code_measures import MAINTAINABILITY_SCORE, PATHS_THROUGH, READABILITY_SCORE, TOTAL_COMPLEXITY
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


class StandInLizard(MeasuringTool):
    """Lizard, stood in for: every function has 14 paths and a readability score of 3, every class a total of 40."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {PATHS_THROUGH.name: lambda measured: 14, READABILITY_SCORE.name: lambda measured: 3, TOTAL_COMPLEXITY.name: lambda measured: 40}


class StandInRadon(MeasuringTool):
    name = "radon"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {MAINTAINABILITY_SCORE.name: lambda measured: 62.5}


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
            self.fixture, self.graph = _tree_of({**MEASURES_CHOSEN, "shop/cart.py": _CART})

        with it("should list, under a function, each fact a limit rule reads, with its plain name, its value and its limit"):
            expect(_group_under(self.graph, _node(self.fixture, "Operation", "total"))).to(equal([
                "paths through a function (cyclomatic complexity): 14, limit 10, past the limit",
                "readability score of a function (cognitive complexity; higher is harder to read): 3, limit 15",
                "lines in a function: 2, limit 50",
                "parameters a function takes: 1, limit 5",
            ]))

        with it("should list, under a class, its total complexity, its methods and its groups of methods sharing no data"):
            expect(_group_under(self.graph, _node(self.fixture, "OoadClass", "Cart"))).to(equal([
                "total complexity of a class (the paths through all its methods, added up): 40, limit 100",
                "methods in a class: 4, limit 30",
                "groups of methods in a class that share no data with one another (lack of cohesion): 2, limit 1, past the limit",
            ]))

        with it("should list, under a module, its import loops"):
            expect(_group_under(self.graph, _node(self.fixture, "Package", "shop"))).to(equal(["loops of modules importing one another that a module is part of: 0, limit 0"]))

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
