"""The facts a class's or an operation's source gives the rules, worked out apart from the graph nodes that keep them:
a node keeps what these find as its own graph facts, so a rule reads them from a node read now or read back from a
saved graph alike."""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING, Callable, TypedDict

from cdd_guidance.practices.source_code import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.source_code import SourceText
from cdd_guidance.practices.clean_engineering.model.operation_metrics import MIN_DELEGATION_LINES, CardBullets

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
    from cdd_guidance.practices.clean_engineering.model.code_class_model import CodeClass
    from cdd_guidance.practices.clean_engineering.model.operation import Operation


class OperationShape(TypedDict):
    """<<Value Object>> What a class read from code saves of each of its operations: its name, whether it reads or
    sets a property, whether its language's keyword makes it private, and the operations it calls. A getter is a
    property node in the graph, so a class's own shapes are where a rule finds its getters among its operations."""

    name: str
    is_property: bool
    is_private: bool
    callees: list[str]

# `self.column_name = ...` or `this.columnName: string = ...` in a constructor: a field the class holds.
_ASSIGNED_FIELD = re.compile(r"(?:self|this)\.(\w+)\s*(?::\s*([^=\n]+?))?\s*=(?!=)")
# The same assignment with what it assigns, as far as the line holds it: `self.isbn = isbn`.
_ASSIGNED_FROM = re.compile(r"(?:self|this)\.(\w+)\s*(?::\s*([^=\n]+?))?\s*=(?!=)\s*([^;\n]*)")
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
    """The facts a class's source gives: the lines of its file it spans, the shape of its members, what its
    constructor builds, the fields it holds, and what the comments and bullets of those lines say. Its class makes it
    once and keeps it (``oclass.source_facts``)."""

    def __init__(self, oclass: OoadClass) -> None:
        self._class = oclass
        # The lines of its file the class spans, empty until its parser keeps them (take_lines).
        self.span = SourceText("")

    def take_lines(self, lines: list[str]) -> None:
        """Keep the lines of its file the class spans, from its line to its end line, and each operation's."""
        oclass = self._class
        start = oclass.line or 1
        self.span = SourceText("\n".join(lines[start - 1 : oclass.end_line or start]))
        for operation in oclass.operations:
            operation.source_facts.take_lines(lines)

    def load(self) -> None:
        """Keep the facts the lines it spans give in the class's own fields, which save with the graph, so a rule reads
        them from a class read now or read back from a saved graph alike: the bold bullets a markdown card writes."""
        bullets = CardBullets(self.span.text)
        self._class.bold_interaction_lines = bullets.interaction_lines
        self._class.bold_invariant_lines = bullets.invariant_lines

    def held_fields(self) -> dict[str, str]:
        """Each field the class holds, with its type hint: its declared properties, then the fields its constructor
        assigns (``self.name = ...``, ``this.name: Type = ...``)."""
        found = {prop.name: prop.type_hint or "" for prop in self._class.properties}
        for operation in self._class.operations:
            if operation.is_constructor:
                for name, hint in _ASSIGNED_FIELD.findall(operation.body.text):
                    found.setdefault(name, (hint or "").strip())
        return found

    def constructor_fields(self) -> list[Property]:
        """A property for each public field the constructor assigns that the class does not declare, in the order it
        assigns them, each at the line that assigns it: typed as the assignment writes it, else as the parameter it is
        assigned from."""
        return self._fields_from(self._assignments_in)

    def assigned_fields(self) -> list[Property]:
        """The properties ``constructor_fields`` gives, read from the constructor's body rather than the lines of the
        class's file: a class carried into another language has a body, and no lines of a file of its own."""
        return self._fields_from(lambda operation: [(0, *found) for found in _ASSIGNED_FROM.findall(operation.body.text)])

    def _fields_from(self, assignments: "Callable[[Operation], list[tuple[int, str, str, str]]]") -> list[Property]:
        """A property for each public field the constructor's assignments set that the class does not declare."""
        declared = {prop.name for prop in self._class.properties}
        found: dict[str, Property] = {}
        for operation in (item for item in self._class.operations if item.is_constructor):
            hints = {parameter.name: parameter.type_hint for parameter in operation.parameters}
            for line, name, hint, value in assignments(operation):
                if name in declared or name in found or name.startswith("_"):
                    continue
                found[name] = Property(name, len(declared) + len(found) + 1, (hint or hints.get(value.strip(), "") or "").strip())
                found[name].line = line
        return list(found.values())

    def _assignments_in(self, operation: Operation) -> list[tuple[int, str, str, str]]:
        """Each field the operation's lines assign, in the order they assign them: the line's number, the field's name,
        the type the assignment writes, and what it assigns."""
        return [(line, *assigned) for line, text in self._lines_of(operation) for assigned in _ASSIGNED_FROM.findall(text)]

    def _lines_of(self, operation: Operation) -> list[tuple[int, str]]:
        """Each line of its file the operation spans, with its number, from the lines the class keeps."""
        first = self._class.line or 1
        start, end = operation.source_lines
        lines = self.span.text.split("\n")
        return [(number, lines[number - first]) for number in range(start, end + 1) if 0 <= number - first < len(lines)]


