"""Clean-engineering graph checks against loaded nodes and source."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_NEW = re.compile(r"\bnew\s+([A-Z]\w*)")
_CATCH = re.compile(r"\bcatch\s*(\([^)]*\))?\s*\{")
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_NUMBER = re.compile(r"\b(\d+(?:\.\d+)?)\b")
_SAFE_NUMBERS = {0, 1, 2, -1, 0.0, 1.0, 0.5, 10, 100}


class LimitOperationParameters(PracticeGraphRule):
    slug = "limit-operation-parameters"
    node_types = ("Operation",)

    def check(self, node, text: str) -> list[str]:
        count = sum(
            1
            for edge in node.practice.edges.get("hasParameter", [])
            if edge.parent is node
        )
        if count <= 2:
            return []
        return [f"Operation '{node.name}' takes more than two parameters."]


class UseExplicitDependencies(PracticeGraphRule):
    slug = "use-explicit-dependencies"
    node_types = ("OoadClass",)

    def check(self, node, text: str) -> list[str]:
        body = _class_body(text, node.name)
        constructor = _constructor_body(body)
        if not constructor:
            return []
        for created in _NEW.findall(constructor):
            if created != node.name:
                return [f"Class '{node.name}' constructs '{created}' inside its constructor."]
        return []


class KeepOperationsSmall(PracticeGraphRule):
    slug = "keep-operations-small-focused"
    node_types = ("Operation",)
    limit = 20

    def check(self, node, text: str) -> list[str]:
        start = node.source.start_line
        end = node.source.end_line
        if end <= start:
            return []
        size = end - start + 1
        if size <= self.limit:
            return []
        return [f"Operation '{node.name}' is {size} lines (max {self.limit})."]


class SimplifyControlFlow(PracticeGraphRule):
    slug = "simplify-control-flow"
    node_types = ("Operation",)
    limit = 3

    def check(self, node, text: str) -> list[str]:
        depth = max(0, _brace_depth(_span(node, text)) - 1)
        if depth <= self.limit:
            return []
        return [f"Operation '{node.name}' nests control flow {depth} levels deep (max {self.limit})."]


class UseExceptionsProperly(PracticeGraphRule):
    slug = "use-exceptions-properly"
    node_types = ("Operation",)

    def check(self, node, text: str) -> list[str]:
        for match in _CATCH.finditer(_span(node, text)):
            binding = (match.group(1) or "").strip()
            if binding and binding != "()":
                continue
            return [f"Operation '{node.name}' has a bare catch."]
        return []


class NeverSwallowExceptions(PracticeGraphRule):
    slug = "never-swallow-exceptions"
    node_types = ("Operation",)

    def check(self, node, text: str) -> list[str]:
        body = _span(node, text)
        for match in _CATCH.finditer(body):
            catch_body = _brace_body(body, match.end() - 1)
            if catch_body is None:
                continue
            stripped = catch_body.strip()
            if stripped and stripped not in {";", "pass", "// ignore", "/* ignore */"}:
                continue
            return [f"Operation '{node.name}' swallows a caught failure."]
        return []


class ProvideMeaningfulContext(PracticeGraphRule):
    slug = "provide-meaningful-context"
    node_types = ("Operation",)

    def check(self, node, text: str) -> list[str]:
        code = _STRING.sub('""', _span(node, text))
        for raw in _NUMBER.findall(code):
            value = float(raw)
            if value in _SAFE_NUMBERS:
                continue
            return [f"Operation '{node.name}' uses the unnamed number {raw}."]
        return []


RULES: tuple[PracticeGraphRule, ...] = (
    LimitOperationParameters(),
    UseExplicitDependencies(),
    KeepOperationsSmall(),
    SimplifyControlFlow(),
    UseExceptionsProperly(),
    NeverSwallowExceptions(),
    ProvideMeaningfulContext(),
)

BY_SLUG: dict[str, PracticeGraphRule] = {rule.slug: rule for rule in RULES}


def _span(node, text: str) -> str:
    start = node.source.start_line
    end = node.source.end_line
    if not text or not start or not end or end < start:
        return text
    return "\n".join(text.splitlines()[start - 1 : end])


def _class_body(text: str, name: str) -> str:
    match = re.search(rf"\bclass\s+{re.escape(name)}\b[^{{]*\{{", text)
    if match is None:
        return ""
    return _brace_body(text, match.end() - 1) or ""


def _constructor_body(class_body: str) -> str:
    match = re.search(r"\bconstructor\s*\([^)]*\)\s*\{", class_body)
    if match is None:
        return ""
    return _brace_body(class_body, match.end() - 1) or ""


def _brace_body(text: str, open_index: int) -> str | None:
    if open_index >= len(text) or text[open_index] != "{":
        return None
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index]
    return None


def _brace_depth(text: str) -> int:
    depth = 0
    deepest = 0
    for character in text:
        if character == "{":
            depth += 1
            deepest = max(deepest, depth)
        elif character == "}":
            depth = max(0, depth - 1)
    return deepest
