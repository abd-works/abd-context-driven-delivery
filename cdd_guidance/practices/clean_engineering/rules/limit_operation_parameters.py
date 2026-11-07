"""Graph + model — applies to every code channel."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.rules_shared.measured_operation import (
    MeasuredOperation,
    OperationMeasureRule,
)

MAX_DOMAIN_PARAMETERS = 3
_PARAMETER_NAMES_EXCLUDED_FROM_COUNT = frozenset({"self", "cls"})
# Creation / mapping factories may take a record or full field set (align with prefer-instance-operations).
_PARAMETER_COUNT_EXEMPT_OPERATION_NAMES = frozenset({"create", "fromFields", "instance", "fromRequest"})
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z].*)?$")


def _parameter_count_exempt(operation_name: str) -> bool:
    if operation_name in _PARAMETER_COUNT_EXEMPT_OPERATION_NAMES:
        return True
    if operation_name.startswith("from_"):
        return True
    if _CAMEL_FROM_FACTORY.match(operation_name):
        return True
    return _LOAD_FACTORY.match(operation_name) is not None


def counted_parameters(names: list[str], packed: dict[str, int] | None = None) -> int:
    """Each named parameter counts once, except a packed tuple or ``*args``, which counts each value it carries."""
    packed = packed or {}
    named = [name for name in names if name not in _PARAMETER_NAMES_EXCLUDED_FROM_COUNT]
    unnamed = [values for name, values in packed.items() if name not in named]
    return sum(packed.get(name, 1) for name in named) + sum(unnamed)


class LimitOperationParameters(OperationMeasureRule):
    slug = "limit-operation-parameters"

    def measure(self, operation: MeasuredOperation) -> list[str]:
        if _parameter_count_exempt(operation.name):
            return []
        names = [name for name, _hint in operation.fact("parameters", None) or []]
        packed = operation.fact("packed_parameters", None) or {}
        count = counted_parameters(names, packed)
        if count <= MAX_DOMAIN_PARAMETERS:
            return []
        packing = " A packed tuple or *args counts each value it carries." if packed else ""
        return [f"{operation.label} takes {count} parameters (maximum {MAX_DOMAIN_PARAMETERS}, excluding self).{packing}"]
