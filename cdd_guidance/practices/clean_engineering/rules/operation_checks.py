"""Code-channel graph rules — read the facts each parsed Operation and OoadClass recorded on its graph node."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.graph_reading import parameters_of
from cdd_guidance.practices.clean_engineering.rules.class_graph import ClassGraph
from cdd_guidance.practices.clean_engineering.rules.near_copies import NearCopies
from cdd_guidance.practices.clean_engineering.rules.operation_semantics import SEMANTIC_RULES
from cdd_guidance.practices.clean_engineering.model.production_code import ProductionCodeRule, is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

VAGUE_NAMES = {
    "thing",
    "stuff",
    "info",
    "data",
    "args_list",
    "params",
    "options",
    "misc",
    "obj",
    "payload",
}

# snake_case requires at least one underscore between words; plain `register` is not snake_case.
_SNAKE_CASE = re.compile(r"^_*[a-z][a-z0-9]*(_[a-z0-9]+)+_*$")
_CAMEL_CASE = re.compile(r"^_*[a-z]+[A-Z][a-zA-Z0-9]*$")
_DUNDER = re.compile(r"^__[a-z]+__$")
_SKIP_OP_NAMES = frozenset(
    {
        "constructor",
        "__init__",
        "setUp",
        "tearDown",
        "setUpClass",
        "tearDownClass",
        "setUpModule",
    }
)
_STATIC_FACTORY_NAMES = frozenset({"instance", "create"})
# Static factories beyond name patterns (creation / mapping helpers): `now` makes a new value for this moment, as
# `datetime.now` does, and `every` makes each value a class allows, such as `FormatGroup.every()`. A global accessor
# such as `current` is not one: it hands out ambient state, which `hold-state-on-the-object-not-in-parameters` replaces
# with an object the caller holds.
_STATIC_FACTORY_EXTRA_NAMES = frozenset({"fromRequest", "now", "every"})
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z_].*)?$")
# The names a return type spells: `list[CatalogPractice]` spells `list` and `CatalogPractice`.
_TYPE_NAME = re.compile(r"[A-Za-z_]\w*")


def _allows_static_factory_operation(name: str) -> bool:
    if name in _STATIC_FACTORY_NAMES or name in _STATIC_FACTORY_EXTRA_NAMES:
        return True
    if name.startswith("from_"):
        return True
    if _CAMEL_FROM_FACTORY.match(name):
        return True
    return _LOAD_FACTORY.match(name) is not None


def _makes_its_own_class(operation: "Node") -> bool:
    """A factory: a class-level operation that makes its own class from what it is given, such as `for_project(root)
    -> ProjectApproach`, `every(folder) -> list[Practice]`, or `-> Self`; no instance exists yet to call it on. One
    that takes nothing, such as `current() -> Board`, hands out a global instance, which a caller should hold instead."""
    if not parameters_of(operation):
        return False
    spelled = set(_TYPE_NAME.findall(str(getattr(operation, "return_type", "") or "")))
    return bool(spelled & {operation.get_fact("owner", ""), "Self"})


_VAGUE_PARAMETER_NAMES = frozenset({"options", "opts", "config", "settings"})

GENERIC_NAMES = {
    "info",
    "thing",
    "stuff",
    "temp",
    "tmp",
    "val",
    "obj",
    "item",
    "foo",
    "bar",
    "baz",
    "misc",
    "blob",
    "value",
}


def _parameter_names(node: "Node") -> list[str]:
    return [parameter.name for parameter in parameters_of(node)]


def _setter_parameter(name: str, property_setter: bool) -> bool:
    """`value` in a setter, TypeScript's `set email(value)` or Python's `@email.setter`: the property names the intent."""
    return name == "value" and property_setter


class UseExplicitDependencies(ProductionCodeRule):
    """A collaborator a constructor builds that its caller cannot hand it. The parser leaves out what a caller can
    replace or what the class owns: a failure it raises, a parameter's default, a part built from its own state. This
    rule passes values, failures, and collections (``ClassGraph.is_value``) and the peers an Entity composes."""

    slug = "use-explicit-dependencies"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        classes = context.index(ClassGraph)
        for type_name in node.get_fact("constructs", []):
            if type_name == node.name or classes.is_value(type_name):
                continue
            # <<Entity>> / <<Aggregate Root>> may compose sibling types from the same file.
            if node.get_fact("composes_peers") and type_name in node.get_fact("peer_names", []):
                continue
            return [f"Class '{node.name}' constructs '{type_name}' inside its constructor."]
        return []


class OperationMeasureRule(ProductionCodeRule):
    """Measures each operation body the graph records: every Operation node, and each Property node a getter backs,
    whose node records the getter's measurements."""

    node_types = ("Operation", "Property")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return self.measure(node)

    def measure(self, operation: "Node") -> list[str]:
        return []


