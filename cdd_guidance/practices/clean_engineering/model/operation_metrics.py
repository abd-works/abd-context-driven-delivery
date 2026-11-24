"""What the Clean Engineering rules measure in source: *SourceText* reads a span of any language's text, and
*PythonFunctionBody* reads a Python function from its syntax tree. The parsers ask them while they read a class or an
operation, and keep the answers as the node's facts."""

from __future__ import annotations

import ast
import builtins
import re
import sys
import textwrap

from cdd_guidance.practices.source_code import MeasuredBody
from cdd_guidance.practices.source_code.source_text import OWN_CLASS_RECEIVERS, OWN_RECEIVERS, SAFE_NUMBERS, STRING_LITERAL, WIRED_PEER_FIELDS, is_dunder

# The dunders Python calls with another object of the same class as the operand: comparison and arithmetic.
_PEER_OPERAND_DUNDERS = frozenset(
    {"__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__", "__add__", "__sub__", "__or__", "__and__"}
)
_CATCH_ALL_TYPES = frozenset({"Exception", "BaseException"})
# The top-level modules of Python's standard library, whose documented members include underscore functions such as
# `os._exit` and `sys._getframe`.
_STANDARD_MODULES = frozenset(name for name in sys.stdlib_module_names if not name.startswith("_"))
_BOLD_INTERACTION = re.compile(r"\*\*Interaction:\*\*", re.I)
_BOLD_INVARIANT_BULLET = re.compile(r"^\s*[-*]\s+\*\*Invariant:\*\*", re.I | re.M)
_L_TAG = re.compile(r"<!--\s*L\s*-->", re.I)
_LANGUAGE_HEADING = re.compile(r"^#{1,3}\s+Language\b", re.I)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")
_META = re.compile(
    r"do\s+\*\*not\*\*\s+invent|do not invent|never invent|parallel symbol|as collaboration markers",
    re.I,
)
# What the brace-language statement count reads: a comment, a `{` that opens a block rather than an object literal, and
# a line that carries on the statement before it, such as `} else {` or `});`.
_STRING_OR_COMMENT = re.compile(r"/\*[\s\S]*?\*/|//[^\n]*|" + STRING_LITERAL.pattern)
_OPENS_BLOCK = re.compile(r"(?:\)|=>|\belse|\btry|\bfinally|\bdo)\s*$")
_CONTINUES_STATEMENT = re.compile(r"^[)\]}]")
_BLOCK = "block"
MIN_DELEGATION_LINES = 12


class CardBullets:
    """<<Value Object>> The bold Interaction and Invariant bullets of a span that is a markdown card, by line; a span
    of code has none."""

    def __init__(self, text: str) -> None:
        # The lines, counted from 1, of each bold Interaction bullet and each bold Invariant bullet outside a language
        # section; none of either for a span that is not markdown.
        self.interaction_lines: list[int] = []
        self.invariant_lines: list[int] = []
        if text.strip() and text.lstrip().startswith("#"):
            self._read(text)

    def _read(self, text: str) -> None:
        in_language = False
        for line_number, line in enumerate(text.splitlines(), start=1):
            in_language = _LANGUAGE_HEADING.match(line) is not None or (in_language and not _ANY_HEADING.match(line))
            if _META.search(line):
                continue
            if _BOLD_INTERACTION.search(line):
                self.interaction_lines.append(line_number)
            if _BOLD_INVARIANT_BULLET.search(line) and not (in_language or _L_TAG.search(line)):
                self.invariant_lines.append(line_number)


