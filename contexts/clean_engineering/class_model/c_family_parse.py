"""Shared brace-language parse → CleanEngineering model (TypeScript / JavaScript / Java).

Fills the same Operation metrics as the Python channel so RuleEvals stay language-agnostic.
"""
from __future__ import annotations

import hashlib
import re
from typing import Callable

from contexts.clean_engineering.class_model.base_class_model import CleanEngineeringModel, Module, OoadClass, Operation

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


def parse_c_family(
    text: str,
    *,
    model_factory: Callable[[], CleanEngineeringModel],
    class_factory: Callable[..., OoadClass],
) -> CleanEngineeringModel:
    model = model_factory()
    module = Module(name="", sequential_order=1)
    narration: list[int] = []
    commented: list[int] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if _NARRATION.match(line):
            narration.append(i)
        elif _COMMENTED_CODE.match(line):
            commented.append(i)

    class_order = 1
    for cm in _CLASS_RE.finditer(text):
        class_name = cm.group(1)
        body, body_start = _brace_body(text, cm.end() - 1)
        if body is None:
            continue
        oclass = class_factory(name=class_name, sequential_order=class_order, line=_line_at(text, cm.start()))
        oclass.narration_comment_lines = list(narration)
        oclass.commented_code_lines = list(commented)
        oclass.operations = _methods_from_body(text, body, body_start, class_name=class_name)
        for ctor in _CTOR_RE.finditer(body):
            ctor_body, _rel = _brace_body(body, ctor.end() - 1)
            if ctor_body is None:
                continue
            abs_start = body_start + ctor.start()
            params = _split_params(ctor.group(1))
            op = _operation_from_body(
                "constructor",
                params,
                ctor_body,
                line=_line_at(text, abs_start),
            )
            oclass.operations.insert(0, op)
        module.classes.append(oclass)
        class_order += 1

    top_ops = _top_level_functions(text)
    if top_ops and not module.classes:
        holder = class_factory(name="_module", sequential_order=1)
        holder.narration_comment_lines = list(narration)
        holder.commented_code_lines = list(commented)
        holder.operations = top_ops
        module.classes.append(holder)
    elif top_ops and module.classes:
        module.classes[0].operations.extend(top_ops)

    if module.classes:
        model.modules.append(module)
    return model


def _top_level_functions(text: str) -> list[Operation]:
    ops: list[Operation] = []
    # Skip function-like matches that sit inside a class body by requiring
    # the match start to be outside any class brace range we already parsed.
    class_spans: list[tuple[int, int]] = []
    for cm in _CLASS_RE.finditer(text):
        body, body_start = _brace_body(text, cm.end() - 1)
        if body is None:
            continue
        class_spans.append((body_start, body_start + len(body)))
    for m in _TOP_FN_RE.finditer(text):
        if any(start <= m.start() <= end for start, end in class_spans):
            continue
        body, _rel = _brace_body(text, m.end() - 1)
        if body is None:
            continue
        ops.append(
            _operation_from_body(
                m.group(1),
                _split_params(m.group(2) or ""),
                body,
                line=_line_at(text, m.start()),
            )
        )
    return ops


def _methods_from_body(
    full_text: str,
    class_body: str,
    body_start: int,
    *,
    class_name: str = "",
) -> list[Operation]:
    ops: list[Operation] = []
    for m in _METHOD_RE.finditer(class_body):
        name = m.group(1)
        if name in {"if", "for", "while", "switch", "catch", "class", "constructor"}:
            continue
        # Java constructors share the class name
        op_name = "constructor" if class_name and name == class_name else name
        params = _split_params(m.group(2) or "")
        method_body, _rel = _brace_body(class_body, m.end() - 1)
        if method_body is None:
            continue
        abs_index = body_start + m.start()
        op = _operation_from_body(
            op_name,
            params,
            method_body,
            line=_line_at(full_text, abs_index),
        )
        # TypeScript/JavaScript getters: `get name() { ... }`
        prefix = class_body[max(0, m.start() - 12) : m.start()]
        if re.search(r"\bget\s*$", prefix):
            op.is_property = True
        ops.append(op)
    return ops


