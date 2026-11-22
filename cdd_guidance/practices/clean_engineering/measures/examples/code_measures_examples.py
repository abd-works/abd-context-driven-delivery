"""The examples the three stories of code measures share: the shop project, whose `shop/cart.py` holds the class Cart
with the function total, the outside measuring tools stood in for, and the reads that keep the measures on the nodes.

Scenarios: story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/

The outside tool, lizard, is stood in for here, at the one place the practice asks a tool, so each scenario runs in
milliseconds; `measures/code_measures_heavy_spec.py` runs the same behaviour with the real lizard.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from cdd_guidance.practices.clean_engineering.measures.code_measures import (
    MEASURES,
    ChosenTools,
    PATHS_THROUGH,
    READABILITY_SCORE,
    TOTAL_COMPLEXITY,
)
from cdd_guidance.practices.clean_engineering.measures.measuring_tools import MeasuringTool
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.rule_examples import MEASURES_CHOSEN, example_asset_paths, practice_from_files
from harness.graph.rule_fixture import RuleFixture, RulePair

# Seed: the shop project's cart file, and the file a validate names.
CART_FILE = "shop/cart.py"
# The shop module's card: a folder is a module, measured as one, only when it owns `.context/module-context.md`.
SHOP_CARD = {"shop/.context/module-context.md": "# shop\n*Cart* is what a customer fills.\n\n- **Seam (terms):** Cart\n\n## Constraint\n\nUse Cart only.\n"}
CART = '''class Cart:
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
# Seed: Cart with one more method, label, which uses no field of the cart.
CART_WITH_A_HELPER = CART + "\n    def label(self, sku: str) -> str:\n        return sku.upper()\n"
# Seed: the parcels project's function send, which takes six parameters.
PARCEL_FILE = "src/parcels/parcel.py"
SIX_PARAMETERS = "class Parcel:\n    def send(self, street: str, town: str, postcode: str, country: str, carrier: str, insured: bool) -> str:\n        return street\n"
# Seed: the Catalogue class's priceOf with eleven branches, in each language a tool is chosen for, by file extension.
_BRACE_BRANCHES = "".join(f'    if (kind === "{name}") return {index};\n' for index, name in enumerate("abcdefghijk", start=1))
_PYTHON_BRANCHES = "".join(f'        if kind == "{name}":\n            return {index}\n' for index, name in enumerate("abcdefghijk", start=1))
CATALOGUE = {
    "py": f"class Catalogue:\n    def priceOf(self, kind: str) -> int:\n{_PYTHON_BRANCHES}        return 0\n",
    "ts": f"export class Catalogue {{\n  priceOf(kind: string): number {{\n{_BRACE_BRANCHES}    return 0;\n  }}\n}}\n",
    "js": f"export class Catalogue {{\n  priceOf(kind) {{\n{_BRACE_BRANCHES}    return 0;\n  }}\n}}\n",
}
# Seed: a config whose code measures section sets one limit, or chooses one tool, of its own.
PATHS_LIMIT_OF_20 = {".context/config.json": '{"code_measures": {"limits": {"paths_through": 20}}}'}
NO_MEASURES_CHOSEN: dict[str, str] = {}


class StandInLizard(MeasuringTool):
    """Lizard, stood in for: every function has 14 paths and a readability score of 3, and every class a total
    complexity of 40."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {PATHS_THROUGH.name: lambda measured: 14, READABILITY_SCORE.name: lambda measured: 3, TOTAL_COMPLEXITY.name: lambda measured: 40}


class CountingLizard(MeasuringTool):
    """Lizard, stood in for where a scenario says how it counts: one path, and one more for each `if` in the function's
    own lines."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {PATHS_THROUGH.name: self._paths, READABILITY_SCORE.name: lambda measured: 0, TOTAL_COMPLEXITY.name: self._paths}

    def _paths(self, measured) -> int:
        first, last = measured.lines
        written = measured.file.read_text(encoding="utf-8").splitlines()[first - 1 : last]
        return 1 + sum(line.strip().startswith("if ") for line in written)


class LizardNotInstalled(MeasuringTool):
    """Lizard as it is on a machine that never installed it."""

    name = "lizard"

    def value(self, measure, measured):
        return self._imported("a_measuring_tool_nobody_installed", measure)


class MeasuresNothing(MeasuringTool):
    """An outside tool that finds nothing to measure, so only the practice's own reader answers."""

    def value(self, measure, measured):
        return None


STAND_INS = {"lizard": StandInLizard}
READER_ALONE = {"lizard": MeasuresNothing}


def shop_project(config: dict[str, str] = MEASURES_CHOSEN, files: dict[str, str] | None = None, tools: dict | None = None) -> RuleFixture:
    """Seed: the shop project, read into the graph as a load of its whole working copy reads it: its config, and its
    cart file unless files says what it holds. The outside tools are stood in for by tools, else by the stand-ins that
    answer the same for every function, class and file."""
    project = practice_from_files({**config, **(files if files is not None else {CART_FILE: CART})})
    project.practice.reading.measuring_tools.update(tools or STAND_INS)
    return project


def code_files(project: RuleFixture) -> list[Path]:
    """Seed: the project's code files, as a read that names them names them."""
    return [path for path in sorted(project.root.rglob("*")) if path.is_file() and path.suffix in (".py", ".ts", ".js")]


def checked_graph_file() -> Path:
    """Seed: where the refresh a validate asks for saves the graph it checked."""
    return Path(tempfile.mkdtemp(prefix="cdd-checked-")) / "checked.json"


def node_of(project: RuleFixture, kind: str, name: str):
    return next(found for found in project.practice.reading.in_graph.nodes(kind) if found.name == name)


def kept_on(project: RuleFixture, kind: str, name: str, measures: list[str]) -> dict:
    """The facts of those names the node holds."""
    node = node_of(project, kind, name)
    return {measure: node.get_fact(measure) for measure in measures if node.has_fact(measure)}


def any_measure_kept(project: RuleFixture) -> bool:
    """Whether any node holds a code measure a tool supplies."""
    supplied = [measure.name for measure in MEASURES if ChosenTools({}).supplied_by_a_tool(measure)]
    return any(node.has_fact(name) for node in project.practice.reading.in_graph.nodes() for name in supplied)


def holding(project: RuleFixture, kind: str, name: str, fact: str, value) -> RuleFixture:
    """project whose node holds fact with value, as a read that measured it leaves it."""
    setattr(node_of(project, kind, name), fact, value)
    return project


def reports_of(project: RuleFixture, rule: str) -> list[str]:
    """What the graph rule reports once the graph rules run."""
    return project.hits(BY_SLUG[rule])


def metrics_under(project: RuleFixture, kind: str, name: str) -> list[str]:
    """The entries of the metrics group the explorer tree shows under the node; none when it has no such group."""
    graph = project.practice.reading.graph
    graph.practices.rebuild_trees()
    node = node_of(project, kind, name)
    groups = [child for child in graph.explorer_branch(node.node_id).children if getattr(child, "name", "") == "metrics"]
    return [leaf.name for group in groups for leaf in graph.explorer_branch(group.node_id).children]


def example_pair(rule: str, tools: dict) -> RulePair:
    """Seed: the rule's failing example and its repaired example, each in a project that chose the shipped tools."""
    faulty_path, repaired_path = example_asset_paths(rule)
    faulty, repaired = (shop_project(files={"example/example.py": path.read_text(encoding="utf-8")}, tools=tools) for path in (faulty_path, repaired_path))
    return RulePair(BY_SLUG[rule], faulty, repaired)
