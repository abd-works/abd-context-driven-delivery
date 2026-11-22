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

import keyword
import re
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, NamedTuple

from cdd_guidance.practices.clean_engineering.model import CONSTRUCTOR_NAMES, MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.reading.receiver_causes import (
    ON_OUTSIDE_OBJECTS,
    OTHERWISE,
    UNRESOLVED_CALLS_FACTS,
    ReceiverCauses,
    UnjoinedCalls,
)
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
# A call's arguments that look an object up rather than hand it one: a string, or a name, path, key, or slug.
_LOOKUP_ARGUMENTS = re.compile(r"[\"'`]|(?i:\b\w*(?:name|path|key|slug)s?\b)")

# How the code of one class reaches another class it depends on, which its dependency edge keeps (``reached``): the
# class is built on each call, or in the constructor or a field's initializer; found through a class operation, a call
# with a name, path, or key, or a mapping's item; held in a field of its own; handed in as a parameter; reached through
# another object it calls or reads; a module's own object, such as a registry a module assigns; or named as a value,
# as an isinstance check, a list, or a call it is handed to names the class itself.
CREATED_ON_EACH_CALL = "created on each call"
CREATED_IN_THE_CONSTRUCTOR = "created in the constructor"
LOOKED_UP_BY_NAME = "looked up by name"
HELD_AS_A_FIELD = "held as a field"
HANDED_IN_AS_A_PARAMETER = "handed in as a parameter"
REACHED_THROUGH_ANOTHER_OBJECT = "reached through another object"
A_MODULES_OBJECT = "a module's object"
NAMED_AS_A_VALUE = "named as a value"
# A receiver that is the object itself or the class it extends, which no dependency reaches, and a class named outright,
# whose operation a call reaches through the class.
_ITSELF = ""
_THE_CLASS = "the class itself"
_CREATED = frozenset({CREATED_ON_EACH_CALL, CREATED_IN_THE_CONSTRUCTOR})
# The facts a dependency edge keeps: how the class reaches the class it depends on, and the members it reaches it
# through. The fact an invokes edge keeps when no call it records was joined by its receiver's class, only by a guess.
REACHED_FACT = "reached"
THROUGH_FACT = "through"
JOINED_FACT = "joined"
JOINED_BY_A_GUESS = "by a guess: one class in reach declares the name"
# Where a class named as a value is a type instead: after these, or as the subject of a generic or a subscript.
_TYPE_MARKS = ("->", "|", "&", "<", "@")
_AS_CAST = re.compile(r"\bas$")
# The name a subscript is taken on, `list` in `list[Line]`, and the words after which a bracket opens a list instead.
_SUBSCRIPTED = re.compile(r"[A-Za-z_$][\w$.]*$")
_VALUE_WORDS = frozenset({*keyword.kwlist, "return", "yield", "await", "in", "of", "typeof", "new", "case", "throw"})
# A string written on one line, which a span's bare class names are not read inside.
_STRING = re.compile(r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`")


class CodeSpan(NamedTuple):
    """A span of code to read for what it calls: its text, the class it is written in (none outside a class, such as
    a spec's block), the type hint of each parameter it takes, by the parameter's name, the code that runs before
    it, such as a spec's setups, read only for the locals it makes, and whether it runs while its object is built, as a
    constructor and a field's initializer do. A parameter with no hint is a name whose class the code does not say."""

    text: str
    owner: "Node | None" = None
    typed: dict[str, str] = {}
    before: str = ""
    builds_its_object: bool = False

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

    @property
    def class_held(self) -> "Node | None":
        """The class of the object this value is, or of each element or each value it holds; none for a tuple or a
        script's object of fields."""
        inner = self.each or self.by_key
        return self.of if self.of is not None else inner.class_held if inner is not None else None

    @property
    def is_many(self) -> bool:
        """Whether this value holds many objects: a collection or a mapping."""
        return self.each is not None or self.by_key is not None


class _Read(NamedTuple):
    """What an expression of the code is, where it ends, how the code reaches the object it is, and, when the read
    cannot tell its class, why (a cause of ``receiver_causes``)."""

    value: "Typed | None"
    end: int
    reach: str = REACHED_THROUGH_ANOTHER_OBJECT
    cause: str = OTHERWISE


class SpanReach:
    """What one span of code reaches: each member it calls or reads, in the order its code names them, and those of them
    joined by a guess, since one class in reach alone declares the name its receiver of no known class is called by;
    each class of the code it creates, calls, reads, or names as a value, with how it reaches that class; and, by cause,
    how many of its calls name an operation some class of the code declares on a receiver whose class the read cannot
    tell, which are joined to nothing, so a rule can tell a call the read cannot see from one the code does not make."""

    def __init__(self) -> None:
        self.members: list["Node"] = []
        self.guessed: list["Node"] = []
        self.classes: list[tuple["Node", str]] = []
        self.unresolved_calls: dict[str, int] = {cause: 0 for cause in UNRESOLVED_CALLS_FACTS}

    def reach_class(self, reached: "Node", reach: str) -> None:
        """Keep that the span reaches the class reached the way reach says; a class named outright is looked up."""
        self.classes.append((reached, LOOKED_UP_BY_NAME if reach == _THE_CLASS else reach))

    def joined_only_by_a_guess(self, member: "Node") -> bool:
        """Whether every call of member the span makes was joined to it by a guess."""
        return sum(1 for found in self.members if found is member) == sum(1 for found in self.guessed if found is member)


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
        self._causes: ReceiverCauses | None = None

    @property
    def receiver_causes(self) -> ReceiverCauses:
        """Why a receiver of this file's code has no class the read can tell, as the file's text says, read once."""
        if self._causes is None:
            self._causes = ReceiverCauses(self, self._index.answers.text_of(self.relative), Path(self._index.source_root))
        return self._causes

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
        return list(dict.fromkeys(self.reach_of(span).members))

    def reach_of(self, span: CodeSpan) -> SpanReach:
        """What span reaches: the members it calls and reads, the classes it reaches and how, and the calls it makes on
        a receiver whose class its code does not say."""
        return _SpanCalls(self, self._index, span).reach()

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

    def held_in(self, holder: "Node", name: str) -> "Typed | None":
        """What holder's own field name holds, private or public: what the type hint holder keeps for it names
        (``held_fields``), else what its constructor or its initializer assigns it."""
        hint = (holder.get_fact("held_fields") or {}).get(name)
        typed = self._index.file(holder.source.file).typed_by_hint(str(hint), holder) if hint else None
        return typed if typed is not None else self.field_of(holder, name)

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
        text = CodeSpan.code_of(self.text_of(relative))
        match = re.search(_MODULE_ASSIGNMENT.format(name=re.escape(name)), text)
        file = self._index.file(relative)
        if match is None:
            declared = re.search(_MODULE_DECLARATION.format(name=re.escape(name)), text) if file.is_script else None
            return file.typed_by_hint(declared.group(1)) if declared is not None else None
        if match.group(1):
            return file.typed_by_hint(match.group(1))
        return _SpanCalls(file, self._index, CodeSpan("")).typed_at(match.end(), text)[0]

    def _declared_function(self, relative: str, name: str) -> "Typed | None":
        text = self.text_of(relative)
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

    def text_of(self, relative: str) -> str:
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
        # How the span reaches an object it builds: while its object is built, or on each call.
        self._creates = CREATED_IN_THE_CONSTRUCTOR if span.builds_its_object else CREATED_ON_EACH_CALL
        # What each local is, by its name, from its first assignment the code types, and how the code reaches it; and
        # the calls the span makes that the read cannot join, with why each name it writes has no class.
        self._locals: dict[str, Typed] = {}
        self._reaches: dict[str, str] = {}
        self._unjoined = UnjoinedCalls(file, index)
        for name, hint in span.typed.items():
            self._keep_local(name, file.typed_by_hint(hint, self._owner), HANDED_IN_AS_A_PARAMETER, file.receiver_causes.of_hint(hint))
        for code in (span.before, self._code):
            self._name_locals_in(code)

    def reach(self) -> SpanReach:
        """The members its code calls and the properties it reads, in the order the code names them, the classes it
        reaches and how, and the calls it could not join."""
        found = SpanReach()
        self._reach_through_receivers(found)
        found.members.extend(self._called_by_name())
        return found

    def typed_at(self, start: int, code: str | None = None) -> _Read:
        """What the expression that starts at start in code (the span's own by default) is, where it ends, and how the
        code reaches it: one chain, a tuple of chains separated by commas, or a script's chain cast `as` a class. None
        when it is anything else, such as a sum or a condition."""
        code = self._code if code is None else code
        parts: list[_Read] = []
        position = start
        while True:
            read = self._typed_chain_at(code, position)
            parts.append(read)
            comma = _NEXT_PART.match(code, read.end)
            if comma is None:
                break
            position = comma.end()
        if len(parts) > 1:
            values = tuple(part.value for part in parts)
            return _Read(Typed(items=values) if any(value is not None for value in values) else None, parts[-1].end, parts[0].reach)
        return parts[0]

    def _typed_chain_at(self, code: str, start: int) -> _Read:
        """What the one chain at start is, when the statement or tuple part ends with it."""
        read = self._chain_value(code, start)
        rest = code[read.end:].lstrip(" \t")
        if rest and rest[0] not in _ENDS and _ALTERNATIVE.match(rest) is None:
            return _Read(None, read.end)
        return read

    def _chain_value(self, code: str, start: int) -> _Read:
        """What the chain at start is, after an `await` or `new`, and cast `as` a class in a script, and where it ends."""
        prefix = _PREFIX.match(code, start)
        position = prefix.end() if prefix else start
        if code[position:position + 1] == "{" and self._file.is_script:
            return self._object_at(code, position)
        chain = _chain_at(code, position)
        if chain is None:
            return _Read(None, start, cause=ON_OUTSIDE_OBJECTS if ReceiverCauses.is_literal(code, position) else OTHERWISE)
        found, reach, cause = self._walk(chain, None)
        cast = _CAST.match(code, chain.end) if self._file.is_script else None
        if cast is not None:
            return _Read(self._file.typed_by_hint(cast.group(1), self._owner), cast.end(), reach, self._file.receiver_causes.of_hint(cast.group(1)))
        return _Read(found, chain.end, reach, cause)

    def _object_at(self, code: str, opening: int) -> _Read:
        """What a script's object literal at opening holds, field by field: `{ page, opened: board.openedChats() }`."""
        closing = _closing(code, opening)
        if closing is None:
            return _Read(None, opening)
        fields = []
        position = opening + 1
        while position < closing:
            named = _OBJECT_FIELD.match(code, position)
            if named is None:
                break
            if named.group(2):
                value, end, _reach, _cause = self._typed_chain_at(code, named.end())
            else:
                value, end = self._locals.get(named.group(1)), named.end()
            fields.append((named.group(1), value))
            following = re.compile(r"\s*,").match(code, end)
            if following is None:
                break
            position = following.end()
        found = Typed(fields=tuple(fields)) if any(value is not None for _name, value in fields) else None
        return _Read(found, closing + 1)

    def _name_locals_in(self, code: str) -> None:
        """Type each local code declares, assigns, loops over, or opens a block on, in the order the code writes them:
        by its hint, else by what the expression assigned to it is, with how the code reaches it."""
        readers = (
            (_DECLARED_LOCAL, lambda match: [(match.group(1), self._hinted(match.group(2), _Read(None, 0)))]),
            (_ASSIGNMENT, lambda match: self._assigned(code, match)),
            (_DESTRUCTURED, lambda match: self._destructured(code, match)),
            (_LOOP, lambda match: [(match.group(1), self._element_read(self._typed_chain_at(code, match.end())))]),
            (_WITH, lambda match: self._opened(code, match.end())),
        )
        # Each is typed after the ones written before it, which its expression may use.
        found = sorted(((match.start(), read, match) for pattern, read in readers for match in pattern.finditer(code)), key=lambda item: item[0])
        for _position, read, match in found:
            for name, value in read(match):
                self._keep_local(name, value.value, value.reach, value.cause)

    def _hinted(self, hint: str, read: _Read) -> _Read:
        """What a value a type hint types is, reached as read says, with why it has no class when the hint names none."""
        return _Read(self._file.typed_by_hint(hint, self._owner), read.end, read.reach, self._file.receiver_causes.of_hint(hint))

    def _assigned(self, code: str, match: re.Match) -> "list[tuple[str, _Read]]":
        names = [name.strip() for name in match.group(1).strip("()").split(",")]
        read = self.typed_at(match.end(), code)
        if match.group(2) and len(names) == 1:
            return [(names[0], self._hinted(match.group(2), read))]
        if len(names) == 1:
            return [(names[0], read)]
        items = read.value.items if read.value is not None else ()
        return [(name, _Read(items[position] if position < len(items) else None, read.end, read.reach, read.cause)) for position, name in enumerate(names)]

    def _destructured(self, code: str, match: re.Match) -> "list[tuple[str, _Read]]":
        """Each local a script takes out of an object by its field's name: `const { page, stop } = await opened()`."""
        read = self.typed_at(match.end(), code)
        fields = dict(read.value.fields) if read.value is not None else {}
        found = []
        for part in _top_level_parts(match.group(1)):
            field, _colon, local = part.split("=")[0].partition(":")
            local = (local or field).strip()
            if _NAME.match(local):
                found.append((local, _Read(fields.get(field.strip()), read.end, read.reach, read.cause)))
        return found

    def _opened(self, code: str, start: int) -> "list[tuple[str, _Read]]":
        """Each local a Python `with` opens, as the object it opens is."""
        opened = []
        position = start
        while True:
            read = self._chain_value(code, position)
            local = _AS_LOCAL.match(code, read.end)
            if local is None:
                return opened
            opened.append((local.group(1), read))
            following = _NEXT_PART.match(code, local.end())
            if following is None:
                return opened
            position = following.end()

    def _element_read(self, read: _Read) -> _Read:
        """Each element a loop over what read is takes, reached as the collection is."""
        return _Read(self._element_of(read.value), read.end, read.reach, read.cause)

    def _keep_local(self, name: str, found: "Typed | None", reach: str, cause: str) -> None:
        if name in _OWN_OBJECT or name in self._locals:
            return
        if found is None:
            self._unjoined.keep_local(name, cause)
            return
        self._locals[name] = found
        self._reaches[name] = reach

    def _reach_through_receivers(self, found: SpanReach) -> None:
        """Each member a chain reaches: every member it names after its first name is a member of what the part before
        it is, and a call's answer or an item it takes is what the next member is found on. A member with a call after
        it may be an operation; any other is a property read. A name of no known class followed by one member reaches
        the member the file's reach declares once. A class the code names alone, as a value, is reached that way."""
        # The code with each string blanked, where a bare name is read only outside a string.
        masked = _STRING.sub(lambda written: " " * len(written.group(0)), self._code)
        for head in _HEAD.finditer(self._code):
            chain = _chain_at(self._code, head.start())
            if chain is not None and chain.steps:
                self._walk(chain, found)
            elif chain is not None and masked[head.start()] != " ":
                self._name_value(found, chain.head, masked, head.start())

    def _name_value(self, found: SpanReach, head: str, masked: str, start: int) -> None:
        """Keep the class a bare name names, when it names a class of the code as a value and not as a type."""
        named = self._file.class_named(head) if _is_class_name(head) and head not in self._locals else None
        if named is not None and named is not self._owner and not _names_a_type(masked, start):
            found.reach_class(named, NAMED_AS_A_VALUE)

    def _walk(self, chain: _Chain, found: SpanReach | None) -> "tuple[Typed | None, str, str]":
        """What chain is, how the code reaches it, and, when the read cannot tell its class, why; adding to found, when
        given, each member it calls or reads on the way, each class it reaches and how, and each call it cannot join."""
        steps = chain.steps
        value, at, reach = self._typed_head(chain.head, steps)
        if value is None and at == 0 and steps and steps[0].kind == "member" and _is_class_name(steps[0].text):
            value, at, reach = self._through_module(chain.head, steps, found)
        cause = self._unjoined.of_head(chain.head, bool(steps) and steps[0].kind == "call") if value is None else OTHERWISE
        guessed = at == 0 and _is_local_name(chain.head) and bool(steps) and steps[0].kind == "member"
        guessed = guessed and (len(steps) == 1 or steps[1].kind != "member")
        # A local of no known class, or of a class that neither declares nor inherits the member, such as one a
        # decorator gives its members, reaches the one member of that name the file's reach declares.
        if guessed and (value is None or (value.of is not None and self._member_of(value.of, steps[0].text) is None)):
            self._guess(steps, value, found, cause)
            return None, reach, cause
        if found is not None and value is not None and value.of is not None and reach in _CREATED:
            found.reach_class(value.of, reach)
        while at < len(steps):
            step = steps[at]
            calls = at + 1 < len(steps) and steps[at + 1].kind == "call"
            if value is None:
                if found is not None and step.kind == "member" and calls:
                    self._unjoined.count(found.unresolved_calls, step.text, cause)
                return None, reach, cause
            if step.kind == "item":
                reach = LOOKED_UP_BY_NAME if value.by_key is not None else reach
                value = self._item_of(value, step.text)
                at += 1
                continue
            if step.kind == "member" and value.fields:
                value = dict(value.fields).get(step.text)
                at += 1
                continue
            if step.kind == "call" or value.of is None:
                return None, reach, ON_OUTSIDE_OBJECTS if value.is_many else OTHERWISE
            member = self._member_of(value.of, step.text)
            if found is not None:
                self._reach_member(found, value.of, member, reach, calls)
            answer = self._answer_of(value.of, step.text, member, calls)
            if answer is None:
                cause = self._unjoined.of_member([value.of, *self._bases_of(value.of)], step.text, member, calls)
            value = self._as_receiver(answer, value.of, member)
            reach = _reach_after(reach, steps[at + 1].text if calls else None)
            at += 2 if calls else 1
        return value, reach, cause

    def _reach_member(self, found: SpanReach, holder: "Node", member: "Node | None", reach: str, called: bool) -> None:
        """Keep the member a step reaches on holder, and the class holder when the code reaches another object."""
        if member is not None and (member.type == "Property" or called or self._file.getter_of(member) is member):
            found.members.append(member)
        if reach != _ITSELF:
            found.reach_class(holder, reach)

    def _guess(self, steps: list, value: "Typed | None", found: SpanReach | None, cause: str) -> None:
        """The one member of the step's name the file's reach declares, for a receiver of no known class, joined by a
        guess; a call of a name more than one class declares, on a receiver of no known class, is counted under cause
        as a call the read cannot join."""
        if found is None:
            return
        called = len(steps) > 1 and steps[1].kind == "call"
        only = self._file.only_member_named(steps[0].text, called)
        if only is not None:
            found.members.append(only)
            found.guessed.append(only)
        elif value is None and called:
            self._unjoined.count(found.unresolved_calls, steps[0].text, cause)

    def _through_module(self, head: str, steps: list, found: SpanReach | None) -> "tuple[Typed | None, int, str]":
        """A class the file reaches through a module it imports, `prompt_log.LoggedFile(path)`: built when called, which
        runs its constructor, else the class itself."""
        if head in self._locals or head in _OWN_OBJECT:
            return None, 0, _ITSELF
        named = self._file.class_named(steps[0].text)
        if named is None:
            return None, 0, _ITSELF
        if len(steps) > 1 and steps[1].kind == "call":
            if found is not None:
                found.members.extend(self._index.constructors_of(named))
            return Typed(named), 2, self._creates
        return Typed(named), 1, _THE_CLASS

    def _typed_head(self, head: str, steps: list) -> "tuple[Typed | None, int, str]":
        """What a chain's first name is, the step its walk goes on from, and how the code reaches it: a call of a class
        builds one of it, a call of a function answers what the function returns."""
        called = bool(steps) and steps[0].kind == "call"
        if head in _BASE_OBJECT:
            base = next(iter(self._bases_of(self._owner)), None) if self._owner is not None else None
            return (Typed(base) if base is not None else None), (1 if called else 0), _ITSELF
        if called:
            return self._called_head(head, steps[0].text)
        if head in _OWN_OBJECT:
            return (Typed(self._owner) if self._owner is not None else None), 0, _ITSELF
        if head in self._locals:
            return self._locals[head], 0, self._reaches[head]
        if _is_class_name(head):
            named = self._file.class_named(head)
            if named is not None:
                return Typed(named), 0, _THE_CLASS
        return self._file.module_value(head), 0, A_MODULES_OBJECT

    def _called_head(self, head: str, arguments: str) -> "tuple[Typed | None, int, str]":
        """What a chain that opens with a call is: an object of the class it builds, or what the function answers."""
        if head in self._locals:
            return None, 1, _ITSELF
        if head == "cls":
            return (Typed(self._owner) if self._owner is not None else None), 1, _ITSELF
        built = self._file.class_named(head) if _is_class_name(head) else None
        if built is not None:
            return Typed(built), 1, self._creates
        function = self._file.function_named(head)
        answer = self._answers.declared_function(self._file.relative, head) if function is None else self._answers.answer_of(function)
        return answer, 1, _reach_after(REACHED_THROUGH_ANOTHER_OBJECT, arguments)

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
            found = self._answers.held_in(owner, name)
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


def _names_a_type(code: str, start: int) -> bool:
    """Whether the bare name at start names a type rather than a value: a hint after a colon outside a mapping's
    braces, a return type, a part of a union, a generic's argument, the subject of a subscript (`list[Line]`), a cast,
    or a decorator."""
    before = code[:start].rstrip()
    if before.endswith(_TYPE_MARKS) or _AS_CAST.search(before):
        return True
    opener = _opening_before(code, start)
    if before.endswith(":"):
        return opener != "{"
    if before.endswith(("[", ",")) and opener is not None:
        subject = _SUBSCRIPTED.search(code[:code.rfind(opener, 0, start)].rstrip())
        return opener == "<" or (opener == "[" and subject is not None and subject.group(0) not in _VALUE_WORDS)
    return False


def _opening_before(code: str, start: int) -> "str | None":
    """The bracket open around start: the nearest one before it that no bracket between them closes."""
    depth = 0
    for position in range(start - 1, -1, -1):
        character = code[position]
        if character in ")]}":
            depth += 1
        elif character in "([{<":
            if depth == 0:
                return character
            if character != "<":
                depth -= 1
    return None


def _reach_after(reach: str, arguments: str | None) -> str:
    """How the code reaches what one step of a chain answers, from how it reached the object the step is taken on and
    the arguments of the step's call (none for a member read): an object a call with a string, name, path, or key
    answers, or one a class named outright answers, is looked up by name; a field of the object itself is held; any
    other is reached through another object."""
    if (arguments is not None and _LOOKUP_ARGUMENTS.search(arguments)) or reach == _THE_CLASS:
        return LOOKED_UP_BY_NAME
    if reach == _ITSELF and arguments is None:
        return HELD_AS_A_FIELD
    return REACHED_THROUGH_ANOTHER_OBJECT


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
