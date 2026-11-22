"""refuse-unreadable-input: a read that could not parse or decode what it read refuses by name; it never answers an
empty value, which its caller would take for nothing there and save over."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.rules.operation_checks import OperationMeasureRule, operation_label

if TYPE_CHECKING:
    from harness.graph.graph import Node


class RefuseUnreadableInput(OperationMeasureRule):
    """Reports an operation one of whose catches takes a failure to parse or decode and answers an empty value. The
    build keeps the failure caught on the operation (``unreadable_read_as_empty``): one named for it, such as
    ``JSONDecodeError``, or a wider one around a call that parses stored text. A catch for a file that is not there
    passes, since nothing there is an empty result."""

    slug = "refuse-unreadable-input"

    def measure(self, operation: "Node") -> list[str]:
        caught = operation.get_fact("unreadable_read_as_empty", "")
        if not caught:
            return []
        return [
            f"{operation_label(operation)} catches {caught}, a failure to parse or decode what it read, and answers an empty value. "
            "Raise a failure that names the file or record instead: a caller reads the empty value as nothing there and writes over what could not be read."
        ]
