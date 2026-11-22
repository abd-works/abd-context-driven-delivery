"""Why the read cannot tell the class of a receiver a call is made on, so the calls it cannot join are counted by cause:
the receiver is an object from outside the code read (a standard-library, third-party, or built-in object, or a literal
value), no type says what it is (an untyped parameter, `Any`, or a value nothing types), or anything else, such as a
type hint naming a class no file declares."""

from __future__ import annotations

import builtins
import re
import typing
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.code_file import CodeFile
    from cdd_guidance.practices.clean_engineering.reading.graph_reading import CodeIndex

from cdd_guidance.practices.clean_engineering.model import MODULE_FUNCTION_HOLDER

# The causes of a call the read cannot join, each kept on the class as its own fact (``UNRESOLVED_CALLS_FACTS``).
ON_OUTSIDE_OBJECTS = "on_outside_objects"
ON_UNTYPED_VALUES = "on_untyped_values"
OTHERWISE = "otherwise"
UNRESOLVED_CALLS_FACTS = {cause: f"unresolved_calls_{cause}" for cause in (ON_OUTSIDE_OBJECTS, ON_UNTYPED_VALUES, OTHERWISE)}

# The hints that say a value may be anything.
_UNTYPED = frozenset({"Any", "any", "object", "Object", "unknown"})
# The hints that wrap the type that says what the value is.
_WRAPPERS = frozenset({"Optional", "Union", "Final", "ClassVar", "Annotated", "Readonly", "Promise", "Awaitable", "type", "Type"})
# The types a script has without importing them.
_SCRIPT_TYPES = frozenset({
    "string", "number", "boolean", "bigint", "symbol", "void", "never", "null", "undefined", "Array", "ReadonlyArray",
    "Record", "Map", "Set", "WeakMap", "WeakSet", "Promise", "Date", "RegExp", "Error", "JSON", "Math", "Object",
    "Function", "console", "document", "window", "process", "Buffer", "HTMLElement", "Element", "Event", "URL",
    "Response", "Request", "Headers", "Partial", "Pick", "Omit", "Required", "ReturnType", "Parameters",
})
_OUTSIDE_TYPES = frozenset(dir(builtins)) | frozenset(typing.__all__) | _SCRIPT_TYPES
_FIRST_NAME = re.compile(r"[A-Za-z_$][\w$.]*")
_INSIDE_WRAPPER = re.compile(r"^[\w.]+\s*[\[<](.*)[\]>]\s*$")
# A Python import and the names it brings: `import json`, `import numpy as np`, `from pathlib import Path, PurePath`.
_PYTHON_IMPORT = re.compile(r"(?m)^[ \t]*import[ \t]+([\w.]+)(?:[ \t]+as[ \t]+(\w+))?")
_PYTHON_FROM = re.compile(r"(?m)^[ \t]*from[ \t]+([\w.]+)[ \t]+import[ \t]+\(?([^)\n]+)")
# A script import and the module it names: `import { chromium } from 'playwright'`, `import fs from 'node:fs'`.
_SCRIPT_IMPORT = re.compile(r"""\bimport\s+(?:type\s+)?([^;'"]*?)\s+from\s+['"]([^'"]+)['"]""")
_SCRIPT_NAME = re.compile(r"(?:\bas\s+)?([A-Za-z_$][\w$]*)\s*(?:,|}|$)")
# Where a value written as a literal starts: a list, a mapping, a string, a number, or a constant.
_LITERAL = re.compile(r"""\s*(?:[\[{"'`]|f["']|-?\d|(?:True|False|None|null|undefined)\b)""")


