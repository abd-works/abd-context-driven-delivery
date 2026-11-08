"""What the Clean Engineering rules measure in source: *SourceText* reads a span of any language's text, and
*PythonFunctionBody* reads a Python function from its syntax tree. The parsers ask them while they read a class or an
operation, and keep the answers as the node's facts."""

from __future__ import annotations

import ast
import builtins
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
# `new Repo(` in a brace-language body, and what makes the construction a failure thrown or a parameter's default:
# `throw new`, `?? new`, `|| new`, right before it.
_NEW_CLASS = re.compile(r"\bnew\s+([A-Z][\w$]*)\s*\(")
_THROWN_OR_DEFAULTED = re.compile(r"(?:\bthrow|\?\?|\|\|)\s*$")
# A name a construction's arguments read: not a member after a dot, and not a function or class it calls.
_ARGUMENT_NAME = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)\b(?!\s*\()")
# A name a brace-language body declares, which it then holds: `const x =`, `let x`, `var x`.
_DECLARED_LOCAL = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)")
_SCRIPT_VALUES = frozenset({"true", "false", "null", "undefined", "typeof", "instanceof", "as", "void", "await", "new"})
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
    r"if\s+(?:not\s+\w+|len\s*\([^)]+\)\s*(?:==|<=)\s*0|\w+\s+is\s+None)\s*:[^\n]*\n(?:[^\n]*\n){0,3}\s*raise\b([^\n]*)",
    re.MULTILINE,
)
_EDGE_RAISE_BRACE = re.compile(
    r"if\s*\(\s*(?:!\s*\w+|len\s*\([^)]+\)\s*===?\s*0|\w+\s*===?\s*null)\s*\)[^{]*\{[^\}]*raise\b([^\n]*)",
    re.MULTILINE | re.DOTALL,
)
# What a raise names: `UnknownPractice(key, known)` names the failure `UnknownPractice` and gives it what was asked for.
_RAISED_WITH_CONTEXT = re.compile(r"^\s*(?:new\s+)?([A-Z]\w*)\s*\(\s*[^)\s]")
# The failures a language gives every program; raising one on an empty value says nothing about the domain.
_BUILTIN_FAILURES = frozenset(
    {name for name in dir(builtins) if isinstance(getattr(builtins, name), type) and issubclass(getattr(builtins, name), BaseException)}
    | {"Error", "RangeError", "ReferenceError", "IllegalArgumentException", "IllegalStateException", "RuntimeException"}
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
_PRIVATE_REACH = re.compile(r"(?<![\w.])(\w+)\.(_\w+)")
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


def names_call_io_and_domain(callees: list[str]) -> bool:
    """True when the operations called include both I/O, such as `save`, and a domain calculation, such as `total`: the
    last part of each callee's name is the operation it calls."""
    called = "\n".join(f"{callee.split('.')[-1]}(" for callee in callees if callee)
    return bool(_IO_CALL.search(called) and _DOMAIN_CALL.search(called))


class SourceText:
    """A span of source in any language — an operation body, a class, a markdown card — and what the rules measure in
    it. Brace-language measures count `{` blocks; Python measures count indentation."""

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def closing_bracket(self, open_at: int, opener: str = "{", closer: str = "}") -> int | None:
        """The index of the bracket that closes the one at open_at; None when the text never closes it. Every reader
        of brace-language code asks this one matcher."""
        depth = 0
        for index in range(open_at, len(self._text)):
            if self._text[index] == opener:
                depth += 1
            elif self._text[index] == closer:
                depth -= 1
                if depth == 0:
                    return index
        return None

    def braced(self, open_at: int) -> str | None:
        """The text inside the `{` at open_at and the `}` that closes it; None when open_at is no `{` or nothing
        closes it."""
        if open_at >= len(self._text) or self._text[open_at] != "{":
            return None
        close = self.closing_bracket(open_at)
        return self._text[open_at + 1 : close] if close is not None else None

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
            catch_body = self.braced(match.end() - 1)
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

    def built_collaborators(self, parameter_names: frozenset[str], start_line: int) -> list[tuple[str, int]]:
        """The classes this brace-language constructor body builds with `new` that a caller cannot hand it, each with
        its line, read as ``PythonFunctionBody.built_collaborators`` reads Python: a class it throws, the default it
        builds for a parameter (``repo ?? new Repo()``, ``repo || new Repo()``), and a part it builds from its own state
        (``this``, its parameters, its locals, or constants) are left out."""
        code = _STRING.sub('""', self._text)
        unquoted = SourceText(code)
        owned = parameter_names | _OWN_RECEIVERS | set(_DECLARED_LOCAL.findall(code)) | _SCRIPT_VALUES
        found: list[tuple[str, int]] = []
        for match in _NEW_CLASS.finditer(code):
            if _THROWN_OR_DEFAULTED.search(code[: match.start()]):
                continue
            close = unquoted.closing_bracket(match.end() - 1, "(", ")")
            arguments = code[match.end() : close if close is not None else len(code)]
            if arguments.strip() and all(name in owned or name.isupper() for name in _ARGUMENT_NAME.findall(arguments)):
                continue
            found.append((match.group(1), start_line + code.count("\n", 0, match.start())))
        return found

    def mixes_io_and_domain(self) -> bool:
        """A body long enough to mean something that calls both I/O and a domain calculation."""
        return len(self._text.strip()) >= MIN_SIGNAL_BODY and self.calls_io_and_domain()

    def calls_io_and_domain(self) -> bool:
        return bool(_IO_CALL.search(self._text) and _DOMAIN_CALL.search(self._text))

    def raises_on_empty(self) -> bool:
        """True when the body raises on an empty or missing value. A raise of a failure the program declares, given
        what was asked for, such as ``raise UnknownPractice(key, known)`` when no practice has the key, reports a broken
        call rather than an ordinary empty case, so it is left out."""
        for pattern in (_EDGE_RAISE, _EDGE_RAISE_BRACE):
            if any(not _names_broken_call(match.group(1)) for match in pattern.finditer(self._text)):
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
        """True when the body reads a ``_`` member of something other than itself: ``order._lines``, not
        ``self._lines``, ``cls._registry``, or a dunder such as ``type(x).__name__``."""
        return any(
            match.group(1) not in _OWN_RECEIVERS | {"cls"} and not match.group(2).endswith("__")
            for match in _PRIVATE_REACH.finditer(_STRING.sub('""', self._text))
        )

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

    def line_of(self, index: int) -> int:
        """The line, counted from 1, holding the character at index. Rules report a finding by its line, so a fact
        records the line its match starts on."""
        return self._text.count("\n", 0, index) + 1

    def hits(self, pattern: re.Pattern[str]) -> list[list]:
        """[line, matched code] for each match of pattern."""
        return [[self.line_of(match.start()), match.group(0).strip()] for match in pattern.finditer(self._text)]

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

    def built_collaborators(self) -> list[tuple[str, int]]:
        """The classes this constructor builds that a caller cannot hand it, each with its line.

        A class it raises is a failure, not a collaborator. One it builds as the default of a parameter a caller may
        pass (``repo if repo is not None else Repo()``, ``repo or Repo()``, a default in the signature) can be swapped.
        One it builds from its own state, that is from itself, its parameters, values it computes from them, or
        constants, is a part it owns. What is left is built from nothing, or from something outside the object, such
        as a global or a call that reaches the environment, and the caller can never replace it."""
        replaceable = self._raised_or_defaulted()
        owned = self._owned_names()
        return [
            (child.func.id, child.lineno)
            for stmt in self._node.body
            for child in ast.walk(stmt)
            if isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id[:1].isupper()
            and id(child) not in replaceable
            and not _built_from(child, owned)
        ]

    def _parameter_names(self) -> set[str]:
        arguments = self._node.args
        named = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
        extra = [item for item in (arguments.vararg, arguments.kwarg) if item is not None]
        return {item.arg for item in named + extra}

    def _owned_names(self) -> set[str]:
        """Itself, its parameters, and every name its body assigns: what the constructor holds or computes."""
        stored = {
            child.id
            for stmt in self._node.body
            for child in ast.walk(stmt)
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
        }
        return self._parameter_names() | stored

    def _raised_or_defaulted(self) -> set[int]:
        """The constructions a caller can replace, and the failures it raises, by node identity."""
        parameters = self._parameter_names() - {"self"}
        found: set[int] = set()
        for stmt in self._node.body:
            for child in ast.walk(stmt):
                if isinstance(child, ast.Raise) and isinstance(child.exc, ast.Call):
                    found.add(id(child.exc))
                elif isinstance(child, ast.IfExp) and {_name_of(child.body), _name_of(child.orelse)} & parameters:
                    # `repo if repo is not None else Repo()`: the parameter, or the default built in its place.
                    found.update(id(branch) for branch in (child.body, child.orelse) if isinstance(branch, ast.Call))
                elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.Or) and _name_of(child.values[0]) in parameters:
                    # `repo or Repo()`.
                    found.update(id(value) for value in child.values[1:] if isinstance(value, ast.Call))
                elif isinstance(child, ast.If) and _absent_parameter(child.test) in parameters:
                    # `if repo is None: repo = Repo()`.
                    found.update(
                        id(inner.value) for inner in child.body if isinstance(inner, ast.Assign) and isinstance(inner.value, ast.Call)
                    )
        return found

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


