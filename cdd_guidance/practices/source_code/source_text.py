"""A span of source in any language, read for what the rules of several practices measure in it: *SourceText* and the
parts it holds, *SpanFailures* (what the span raises) and *SpanCollaborators* (the objects it reaches)."""

from __future__ import annotations

import builtins
import re
from typing import Protocol

from cdd_guidance.practices.source_code.bracket_structure import BracketStructure

_CATCH = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{")
_PY_EXCEPT = re.compile(r"\bexcept\s*(?::|\([^)]*\)\s*:)")
STRING_LITERAL = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
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
# A `_` member read off a name: `order._lines`, `self.repo._cache` (receiver `repo`).
_PEER_PRIVATE_FIELD = re.compile(r"(\w+)\.(_\w+)")
SAFE_NUMBERS = {
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
OWN_RECEIVERS = frozenset({"this", "self", "super"})
# The names an operation reads its own class by: `cls` in a Python classmethod.
OWN_CLASS_RECEIVERS = frozenset({"cls"})
# `new Repo(` in a brace-language body, and what makes the construction a failure thrown or a parameter's default:
# `throw new`, `?? new`, `|| new`, right before it.
_NEW_CLASS = re.compile(r"\bnew\s+([A-Z][\w$]*)\s*\(")
_THROWN_OR_DEFAULTED = re.compile(r"(?:\bthrow|\?\?|\|\|)\s*$")
# A name a construction's arguments read: not a member after a dot, and not a function or class it calls.
_ARGUMENT_NAME = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)\b(?!\s*\()")
# A name a brace-language body declares, which it then holds: `const x =`, `let x`, `var x`.
_DECLARED_LOCAL = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)")
# An arrow function's parameters: `(scenario, index) =>` or `selected =>`.
_ARROW_FUNCTION = re.compile(r"(?:\(([^()]*)\)|([A-Za-z_$][\w$]*))\s*=>")
_SCRIPT_VALUES = frozenset({"true", "false", "null", "undefined", "typeof", "instanceof", "as", "void", "await", "new"})
WIRED_PEER_FIELDS = frozenset({"repository", "repo"})
# A call that reaches outside the program: a file, the network, another process, or standard output. Reading text the
# program already holds, such as `parse(text)`, `text.splitlines()`, or a reader's `read(lines)`, is calculation.
_IO_CALL = re.compile(
    r"(?<![\w$])(?:open|read_text|read_bytes|write_text|write_bytes|readlines|writelines|readFile\w*|writeFile\w*"
    r"|appendFile\w*|fetch|urlopen|urlretrieve|print|Popen|check_output|check_call|sendall|recv|upload\w*|download\w*)"
    r"\s*\("
    r"|\b(?:subprocess|requests|httpx|socket|shutil)\.\w+\s*\(|\bsys\.std(?:out|err)\.write\s*\(|\bos\.(?:remove|unlink"
    r"|rename|replace|makedirs|mkdir|rmdir|listdir|scandir|walk|system)\s*\(",
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
_RAISED_CLASS = re.compile(r"^\s*(?:new\s+)?([A-Z]\w*)\b")
# The failures a language gives every program for an ordinary bad value; raising one on an empty value says nothing
# about the domain. A failure of the world outside the program, such as a connection closing (`OSError`, `EOFError`),
# is no empty case the program could define away, so it is not one of them.
_BUILTIN_FAILURES = frozenset(
    {
        name
        for name in dir(builtins)
        if isinstance(getattr(builtins, name), type)
        and issubclass(getattr(builtins, name), BaseException)
        and not issubclass(getattr(builtins, name), (OSError, EOFError))
    }
    | {"Error", "RangeError", "ReferenceError", "IllegalArgumentException", "IllegalStateException", "RuntimeException"}
)
# A docstring or a comment: text about the code, which the raise measures leave out.
_DOC_OR_COMMENT = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|^\s*(?:#|//).*$', re.M)
_EDGE_RAISE_MESSAGE = re.compile(r"raise\s+(\w*(?:Error|Exception))\([^)]*(?:empty|not found|missing|none)", re.I)
_EDGE_GUARD = re.compile(r"if\s+(?:not\s+|len\s*\([^)]*\)\s*==\s*0)")
_EMPTY_EXCEPTION = re.compile(r"raise\s+(\w+(?:Error|Exception))\s*\(\s*([\"']?)\s*\2\s*\)")
_GENERIC_EXCEPTION = re.compile(r"raise\s+\w+(?:Error|Exception)\s*\(\s*f?[\"'](?:error|failed|invalid)[\"']\s*\)", re.I)
# Nested property writes (this.token, this.validation.verified) — not helper-local state.
_COORDINATED_MUTATION = re.compile(r"\b(?:self|this)(?:\.\w+)+\s*=")
# A generator, a `@contextmanager` among them, hands its caller what it yields, and the state it changes for the
# caller's block is put back when the block ends, so `yield` gives the outcome as `return` does.
_RETURN = re.compile(r"\b(?:return|yield)\b")
_VOID_RETURN = re.compile(r"->\s*None\b|: void\b")
_THROWS = re.compile(r"\b(?:throw|raise)\b")
_PROTOTYPE_SWAP = re.compile(r"\bObject\.setPrototypeOf\s*\(|\.__proto__\s*=(?!=)|\.__class__\s*=(?!=)")
# Below these sizes a body is too small for the mixed-concerns and unrecorded-mutation measures to mean anything.
MIN_SIGNAL_BODY = 40
MIN_MUTATION_BODY = 30


class MeasuredBody(Protocol):
    """An operation's body as the rules measure it, whichever way its parser reads it: as a span of text in any
    language (*SourceText*), or as a Python function's syntax tree (Clean Engineering's *PythonFunctionBody*). An
    operation keeps the same measures from either, so a rule never asks which language it was read from."""

    def control_flow_depth(self) -> int:
        """The deepest nesting of if, for, and while blocks."""
        ...

    def unnamed_numbers(self) -> list[str]:
        """Each number literal no name explains."""
        ...

    def catches_everything(self) -> bool:
        """True when a catch names no failure, so it catches every one, the broken invariant included."""
        ...

    def swallows(self) -> bool:
        """True when a catch drops what it caught: an empty one, or one that hands back a fallback value instead."""
        ...


class SourceText(MeasuredBody):
    """A span of source in any language, an operation body or a class, and what the rules measure in its code.
    Brace-language measures count `{` blocks; Python measures count indentation."""

    def __init__(self, text: str) -> None:
        self._text = text
        # Which bracket closes which in the text, for the measures that read its blocks.
        self._brackets = BracketStructure(text)
        # What it raises, and the objects it builds and reads: each a part the span makes once.
        self.failures = SpanFailures(self)
        self.collaborators = SpanCollaborators(self)

    @property
    def text(self) -> str:
        return self._text

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

    def unnamed_numbers(self) -> list[str]:
        """Each number literal outside strings and regular expressions that no name explains."""
        code = _REGEXP_LITERAL.sub('""', STRING_LITERAL.sub('""', self._text))
        return [raw for raw in _NUMBER.findall(code) if float(raw) not in SAFE_NUMBERS]

    def catches_everything(self) -> bool:
        """A catch with no failure named, `catch ()` or Python's bare `except:`. TypeScript's optional catch binding,
        `catch {`, is written on purpose and is not one."""
        if _OPTIONAL_CATCH_BINDING.search(self._text):
            return False
        return bool(_EMPTY_CATCH_BINDING.search(self._text) or _BARE_EXCEPT.search(self._text))

    def swallows(self) -> bool:
        """An empty catch, or one that hands back a fallback value without throwing again."""
        for match in _CATCH.finditer(self._text):
            catch_body = self._brackets.braced(match.end() - 1)
            if catch_body is None:
                continue
            stripped = catch_body.strip()
            if not stripped or stripped in _IGNORED_CATCH_BODIES or self._returns_fallback(stripped):
                return True
        return any(_PASS_LINE.match(self._text[match.end() :]) for match in _PY_EXCEPT.finditer(self._text))

    def _returns_fallback(self, catch_body: str) -> bool:
        return _THROW.search(catch_body) is None and _FALLBACK_RETURN.search(catch_body) is not None

    def mixes_io_and_domain(self) -> bool:
        """A body long enough to mean something that calls both I/O and a domain calculation."""
        return len(self._text.strip()) >= MIN_SIGNAL_BODY and self.calls_io_and_domain()

    def calls_io_and_domain(self) -> bool:
        return bool(_IO_CALL.search(self._text) and _DOMAIN_CALL.search(self._text))

    def mutates_without_record(self) -> bool:
        text = self._text
        if len(text.strip()) < MIN_MUTATION_BODY or len(_COORDINATED_MUTATION.findall(text)) <= 1:
            return False
        return not (_RETURN.search(text) or _VOID_RETURN.search(text) or _THROWS.search(text))

    def has_prose_comment(self, hash_only: bool = False) -> bool:
        for line in self._text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") and _NARRATIVE_COMMENT.search(stripped):
                return True
            if not hash_only and _NARRATIVE_COMMENT.search(self._slash_comment(stripped)):
                return True
        return False

    def _slash_comment(self, line: str) -> str:
        """The `//` comment that ends a line; none when the line's only `//` sits inside a string, such as a line of
        generated code a Python string holds."""
        code = STRING_LITERAL.sub(lambda found: " " * len(found.group(0)), line)
        start = code.find("//")
        return line[start:] if start >= 0 else ""

    def prototype_swap(self, start_line: int) -> dict[str, str | int]:
        """The code that swaps an object's class and the line it is on, when the text does; empty when it does not."""
        found = _PROTOTYPE_SWAP.search(self._text)
        if found is None:
            return {}
        return {"code": found.group(0).strip(), "line": start_line + self._text.count("\n", 0, found.start())}

    def line_of(self, index: int) -> int:
        """The line, counted from 1, holding the character at index. Rules report a finding by its line, so a fact
        records the line its match starts on."""
        return self._text.count("\n", 0, index) + 1

    def hits(self, pattern: re.Pattern[str]) -> list[list]:
        """[line, matched code] for each match of pattern."""
        return [[self.line_of(match.start()), match.group(0).strip()] for match in pattern.finditer(self._text)]

    def _brace_depth(self) -> int:
        """Count only the blocks control flow opens: JSX containers, object literals and arrow bodies nest no logic."""
        code = STRING_LITERAL.sub('""', self._text)
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
        opening = BracketStructure(head).opening_bracket(len(head) - 1)
        return opening >= 0 and _CONTROL_CONDITION.search(head[:opening]) is not None
class SpanFailures:
    """The failures a span of source raises: a builtin failure raised on an empty value, and a raise with no message or
    a generic one. What it catches the span answers itself, as every measured body does (``catches_everything``,
    ``swallows``)."""

    def __init__(self, span: SourceText) -> None:
        self._span = span

    def raises_on_empty(self) -> bool:
        """True when the body raises a builtin failure on an empty or missing value. A raise of a failure the program
        declares, such as ``raise UnknownPractice(key, known)`` when no practice has the key or
        ``raise CommitPathsRequiredError()`` when a required argument is missing, is a named refusal of a broken call
        rather than an ordinary empty case, so it is left out; whether it carries enough context is
        ``domain-exception-carries-context``'s question."""
        code = self._code()
        for pattern in (_EDGE_RAISE, _EDGE_RAISE_BRACE):
            if any(not self._names_declared_failure(match.group(1)) for match in pattern.finditer(code)):
                return True
        return self._raises_builtin_with_message()

    def exception_without_message(self) -> str:
        found = _EMPTY_EXCEPTION.search(self._code())
        return found.group(1) if found else ""

    def generic_exception_message(self) -> bool:
        return bool(_GENERIC_EXCEPTION.search(self._code()))

    def _code(self) -> str:
        """The text without its docstrings and comments, so a raise a docstring shows as an example raises nothing."""
        return _DOC_OR_COMMENT.sub("", self._span.text)

    def _raises_builtin_with_message(self) -> bool:
        """A builtin failure raised under an empty-value guard whose message says what is empty or missing."""
        code = self._code()
        message = _EDGE_RAISE_MESSAGE.search(code)
        return bool(message and not self._names_declared_failure(message.group(1)) and _EDGE_GUARD.search(code))

    def _names_declared_failure(self, raised: str) -> bool:
        """A raise of a failure the program declares rather than one its language gives every program:
        `UnknownPractice(key, known)`, `CommitPathsRequiredError()`; not `ValueError("missing")`."""
        named = _RAISED_CLASS.match(raised)
        return named is not None and named.group(1) not in _BUILTIN_FAILURES
class SpanCollaborators:
    """The objects a brace-language span builds and reads: the collaborators its constructor builds that a caller cannot
    hand it, the locals it builds of a class, and whether it reads another object's private state."""

    def __init__(self, span: SourceText) -> None:
        self._span = span

    def reaches_peer_private(self, own_objects: frozenset[str] = frozenset(), own_members: frozenset[str] = frozenset()) -> bool:
        """True when the body reads a ``_`` member of another object: ``order._lines``, not ``this._lines``,
        ``cls._registry``, or a dunder such as ``other.__dict__``. Copying a field from a peer into the same field of
        this object, and the repository a peer is wired to, are not reaches. Neither is a member of another object of
        the class the body belongs to, since privacy is per class: own_objects names the objects of that class the body
        holds, and own_members the members that class declares."""
        code = STRING_LITERAL.sub('""', self._span.text)
        own = OWN_RECEIVERS | OWN_CLASS_RECEIVERS | own_objects
        for match in _PEER_PRIVATE_FIELD.finditer(code):
            receiver, member = match.group(1), match.group(2)
            if receiver in own or member in own_members or is_dunder(member) or member.lstrip("_") in WIRED_PEER_FIELDS:
                continue
            if self._copies_same_field(receiver, member.lstrip("_")):
                continue
            return True
        return False

    def built(self, parameter_names: frozenset[str], start_line: int) -> list[tuple[str, int]]:
        """The classes this brace-language constructor body builds with `new` that a caller cannot hand it, each with
        its line, read as ``FunctionCollaborators.built`` reads Python: a class it throws, the default it
        builds for a parameter (``repo ?? new Repo()``, ``repo || new Repo()``), and a part it builds from its own state
        (``this``, its parameters, its locals, constants, or classes it names) are left out."""
        code = STRING_LITERAL.sub('""', self._span.text)
        unquoted = BracketStructure(code)
        owned = parameter_names | OWN_RECEIVERS | set(_DECLARED_LOCAL.findall(code)) | _SCRIPT_VALUES | self._arrow_parameters(code)
        found: list[tuple[str, int]] = []
        for match in _NEW_CLASS.finditer(code):
            if _THROWN_OR_DEFAULTED.search(code[: match.start()]):
                continue
            close = unquoted.closing_bracket(match.end() - 1, "(", ")")
            arguments = code[match.end() : close if close is not None else len(code)]
            if arguments.strip() and all(name in owned or name[:1].isupper() for name in _ARGUMENT_NAME.findall(arguments)):
                continue
            found.append((match.group(1), start_line + code.count("\n", 0, match.start())))
        return found

    def _arrow_parameters(self, code: str) -> set[str]:
        """The names the arrow functions in a brace-language body bind: `scenario` and `index` in
        `(scenario, index) => new ScenarioViewModel(scenario, index)`. A part built from them is built from what the
        body itself holds."""
        bound: set[str] = set()
        for match in _ARROW_FUNCTION.finditer(code):
            bound.update(_ARGUMENT_NAME.findall(match.group(1) or match.group(2) or ""))
        return bound

    def locals_built_of(self, class_name: str) -> frozenset[str]:
        """Each local a brace-language body declares as a new object of the class: ``const copy = new Money()``."""
        built = rf"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*new\s+{re.escape(class_name)}\b"
        return frozenset(re.findall(built, self._span.text))

    def _copies_same_field(self, receiver: str, field: str) -> bool:
        """``this._field = receiver._field`` (or public ``field``) — an aggregate copying from a peer instance."""
        copy = rf"(?:this|self)\._?{re.escape(field)}\s*=\s*{re.escape(receiver)}\._?{re.escape(field)}\b"
        return bool(re.search(copy, self._span.text))
def is_dunder(member: str) -> bool:
    """A Python special member such as ``__dict__``, which every object answers and none hides."""
    return member.startswith("__") and member.endswith("__")
