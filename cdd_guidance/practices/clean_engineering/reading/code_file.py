"""One file of the code read, as the code written in it names things, and the members a span of that code calls.

*CodeIndex.file* answers a *CodeFile*, the one seam every practice asks to resolve a name its code writes: the class or
module function the file declares, imports, or finds beside itself in its own folder and language, and each member a
span of its code calls and reads (*CodeSpan*: the code, the class it is written in, and the type of each local it knows).
Clean Engineering asks it for each operation's and property's own body, and BDD for each observation and the setups
around it, so an `invokes` edge means the same member whichever practice draws it. A name is joined to the node the
file's own declarations and imports name, never to every node of that name: two classes may both have a `total`, and a
call on an order runs only the order's.

A receiver's class is what the code says it is: a parameter's or a member's type hint, the class a local is built from,
the class the operation that answered it returns, or, where the code writes no hint, what the operation's `return`
statements answer, what the constructor assigns to a field, and what a module assigns to a module variable
(*MemberAnswers*). A chain is followed through every call's answer and every item it takes, so
`self.board.column("Backlog").cards[0].title` reaches the card's title."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, NamedTuple

from cdd_guidance.practices.clean_engineering.model import CONSTRUCTOR_NAMES, MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.source_code import STAR, ClassReference

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import CodeIndex

# The marker the source view puts after a line for each call on it, `/* call:show */`, which is no code.
_CALL_MARKER = re.compile(r"\s*/\* call:[^*]*\*/")
# What is no code: a doc string, a block comment, and a line comment to the end of its line. A string on one line is
# matched too, and kept, so a `#` or `//` written inside it is no comment.
_NOT_CODE = re.compile(
    r'(?s)""".*?"""|\'\'\'.*?\'\'\'|/\*.*?\*/'
    r'|("(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\')'
    r"|(?:#|//)[^\n]*"
)
# Where an expression may start: a name that no dot, name, or closing bracket comes before.
_HEAD = re.compile(r"(?<![\w.$)\]])[A-Za-z_$][\w$]*")
_IDENTIFIER = re.compile(r"[A-Za-z_$][\w$]*")
# What may open an expression without being part of its value: `await order.paid()`, `new Order()`.
_PREFIX = re.compile(r"(?:await|new|yield)\s+")
# A function called by its name alone, and a brace language's call of its base constructor.
_BARE_CALL = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)\s*\(")
# A local the code assigns: `order = `, `const order = `, `order: Order = `, `root, board = `, `(root, board) = `.
_ASSIGNMENT = re.compile(
    r"(?:^|(?<=[;{]))[ \t]*(?:(?:const|let|var)\s+)?(\(?[A-Za-z_$][\w$]*(?:[ \t]*,[ \t]*[A-Za-z_$][\w$]*)*\)?)"
    r"[ \t]*(?::[ \t]*([^=\n]+?))?[ \t]*=(?![=>])[ \t]*",
    re.MULTILINE,
)
# The locals a script takes out of an object by its fields' names: `const { page, stop } = `.
_DESTRUCTURED = re.compile(r"\b(?:const|let|var)\s*\{([^{}]*)\}\s*(?::[^=\n]+)?=(?![=>])\s*")
# A local a script declares as one class without assigning it: `let order: Order`.
_DECLARED_LOCAL = re.compile(r"\b(?:let|const|var)\s+([A-Za-z_$][\w$]*)\s*:\s*([A-Z][\w$]*)")
# A loop's local and where the collection it walks starts: `for line in `, `for (const line of `.
_LOOP = re.compile(r"\bfor\s*\(?\s*(?:const\s+|let\s+|var\s+)?([A-Za-z_$][\w$]*)\s+(?:in|of)\s+")
# A Python block's object and its local: `with Order() as order`, and each further `, Cart() as cart` of one with.
_WITH = re.compile(r"(?<![\w$.])with\s+")
_AS_LOCAL = re.compile(r"\s+as\s+([A-Za-z_$][\w$]*)")
# A script's cast of an expression to one class: `foo() as Order`.
_CAST = re.compile(r"\s+as\s+([A-Z][\w$]*)\b")
# A `return` and what it answers.
_RETURN = re.compile(r"(?<![\w$.])return\s+")
# A module's own assignment of a module variable, at the start of a line.
_MODULE_ASSIGNMENT = r"(?m)^(?:export\s+)?(?:(?:const|let|var)\s+)?{name}[ \t]*(?::[ \t]*([^=\n]+?))?[ \t]*=(?![=>])[ \t]*"
# A script's module variable declared as one class and assigned later: `let board: BoardOnProject`.
_MODULE_DECLARATION = r"(?m)^(?:export\s+)?(?:let|var)\s+{name}\s*:\s*([^=\n;]+?)\s*;?\s*$"
# A field a class declares with the value it starts with: `readonly fileBar = new FileBar(this)`, `lines: list = []`.
_INITIALIZED = r"(?<![\w$.]){name}[ \t]*[?!]?[ \t]*(?::[ \t]*([^=\n]+?))?[ \t]*=(?![=>])[ \t]*"
# A function a file declares, the end of a Python signature with the return type it writes, and a script function.
_PYTHON_DEF = r"(?m)^([ \t]*)(?:async[ \t]+)?def[ \t]+{name}[ \t]*\("
_SCRIPT_FUNCTION = r"(?<![\w$.])(?:function\s*\*?\s*{name}\s*(?:<[^>()]*>)?\s*|(?:const|let|var)\s+{name}\s*=\s*(?:async\s*)?)\("
_SIGNATURE_END = re.compile(r"[ \t]*(?:->[ \t]*([^:\n]+?))?[ \t]*:")
_OPTIONAL = re.compile(r"^(?:Optional\[(.+)\]|(.+?)\s*\|\s*(?:None|null|undefined)|(?:None|null|undefined)\s*\|\s*(.+))$")
_GENERIC = re.compile(r"^([A-Za-z_][\w.]*)\s*[\[<](.*)[\]>]$")
_ARRAY = re.compile(r"^([A-Za-z_]\w*)\s*\[\]$")
_NAME = re.compile(r"^[A-Za-z_]\w*$")
_INTEGER = re.compile(r"^-?\d+$")
# The generic types that hold many of one kind, that one kind is the last they name, and those that hold one of it.
_SEQUENCES = frozenset({
    "list", "List", "Sequence", "MutableSequence", "Iterable", "Iterator", "Generator", "AsyncIterator", "AsyncIterable",
    "set", "Set", "frozenset", "FrozenSet", "Collection", "deque", "Array", "ReadonlyArray",
})
_MAPPINGS = frozenset({"dict", "Dict", "Mapping", "MutableMapping", "defaultdict", "OrderedDict", "Record", "Map", "ReadonlyMap"})
_WRAPPERS = frozenset({"Optional", "Promise", "Awaitable", "Final", "ClassVar", "Readonly", "type", "Type"})
_TUPLES = frozenset({"tuple", "Tuple"})
_SELF_TYPES = frozenset({"Self", "this"})
_OWN_OBJECT = frozenset({"self", "this", "cls"})
_BASE_OBJECT = frozenset({"super"})
_SCRIPT_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".jsx", ".mjs"})
# Where an expression a local is assigned, a loop walks, or a `return` answers, has ended: the end of its statement, of a
# tuple part, or of a loop's or block's header.
_ENDS = frozenset("\n;,:)]}")
# What may follow an expression and still leave it the value, when it holds: `opener = Chat.load(id) if id else None`,
# `chat = found or Chat()`, `const chat = found ?? fresh()`.
_ALTERNATIVE = re.compile(r"(?:if|or)\b|\?\?|\|\|")
# One field of a script's object literal, written alone or with its value after a colon.
_OBJECT_FIELD = re.compile(r"\s*([A-Za-z_$][\w$]*)\s*(:\s*)?")
# The comma before a tuple's next part, when a part follows it on its line.
_NEXT_PART = re.compile(r"[ \t]*,[ \t]*(?=[A-Za-z_$])")
_QUOTES = frozenset("'\"`")


class CodeSpan(NamedTuple):
    """A span of code to read for what it calls: its text, the class it is written in (none outside a class, such as
    a spec's block), the type hint of each parameter it takes, by the parameter's name, and the code that runs before
    it, such as a spec's setups, read only for the locals it makes. A parameter with no hint is a name whose class the
    code does not say."""

    text: str
    owner: "Node | None" = None
    typed: dict[str, str] = {}
    before: str = ""

    @staticmethod
    def code_of(text: str) -> str:
        """The code of text: without the calls the source view marks, doc strings, or comments."""
        return _NOT_CODE.sub(lambda found: found.group(1) or "", _CALL_MARKER.sub("", text))


class Typed(NamedTuple):
    """What a value of the code is, as far as the code says: one object of a class (``of``), a tuple of values by
    position (``items``), a collection whose every element is one value (``each``), a mapping whose every value is one
    (``by_key``), or a script's object of named fields, each with its value (``fields``)."""

    of: "Node | None" = None
    items: tuple = ()
    each: "Typed | None" = None
    by_key: "Typed | None" = None
    fields: tuple = ()


class CodeFile:
    """One file of the code read, as the code in it can name things: the classes and module functions it declares,
    then those its imports name, then, with no import, the one declared beside it in its own folder and language. A
    graph read over the whole working copy (whole) also lets a name its imports and folder declare once say which
    member a receiver of no known class reaches."""

    def __init__(self, index: "CodeIndex", relative: str, imports: list[ClassReference], whole: bool) -> None:
        self._index = index
        self.relative = relative
        self._imports = imports
        self._whole = whole

    def class_named(self, name: str) -> "Node | None":
        """The class this file means by name: the one it declares, else the one it imports; none when it names
        neither."""
        return self._in_reach(self._index.classes_named(name), name)

    def function_named(self, name: str) -> "Node | None":
        """The module function this file means by name: its own, else the one it imports."""
        functions = [member for member in self._index.members_named(name) if member.get_fact("owner") == MODULE_FUNCTION_HOLDER]
        return self._in_reach(functions, name)

    def constructors_of(self, class_name: str) -> "list[Node]":
        """The constructor the class this file names class_name writes; none when the class writes none."""
        found = self.class_named(class_name)
        return self._index.constructors_of(found) if found is not None else []

    @property
    def imported_classes(self) -> "list[Node]":
        """The classes this file's imports name, in the order it imports them."""
        found = (self.class_named(name) for reference in self._imports for name in reference.names())
        return list(dict.fromkeys(node for node in found if node is not None and node.source.file != self.relative))

    def members_called_in(self, span: CodeSpan) -> "list[Node]":
        """The members span calls and the properties it reads, in the order its code names them, each once."""
        return list(dict.fromkeys(_SpanCalls(self, self._index, span).called()))

    def module_value(self, name: str) -> "Typed | None":
        """What a module variable this file names is: the one this file assigns, else the one a file its imports name
        assigns, as that file's assignment types it (`PRACTICES = PracticeCatalogue()`); none when no such file assigns
        name at the start of a line."""
        for relative in [self.relative, *sorted(self._imported_files(name))]:
            found = self._index.answers.module_value(relative, name)
            if found is not None:
                return found
        return None

    def only_member_named(self, name: str, called: bool) -> "Node | None":
        """The member called name a receiver of no known class can be: an operation when it is called, else a property,
        or the getter that reads it. The one that exactly one class of this file declares; else the one that exactly
        one class of the files its imports name declares; else, in a graph that holds the whole working copy, the one
        that exactly one class of the files of its own folder in its own language declares. None when no class there
        declares it or more than one does, since the name alone does not say which is meant. A load of some files
        alone holds only some of the folder, so it looks no further than the file and its imports."""
        members = [
            member for member in self._index.members_named(name)
            if member.get_fact("owner") != MODULE_FUNCTION_HOLDER and (member.type == "Operation") == called
        ]
        if any(member.source.file == self.relative for member in members):
            return self._read_as(self._only([member for member in members if member.source.file == self.relative]))
        imported = self._imported_files()
        found = self._only([member for member in members if member.source.file in imported])
        if found is not None or not self._whole or any(member.source.file in imported for member in members):
            return self._read_as(found)
        return self._read_as(self._only([member for member in members if self._beside(member.source.file)]))

    def getter_of(self, prop: "Node") -> "Node | None":
        """The operation that reads prop, when its class declares it as a getter: the member that runs."""
        return next(
            (member for member in self._index.members_named(prop.name)
             if member.type == "Operation" and member.get_fact("owner") == prop.get_fact("owner") and member.source.file == prop.source.file),
            None,
        )

    def typed_by_hint(self, hint: str | None, owner: "Node | None" = None) -> "Typed | None":
        """What a type hint written in this file says a value is: one object of the class it names, an optional one
        included; a tuple of such by position; a collection or mapping of one; owner itself for `Self`. None for a
        built-in, a union of two classes, or a name this file does not reach."""
        written = (hint or "").strip().strip("\"'").strip()
        if written.startswith("{") and written.endswith("}"):
            return self._typed_object(written[1:-1], owner)
        optional = _OPTIONAL.match(written)
        if optional:
            written = next(group for group in optional.groups() if group).strip().strip("\"'").strip()
        if written in _SELF_TYPES:
            return Typed(owner) if owner is not None else None
        generic = _GENERIC.match(written)
        if generic:
            return self._typed_generic(generic.group(1).rsplit(".", 1)[-1], _top_level_parts(generic.group(2)), owner)
        array = _ARRAY.match(written)
        if array:
            each = self.typed_by_hint(array.group(1), owner)
            return Typed(each=each) if each is not None else None
        if not _NAME.match(written):
            return None
        found = self.class_named(written)
        return Typed(found) if found is not None else None

    def _typed_object(self, written: str, owner: "Node | None") -> "Typed | None":
        """What a script's object type says each of its fields is: `{ page: FilesPage; stop: () => void }`."""
        fields = []
        for part in _top_level_parts(written, ",;"):
            name, _colon, hint = part.partition(":")
            name = name.strip().removeprefix("readonly ").rstrip("?").strip()
            if _NAME.match(name):
                fields.append((name, self.typed_by_hint(hint, owner)))
        return Typed(fields=tuple(fields)) if any(value is not None for _name, value in fields) else None

    def _typed_generic(self, generic: str, parts: list[str], owner: "Node | None") -> "Typed | None":
        if not parts:
            return None
        if generic in _WRAPPERS:
            return self.typed_by_hint(parts[0], owner)
        if generic in _TUPLES:
            if len(parts) == 2 and parts[1].strip() == "...":
                each = self.typed_by_hint(parts[0], owner)
                return Typed(each=each) if each is not None else None
            items = tuple(self.typed_by_hint(part, owner) for part in parts)
            return Typed(items=items) if any(item is not None for item in items) else None
        if generic in _SEQUENCES:
            each = self.typed_by_hint(parts[0], owner)
            return Typed(each=each) if each is not None else None
        if generic in _MAPPINGS:
            value = self.typed_by_hint(parts[-1], owner)
            return Typed(by_key=value) if value is not None else None
        return None

    def _read_as(self, member: "Node | None") -> "Node | None":
        """A property a getter reads is reached through the getter, the member that runs."""
        if member is None or member.type != "Property":
            return member
        return self.getter_of(member) or member

    def _imported_files(self, name: str | None = None) -> set[str]:
        """The files this file's imports name, those naming name alone when given, in this file's own language; an
        import of a generated language adapter names the Python module it is generated from."""
        return {
            path
            for reference in self._imports if name is None or name in reference.names()
            for path in reference.files()
            if reference.through_adapter() or _language_of(path) == _language_of(self.relative)
        }

    def _in_reach(self, candidates: "list[Node]", name: str) -> "Node | None":
        own = next((node for node in candidates if node.source.file == self.relative), None)
        if own is not None or not candidates:
            return own
        return self._passed_on(candidates, name, frozenset({self.relative})) or self._in_same_package(candidates)

    def _passed_on(self, candidates: "list[Node]", name: str, seen: frozenset) -> "Node | None":
        """The one of candidates a file this file imports name from declares, or passes on in turn: a package's
        `__init__.py` or a script's `index.ts` that re-exports it, by its name or with a star. Each file is followed
        once, so a cycle of re-exports ends."""
        imported = self._imported_files(name)
        found = next((node for node in candidates if node.source.file in imported), None)
        if found is not None:
            return found
        for path in sorted(imported | self._imported_files(STAR)):
            if path not in seen and self._index.has_imports(path):
                found = self._index.file(path)._passed_on(candidates, name, seen | {path})
                if found is not None:
                    return found
        return None

    def _in_same_package(self, candidates: "list[Node]") -> "Node | None":
        """The class a file names with no import, when exactly one file of its own folder, in its own language,
        declares it: a Python or script file whose annotation names a class it does not import means the one beside
        it, never a class of that name in another package."""
        beside = [node for node in candidates if self._beside(node.source.file)]
        return beside[0] if len(beside) == 1 else None

    def _only(self, members: "list[Node]") -> "Node | None":
        """The one of members, when one class alone declares them."""
        return members[0] if len({(member.source.file, member.get_fact("owner")) for member in members}) == 1 else None

    def _beside(self, other: str) -> bool:
        """Whether other is another file of this file's folder written in its language."""
        return other != self.relative and other.rsplit("/", 1)[0] == self.relative.rsplit("/", 1)[0] and _language_of(other) == _language_of(self.relative)

    @property
    def is_script(self) -> bool:
        return _language_of(self.relative) == "script"


class MemberAnswers:
    """What each member of the code read answers, and what each module variable is, where the code writes no type hint
    for it: an operation by what its `return` statements answer, a field by what its class's constructor assigns it,
    and a module variable by what its module assigns it. Each is read once per index, and a member whose answer is being
    read while it is asked again, as a recursion does, answers nothing."""

    _READING = object()

    def __init__(self, index: "CodeIndex") -> None:
        self._index = index
        self._answers: dict[str, object] = {}
        self._fields: dict[tuple[str, str], object] = {}
        self._modules: dict[tuple[str, str], object] = {}
        self._declared: dict[tuple[str, str], object] = {}
        self._texts: dict[str, str] = {}

    def answer_of(self, operation: "Node") -> "Typed | None":
        """What calling operation answers: what its return type names, else what every `return` it writes that the code
        types answers, when they agree."""
        return self._once(self._answers, operation.node_id, lambda: self._answer_of(operation))

    def field_of(self, holder: "Node", name: str) -> "Typed | None":
        """What the field name of holder is when no hint types it: what holder's constructor assigns it."""
        return self._once(self._fields, (holder.node_id, name), lambda: self._field_of(holder, name))

    def module_value(self, relative: str, name: str) -> "Typed | None":
        """What the module variable name the file at relative assigns at the start of a line is."""
        return self._once(self._modules, (relative, name), lambda: self._module_value(relative, name))

    def declared_function(self, relative: str, name: str) -> "Typed | None":
        """What a function the file at relative declares answers, read from the file's text: what the hint its signature
        writes names, else what its `return` statements answer. It reads a function the class model leaves out, such as
        a helper a spec declares in its describe block (`def version(self) -> CddVersion:`), and a script function's
        return type the class model does not keep (`Promise<{ page: FilesPage }>`)."""
        return self._once(self._declared, (relative, name), lambda: self._declared_function(relative, name))

    def _once(self, kept: dict, key, read) -> "Typed | None":
        found = kept.get(key)
        if found is self._READING:
            return None
        if key in kept:
            return found  # type: ignore[return-value]
        kept[key] = self._READING
        kept[key] = read()
        return kept[key]  # type: ignore[return-value]

    def _answer_of(self, operation: "Node") -> "Typed | None":
        owner = self._index.class_declaring(operation)
        file = self._index.file(operation.source.file)
        written = str(operation.get_fact("return_type") or "").strip()
        if written or not operation.source.file:
            return file.typed_by_hint(written, owner)
        if owner is None and file.is_script:
            declared = self.declared_function(operation.source.file, operation.name)
            if declared is not None:
                return declared
        span = self._index.span_of(operation)
        calls = _SpanCalls(file, self._index, span)
        answers = [calls.typed_at(match.end())[0] for match in _RETURN.finditer(span.text)]
        typed = [answer for answer in answers if answer is not None]
        return typed[0] if typed and all(answer == typed[0] for answer in typed) else None

    def _field_of(self, holder: "Node", name: str) -> "Typed | None":
        assigned = re.compile(rf"(?<![\w$.])(?:self|this)\.{re.escape(name)}[ \t]*(?::[ \t]*([^=\n]+?))?[ \t]*=(?![=>])[ \t]*")
        file = self._index.file(holder.source.file)
        for declared in self._index.members_named(name):
            if declared.type != "Property" or declared.get_fact("owner") != holder.name or declared.source.file != holder.source.file:
                continue
            code = CodeSpan.code_of(declared.source.text)
            initialized = re.search(_INITIALIZED.format(name=re.escape(name)), code)
            if initialized is not None:
                found = _SpanCalls(file, self._index, CodeSpan(code, holder)).typed_at(initialized.end())[0]
                if found is not None:
                    return found
        for constructor in self._index.constructors_of(holder):
            span = self._index.span_of(constructor)
            file = self._index.file(constructor.source.file)
            for match in assigned.finditer(span.text):
                found = file.typed_by_hint(match.group(1), holder) if match.group(1) else None
                found = found or _SpanCalls(file, self._index, span).typed_at(match.end())[0]
                if found is not None:
                    return found
        return None

    def _module_value(self, relative: str, name: str) -> "Typed | None":
        text = CodeSpan.code_of(self._text_of(relative))
        match = re.search(_MODULE_ASSIGNMENT.format(name=re.escape(name)), text)
        file = self._index.file(relative)
        if match is None:
            declared = re.search(_MODULE_DECLARATION.format(name=re.escape(name)), text) if file.is_script else None
            return file.typed_by_hint(declared.group(1)) if declared is not None else None
        if match.group(1):
            return file.typed_by_hint(match.group(1))
        return _SpanCalls(file, self._index, CodeSpan("")).typed_at(match.end(), text)[0]

    def _declared_function(self, relative: str, name: str) -> "Typed | None":
        text = self._text_of(relative)
        file = self._index.file(relative)
        found = _script_function(text, name) if file.is_script else _python_function(text, name)
        if found is None:
            return None
        hint, body = found
        if hint:
            return file.typed_by_hint(hint)
        code = CodeSpan.code_of(body)
        calls = _SpanCalls(file, self._index, CodeSpan(code))
        answers = [answer for answer in (calls.typed_at(match.end())[0] for match in _RETURN.finditer(code)) if answer is not None]
        return answers[0] if answers and all(answer == answers[0] for answer in answers) else None

    def _text_of(self, relative: str) -> str:
        if relative not in self._texts:
            try:
                self._texts[relative] = (Path(self._index.source_root) / relative).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError, TypeError):
                self._texts[relative] = ""
        return self._texts[relative]


