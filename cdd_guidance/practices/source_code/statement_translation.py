"""The statements of a body written in Python or in a script language (TypeScript, JavaScript), written in the other.

A render carries an operation's body from the language it was read in to the one it writes. *BodyTranslation* is the
one place that does it, for every render that writes code (Clean Engineering's class model, and DDD's through it): it
reads the body, writes each statement it can in the target language, and keeps any other statement in the source
language under a note naming it (*TranslatedBody.untranslated*), so a statement it cannot write is never dropped.

Python is read with ``ast``. A script body is read here, by *ScriptReading*, into the same Python syntax tree, so
both directions share one tree: Python is written from it with ``ast.unparse``, a script by *ScriptWriting*. The subset
both languages hold: assignments to locals and fields, returns, calls with their arguments, if / elif / else, a loop
over a collection or a range, while, raise / throw, comparisons and boolean operators, strings and f-strings / template
literals, list and dict literals, ``len(x)`` / ``x.length``, and a list comprehension / ``filter`` and ``map``.
"""

from __future__ import annotations

import ast
import io
import json
import re
import textwrap
import tokenize
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from cdd_guidance.practices.source_code.code_body import JAVASCRIPT, PYTHON, TYPESCRIPT, CodeLanguage


class Untranslatable(Exception):
    """A statement, or part of one, outside the subset both languages hold."""


@dataclass
class TranslatedBody:
    """A body written in the target language: its lines, relative to the body's indent, and the source text of each
    statement that could not be translated, which its lines keep under a note naming the source language."""

    lines: List[str] = field(default_factory=list)
    untranslated: List[str] = field(default_factory=list)


class BodyTranslation:
    """Translates a body from source to target. Made for one render: parameters names the parameters of each
    operation the model being written declares, by the operation's name as the source writes it, so a Python call
    with keyword arguments is written with its arguments in the operation's order."""

    def __init__(self, source: CodeLanguage, target: CodeLanguage, parameters: Optional[Dict[str, List[str]]] = None) -> None:
        self.source = source
        self.target = target
        self.parameters = parameters or {}

    @property
    def is_possible(self) -> bool:
        """Whether the two languages are Python and a script language, one each way."""
        scripts = (TYPESCRIPT, JAVASCRIPT)
        return (self.source is PYTHON and self.target in scripts) or (self.source in scripts and self.target is PYTHON)

    def translate(self, text: str, declared: Sequence[str] = ()) -> Optional[TranslatedBody]:
        """The body text holds, written in the target language; declared names the operation's parameters, which a
        script body does not declare again. None when the two languages are not Python and a script language, or
        the body cannot be read at all."""
        if not self.is_possible or not text.strip():
            return None
        if self.source is PYTHON:
            return PythonToScript(self.target, self.parameters).translate(text, declared)
        return ScriptToPython().translate(text)


# -- Python to a script language ------------------------------------------------------------------------------------

# A script language's precedence of each kind of expression: a part of lower precedence than its place needs is put in
# parentheses.
_TERNARY, _OR, _AND, _EQUALITY, _RELATIONAL, _ADDITIVE, _MULTIPLICATIVE, _EXPONENT, _UNARY, _POSTFIX, _PRIMARY = (
    2, 3, 4, 8, 9, 11, 12, 13, 14, 17, 18,
)
_BINARY = {
    ast.Add: ("+", _ADDITIVE), ast.Sub: ("-", _ADDITIVE), ast.Mult: ("*", _MULTIPLICATIVE),
    ast.Div: ("/", _MULTIPLICATIVE), ast.Mod: ("%", _MULTIPLICATIVE), ast.Pow: ("**", _EXPONENT),
}
_COMPARISON = {
    ast.Eq: ("===", _EQUALITY), ast.NotEq: ("!==", _EQUALITY), ast.Is: ("===", _EQUALITY), ast.IsNot: ("!==", _EQUALITY),
    ast.Lt: ("<", _RELATIONAL), ast.LtE: ("<=", _RELATIONAL), ast.Gt: (">", _RELATIONAL), ast.GtE: (">=", _RELATIONAL),
}
_AUGMENTED = {ast.Add: "+=", ast.Sub: "-=", ast.Mult: "*=", ast.Div: "/=", ast.Mod: "%="}
# A Python method and the script method that does the same.
_SCRIPT_METHODS = {
    "append": "push", "upper": "toUpperCase", "lower": "toLowerCase", "strip": "trim",
    "startswith": "startsWith", "endswith": "endsWith",
}
# A Python function and the script function that does the same.
_SCRIPT_FUNCTIONS = {"str": "String", "print": "console.log", "abs": "Math.abs", "min": "Math.min", "max": "Math.max"}


