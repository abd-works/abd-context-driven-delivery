"""Code-channel graph rules — prefer Operation model fields from parsers."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.model.rules_shared.operation_semantics import SEMANTIC_RULES
from practices.clean_engineering.model.rules_shared.span_helpers import (
    bare_catch_in_span,
    class_body,
    constructor_body,
    control_flow_depth,
    swallowing_catch_in_span,
    unnamed_numbers_in_span,
)

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

_SNAKE_CASE = re.compile(r"^_*[a-z][a-z0-9]*(_[a-z0-9]+)*_*$")
_CAMEL_CASE = re.compile(r"^_*[a-z]+[A-Z][a-zA-Z0-9]*$")
_DUNDER = re.compile(r"^__[a-z]+__$")
_SKIP_OP_NAMES = frozenset({"setUp", "tearDown", "setUpClass", "tearDownClass", "setUpModule"})
_STATIC_FACTORY_NAMES = frozenset({"instance", "create"})

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


def _parsed_operation(context, node):
    matched = context.ce_operation(node)
    return matched[1] if matched else None


class UseExplicitDependencies(PracticeGraphRule):
    slug = "use-explicit-dependencies"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is not None:
            for op in oclass.operations:
                if op.name not in {"__init__", "constructor"}:
                    continue
                for type_name, _line in op.constructed_types:
                    if type_name != node.name:
                        return [f"Class '{node.name}' constructs '{type_name}' inside its constructor."]
            return []
        text = context.text(node)
        body = class_body(text, node.name)
        constructor = constructor_body(body)
        if not constructor:
            return []
        for created in re.findall(r"\bnew\s+([A-Z]\w*)", constructor):
            if created != node.name:
                return [f"Class '{node.name}' constructs '{created}' inside its constructor."]
        return []


class KeepOperationsSmall(PracticeGraphRule):
    slug = "keep-operations-small-focused"
    node_types = ("Operation",)
    limit = 20

    def check(self, node, context) -> list[str]:
        operation = _parsed_operation(context, node)
        if operation is not None and operation.line_count is not None:
            size = operation.line_count
        else:
            size = _line_span(node)
        if size <= self.limit:
            return []
        return [f"Operation '{node.name}' is {size} lines (max {self.limit})."]


class SimplifyControlFlow(PracticeGraphRule):
    slug = "simplify-control-flow"
    node_types = ("Operation",)
    limit = 3

    def check(self, node, context) -> list[str]:
        operation = _parsed_operation(context, node)
        if operation is not None:
            depth = operation.max_control_flow_depth
        else:
            depth = control_flow_depth(context.span(node))
        if depth <= self.limit:
            return []
        return [f"Operation '{node.name}' nests control flow {depth} levels deep (max {self.limit})."]


class UseExceptionsProperly(PracticeGraphRule):
    slug = "use-exceptions-properly"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        operation = _parsed_operation(context, node)
        bare = operation.has_bare_catch if operation is not None else bare_catch_in_span(context.span(node))
        if not bare:
            return []
        return [f"Operation '{node.name}' has a bare catch."]


class NeverSwallowExceptions(PracticeGraphRule):
    slug = "never-swallow-exceptions"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        operation = _parsed_operation(context, node)
        swallow = (
            operation.swallows_exceptions
            if operation is not None
            else swallowing_catch_in_span(context.span(node))
        )
        if not swallow:
            return []
        return [f"Operation '{node.name}' swallows a caught failure."]


class ProvideMeaningfulContext(PracticeGraphRule):
    slug = "provide-meaningful-context"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        operation = _parsed_operation(context, node)
        numbers = (
            operation.unnamed_literal_numbers
            if operation is not None
            else unnamed_numbers_in_span(context.span(node))
        )
        for raw in numbers:
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
        matched = context.ce_operation(node)
        if matched is None:
            return []
        _oclass, operation = matched
        for param in operation.parameters:
            if param.name.lower() in VAGUE_NAMES:
                return [f"Parameter '{param.name}' in '{operation.name}' is vague."]
        return []


class UseIntentionRevealingNames(PracticeGraphRule):
    slug = "use-intention-revealing-names"
    node_types = ("Parameter", "Operation")

    def check(self, node, context) -> list[str]:
        if node.type == "Parameter":
            if len(node.name) < 3 or node.name.lower() in GENERIC_NAMES:
                return [f"Parameter '{node.name}' does not reveal intent."]
            return []
        matched = context.ce_operation(node)
        if matched is None:
            return []
        _oclass, operation = matched
        for param in operation.parameters:
            if len(param.name) < 3 or param.name.lower() in GENERIC_NAMES:
                return [f"Parameter '{param.name}' in '{operation.name}' does not reveal intent."]
        return []


class UseConsistentNaming(PracticeGraphRule):
    slug = "use-consistent-naming"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        snake_ops: list = []
        camel_ops: list = []
        for op in oclass.operations:
            name = op.name
            if name in _SKIP_OP_NAMES or _DUNDER.match(name):
                continue
            if _CAMEL_CASE.match(name):
                camel_ops.append(op)
            elif _SNAKE_CASE.match(name):
                snake_ops.append(op)
        if not snake_ops or not camel_ops:
            return []
        minority = camel_ops if len(camel_ops) <= len(snake_ops) else snake_ops
        style = "camelCase" if minority is camel_ops else "snake_case"
        op = minority[0]
        return [
            f"Operation '{op.name}' uses {style} while other operations on '{node.name}' "
            "use the other convention."
        ]


class PreferInstanceOperations(PracticeGraphRule):
    slug = "prefer-instance-operations"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        operation = _parsed_operation(context, node)
        if operation is None:
            return []
        if not operation.is_static and not operation.is_classmethod:
            return []
        name = operation.name
        if name in _STATIC_FACTORY_NAMES or name.startswith("from_"):
            return []
        kind = "classmethod" if operation.is_classmethod else "staticmethod"
        return [f"Operation '{name}' is a {kind}; prefer an instance operation."]


class UsePropertyNotAccessor(PracticeGraphRule):
    slug = "use-property-not-accessor"
    node_types = ("Operation",)

    _PREFIXES = ("calculate_", "compute_", "get_")

    def check(self, node, context) -> list[str]:
        matched = context.ce_operation(node)
        if matched is None:
            return []
        oclass, operation = matched
        if operation.is_property:
            return []
        if any(operation.name.startswith(prefix) for prefix in self._PREFIXES):
            if len(operation.parameters) == 0:
                return [
                    f"Operation '{operation.name}' on '{oclass.name}' looks like a getter; use a property."
                ]
        return []


class EliminateDuplication(PracticeGraphRule):
    slug = "eliminate-duplication"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        return []

    def check_practice(self, context) -> list[tuple[str, str]]:
        seen: dict[str, tuple[str, str]] = {}
        hits: list[tuple[str, str]] = []
        for op_node in context.practice.nodes.get("Operation", []):
            matched = context.ce_operation(op_node)
            if matched is None:
                continue
            _oclass, operation = matched
            fp = operation.body_fingerprint or context.operation_fingerprint(op_node, operation)
            if not fp or (operation.line_count or 0) < 3:
                continue
            if fp in seen:
                orig_id, orig_name = seen[fp]
                hits.append(
                    (
                        op_node.node_id,
                        f"Operation '{op_node.name}' duplicates the body of '{orig_name}'.",
                    )
                )
            else:
                seen[fp] = (op_node.node_id, op_node.name)
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
