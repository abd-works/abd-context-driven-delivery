"""Shared brace-language parse -> CleanEngineering model (TypeScript / JavaScript / Java).

Fills the same Operation metrics as the Python channel so RuleEvals stay language-agnostic.
"""
from __future__ import annotations

import hashlib
import re
from typing import Callable

from practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, Operation

_CLASS_RE = re.compile(
    r"(?:export\s+)?(?:abstract\s+)?(?:public\s+|private\s+|protected\s+)?class\s+(\w+)",
)
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
_CALC_RE = re.compile(r"[+\-*/%]|===|!==|==|!=|<=|>=|&&|\|\|")
_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_PUBLIC_ATTR = re.compile(r"\b(?:this|self)\.([A-Za-z]\w*)\s*=")
_PRIVATE_RETURN = re.compile(r"\breturn\s+(?:this|self)\._\w+")
_CATCH_RE = re.compile(r"\bcatch\s*(\([^)]*\))?\s*\{")
_FOR_OF_RE = re.compile(
    r"\bfor\s*\(\s*(?:const|let|var|int|final)?\s*([A-Za-z_]\w*)\s*(?::|of|in)\b"
)
_VALIDATION_RE = re.compile(
    r"\b(?:throw|raise|assert|require|Preconditions\.|Objects\.requireNonNull)\b"
)
_NARRATION = re.compile(
    r"^\s*//\s*(get|set|return|handle|create|init|import|increment|define)\s",
    re.I,
)
_COMMENTED_CODE = re.compile(
    r"^\s*//\s*(function |class |if |for |while |return |throw |try)",
)


