"""Code-channel graph rules — read the facts each parsed Operation and OoadClass recorded on its graph node."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.rules_shared.operation_semantics import SEMANTIC_RULES

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
# Static factories beyond name patterns (creation / mapping helpers).
_STATIC_FACTORY_EXTRA_NAMES = frozenset(
    {
        "fromRequest",
    }
)
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z].*)?$")


def _allows_static_factory_operation(name: str) -> bool:
    if name in _STATIC_FACTORY_NAMES or name in _STATIC_FACTORY_EXTRA_NAMES:
        return True
    if name.startswith("from_"):
        return True
    if _CAMEL_FROM_FACTORY.match(name):
        return True
    return _LOAD_FACTORY.match(name) is not None

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


def _parameter_names(node) -> list[str]:
    return [name for name, _hint in node.get_fact("parameters", [])]


def _setter_parameter(name: str, property_setter: bool) -> bool:
    """TypeScript/JavaScript `set email(value)` — intent is in the property name."""
    return name == "value" and property_setter


def _operation_is_setter(node) -> bool:
    return bool(node.get_fact("is_property")) and len(node.get_fact("parameters", [])) == 1


class UseExplicitDependencies(PracticeGraphRule):
    slug = "use-explicit-dependencies"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        for type_name in node.get_fact("constructs", []):
            if type_name == node.name:
                continue
            # <<Entity>> / <<Aggregate Root>> may compose sibling types from the same file.
            if node.get_fact("composes_peers") and type_name in node.get_fact("peer_names", []):
                continue
            return [f"Class '{node.name}' constructs '{type_name}' inside its constructor."]
        return []


class KeepOperationsSmall(PracticeGraphRule):
    slug = "keep-operations-small-focused"
    node_types = ("Operation",)
    limit = 20

    def check(self, node, context) -> list[str]:
        size = node.get_fact("line_count") or _line_span(node)
        if size <= self.limit:
            return []
        return [f"Operation '{node.name}' is {size} lines (max {self.limit})."]


class SimplifyControlFlow(PracticeGraphRule):
    slug = "simplify-control-flow"
    node_types = ("Operation",)
    limit = 3

    def check(self, node, context) -> list[str]:
        if node.name.startswith("register") and node.name.endswith("Route"):
            return []
        if node.name.startswith("create") and node.name.endswith("Routes"):
            return []
        depth = node.get_fact("max_control_flow_depth", 0)
        if depth <= self.limit:
            return []
        return [f"Operation '{node.name}' nests control flow {depth} levels deep (max {self.limit})."]


class UseExceptionsProperly(PracticeGraphRule):
    slug = "use-exceptions-properly"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if not node.get_fact("has_bare_catch"):
            return []
        return [f"Operation '{node.name}' has a bare catch."]


class NeverSwallowExceptions(PracticeGraphRule):
    slug = "never-swallow-exceptions"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if not node.get_fact("swallows_exceptions"):
            return []
        return [f"Operation '{node.name}' swallows a caught failure."]


class ProvideMeaningfulContext(PracticeGraphRule):
    slug = "provide-meaningful-context"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        for raw in node.get_fact("unnamed_literal_numbers", []):
            return [f"Operation '{node.name}' uses the unnamed number {raw}."]
        return []


class AvoidVagueParameterNames(PracticeGraphRule):
    slug = "avoid-vague-parameter-names"
    node_types = ("Parameter", "Operation")

    def check(self, node, context) -> list[str]:
        if node.type == "Parameter":
            if node.name.lower() in VAGUE_NAMES:
                return [f"Parameter '{node.name}' is vague. Use a domain-specific name."]
            return []
        for name in _parameter_names(node):
            lowered = name.lower()
            if lowered in VAGUE_NAMES or lowered in _VAGUE_PARAMETER_NAMES:
                return [f"Parameter '{name}' in '{node.name}' is vague."]
        return []


class UseIntentionRevealingNames(PracticeGraphRule):
    slug = "use-intention-revealing-names"
    node_types = ("Parameter", "Operation")

    def check(self, node, context) -> list[str]:
        if node.type == "Parameter":
            return self._parameter_hits(node)
        for name in _parameter_names(node):
            if _setter_parameter(name, _operation_is_setter(node)):
                continue
            if len(name) < 3 or name.lower() in GENERIC_NAMES:
                return [f"Parameter '{name}' in '{node.name}' does not reveal intent."]
        return []

    def _parameter_hits(self, node) -> list[str]:
        if not re.match(r"^[\w$]+$", node.name):
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


class UseConsistentNaming(PracticeGraphRule):
    slug = "use-consistent-naming"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
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


class PreferInstanceOperations(PracticeGraphRule):
    slug = "prefer-instance-operations"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        is_static = bool(node.get_fact("is_static"))
        is_classmethod = bool(node.get_fact("is_classmethod"))
        if not is_static and not is_classmethod:
            return []
        if _allows_static_factory_operation(node.name):
            return []
        kind = "classmethod" if is_classmethod else "staticmethod"
        return [f"Operation '{node.name}' is a {kind}; prefer an instance operation."]


class UsePropertyNotAccessor(PracticeGraphRule):
    slug = "use-property-not-accessor"
    node_types = ("Operation",)

    _PREFIXES = ("calculate_", "compute_", "get_")

    def check(self, node, context) -> list[str]:
        if node.get_fact("is_property") or not node.has_fact("parameters"):
            return []
        if not any(node.name.startswith(prefix) for prefix in self._PREFIXES):
            return []
        if _parameter_names(node):
            return []
        owner = node.get_fact("owner", "")
        return [f"Operation '{node.name}' on '{owner}' looks like a getter; use a property."]


class EliminateDuplication(PracticeGraphRule):
    slug = "eliminate-duplication"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        return []

    def check_practice(self, context) -> list[tuple[str, str]]:
        seen: dict[str, str] = {}
        hits: list[tuple[str, str]] = []
        for op_node in context.practice.nodes.get("Operation", []):
            fingerprint = op_node.get_fact("body_fingerprint", "")
            if not fingerprint or op_node.get_fact("line_count", 0) < 3:
                continue
            if fingerprint in seen:
                hits.append((op_node.node_id, f"Operation '{op_node.name}' duplicates the body of '{seen[fingerprint]}'."))
            else:
                seen[fingerprint] = op_node.name
        return hits


def _line_span(node) -> int:
    start = node.source.start_line
    end = node.source.end_line
    if end <= start:
        return 0
    return end - start + 1


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