class StatementCount:
    """How many statements an operation's body holds: what `keep-operations-small-focused` measures. A statement that
    spans several lines, such as a call, a list, or a string written over many lines, counts once, and the signature and
    the docstring are no statements. A Python body is counted from its syntax tree; a brace-language body counts each
    line that starts a statement outside any open bracket, so the lines inside a call, an array, an object literal, or
    a JSX expression belong to the statement that opened them."""

    def __init__(self, body: str, python: bool) -> None:
        self._body = body
        self._python = python

    def count(self) -> int | None:
        """The statements in the body; none for an empty body or Python text that does not parse on its own."""
        if not self._body.strip():
            return None
        return self._python_statements() if self._python else self._brace_statements()

    def _python_statements(self) -> int | None:
        try:
            tree = ast.parse(textwrap.dedent(self._body))
        except SyntaxError:
            return None
        return sum(1 for child in ast.walk(tree) if isinstance(child, ast.stmt) and not self._is_docstring(child))

    def _brace_statements(self) -> int:
        code = _STRING_OR_COMMENT.sub(lambda found: "" if found.group(0)[:1] == "/" else '""', self._body)
        open_brackets: list[str] = []
        statements = 0
        for line in code.splitlines():
            stripped = line.strip()
            in_block = not open_brackets or open_brackets[-1] == _BLOCK
            if in_block and stripped and not _CONTINUES_STATEMENT.match(stripped):
                statements += 1
            self._follow_brackets(line, open_brackets)
        return statements

    def _follow_brackets(self, line: str, open_brackets: list[str]) -> None:
        """Keep the brackets still open after the line. A `{` after a condition, an arrow, or `else`, `try`, `finally`,
        or `do` opens a block, whose lines are statements of their own, even inside a call's arguments (a callback); any
        other `{` opens an object literal, which belongs to its statement as a `(` or a `[` does."""
        for index, character in enumerate(line):
            if character in ")]}":
                del open_brackets[-1:]
            elif character in "([{":
                open_brackets.append(_BLOCK if character == "{" and _OPENS_BLOCK.search(line[:index]) else character)

    def _is_docstring(self, statement: ast.stmt) -> bool:
        """A bare string: the docstring of a function, or text no statement uses."""
        value = statement.value if isinstance(statement, ast.Expr) else None
        return isinstance(value, ast.Constant) and isinstance(value.value, str)


