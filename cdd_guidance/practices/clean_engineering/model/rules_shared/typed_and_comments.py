"""Parameter typing and comment discipline on Operation."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_VAGUE_TYPES = frozenset({"any", "object", "dict", "Dict", "Any", "Mapping", "mapping"})
_PROSE_COMMENT = re.compile(
    r"(?:transient|value object|carries|implementation|see also|cross-ref)",
    re.IGNORECASE,
)


class UseTypedSignatures(PracticeGraphRule):
    slug = "use-typed-signatures"
    node_types = ("Operation", "Parameter")

    def check(self, node, context) -> list[str]:
        if node.type == "Parameter":
            return _param_violation(node.name, _hint_for_param(context, node))
        matched = context.ce_operation(node)
        if matched is None:
            return []
        _oclass, operation = matched
        for param in operation.parameters:
            hit = _param_violation(param.name, (param.type_hint or "").strip())
            if hit:
                return [f"In '{operation.name}': {hit[0]}"]
        return []


class LimitComments(PracticeGraphRule):
    slug = "limit-comments"
    node_types = ("Operation", "OoadClass")

    def check(self, node, context) -> list[str]:
        if node.type == "OoadClass":
            text = context.text(node)
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("#") and _PROSE_COMMENT.search(stripped):
                    return [f"Class '{node.name}' has a descriptive comment; use invariants only."]
            return []
        span = context.span(node)
        for line in span.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and _PROSE_COMMENT.search(stripped):
                return [f"Operation '{node.name}' has a descriptive comment."]
            if "//" in stripped and _PROSE_COMMENT.search(stripped):
                return [f"Operation '{node.name}' has a descriptive comment."]
        return []


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


def _hint_for_param(context, node) -> str:
    param = context.ce_parameter(node)
    return (param.type_hint or "").strip() if param is not None else ""


def _parsed_op(context, node):
    matched = context.ce_operation(node)
    return matched[1] if matched else None
