"""Graph + model — applies to every code channel."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.reading.production_classes import counted_parameters, parameters_of
from cdd_guidance.practices.clean_engineering.measures import code_measures
from cdd_guidance.practices.clean_engineering.rules.operation_checks import (
    OperationMeasureRule,
    operation_label,
)

if TYPE_CHECKING:
    from harness.graph.graph import Node

# Creation / mapping factories may take a record or full field set (align with prefer-instance-operations).
_PARAMETER_COUNT_EXEMPT_OPERATION_NAMES = frozenset({"create", "fromFields", "instance", "fromRequest"})
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z].*)?$")
# The types an Express error handler takes after the failure. Express knows an error handler only by its four
# parameters, so the count is the framework's contract, not setup the handler could be spared.
_EXPRESS_ERROR_HANDLER_TYPES = ["Request", "Response", "NextFunction"]


class LimitOperationParameters(OperationMeasureRule):
    """Holds the parameters an operation takes to the limit of the measure ``parameters_taken``: the limit the project
    being checked sets in its config's code measures, else the shipped one. It reports in every project, whether or
    not the project measures its code, since the count is read from the operation's own parameter nodes."""

    slug = "limit-operation-parameters"

    def most_parameters(self, operation: "Node") -> float:
        """The most parameters operation may take: its project's own limit when the project sets one, else the shipped
        limit."""
        held = operation.graph.practices.opened.get("clean_engineering")
        chosen = held.reading.chosen_tools.limit(code_measures.PARAMETERS_TAKEN) if held is not None else None
        return chosen if chosen is not None else code_measures.SHIPPED_LIMITS[code_measures.PARAMETERS_TAKEN.name]

    def measure(self, operation: "Node") -> list[str]:
        if self._parameter_count_exempt(operation.name) or operation.get_fact("published_as_tool", False):
            return []
        parameters = parameters_of(operation)
        if self._express_error_handler(parameters):
            return []
        names = [parameter.name for parameter in parameters]
        packed = operation.get_fact("packed_parameters", None) or {}
        count = counted_parameters(names, packed)
        most = self.most_parameters(operation)
        if count <= most:
            return []
        packing = " A packed tuple or *args counts each value it carries." if packed else ""
        return [f"{operation_label(operation)} takes {count} parameters (maximum {most:g}, excluding self).{packing}"]

    def _express_error_handler(self, parameters: list["Node"]) -> bool:
        """True for Express's four-parameter error handler: a failure, then the request, response, and next function."""
        hints = [parameter.get_fact("type_hint", "") for parameter in parameters]
        return len(hints) == len(_EXPRESS_ERROR_HANDLER_TYPES) + 1 and hints[1:] == _EXPRESS_ERROR_HANDLER_TYPES

    def _parameter_count_exempt(self, operation_name: str) -> bool:
        if operation_name in _PARAMETER_COUNT_EXEMPT_OPERATION_NAMES:
            return True
        if operation_name.startswith("from_"):
            return True
        if _CAMEL_FROM_FACTORY.match(operation_name):
            return True
        return _LOAD_FACTORY.match(operation_name) is not None