def operation_label(operation: "Node") -> str:
    """How a message names the measured operation: `Operation 'load'`, or `Property 'total'` for a getter."""
    return f"{operation.type} '{operation.name}'"


def operation_line_count(operation: "Node") -> int:
    """The parser's count; for a node without one, the lines its source span covers."""
    span = operation.source.end_line - operation.source.start_line + 1
    return operation.get_fact("line_count") or (span if span > 1 else 0)


class KeepOperationsSmall(OperationMeasureRule):
    slug = "keep-operations-small-focused"
    limit = 20

    def measure(self, operation: "Node") -> list[str]:
        size = operation_line_count(operation)
        if size <= self.limit:
            return []
        return [f"{operation_label(operation)} is {size} lines (max {self.limit})."]


class SimplifyControlFlow(OperationMeasureRule):
    slug = "simplify-control-flow"
    limit = 3

    def measure(self, operation: "Node") -> list[str]:
        if operation.name.startswith("register") and operation.name.endswith("Route"):
            return []
        if operation.name.startswith("create") and operation.name.endswith("Routes"):
            return []
        depth = operation.get_fact("max_control_flow_depth", 0) or 0
        if depth <= self.limit:
            return []
        return [f"{operation_label(operation)} nests control flow {depth} levels deep (max {self.limit})."]


class UseExceptionsProperly(ProductionCodeRule):
    """A spec catches every exception on purpose, to prove what a call raises, so only production code is judged."""

    slug = "use-exceptions-properly"
    node_types = OperationMeasureRule.node_types

    def check_production(self, operation: "Node", context: "RuleCheckContext") -> list[str]:
        if not operation.get_fact("has_bare_catch"):
            return []
        return [f"{operation_label(operation)} catches every exception (a bare except, or except Exception that never re-raises)."]


class NeverSwallowExceptions(ProductionCodeRule):
    slug = "never-swallow-exceptions"
    node_types = OperationMeasureRule.node_types

    def check_production(self, operation: "Node", context: "RuleCheckContext") -> list[str]:
        if not operation.get_fact("swallows_exceptions"):
            return []
        return [f"{operation_label(operation)} swallows a caught failure or hands back a fallback in its place."]


class ProvideMeaningfulContext(ProductionCodeRule):
    slug = "provide-meaningful-context"
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        for raw in node.get_fact("unnamed_literal_numbers", []):
            return [f"Operation '{node.name}' uses the unnamed number {raw}."]
        return []


class AvoidVagueParameterNames(ProductionCodeRule):
    slug = "avoid-vague-parameter-names"
    node_types = ("Parameter", "Operation")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if node.type == "Parameter":
            if node.name.lower() in VAGUE_NAMES:
                return [f"Parameter '{node.name}' is vague. Use a domain-specific name."]
            return []
        for name in _parameter_names(node):
            lowered = name.lower()
            if lowered in VAGUE_NAMES or lowered in _VAGUE_PARAMETER_NAMES:
                return [f"Parameter '{name}' in '{node.name}' is vague."]
        return []


# A Claude Code mod hands every hook its engine as `$`, the name the mod API documents, so a reader knows it on sight.
_CONVENTIONAL_PARAMETER_NAMES = frozenset({"$"})