class PythonFunctionBody(MeasuredBody):
    """A Python function read from its syntax tree, and what the rules measure in it. A method keeps the class that
    declares it, since what counts as reaching another object's private state depends on that class; a module function
    has none. It holds the objects it builds and reads, read from the tree."""

    def __init__(self, node: ast.FunctionDef | ast.AsyncFunctionDef, owner: ast.ClassDef | None) -> None:
        self._node = node
        self._owner = owner
        # The objects it builds and reads, a part it makes once.
        self.collaborators = FunctionCollaborators(node, owner)

    def control_flow_depth(self) -> int:
        return self._deepest_block(self._node.body, 0)

    def decorated(self, name: str) -> bool:
        """True when a decorator with no arguments of that name marks the function: `@property`, `@classmethod`, or one
        read from its module, such as `@functools.cached_property`."""
        return any(self._names(decorator, name) for decorator in self._node.decorator_list)

    def _names(self, decorator: ast.expr, name: str) -> bool:
        if isinstance(decorator, ast.Attribute):
            return isinstance(decorator.value, ast.Name) and decorator.attr == name
        return isinstance(decorator, ast.Name) and decorator.id == name

    def parameters(self) -> list[str]:
        """Each parameter as `name: type`, without the receiver Python hands a method first: `self`, or the class as
        `cls` in a classmethod, `__new__`, `__init_subclass__`, or a metaclass's operations. A static method and a
        module function have none."""
        arguments = [*self._node.args.posonlyargs, *self._node.args.args]
        if self._receives_itself() and arguments:
            arguments = arguments[1:]
        return [
            f"{arg.arg}: {ast.unparse(arg.annotation)}" if arg.annotation is not None else arg.arg
            for arg in [*arguments, *self._node.args.kwonlyargs]
            if arg.arg != "self"
        ]

    def _receives_itself(self) -> bool:
        """True for a method Python calls with its object or its class as the first argument."""
        return self._owner is not None and not self.decorated("staticmethod")

    def callees(self) -> list[str]:
        """The name of each function or member the function calls, in the order the tree holds them; a member called
        on a class it names is written with that class, `Book.is_in_stock`, as a brace language's is."""
        called = [child.func for child in ast.walk(self._node) if isinstance(child, ast.Call)]
        return [self._callee_name(func) for func in called if isinstance(func, (ast.Name, ast.Attribute))]

    def _callee_name(self, func: ast.Name | ast.Attribute) -> str:
        if isinstance(func, ast.Name):
            return func.id
        receiver = func.value
        on_class = isinstance(receiver, ast.Name) and receiver.id[:1].isupper()
        return f"{receiver.id}.{func.attr}" if on_class else func.attr

    def body_text(self, source: str) -> str:
        """The statements as written in source, with the comments above them; the docstring stays the description."""
        node = self._node
        statements = node.body[1:] if ast.get_docstring(node) is not None else node.body
        if not statements:
            return ""
        if statements[0].lineno == node.lineno:
            return "\n".join(ast.get_source_segment(source, stmt) or "" for stmt in statements)
        lines = source.split("\n")
        boundary = node.body[0].end_lineno if statements is not node.body else node.lineno
        start = statements[0].lineno
        while start - 1 > boundary and lines[start - 2].strip().startswith("#"):
            start -= 1
        return "\n".join(lines[start - 1 : node.end_lineno])

    def catches_everything(self) -> bool:
        """True when any ``except`` clause of the function catches everything."""
        return any(clause.catches_everything() for clause in self._catch_clauses())

    def swallows(self) -> bool:
        """True when any ``except`` clause of the function drops the failure it caught."""
        return any(clause.swallows() for clause in self._catch_clauses())

    def unreadable_read_as_empty(self) -> str:
        """The failure to parse or decode that an ``except`` clause of the function answers with an empty value."""
        tries = [child for child in ast.walk(self._node) if isinstance(child, ast.Try)]
        found = (CatchClause(handler).unreadable_read_as_empty(tried) for tried in tries for handler in tried.handlers)
        return next((caught for caught in found if caught), "")

    def _catch_clauses(self) -> list["CatchClause"]:
        return [CatchClause(child) for child in ast.walk(self._node) if isinstance(child, ast.ExceptHandler)]

    def unnamed_numbers(self) -> list[str]:
        return [
            str(child.value)
            for child in ast.walk(self._node)
            if isinstance(child, ast.Constant)
            and isinstance(child.value, (int, float))
            and not isinstance(child.value, bool)
            and float(child.value) not in SAFE_NUMBERS
        ]

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


class FunctionCollaborators:
    """The objects a Python function builds and reads, read from its syntax tree: the collaborators its constructor
    builds that a caller cannot hand it, and whether it reads another object's private state. It holds the objects of
    its own class the function reads, since privacy in Python is per class."""

    def __init__(self, node: ast.FunctionDef | ast.AsyncFunctionDef, owner: ast.ClassDef | None) -> None:
        self._node = node
        self._own = OwnObjects(node, owner)

    def reaches_peer_private(self) -> bool:
        """True when the function reads a ``_`` member of another object, as ``SpanCollaborators.reaches_peer_private``
        reads a brace-language body: not of itself (``self``, or its class in a classmethod), not of another object of its own
        class (privacy in Python is per class), not a member its own class declares, not a dunder, not the repository a
        peer is wired to, and not a field it copies into the same field of this object."""
        own = OWN_RECEIVERS | OWN_CLASS_RECEIVERS | self._own.names()
        members = self._own.members()
        modules = self._standard_modules()
        for child in ast.walk(self._node):
            if not (isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name)):
                continue
            if child.value.id in own | modules or not child.attr.startswith("_") or is_dunder(child.attr) or child.attr in members:
                continue
            if child.attr.lstrip("_") in WIRED_PEER_FIELDS or self._copies_same_field(child.value.id, child.attr):
                continue
            return True
        return False

    def _standard_modules(self) -> frozenset[str]:
        """The standard library modules the function reads by name, such as `os` in `os._exit(0)`: an underscore
        function a standard module documents is a function of that module, not state another object keeps. A parameter
        or a local of the same name is an object, not the module."""
        bound = {arg.arg for arg in ast.walk(self._node.args) if isinstance(arg, ast.arg)}
        bound |= {child.id for child in ast.walk(self._node) if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)}
        return frozenset(_STANDARD_MODULES - bound)

    def built(self) -> list[tuple[str, int]]:
        """The classes this constructor builds that a caller cannot hand it, each with its line."""
        return Constructions(self._node).collaborators()

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

