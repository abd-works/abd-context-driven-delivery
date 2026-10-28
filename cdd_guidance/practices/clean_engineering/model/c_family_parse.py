"""Shared brace-language parse -> CleanEngineering model (TypeScript / JavaScript / Java)."""
from __future__ import annotations

import re
from typing import Callable

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, Operation
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.operation import operation_body_fingerprint
from cdd_guidance.practices.clean_engineering.model.operation_metrics import apply_brace_body_metrics
from cdd_guidance.practices.clean_engineering.model.property import Property, append_invariant, take_property_note

_CLASS_RE = re.compile(
    r"(?:export\s+)?(?:abstract\s+)?(?:public\s+|private\s+|protected\s+)?class\s+(\w+)",
)
_EXTENDS_RE = re.compile(r"\bextends\s+([\w.]+)")
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
_CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_FIELD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|static)\s+)*(\w+)\s*:\s*([^;=]+);",
    re.M,
)
_ASSIGN_FIELD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|static|declare|override)\s+)+(\w+)\s*=",
    re.M,
)
_SKIP_TYPES = frozenset({
    "String", "Number", "Boolean", "Void", "Any", "Unknown", "Object",
    "Record", "Array", "Promise", "Partial", "Omit", "Pick", "Date", "Error",
    "Map", "Set", "Readonly", "Required", "NonNullable",
})


