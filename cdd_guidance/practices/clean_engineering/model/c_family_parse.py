"""The brace-language reading the TypeScript, JavaScript, and Java class models share."""
from __future__ import annotations

import re
from typing import Iterator

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    MODULE_FUNCTION_HOLDER,
    Module,
    OoadClass,
)
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import ClassHead
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.bracket_structure import BracketStructure
from cdd_guidance.practices.clean_engineering.model.type_refs import split_top_level

_CLASS_RE = re.compile(
    r"(?:export\s+)?(?:abstract\s+)?(?:public\s+|private\s+|protected\s+)?class\s+(\w+)",
)
# A member declared with no body, ending its signature with `;`: an interface's method (`draw(scale: number): void;`,
# `void draw(double scale);`) or an abstract one (`abstract area(width: number): number;`).
# Everything outside the parameter list stays on one line: the class body arrives with its nested bodies blanked to
# spaces, and a pattern free to cross lines rescans every blank line below each line start, growing with the square of
# the body.
_BODILESS_RE = re.compile(
    r"^[ \t]*(?:(?:public|protected|private|static|abstract|default|readonly)\s+)*(?:[\w<>\[\],.?]+\s+)?(\w+)\s*\(([^)]*)\)[ \t]*(?::[ \t]*([^;{=\n]+?))?[ \t]*;[ \t]*$",
    re.M,
)
_NOT_MEMBERS = frozenset({"if", "for", "while", "switch", "catch", "return", "super", "this"})
# A class's heritage clause: `extends Basket implements Auditable, ICart`.
_HERITAGE_RE = re.compile(r"\b(?:extends|implements)\s+(.+?)(?=\s+implements\b|$)", re.S)
_METHOD_RE = re.compile(
    r"(?:public|private|protected|static|async|override)?\s*"
    r"(?:public|private|protected|static|async|override)?\s*"
    r"(?:[\w<>\[\],\s?]+\s+)?"
    r"(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{;]+))?\s*\{",
)
_CTOR_RE = re.compile(r"constructor\s*\(([^)]*)\)\s*\{")
# A TypeScript constructor parameter declared with an access modifier, `private readonly page: BoardPage`, declares a
# field the class holds as well as a parameter.
_PARAMETER_PROPERTY_RE = re.compile(
    r"^\s*(?P<modifiers>(?:(?:public|private|protected|readonly|override)\s+)+)(?P<name>\w+)\??\s*(?::\s*(?P<type>[^=]+?))?\s*(?:=.*)?$",
    re.S,
)
_TOP_FN_RE = re.compile(
    r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*[^{]+)?\s*\{",
)
# A function a file defines as a top-level constant: `export const ticketOn = (page: BoardPage, name: string): TicketClient => …`.
_TOP_ARROW_RE = re.compile(
    r"^(?:export\s+)?const\s+(\w+)\s*(?::[^=\n]+)?=\s*(?:async\s*)?\(([^)]*)\)\s*(?::\s*([^=\n]+?))?\s*=>\s*",
    re.M,
)
# A field a constructor function assigns on the object it builds: `this.stages = stages`.
_THIS_FIELD_RE = re.compile(r"\bthis\.\w+\s*=(?!=)")
_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
# A name after ``new`` is constructed, not called.
_CONSTRUCTION_RE = re.compile(r"\bnew\s+$")
_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
# A comment or a string, read left to right so a `//` inside a string, or a quote inside a comment, stays inside it.
_COMMENT_OR_STRING_RE = re.compile(r"//[^\n]*|/\*.*?\*/|" + _STRING_RE.pattern, re.S)
# A declared field, `name: Type;` or `name: Type = value;`, with its modifiers. Like `_BODILESS_RE`, its start stays on
# its own line.
_FIELD_RE = re.compile(
    r"^[ \t]*(?P<modifiers>(?:(?:public|private|protected|readonly|static|declare|override)\s+)*)(?P<name>\w+)\s*:\s*(?P<type>[^;=\n]+?)(?:\s*=\s*[^;\n]*)?\s*;",
    re.M,
)
_ASSIGN_FIELD_RE = re.compile(
    r"^[ \t]*(?P<modifiers>(?:(?:public|private|protected|readonly|static|declare|override)\s+)+)(?P<name>\w+)\s*=",
    re.M,
)
# Names a method header pattern also matches that declare no method: control statements, and the constructor, which
# the constructor pattern reads.
_NOT_METHOD_NAMES = frozenset({"if", "for", "while", "switch", "catch", "class", "constructor"})
# How far before a method's header its modifiers (`private static`) can sit.
_MODIFIER_LOOKBACK = 24
_GETTER_OR_SETTER_RE = re.compile(r"\b[gs]et\s+\w+\s*\(")
_STATIC_RE = re.compile(r"\bstatic\b")
_PRIVATE_RE = re.compile(r"\bprivate\b")


class CFamilyParse:
    """The reading every brace-language class model shares: TypeScript, JavaScript, and Java. The model it is mixed
    into holds the language it reads and fills its own modules, classes, and members from the text."""

    language: CodeLanguage
    modules: list
    module_type: type
    class_type: type
    operation_type: type
    property_type: type

    def parse(self, text: str) -> "CFamilyParse":
        """Read the text's classes and top-level functions into this model's one module, and return the model. The
        module keeps the text, and each class and operation the lines it spans."""
        self._text = text
        self._class_heads = self._read_class_heads()
        self.modules = []
        module = self.module_type(name="", sequential_order=1)
        module.preamble = self._read_preamble()
        self._append_classes(module)
        self._attach_top_level(module)
        module.source_facts.take_lines(text)
        self._file_module = module
        if module.classes:
            self.modules.append(module)
        return self

    def _read_class_heads(self) -> list[re.Match]:
        """Each `class Name` the code declares. The search reads the text with its comments and strings blanked, so
        a comment such as `so this class names none` declares no class `names`; the offsets match the text."""
        code = _COMMENT_OR_STRING_RE.sub(lambda found: re.sub(r"[^\n]", " ", found.group(0)), self._text)
        return list(_CLASS_RE.finditer(code))

    def _read_preamble(self) -> CodeBody:
        """Imports and constants above the first class, as written."""
        if not self._class_heads:
            return CodeBody()
        line_start = self._text.rfind("\n", 0, self._class_heads[0].start()) + 1
        return CodeBody(self._text[:line_start].rstrip(), self.language)

    def _append_classes(self, module: Module) -> None:
        for match in self._class_heads:
            body, body_start = self._brace_body(self._text, self._body_open(match.end()))
            if body is None:
                continue
            self._class_body, self._body_start = body, body_start
            module.classes.append(self._read_class(match, len(module.classes) + 1))

    def _read_class(self, match: re.Match, class_order: int) -> OoadClass:
        """The class declared at match, whose body this parse holds, with its head, heritage, and members."""
        head = ClassHead.above(self._text[: match.start()])
        oclass = self.class_type(name=match.group(1), sequential_order=class_order)
        oclass.line = self._line_at(self._text, match.start())
        head.documented.describe(oclass)
        oclass.stereotypes = head.stereotypes
        oclass.end_line = self._line_at(self._text, self._body_start + len(self._class_body))
        oclass.bases = self._bases(self._text[match.end() : self._body_start]) + head.implemented
        self._read_members(oclass)
        return oclass

    def _read_members(self, oclass: OoadClass) -> None:
        """The operations and fields the class body declares, measured once the class holds them."""
        oclass.operations = self._methods_from_body(oclass.name) + self._bodiless_members()
        self._prepend_constructors(oclass)
        oclass.properties = self._fields_from_body()
        self._derive_member_relationships(oclass)
        self._load_body_facts(oclass)

    def _bases(self, heritage: str) -> list[str]:
        """Every class the heritage clause between the name and the body extends or implements."""
        clause = heritage.strip().rstrip("{").strip()
        return [
            base.strip()
            for names in _HERITAGE_RE.findall(clause)
            for base in split_top_level(names)
            if base.strip()
        ]

    def _prepend_constructors(self, oclass: OoadClass) -> None:
        for ctor in _CTOR_RE.finditer(self._class_body):
            ctor_body, _rel = self._brace_body(self._class_body, ctor.end() - 1)
            if ctor_body is None:
                continue
            operation = self._declared_operation("constructor", ctor.group(1))
            operation.line = self._line_at(self._text, self._body_start + ctor.start())
            self._apply_method_end_line(operation, ctor.end() - 1)
            oclass.operations.insert(0, self._operation_from_body(operation, ctor_body))

    def _attach_top_level(self, module: Module) -> None:
        top_ops = self._top_level_functions()
        if not top_ops:
            return
        holder = self.class_type(name=MODULE_FUNCTION_HOLDER, sequential_order=len(module.classes) + 1)
        holder.line = 1
        holder.end_line = 1
        holder.operations = top_ops
        self._load_body_facts(holder)
        module.classes.append(holder)

    def _top_level_functions(self) -> list[Operation]:
        class_spans = self._class_spans()
        functions = [self._function_operation(match) for match in self._outside(_TOP_FN_RE.finditer(self._text), class_spans)]
        arrows = [self._arrow_operation(match) for match in self._outside(_TOP_ARROW_RE.finditer(self._text), class_spans)]
        found = sorted([operation for operation in functions if operation is not None] + arrows, key=lambda operation: operation.line)
        for operation in found:
            operation.is_private = not self._is_exported(operation.name)
        return found

    def _is_exported(self, name: str) -> bool:
        """True for a top-level function its file exports: `export function name`, `export const name =`, `export
        default function name`, a name in an `export { ... }` list, or a CommonJS `module.exports` naming it. Any other
        is private to its file."""
        word = re.escape(name)
        exported = (
            rf"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|const)\s+{word}\b",
            rf"\bexport\s*\{{[^}}]*\b{word}\b[^}}]*\}}",
            rf"\bmodule\.exports\b[^;]*\b{word}\b",
            rf"\bexports\.{word}\s*=",
        )
        return any(re.search(pattern, self._text) for pattern in exported)

    def _outside(self, matches: Iterator[re.Match], class_spans: list[tuple[int, int]]) -> list[re.Match]:
        """The matches that start outside every class body: a class's methods are no top-level functions."""
        return [match for match in matches if not any(start <= match.start() <= end for start, end in class_spans)]

    def _function_operation(self, match: re.Match) -> Operation | None:
        """The top-level `function` declared at match; None when its braces never close."""
        body, body_start = self._brace_body(self._text, match.end() - 1)
        if body is None:
            return None
        operation = self._declared_operation(match.group(1), match.group(2) or "")
        operation.line = self._line_at(self._text, match.start())
        operation.end_line = self._line_at(self._text, body_start + len(body))
        operation.is_constructor_function = self._is_constructor_function(match.group(1), body)
        return self._operation_from_body(operation, body)

    def _is_constructor_function(self, name: str, body: str) -> bool:
        """True for an old-style JavaScript constructor: a capitalised function that assigns `this.` fields and that
        its file calls with `new`."""
        return (
            name[:1].isupper()
            and _THIS_FIELD_RE.search(body) is not None
            and re.search(rf"\bnew\s+{re.escape(name)}\s*\(", self._text) is not None
        )

    def _arrow_operation(self, match: re.Match) -> Operation:
        """The top-level constant arrow function declared at match."""
        body = self._arrow_body(match.end())
        operation = self._declared_operation(match.group(1), match.group(2) or "", (match.group(3) or "").strip())
        operation.line = self._line_at(self._text, match.start())
        operation.end_line = self._line_at(self._text, self._text.find(body, match.end()) + len(body))
        return self._operation_from_body(operation, body)

    def _arrow_body(self, start: int) -> str:
        """An arrow function's body: its braces when it has them, else the expression on the rest of its line."""
        if self._text.startswith("{", start):
            body, _rel = self._brace_body(self._text, start)
            if body is not None:
                return body
        line_end = self._text.find("\n", start)
        return self._text[start : line_end if line_end >= 0 else len(self._text)]

    def _class_spans(self) -> list[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        for match in self._class_heads:
            body, body_start = self._brace_body(self._text, self._body_open(match.end()))
            if body is not None:
                spans.append((body_start, body_start + len(body)))
        return spans

    def _methods_from_body(self, class_name: str) -> list[Operation]:
        operations: list[Operation] = []
        position = 0
        while (match := _METHOD_RE.search(self._class_body, position)) is not None:
            method_body, body_start = self._method_body(match)
            if method_body is None:
                position = match.end(1)
                continue
            # Reading on after the body keeps a statement inside it, such as `for (...) {`, from being taken for the next header.
            position = body_start + len(method_body) + 1
            operations.append(self._method(match, method_body, class_name))
        return operations

    def _method_body(self, match: re.Match) -> tuple[str | None, int]:
        """The braces of the method whose header is match; none for a header that declares no method."""
        name_start = match.start(1)
        # A name after a dot is a call on something (`this.store.change(`), not a method this class declares. The
        # check reads the character before the name, since a match can open on the full stop ending a comment above.
        if (name_start > 0 and self._class_body[name_start - 1] == ".") or match.group(1) in _NOT_METHOD_NAMES:
            return None, -1
        return self._brace_body(self._class_body, match.end() - 1)

    def _method(self, match: re.Match, method_body: str, class_name: str) -> Operation:
        """The method whose header is match, named constructor when it carries its class's name."""
        name = match.group(1)
        operation = self._declared_operation(
            "constructor" if class_name and name == class_name else name, match.group(2) or "", (match.group(3) or "").strip()
        )
        header = match.group(0)
        header_start = match.start() + len(header) - len(header.lstrip())
        operation.line = self._line_at(self._text, self._body_start + header_start)
        self._apply_method_end_line(operation, match.end() - 1)
        filled = self._operation_from_body(operation, method_body)
        self._read_modifiers(filled, match)
        return filled

    def _read_modifiers(self, operation: Operation, match: re.Match) -> None:
        """Whether the method is an accessor, static, or private, as its header and the words before it say."""
        prefix = self._class_body[max(0, match.start() - _MODIFIER_LOOKBACK) : match.start()]
        header = match.group(0)
        if _GETTER_OR_SETTER_RE.search(header):
            operation.is_property = True
        operation.is_static = bool(_STATIC_RE.search(prefix) or _STATIC_RE.search(header))
        # Only the method's own line can declare it private: a `private` further up belongs to another member.
        own_line = prefix.rsplit("\n", 1)[-1] + header.split("(", 1)[0]
        operation.is_private = bool(_PRIVATE_RE.search(own_line))

    def _bodiless_members(self) -> list[Operation]:
        """The members the class declares with no body, on lines of its body's top level: an interface's methods and
        its abstract ones. They call nothing: a class that implements one gives it its code."""
        operations: list[Operation] = []
        code = _COMMENT_OR_STRING_RE.sub(lambda found: re.sub(r"[^\n]", " ", found.group(0)), self._class_body)
        for match in _BODILESS_RE.finditer(self._top_level(code)):
            if match.group(1) in _NOT_MEMBERS:
                continue
            operation = self._declared_operation(match.group(1), match.group(2) or "", (match.group(3) or "").strip())
            operation.line = self._line_at(self._text, self._body_start + match.start(1))
            operation.end_line = operation.line
            operations.append(self._operation_from_body(operation, ""))
        return operations

    def _declared_operation(self, name: str, parameters: str, return_type: str = "") -> Operation:
        """An operation of this language's kind named name, with the parameters its header lists between parentheses."""
        operation = self.operation_type(name, return_type=return_type)
        operation.take_parameters(self._split_params(parameters))
        return operation

    def _operation_from_body(self, operation: Operation, body: str) -> Operation:
        """The operation with the statements inside its braces as its body, the operations they call, and the notes
        its `//` comments give it."""
        for line in body.splitlines():
            if line.strip().startswith("//"):
                operation.add_invariant(line.strip()[2:].strip())
        operation.take_brace_body(body, self._callees(body, operation.name))
        return operation

    def _callees(self, body: str, caller: str) -> list[str]:
        """What the body calls, outside comments and strings: qualified calls such as `Ticket.load(`, then bare names
        that are neither the caller itself, a construction, nor the last part of a qualified call."""
        code_only = "\n".join(line for line in body.splitlines() if not line.strip().startswith("//"))
        stripped = _STRING_RE.sub('""', code_only)
        qualified = re.findall(r"(?<![\w.])([A-Z]\w*(?:\.[A-Za-z_]\w*)+)\s*\(", stripped)
        bare = [
            found.group(1) for found in _CALL_RE.finditer(stripped)
            if found.group(1) != caller and not _CONSTRUCTION_RE.search(stripped[: found.start()])
        ]
        suffixes = {item.split(".")[-1] for item in qualified}
        return qualified + [name for name in bare if name not in suffixes]

    def _load_body_facts(self, oclass: OoadClass) -> None:
        """Measure each operation's body once its class holds it, so the operation reads its owner itself."""
        for operation in oclass.operations:
            operation.load_brace_body_facts()

    def _apply_method_end_line(self, operation: Operation, search_from: int) -> None:
        brace_open = self._class_body.find("{", search_from)
        if brace_open < 0:
            return
        close_index = BracketStructure(self._class_body).closing_bracket(brace_open)
        if close_index is not None:
            operation.end_line = self._line_at(self._text, self._body_start + close_index)

    def _split_params(self, raw: str) -> list[str]:
        if not raw.strip():
            return []
        return [parameter for parameter in (self._parameter(part) for part in split_top_level(raw)) if parameter]

    def _parameter(self, part: str) -> str | None:
        """One parameter as a model line writes it, `name: Type`, without its default or access modifier; None for a
        receiver such as `this` or a part that names no parameter."""
        default_at = BracketStructure(part).top_level_index("=")
        if default_at >= 0:
            part = part[:default_at].strip()
        part = re.sub(r"^\s*(public|private|protected|final|readonly)\s+", "", part)
        hint_at = BracketStructure(part).top_level_index(":")
        if hint_at >= 0:
            name, type_hint = part[:hint_at].strip().split()[-1], part[hint_at + 1 :].strip()
        else:
            tokens = part.split()
            name, type_hint = (tokens[-1] if tokens else part), ""
        name = name.lstrip("@")
        if not name or name in {"this", "self"} or not re.match(r"^[\w$]+\??$", name):
            return None
        return f"{name}: {type_hint}" if type_hint else name

    def _fields_from_body(self) -> list[Property]:
        """Each field the class body declares, with its line, in the order it declares them: typed declarations first,
        then fields only an assignment with a modifier declares."""
        outside = self._top_level(self._class_body)
        fields = self._declared_fields(outside)
        seen = {field.name for field in fields}
        for match in _ASSIGN_FIELD_RE.finditer(outside):
            if match.group("name") not in seen:
                seen.add(match.group("name"))
                fields.append(self._field(match, len(fields) + 1))
        for field in self._parameter_properties(len(fields)):
            if field.name not in seen:
                seen.add(field.name)
                fields.append(field)
        return fields

    def _parameter_properties(self, declared: int) -> list[Property]:
        """The fields the constructors' parameter properties declare (`constructor(private readonly page: BoardPage)`),
        numbered after the ``declared`` fields the body already declares."""
        fields: list[Property] = []
        for ctor in _CTOR_RE.finditer(self._class_body):
            for part in split_top_level(ctor.group(1)):
                match = _PARAMETER_PROPERTY_RE.match(part)
                if match:
                    fields.append(self._parameter_property(match, ctor.start(1), declared + len(fields) + 1))
        return fields

    def _parameter_property(self, match: re.Match, list_start: int, order: int) -> Property:
        """The field one parameter property declares, on the line of the constructor's parameter list."""
        field = self.property_type(name=match.group("name"), sequential_order=order, type_hint=(match.group("type") or "").strip())
        field.line = self._line_at(self._text, self._body_start + list_start)
        return field

    def _declared_fields(self, outside: str) -> list[Property]:
        """The fields declared with a type, `name: Type;`, each with the `//` notes right above it."""
        fields: list[Property] = []
        seen: set[str] = set()
        cursor = 0
        for match in _FIELD_RE.finditer(outside):
            if match.group("name") in seen:
                continue
            seen.add(match.group("name"))
            field = self._field(match, len(fields) + 1)
            for note in self._comments_above(outside[cursor : match.start()]):
                field.take_note(note)
            fields.append(field)
            cursor = match.end()
        return fields

    def _field(self, match: re.Match, order: int) -> Property:
        """The field a declaration match reads: its name, its type when it is written, its line, and whether it is
        static."""
        type_hint = (match.groupdict().get("type") or "").strip()
        field = self.property_type(name=match.group("name"), sequential_order=order, type_hint=type_hint)
        field.line = self._line_at(self._text, self._body_start + match.start("name"))
        field.is_static = "static" in match.group("modifiers").split()
        return field

    def _comments_above(self, prefix: str) -> list[str]:
        """// lines that sit immediately above a field. A blank line ends the run."""
        notes: list[str] = []
        for line in reversed(prefix.splitlines()):
            stripped = line.strip()
            if not stripped:
                if notes:
                    break
                continue
            if not stripped.startswith("//"):
                break
            notes.append(stripped[2:].strip())
        notes.reverse()
        return notes

    def _derive_member_relationships(self, oclass: OoadClass) -> None:
        """A field relates only when its type names a domain class."""
        for prop in oclass.properties:
            prop.arrow.derive()

    def _body_open(self, after: int) -> int:
        """Where the class body opens: the first `{` after the class name outside the type arguments of its heritage
        clause, whose braces (`extends Component<{ children: ReactNode }>`) open no body; the text's end for none."""
        depth = 0
        for index in range(after, len(self._text)):
            char = self._text[index]
            if char == "{" and not depth:
                return index
            depth += (char == "<") - (char == ">" and depth > 0)
        return len(self._text)

    def _brace_body(self, text: str, open_index: int) -> tuple[str | None, int]:
        """The text inside the first `{` at or after open_index and the `}` that closes it, with where it starts."""
        brace = text.find("{", open_index)
        body = BracketStructure(text).braced(brace) if brace >= 0 else None
        return (body, brace + 1) if body is not None else (None, -1)

    def _line_at(self, text: str, index: int) -> int:
        return text.count("\n", 0, index) + 1

    def _top_level(self, body: str) -> str:
        """body with everything inside its braces blanked, every line kept where it is, so only its top level is read."""
        depth, kept = 0, []
        for char in body:
            depth += char == "{"
            kept.append(char if depth == 0 or char == "\n" else " ")
            depth -= char == "}" and depth > 0
        return "".join(kept)