class _Step(NamedTuple):
    """One step of a chain after its first name: a member it names, a call, or an item it takes, with what it writes."""

    kind: str
    text: str


class _Chain(NamedTuple):
    """An expression that starts with a name and follows it through members, calls, and items, and where it ends."""

    head: str
    steps: list
    end: int


class _SpanCalls:
    """One span of a file's code read for what it calls and reads: it knows the class it is written in, what each local
    it names is, and through them what each receiver in it is."""

    def __init__(self, file: CodeFile, index: "CodeIndex", span: CodeSpan) -> None:
        self._file = file
        self._index = index
        self._answers = index.answers
        self._code = span.text
        self._owner = span.owner
        # What each local is, by its name, from its first assignment the code types.
        self._locals: dict[str, Typed] = {}
        for name, hint in span.typed.items():
            self._keep_local(name, file.typed_by_hint(hint, self._owner))
        for code in (span.before, self._code):
            self._name_locals_in(code)

    def called(self) -> "list[Node]":
        """The members its code calls and the properties it reads, in the order the code names them."""
        return [*self._reached_through_receivers(), *self._called_by_name()]

    def typed_at(self, start: int, code: str | None = None) -> "tuple[Typed | None, int]":
        """What the expression that starts at start in code (the span's own by default) is, and where it ends: one
        chain, a tuple of chains separated by commas, or a script's chain cast `as` a class. None when it is anything
        else, such as a sum or a condition."""
        code = self._code if code is None else code
        parts: list = []
        position = start
        while True:
            found, end = self._typed_chain_at(code, position)
            parts.append(found)
            comma = _NEXT_PART.match(code, end)
            if comma is None:
                break
            position = comma.end()
        if len(parts) > 1:
            return (Typed(items=tuple(parts)) if any(part is not None for part in parts) else None), end
        return parts[0], end

    def _typed_chain_at(self, code: str, start: int) -> "tuple[Typed | None, int]":
        """What the one chain at start is, when the statement or tuple part ends with it."""
        found, end = self._chain_value(code, start)
        rest = code[end:].lstrip(" \t")
        if rest and rest[0] not in _ENDS and _ALTERNATIVE.match(rest) is None:
            return None, end
        return found, end

    def _chain_value(self, code: str, start: int) -> "tuple[Typed | None, int]":
        """What the chain at start is, after an `await` or `new`, and cast `as` a class in a script, and where it ends."""
        prefix = _PREFIX.match(code, start)
        position = prefix.end() if prefix else start
        if code[position:position + 1] == "{" and self._file.is_script:
            return self._object_at(code, position)
        chain = _chain_at(code, position)
        if chain is None:
            return None, start
        found = self._walk(chain, [])
        cast = _CAST.match(code, chain.end) if self._file.is_script else None
        if cast is not None:
            return self._file.typed_by_hint(cast.group(1), self._owner), cast.end()
        return found, chain.end

    def _object_at(self, code: str, opening: int) -> "tuple[Typed | None, int]":
        """What a script's object literal at opening holds, field by field: `{ page, opened: board.openedChats() }`."""
        closing = _closing(code, opening)
        if closing is None:
            return None, opening
        fields = []
        position = opening + 1
        while position < closing:
            named = _OBJECT_FIELD.match(code, position)
            if named is None:
                break
            if named.group(2):
                value, end = self._typed_chain_at(code, named.end())
            else:
                value, end = self._locals.get(named.group(1)), named.end()
            fields.append((named.group(1), value))
            following = re.compile(r"\s*,").match(code, end)
            if following is None:
                break
            position = following.end()
        found = Typed(fields=tuple(fields)) if any(value is not None for _name, value in fields) else None
        return found, closing + 1

    def _name_locals_in(self, code: str) -> None:
        """Type each local code declares, assigns, loops over, or opens a block on, in the order the code writes them:
        by its hint, else by what the expression assigned to it is."""
        readers = (
            (_DECLARED_LOCAL, lambda match: [(match.group(1), self._file.typed_by_hint(match.group(2), self._owner))]),
            (_ASSIGNMENT, lambda match: self._assigned(code, match)),
            (_DESTRUCTURED, lambda match: self._destructured(code, match)),
            (_LOOP, lambda match: [(match.group(1), self._element_of(self._typed_chain_at(code, match.end())[0]))]),
            (_WITH, lambda match: self._opened(code, match.end())),
        )
        # Each is typed after the ones written before it, which its expression may use.
        found = sorted(((match.start(), read, match) for pattern, read in readers for match in pattern.finditer(code)), key=lambda item: item[0])
        for _position, read, match in found:
            for name, value in read(match):
                self._keep_local(name, value)

    def _assigned(self, code: str, match: re.Match) -> "list[tuple[str, Typed | None]]":
        names = [name.strip() for name in match.group(1).strip("()").split(",")]
        if match.group(2) and len(names) == 1:
            return [(names[0], self._file.typed_by_hint(match.group(2), self._owner))]
        value, _end = self.typed_at(match.end(), code)
        if len(names) == 1:
            return [(names[0], value)]
        items = value.items if value is not None else ()
        return [(name, items[position] if position < len(items) else None) for position, name in enumerate(names)]

    def _destructured(self, code: str, match: re.Match) -> "list[tuple[str, Typed | None]]":
        """Each local a script takes out of an object by its field's name: `const { page, stop } = await opened()`."""
        value, _end = self.typed_at(match.end(), code)
        fields = dict(value.fields) if value is not None else {}
        found = []
        for part in _top_level_parts(match.group(1)):
            field, _colon, local = part.split("=")[0].partition(":")
            local = (local or field).strip()
            if _NAME.match(local):
                found.append((local, fields.get(field.strip())))
        return found

    def _opened(self, code: str, start: int) -> "list[tuple[str, Typed | None]]":
        """Each local a Python `with` opens, as the object it opens is."""
        opened = []
        position = start
        while True:
            value, end = self._chain_value(code, position)
            local = _AS_LOCAL.match(code, end)
            if local is None:
                return opened
            opened.append((local.group(1), value))
            following = _NEXT_PART.match(code, local.end())
            if following is None:
                return opened
            position = following.end()

    def _keep_local(self, name: str, found: "Typed | None") -> None:
        if found is not None and name not in _OWN_OBJECT:
            self._locals.setdefault(name, found)

    def _reached_through_receivers(self) -> "Iterator[Node]":
        """Each member a chain reaches: every member it names after its first name is a member of what the part before
        it is, and a call's answer or an item it takes is what the next member is found on. A member with a call after
        it may be an operation; any other is a property read. A name of no known class followed by one member reaches
        the member the file's reach declares once."""
        for head in _HEAD.finditer(self._code):
            chain = _chain_at(self._code, head.start())
            if chain is not None and chain.steps:
                reached: list = []
                self._walk(chain, reached)
                yield from reached

    def _walk(self, chain: _Chain, reached: list) -> "Typed | None":
        """What chain is, adding to reached each member it calls or reads on the way."""
        steps = chain.steps
        value, at = self._typed_head(chain.head, steps)
        if value is None and at == 0 and steps and steps[0].kind == "member" and _is_class_name(steps[0].text):
            value, at = self._through_module(chain.head, steps, reached)
        guessed =at == 0 and _is_local_name(chain.head) and bool(steps) and steps[0].kind == "member"
        guessed = guessed and (len(steps) == 1 or steps[1].kind != "member")
        # A local of no known class, or of a class that neither declares nor inherits the member, such as one a
        # decorator gives its members, reaches the one member of that name the file's reach declares.
        if guessed and (value is None or (value.of is not None and self._member_of(value.of, steps[0].text) is None)):
            only = self._file.only_member_named(steps[0].text, len(steps) > 1 and steps[1].kind == "call")
            if only is not None:
                reached.append(only)
            return None
        while at < len(steps):
            step = steps[at]
            if value is None:
                return None
            if step.kind == "item":
                value = self._item_of(value, step.text)
                at += 1
                continue
            if step.kind == "member" and value.fields:
                value = dict(value.fields).get(step.text)
                at += 1
                continue
            if step.kind == "call" or value.of is None:
                return None
            called = at + 1 < len(steps) and steps[at + 1].kind == "call"
            member = self._member_of(value.of, step.text)
            if member is not None and (member.type == "Property" or called or self._file.getter_of(member) is member):
                reached.append(member)
            value = self._as_receiver(self._answer_of(value.of, step.text, member, called), value.of, member)
            at += 2 if called else 1
        return value

    def _through_module(self, head: str, steps: list, reached: list) -> "tuple[Typed | None, int]":
        """A class the file reaches through a module it imports, `prompt_log.LoggedFile(path)`: built when called, which
        runs its constructor, else the class itself."""
        if head in self._locals or head in _OWN_OBJECT:
            return None, 0
        named = self._file.class_named(steps[0].text)
        if named is None:
            return None, 0
        if len(steps) > 1 and steps[1].kind == "call":
            reached.extend(self._index.constructors_of(named))
            return Typed(named), 2
        return Typed(named), 1

    def _typed_head(self, head: str, steps: list) -> "tuple[Typed | None, int]":
        """What a chain's first name is, and the step its walk goes on from: a call of a class builds one of it, a call
        of a function answers what the function returns."""
        called = bool(steps) and steps[0].kind == "call"
        if head in _BASE_OBJECT:
            base = next(iter(self._bases_of(self._owner)), None) if self._owner is not None else None
            return (Typed(base) if base is not None else None), (1 if called else 0)
        if called:
            if head in self._locals:
                return None, 1
            built = self._owner if head == "cls" else self._file.class_named(head) if _is_class_name(head) else None
            if built is not None:
                return Typed(built), 1
            function = self._file.function_named(head)
            if function is None:
                return self._answers.declared_function(self._file.relative, head), 1
            return self._answers.answer_of(function), 1
        if head in _OWN_OBJECT:
            return (Typed(self._owner) if self._owner is not None else None), 0
        if head in self._locals:
            return self._locals[head], 0
        if _is_class_name(head):
            named = self._file.class_named(head)
            if named is not None:
                return Typed(named), 0
        return self._file.module_value(head), 0

    def _answer_of(self, holder: "Node", name: str, member: "Node | None", called: bool) -> "Typed | None":
        """What holder's member called name answers: a call's return, else the member's or field's value."""
        if called:
            return self._answers.answer_of(member) if member is not None and member.type == "Operation" else None
        declaring = self._declaring(holder, member)
        file = self._index.file(declaring.source.file)
        if member is not None and member.get_fact("value_type"):
            return file.typed_by_hint(str(member.get_fact("value_type")), declaring)
        getter = self._file.getter_of(member) if member is not None else None
        if getter is not None:
            return self._answers.answer_of(getter)
        if member is not None and member.type == "Operation":
            return None
        for owner in [holder, *self._bases_of(holder)]:
            hint = (owner.get_fact("held_fields") or {}).get(name)
            if hint:
                return self._index.file(owner.source.file).typed_by_hint(str(hint), owner)
            found = self._answers.field_of(owner, name)
            if found is not None:
                return found
        return None

    def _as_receiver(self, answer: "Typed | None", holder: "Node", member: "Node | None") -> "Typed | None":
        """A member a class extends that answers the class declaring it answers the receiver's own class, as `Self` and
        `return self` do: `markdown_map.copy_of(source)` is a markdown map."""
        if answer is None or answer.of is None or member is None:
            return answer
        declaring = self._index.class_declaring(member)
        return Typed(holder) if declaring is not None and answer.of is declaring and holder is not declaring else answer

    def _declaring(self, holder: "Node", member: "Node | None") -> "Node":
        """The class that declares member, holder itself or a class it extends."""
        if member is None or member.get_fact("owner") == holder.name and member.source.file == holder.source.file:
            return holder
        return self._index.class_declaring(member) or holder

    def _item_of(self, value: Typed, written: str) -> "Typed | None":
        """What an item value takes is: a tuple's part by its position, a collection's element, a mapping's value, or
        what its class's `__getitem__` answers."""
        if value.items and _INTEGER.match(written.strip()):
            position = int(written.strip())
            return value.items[position] if -len(value.items) <= position < len(value.items) else None
        if value.each is not None:
            return value.each
        if value.by_key is not None:
            return value.by_key
        if value.of is not None:
            getitem = self._member_of(value.of, "__getitem__")
            return self._answers.answer_of(getitem) if getitem is not None else None
        return None

    def _element_of(self, value: "Typed | None") -> "Typed | None":
        """What each element a loop over value takes is: a collection's element, or what its class's `__iter__` yields."""
        if value is None:
            return None
        if value.each is not None:
            return value.each
        if value.of is not None:
            iterate = self._member_of(value.of, "__iter__")
            walked = self._answers.answer_of(iterate) if iterate is not None else None
            return walked.each if walked is not None else None
        return None

    def _called_by_name(self) -> "Iterator[Node]":
        """Each module function its code calls by name alone, the constructor of each class it builds by its name, and
        the constructor of the class it extends for a brace language's `super(...)`."""
        for name in dict.fromkeys(_BARE_CALL.findall(self._code)):
            if name == "super":
                base = next(iter(self._bases_of(self._owner)), None) if self._owner is not None else None
                constructor = self._member_of(base, "constructor") if base is not None else None
                if constructor is not None:
                    yield constructor
                continue
            function = self._file.function_named(name)
            if function is not None:
                yield function
            elif _is_class_name(name):
                yield from self._file.constructors_of(name)

    def _member_of(self, holder: "Node", name: str, seen: frozenset = frozenset()) -> "Node | None":
        """The member called name that holder declares, an operation before a property, else the one a class it
        extends declares."""
        declared = next(
            (member for member in self._index.members_named(name)
             if member.get_fact("owner") == holder.name and member.source.file == holder.source.file),
            None,
        )
        if declared is not None or holder.node_id in seen:
            return declared
        inherited = (self._member_of(base, name, seen | {holder.node_id}) for base in self._bases_of(holder))
        return next((member for member in inherited if member is not None), None)

    def _bases_of(self, holder: "Node") -> "list[Node]":
        file = self._index.file(holder.source.file) if holder.source.file != self._file.relative else self._file
        named = (file.class_named(str(base).split("[")[0].split("<")[0].strip()) for base in holder.get_fact("bases") or [])
        return [base for base in named if base is not None and base is not holder]