# The failures that say by their name that stored data could not be read: JSON that does not parse, and text that
# does not decode. Source code that does not parse (SyntaxError) is not stored data: a code reader skips it, and
# source-parses reports the file.
_UNREADABLE_FAILURES = frozenset({"JSONDecodeError", "UnicodeDecodeError", "UnicodeError"})
# The failures that catch a parse failure among much else.
_WIDE_FAILURES = frozenset({"ValueError", "Exception", "BaseException"})
# The calls that parse stored JSON, each as the module and the function it is called by.
_PARSERS = frozenset({("json", "load"), ("json", "loads")})
# The calls that build an empty value.
_EMPTY_BUILDERS = frozenset({"dict", "list", "tuple", "set", "frozenset", "str"})


class CatchClause:
    """One ``except`` clause of a Python function: what it catches, and whether it hands the failure on, by raising it
    again or by keeping it on its own object for a later call or another thread to raise or report, or drops it."""

    def __init__(self, handler: ast.ExceptHandler) -> None:
        self._handler = handler

    def catches_everything(self) -> bool:
        """A bare ``except`` catches everything. So does ``except Exception`` that never hands the failure on: it
        returns or substitutes a fallback for every failure, the broken invariant included."""
        caught = self._handler.type
        return caught is None or (self._catches_every_exception(caught) and not self._hands_on())

    def swallows(self) -> bool:
        """An empty handler, or one that catches everything and hands nothing on."""
        return self._ignores() or (self.catches_everything() and not self._hands_on())

    def unreadable_read_as_empty(self, tried: ast.Try) -> str:
        """The failure to parse or decode this clause catches and answers with an empty value, by name; empty when it
        catches none, raises, or answers something else. A failure that says so by its name (``JSONDecodeError``) is
        one wherever it is caught; ``ValueError`` and the catch-all types are one only when the ``try`` they guard
        parses stored text (``json.loads``), since they also catch a number that does not parse, which reads nothing. A
        clause that keeps the failure on its own object, for a later call to report or raise, hands it on as a raise does."""
        if self._hands_on() or not self._answers_empty():
            return ""
        caught = self._caught_names()
        named = next((name for name in caught if name in _UNREADABLE_FAILURES), "")
        if named:
            return named
        wide = next((name for name in caught if name in _WIDE_FAILURES), "")
        return wide if wide and self._parses(tried) else ""

    def _caught_names(self) -> list[str]:
        """Each failure type the clause names, by the last part of its name; ``BaseException`` for a bare ``except``."""
        caught = self._handler.type
        if caught is None:
            return ["BaseException"]
        named = caught.elts if isinstance(caught, ast.Tuple) else [caught]
        return [part.attr if isinstance(part, ast.Attribute) else part.id for part in named if isinstance(part, (ast.Attribute, ast.Name))]

    def _answers_empty(self) -> bool:
        """True when the clause returns an empty value, or sets a name to one for the code after it to carry on with."""
        for inner in ast.walk(self._handler):
            if isinstance(inner, ast.Return) and (inner.value is None or self._is_empty(inner.value)):
                return True
            if isinstance(inner, (ast.Assign, ast.AnnAssign)) and inner.value is not None and self._is_empty(inner.value):
                return True
        return False

    def _is_empty(self, value: ast.expr) -> bool:
        if isinstance(value, ast.Constant):
            return value.value is None or value.value == "" or value.value == b""
        if isinstance(value, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            return not (value.keys if isinstance(value, ast.Dict) else value.elts)
        return isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in _EMPTY_BUILDERS and not value.args and not value.keywords

    def _parses(self, tried: ast.Try) -> bool:
        """True when the guarded block calls a parser of stored text: ``json.loads``, ``yaml.safe_load``, ``ast.parse``."""
        calls = (inner.func for block in tried.body for inner in ast.walk(block) if isinstance(inner, ast.Call))
        return any(isinstance(called, ast.Attribute) and isinstance(called.value, ast.Name) and (called.value.id, called.attr) in _PARSERS for called in calls)

    def _hands_on(self) -> bool:
        return any(isinstance(inner, ast.Raise) for inner in ast.walk(self._handler)) or self._keeps_on_object()

    def _keeps_on_object(self) -> bool:
        """True when the handler keeps the failure it caught on its own object: ``self._error = error``,
        ``self.thread_errors.append(f"stdout: {error}")``."""
        caught = self._handler.name
        return bool(caught) and any(
            isinstance(name, ast.Name) and name.id == caught for kept in self._kept_on_self() for name in ast.walk(kept)
        )

    def _kept_on_self(self) -> list[ast.AST]:
        """What the handler stores on its own object: the value it sets on ``self``, and each call it makes on a member
        of ``self``."""
        kept: list[ast.AST] = []
        for inner in ast.walk(self._handler):
            if isinstance(inner, ast.Assign) and any(self._on_self(target) for target in inner.targets):
                kept.append(inner.value)
            elif isinstance(inner, ast.Call) and self._on_self(inner.func):
                kept.append(inner)
        return kept

    def _on_self(self, expression: ast.expr) -> bool:
        """True for a member reached from ``self``: ``self._error``, ``self.thread_errors.append``, ``self._unreadable[file]``."""
        reached = expression
        while isinstance(reached, (ast.Attribute, ast.Subscript)):
            reached = reached.value
        return reached is not expression and isinstance(reached, ast.Name) and reached.id == "self"

    def _catches_every_exception(self, caught: ast.expr) -> bool:
        if isinstance(caught, ast.Tuple):
            return any(self._catches_every_exception(element) for element in caught.elts)
        return isinstance(caught, ast.Name) and caught.id in _CATCH_ALL_TYPES

    def _ignores(self) -> bool:
        """An empty handler, or one that only says ``pass`` or ``...``."""
        return all(
            isinstance(stmt, ast.Pass) or (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
            for stmt in self._handler.body
        )


class Constructions:
    """The objects a Python constructor builds, and which of them its caller cannot hand it.

    A class it raises is a failure, not a collaborator. One it builds as the default of a parameter a caller may pass
    (``repo if repo is not None else Repo()``, ``repo or Repo()``, a default in the signature) can be swapped. One it
    builds from its own state, that is from itself, its parameters, values it computes from them, or constants, is a
    part it owns. What is left is built from nothing, or from something outside the object, such as a global or a call
    that reaches the environment, and the caller can never replace it."""

    def __init__(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._node = node
        arguments = node.args
        named = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
        extra = [item for item in (arguments.vararg, arguments.kwarg) if item is not None]
        self._parameters = {item.arg for item in named + extra}
        # The parameters a caller may pass, whose defaults it can replace.
        self._given = self._parameters - {"self"}

    def collaborators(self) -> list[tuple[str, int]]:
        """The classes it builds that a caller cannot hand it, each with its line."""
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
            and not self._built_from(child, owned)
        ]

    def _owned_names(self) -> set[str]:
        """Itself, its parameters, and every name its body assigns: what the constructor holds or computes."""
        stored = {
            child.id
            for stmt in self._node.body
            for child in ast.walk(stmt)
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
        }
        return self._parameters | stored

    def _raised_or_defaulted(self) -> set[int]:
        """The constructions a caller can replace, and the failures it raises, by node identity."""
        return {
            id(built)
            for stmt in self._node.body
            for child in ast.walk(stmt)
            for built in self._replaceable_in(child)
            if isinstance(built, ast.Call)
        }

    def _replaceable_in(self, child: ast.AST) -> list:
        """What a node builds that its caller can replace: the failure a raise builds, or the default built in place of
        a parameter the caller may pass."""
        if isinstance(child, ast.Raise):
            return [child.exc]
        if isinstance(child, ast.IfExp):
            return self._defaulted_branches(child)
        if isinstance(child, ast.BoolOp):
            return self._defaulted_alternatives(child)
        if isinstance(child, ast.If):
            return self._defaults_assigned(child)
        return []

    def _defaulted_branches(self, choice: ast.IfExp) -> list:
        """`repo if repo is not None else Repo()`: the parameter, or the default built in its place."""
        return [choice.body, choice.orelse] if {_name_of(choice.body), _name_of(choice.orelse)} & self._given else []

    def _defaulted_alternatives(self, either: ast.BoolOp) -> list:
        """`repo or Repo()`: the defaults after a parameter."""
        return either.values[1:] if isinstance(either.op, ast.Or) and _name_of(either.values[0]) in self._given else []

    def _defaults_assigned(self, test: ast.If) -> list:
        """`if repo is None: repo = Repo()`: the values a missing parameter's branch assigns."""
        if self._absent_parameter(test.test) not in self._given:
            return []
        return [inner.value for inner in test.body if isinstance(inner, ast.Assign)]

    def _built_from(self, construction: ast.Call, owned: set[str]) -> bool:
        """A construction given only what the constructor owns: every name its arguments read is one the constructor
        holds or computes, a constant or a class named with a capital that it does not call (the failure a file reports,
        ``JsonFile(self.path, HooksFileUnreadable)``), or a builtin; a function or class it calls is judged on its own,
        and a class whose operation it calls (``Path.cwd()``) reaches outside the object. A construction given nothing
        has no tie to its owner."""
        arguments = [*construction.args, *(keyword.value for keyword in construction.keywords)]
        nodes = [child for argument in arguments for child in ast.walk(argument)]
        calls = [child.func for child in nodes if isinstance(child, ast.Call)]
        called = {id(func) for func in calls}
        # A class whose operation the argument calls, such as `Path` in `Path.cwd()`, is no constant.
        receivers = {id(func.value) for func in calls if isinstance(func, ast.Attribute)}
        known = owned | self._bound_in(nodes)
        read = [child for child in nodes if isinstance(child, ast.Name) and id(child) not in called]
        return bool(arguments) and all(self._names_owned_value(name, known, id(name) in receivers) for name in read)

    def _names_owned_value(self, name: ast.Name, known: set[str], called_on: bool) -> bool:
        """True for a name the constructor holds, a builtin, or a constant or class it names without calling."""
        return name.id in known or hasattr(builtins, name.id) or (name.id[:1].isupper() and not called_on)

    def _bound_in(self, nodes: list[ast.AST]) -> set[str]:
        """The names a comprehension or a lambda inside the arguments binds itself."""
        bound = {child.id for child in nodes if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)}
        return bound | {child.arg for child in nodes if isinstance(child, ast.arg)}

    def _absent_parameter(self, test: ast.expr) -> str:
        """The name a test asks is missing, `x is None` or `not x`; empty for any other test."""
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return _name_of(test.operand)
        if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Is):
            compared = test.comparators[0]
            if isinstance(compared, ast.Constant) and compared.value is None:
                return _name_of(test.left)
        return ""


