"""Parameter typing and comment discipline on Operation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.production_code import ProductionCodeRule
from cdd_guidance.practices.clean_engineering.model.graph_reading import parameters_of

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_VAGUE_TYPES = frozenset({"any", "object", "dict", "Dict", "Any", "Mapping", "mapping"})
# A client's `withEmail(email)` answers a copy with one field changed: a property setter, not an operation.
_FIELD_CHANGE = re.compile(r"^with[A-Z]")


class UseTypedSignatures(ProductionCodeRule):
    slug = "use-typed-signatures"
    node_types = ("Operation", "Parameter")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if _FIELD_CHANGE.match(_operation_name(node)):
            return []
        if node.type == "Parameter":
            if not node.has_fact("type_hint"):
                return []
            return _param_violation(node.name, node.get_fact("type_hint"))
        for parameter in parameters_of(node):
            hit = _param_violation(parameter.name, parameter.get_fact("type_hint", ""))
            if hit:
                return [f"In '{node.name}': {hit[0]}"]
        return []


class LimitComments(PracticeGraphRule):
    slug = "limit-comments"
    node_types = ("Operation", "OoadClass")

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if not node.get_fact("prose_comment"):
            return []
        if node.type == "OoadClass":
            return [f"Class '{node.name}' has a descriptive comment; use invariants only."]
        return [f"Operation '{node.name}' has a descriptive comment."]


_INVALID_PARAM_NAME = re.compile(r"^[\w$]+$")


def _operation_name(node: "Node") -> str:
    if node.type == "Operation":
        return node.name
    return str(node.get_fact("operation_name") or "")


def _param_violation(name: str, hint: str) -> list[str]:
    from cdd_guidance.practices.clean_engineering.model.type_refs import is_primitive_type

    if not _INVALID_PARAM_NAME.match(name):
        return []
    cleaned = (hint or "").strip()
    if not cleaned:
        return [f"Parameter '{name}' is missing a type annotation."]
    if cleaned in _VAGUE_TYPES:
        return [f"Parameter '{name}' needs a domain-specific type, not a generic container."]
    if is_primitive_type(cleaned) and cleaned.lower() in {"any", "object", "dict"}:
        return [f"Parameter '{name}' needs a domain-specific type, not a generic container."]
    return []
