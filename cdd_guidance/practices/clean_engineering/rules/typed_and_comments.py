"""Parameter typing and comment discipline on Operation."""

from __future__ import annotations

from harness.graph.violation import Finding

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.type_refs import is_primitive_type
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_VAGUE_TYPES = frozenset({"any", "object", "dict", "Dict", "Any", "Mapping", "mapping"})
# A client's `withEmail(email)` answers a copy with one field changed: a property setter, not an operation.
_FIELD_CHANGE = re.compile(r"^with[A-Z]")
_INVALID_PARAM_NAME = re.compile(r"^[\w$]+$")
# A Python special operation whose parameters the language fixes, such as `__eq__` or `__contains__`; the operations
# that build or call an object take whatever parameters the class chooses, so they are judged.
_PROTOCOL_OPERATION = re.compile(r"^__(?!(?:init|new|call|post_init)__$)\w+__$")


class UseTypedSignatures(ProductionCodeRule):
    """Judged on each parameter, which the graph reads for every operation's signature, so an untyped parameter is
    reported once, where it is written. A parameter of a language with no type syntax, such as plain JavaScript, has
    nothing to judge. Neither has a parameter of a Python protocol operation, such as `__eq__(self, other: object)` or
    `__setattr__(self, name, value)`: Python fixes its signature, so the operation cannot choose a narrower type."""

    slug = "use-typed-signatures"
    node_types = ("Parameter",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        operation = str(node.get_fact("operation_name") or "")
        if _FIELD_CHANGE.match(operation) or _PROTOCOL_OPERATION.match(operation) or not node.has_fact("type_hint"):
            return []
        if not node.get_fact("in_typed_language", True):
            return []
        return [Finding(node, message) for message in self._param_violation(node.name, node.get_fact("type_hint"))]

    def _param_violation(self, name: str, hint: str) -> list[str]:
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


class LimitComments(ProductionCodeRule):
    slug = "limit-comments"
    node_types = ("Operation", "OoadClass")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if not node.get_fact("prose_comment"):
            return []
        if node.type == "OoadClass":
            return [Finding(node, f"Class '{node.name}' has a descriptive comment; use invariants only.")]
        return [Finding(node, f"Operation '{node.name}' has a descriptive comment.")]
