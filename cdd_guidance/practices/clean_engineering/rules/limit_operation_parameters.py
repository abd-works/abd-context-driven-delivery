"""Graph + model — applies to every code channel."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.graph_reading import parameters_of
from cdd_guidance.practices.clean_engineering.rules.operation_checks import (
    OperationMeasureRule,
    operation_label,
)

if TYPE_CHECKING:
    from harness.graph.graph import Node

MAX_DOMAIN_PARAMETERS = 3
_PARAMETER_NAMES_EXCLUDED_FROM_COUNT = frozenset({"self", "cls"})
# Creation / mapping factories may take a record or full field set (align with prefer-instance-operations).
_PARAMETER_COUNT_EXEMPT_OPERATION_NAMES = frozenset({"create", "fromFields", "instance", "fromRequest"})
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z].*)?$")
# The types an Express error handler takes after the failure. Express knows an error handler only by its four
# parameters, so the count is the framework's contract, not setup the handler could be spared.
_EXPRESS_ERROR_HANDLER_TYPES = ["Request", "Response", "NextFunction"]


def counted_parameters(names: list[str], packed: dict[str, int] | None = None) -> int:
    """Each named parameter counts once, except a packed tuple or ``*args``, which counts each value it carries."""
    packed = packed or {}
    named = [name for name in names if name not in _PARAMETER_NAMES_EXCLUDED_FROM_COUNT]
    unnamed = [values for name, values in packed.items() if name not in named]
    return sum(packed.get(name, 1) for name in named) + sum(unnamed)


class LimitOperationParameters(OperationMeasureRule):
    slug = "limit-operation-parameters"

    def measure(self, operation: "Node") -> list[str]:
        if self._parameter_count_exempt(operation.name) or operation.get_fact("published_as_tool", False):
            return []
        parameters = parameters_of(operation)
        if self._express_error_handler(parameters):
            return []
        names = [parameter.name for parameter in parameters]
        packed = operation.get_fact("packed_parameters", None) or {}
        count = counted_parameters(names, packed)
        if count <= MAX_DOMAIN_PARAMETERS:
            return []
        packing = " A packed tuple or *args counts each value it carries." if packed else ""
        return [f"{operation_label(operation)} takes {count} parameters (maximum {MAX_DOMAIN_PARAMETERS}, excluding self).{packing}"]

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
