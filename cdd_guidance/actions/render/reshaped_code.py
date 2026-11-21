"""A render written onto a code file that is already there: the file takes the new shape and loses nothing.

A code file holds what its model does not: bodies, comments, imports, helpers, decorators, the text between members.
So a render onto a file already there never replaces it. It edits the file:

- A class or an operation the source has and the file lacks is **added**, as the render wrote it, empty: an operation
  at the end of its class, a class after the classes the file holds.
- An operation the file has and the source lacks is **kept**: it stays in its class, moved to the end under a line that
  says it is no longer in the model and where it was, with the comments and decorators written above it. It is still
  code, so the file still runs; a person or an agent moves its body into the member that replaced it and then deletes
  it. A class only the file holds stays where it is, since a file often holds classes its model does not, such as an
  exception. So does a member whose name starts with an underscore, a constructor, and everything outside a class.
- A property the source has and the file lacks is **added** to its class, after the properties the class holds, else
  above its operations.
- A member both hold stays exactly as the file has it, opening line included, so nothing a person wrote is replaced.
  When the render writes that opening line otherwise, such as an operation that now takes a tax, the member is named
  as **changed** with the render's line, for whoever brings the file's line up to date.

A format that knows its files better writes the new shape onto the existing text itself: its adapter answers
``reshape(rendered, existing)`` with a *Reshaped* (harness/guidance), the text and the members it kept and added. A file
whose members this reader does not find, such as a spec of nested ``with`` blocks, falls back to the rendered shape
with the lines only the file holds set apart below it as comments.

Whichever wrote the text, it is checked: every line of the old file that carried content must be in the new text, else
*RenderWouldLoseContent* names the lines missing and the file is left as it was.
"""

from __future__ import annotations

import re
from typing import Callable

from harness.guidance.practice_formats import NO_LONGER_IN_MODEL, Reshaped
from harness.markdown.format import Format

_PYTHON = "python"
_PYTHON_MEMBER = re.compile(r"^(\s*)(?:async\s+)?(def|class)\s+(\w+)")
_BRACE_CLASS = re.compile(r"^(\s*)(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+)")
_BRACE_FUNCTION = re.compile(r"^(\s*)(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s+(\w+)")
_BRACE_OPERATION = re.compile(r"^(\s*)(?:(?:public|private|protected|static|async|override|readonly|get|set)\s+)*(#?\w+)\s*(?:<[^>]*>)?\(")
# Words that open a statement with a parenthesis and are no operation.
_PYTHON_PROPERTY = re.compile(r"^(\s+)(\w+)\s*:\s*[^=]+?(?:\s*=.*)?$")
_BRACE_PROPERTY = re.compile(r"^(\s+)(?:(?:public|private|protected|static|readonly|declare)\s+)*(#?\w+)[?!]?\s*(?::[^=;]+)?(?:=[^;]*)?;\s*$")
_STATEMENTS = frozenset({"if", "for", "while", "switch", "catch", "return", "super", "function", "await", "new", "throw"})
# The members a model does not name: a constructor, and a helper whose name starts with an underscore or a hash.
_CONSTRUCTORS = frozenset({"__init__", "constructor"})

Reshape = Callable[[str, str], Reshaped]
"""A format's own way to write a rendered shape onto existing text: ``reshape(rendered, existing)``."""


class RenderWouldLoseContent(ValueError):
    """A render onto a file already there made text that lacks lines the file held, so it was not written."""

    def __init__(self, missing: list[str]) -> None:
        listed = "; ".join(line.strip() for line in missing)
        super().__init__(f"The render would lose {len(missing)} line(s) the file holds, so the file was left as it was: {listed}")
        self.missing = list(missing)


class Member:
    """One class, function or operation of a code file: its name, the lines it covers with the comments and decorators
    written above it, and, for a class, its operations."""

    def __init__(self, name: str, lead: int, start: int, end: int, indent: str) -> None:
        self.name = name
        # The first line of the comments and decorators above it, its own first line, and the line after its last.
        self.lead = lead
        self.start = start
        self.end = end
        self.indent = indent
        self.operations: list[Member] = []
        self.is_class = False
        # For a class: the first line of its body, and the line each property it declares is written on, by name.
        self.body = start + 1
        self.properties: dict[str, int] = {}

    @property
    def is_named_by_a_model(self) -> bool:
        return self.name not in _CONSTRUCTORS and not self.name.startswith(("_", "#"))