class CFamilyParse:
    def __init__(
        self,
        model_factory: Callable[[], CleanEngineeringModel],
        class_factory: Callable[..., OoadClass],
        language: CodeLanguage,
    ) -> None:
        self._model_factory = model_factory
        self._class_factory = class_factory
        self._language = language

    @staticmethod
    def method_span_in_text(text: str, name: str, fallback_line: int = 1) -> tuple[int, int]:
        """Brace-language method extent in full file text (used by graph load when end_line missing)."""
        match = re.search(rf"\b{re.escape(name)}\s*\([^)]*\)\s*(?::\s*[^{{]+)?\s*\{{", text)
        if match is None:
            line = fallback_line
            return line, line
        start = text[: match.start()].count("\n") + 1
        depth = 0
        opened = False
        for index in range(match.end() - 1, len(text)):
            if text[index] == "{":
                depth += 1
                opened = True
            elif text[index] == "}":
                depth -= 1
                if opened and depth == 0:
                    return start, text[:index].count("\n") + 1
        return start, start

    def parse(self, text: str) -> CleanEngineeringModel:
        self._text = text
        model = self._model_factory()
        module = model.load_module(Module(name="", sequential_order=1))
        module.preamble = self._preamble()
        self._append_classes(module)
        self._attach_top_level(module)
        if module.classes:
            model.modules.append(module)
        return model

    def _preamble(self) -> CodeBody:
        """Imports and constants above the first class, as written."""
        first = _CLASS_RE.search(self._text)
        if first is None:
            return CodeBody()
        line_start = self._text.rfind("\n", 0, first.start()) + 1
        return CodeBody(self._text[:line_start].rstrip(), self._language)

    def _append_classes(self, module: Module) -> None:
        class_order = 1
        for match in _CLASS_RE.finditer(self._text):
            body, body_start = self._brace_body(self._text, match.end() - 1)
            if body is None:
                continue
            self._body_start = body_start
            oclass = self._class_factory(
                name=match.group(1),
                sequential_order=class_order,
                line=self._line_at(self._text, match.start()),
            )
            oclass.end_line = self._line_at(self._text, body_start + len(body))
            oclass.bases = _EXTENDS_RE.findall(self._text[match.end() : body_start])
            oclass.operations = self._methods_from_body(body, match.group(1))
            self._prepend_constructors(oclass, body)
            oclass.properties = self._fields_from_body(oclass, body)
            self._bind_member_relationships(oclass)
            module.classes.append(oclass)
            class_order += 1

    def _prepend_constructors(self, oclass: OoadClass, body: str) -> None:
        for ctor in _CTOR_RE.finditer(body):
            ctor_body, _rel = self._brace_body(body, ctor.end() - 1)
            if ctor_body is None:
                continue
            op = Operation(name="constructor", parameters=self._split_params(ctor.group(1)))
            op.line = self._line_at(self._text, self._body_start + ctor.start())
            self._apply_method_end_line(op, body, ctor.end() - 1)
            oclass.operations.insert(0, self._operation_from_body(op, ctor_body))

    def _attach_top_level(self, module: Module) -> None:
        top_ops = self._top_level_functions()
        if not top_ops:
            return
        holder = self._class_factory(name="_module", sequential_order=len(module.classes) + 1)
        holder.operations = top_ops
        module.classes.append(holder)

    def _top_level_functions(self) -> list[Operation]:
        ops: list[Operation] = []
        class_spans = self._class_spans()
        for match in _TOP_FN_RE.finditer(self._text):
            if any(start <= match.start() <= end for start, end in class_spans):
                continue
            body, _rel = self._brace_body(self._text, match.end() - 1)
            if body is None:
                continue
            op = Operation(name=match.group(1), parameters=self._split_params(match.group(2) or ""))
            op.line = self._line_at(self._text, match.start())
            ops.append(self._operation_from_body(op, body))
        return ops

    def _class_spans(self) -> list[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        for match in _CLASS_RE.finditer(self._text):
            body, body_start = self._brace_body(self._text, match.end() - 1)
            if body is not None:
                spans.append((body_start, body_start + len(body)))
        return spans

    def _methods_from_body(self, class_body: str, class_name: str) -> list[Operation]:
        ops: list[Operation] = []
        for match in _METHOD_RE.finditer(class_body):
            name = match.group(1)
            if match.start() > 0 and class_body[match.start() - 1] == ".":
                continue
            if name in {"if", "for", "while", "switch", "catch", "class", "constructor"}:
                continue
            op_name = "constructor" if class_name and name == class_name else name
            method_body, _rel = self._brace_body(class_body, match.end() - 1)
            if method_body is None:
                continue
            op = Operation(
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
        code_only = "\n".join(
            line for line in body.splitlines() if not line.strip().startswith("//")
        )
        stripped = _STRING_RE.sub('""', code_only)
        qualified = re.findall(r"(?<![\w.])([A-Z]\w*(?:\.[A-Za-z_]\w*)+)\s*\(", stripped)
        bare = [m.group(1) for m in _CALL_RE.finditer(stripped) if m.group(1) != op.name]
        suffixes = {item.split(".")[-1] for item in qualified}
        callees = qualified + [name for name in bare if name not in suffixes]
        notes = [
            line.strip()[2:].strip()
            for line in body.splitlines()
            if line.strip().startswith("//")
        ]
        for note in notes:
            append_invariant(op, note)
        op.callees = callees
        op.line_count = max(1, len([line for line in body.splitlines() if line.strip()]))
        op.body_fingerprint = operation_body_fingerprint(body)
        op.body = CodeBody(body, self._language)
        apply_brace_body_metrics(op, body)
        if op.name in {"constructor", "__init__"}:
            op.constructed_types = self._constructed_types(body, op.line or 1)
        return op

    def _apply_method_end_line(self, op: Operation, class_body: str, search_from: int) -> None:
        brace_open = class_body.find("{", search_from)
        if brace_open < 0:
            return
        close_idx = self._closing_brace_index(class_body, brace_open)
        if close_idx >= 0:
            op.end_line = self._line_at(self._text, self._body_start + close_idx)

    def _closing_brace_index(self, text: str, open_index: int) -> int:
        depth = 0
        for index in range(open_index, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    return index
        return -1

    def _constructed_types(self, body: str, start_line: int) -> list[tuple[str, int]]:
        found: list[tuple[str, int]] = []
        for index, line in enumerate(body.splitlines()):
            for match in re.finditer(r"\bnew\s+([A-Z]\w*)\s*\(", line):
                found.append((match.group(1), start_line + index))
        return found

    def _split_params(self, raw: str) -> list[str]:
        if not raw.strip():
            return []
        params: list[str] = []
        for part in self._split_param_parts(raw):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                part = part.split("=", 1)[0].strip()
            part = re.sub(r"^\s*(public|private|protected|final|readonly)\s+", "", part)
            if ":" in part:
                name_part, type_hint = part.split(":", 1)
                name = name_part.strip().split()[-1]
                type_hint = type_hint.strip()
            else:
                tokens = part.split()
                name = tokens[-1] if tokens else part
                type_hint = ""
            name = name.lstrip("@")
            if name and name not in {"this", "self"} and re.match(r"^[\w$]+$", name):
                params.append(f"{name}: {type_hint}" if type_hint else name)
        return params

    def _split_param_parts(self, raw: str) -> list[str]:
        """Split parameter list on commas outside generic brackets."""
        parts: list[str] = []
        depth = 0
        start = 0
        for index, ch in enumerate(raw):
            if ch in "<([{":
                depth += 1
            elif ch in ">)]}":
                depth = max(0, depth - 1)
            elif ch == "," and depth == 0:
                parts.append(raw[start:index])
                start = index + 1
        parts.append(raw[start:])
        return parts

    def _fields_from_body(self, oclass: OoadClass, body: str) -> list:
        outside = self._outside_braces(body)
        props = []
        seen: set[str] = set()
        load = getattr(oclass, "load_property_field", None)
        cursor = 0
        for match in _FIELD_RE.finditer(outside):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            prop = Property(name=name, sequential_order=len(props) + 1, type_hint=match.group(2).strip())
            for note in self._comments_above(outside[cursor:match.start()]):
                take_property_note(prop, note)
            props.append(load(prop) if load is not None else prop)
            cursor = match.end()
        for match in _ASSIGN_FIELD_RE.finditer(outside):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            props.append(
                load(Property(name=name, sequential_order=len(props) + 1))
                if load is not None
                else Property(name=name, sequential_order=len(props) + 1)
            )
        return props

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

    def _bind_member_relationships(self, oclass: OoadClass) -> None:
        """A field relates only when its type names a domain class."""
        from cdd_guidance.practices.clean_engineering.model.property import bind_property_relationship

        for prop in oclass.properties:
            bind_property_relationship(prop)

    def _domain_types(self, type_raw: str) -> list[str]:
        names: list[str] = []
        for match in re.finditer(r"\b([A-Z][A-Za-z0-9]*)\b", type_raw or ""):
            name = match.group(1)
            if name in _SKIP_TYPES or name in names:
                continue
            names.append(name)
        return names

    def _brace_body(self, text: str, open_index: int) -> tuple[str | None, int]:
        while open_index < len(text) and text[open_index] != "{":
            open_index += 1
        if open_index >= len(text):
            return None, -1
        depth = 0
        i = open_index
        while i < len(text):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[open_index + 1 : i], open_index + 1
            i += 1
        return None, -1

    def _line_at(self, text: str, index: int) -> int:
        return text.count("\n", 0, index) + 1