class CodeClassSourceFacts(ClassSourceFacts):
    """The facts the source of a class read from code gives, beyond a card's bullets: the measures of its code, which it
    keeps in the fields only a class read from code declares. A class read from a markdown model document has none of
    them, so no rule that measures code ever measures one. Only a class read from code makes one."""

    _class: CodeClass

    def load(self) -> None:
        """Keep the measures of its code in the class's own fields, as well as what every class's lines give."""
        super().load()
        oclass = self._class
        operations = list(oclass.operations)
        constructor = next((op for op in operations if op.is_constructor), None)
        oclass.method_count = len(operations)
        oclass.operation_shapes = [self._shape(op) for op in operations]
        oclass.property_names = sorted(prop.name for prop in oclass.properties)
        oclass.constructs = [type_name for type_name, _line in constructor.constructed_types] if constructor else []
        oclass.prose_comment = self.span.has_prose_comment(hash_only=True)
        oclass.prototype_swap = self.span.prototype_swap(oclass.line or 1)

    def _shape(self, operation: Operation) -> OperationShape:
        return {
            "name": operation.name,
            "is_property": operation.is_property or operation.is_setter,
            "is_private": operation.is_private,
            "callees": [callee for callee in operation.callees if callee],
        }


class OperationSourceFacts:
    """What an operation's source says, as its parser reads it: the statements of its body and their fingerprint, the
    lines of its file it spans, and the facts those lines give beyond what the parser measured: how it mixes I/O and
    domain work, how it raises, whether it records what it changes, and what its comments and bullets say. Its
    operation makes it once and keeps it (``operation.source_facts``)."""

    def __init__(self, operation: Operation) -> None:
        self._operation = operation
        # The lines of its file the operation spans, empty until its parser keeps them (take_lines).
        self.span = SourceText("")

    def take_body(self, text: str, language: CodeLanguage) -> None:
        """Keep the statements its parser read, in the language they are written in, as the operation's body. A body
        that is only what a render wrote from the model (its notes, its calls, then the line that fails until it is
        written) is no body: the operation keeps those calls, as written, as the ones it makes, and its notes as its
        parser read them, so a render into another language writes them in that language."""
        calls = language.scaffold_calls(text)
        if calls is None:
            self._operation.body = CodeBody(text, language)
            return
        self._operation.body = CodeBody()
        self._operation.callees = calls

    def take_body_fingerprint(self, body: str) -> None:
        """Keep the fingerprint of its body text, which another operation with the same whitespace-collapsed body
        shares; none for a body too short for two copies of it to be a duplication."""
        self._operation.body_fingerprint = BodyFingerprint(body).of_body()

    def take_lines(self, lines: list[str]) -> None:
        """Keep the lines of its file the operation spans."""
        start, end = self._operation.source_lines
        self.span = SourceText("\n".join(lines[start - 1 : end]))

    def load(self) -> None:
        """Keep the facts the operation's source span carries, beyond what the parser measured, in the operation's own
        fields, which save with the graph."""
        operation = self._operation
        span = self.span
        operation.body_fingerprint = operation.body_fingerprint or BodyFingerprint(span.text).of_span()
        operation.io_and_domain_callees = self._delegates_io_and_domain()
        operation.io_and_domain = span.mixes_io_and_domain()
        operation.raises_on_empty = operation.name not in _BUILDING_NAMES and span.failures.raises_on_empty()
        operation.exception_without_message = span.failures.exception_without_message()
        operation.generic_exception_message = span.failures.generic_exception_message()
        # A constructor, or a JavaScript constructor function, sets up the object it builds and cannot return a record,
        # so it is not a state change to report.
        operation.mutates_without_record = not (operation.is_constructor or operation.is_constructor_function) and span.mutates_without_record()
        operation.prose_comment = span.has_prose_comment()
        bullets = CardBullets(span.text)
        operation.bold_interaction_lines = bullets.interaction_lines
        operation.bold_invariant_lines = bullets.invariant_lines

    def _delegates_io_and_domain(self) -> bool:
        """A long operation that calls both I/O, such as `save`, and a domain calculation, such as `total`, does two
        jobs, even when it only delegates: the last part of each callee's name is the operation it calls."""
        if (self._operation.line_count or 0) < MIN_DELEGATION_LINES:
            return False
        called = "\n".join(f"{callee.split('.')[-1]}(" for callee in self._operation.callees if callee)
        return SourceText(called).calls_io_and_domain()