class CodeOutline:
    """The classes and functions one code text holds, each with the lines it covers: Python by its indentation,
    TypeScript and JavaScript by their braces. It reads only what a render needs to place members; a brace inside a
    string or a comment is counted like any other, which a file written by a render or kept tidy does not trip."""

    def __init__(self, text: str, language: Format) -> None:
        self.lines = text.splitlines()
        self._is_python = language.name == _PYTHON
        self.members = self._python_members(0, len(self.lines), "") if self._is_python else self._brace_members()
        # A Python file's own members open at no indent; a class's operations open at the first indent found in it.

    @property
    def classes(self) -> dict[str, Member]:
        return {member.name: member for member in self.members if member.is_class}

    def _lead_of(self, start: int, indent: str, floor: int) -> int:
        """The first of the comment and decorator lines written directly above the line at start, at its indent."""
        lead = start
        while lead > floor and self.lines[lead - 1].startswith(indent) and self.lines[lead - 1][len(indent):].startswith(("#", "@", "//", "/*", "*")):
            lead -= 1
        return lead

    def _python_members(self, first: int, last: int, indent: str | None) -> list[Member]:
        """The members whose opening lines sit between first and last at indent; with none given, at the indent of the
        first one found there, which is how deep a class writes its operations."""
        found: list[Member] = []
        index = first
        while index < last:
            opened = _PYTHON_MEMBER.match(self.lines[index])
            wanted = indent if indent is not None else (found[0].indent if found else None)
            if opened is None or (wanted is not None and opened.group(1) != wanted):
                index += 1
                continue
            member = self._python_member(index, last, opened, first)
            found.append(member)
            index = member.end
        return found

    def _python_member(self, start: int, last: int, opened: re.Match[str], floor: int) -> Member:
        indent = opened.group(1)
        body = self._python_opening_end(start)
        end = body
        for index in range(body, last):
            line = self.lines[index]
            if line.strip() and len(line) - len(line.lstrip()) <= len(indent):
                break
            if line.strip():
                end = index + 1
        member = Member(opened.group(3), self._lead_of(start, indent, floor), start, end, indent)
        if opened.group(2) == "class":
            member.is_class = True
            member.body = body
            member.operations = self._python_members(body, end, None)
            member.properties = self._properties_of(member, _PYTHON_PROPERTY)
        return member

    def _python_opening_end(self, start: int) -> int:
        """The line after a member's opening lines, which end where the parentheses are closed and a colon ends the line."""
        depth = 0
        for index in range(start, len(self.lines)):
            line = self.lines[index]
            depth += line.count("(") + line.count("[") - line.count(")") - line.count("]")
            if depth <= 0 and line.rstrip().endswith(":"):
                return index + 1
        return start + 1

    def _properties_of(self, owner: Member, written_as: re.Pattern[str]) -> dict[str, int]:
        """The line each property the class declares is written on: a line of its body outside its operations that
        names a property, at the indent of the first one found."""
        inside = {index for operation in owner.operations for index in range(operation.lead, operation.end)}
        found: dict[str, int] = {}
        indent = None
        for index in range(owner.body, owner.end):
            named = written_as.match(self.lines[index]) if index not in inside else None
            if named is not None and indent in (None, named.group(1)) and named.group(2) not in _STATEMENTS:
                indent = named.group(1)
                found.setdefault(named.group(2), index)
        return found

    def _brace_members(self) -> list[Member]:
        found: list[Member] = []
        index = 0
        while index < len(self.lines):
            opened = _BRACE_CLASS.match(self.lines[index]) or _BRACE_FUNCTION.match(self.lines[index])
            if opened is None:
                index += 1
                continue
            member = Member(opened.group(2), self._lead_of(index, opened.group(1), 0), index, self._brace_end(index), opened.group(1))
            if _BRACE_CLASS.match(self.lines[index]):
                member.is_class = True
                member.operations = self._brace_operations(member)
                member.properties = self._properties_of(member, _BRACE_PROPERTY)
            found.append(member)
            index = member.end
        return found

    def _brace_end(self, start: int) -> int:
        """The line after the one that closes the braces the member at start opens; the next line for one that opens none."""
        depth, opened = 0, False
        for index in range(start, len(self.lines)):
            line = self.lines[index]
            depth += line.count("{") - line.count("}")
            opened = opened or "{" in line
            if opened and depth <= 0:
                return index + 1
            if not opened and line.rstrip().endswith(";"):
                return index + 1
        return start + 1

    def _brace_operations(self, owner: Member) -> list[Member]:
        found: list[Member] = []
        index = owner.start + 1
        while index < owner.end - 1:
            opened = _BRACE_OPERATION.match(self.lines[index])
            if opened is None or opened.group(2) in _STATEMENTS:
                index += 1
                continue
            member = Member(opened.group(2), self._lead_of(index, opened.group(1), owner.start + 1), index, self._brace_end(index), opened.group(1))
            found.append(member)
            index = member.end
        return found