def _name_of(expression: ast.expr) -> str:
    """The name an expression is, when it is a bare name; empty otherwise."""
    return expression.id if isinstance(expression, ast.Name) else ""


class OwnObjects:
    """The objects of its own class a Python function reads. Privacy in Python is per class, so reading a ``_`` member of
    any of them is reading the class's own state.

    It holds them by name: a classmethod's first parameter, the class's own name, a parameter typed as the class, the
    other operand of a comparison or arithmetic dunder such as ``__eq__``, a local it builds from the class (``cls()``,
    ``Plan()``, ``cls.read(...)``, ``type(self)()``), and the loop name over a field the class declares as holding
    objects of the class (``epics: list['Epic']``). And it knows the private members the class declares, so a read of
    one of them off a local, a loop name, or a copy of itself (``node = self``, ``moved = copy.copy(self)``) is a read
    of another object of the class. A module function has no class, so none."""

    def __init__(self, node: ast.FunctionDef | ast.AsyncFunctionDef, owner: ast.ClassDef | None) -> None:
        self._node = node
        self._owner = owner

    def names(self) -> frozenset[str]:
        if self._owner is None:
            return frozenset()
        names = self._parameters() | self._bound_in_body()
        names.add(self._owner.name)
        names.discard("")
        return frozenset(names)

    def members(self) -> frozenset[str]:
        """The ``_`` members the class declares: its operations, its class fields, and the fields its operations set
        on ``self``."""
        if self._owner is None:
            return frozenset()
        declared = {item.name for item in self._owner.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
        declared |= {_name_of(target) for item in self._owner.body for target in self._targets(item)}
        declared |= {self._self_field(target) for child in ast.walk(self._owner) for target in self._targets(child)}
        return frozenset(name for name in declared if name.startswith("_"))

    def _parameters(self) -> set[str]:
        arguments = self._node.args.posonlyargs + self._node.args.args + self._node.args.kwonlyargs
        if self._node.name in _PEER_OPERAND_DUNDERS:
            return {argument.arg for argument in arguments}
        typed = {argument.arg for argument in arguments if self._names_class(argument.annotation)}
        decorators = {decorator.id for decorator in self._node.decorator_list if isinstance(decorator, ast.Name)}
        if "classmethod" in decorators and self._node.args.args:
            typed.add(self._node.args.args[0].arg)
        return typed

    def _bound_in_body(self) -> set[str]:
        own_fields = self._fields_holding_class()
        names: set[str] = set()
        for child in ast.walk(self._node):
            if isinstance(child, ast.Assign) and self._builds_class(child.value):
                names.update(target.id for target in child.targets if isinstance(target, ast.Name))
            elif isinstance(child, (ast.For, ast.comprehension)) and self._self_field(child.iter) in own_fields:
                names.add(_name_of(child.target))
        return names

    def _names_class(self, annotation: ast.expr | None) -> bool:
        """True when a type annotation names the class: ``Plan``, ``'Plan'``, ``Plan | None``, ``list['Plan']``."""
        named = rf"\b{re.escape(self._owner.name)}\b"
        return annotation is not None and re.search(named, ast.unparse(annotation)) is not None

    def _builds_class(self, assigned: ast.expr) -> bool:
        """True when an assigned value is an object the class makes: a call of the class, of ``cls``, of
        ``type(self)``, or of a factory on the class (``Plan.read(...)``, ``cls.read(...)``)."""
        if not isinstance(assigned, ast.Call):
            return False
        called = assigned.func
        if isinstance(called, ast.Attribute):
            called = called.value
        if isinstance(called, ast.Call):
            return _name_of(called.func) == "type"
        return _name_of(called) in {self._owner.name, "cls"}

    def _fields_holding_class(self) -> set[str]:
        """The fields the class declares as holding objects of the class itself, at class level or as ``self.x: T``."""
        fields = {
            _name_of(child.target) or self._self_field(child.target)
            for child in ast.walk(self._owner)
            if isinstance(child, ast.AnnAssign) and self._names_class(child.annotation)
        }
        fields.discard("")
        return fields

    def _self_field(self, expression: ast.expr) -> str:
        """The field an expression reads off ``self`` (``self.epics``); empty for anything else."""
        if isinstance(expression, ast.Attribute) and _name_of(expression.value) == "self":
            return expression.attr
        return ""

    def _targets(self, statement: ast.AST) -> list[ast.expr]:
        """What an assignment statement assigns to; none for any other node."""
        if isinstance(statement, ast.Assign):
            return statement.targets
        return [statement.target] if isinstance(statement, (ast.AnnAssign, ast.AugAssign)) else []


