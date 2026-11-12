"""The brace-language reading the TypeScript, JavaScript, and Java class models share."""
from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    MODULE_FUNCTION_HOLDER,
    Module,
    OoadClass,
)
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import ClassHead
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.bracket_structure import BracketStructure
from cdd_guidance.practices.clean_engineering.model.type_refs import split_top_level

_CLASS_RE = re.compile(
    r"(?:export\s+)?(?:abstract\s+)?(?:public\s+|private\s+|protected\s+)?class\s+(\w+)",
)
# A class's heritage clause: `extends Basket implements Auditable, ICart`.
_HERITAGE_RE = re.compile(r"\b(?:extends|implements)\s+(.+?)(?=\s+implements\b|$)", re.S)
_METHOD_RE = re.compile(
    r"(?:public|private|protected|static|async|override)?\s*"
    r"(?:public|private|protected|static|async|override)?\s*"
    r"(?:[\w<>\[\],\s?]+\s+)?"
    r"(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{;]+))?\s*\{",
)
_CTOR_RE = re.compile(r"constructor\s*\(([^)]*)\)\s*\{")
_TOP_FN_RE = re.compile(
    r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*[^{]+)?\s*\{",
)
# A function a file defines as a top-level constant: `export const ticketOn = (page: BoardPage, name: string): TicketClient => …`.
_TOP_ARROW_RE = re.compile(
    r"^(?:export\s+)?const\s+(\w+)\s*(?::[^=\n]+)?=\s*(?:async\s*)?\(([^)]*)\)\s*(?::\s*([^=\n]+?))?\s*=>\s*",
    re.M,
)
_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
# A name after ``new`` is constructed, not called.
_CONSTRUCTION_RE = re.compile(r"\bnew\s+$")
_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
# A comment or a string, read left to right so a `//` inside a string, or a quote inside a comment, stays inside it.
_COMMENT_OR_STRING_RE = re.compile(r"//[^\n]*|/\*.*?\*/|" + _STRING_RE.pattern, re.S)
# A declared field, `name: Type;` or `name: Type = value;`, with its modifiers.
_FIELD_RE = re.compile(
    r"^\s*((?:(?:public|private|protected|readonly|static|declare|override)\s+)*)(\w+)\s*:\s*([^;=\n]+?)(?:\s*=\s*[^;\n]*)?\s*;",
    re.M,
)
_ASSIGN_FIELD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|static|declare|override)\s+)+(\w+)\s*=",
    re.M,
)
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
        module.take_lines(text)
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
        class_order = 1
        for match in self._class_heads:
            body, body_start = self._brace_body(self._text, self._body_open(match.end()))
            if body is None:
                continue
            self._body_start = body_start
            head = ClassHead.above(self._text[: match.start()])
            oclass = self.class_type(
                name=match.group(1),
                sequential_order=class_order,
                line=self._line_at(self._text, match.start()),
            )
            head.documented.describe(oclass)
            oclass.stereotypes = head.stereotypes
            oclass.end_line = self._line_at(self._text, body_start + len(body))
            oclass.bases = self._bases(self._text[match.end() : body_start]) + head.implemented
            oclass.operations = self._methods_from_body(body, match.group(1))
            self._prepend_constructors(oclass, body)
            oclass.properties = self._fields_from_body(oclass, body)
            self._derive_member_relationships(oclass)
            self._load_body_facts(oclass)
            module.classes.append(oclass)
            class_order += 1

    def _bases(self, heritage: str) -> list[str]:
        """Every class the heritage clause between the name and the body extends or implements."""
        clause = heritage.strip().rstrip("{").strip()
        return [
            base.strip()
            for names in _HERITAGE_RE.findall(clause)
            for base in split_top_level(names)
            if base.strip()
        ]

    def _prepend_constructors(self, oclass: OoadClass, body: str) -> None:
        for ctor in _CTOR_RE.finditer(body):
            ctor_body, _rel = self._brace_body(body, ctor.end() - 1)
            if ctor_body is None:
                continue
            op = self.operation_type(name="constructor", parameters=self._split_params(ctor.group(1)))
            op.line = self._line_at(self._text, self._body_start + ctor.start())
            self._apply_method_end_line(op, body, ctor.end() - 1)
            oclass.operations.insert(0, self._operation_from_body(op, ctor_body))

    def _attach_top_level(self, module: Module) -> None:
        top_ops = self._top_level_functions()
        if not top_ops:
            return
        holder = self.class_type(name=MODULE_FUNCTION_HOLDER, sequential_order=len(module.classes) + 1, line=1)
        holder.end_line = 1
        holder.operations = top_ops
        self._load_body_facts(holder)
        module.classes.append(holder)

    def _top_level_functions(self) -> list[Operation]:
        ops: list[Operation] = []
        class_spans = self._class_spans()
        for match in _TOP_FN_RE.finditer(self._text):
            if any(start <= match.start() <= end for start, end in class_spans):
                continue
            body, body_start = self._brace_body(self._text, match.end() - 1)
            if body is None:
                continue
            op = self.operation_type(name=match.group(1), parameters=self._split_params(match.group(2) or ""))
            op.line = self._line_at(self._text, match.start())
            op.end_line = self._line_at(self._text, body_start + len(body))
            ops.append(self._operation_from_body(op, body))
        for match in _TOP_ARROW_RE.finditer(self._text):
            if any(start <= match.start() <= end for start, end in class_spans):
                continue
            body = self._arrow_body(match.end())
            op = self.operation_type(
                name=match.group(1),
                parameters=self._split_params(match.group(2) or ""),
                return_type=(match.group(3) or "").strip(),
            )
            op.line = self._line_at(self._text, match.start())
            op.end_line = self._line_at(self._text, self._text.find(body, match.end()) + len(body))
            ops.append(self._operation_from_body(op, body))
        return sorted(ops, key=lambda op: op.line)

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

    def _methods_from_body(self, class_body: str, class_name: str) -> list[Operation]:
        ops: list[Operation] = []
        position = 0
        while (match := _METHOD_RE.search(class_body, position)) is not None:
            name = match.group(1)
            name_start = match.start(1)
            # A name after a dot is a call on something (`this.store.change(`), not a method this class declares. The
            # check reads the character before the name, since a match can open on the full stop ending a comment above.
            if (name_start > 0 and class_body[name_start - 1] == ".") or name in {"if", "for", "while", "switch", "catch", "class", "constructor"}:
                position = name_start + len(name)
                continue
            op_name = "constructor" if class_name and name == class_name else name
            method_body, body_start = self._brace_body(class_body, match.end() - 1)
            if method_body is None:
                position = name_start + len(name)
                continue
            # Reading on after the body keeps a statement inside it, such as `for (…) {`, from being taken for the next header.
            position = body_start + len(method_body) + 1
            op = self.operation_type(
                name=op_name,
                parameters=self._split_params(match.group(2) or ""),
                return_type=(match.group(3) or "").strip(),
            )
            header = match.group(0)
            header_start = match.start() + len(header) - len(header.lstrip())
            op.line = self._line_at(self._text, self._body_start + header_start)
            self._apply_method_end_line(op, class_body, match.end() - 1)
            filled = self._operation_from_body(op, method_body)
            prefix = class_body[max(0, match.start() - 24) : match.start()]
            header = match.group(0)
            if re.search(r"\bget\s+\w+\s*\(", header) or re.search(r"\bset\s+\w+\s*\(", header):
                filled.is_property = True
            filled.is_static = bool(re.search(r"\bstatic\b", prefix) or re.search(r"\bstatic\b", header))
            ops.append(filled)
        return ops

    def _operation_from_body(self, op: Operation, body: str) -> Operation:
        """The operation with the statements inside its braces as its body, the operations they call, and the notes
        its `//` comments give it."""
        code_only = "\n".join(
            line for line in body.splitlines() if not line.strip().startswith("//")
        )
        stripped = _STRING_RE.sub('""', code_only)
        qualified = re.findall(r"(?<![\w.])([A-Z]\w*(?:\.[A-Za-z_]\w*)+)\s*\(", stripped)
        bare = [
            m.group(1) for m in _CALL_RE.finditer(stripped)
            if m.group(1) != op.name and not _CONSTRUCTION_RE.search(stripped[: m.start()])
        ]
        suffixes = {item.split(".")[-1] for item in qualified}
        callees = qualified + [name for name in bare if name not in suffixes]
        notes = [
            line.strip()[2:].strip()
            for line in body.splitlines()
            if line.strip().startswith("//")
        ]
        for note in notes:
            op.add_invariant(note)
        op.take_brace_body(body, callees)
        return op

    def _load_body_facts(self, oclass: OoadClass) -> None:
        """Measure each operation's body once its class holds it, so the operation reads its owner itself."""
        for operation in oclass.operations:
            operation.load_brace_body_facts()

    def _apply_method_end_line(self, op: Operation, class_body: str, search_from: int) -> None:
        brace_open = class_body.find("{", search_from)
        if brace_open < 0:
            return
        close_idx = BracketStructure(class_body).closing_bracket(brace_open)
        if close_idx is not None:
            op.end_line = self._line_at(self._text, self._body_start + close_idx)

    def _split_params(self, raw: str) -> list[str]:
        if not raw.strip():
            return []
        params: list[str] = []
        for part in split_top_level(raw):
            default_at = BracketStructure(part).top_level_index("=")
            if default_at >= 0:
                part = part[:default_at].strip()
            part = re.sub(r"^\s*(public|private|protected|final|readonly)\s+", "", part)
            hint_at = BracketStructure(part).top_level_index(":")
            if hint_at >= 0:
                name_part, type_hint = part[:hint_at], part[hint_at + 1 :]
                name = name_part.strip().split()[-1]
                type_hint = type_hint.strip()
            else:
                tokens = part.split()
                name = tokens[-1] if tokens else part
                type_hint = ""
            name = name.lstrip("@")
            if name and name not in {"this", "self"} and re.match(r"^[\w$]+\??$", name):
                params.append(f"{name}: {type_hint}" if type_hint else name)
        return params

    def _fields_from_body(self, oclass: OoadClass, body: str) -> list:
        """Each field the class body declares, with its line, in the order it declares them."""
        outside = self._outside_braces(body)
        props = []
        seen: set[str] = set()
        cursor = 0
        for match in _FIELD_RE.finditer(outside):
            name = match.group(2)
            if name in seen:
                continue
            seen.add(name)
            prop = self._field(name, len(props) + 1, match.start(2), match.group(3).strip())
            prop.is_static = "static" in match.group(1).split()
            for note in self._comments_above(outside[cursor:match.start()]):
                prop.take_note(note)
            props.append(prop)
            cursor = match.end()
        for match in _ASSIGN_FIELD_RE.finditer(outside):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            prop = self._field(name, len(props) + 1, match.start(1))
            prop.is_static = bool(re.search(r"\bstatic\b", match.group(0)))
            props.append(prop)
        return props

    def _field(self, name: str, order: int, at: int, type_hint: str = ""):
        prop = self.property_type(name=name, sequential_order=order, type_hint=type_hint)
        prop.line = self._line_at(self._text, self._body_start + at)
        return prop

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

    def _outside_braces(self, body: str) -> str:
        chars: list[str] = []
        depth = 0
        for ch in body:
            if ch == "{":
                depth += 1
                chars.append(" ")
            elif ch == "}":
                depth = max(0, depth - 1)
                chars.append(" ")
            elif depth == 0:
                chars.append(ch)
            else:
                chars.append(" ")
        return "".join(chars)

    def _derive_member_relationships(self, oclass: OoadClass) -> None:
        """A field relates only when its type names a domain class."""
        for prop in oclass.properties:
            prop.derive_relationship()

    def _body_open(self, after: int) -> int:
        """Where the class body opens: the first `{` after the class name outside the type arguments of its heritage
        clause, whose braces (`extends Component<{ children: ReactNode }>`) open no body; the text's end for none."""
        depth = 0
        for index in range(after, len(self._text)):
            char = self._text[index]
            if char == "<":
                depth += 1
            elif char == ">" and depth:
                depth -= 1
            elif char == "{" and not depth:
                return index
        return len(self._text)

    def _brace_body(self, text: str, open_index: int) -> tuple[str | None, int]:
        """The text inside the first `{` at or after open_index and the `}` that closes it, with where it starts."""
        brace = text.find("{", open_index)
        body = BracketStructure(text).braced(brace) if brace >= 0 else None
        return (body, brace + 1) if body is not None else (None, -1)

    def _line_at(self, text: str, index: int) -> int:
        return text.count("\n", 0, index) + 1
