"""Code-channel graph rules — use the Clean Engineering class model, span only where needed."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

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
        matched = context.ce_operation(node)
        if matched is not None:
            _oclass, operation = matched
            size = operation.line_count if operation.line_count is not None else _line_span(node)
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
        depth = control_flow_depth(context.span(node))
        if depth <= self.limit:
            return []
        return [f"Operation '{node.name}' nests control flow {depth} levels deep (max {self.limit})."]


class UseExceptionsProperly(PracticeGraphRule):
    slug = "use-exceptions-properly"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if bare_catch_in_span(context.span(node)):
            return [f"Operation '{node.name}' has a bare catch."]
        return []


class NeverSwallowExceptions(PracticeGraphRule):
    slug = "never-swallow-exceptions"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if swallowing_catch_in_span(context.span(node)):
            return [f"Operation '{node.name}' swallows a caught failure."]
        return []


class ProvideMeaningfulContext(PracticeGraphRule):
    slug = "provide-meaningful-context"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        for raw in unnamed_numbers_in_span(context.span(node)):
            return [f"Operation '{node.name}' uses the unnamed number {raw}."]
        return []


class AvoidVagueParameterNames(PracticeGraphRule):
    """From clear_parameters_scanner — schema slug avoid-vague-parameter-names."""

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
        hits: list[str] = []
        for param in operation.parameters:
            if param.name.lower() in VAGUE_NAMES:
                hits.append(f"Parameter '{param.name}' in '{operation.name}' is vague.")
        return hits[:1]


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


class UsePropertyNotAccessor(PracticeGraphRule):
    """From property_encapsulation_code_scanner."""

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
    KeepOperationsSmall(),
    SimplifyControlFlow(),
    UseExceptionsProperly(),
    NeverSwallowExceptions(),
    ProvideMeaningfulContext(),
    AvoidVagueParameterNames(),
    UseIntentionRevealingNames(),
    UsePropertyNotAccessor(),
    EliminateDuplication(),
)
