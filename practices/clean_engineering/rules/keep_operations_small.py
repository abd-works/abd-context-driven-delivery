from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class KeepOperationsSmall(PracticeGraphRule):
    slug = "keep-operations-small-focused"
    node_types = ("Operation",)
    limit = 20

    def check(self, node, context) -> list[str]:
        matched = context.ce_operation(node)
        if matched is not None:
            _oclass, operation = matched
            if operation.line_count is not None:
                size = operation.line_count
            else:
                size = _line_span(node)
        else:
            size = _line_span(node)
        if size <= self.limit:
            return []
        return [f"Operation '{node.name}' is {size} lines (max {self.limit})."]


def _line_span(node) -> int:
    start = node.source.start_line
    end = node.source.end_line
    if end <= start:
        return 0
    return end - start + 1
