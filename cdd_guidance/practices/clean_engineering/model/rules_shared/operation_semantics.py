"""Operation rules about responsibilities, errors, and state-change contracts."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.rules_shared.span_helpers import method_body

_IO = re.compile(
    r"\b(?:open|read|write|save|fetch|load|store|send|post|put|delete|upload|download|print)\w*\s*\(",
    re.IGNORECASE,
)
_DOMAIN = re.compile(
    r"\b(?:calculate|compute|validate|parse|transform|convert|aggregate|total|sum|apply|build)\w*\s*\(",
    re.IGNORECASE,
)
_EDGE_RAISE = re.compile(
    r"if\s+(?:not\s+\w+|len\s*\([^)]+\)\s*(?:==|<=)\s*0|\w+\s+is\s+None)\s*:[^\n]*\n(?:[^\n]*\n){0,3}\s*raise\b",
    re.MULTILINE,
)
_EDGE_RAISE_BRACE = re.compile(
    r"if\s*\(\s*(?:!\s*\w+|len\s*\([^)]+\)\s*===?\s*0|\w+\s*===?\s*null)\s*\)[^{]*\{[^\}]*raise\b",
    re.MULTILINE | re.DOTALL,
)
_MUTATION = re.compile(r"\bself\.\w+\s*=|\bthis\.\w+\s*=")
# Nested property writes (this.token, this.validation.verified) — not helper-local state.
_COORDINATED_MUTATION = re.compile(r"\b(?:self|this)(?:\.\w+)+\s*=")
_RETURN = re.compile(r"\breturn\b")


_LIFECYCLE_WITH_VALIDATION = frozenset(
    {
        "load",
        "hydrate",
        "update",
        "loadState",
        "postOnboarding",
        "refresh",
        "importStoredPortabilities",
        "exportStoredPortabilities",
    }
)

_ROUTE_REGISTRAR = re.compile(r"^register\w+Route$")


class KeepOperationsSingleResponsibility(PracticeGraphRule):
    """Flag operations that mix I/O-style calls with domain calculation in one body."""

    slug = "keep-operations-single-responsibility"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if node.name.endswith("Routes") and node.name.startswith("create"):
            return []
        if _ROUTE_REGISTRAR.match(node.name):
            return []
        if node.name in _LIFECYCLE_WITH_VALIDATION:
            return []
        matched = context.ce_operation(node)
        span = context.span(node) if matched is None else _operation_body(context, node, matched[1])
        if not span or len(span.strip()) < 40:
            return []
        if _IO.search(span) and _DOMAIN.search(span):
            return [
                f"Operation '{node.name}' mixes I/O-style calls with domain calculation; split responsibilities."
            ]
        operation = matched[1] if matched else None
        if operation is not None and (operation.line_count or 0) >= 12:
            callees = [c for c in operation.callees if c]
            ioish = sum(1 for c in callees if _IO.search(f"{c}("))
            domainish = sum(1 for c in callees if _DOMAIN.search(f"{c}("))
            if ioish and domainish:
                return [
                    f"Operation '{node.name}' delegates to both I/O and domain helpers; give it one job."
                ]
        return []


class ErrorsOutOfExistence(PracticeGraphRule):
    """Ordinary empty/absent cases should not raise."""

    slug = "errors-out-of-existence"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        span = context.span(node)
        if not span:
            return []
        if _EDGE_RAISE.search(span) or _EDGE_RAISE_BRACE.search(span):
            return [
                f"Operation '{node.name}' raises on an empty or missing value; return a quiet result instead."
            ]
        if re.search(r"raise\s+\w*(?:Error|Exception)\([^)]*(?:empty|not found|missing|none)", span, re.I):
            if re.search(r"if\s+(?:not\s+|len\s*\([^)]*\)\s*==\s*0)", span):
                return [
                    f"Operation '{node.name}' treats an ordinary edge case as an exception."
                ]
        return []


class StateChangeReturnsRecordOrNamedFailure(PracticeGraphRule):
    """Mutating operations should return the record or an explicit outcome."""

    slug = "state-change-returns-record-or-named-failure"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        span = context.span(node)
        if not span or len(span.strip()) < 30:
            return []
        coordinated = len(_COORDINATED_MUTATION.findall(span))
        if coordinated == 0:
            return []
        if _RETURN.search(span):
            return []
        if coordinated <= 1:
            return []
        if re.search(r"->\s*None\b|: void\b", span):
            return []
        if re.search(r"\b(?:throw|raise)\b", span):
            return []
        return [
            f"Operation '{node.name}' mutates state but does not return the record or a named failure."
        ]


class DomainExceptionCarriesContext(PracticeGraphRule):
    slug = "domain-exception-carries-context"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        span = context.span(node)
        if not span:
            return []
        for match in re.finditer(r"raise\s+(\w+(?:Error|Exception))\s*\(\s*([\"']?)\s*\2\s*\)", span):
            return [
                f"Operation '{node.name}' raises {match.group(1)} without context; name the rejected rule."
            ]
        if re.search(r"raise\s+(\w+(?:Error|Exception))\s*\(\s*f?[\"'](?:error|failed|invalid)[\"']\s*\)", span, re.I):
            return [
                f"Operation '{node.name}' raises a generic message; carry domain context."
            ]
        return []


def _operation_body(context, node, operation) -> str:
    from cdd_guidance.practices.clean_engineering.model.operation import operation_source_span

    text = context.text(node)
    span_lines = operation_source_span(operation)
    if text and span_lines:
        start, end = span_lines
        return "\n".join(text.splitlines()[start - 1 : end])
    return method_body(context.text(node), node.name) or context.span(node)


SEMANTIC_RULES: tuple[PracticeGraphRule, ...] = (
    KeepOperationsSingleResponsibility(),
    ErrorsOutOfExistence(),
    StateChangeReturnsRecordOrNamedFailure(),
    DomainExceptionCarriesContext(),
)