class ReceiverCauses:
    """Why a receiver of one file's code has no class the read can tell, as that file's code says: what a type hint
    names, and what a name the code writes with no hint is. The file makes it once and keeps it
    (``CodeFile.receiver_causes``)."""

    def __init__(self, file: "CodeFile", text: str, root: Path) -> None:
        self._file = file
        self._root = root
        # The names the file imports from modules outside the code read.
        self.outside_names = self._outside_names(text)

    def of_hint(self, hint: object) -> str:
        """Why a value a type hint types has no class of the code: no hint, or one that says it may be anything, is
        untyped; one naming a built-in, standard-library, or third-party type is outside the code; any other names a
        type the read cannot reach."""
        written = str(hint or "").strip().strip("\"'").strip()
        if not written:
            return ON_UNTYPED_VALUES
        first = _FIRST_NAME.match(written)
        if first is None:
            return OTHERWISE
        name = first.group(0)
        inside = _INSIDE_WRAPPER.match(written)
        if name.rsplit(".", 1)[-1] in _WRAPPERS and inside is not None:
            return self.of_hint(inside.group(1).split(",")[0])
        if name.rsplit(".", 1)[-1] in _UNTYPED:
            return ON_UNTYPED_VALUES
        return ON_OUTSIDE_OBJECTS if self.is_outside(name) else OTHERWISE

    def is_outside(self, name: str) -> bool:
        """Whether a name the code writes is an object from outside the code read: a built-in, or a name the file
        imports from a module outside it."""
        head = name.split(".")[0]
        return head in self.outside_names or name in _OUTSIDE_TYPES or head in _OUTSIDE_TYPES

    @staticmethod
    def is_literal(code: str, start: int) -> bool:
        """Whether the expression at start is a literal value, which is a built-in object."""
        return _LITERAL.match(code, start) is not None

    def _outside_names(self, text: str) -> frozenset[str]:
        if self._file.is_script:
            return frozenset(
                found.group(1)
                for imported in _SCRIPT_IMPORT.finditer(text) if not imported.group(2).startswith((".", "@cdd/"))
                for found in _SCRIPT_NAME.finditer(imported.group(1).replace("{", ",").replace("*", ","))
            )
        names = {imported.group(2) or imported.group(1).split(".")[0] for imported in _PYTHON_IMPORT.finditer(text) if not self._in_the_code(imported.group(1))}
        for imported in _PYTHON_FROM.finditer(text):
            if not self._in_the_code(imported.group(1)):
                names.update(part.split(" as ")[-1].strip() for part in imported.group(2).split(",") if part.strip())
        return frozenset(names)

    def _in_the_code(self, module: str) -> bool:
        """Whether a Python module an import names is one of the code read: a relative import, or a module or package
        under the source root."""
        if module.startswith("."):
            return True
        path = self._root.joinpath(*module.split("."))
        return path.with_suffix(".py").is_file() or (path / "__init__.py").is_file() or path.is_dir()


class UnjoinedCalls:
    """The calls one span of a file's code makes that the read cannot join, counted by why its receiver has no class
    the read can tell: what each name the span writes with no class is (a parameter whose hint names none, or a local
    assigned what the read cannot type), what a function answers, and what a member of a class of the code holds or
    answers. A call is counted only when some class of the code declares an operation of its name, since only then
    could the read have missed an edge. The span makes one and keeps it."""

    def __init__(self, file: "CodeFile", index: "CodeIndex") -> None:
        self._file = file
        self._index = index
        self._causes = file.receiver_causes
        # Why each name the span writes has no class, by the name.
        self._unknown: dict[str, str] = {}

    def keep_parameter(self, name: str, hint: str) -> None:
        """A parameter whose hint names no class of the code, untyped when it has none."""
        self._unknown.setdefault(name, self._causes.of_hint(hint))

    def names_a_local(self, name: str) -> bool:
        """Whether name is a parameter or a local of the span whose class the read cannot tell."""
        return name in self._unknown

    def keep_local(self, name: str, cause: str) -> None:
        """A local assigned what the read cannot type, for the cause its expression gives."""
        self._unknown.setdefault(name, cause)

    def of_head(self, head: str, called: bool) -> str:
        """Why the first name of a chain has no class: what the span knows of it, else an object from outside the code,
        else, for a function the code declares, what its return type says, else, for a module variable, what its module
        assigns it, else a name the read cannot reach."""
        if head in self._unknown:
            return self._unknown[head]
        if self._causes.is_outside(head):
            return ON_OUTSIDE_OBJECTS
        if called:
            function = self._file.function_named(head)
            return self._causes.of_hint(function.get_fact("return_type") if function is not None else "")
        return self._file.module_cause(head) or OTHERWISE

    def of_member(self, holders: "list[Node]", name: str, member: "Node | None", called: bool) -> str:
        """Why what a member of holders[0] (or a class it extends, holders[1:]) answers has no class: what its return
        type, its type, or the hint its holder keeps for the field says, and for a field with no hint, what its
        constructor or initializer assigns it; a member no class of the code declares is inherited from outside the code
        when the class extends a class the read does not hold."""
        if member is not None and called and member.type == "Operation":
            return self._index.file(member.source.file).receiver_causes.of_hint(member.get_fact("return_type"))
        for holder in holders:
            fields = holder.get_fact("held_fields") or {}
            if name in fields:
                return self._field_cause(holder, name, fields[name])
        if member is not None:
            return self._index.file(member.source.file).receiver_causes.of_hint(member.get_fact("value_type"))
        held = {holder.name for holder in holders}
        written = (str(base).split("[")[0].split("<")[0].strip().rsplit(".", 1)[-1] for holder in holders for base in holder.get_fact("bases") or [])
        return ON_OUTSIDE_OBJECTS if any(base not in held for base in written) else OTHERWISE

    def _field_cause(self, holder: "Node", name: str, hint: str) -> str:
        """Why a field of holder has no class: what its hint says, or, with no hint, what is assigned to it."""
        if hint:
            return self._index.file(holder.source.file).receiver_causes.of_hint(hint)
        return self._index.answers.field_cause(holder, name) or ON_UNTYPED_VALUES

    def count(self, unresolved: dict[str, int], name: str, cause: str) -> None:
        """Count a call of name, on a receiver of no class the read can tell, under its cause."""
        if any(member.type == "Operation" and member.get_fact("owner") != MODULE_FUNCTION_HOLDER for member in self._index.members_named(name)):
            unresolved[cause] += 1