class PythonToScript:
    """A Python body written as a script language writes it, read with ``ast``."""

    def __init__(self, target: CodeLanguage, parameters: Dict[str, List[str]]) -> None:
        self.target = target
        self.parameters = parameters
        self.indent = target.indent
        self.comment = target.line_comment

    def translate(self, text: str, declared: Sequence[str]) -> Optional[TranslatedBody]:
        source = textwrap.dedent(text)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None
        self.source_lines = source.splitlines()
        self.comments = self._comments(source)
        self.declared = {self._spelled(name) for name in declared}
        self.reassigned = self._reassigned(tree)
        self.result = TranslatedBody()
        self._block(tree.body, 0)
        self._comments_before(len(self.source_lines) + 1, 0)
        return self.result

    def _comments(self, source: str) -> List[Tuple[int, str]]:
        """Each comment of the source, by its line, in order."""
        try:
            tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        except (tokenize.TokenError, IndentationError):
            return []
        return [(token.start[0], token.string[1:].strip()) for token in tokens if token.type == tokenize.COMMENT]

    def _comments_before(self, line: int, depth: int) -> None:
        while self.comments and self.comments[0][0] < line:
            self._write(depth, f"{self.comment} {self.comments.pop(0)[1]}".rstrip())

    def _reassigned(self, tree: ast.AST) -> set:
        """The locals assigned more than once, or changed by an augmented assignment, which `let` declares."""
        counts: Dict[str, int] = {}
        for node in ast.walk(tree):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, (ast.AugAssign, ast.AnnAssign)) else []
            for target in targets:
                if isinstance(target, ast.Name):
                    counts[target.id] = counts.get(target.id, 0) + (2 if isinstance(node, ast.AugAssign) else 1)
        return {name for name, count in counts.items() if count > 1}

    def _write(self, depth: int, line: str) -> None:
        self.result.lines.append(f"{self.indent * depth}{line}" if line else "")

    def _block(self, statements: Sequence[ast.stmt], depth: int) -> None:
        for statement in statements:
            self._comments_before(statement.lineno, depth)
            written = len(self.result.lines)
            try:
                self._statement(statement, depth)
            except Untranslatable:
                del self.result.lines[written:]
                self._keep(statement, depth)

    def _keep(self, statement: ast.stmt, depth: int) -> None:
        """statement as Python wrote it, under a note naming Python, and noted as not translated."""
        original = textwrap.dedent("\n".join(self.source_lines[statement.lineno - 1 : statement.end_lineno]))
        self.result.untranslated.append(original)
        self._write(depth, f"{self.comment} {PYTHON.name} statement to translate:")
        for line in original.splitlines():
            self._write(depth, f"{self.comment} {line}".rstrip())
        self.comments = [comment for comment in self.comments if comment[0] > statement.end_lineno]

    def _statement(self, node: ast.stmt, depth: int) -> None:
        end = self.target.spelling.statement_end
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                return
            self._write(depth, f"{self._expression(node.value)}{end}")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            self._assignment(node, depth)
        elif isinstance(node, ast.AugAssign):
            operator = _AUGMENTED.get(type(node.op))
            if operator is None:
                raise Untranslatable(node)
            self._write(depth, f"{self._target(node.target)} {operator} {self._expression(node.value)}{end}")
        elif isinstance(node, ast.Return):
            self._write(depth, f"return {self._expression(node.value)}{end}" if node.value is not None else f"return{end}")
        elif isinstance(node, ast.If):
            self._if(node, depth, "if")
        elif isinstance(node, ast.For):
            self._for(node, depth)
        elif isinstance(node, ast.While):
            if node.orelse:
                raise Untranslatable(node)
            self._write(depth, f"while ({self._expression(node.test)}) {{")
            self._block(node.body, depth + 1)
            self._write(depth, "}")
        elif isinstance(node, ast.Raise):
            self._write(depth, f"throw {self._thrown(node.exc)}{end}")
        elif isinstance(node, ast.Pass):
            return
        elif isinstance(node, ast.Break):
            self._write(depth, f"break{end}")
        elif isinstance(node, ast.Continue):
            self._write(depth, f"continue{end}")
        else:
            raise Untranslatable(node)

    def _assignment(self, node: ast.Assign | ast.AnnAssign, depth: int) -> None:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if len(targets) != 1 or node.value is None:
            raise Untranslatable(node)
        target, value = targets[0], self._expression(node.value)
        end = self.target.spelling.statement_end
        if isinstance(target, ast.Name) and self._spelled(target.id) not in self.declared:
            self.declared.add(self._spelled(target.id))
            keyword = "let" if target.id in self.reassigned else "const"
            self._write(depth, f"{keyword} {self._spelled(target.id)} = {value}{end}")
            return
        self._write(depth, f"{self._target(target)} = {value}{end}")

    def _target(self, node: ast.expr) -> str:
        if not isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            raise Untranslatable(node)
        return self._expression(node)

    def _if(self, node: ast.If, depth: int, opening: str) -> None:
        self._write(depth, f"{opening} ({self._expression(node.test)}) {{")
        self._block(node.body, depth + 1)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self.result.lines[-1:] = []
            self.result.lines.append(f"{self.indent * depth}}}")
            self._if_else(node.orelse[0], depth)
            return
        if node.orelse:
            self._write(depth, "} else {")
            self._block(node.orelse, depth + 1)
        self._write(depth, "}")

    def _if_else(self, node: ast.If, depth: int) -> None:
        """An elif, written on the line that closes the branch before it: `} else if (...) {`."""
        closing = self.result.lines.pop()
        self.result.lines.append(f"{closing} else if ({self._expression(node.test)}) {{")
        self._block(node.body, depth + 1)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self._write(depth, "}")
            self._if_else(node.orelse[0], depth)
            return
        if node.orelse:
            self._write(depth, "} else {")
            self._block(node.orelse, depth + 1)
        self._write(depth, "}")

    def _for(self, node: ast.For, depth: int) -> None:
        if node.orelse or not isinstance(node.target, ast.Name):
            raise Untranslatable(node)
        name = self._spelled(node.target.id)
        bounds = self._range(node.iter)
        if bounds is not None:
            start, stop = bounds
            self._write(depth, f"for (let {name} = {start}; {name} < {stop}; {name}++) {{")
        else:
            self._write(depth, f"for (const {name} of {self._expression(node.iter)}) {{")
        declared = name in self.declared
        self.declared.add(name)
        self._block(node.body, depth + 1)
        if not declared:
            self.declared.discard(name)
        self._write(depth, "}")

    def _range(self, node: ast.expr) -> Optional[Tuple[str, str]]:
        """The start and stop of `range(stop)` or `range(start, stop)`; none for any other collection."""
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range"):
            return None
        if node.keywords or len(node.args) not in (1, 2):
            raise Untranslatable(node)
        arguments = [self._expression(argument) for argument in node.args]
        return ("0", arguments[0]) if len(arguments) == 1 else (arguments[0], arguments[1])

    def _thrown(self, node: Optional[ast.expr]) -> str:
        if node is None:
            raise Untranslatable(node)
        if isinstance(node, ast.Name):
            return f"new {self.target.type_name(node.id)}()"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return f"new {self.target.type_name(node.func.id)}({self._arguments(node, node.func.id)})"
        return self._expression(node)

    # -- expressions --

    def _expression(self, node: ast.expr) -> str:
        return self._written(node)[0]

    def _part(self, node: ast.expr, needed: int) -> str:
        """node, in parentheses when it binds less tightly than its place needs."""
        text, precedence = self._written(node)
        return f"({text})" if precedence < needed else text

    def _written(self, node: ast.expr) -> Tuple[str, int]:
        """node as the script language writes it, with the precedence of what it is."""
        writer = getattr(self, f"_{type(node).__name__.lower()}", None)
        if writer is None:
            raise Untranslatable(node)
        return writer(node)

    def _constant(self, node: ast.Constant) -> Tuple[str, int]:
        value = node.value
        if value is None:
            return "null", _PRIMARY
        if isinstance(value, bool):
            return ("true" if value else "false"), _PRIMARY
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False), _PRIMARY
        if isinstance(value, (int, float)):
            return repr(value), _PRIMARY
        raise Untranslatable(node)

    def _spelled(self, name: str) -> str:
        """A Python name as the script language writes it: `self` is `this`; a class or a constant keeps its name."""
        if name == "self":
            return "this"
        if name[:1].isupper() or name.isupper():
            return self.target.type_name(name) if name in self.target.type_names else name
        return self.target.identifier(name)

    def _name(self, node: ast.Name) -> Tuple[str, int]:
        return self._spelled(node.id), _PRIMARY

    def _attribute(self, node: ast.Attribute) -> Tuple[str, int]:
        attribute = node.attr if node.attr[:1].isupper() else self.target.identifier(node.attr)
        return f"{self._part(node.value, _POSTFIX)}.{attribute}", _POSTFIX

    def _subscript(self, node: ast.Subscript) -> Tuple[str, int]:
        if isinstance(node.slice, ast.Slice):
            raise Untranslatable(node)
        return f"{self._part(node.value, _POSTFIX)}[{self._expression(node.slice)}]", _POSTFIX

    def _boolop(self, node: ast.BoolOp) -> Tuple[str, int]:
        operator, precedence = ("&&", _AND) if isinstance(node.op, ast.And) else ("||", _OR)
        return f" {operator} ".join(self._part(value, precedence + 1) for value in node.values), precedence

    def _unaryop(self, node: ast.UnaryOp) -> Tuple[str, int]:
        sign = {ast.Not: "!", ast.USub: "-", ast.UAdd: "+"}.get(type(node.op))
        if sign is None:
            raise Untranslatable(node)
        return f"{sign}{self._part(node.operand, _UNARY)}", _UNARY

    def _binop(self, node: ast.BinOp) -> Tuple[str, int]:
        if isinstance(node.op, ast.FloorDiv):
            return f"Math.floor({self._part(node.left, _MULTIPLICATIVE)} / {self._part(node.right, _MULTIPLICATIVE + 1)})", _POSTFIX
        operator = _BINARY.get(type(node.op))
        if operator is None:
            raise Untranslatable(node)
        sign, precedence = operator
        return f"{self._part(node.left, precedence)} {sign} {self._part(node.right, precedence + 1)}", precedence

    def _compare(self, node: ast.Compare) -> Tuple[str, int]:
        parts = []
        left = node.left
        for operator, right in zip(node.ops, node.comparators):
            parts.append(self._comparison(left, operator, right))
            left = right
        if len(parts) == 1:
            return parts[0]
        return " && ".join(text if precedence > _AND else f"({text})" for text, precedence in parts), _AND

    def _comparison(self, left: ast.expr, operator: ast.cmpop, right: ast.expr) -> Tuple[str, int]:
        if isinstance(operator, (ast.In, ast.NotIn)):
            found = f"{self._part(right, _POSTFIX)}.includes({self._expression(left)})"
            return (f"!{found}", _UNARY) if isinstance(operator, ast.NotIn) else (found, _POSTFIX)
        sign, precedence = _COMPARISON[type(operator)]
        return f"{self._part(left, precedence)} {sign} {self._part(right, precedence + 1)}", precedence

    def _ifexp(self, node: ast.IfExp) -> Tuple[str, int]:
        return f"{self._part(node.test, _OR)} ? {self._part(node.body, _TERNARY)} : {self._part(node.orelse, _TERNARY)}", _TERNARY

    def _joinedstr(self, node: ast.JoinedStr) -> Tuple[str, int]:
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${"))
            elif isinstance(value, ast.FormattedValue) and value.conversion == -1 and value.format_spec is None:
                parts.append(f"${{{self._expression(value.value)}}}")
            else:
                raise Untranslatable(node)
        return f"`{''.join(parts)}`", _PRIMARY

    def _list(self, node: ast.List | ast.Tuple) -> Tuple[str, int]:
        return f"[{', '.join(self._expression(element) for element in node.elts)}]", _PRIMARY

    _tuple = _list

    def _starred(self, node: ast.Starred) -> Tuple[str, int]:
        return f"...{self._part(node.value, _UNARY)}", _UNARY

    def _dict(self, node: ast.Dict) -> Tuple[str, int]:
        entries = []
        for key, value in zip(node.keys, node.values):
            if key is None:
                entries.append(f"...{self._part(value, _UNARY)}")
            else:
                entries.append(f"{self._expression(key)}: {self._expression(value)}")
        return f"{{{', '.join(entries)}}}", _PRIMARY

    def _lambda(self, node: ast.Lambda) -> Tuple[str, int]:
        names = ", ".join(self._spelled(argument.arg) for argument in node.args.args)
        return f"({names}) => {self._part(node.body, _TERNARY)}", _TERNARY

    def _listcomp(self, node: ast.ListComp) -> Tuple[str, int]:
        if len(node.generators) != 1:
            raise Untranslatable(node)
        generator = node.generators[0]
        if generator.is_async or not isinstance(generator.target, ast.Name):
            raise Untranslatable(node)
        name = self._spelled(generator.target.id)
        written = self._part(generator.iter, _POSTFIX)
        if generator.ifs:
            condition = " && ".join(self._part(test, _AND + 1) for test in generator.ifs)
            written += f".filter(({name}) => {condition})"
        if not (isinstance(node.elt, ast.Name) and node.elt.id == generator.target.id):
            written += f".map(({name}) => {self._part(node.elt, _TERNARY)})"
        return written, _POSTFIX

    def _call(self, node: ast.Call) -> Tuple[str, int]:
        function = node.func
        if isinstance(function, ast.Name):
            return self._function_call(node, function.id)
        if isinstance(function, ast.Attribute):
            return self._method_call(node, function)
        raise Untranslatable(node)

    def _function_call(self, node: ast.Call, name: str) -> Tuple[str, int]:
        if name == "len" and len(node.args) == 1 and not node.keywords:
            return f"{self._part(node.args[0], _POSTFIX)}.length", _POSTFIX
        if name == "isinstance" and len(node.args) == 2 and isinstance(node.args[1], ast.Name):
            return f"{self._part(node.args[0], _RELATIONAL)} instanceof {self._spelled(node.args[1].id)}", _RELATIONAL
        if name in ("range", "sum", "any", "all", "sorted", "enumerate", "zip", "map", "filter", "dict", "list", "set", "int", "float", "super"):
            raise Untranslatable(node)
        if name in _SCRIPT_FUNCTIONS:
            return f"{_SCRIPT_FUNCTIONS[name]}({self._arguments(node, name)})", _POSTFIX
        if name[:1].isupper():
            return f"new {self.target.type_name(name)}({self._arguments(node, name)})", _POSTFIX
        return f"{self._spelled(name)}({self._arguments(node, name)})", _POSTFIX

    def _method_call(self, node: ast.Call, function: ast.Attribute) -> Tuple[str, int]:
        owner = function.value
        if isinstance(owner, ast.Call) and isinstance(owner.func, ast.Name) and owner.func.id == "super":
            base = self.target.spelling.base_constructor if function.attr == "__init__" else f"super.{self.target.identifier(function.attr)}"
            return f"{base}({self._arguments(node, function.attr)})", _POSTFIX
        if function.attr == "join" and len(node.args) == 1 and not node.keywords:
            return f"{self._part(node.args[0], _POSTFIX)}.join({self._expression(owner)})", _POSTFIX
        method = _SCRIPT_METHODS.get(function.attr) or (function.attr if function.attr[:1].isupper() else self.target.identifier(function.attr))
        return f"{self._part(owner, _POSTFIX)}.{method}({self._arguments(node, function.attr)})", _POSTFIX

    def _arguments(self, node: ast.Call, called: str) -> str:
        """The call's arguments in order: its keyword arguments in the order the operation called names its parameters
        when the model declares it, else as one object after the others."""
        written = [self._expression(argument) for argument in node.args]
        keywords = [keyword for keyword in node.keywords]
        if any(keyword.arg is None for keyword in keywords):
            raise Untranslatable(node)
        if not keywords:
            return ", ".join(written)
        known = self.parameters.get(called)
        if known is not None:
            given = {keyword.arg: self._expression(keyword.value) for keyword in keywords}
            rest = [name for name in known if name not in {"self"}][len(node.args):]
            if set(given) <= set(rest):
                positional = [given.get(name, "undefined") for name in rest]
                while positional and positional[-1] == "undefined":
                    positional.pop()
                return ", ".join(written + positional)
        entries = ", ".join(f"{self.target.identifier(keyword.arg)}: {self._expression(keyword.value)}" for keyword in keywords)
        return ", ".join(written + [f"{{{entries}}}"])


# -- a script language to Python -----------------------------------------------------------------------------------


@dataclass
class _Token:
    kind: str  # name, number, string, template, punct, comment
    text: str
    start: int
    end: int
    line: int


_TOKEN = re.compile(
    r"(?P<space>[ \t\r]+)|(?P<newline>\n)|(?P<comment>//[^\n]*)|(?P<block>/\*.*?\*/)"
    r"|(?P<template>`(?:\\.|\$\{(?:[^{}]|\{[^{}]*\})*\}|[^`\\])*`)"
    r"|(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<number>\d+(?:\.\d+)?)|(?P<name>[A-Za-z_$][\w$]*)"
    r"|(?P<punct>===|!==|\*\*=|\.\.\.|=>|==|!=|<=|>=|&&|\|\||\?\?|\?\.|\+\+|--|\+=|-=|\*=|/=|%=|\*\*|[{}()\[\];,.<>+\-*/%=!?:&|^~])",
    re.DOTALL,
)


def _tokens(text: str) -> List[_Token]:
    found: List[_Token] = []
    line, position = 1, 0
    while position < len(text):
        match = _TOKEN.match(text, position)
        if match is None:
            raise Untranslatable(text[position:position + 20])
        kind = match.lastgroup or ""
        if kind not in ("space", "newline", "block"):
            found.append(_Token(kind, match.group(0), match.start(), match.end(), line))
        line += match.group(0).count("\n")
        position = match.end()
    return found


class _Comment(ast.stmt):
    """A comment line among a script body's statements, kept for the Python written from it."""

    _fields = ("text",)


# A script method and the Python method that does the same.
_PYTHON_METHODS = {value: key for key, value in _SCRIPT_METHODS.items()}
_PYTHON_FUNCTIONS = {"String": "str", "console.log": "print", "Math.abs": "abs", "Math.min": "min", "Math.max": "max"}


class ScriptReading:
    """A script body read into Python's syntax tree, statement by statement: a statement outside the subset is kept
    as its source text."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens = _tokens(text)
        self.position = 0

    # -- statements --

    def statements(self, end: str = "") -> List[ast.stmt | str]:
        """The statements up to the closing token end, or to the end of the body; each a Python statement, a comment,
        or, for one outside the subset, the source text it was written as."""
        found: List[ast.stmt | str] = []
        while self.position < len(self.tokens) and not self._at(end):
            if self._peek().kind == "comment":
                found.append(_Comment(text=self._next().text[2:].strip()))
                continue
            first = self.position
            last = self._statement_end(first)
            try:
                statement = self._statement()
                if self.position != last:
                    raise Untranslatable(statement)
                found.append(statement)
            except (Untranslatable, IndexError):
                self.position = last
                found.append(self.text[self.tokens[first].start : self.tokens[last - 1].end])
        return found

    def _statement_end(self, index: int) -> int:
        """The index past the last token of the statement that starts at index."""
        token = self.tokens[index]
        if token.text in ("if", "for", "while"):
            index = self._group_end(index + 1)
            index = self._body_end(index)
            while token.text == "if" and index < len(self.tokens) and self.tokens[index].text == "else":
                index = self._body_end(index + 1)
            return index
        if token.text == "{":
            return self._group_end(index)
        depth = 0
        while index < len(self.tokens):
            text = self.tokens[index].text
            if self.tokens[index].kind == "punct":
                depth += text in "([{" and len(text) == 1
                depth -= text in ")]}" and len(text) == 1
                if depth < 0:
                    return index
                if depth == 0 and text == ";":
                    return index + 1
            index += 1
        return index

    def _body_end(self, index: int) -> int:
        if index < len(self.tokens) and self.tokens[index].text == "if":
            return self._statement_end(index)
        return self._group_end(index) if index < len(self.tokens) and self.tokens[index].text == "{" else self._statement_end(index)

    def _group_end(self, index: int) -> int:
        """The index past the bracket that closes the one at index."""
        depth = 0
        while index < len(self.tokens):
            text = self.tokens[index].text
            if self.tokens[index].kind == "punct" and len(text) == 1 and text in "([{":
                depth += 1
            elif self.tokens[index].kind == "punct" and len(text) == 1 and text in ")]}":
                depth -= 1
                if depth == 0:
                    return index + 1
            index += 1
        return index

    def _statement(self) -> ast.stmt:
        token = self._peek()
        keyword = token.text if token.kind == "name" else ""
        if keyword in ("const", "let", "var"):
            return self._declaration()
        if keyword == "if":
            return self._if()
        if keyword == "for":
            return self._for()
        if keyword == "while":
            self._next()
            test = self._parenthesised()
            return ast.While(test=test, body=self._body(), orelse=[])
        if keyword == "return":
            self._next()
            value = None if self._at(";") else self.expression()
            self._end()
            return ast.Return(value=value)
        if keyword == "throw":
            self._next()
            raised = self.expression()
            self._end()
            return ast.Raise(exc=raised, cause=None)
        if keyword in ("break", "continue"):
            self._next()
            self._end()
            return ast.Break() if keyword == "break" else ast.Continue()
        return self._expression_statement()

    def _declaration(self) -> ast.stmt:
        self._next()
        name = self._expect_name()
        if self._at(":"):
            while not self._at("="):
                self._next()
        self._expect("=")
        value = self.expression()
        self._end()
        return ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=value)

    def _if(self) -> ast.If:
        self._next()
        test = self._parenthesised()
        body = self._body()
        orelse: List[ast.stmt] = []
        if self._at("else"):
            self._next()
            orelse = [self._if()] if self._at("if") else self._body()
        return ast.If(test=test, body=body, orelse=orelse)

    def _for(self) -> ast.For:
        self._next()
        self._expect("(")
        if self._peek().text in ("const", "let", "var"):
            self._next()
        name = self._expect_name()
        if self._at("of"):
            self._next()
            collection = self.expression()
            self._expect(")")
            return ast.For(target=ast.Name(id=name, ctx=ast.Store()), iter=collection, body=self._body(), orelse=[], type_comment=None)
        self._expect("=")
        start = self.expression()
        self._expect(";")
        if self._expect_name() != name or self._next().text != "<":
            raise Untranslatable(name)
        stop = self.expression()
        self._expect(";")
        if self._expect_name() != name or self._next().text != "++":
            raise Untranslatable(name)
        self._expect(")")
        arguments = [stop] if isinstance(start, ast.Constant) and start.value == 0 else [start, stop]
        call = ast.Call(func=ast.Name(id="range", ctx=ast.Load()), args=arguments, keywords=[])
        return ast.For(target=ast.Name(id=name, ctx=ast.Store()), iter=call, body=self._body(), orelse=[], type_comment=None)

    def _body(self) -> List[ast.stmt]:
        """A block in braces, or the one statement a branch holds without them; a statement in it outside the subset
        makes the whole statement that holds it untranslatable."""
        if not self._at("{"):
            return [self._statement()]
        self._next()
        found = self.statements("}")
        self._expect("}")
        if any(isinstance(statement, str) for statement in found):
            raise Untranslatable(found)
        return [statement for statement in found if not isinstance(statement, str)] or [ast.Pass()]

    def _expression_statement(self) -> ast.stmt:
        if self._at("super") and self.tokens[self.position + 1].text == "(":
            self._next()
            arguments = self._arguments()
            self._end()
            initialise = ast.Attribute(value=ast.Call(func=ast.Name(id="super", ctx=ast.Load()), args=[], keywords=[]), attr="__init__", ctx=ast.Load())
            return ast.Expr(value=ast.Call(func=initialise, args=arguments, keywords=[]))
        target = self.expression()
        token = self._peek() if self.position < len(self.tokens) else None
        if token is not None and token.text == "=":
            self._next()
            value = self.expression()
            self._end()
            return ast.Assign(targets=[self._stored(target)], value=value)
        if token is not None and token.text in ("+=", "-=", "*=", "/=", "%="):
            self._next()
            value = self.expression()
            self._end()
            return ast.AugAssign(target=self._stored(target), op=_AUGMENTED_OPERATORS[token.text](), value=value)
        if token is not None and token.text in ("++", "--"):
            self._next()
            self._end()
            operator = ast.Add() if token.text == "++" else ast.Sub()
            return ast.AugAssign(target=self._stored(target), op=operator, value=ast.Constant(value=1))
        self._end()
        return ast.Expr(value=target)

    def _stored(self, node: ast.expr) -> ast.expr:
        if not isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
            raise Untranslatable(node)
        node.ctx = ast.Store()
        return node

    def _end(self) -> None:
        if self.position < len(self.tokens) and self._at(";"):
            self._next()

    # -- expressions, from the loosest binding to the tightest --

    def expression(self) -> ast.expr:
        test = self._or()
        if not self._at("?"):
            return test
        self._next()
        body = self.expression()
        self._expect(":")
        return ast.IfExp(test=test, body=body, orelse=self.expression())

    def _or(self) -> ast.expr:
        return self._boolean("||", ast.Or, self._and)

    def _and(self) -> ast.expr:
        return self._boolean("&&", ast.And, self._equality)

    def _boolean(self, sign: str, operator: type, tighter) -> ast.expr:
        values = [tighter()]
        while self._at(sign):
            self._next()
            values.append(tighter())
        return values[0] if len(values) == 1 else ast.BoolOp(op=operator(), values=values)

    def _equality(self) -> ast.expr:
        left = self._relational()
        while self.position < len(self.tokens) and self._peek().text in ("===", "!==", "==", "!="):
            sign = self._next().text
            right = self._relational()
            is_none = isinstance(right, ast.Constant) and right.value is None
            if sign in ("===", "=="):
                operator = ast.Is() if is_none else ast.Eq()
            else:
                operator = ast.IsNot() if is_none else ast.NotEq()
            left = ast.Compare(left=left, ops=[operator], comparators=[right])
        return left

    def _relational(self) -> ast.expr:
        left = self._additive()
        signs = {"<": ast.Lt, "<=": ast.LtE, ">": ast.Gt, ">=": ast.GtE}
        while self.position < len(self.tokens) and (self._peek().text in signs or self._at("instanceof")):
            sign = self._next().text
            right = self._additive()
            if sign == "instanceof":
                left = ast.Call(func=ast.Name(id="isinstance", ctx=ast.Load()), args=[left, right], keywords=[])
            else:
                left = ast.Compare(left=left, ops=[signs[sign]()], comparators=[right])
        return left

    def _additive(self) -> ast.expr:
        return self._binary({"+": ast.Add, "-": ast.Sub}, self._multiplicative)

    def _multiplicative(self) -> ast.expr:
        return self._binary({"*": ast.Mult, "/": ast.Div, "%": ast.Mod}, self._exponent)

    def _exponent(self) -> ast.expr:
        return self._binary({"**": ast.Pow}, self._unary)

    def _binary(self, signs: dict, tighter) -> ast.expr:
        left = tighter()
        while self.position < len(self.tokens) and self._peek().kind == "punct" and self._peek().text in signs:
            operator = signs[self._next().text]
            left = ast.BinOp(left=left, op=operator(), right=tighter())
        return left

    def _unary(self) -> ast.expr:
        if self._at("!"):
            self._next()
            return ast.UnaryOp(op=ast.Not(), operand=self._unary())
        if self._at("-"):
            self._next()
            return ast.UnaryOp(op=ast.USub(), operand=self._unary())
        if self._at("..."):
            self._next()
            return ast.Starred(value=self._unary(), ctx=ast.Load())
        return self._postfix(self._primary())

    def _postfix(self, node: ast.expr) -> ast.expr:
        while self.position < len(self.tokens):
            if self._at("."):
                self._next()
                node = self._member(node, self._expect_name())
            elif self._at("("):
                node = self._called(node, self._arguments())
            elif self._at("["):
                self._next()
                index = self.expression()
                self._expect("]")
                node = ast.Subscript(value=node, slice=index, ctx=ast.Load())
            elif self._at("?.") or self._at("??"):
                raise Untranslatable(node)
            else:
                return node
        return node

    def _member(self, owner: ast.expr, name: str) -> ast.expr:
        if name == "length" and not self._at("("):
            return ast.Call(func=ast.Name(id="len", ctx=ast.Load()), args=[owner], keywords=[])
        return ast.Attribute(value=owner, attr=name, ctx=ast.Load())

    def _called(self, function: ast.expr, arguments: List[ast.expr]) -> ast.expr:
        """A call, as Python writes what the script calls: a method of a list or a string by Python's name for it,
        `filter` and `map` as a list comprehension, `includes` as `in`."""
        dotted = ast.unparse(function) if isinstance(function, (ast.Name, ast.Attribute)) else ""
        if dotted in _PYTHON_FUNCTIONS:
            return ast.Call(func=ast.Name(id=_PYTHON_FUNCTIONS[dotted], ctx=ast.Load()), args=arguments, keywords=[])
        if dotted == "Math.floor" and len(arguments) == 1 and isinstance(arguments[0], ast.BinOp) and isinstance(arguments[0].op, ast.Div):
            return ast.BinOp(left=arguments[0].left, op=ast.FloorDiv(), right=arguments[0].right)
        if not isinstance(function, ast.Attribute):
            return ast.Call(func=function, args=arguments, keywords=[])
        owner, method = function.value, function.attr
        if method == "includes" and len(arguments) == 1:
            return ast.Compare(left=arguments[0], ops=[ast.In()], comparators=[owner])
        if method == "join" and len(arguments) == 1:
            return ast.Call(func=ast.Attribute(value=arguments[0], attr="join", ctx=ast.Load()), args=[owner], keywords=[])
        if method in ("filter", "map") and len(arguments) == 1 and isinstance(arguments[0], ast.Lambda):
            return self._comprehension(owner, method, arguments[0])
        return ast.Call(func=ast.Attribute(value=owner, attr=_PYTHON_METHODS.get(method, method), ctx=ast.Load()), args=arguments, keywords=[])

    def _comprehension(self, owner: ast.expr, method: str, function: ast.Lambda) -> ast.ListComp:
        if len(function.args.args) != 1:
            raise Untranslatable(function)
        name = function.args.args[0].arg
        target = ast.Name(id=name, ctx=ast.Store())
        if method == "map" and isinstance(owner, ast.ListComp) and isinstance(owner.elt, ast.Name) and owner.elt.id == owner.generators[0].target.id == name:
            owner.elt = function.body
            return owner
        if method == "filter":
            generator = ast.comprehension(target=target, iter=owner, ifs=[function.body], is_async=0)
            return ast.ListComp(elt=ast.Name(id=name, ctx=ast.Load()), generators=[generator])
        generator = ast.comprehension(target=target, iter=owner, ifs=[], is_async=0)
        return ast.ListComp(elt=function.body, generators=[generator])

    def _arguments(self) -> List[ast.expr]:
        self._expect("(")
        found = []
        while not self._at(")"):
            found.append(self.expression())
            if self._at(","):
                self._next()
        self._expect(")")
        return found

    def _primary(self) -> ast.expr:
        token = self._next()
        if token.kind == "number":
            return ast.Constant(value=float(token.text) if "." in token.text else int(token.text))
        if token.kind == "string":
            return ast.Constant(value=ast.literal_eval(token.text) if token.text[0] == '"' else ast.literal_eval(token.text))
        if token.kind == "template":
            return self._template(token.text[1:-1])
        if token.text == "(":
            if self._arrow_ahead():
                return self._arrow()
            inner = self.expression()
            self._expect(")")
            return inner
        if token.text == "[":
            elements = []
            while not self._at("]"):
                elements.append(self.expression())
                if self._at(","):
                    self._next()
            self._expect("]")
            return ast.List(elts=elements, ctx=ast.Load())
        if token.text == "{":
            return self._object()
        if token.kind != "name":
            raise Untranslatable(token.text)
        return self._named(token)

    def _named(self, token: _Token) -> ast.expr:
        words = {"this": ast.Name(id="self", ctx=ast.Load()), "null": ast.Constant(value=None), "undefined": ast.Constant(value=None),
                 "true": ast.Constant(value=True), "false": ast.Constant(value=False)}
        if token.text in words:
            return words[token.text]
        if token.text == "new":
            name = self._expect_name()
            return ast.Call(func=ast.Name(id=PYTHON.type_name(name), ctx=ast.Load()), args=self._arguments(), keywords=[])
        if self._at("=>"):
            self._next()
            return ast.Lambda(args=self._lambda_arguments([token.text]), body=self.expression())
        return ast.Name(id=token.text, ctx=ast.Load())

    def _arrow_ahead(self) -> bool:
        """Whether the parenthesis just read opens an arrow function's parameters: its closing one is followed by =>."""
        closing = self._group_end(self.position - 1)
        return closing < len(self.tokens) and self.tokens[closing].text == "=>"

    def _arrow(self) -> ast.Lambda:
        names = []
        while not self._at(")"):
            names.append(self._expect_name())
            if self._at(":"):
                raise Untranslatable(names)
            if self._at(","):
                self._next()
        self._expect(")")
        self._expect("=>")
        if self._at("{"):
            raise Untranslatable(names)
        return ast.Lambda(args=self._lambda_arguments(names), body=self.expression())

    def _lambda_arguments(self, names: List[str]) -> ast.arguments:
        return ast.arguments(posonlyargs=[], args=[ast.arg(arg=name) for name in names], kwonlyargs=[], kw_defaults=[], defaults=[])

    def _object(self) -> ast.Dict:
        keys: List[Optional[ast.expr]] = []
        values: List[ast.expr] = []
        while not self._at("}"):
            if self._at("..."):
                self._next()
                keys.append(None)
                values.append(self.expression())
            else:
                key = self._next()
                name = ast.literal_eval(key.text) if key.kind == "string" else key.text
                keys.append(ast.Constant(value=name))
                if self._at(":"):
                    self._next()
                    values.append(self.expression())
                else:
                    values.append(ast.Name(id=name, ctx=ast.Load()))
            if self._at(","):
                self._next()
        self._expect("}")
        return ast.Dict(keys=keys, values=values)

    def _template(self, raw: str) -> ast.JoinedStr:
        values: List[ast.expr] = []
        position = 0
        for match in re.finditer(r"\$\{((?:[^{}]|\{[^{}]*\})*)\}", raw):
            if match.start() > position:
                values.append(ast.Constant(value=raw[position:match.start()].replace("\\`", "`")))
            inner = ScriptReading(match.group(1))
            values.append(ast.FormattedValue(value=inner.expression(), conversion=-1, format_spec=None))
            position = match.end()
        if position < len(raw):
            values.append(ast.Constant(value=raw[position:].replace("\\`", "`")))
        return ast.JoinedStr(values=values)

    # -- tokens --

    def _peek(self) -> _Token:
        return self.tokens[self.position]

    def _next(self) -> _Token:
        token = self.tokens[self.position]
        self.position += 1
        return token

    def _at(self, text: str) -> bool:
        return bool(text) and self.position < len(self.tokens) and self.tokens[self.position].text == text

    def _expect(self, text: str) -> None:
        if not self._at(text):
            raise Untranslatable(text)
        self._next()

    def _expect_name(self) -> str:
        token = self._next()
        if token.kind != "name":
            raise Untranslatable(token.text)
        return token.text

    def _parenthesised(self) -> ast.expr:
        self._expect("(")
        inner = self.expression()
        self._expect(")")
        return inner


_AUGMENTED_OPERATORS = {"+=": ast.Add, "-=": ast.Sub, "*=": ast.Mult, "/=": ast.Div, "%=": ast.Mod}


class ScriptToPython:
    """A script body written as Python writes it."""

    def translate(self, text: str) -> Optional[TranslatedBody]:
        try:
            reading = ScriptReading(textwrap.dedent(text))
        except Untranslatable:
            return None
        result = TranslatedBody()
        self._block(reading.statements(), 0, result)
        return result

    def _block(self, statements: Sequence[ast.stmt | str], depth: int, result: TranslatedBody) -> None:
        indent = PYTHON.indent * depth
        for statement in statements:
            if isinstance(statement, str):
                result.untranslated.append(statement)
                result.lines.append(f"{indent}{PYTHON.comment(f'{TYPESCRIPT.name} statement to translate:')}")
                result.lines.extend(f"{indent}{PYTHON.comment(line)}" for line in textwrap.dedent(statement).splitlines())
            elif isinstance(statement, _Comment):
                result.lines.append(f"{indent}{PYTHON.comment(statement.text)}")
            elif isinstance(statement, (ast.If, ast.For, ast.While)):
                self._compound(statement, depth, result)
            else:
                result.lines.append(f"{indent}{ast.unparse(ast.fix_missing_locations(statement))}")

    def _compound(self, statement: ast.If | ast.For | ast.While, depth: int, result: TranslatedBody, opening: str = "") -> None:
        indent = PYTHON.indent * depth
        if isinstance(statement, ast.For):
            head = f"for {ast.unparse(statement.target)} in {ast.unparse(ast.fix_missing_locations(statement.iter))}:"
        else:
            head = f"{opening or ('if' if isinstance(statement, ast.If) else 'while')} {ast.unparse(ast.fix_missing_locations(statement.test))}:"
        result.lines.append(f"{indent}{head}")
        self._block(statement.body, depth + 1, result)
        if not isinstance(statement, ast.If) or not statement.orelse:
            return
        if len(statement.orelse) == 1 and isinstance(statement.orelse[0], ast.If):
            self._compound(statement.orelse[0], depth, result, "elif")
            return
        result.lines.append(f"{indent}else:")
        self._block(statement.orelse, depth + 1, result)
