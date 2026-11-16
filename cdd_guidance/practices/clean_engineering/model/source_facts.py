"""The facts a class's or an operation's source gives the rules, worked out apart from the graph nodes that keep them:
a node keeps what these find as its own graph facts, so a rule reads them from a node read now or read back from a
saved graph alike."""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING, Any

from cdd_guidance.practices.clean_engineering.model.operation_metrics import (
    MIN_DELEGATION_LINES,
    CardBullets,
    names_call_io_and_domain,
)

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
    from cdd_guidance.practices.clean_engineering.model.operation import Operation

# `self.column_name = ...` or `this.columnName: string = ...` in a constructor: a field the class holds.
_ASSIGNED_FIELD = re.compile(r"(?:self|this)\.(\w+)\s*(?::\s*([^=\n]+?))?\s*=(?!=)")
# A body shorter than this, once its whitespace is collapsed, is too small for two copies of it to be a duplication.
_MIN_FINGERPRINTED_CHARACTERS = 40
# How many hex digits of the hash a fingerprint keeps: enough that two different bodies never share one in practice.
_FINGERPRINT_DIGITS = 24
# The names a constructor goes by: Python's and the C-family languages'.
CONSTRUCTOR_NAMES = frozenset({"__init__", "constructor"})
# The operations that build their object, Python's `__new__` with the constructors. One can only build the object or
# refuse the call; it has no quiet result to return instead.
_BUILDING_NAMES = CONSTRUCTOR_NAMES | {"__new__"}


class BodyFingerprint:
    """<<Value Object>> The hash two operations share when their whitespace-collapsed text is the same, which the
    duplication rule compares."""

    def __init__(self, text: str) -> None:
        self._normalized = re.sub(r"\s+", " ", text.strip())

    def of_body(self) -> str:
        """The fingerprint of a body's statements; none for a body too short for two copies of it to be a duplication."""
        return self._hash() if len(self._normalized) >= _MIN_FINGERPRINTED_CHARACTERS else ""

    def of_span(self) -> str:
        """The fingerprint of a whole source span, for a parser that took none of the body; none for an empty span."""
        return self._hash() if self._normalized else ""

    def _hash(self) -> str:
        return hashlib.sha256(self._normalized.encode()).hexdigest()[:_FINGERPRINT_DIGITS]


class ClassSourceFacts:
    """The facts a class's source gives: the shape of its members, what its constructor builds, the fields it holds,
    and what the comments and bullets of the lines it spans say."""

    def __init__(self, oclass: OoadClass) -> None:
        self._class = oclass

    def facts(self) -> dict[str, Any]:
        """Each fact by the name the class keeps it under."""
        oclass = self._class
        operations = list(oclass.operations)
        constructor = next((op for op in operations if op.name in CONSTRUCTOR_NAMES), None)
        span = oclass.span
        return {
            "method_count": len(operations),
            "operation_shapes": [self._shape(op) for op in operations],
            "property_names": sorted(prop.name for prop in oclass.properties),
            "constructs": [type_name for type_name, _line in constructor.constructed_types] if constructor else [],
            "prose_comment": span.has_prose_comment(hash_only=True),
            "prototype_swap": span.prototype_swap(oclass.line or 1),
            **CardBullets(span.text).lines(),
        }

    def held_fields(self) -> dict[str, str]:
        """Each field the class holds, with its type hint: its declared properties, then the fields its constructor
        assigns (``self.name = ...``, ``this.name: Type = ...``)."""
        found = {prop.name: prop.type_hint or "" for prop in self._class.properties}
        for operation in self._class.operations:
            if operation.is_constructor:
                for name, hint in _ASSIGNED_FIELD.findall(operation.body.text):
                    found.setdefault(name, (hint or "").strip())
        return found

    def _shape(self, operation: Operation) -> dict[str, Any]:
        return {
            "name": operation.name,
            "is_property": operation.is_property or operation.is_setter,
            "is_private": operation.is_private,
            "callees": [callee for callee in operation.callees if callee],
        }


class OperationSpanFacts:
    """The facts the lines an operation spans give, beyond what its parser measured: its fingerprint when the parser
    took none, how it mixes I/O and domain work, how it raises, whether it records what it changes, and what its
    comments and bullets say."""

    def __init__(self, operation: Operation) -> None:
        self._operation = operation

    def facts(self) -> dict[str, Any]:
        """Each fact by the name the operation keeps it under."""
        operation = self._operation
        span = operation.span
        # A constructor sets up the object it builds and cannot return a record, so it is not a state change to report.
        return {
            "body_fingerprint": operation.body_fingerprint or BodyFingerprint(span.text).of_span(),
            "io_and_domain_callees": self._delegates_io_and_domain(),
            "io_and_domain": span.mixes_io_and_domain(),
            "raises_on_empty": operation.name not in _BUILDING_NAMES and span.raises_on_empty(),
            "exception_without_message": span.exception_without_message(),
            "generic_exception_message": span.generic_exception_message(),
            "mutates_without_record": not operation.is_constructor and span.mutates_without_record(),
            "prose_comment": span.has_prose_comment(),
            **CardBullets(span.text).lines(),
        }

    def _delegates_io_and_domain(self) -> bool:
        """A long operation that calls both I/O and domain calculations does two jobs, even when it only delegates."""
        if (self._operation.line_count or 0) < MIN_DELEGATION_LINES:
            return False
        return names_call_io_and_domain(self._operation.callees)
