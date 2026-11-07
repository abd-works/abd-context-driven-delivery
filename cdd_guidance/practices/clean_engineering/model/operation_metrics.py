"""What the Clean Engineering rules measure in source: *SourceText* reads a span of any language's text, and
*PythonFunctionBody* reads a Python function from its syntax tree. The parsers ask them while they read a class or an
operation, and keep the answers as the node's facts."""

from __future__ import annotations

import ast
import re

_CATCH = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{")
_PY_EXCEPT = re.compile(r"\bexcept\s*(?::|\([^)]*\)\s*:)")
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_NUMBER = re.compile(r"\b(\d+(?:\.\d+)?)\b")
_REGEXP_LITERAL = re.compile(r"/(?:\\.|[^/\\])*/[gimsuy]*")
_CONTROL_KEYWORD = re.compile(r"\b(?:else|try|do|finally|catch)\s*$")
_CONTROL_CONDITION = re.compile(r"\b(?:if|for|while|switch|catch)\s*$")
_CONTROL_LINE = re.compile(r"(if|for|while|elif)\b")
# TypeScript's optional catch binding `catch {` is intentional, not a handler that catches everything.
_OPTIONAL_CATCH_BINDING = re.compile(r"\bcatch\s*\{")
_EMPTY_CATCH_BINDING = re.compile(r"\bcatch\s*\(\s*\)")
_BARE_EXCEPT = re.compile(r"\bexcept\s*:")
_PASS_LINE = re.compile(r"^\s*pass\b", re.M)
_IGNORED_CATCH_BODIES = frozenset({";", "pass", "// ignore", "/* ignore */"})
_PEER_PRIVATE_FIELD = re.compile(r"(\w+)\._(\w+)")
_SAFE_NUMBERS = {
    0,
    1,
    2,
    3,
    4,
    5,
    -1,
    0.0,
    1.0,
    0.5,
    8,
    9,
    10,
    100,
    200,
    201,
    204,
    301,
    302,
    400,
    401,
    403,
    404,
    409,
    422,
    500,
    502,
    503,
}
_NARRATIVE_COMMENT = re.compile(
    r"(?:transient|value object|carries|implementation|see also|cross-ref)",
    re.IGNORECASE,
)
_THROW = re.compile(r"\bthrow\b")
# The catch ends by handing back a stand-in value, so the caller never learns the call failed.
_FALLBACK_RETURN = re.compile(r"\breturn\s*(?:null|undefined|false|true|\[\s*\]|\{\s*\}|''|\"\"|-?\d+)?\s*;?\s*$")
_OWN_RECEIVERS = frozenset({"this", "self", "super"})
_WIRED_PEER_FIELDS = frozenset({"repository", "repo"})
_CATCH_ALL_TYPES = frozenset({"Exception", "BaseException"})
_IO_CALL = re.compile(
    r"\b(?:open|read|write|save|fetch|load|store|send|post|put|delete|upload|download|print)\w*\s*\(",
    re.IGNORECASE,
)
_DOMAIN_CALL = re.compile(
    r"\b(?:calculate|compute|validate|parse|transform|convert|aggregate|total|sum|apply|build)\w*\s*\(",
    re.IGNORECASE,
)
_EDGE_RAISE = re.compile(
    r"if\s+(?:not\s+\w+|len\s*\([^)]+\)\s*(?:==|<=)\s*0|\w+\s+is\s+None)\s*:[^\n]*\n(?:[^\n]*\n){0,3}\s*raise\b",
    re.MULTILINE,
)
_EDGE_RAISE_BRACE = re.compile(
    r"if\s*\(\s*(?:!\s*\w+|len\s*\([^)]+\)\s*===?\s*0|\w+\s*===?\s*null)\s*\)[^{]*\{[^\}]*raise\b",
    re.MULTILINE | re.DOTALL,
)
_EDGE_RAISE_MESSAGE = re.compile(r"raise\s+\w*(?:Error|Exception)\([^)]*(?:empty|not found|missing|none)", re.I)
_EDGE_GUARD = re.compile(r"if\s+(?:not\s+|len\s*\([^)]*\)\s*==\s*0)")
_EMPTY_EXCEPTION = re.compile(r"raise\s+(\w+(?:Error|Exception))\s*\(\s*([\"']?)\s*\2\s*\)")
_GENERIC_EXCEPTION = re.compile(r"raise\s+\w+(?:Error|Exception)\s*\(\s*f?[\"'](?:error|failed|invalid)[\"']\s*\)", re.I)
# Nested property writes (this.token, this.validation.verified) — not helper-local state.
_COORDINATED_MUTATION = re.compile(r"\b(?:self|this)(?:\.\w+)+\s*=")
_RETURN = re.compile(r"\breturn\b")
_VOID_RETURN = re.compile(r"->\s*None\b|: void\b")
_THROWS = re.compile(r"\b(?:throw|raise)\b")
_PRIVATE_REACH = re.compile(r"(?<![\w.])\w+\._\w+")
_PROTOTYPE_SWAP = re.compile(r"\bObject\.setPrototypeOf\s*\(|\.__proto__\s*=(?!=)|\.__class__\s*=(?!=)")
_BOLD_INTERACTION = re.compile(r"\*\*Interaction:\*\*", re.I)
_BOLD_INVARIANT_BULLET = re.compile(r"^\s*[-*]\s+\*\*Invariant:\*\*", re.I | re.M)
_L_TAG = re.compile(r"<!--\s*L\s*-->", re.I)
_LANGUAGE_HEADING = re.compile(r"^#{1,3}\s+Language\b", re.I)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")
_META = re.compile(
    r"do\s+\*\*not\*\*\s+invent|do not invent|never invent|parallel symbol|as collaboration markers",
    re.I,
)
# Below these sizes a body is too small for the mixed-concerns and unrecorded-mutation measures to mean anything.
MIN_SIGNAL_BODY = 40
MIN_MUTATION_BODY = 30
MIN_DELEGATION_LINES = 12


class SourceText:
    """A span of source in any language — an operation body, a class, a markdown card — and what the rules measure in
    it. Brace-language measures count `{` blocks; Python measures count indentation."""

    def __init__(self, text: str) -> None:
        self._text = text

    def control_flow_depth(self) -> int:
        """The deepest nesting of if/for/while, by indentation or by control-flow braces, whichever is deeper."""
        stack: list[int] = []
        deepest = 0
        for line in self._text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
            indent = len(line.expandtabs()) - len(line.lstrip())
            while stack and indent <= stack[-1]:
                stack.pop()
            if _CONTROL_LINE.match(stripped):
                stack.append(indent)
                deepest = max(deepest, len(stack))
        return max(deepest, self._brace_depth())

    def has_bare_catch(self) -> bool:
        if _OPTIONAL_CATCH_BINDING.search(self._text):
            return False
        return bool(_EMPTY_CATCH_BINDING.search(self._text) or _BARE_EXCEPT.search(self._text))

    def swallows_exceptions(self) -> bool:
        """An empty catch, or one that hands back a fallback value without throwing again."""
        for match in _CATCH.finditer(self._text):
            catch_body = self._brace_body(match.end() - 1)
            if catch_body is None:
                continue
            stripped = catch_body.strip()
            if not stripped or stripped in _IGNORED_CATCH_BODIES or self._returns_fallback(stripped):
                return True
        return any(_PASS_LINE.match(self._text[match.end() :]) for match in _PY_EXCEPT.finditer(self._text))

    def unnamed_numbers(self) -> list[str]:
        """Each number literal outside strings and regular expressions that no name explains."""
        code = _REGEXP_LITERAL.sub('""', _STRING.sub('""', self._text))
        return [raw for raw in _NUMBER.findall(code) if float(raw) not in _SAFE_NUMBERS]

    def reaches_peer_private(self, parameter_names: frozenset[str] = frozenset()) -> bool:
        """True when the body reads another object's ``._`` field (not ``this._`` / ``self._``). Copying a field from a
        parameter of the same type into the same field of this object is not a reach."""
        for match in _PEER_PRIVATE_FIELD.finditer(self._text):
            receiver, field = match.group(1), match.group(2)
            if receiver in _OWN_RECEIVERS or field in _WIRED_PEER_FIELDS:
                continue
            if receiver in parameter_names and self._copies_same_field(receiver, field):
                continue
            return True
        return False

    def mixes_io_and_domain(self) -> bool:
        """A body long enough to mean something that calls both I/O and a domain calculation."""
        return len(self._text.strip()) >= MIN_SIGNAL_BODY and self.calls_io_and_domain()

    def calls_io_and_domain(self) -> bool:
        return bool(_IO_CALL.search(self._text) and _DOMAIN_CALL.search(self._text))

    def raises_on_empty(self) -> bool:
        if _EDGE_RAISE.search(self._text) or _EDGE_RAISE_BRACE.search(self._text):
            return True
        return bool(_EDGE_RAISE_MESSAGE.search(self._text) and _EDGE_GUARD.search(self._text))

    def exception_without_message(self) -> str:
        found = _EMPTY_EXCEPTION.search(self._text)
        return found.group(1) if found else ""

    def generic_exception_message(self) -> bool:
        return bool(_GENERIC_EXCEPTION.search(self._text))

    def mutates_without_record(self) -> bool:
        text = self._text
        if len(text.strip()) < MIN_MUTATION_BODY or len(_COORDINATED_MUTATION.findall(text)) <= 1:
            return False
        return not (_RETURN.search(text) or _VOID_RETURN.search(text) or _THROWS.search(text))

    def private_reach(self) -> bool:
        return bool(_PRIVATE_REACH.search(self._text))

    def has_prose_comment(self, hash_only: bool = False) -> bool:
        for line in self._text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and _NARRATIVE_COMMENT.search(stripped):
                return True
            if not hash_only and "//" in stripped and _NARRATIVE_COMMENT.search(stripped):
                return True
        return False

    def prototype_swap(self, start_line: int) -> dict:
        """The code that swaps an object's class and the line it is on, when the text does; empty when it does not."""
        found = _PROTOTYPE_SWAP.search(self._text)
        if found is None:
            return {}
        return {"code": found.group(0).strip(), "line": start_line + self._text.count("\n", 0, found.start())}

    def markdown_bullet_lines(self) -> dict:
        """Bold Interaction / Invariant bullets when the span is markdown; empty for code."""
        if not self._text.strip() or not self._text.lstrip().startswith("#"):
            return {}
        interactions: list[int] = []
        invariants: list[int] = []
        in_language = False
        for line_number, line in enumerate(self._text.splitlines(), start=1):
            in_language = _LANGUAGE_HEADING.match(line) is not None or (in_language and not _ANY_HEADING.match(line))
            if _META.search(line):
                continue
            if _BOLD_INTERACTION.search(line):
                interactions.append(line_number)
            if _BOLD_INVARIANT_BULLET.search(line) and not (in_language or _L_TAG.search(line)):
                invariants.append(line_number)
        return {"bold_interaction_lines": interactions, "bold_invariant_lines": invariants}

    def _brace_body(self, open_index: int) -> str | None:
        text = self._text
        if open_index >= len(text) or text[open_index] != "{":
            return None
        depth = 0
        for index in range(open_index, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    return text[open_index + 1 : index]
        return None

    def _brace_depth(self) -> int:
        """Count only the blocks control flow opens: JSX containers, object literals and arrow bodies nest no logic."""
        code = _STRING.sub('""', self._text)
        opens_control: list[bool] = []
        deepest = 0
        for index, character in enumerate(code):
            if character == "{":
                opens_control.append(self._opens_control_block(code[:index]))
                deepest = max(deepest, opens_control.count(True))
            elif character == "}" and opens_control:
                opens_control.pop()
        return deepest

    def _opens_control_block(self, before: str) -> bool:
        head = before.rstrip()
        if _CONTROL_KEYWORD.search(head):
            return True
        if not head.endswith(")"):
            return False
        opening = self._matching_open_paren(head)
        return opening >= 0 and _CONTROL_CONDITION.search(head[:opening]) is not None

    def _matching_open_paren(self, head: str) -> int:
        depth = 0
        for index in range(len(head) - 1, -1, -1):
            if head[index] == ")":
                depth += 1
            elif head[index] == "(":
                depth -= 1
                if depth == 0:
                    return index
        return -1

    def _returns_fallback(self, catch_body: str) -> bool:
        return _THROW.search(catch_body) is None and _FALLBACK_RETURN.search(catch_body) is not None

    def _copies_same_field(self, receiver: str, field: str) -> bool:
        """``this._field = receiver._field`` (or public ``field``) — an aggregate copying from a peer instance."""
        copy = rf"(?:this|self)\._?{re.escape(field)}\s*=\s*{re.escape(receiver)}\._?{re.escape(field)}\b"
        return bool(re.search(copy, self._text))


class PythonFunctionBody:
    """A Python function read from its syntax tree, and what the rules measure in it."""

    def __init__(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._node = node

    def control_flow_depth(self) -> int:
        return self._deepest_block(self._node.body, 0)

    def except_flags(self) -> tuple[bool, bool]:
        """(catches everything, swallows a failure). A bare ``except`` catches everything. So does ``except Exception``
        that never raises again: it returns or substitutes a fallback for every failure, the broken invariant included."""
        bare = False
        swallow = False
        for child in ast.walk(self._node):
            if not isinstance(child, ast.ExceptHandler):
                continue
            reraises = any(isinstance(inner, ast.Raise) for inner in ast.walk(child))
            catch_all = child.type is None or (self._catches_every_exception(child.type) and not reraises)
            bare = bare or catch_all
            swallow = swallow or self._handler_ignores(child.body) or (catch_all and not reraises)
        return bare, swallow

    def unnamed_numbers(self) -> list[str]:
        return [
            str(child.value)
            for child in ast.walk(self._node)
            if isinstance(child, ast.Constant)
            and isinstance(child.value, (int, float))
            and not isinstance(child.value, bool)
            and float(child.value) not in _SAFE_NUMBERS
        ]

    def reaches_peer_private(self) -> bool:
        """True when the function reads a ``_`` field of one of its parameters, other than copying that field into the
        same field of this object."""
        params = {a.arg for a in self._node.args.args if a.arg != "self"}
        params.update(a.arg for a in self._node.args.kwonlyargs)
        for child in ast.walk(self._node):
            if not (isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name)):
                continue
            if child.value.id not in params or not child.attr.startswith("_"):
                continue
            if child.attr.lstrip("_") in _WIRED_PEER_FIELDS or self._copies_same_field(child.value.id, child.attr):
                continue
            return True
        return False

    def packed_parameters(self) -> dict[str, int]:
        """Each parameter that carries several values, with how many: a tuple the body unpacks (``x, y = rest``), and a
        ``*args`` the parser leaves out of the parameter list. A packed tuple hides real parameters from the count."""
        names = {arg.arg for arg in self._node.args.args + self._node.args.kwonlyargs}
        packed: dict[str, int] = {}
        if self._node.args.vararg is not None:
            packed[self._node.args.vararg.arg] = 1
            names.add(self._node.args.vararg.arg)
        for child in ast.walk(self._node):
            if not isinstance(child, ast.Assign) or not isinstance(child.value, ast.Name) or child.value.id not in names:
                continue
            for target in child.targets:
                if isinstance(target, (ast.Tuple, ast.List)):
                    packed[child.value.id] = max(packed.get(child.value.id, 0), len(target.elts))
        return packed

    def _deepest_block(self, block: list[ast.stmt], depth: int) -> int:
        deepest = depth
        for stmt in block:
            for inner in self._nested_blocks(stmt):
                deepest = max(deepest, self._deepest_block(inner, depth + 1))
        return deepest

    def _nested_blocks(self, stmt: ast.stmt) -> list[list[ast.stmt]]:
        if isinstance(stmt, ast.If):
            return [stmt.body] + ([stmt.orelse] if stmt.orelse else [])
        if isinstance(stmt, (ast.For, ast.While, ast.With)):
            return [stmt.body]
        if isinstance(stmt, ast.Try):
            return [stmt.body] + [handler.body for handler in stmt.handlers]
        return []

    def _copies_same_field(self, param_name: str, attr: str) -> bool:
        field = attr.lstrip("_")
        for child in ast.walk(self._node):
            if not isinstance(child, ast.Assign) or len(child.targets) != 1:
                continue
            target, value = child.targets[0], child.value
            if not isinstance(target, ast.Attribute) or not isinstance(value, ast.Attribute):
                continue
            if not isinstance(target.value, ast.Name) or target.value.id != "self":
                continue
            if not isinstance(value.value, ast.Name) or value.value.id != param_name:
                continue
            if target.attr.lstrip("_") == field and value.attr.lstrip("_") == field:
                return True
        return False

    def _catches_every_exception(self, caught: ast.expr) -> bool:
        if isinstance(caught, ast.Tuple):
            return any(self._catches_every_exception(element) for element in caught.elts)
        return isinstance(caught, ast.Name) and caught.id in _CATCH_ALL_TYPES

    def _handler_ignores(self, body: list[ast.stmt]) -> bool:
        """An empty handler, or one that only says ``pass`` or ``...``."""
        return all(
            isinstance(stmt, ast.Pass) or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
            for stmt in body
        )