class UseIntentionRevealingNames(ProductionCodeRule):
    """Judged on each parameter, which the graph reads for every operation's signature, so a name is reported once,
    where it is written."""

    slug = "use-intention-revealing-names"
    node_types = ("Parameter",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if not re.match(r"^[\w$]+$", node.name) or node.name in _CONVENTIONAL_PARAMETER_NAMES:
            return []
        operation = node.get_fact("operation_name", "")
        if _setter_parameter(node.name, bool(node.get_fact("property_setter"))):
            return []
        if operation == "text" and node.name in {"value", "rawField"}:
            return []
        if node.name == "value" and operation == "asyncRoute":
            return []
        if len(node.name) < 3 or node.name.lower() in GENERIC_NAMES:
            return [f"Parameter '{node.name}' does not reveal intent."]
        return []


class UseConsistentNaming(ProductionCodeRule):
    slug = "use-consistent-naming"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        snake_names: list[str] = []
        camel_names: list[str] = []
        for shape in node.get_fact("operation_shapes", []):
            name = shape["name"]
            if not name or name in _SKIP_OP_NAMES or _DUNDER.match(name) or name.startswith("_"):
                continue
            if _CAMEL_CASE.match(name):
                camel_names.append(name)
            elif _SNAKE_CASE.match(name):
                snake_names.append(name)
        if not snake_names or not camel_names:
            return []
        minority = camel_names if len(camel_names) <= len(snake_names) else snake_names
        style = "camelCase" if minority is camel_names else "snake_case"
        return [
            f"Operation '{minority[0]}' uses {style} while other operations on '{node.name}' "
            "use the other convention."
        ]


class PreferInstanceOperations(ProductionCodeRule):
    slug = "prefer-instance-operations"
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        is_static = bool(node.get_fact("is_static"))
        is_classmethod = bool(node.get_fact("is_classmethod"))
        if not is_static and not is_classmethod:
            return []
        if _allows_static_factory_operation(node.name) or _makes_its_own_class(node):
            return []
        kind = "classmethod" if is_classmethod else "staticmethod"
        return [f"Operation '{node.name}' is a {kind}; prefer an instance operation."]


class UsePropertyNotAccessor(ProductionCodeRule):
    slug = "use-property-not-accessor"
    node_types = ("Operation",)

    _PREFIXES = ("calculate_", "compute_", "get_")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if node.get_fact("is_property"):
            return []
        if not any(node.name.startswith(prefix) for prefix in self._PREFIXES):
            return []
        if _parameter_names(node):
            return []
        owner = node.get_fact("owner", "")
        return [f"Operation '{node.name}' on '{owner}' looks like a getter; use a property."]


class EliminateDuplication(PracticeGraphRule):
    """Production operations whose bodies are the same, or nearly the same: a copy with a renamed variable or one
    changed line is still a second place the same fix has to go."""

    slug = "eliminate-duplication"
    node_types = ("Operation",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        operations = [node for node in context.nodes("Operation") if not is_test_code(node.source.file)]
        seen: dict[str, str] = {}
        hits: list[tuple[str, str]] = []
        copied: set[str] = set()
        for op_node in operations:
            fingerprint = op_node.get_fact("body_fingerprint", "")
            if not fingerprint or op_node.get_fact("line_count", 0) < 3:
                continue
            if fingerprint in seen:
                copied.add(op_node.node_id)
                hits.append((op_node.node_id, f"Operation '{op_node.name}' duplicates the body of '{seen[fingerprint]}'."))
            else:
                seen[fingerprint] = op_node.name
        near = NearCopies([node for node in operations if node.node_id not in copied])
        for copy, original, shared in near.pairs():
            hits.append(
                (
                    copy.node_id,
                    f"Operation '{copy.name}' nearly duplicates '{original.name}' ({original.source.file}): "
                    f"{round(100 * shared)}% of their code is the same. Give the shared logic one function.",
                )
            )
        return hits


CODE_RULES: tuple[PracticeGraphRule, ...] = (
    UseExplicitDependencies(),
    UseConsistentNaming(),
    KeepOperationsSmall(),
    SimplifyControlFlow(),
    UseExceptionsProperly(),
    NeverSwallowExceptions(),
    ProvideMeaningfulContext(),
    AvoidVagueParameterNames(),
    UseIntentionRevealingNames(),
    PreferInstanceOperations(),
    UsePropertyNotAccessor(),
    EliminateDuplication(),
) + SEMANTIC_RULES