def _names_broken_call(raised: str) -> bool:
    """A raise of a failure the program declares, given the value it could not use: `UnknownPractice(key, known)`."""
    named = _RAISED_WITH_CONTEXT.match(raised)
    return named is not None and named.group(1) not in _BUILTIN_FAILURES


def _name_of(expression: ast.expr) -> str:
    """The name an expression is, when it is a bare name; empty otherwise."""
    return expression.id if isinstance(expression, ast.Name) else ""


def _absent_parameter(test: ast.expr) -> str:
    """The name a test asks is missing, `x is None` or `not x`; empty for any other test."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _name_of(test.operand)
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Is):
        compared = test.comparators[0]
        if isinstance(compared, ast.Constant) and compared.value is None:
            return _name_of(test.left)
    return ""


def _built_from(construction: ast.Call, owned: set[str]) -> bool:
    """A construction given only what the constructor owns: every name its arguments read is one the constructor holds
    or computes, a constant spelled in capitals, or a builtin; a function or class it calls is judged on its own. A
    construction given nothing has no tie to its owner."""
    arguments = [*construction.args, *(keyword.value for keyword in construction.keywords)]
    if not arguments:
        return False
    nodes = [child for argument in arguments for child in ast.walk(argument)]
    # A comprehension's or a lambda's own names are bound inside the argument.
    bound = {child.id for child in nodes if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)}
    bound |= {child.arg for child in nodes if isinstance(child, ast.arg)}
    called = {id(child.func) for child in nodes if isinstance(child, ast.Call)}
    return all(
        child.id in owned or child.id in bound or child.id.isupper() or hasattr(builtins, child.id)
        for child in nodes
        if isinstance(child, ast.Name) and id(child) not in called
    )
