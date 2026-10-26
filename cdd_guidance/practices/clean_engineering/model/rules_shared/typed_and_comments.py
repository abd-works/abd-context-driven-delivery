"""Parameter typing and comment discipline on Operation."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_VAGUE_TYPES = frozenset({"any", "object", "dict", "Dict", "Any", "Mapping", "mapping"})


class UseTypedSignatures(PracticeGraphRule):
    slug = "use-typed-signatures"
    node_types = ("Operation", "Parameter")

    def check(self, node, context) -> list[str]:
        if node.type == "Parameter":
            if not node.has_fact("type_hint"):
                return []
            return _param_violation(node.name, node.get_fact("type_hint"))
        for name, hint in node.get_fact("parameters", []):
            hit = _param_violation(name, hint)
            if hit:
                return [f"In '{node.name}': {hit[0]}"]
        return []


class LimitComments(PracticeGraphRule):
    slug = "limit-comments"
    node_types = ("Operation", "OoadClass")

    def check(self, node, context) -> list[str]:
        if not node.get_fact("prose_comment"):
            return []
        if node.type == "OoadClass":
            return [f"Class '{node.name}' has a descriptive comment; use invariants only."]
        return [f"Operation '{node.name}' has a descriptive comment."]


_INVALID_PARAM_NAME = re.compile(r"^[\w$]+$")


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