class ReshapedCode:
    """One language's way to write a rendered shape onto a code file already there, losing nothing: the format's own
    ``reshape`` when it has one, else the edit of the file described above, else the rendered shape with the file's
    own lines set apart; then the check that every line the file held is in the text."""

    def __init__(self, language: Format, reshape: Reshape | None = None) -> None:
        self._language = language
        self._reshape = reshape
        self._comment = "#" if language.name == _PYTHON else "//"

    def onto(self, existing: str, rendered: str) -> Reshaped:
        """The text of existing in the shape rendered has, with the members kept and added; raises
        *RenderWouldLoseContent* when a line existing holds is in it nowhere."""
        reshaped = self._reshape(rendered, existing) if self._reshape is not None else self._edited(existing, rendered)
        held = reshaped.text.splitlines()
        missing = [line for line in existing.splitlines() if line.strip() and not any(line.strip() in kept for kept in held)]
        if missing:
            raise RenderWouldLoseContent(missing)
        return reshaped

    def _edited(self, existing: str, rendered: str) -> Reshaped:
        file, shape = CodeOutline(existing, self._language), CodeOutline(rendered, self._language)
        if not file.classes or not shape.classes:
            return self._set_apart(existing, rendered)
        edit = _FileEdit(file, shape, self._comment)
        return Reshaped(edit.text(existing.endswith("\n")), sorted(edit.kept), sorted(edit.added), dict(sorted(edit.changed.items())))

    def _set_apart(self, existing: str, rendered: str) -> Reshaped:
        """The rendered shape, then the lines only the existing file holds as comments under one line saying so; lines
        an earlier render set apart are carried over as they are, so a second render changes nothing."""
        lines = existing.splitlines()
        marked = next((index for index, line in enumerate(lines) if NO_LONGER_IN_MODEL in line), len(lines))
        carried = lines[marked + 1:]
        shape = rendered.splitlines()
        unplaced = [line for line in lines[:marked] if line.strip() and not any(line.strip() in kept for kept in shape)]
        apart = carried + [f"{self._comment} {line}" for line in unplaced]
        if not apart:
            return Reshaped(rendered, [], [])
        heading = f"{self._comment} ---- {NO_LONGER_IN_MODEL}: the lines below were in this file and the render did not write them. Move each into the member it belongs to, then delete it. ----"
        text = "\n".join([*shape, "", heading, *apart]) + "\n"
        return Reshaped(text, [f"{len(apart)} line(s) set apart"], [])


