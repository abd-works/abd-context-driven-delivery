"""The limits on Clean Engineering's code measures: each rule reads one measure off a node and reports the node when
the measure is past the limit the project keeps for it.

A function's lines and parameters and a class's methods are facts the reader keeps on every read. The measures a
tool supplies are facts the reader keeps of the files a read names, as the refresh a validate asks for does
(``measures/checked_measures.py``), so a node of a file no read named holds none and no rule here reports it. A measure
no tool could take is kept as the reason why, and its rule reports that, so unmeasured code never passes as code within
its limit. The limit is read from the project's choices, beside the tool that supplies the measure, so a project that
changes a limit changes it in one place."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.measures.code_measures import (
    CODE_LINES,
    METHOD_COUNT,
    PATHS_THROUGH,
    READABILITY_SCORE,
    TOTAL_COMPLEXITY,
    UNSHARED_METHOD_GROUPS,
    CodeMeasure,
)
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

# The practice whose reading keeps the project's chosen limits.
_LIMITS_KEPT_BY = "clean_engineering"
_FUNCTION_NODES = ("Operation", "Property")
_CLASS_NODES = ("OoadClass",)
# How a message names the node measured, by its type: an operation and a getter are both functions to a reader.
_KIND = {"Operation": "Function", "Property": "Property", "OoadClass": "Class"}


class CodeMeasureLimit(ProductionCodeRule):
    """One measure held to its limit on the nodes that carry it. A node holding no such measure was not measured, and
    is passed; a node holding the reason no tool could take it is reported with that reason."""

    measure: CodeMeasure
    code_fidelity_only = True
    # What to do about a node past the limit, said after the numbers.
    advice = ""

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if node.has_fact(self.measure.not_taken_fact):
            return [Finding(node, str(node.data[self.measure.not_taken_fact]))]
        limit = self._limit(context)
        value = self.measure.value_on(node) if limit is not None else None
        if value is None or limit is None or value <= limit:
            return []
        return [Finding(node, f"{_KIND.get(node.type, node.type)} '{node.name}' has {self.measure.said_of(value)}, over the limit of {limit:g}. {self.advice}")]


    def _limit(self, context: "RuleCheckContext") -> float | None:
        """The most the measure may be in the project being checked, which Clean Engineering's reading of it keeps.
        A practice that extends Clean Engineering's rules, such as DDD, checks its own nodes against the same limit;
        a graph that holds no Clean Engineering practice holds its code to none."""
        held = context.practice.reading.graph.practices.opened.get(_LIMITS_KEPT_BY)
        return held.reading.chosen_tools.limit(self.measure) if held is not None else None


class LimitPathsThroughAFunction(CodeMeasureLimit):
    slug = "limit-paths-through-a-function"
    node_types = _FUNCTION_NODES
    measure = PATHS_THROUGH
    advice = "Move a branch into a function of its own, named for the case it handles."


class KeepFunctionsReadable(CodeMeasureLimit):
    slug = "keep-functions-readable"
    node_types = _FUNCTION_NODES
    measure = READABILITY_SCORE
    advice = "Return early for the failing cases and take nested loops and conditions out into named functions."


class LimitFunctionLines(CodeMeasureLimit):
    slug = "limit-function-lines"
    node_types = _FUNCTION_NODES
    measure = CODE_LINES
    advice = "Split it at the steps it takes, each a function named for what it does."


class LimitClassComplexity(CodeMeasureLimit):
    slug = "limit-class-complexity"
    node_types = _CLASS_NODES
    measure = TOTAL_COMPLEXITY
    advice = "Find the second job the class does and give it a class of its own."


class LimitClassMethods(CodeMeasureLimit):
    slug = "limit-class-methods"
    node_types = _CLASS_NODES
    measure = METHOD_COUNT
    advice = "Group the methods by the data they use; each group that stands alone is a class."


class KeepClassMethodsSharingData(CodeMeasureLimit):
    slug = "keep-class-methods-sharing-data"
    node_types = _CLASS_NODES
    measure = UNSHARED_METHOD_GROUPS
    advice = "Each group uses none of the fields the others use, so it is a second class kept inside this one: move it out."


MEASURE_LIMIT_RULES: tuple[CodeMeasureLimit, ...] = (
    LimitPathsThroughAFunction(),
    KeepFunctionsReadable(),
    LimitFunctionLines(),
    LimitClassComplexity(),
    LimitClassMethods(),
    KeepClassMethodsSharingData(),
)