class CFamilyParse:
    def __init__(
        self,
        model_factory: Callable[[], CleanEngineeringModel],
        class_factory: Callable[..., OoadClass],
    ) -> None:
        self._model_factory = model_factory
        self._class_factory = class_factory

    def parse(self, text: str) -> CleanEngineeringModel:
        self._text = text
        self._narration, self._commented = self._comment_issues(text)
        model = self._model_factory()
        module = Module(name="", sequential_order=1)
        self._append_classes(module)
        self._attach_top_level(module)
        if module.classes:
            model.modules.append(module)
        return model

    def _comment_issues(self, text: str) -> tuple[list[int], list[int]]:
        narration: list[int] = []
        commented: list[int] = []
        for i, line in enumerate(text.splitlines(), start=1):
            if _NARRATION.match(line):
                narration.append(i)
            elif _COMMENTED_CODE.match(line):
                commented.append(i)
        return narration, commented

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
            oclass.narration_comment_lines = list(self._narration)
            oclass.commented_code_lines = list(self._commented)
            oclass.operations = self._methods_from_body(body, match.group(1))
            self._prepend_constructors(oclass, body)
            module.classes.append(oclass)
            class_order += 1

    def _prepend_constructors(self, oclass: OoadClass, body: str) -> None:
        for ctor in _CTOR_RE.finditer(body):
            ctor_body, _rel = self._brace_body(body, ctor.end() - 1)
            if ctor_body is None:
                continue
            op = Operation(name="constructor", parameters=self._split_params(ctor.group(1)))
            op.line = self._line_at(self._text, self._body_start + ctor.start())
            oclass.operations.insert(0, self._operation_from_body(op, ctor_body))

    def _attach_top_level(self, module: Module) -> None:
        top_ops = self._top_level_functions()
        if not top_ops:
            return
        if not module.classes:
            holder = self._class_factory(name="_module", sequential_order=1)
            holder.narration_comment_lines = list(self._narration)
            holder.commented_code_lines = list(self._commented)
            holder.operations = top_ops
            module.classes.append(holder)
            return
        module.classes[0].operations.extend(top_ops)

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
            if name in {"if", "for", "while", "switch", "catch", "class", "constructor"}:
                continue
            op_name = "constructor" if class_name and name == class_name else name
            method_body, _rel = self._brace_body(class_body, match.end() - 1)
            if method_body is None:
                continue
            op = Operation(name=op_name, parameters=self._split_params(match.group(2) or ""))
            op.line = self._line_at(self._text, self._body_start + match.start())
            filled = self._operation_from_body(op, method_body)
            prefix = class_body[max(0, match.start() - 12) : match.start()]
            if re.search(r"\bget\s*$", prefix):
                filled.is_property = True
            ops.append(filled)
        return ops

    def _operation_from_body(self, op: Operation, body: str) -> Operation:
        stripped = _STRING_RE.sub('""', body)
        callees = [m.group(1) for m in _CALL_RE.finditer(stripped) if m.group(1) != op.name]
        base_line = op.line or 1
        op.param_count = len(op.parameters)
        op.line_count = body.count("\n") + 1
        op.nesting_depth = self._max_brace_depth(body)
        op.callees = callees
        op.literals = [m.group(0).strip("\"'`") for m in _STRING_RE.finditer(body)]
        op.has_calculation = bool(_CALC_RE.search(stripped))
        op.has_validation = bool(_VALIDATION_RE.search(stripped))
        op.bare_except_lines, op.swallowed_except_lines = self._catch_issues(body, base_line)
        op.body_fingerprint = hashlib.sha256(re.sub(r"\s+", " ", body).strip().encode()).hexdigest()
        op.magic_numbers = self._magic_numbers(body, base_line)
        op.assigned_names = self._assigned_names(op, body)
        op.loop_target_names = [(m.group(1), base_line) for m in _FOR_OF_RE.finditer(body)]
        op.constructed_types = [(c, base_line) for c in callees if c and c[0].isupper()]
        op.public_attr_assigns = [(m.group(1), base_line) for m in _PUBLIC_ATTR.finditer(body)]
        op.returns_private_attr = bool(_PRIVATE_RETURN.search(body))
        op.docstring_parrots_name = False
        return op

    def _magic_numbers(self, body: str, base_line: int) -> list[tuple[float, int]]:
        magic: list[tuple[float, int]] = []
        for i, ln in enumerate(body.splitlines(), start=base_line):
            for num in re.findall(r"\b(\d+(?:\.\d+)?)\b", ln):
                val = float(num)
                if val not in {0, 1, 2, -1, 0.0, 1.0, 0.5, 100, 10}:
                    magic.append((val, i))
        return magic

    def _assigned_names(self, op: Operation, body: str) -> list[tuple[str, int]]:
        base_line = op.line or 1
        assigned = [(p, base_line) for p in op.parameters]
        assigned.extend(
            (m.group(1), base_line)
            for m in re.finditer(
                r"\b(?:let|const|var|int|String|double|boolean|final)?\s*([a-z]\w*)\s*=",
                body,
            )
        )
        return assigned

    def _catch_issues(self, body: str, base_line: int) -> tuple[list[int], list[int]]:
        bare: list[int] = []
        swallowed: list[int] = []
        for match in _CATCH_RE.finditer(body):
            catch_body, _rel = self._brace_body(body, match.end() - 1)
            if catch_body is None:
                continue
            lineno = base_line + body.count("\n", 0, match.start())
            binding = (match.group(1) or "").strip()
            if not binding or binding == "()":
                bare.append(lineno)
            stripped = catch_body.strip()
            if not stripped or stripped in {";", "pass", "// ignore", "/* ignore */"}:
                swallowed.append(lineno)
        return bare, swallowed

    def _split_params(self, raw: str) -> list[str]:
        if not raw.strip():
            return []
        params: list[str] = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            part = re.sub(r"^\s*(public|private|protected|final|readonly)\s+", "", part)
            name = re.split(r"\s*:\s*", part)[0].strip()
            name = name.split()[-1] if name.split() else name
            name = name.lstrip("@")
            if name and name not in {"this", "self"}:
                params.append(name)
        return params

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

    def _max_brace_depth(self, body: str) -> int:
        depth = 0
        max_depth = 0
        for ch in body:
            if ch == "{":
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch == "}":
                depth = max(0, depth - 1)
        return max_depth

    def _line_at(self, text: str, index: int) -> int:
        return text.count("\n", 0, index) + 1