class _FileEdit:
    """The edits that give one file the shape a render brings: operations added to its classes, operations its model
    dropped moved to the end of their class under a marking line, and classes the file lacks added after the others."""

    def __init__(self, file: CodeOutline, shape: CodeOutline, comment: str) -> None:
        self._file = file
        self._shape = shape
        self._comment = comment
        self.kept: list[str] = []
        self.added: list[str] = []
        self.changed: dict[str, str] = {}

    def text(self, ends_with_newline: bool) -> str:
        lines = list(self._file.lines)
        # From the last class up, so the lines of the classes above stay where the outline found them.
        for owner in sorted(self._file.classes.values(), key=lambda member: member.start, reverse=True):
            shaped = self._shape.classes.get(owner.name)
            if shaped is not None:
                lines[owner.start:owner.end] = self._class_lines(owner, shaped)
        lines += [line for name, shaped in self._shape.classes.items() if name not in self._file.classes for line in self._new_class(shaped)]
        return "\n".join(lines) + ("\n" if ends_with_newline else "")

    def _new_class(self, shaped: Member) -> list[str]:
        self.added += [shaped.name, *(f"{shaped.name}.{operation.name}" for operation in shaped.operations)]
        return ["", "", *self._shape.lines[shaped.lead:shaped.end]]

    def _class_lines(self, owner: Member, shaped: Member) -> list[str]:
        """The class's lines with its operations in three runs: those it keeps as they are, those the shape adds, and
        those no longer in the model, each under its marking line."""
        lines = self._file.lines
        in_shape = {operation.name for operation in shaped.operations}
        in_file = {operation.name for operation in owner.operations}
        apart = [operation for operation in owner.operations if self._is_marked(operation) or (operation.is_named_by_a_model and operation.name not in in_shape)]
        added = [operation for operation in shaped.operations if operation.name not in in_file]
        properties = [name for name in shaped.properties if name not in owner.properties]
        self.kept += [f"{owner.name}.{operation.name}" for operation in apart]
        self.added += [f"{owner.name}.{name}" for name in [*properties, *(operation.name for operation in added)]]
        self._note_changed(owner, shaped)
        if not added and not properties and all(self._is_marked(operation) for operation in apart):
            return lines[owner.start:owner.end]
        closing = self._closing_of(owner)
        moved = {index for operation in apart for index in self._lines_moved(owner, operation)}
        after = max(owner.properties.values(), default=owner.body - 1)
        declared = self._declared(owner, shaped, properties)
        staying = self._trimmed([
            written for index in range(owner.start, owner.end - len(closing)) if index not in moved
            for written in ([lines[index], *declared] if index == after else [lines[index]])
        ])
        indent = self._member_indent(owner, shaped)
        new = [line for operation in added for line in ["", *self._reindented(operation, indent)]]
        kept = [line for operation in apart for line in ["", *self._set_apart(owner, operation)]]
        return [*staying, *new, *kept, *closing]

    def _declared(self, owner: Member, shaped: Member, properties: list[str]) -> list[str]:
        """The lines that declare the properties the shape adds, at the indent the file's class gives its members,
        with a blank line after them when the class declared none before."""
        if not properties:
            return []
        indent = self._member_indent(owner, shaped)
        written = [f"{indent}{self._shape.lines[shaped.properties[name]].strip()}" for name in properties]
        return written if owner.properties else [*written, ""]

    def _member_indent(self, owner: Member, shaped: Member) -> str:
        if owner.operations:
            return owner.operations[0].indent
        return shaped.operations[0].indent if shaped.operations else owner.indent + "    "

    def _note_changed(self, owner: Member, shaped: Member) -> None:
        """Name each operation both hold whose opening line the shape writes otherwise than the file, with the shape's."""
        in_file = {operation.name: operation for operation in owner.operations}
        for operation in shaped.operations:
            held = in_file.get(operation.name)
            written = " ".join(self._shape.lines[operation.start].split())
            if held is not None and " ".join(self._file.lines[held.start].split()) != written:
                self.changed[f"{owner.name}.{operation.name}"] = written

    def _lines_moved(self, owner: Member, operation: Member) -> range:
        """The lines an operation set apart leaves: its own, with the blank lines above it, which parted it from the
        member before."""
        first = operation.lead
        while first - 1 > owner.start and not self._file.lines[first - 1].strip():
            first -= 1
        return range(first, operation.end)

    def _closing_of(self, owner: Member) -> list[str]:
        """The line that closes a class written with braces; none for one written by indentation."""
        last = self._file.lines[owner.end - 1]
        return [last] if last.strip().startswith("}") else []

    def _is_marked(self, operation: Member) -> bool:
        """Whether an earlier render set the operation apart: its marking line is among the comments above it."""
        return any(NO_LONGER_IN_MODEL in line for line in self._file.lines[operation.lead:operation.start])

    def _set_apart(self, owner: Member, operation: Member) -> list[str]:
        """The operation's own lines under its marking line: the one it already has, else one saying where it was."""
        lines = self._file.lines
        if self._is_marked(operation):
            return lines[operation.lead:operation.end]
        marking = (
            f"{operation.indent}{self._comment} ---- {NO_LONGER_IN_MODEL}: {owner.name}.{operation.name}, kept from lines "
            f"{operation.lead + 1} to {operation.end}. Move its body into the member that replaced it, then delete it. ----"
        )
        return [marking, *lines[operation.lead:operation.end]]

    def _reindented(self, operation: Member, indent: str) -> list[str]:
        """The operation as the shape wrote it, at the indent the file's class gives its operations."""
        written = self._shape.lines[operation.lead:operation.end]
        return [f"{indent}{line[len(operation.indent):]}" if line.strip() else line for line in written]

    def _trimmed(self, lines: list[str]) -> list[str]:
        while lines and not lines[-1].strip():
            lines = lines[:-1]
        return lines