def _chain_at(code: str, start: int) -> "_Chain | None":
    """The chain that starts with the name at start: each member, call, and item written straight after it."""
    head = _IDENTIFIER.match(code, start)
    if head is None:
        return None
    steps: list = []
    position = head.end()
    while position < len(code):
        character = code[position]
        if character == "." or (character in "?!" and code[position + 1:position + 2] == "."):
            dot = position + (1 if character == "." else 2)
            member = _IDENTIFIER.match(code, dot)
            if member is None:
                break
            steps.append(_Step("member", member.group(0)))
            position = member.end()
        elif character == "!" and code[position + 1:position + 2] in ("[", "("):
            position += 1
        elif character in "([":
            closing = _closing(code, position)
            if closing is None:
                break
            steps.append(_Step("call" if character == "(" else "item", code[position + 1:closing]))
            position = closing + 1
        else:
            break
    return _Chain(head.group(0), steps, position)


def _closing(code: str, opening: int) -> "int | None":
    """Where the bracket that opens at opening closes, skipping strings; none when it does not close."""
    depth = 0
    position = opening
    quote = ""
    while position < len(code):
        character = code[position]
        if quote:
            if character == "\\":
                position += 1
            elif character == quote:
                quote = ""
        elif character in _QUOTES:
            quote = character
        elif character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
            if depth == 0:
                return position
        position += 1
    return None