def _operation_from_body(name: str, params: list[str], body: str, *, line: int | None) -> Operation:
    stripped = _STRING_RE.sub('""', body)
    callees = [m.group(1) for m in _CALL_RE.finditer(stripped) if m.group(1) != name]
    nesting = _max_brace_depth(body)
    line_count = body.count("\n") + 1
    fingerprint = hashlib.sha256(
        re.sub(r"\s+", " ", body).strip().encode()
    ).hexdigest()
    base_line = line or 1
    magic: list[tuple[float, int]] = []
    for i, ln in enumerate(body.splitlines(), start=base_line):
        for num in re.findall(r"\b(\d+(?:\.\d+)?)\b", ln):
            val = float(num)
            if val not in {0, 1, 2, -1, 0.0, 1.0, 0.5, 100, 10}:
                magic.append((val, i))
    assigned = [(p, base_line) for p in params]
    assigned.extend(
        (m.group(1), base_line)
        for m in re.finditer(
            r"\b(?:let|const|var|int|String|double|boolean|final)?\s*([a-z]\w*)\s*=",
            body,
        )
    )
    loop_targets = [(m.group(1), base_line) for m in _FOR_OF_RE.finditer(body)]
    literals = [m.group(0).strip("\"'`") for m in _STRING_RE.finditer(body)]
    bare_except, swallowed = _catch_issues(body, base_line)
    public_attrs = [(m.group(1), base_line) for m in _PUBLIC_ATTR.finditer(body)]
    return Operation(
        name=name,
        parameters=params,
        param_count=len(params),
        line=line,
        line_count=line_count,
        nesting_depth=nesting,
        callees=callees,
        literals=literals,
        has_calculation=bool(_CALC_RE.search(stripped)),
        has_validation=bool(_VALIDATION_RE.search(stripped)),
        bare_except_lines=bare_except,
        swallowed_except_lines=swallowed,
        body_fingerprint=fingerprint,
        magic_numbers=magic,
        assigned_names=assigned,
        loop_target_names=loop_targets,
        constructed_types=[
            (c, base_line) for c in callees if c and c[0].isupper()
        ],
        public_attr_assigns=public_attrs,
        returns_private_attr=bool(_PRIVATE_RETURN.search(body)),
        docstring_parrots_name=False,
    )


def _catch_issues(body: str, base_line: int) -> tuple[list[int], list[int]]:
    bare: list[int] = []
    swallowed: list[int] = []
    for m in _CATCH_RE.finditer(body):
        catch_body, _rel = _brace_body(body, m.end() - 1)
        if catch_body is None:
            continue
        lineno = base_line + body.count("\n", 0, m.start())
        binding = (m.group(1) or "").strip()
        # Optional catch binding / bare catch → bare_except
        if not binding or binding == "()":
            bare.append(lineno)
        stripped = catch_body.strip()
        if not stripped or stripped in {";", "pass", "// ignore", "/* ignore */"}:
            swallowed.append(lineno)
    return bare, swallowed


def _split_params(raw: str) -> list[str]:
    if not raw.strip():
        return []
    params: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        # TypeScript/Java: take the name token (last identifier before : or alone)
        part = re.sub(r"^\s*(public|private|protected|final|readonly)\s+", "", part)
        name = re.split(r"\s*:\s*", part)[0].strip()
        name = name.split()[-1] if name.split() else name
        name = name.lstrip("@")
        if name and name not in {"this", "self"}:
            params.append(name)
    return params


def _brace_body(text: str, open_index: int) -> tuple[str | None, int]:
    """Return body inside braces starting at open_index pointing at '{', and absolute start index of body."""
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


def _max_brace_depth(body: str) -> int:
    depth = 0
    max_depth = 0
    for ch in body:
        if ch == "{":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == "}":
            depth = max(0, depth - 1)
    return max_depth


def _line_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1