def _top_level_parts(written: str, separators: str = ",") -> list[str]:
    """written split at each separator no bracket encloses."""
    parts, depth, current = [], 0, ""
    for character in written:
        if character in "[<({":
            depth += 1
        elif character in "]>)}":
            depth -= 1
        if character in separators and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += character
    if current.strip():
        parts.append(current.strip())
    return parts


def _is_local_name(head: str) -> bool:
    """Whether a chain's head is a variable's name: a lower-case name that is neither the object itself nor its base."""
    return head[:1].islower() and head not in _OWN_OBJECT and head not in _BASE_OBJECT


def _language_of(file: str) -> str:
    """The language family a file is written in, by its extension: every script extension is one family."""
    suffix = "." + file.rsplit(".", 1)[-1].lower()
    return "script" if suffix in _SCRIPT_SUFFIXES else suffix


def _python_function(text: str, name: str) -> "tuple[str, str] | None":
    """The return type a Python function's signature writes, and its body's lines."""
    declared = re.search(_PYTHON_DEF.format(name=re.escape(name)), text)
    closing = _closing(text, declared.end() - 1) if declared else None
    signature = _SIGNATURE_END.match(text, closing + 1) if closing is not None else None
    if signature is None:
        return None
    indent = len(declared.group(1))
    body = []
    for line in text[signature.end():].splitlines()[1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        body.append(line)
    return (signature.group(1) or "").strip(), "\n".join(body)


def _script_function(text: str, name: str) -> "tuple[str, str] | None":
    """The return type a script function's signature writes, `function opened(): Promise<{ page: FilesPage }> {` or
    `const opened = async (): Promise<Page> => {`, and its body's block."""
    declared = re.search(_SCRIPT_FUNCTION.format(name=re.escape(name)), text)
    closing = _closing(text, declared.end() - 1) if declared else None
    if closing is None:
        return None
    position = closing + 1
    while position < len(text) and text[position] in " \t":
        position += 1
    hint = ""
    if text[position:position + 1] == ":":
        hint, position = _script_return_type(text, position + 1)
    arrow = re.match(r"\s*=>\s*", text[position:])
    if arrow is not None:
        position += arrow.end()
    while position < len(text) and text[position] in " \t\n":
        position += 1
    if text[position:position + 1] != "{":
        return hint, ("return " + text[position:text.find("\n", position)]) if arrow is not None else ""
    body_end = _closing(text, position)
    return hint, text[position + 1:body_end] if body_end is not None else ""


def _script_return_type(text: str, start: int) -> "tuple[str, int]":
    """The return type written from start, up to the body's brace or arrow: an object type's braces are part of it."""
    depth = 0
    position = start
    while position < len(text):
        character = text[position]
        if depth == 0 and text.startswith("=>", position):
            break
        if depth == 0 and character == "{":
            written = text[start:position].strip()
            if written and not written.endswith(("|", "&", ":", "<", ",")):
                break
        if character in "<({[":
            depth += 1
        elif character in ")}]" or (character == ">" and text[position - 1] != "="):
            depth -= 1
        position += 1
    return text[start:position].strip(), position


def _is_class_name(name: str) -> bool:
    """Whether a name is written as a class's is: capitalised, after any underscores that mark it private
    (`Order`, `_StoryMapFolder`)."""
    return name.lstrip("_")[:1].isupper()
