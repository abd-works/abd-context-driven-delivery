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
from cdd_guidance.practices.source_code import STAR, ClassReference, imported_files

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
_HEAD = re.compile(r"(?:(?<![\w.$)\]])|(?<=\.\.\.))[A-Za-z_$][\w$]*")
_IDENTIFIER = re.compile(r"[A-Za-z_$][\w$]*")
# What may open an expression without being part of its value: `await order.paid()`, `new Order()`.
_PREFIX = re.compile(r"(?:await|new|yield)\s+")
# Python's built-ins that answer a new collection of the same elements as the one they are handed.
_COPIES = re.compile(r"\b(?:list|tuple|sorted|reversed|set|frozenset|iter)\(")
# A function called by its name alone, and a brace language's call of its base constructor.
_BARE_CALL = re.compile(r"(?:(?<![\w.$])|(?<=\.\.\.))([A-Za-z_$][\w$]*)\s*\(")
# A script's element that renders a component, `<Boundary>` or `<Banner />`: a capitalised name after an opening angle
# bracket no name comes before, which a generic's `Array<Line>` has.
_ELEMENT = re.compile(r"(?<![\w$.])<([A-Z][\w$]*)(?=[\s/>])")
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
_LOOP = re.compile(r"\bfor\s*\(?\s*(?:const\s+|let\s+|var\s+)?(\(?[A-Za-z_$][\w$]*(?:\s*,\s*[A-Za-z_$][\w$]*)*\)?)\s+(?:in|of)\s+")
# The loop of a comprehension, after the expression each item is: `[driver.licence for driver in drivers]`.
_COMPREHENSION = re.compile(r"\s*(?:async\s+)?for\s+([A-Za-z_]\w*)\s+in\s+")
# What a mapping answers that a loop walks: its values, or its items, each a key and a value.
_MAPPING_VIEWS = frozenset({"items", "values"})
# A mapping's calls that answer one of its values by its key.
_MAPPING_LOOKUPS = frozenset({"get", "pop", "setdefault"})
# A Python block's object and its local: `with Order() as order`, and each further `, Cart() as cart` of one with.
_WITH = re.compile(r"(?<![\w$.])with\s+")
# A check that a local is an object of one class, `isinstance(found, Brakes)` or `found instanceof Brakes`.
_CHECKED = re.compile(
    r"\bisinstance\(\s*([A-Za-z_]\w*)\s*,\s*([A-Za-z_][\w.]*)\s*\)|([A-Za-z_$][\w$]*)\s+instanceof\s+([A-Za-z_$][\w$.]*)"
)
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
# A base a class names with type arguments, `Shelving["Spanner"]`; the bases that list a generic class's parameters;
# and a name a hint writes as a whole word.
_SPECIALISED = re.compile(r"^\s*([\w.]+)\s*\[(.*)\]\s*$")
_GENERIC_BASES = frozenset({"Generic", "Protocol"})
_WORD_OF = r"(?<![\w.]){name}(?![\w])"
# An expression an f-string interpolates: what its braces hold, a doubled brace aside.
_INTERPOLATED = re.compile(r"(?<!\{)\{([^{}]+)\}(?!\})")
# The parts of a union that say a value may be missing, which say nothing of its class.
_NO_VALUE = frozenset({"None", "null", "undefined"})
_OWN_OBJECT = frozenset({"self", "this", "cls"})
# The names that always mean the object itself; `cls` means its class only where no parameter's hint says otherwise.
_THE_OBJECT = frozenset({"self", "this"})
_BASE_OBJECT = frozenset({"super"})
_SCRIPT_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".jsx", ".mjs"})
# Where an expression a local is assigned, a loop walks, or a `return` answers, has ended: the end of its statement, of a
# tuple part, or of a loop's or block's header.
_ENDS = frozenset("\n;,:)]}")
# What may follow an expression and still leave it the value, when it holds: `opener = Chat.load(id) if id else None`,
# `chat = found or Chat()`, `const chat = found ?? fresh()`.
_ALTERNATIVE = re.compile(r"(?:if|or|for|async\s+for)\b|\?\?|\|\|")
# One field of a script's object literal, written alone or with its value after a colon.
_OBJECT_FIELD = re.compile(r"\s*([A-Za-z_$][\w$]*)\s*(:\s*)?")
# The comma before a tuple's next part, when a part follows it on its line.
_NEXT_PART = re.compile(r"[ \t]*,[ \t]*(?=[A-Za-z_$])")
_QUOTES = frozenset("'\"`")
# The space before a list's first item, and the comma, on any line, before its next.
_SPACE = re.compile(r"\s*")
_NEXT_ITEM = re.compile(r"\s*,\s*(?=[^\s\])])")
# The comma after a field of a script's object literal.
_NEXT_FIELD = re.compile(r"\s*,")
# A call's arguments that look an object up rather than hand it one: a string, or a name, path, key, or slug.
_LOOKUP_ARGUMENTS = re.compile(r"[\"'`]|(?i:\b\w*(?:name|path|key|slug)s?\b)")

# How the code of one class reaches another class it depends on, which its dependency edge keeps (``reached``): the
# class is built on each call, or in the constructor or a field's initializer; found through a class operation, a call
# with a name, path, or key, or a mapping's item; held in a field of its own; handed in as a parameter; reached through
# another object it calls or reads; a module's own object, such as a registry a module assigns; named as a value, as an
# isinstance check, a list, a call it is handed to, or a metaclass names the class itself; or created with the class, as
# a class attribute's initializer builds it once for every object of the class.
CREATED_ON_EACH_CALL = "created on each call"
CREATED_IN_THE_CONSTRUCTOR = "created in the constructor"
LOOKED_UP_BY_NAME = "looked up by name"
HELD_AS_A_FIELD = "held as a field"
HANDED_IN_AS_A_PARAMETER = "handed in as a parameter"
REACHED_THROUGH_ANOTHER_OBJECT = "reached through another object"
A_MODULES_OBJECT = "a module's object"
NAMED_AS_A_VALUE = "named as a value"
CREATED_WITH_THE_CLASS = "created with the class"
# A receiver that is the object itself or the class it extends, which no dependency reaches, and a class named outright,
# whose operation a call reaches through the class.
_ITSELF = ""
_THE_CLASS = "the class itself"
_CREATED = frozenset({CREATED_ON_EACH_CALL, CREATED_IN_THE_CONSTRUCTOR, CREATED_WITH_THE_CLASS})
# The facts a dependency edge keeps: how the class reaches the class it depends on, and the members it reaches it
# through. The fact an invokes edge keeps when no call it records was joined by its receiver's class, only by a guess.
REACHED_FACT = "reached"
THROUGH_FACT = "through"
JOINED_FACT = "joined"
JOINED_BY_A_GUESS = "by a guess: one class in reach declares the name"
# Where a class named as a value is a type, or an element's tag, instead: after these, or as the subject of a generic or
# a subscript.
_TYPE_MARKS = ("->", "|", "&", "<", "</", "@")
_AS_CAST = re.compile(r"\bas$")
# The name a subscript is taken on, `list` in `list[Line]`, and the words after which a bracket opens a list instead.
_SUBSCRIPTED = re.compile(r"[A-Za-z_$][\w$.]*$")
_VALUE_WORDS = frozenset({*keyword.kwlist, "return", "yield", "await", "in", "of", "typeof", "new", "case", "throw"})
# A string written on one line, which a span's bare class names are not read inside.
_STRING = re.compile(r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`")


class CodeSpan(NamedTuple):
    """A span of code to read for what it calls: its text, the class it is written in (none outside a class, such as
    a spec's block), the type hint of each parameter it takes, by the parameter's name, the code that runs before
    it, such as a spec's setups, read only for the locals it makes, and how an object it builds is reached (``creates``):
    on each call, in the constructor, as a constructor and a field's initializer build it, or with the class, as a class
    attribute's initializer does. A parameter with no hint is a name whose class the code does not say."""

    text: str
    owner: "Node | None" = None
    typed: dict[str, str] = {}
    before: str = ""
    creates: str = CREATED_ON_EACH_CALL

    @staticmethod
    def code_of(text: str) -> str:
        """The code of text: without the calls the source view marks, doc strings, or comments."""
        return _NOT_CODE.sub(_code_kept, _CALL_MARKER.sub("", text))


class Typed(NamedTuple):
    """What a value of the code is, as far as the code says: one object of a class (``of``), a tuple of values by
    position (``items``), a collection whose every element is one value (``each``), a mapping whose every value is one
    (``by_key``), or a script's object of named fields, each with its value (``fields``)."""

    of: "Node | None" = None
    items: tuple = ()
    each: "Typed | None" = None
    by_key: "Typed | None" = None
    fields: tuple = ()
    # For an item a collection holds: the classes the items are, when the code wrote them (``kinds``), else whether an
    # item may be any class that extends ``of`` (``family``), so a call on it reaches the operation each overrides.
    kinds: tuple = ()
    family: bool = False
    # For `super()`: the classes after the calling class in the method resolution order of each class that is or
    # extends it; a call reaches the first class in each order that declares the member, and no override of it.
    orders: tuple = ()
    # For an object of a generic class a hint specialises, `Shelving[Wrench]`: the type arguments the hint passes, as
    # written, and the file that writes them, which names their classes.
    arguments: tuple = ()
    written_in: str = ""

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


class _HintTypes:
    """What a type hint one file's code writes says a value is, as that file names classes: one object of a class, a
    tuple, a collection or mapping of one, or a script's object of fields. The file makes it once and keeps it
    (``CodeFile.hints``)."""

    def __init__(self, file: "CodeFile", index: "CodeIndex") -> None:
        self._file = file
        self._index = index
        self._answers = index.answers
        # The interfaces and object types being read now, which a field of one may name again.
        self._reading: set[str] = set()

    def typed(self, hint: str | None, owner: "Node | None" = None) -> "Typed | None":
        """What a type hint written in this file says a value is: one object of the class it names, an optional one
        included; a tuple of such by position; a collection or mapping of one; one of a union of classes; a script's
        object of fields; owner itself for `Self`. None for a built-in or a name this file does not reach."""
        written = (hint or "").strip().strip("\"'").strip()
        if written.startswith("{") and written.endswith("}"):
            return self._typed_object(written[1:-1], owner)
        optional = _OPTIONAL.match(written)
        if optional:
            written = next(group for group in optional.groups() if group).strip().strip("\"'").strip()
        if written in _SELF_TYPES:
            return Typed(owner) if owner is not None else None
        return self._shaped(written, owner)

    def _shaped(self, written: str, owner: "Node | None") -> "Typed | None":
        """What a hint that is no longer optional says: a union, a generic, an array, or one name."""
        parts = _top_level_parts(written, "|")
        if len(parts) > 1:
            return self._union(parts, owner)
        generic = _GENERIC.match(written)
        if generic:
            return self._typed_generic(generic.group(1).rsplit(".", 1)[-1], _top_level_parts(generic.group(2)), owner)
        array = _ARRAY.match(written)
        if array:
            each = self.typed(array.group(1), owner)
            return Typed(each=each) if each is not None else None
        return self._named(written, owner) if _NAME.match(written) else None

    def _named(self, name: str, owner: "Node | None") -> "Typed | None":
        """What one name a hint writes says: an object of the class this file means by it, else, in a script, of the
        interface or object type it declares or imports."""
        found = self._file.class_named(name)
        if found is not None:
            return Typed(found)
        return self._declared_object(name, owner) if self._file.is_script else None

    def _declared_object(self, name: str, owner: "Node | None") -> "Typed | None":
        """What a script's interface or object type alias the file declares or imports says each field is:
        `interface LoadState { status: LoadStatus }`. A type read while it is being read answers nothing."""
        if name in self._reading:
            return None
        declared = re.compile(rf"(?<![\w$])(?:interface\s+{re.escape(name)}\b[^{{]*|type\s+{re.escape(name)}\s*=\s*)\{{")
        texts = [self._file.relative, *sorted(self._file.imported_files_of(name))]
        for relative in texts:
            text = self._answers.text_of(relative)
            match = declared.search(text)
            closing = _closing(text, match.end() - 1) if match is not None else None
            if closing is not None:
                self._reading.add(name)
                try:
                    return self._typed_object(text[match.end():closing], owner)
                finally:
                    self._reading.discard(name)
        return None

    def _union(self, parts: list[str], owner: "Node | None") -> "Typed | None":
        """What a union of classes says a value is, `Brakes | Lights`: one of them, typed as the nearest class they all
        are or extend; none when a part names no class of the code."""
        typed = [self.typed(part, owner) for part in parts if part not in _NO_VALUE]
        classes = [value.of for value in typed if value is not None and value.of is not None]
        if not classes or len(classes) != len(typed):
            return None
        return Typed(self._index.common_base(classes), kinds=tuple(dict.fromkeys(classes)))

    def _typed_object(self, written: str, owner: "Node | None") -> "Typed | None":
        """What a script's object type says each of its fields is: `{ page: FilesPage; stop: () => void }`."""
        fields = []
        for part in _top_level_parts(written, ",;\n"):
            name, _colon, hint = part.partition(":")
            name = name.strip().removeprefix("readonly ").rstrip("?").strip()
            if _NAME.match(name):
                fields.append((name, self.typed(hint, owner)))
        return Typed(fields=tuple(fields)) if any(value is not None for _name, value in fields) else None

    def _typed_generic(self, generic: str, parts: list[str], owner: "Node | None") -> "Typed | None":
        """What a generic hint says: the one value a wrapper holds, a tuple's values, or a collection's or a mapping's."""
        if not parts:
            return None
        if generic in _WRAPPERS:
            return self.typed(parts[0], owner)
        if generic in _TUPLES:
            return self._typed_tuple(parts, owner)
        if generic not in _SEQUENCES and generic not in _MAPPINGS:
            return self._specialised(generic, parts)
        held = self.typed(parts[0] if generic in _SEQUENCES else parts[-1], owner)
        if held is None:
            return None
        return Typed(each=held) if generic in _SEQUENCES else Typed(by_key=held)

    def _specialised(self, generic: str, parts: list[str]) -> "Typed | None":
        """An object of a generic class of the code a hint passes type arguments, `Shelving[Wrench]`, carrying them."""
        named = self._file.class_named(generic)
        arguments = tuple(part.strip().strip("\"'").strip() for part in parts)
        return Typed(named, arguments=arguments, written_in=self._file.relative) if named is not None else None

    def _typed_tuple(self, parts: list[str], owner: "Node | None") -> "Typed | None":
        """What a tuple hint says: many of one value (`tuple[Line, ...]`), else each value by its position."""
        if len(parts) == 2 and parts[1].strip() == "...":
            each = self.typed(parts[0], owner)
            return Typed(each=each) if each is not None else None
        items = tuple(self.typed(part, owner) for part in parts)
        return Typed(items=items) if any(item is not None for item in items) else None


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
        # What the type hints this file writes say a value is.
        self.hints = _HintTypes(self, index)

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

    def function_of_module(self, module: str, name: str) -> "Node | None":
        """The function called name the module this file imports under the name module declares, `polish.shine` after
        `from garage import polish`; none when the file imports no such module or it declares no such function."""
        files = {
            path for reference in self._imports if module in reference.names()
            for path in [*imported_files(f"{reference.source}/{module}"), *reference.files()]
        }
        found = [member for member in self._index.members_named(name) if member.get_fact("owner") == MODULE_FUNCTION_HOLDER and member.source.file in files]
        return found[0] if len(found) == 1 else None

    def module_value(self, name: str) -> "Typed | None":
        """What a module variable this file names is: the one this file assigns, else the one a file its imports name
        assigns, as that file's assignment types it (`PRACTICES = PracticeCatalogue()`); none when no such file assigns
        name at the start of a line."""
        for relative in [self.relative, *sorted(self.imported_files_of(name))]:
            found = self._index.answers.module_value(relative, name)
            if found is not None:
                return found
        return None

    def module_cause(self, name: str) -> "str | None":
        """Why a module variable this file names has no class, as the file that assigns it says (``module_value``); none
        when no such file assigns name."""
        for relative in [self.relative, *sorted(self.imported_files_of(name))]:
            found = self._index.answers.module_cause(relative, name)
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
        return self._read_as(self._only_in_reach(members))

    def _only_in_reach(self, members: "list[Node]") -> "Node | None":
        """The one of members a class of this file declares, else a class of the files its imports name, else, in a
        graph of the whole working copy, a class of its own folder in its language; none where two classes do."""
        own = self._in_files(members, {self.relative})
        if own:
            return self._only(own)
        imported = self._in_files(members, self.imported_files_of())
        if imported or not self._whole:
            return self._only(imported)
        return self._only([member for member in members if self._beside(member.source.file)])

    def _in_files(self, members: "list[Node]", files: set[str]) -> "list[Node]":
        """The members of members declared in one of files."""
        return [member for member in members if member.source.file in files]

    def getter_of(self, prop: "Node") -> "Node | None":
        """The operation that reads prop, when its class declares it as a getter: the member that runs."""
        return next(
            (member for member in self._index.members_named(prop.name)
             if member.type == "Operation" and member.get_fact("owner") == prop.get_fact("owner") and member.source.file == prop.source.file),
            None,
        )

    def _read_as(self, member: "Node | None") -> "Node | None":
        """A property a getter reads is reached through the getter, the member that runs."""
        if member is None or member.type != "Property":
            return member
        return self.getter_of(member) or member

    def imported_files_of(self, name: str | None = None) -> set[str]:
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
        # A star import brings every name its module declares, so a class declared there is passed on too.
        imported = self.imported_files_of(name) | self.imported_files_of(STAR)
        found = next((node for node in candidates if node.source.file in imported), None)
        if found is not None:
            return found
        for path in sorted(imported):
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
        # Why a field or a module variable the code assigns has no class, when what it assigns has none, by its key.
        self._field_causes: dict[tuple[str, str], str] = {}
        self._module_causes: dict[tuple[str, str], str] = {}

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
        typed = self._index.file(holder.source.file).hints.typed(str(hint), holder) if hint else None
        return typed if typed is not None else self.field_of(holder, name)

    def module_value(self, relative: str, name: str) -> "Typed | None":
        """What the module variable name the file at relative assigns at the start of a line is."""
        return self._once(self._modules, (relative, name), lambda: self._module_value(relative, name))

    def field_cause(self, holder: "Node", name: str) -> "str | None":
        """Why the field name of holder has no class, as what its constructor or initializer assigns it says; none when
        nothing assigns it."""
        self.field_of(holder, name)
        return self._field_causes.get((holder.node_id, name))

    def module_cause(self, relative: str, name: str) -> "str | None":
        """Why the module variable name the file at relative assigns has no class, as what it assigns says; none when
        the file assigns no such variable."""
        self.module_value(relative, name)
        return self._module_causes.get((relative, name))

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
            return file.hints.typed(written, owner)
        declared = self.declared_function(operation.source.file, operation.name) if owner is None and file.is_script else None
        return declared if declared is not None else self._returned(file, operation)

    def _returned(self, file: CodeFile, operation: "Node") -> "Typed | None":
        """What every `return` operation writes that the code types answers, when they agree."""
        span = self._index.span_of(operation)
        calls = _SpanCalls(file, self._index, span).expressions
        answers = [calls.typed_at(match.end())[0] for match in _RETURN.finditer(span.text)]
        typed = [answer for answer in answers if answer is not None]
        return typed[0] if typed and all(answer == typed[0] for answer in typed) else None

    def _field_of(self, holder: "Node", name: str) -> "Typed | None":
        """What the field's initializer assigns it, else what an operation of holder assigns it."""
        initialized = self._initialized(holder, name)
        return initialized if initialized is not None else self._assigned_in_operations(holder, name)

    def _initialized(self, holder: "Node", name: str) -> "Typed | None":
        """What the field holder declares with an initial value starts as: `readonly fileBar = new FileBar(this)`."""
        file = self._index.file(holder.source.file)
        for declared in self._index.members_named(name):
            if declared.type != "Property" or declared.get_fact("is_property") or declared.get_fact("owner") != holder.name or declared.source.file != holder.source.file:
                continue
            code = CodeSpan.code_of(declared.source.text)
            initialized = re.search(_INITIALIZED.format(name=re.escape(name)), code)
            if initialized is not None:
                read = _SpanCalls(file, self._index, CodeSpan(code, holder)).expressions.typed_at(initialized.end())
                self._field_causes.setdefault((holder.node_id, name), read.cause)
                if read.value is not None:
                    return read.value
        return None

    def _assigned_in_operations(self, holder: "Node", name: str) -> "Typed | None":
        """What an operation of holder assigns the field: the type the assignment writes, else what it assigns."""
        assigned = re.compile(rf"(?<![\w$.])(?:self|this)\.{re.escape(name)}[ \t]*(?::[ \t]*([^=\n]+?))?[ \t]*=(?![=>])[ \t]*")
        for assigning in self._assigning_operations(holder):
            span = self._index.span_of(assigning)
            file = self._index.file(assigning.source.file)
            for match in assigned.finditer(span.text):
                found = file.hints.typed(match.group(1), holder) if match.group(1) else None
                read = _SpanCalls(file, self._index, span).expressions.typed_at(match.end()) if found is None else None
                if read is not None:
                    self._field_causes.setdefault((holder.node_id, name), read.cause)
                    found = read.value
                if found is not None:
                    return found
        return None

    def _assigning_operations(self, holder: "Node") -> "list[Node]":
        """The operations of holder that may assign its fields: its constructor first, then each other operation it
        declares, such as a helper the constructor calls (`self._start_declaration()`)."""
        constructors = self._index.constructors_of(holder)
        return [*constructors, *(operation for operation in self._index.operations_of(holder) if operation not in constructors)]

    def _module_value(self, relative: str, name: str) -> "Typed | None":
        text = CodeSpan.code_of(self.text_of(relative))
        match = re.search(_MODULE_ASSIGNMENT.format(name=re.escape(name)), text)
        file = self._index.file(relative)
        if match is None:
            declared = re.search(_MODULE_DECLARATION.format(name=re.escape(name)), text) if file.is_script else None
            return file.hints.typed(declared.group(1)) if declared is not None else None
        if match.group(1):
            self._module_causes[(relative, name)] = file.receiver_causes.of_hint(match.group(1))
            return file.hints.typed(match.group(1))
        read = _SpanCalls(file, self._index, CodeSpan("")).expressions.typed_at(match.end(), text)
        self._module_causes[(relative, name)] = read.cause
        return read.value

    def _declared_function(self, relative: str, name: str) -> "Typed | None":
        text = self.text_of(relative)
        file = self._index.file(relative)
        found = _script_function(text, name) if file.is_script else _python_function(text, name)
        if found is None:
            return None
        hint, body = found
        if hint:
            return file.hints.typed(hint)
        code = CodeSpan.code_of(body)
        calls = _SpanCalls(file, self._index, CodeSpan(code)).expressions
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
    """An expression that starts with a name and follows it through members, calls, and items, where it ends, and
    where it starts."""

    head: str
    steps: list
    end: int
    start: int = 0


class _TypeArguments:
    """What each type parameter of a generic base stands for in a class that specialises it: `Item` is `Spanner` in
    `class ToolShelf(Shelving["Spanner"])`, so an operation `Shelving` declares answering `Iterator[Item]` answers
    spanners on a tool shelf. The class members of a span make one and keep it."""

    def __init__(self, members: "_ClassMembers", index: "CodeIndex") -> None:
        self._members = members
        self._index = index

    def answer_on(self, value: Typed, operation: "Node") -> "Typed | None":
        """What operation answers called on value: its return type with each type parameter value binds put in; else
        what it answers wherever it is declared."""
        bound = self.typed_in(value, str(operation.get_fact("return_type") or ""))
        return bound if bound is not None else self._index.answers.answer_of(operation)

    def typed_in(self, value: Typed, written: str) -> "Typed | None":
        """What a hint a member of value's class writes says, with each type parameter value binds put in, typed in the
        file that writes the binding; none when the hint names no parameter value binds."""
        bound = self._bound(value) if written else {}
        used = [parameter for parameter in bound if _names_word(written, parameter)]
        for parameter in used:
            written = re.sub(_WORD_OF.format(name=re.escape(parameter)), bound[parameter][0], written)
        return self._index.file(bound[used[0]][1]).hints.typed(written, value.of) if used else None

    def _bound(self, value: Typed) -> "dict[str, tuple[str, str]]":
        """Each type parameter value binds, with the hint it stands for and the file that writes that hint: those the
        hint that typed value passes its class, then those its class's lineage passes, nearest class first; a parameter
        bound to a parameter a nearer class binds takes that binding."""
        own = zip(self._parameters(value.of), value.arguments) if value.arguments else []
        bound: dict[str, tuple[str, str]] = {parameter: (argument, value.written_in) for parameter, argument in own}
        for declared in self._members.lineage_of(value.of):
            file = self._index.file(declared.source.file)
            for base, arguments in _specialised_bases(declared):
                generic = file.class_named(base)
                for parameter, argument in zip(self._parameters(generic) if generic is not None else [], arguments):
                    bound.setdefault(parameter, bound.get(argument, (argument, declared.source.file)))
        return bound

    def _parameters(self, generic: "Node") -> "list[str]":
        """The type parameters a generic class declares: those its `Generic[...]` or `Protocol[...]` base lists, else
        each name its specialised bases pass that names no class."""
        specialised = _specialised_bases(generic)
        listed = next((arguments for base, arguments in specialised if base in _GENERIC_BASES), None)
        if listed is not None:
            return listed
        file = self._index.file(generic.source.file)
        return [argument for _base, arguments in specialised for argument in arguments if file.class_named(argument) is None]


class _ClassMembers:
    """What the classes of the code declare and answer, as one file's code reaches them: the member a class declares or
    inherits, the classes it extends, what a member answers or holds, what an item of a collection is, and the operation
    each class an item may be overrides. A span makes one for the file it is written in and keeps it."""

    def __init__(self, file: CodeFile, index: "CodeIndex") -> None:
        self._file = file
        self._index = index
        self._answers = index.answers
        # What the type parameters of a generic base stand for in the class that specialises it.
        self._arguments = _TypeArguments(self, index)

    def member_of(self, holder: "Node", name: str, seen: frozenset = frozenset()) -> "Node | None":
        """The member called name that holder declares, an operation before a property, else the one a class it
        extends declares."""
        declared = next(
            (member for member in self._index.members_named(name)
             if member.get_fact("owner") == holder.name and member.source.file == holder.source.file and not member.get_fact("is_setter")),
            None,
        )
        if declared is not None or holder.node_id in seen:
            return declared
        inherited = (self.member_of(base, name, seen | {holder.node_id}) for base in self.bases_of(holder))
        return next((member for member in inherited if member is not None), None)

    def bases_of(self, holder: "Node") -> "list[Node]":
        """The classes holder extends that the code reads, as the file holder is written in names them."""
        file = self._index.file(holder.source.file) if holder.source.file != self._file.relative else self._file
        named = (file.class_named(str(base).split("[")[0].split("<")[0].strip()) for base in holder.get_fact("bases") or [])
        return [base for base in named if base is not None and base is not holder]

    def lineage_of(self, holder: "Node") -> "list[Node]":
        """holder, then each class it extends, nearest first, at any depth."""
        line = [holder]
        for current in line:
            line.extend(base for base in self.bases_of(current) if base not in line)
        return line

    def following(self, declared: "Node") -> "tuple[tuple[Node, ...], ...]":
        """The classes after declared in the method resolution order of declared and of each class extending it, as
        Python's C3 linearisation orders them; the classes `super()` in declared may reach."""
        found: list[tuple] = []
        for extending in [declared, *self._index.subclasses_of(declared)]:
            order = self._resolution_order(extending)
            after = tuple(order[order.index(declared) + 1:]) if declared in order else ()
            if after and after not in found:
                found.append(after)
        return tuple(found)

    def _resolution_order(self, declared: "Node", seen: frozenset = frozenset()) -> "list[Node]":
        """declared, then the classes it extends, in C3 order: each base's own order merged, keeping every class
        before the classes it extends and the bases in the order the class names them."""
        bases = [base for base in self.bases_of(declared) if base.node_id not in seen]
        orders = [self._resolution_order(base, seen | {declared.node_id}) for base in bases] + [bases]
        return [declared, *_merged(orders)]

    def base_of(self, owner: "Node | None") -> "Node | None":
        """The first class owner extends, which `super` names; none outside a class."""
        return next(iter(self.bases_of(owner)), None) if owner is not None else None

    def answer_of(self, value: Typed, name: str, member: "Node | None", called: bool) -> "Typed | None":
        """What the member called name of value's class answers: a call's return, else the member's or field's value,
        each with the type parameters value binds put in. A call of a field answers what the field holds, as a field
        holding a class, `formats_type: type[PracticeFormats]`, builds an object of it."""
        if called and member is not None and member.type == "Operation":
            return self._arguments.answer_on(value, member)
        return self._value_of(value, name, member)

    def _value_of(self, value: Typed, name: str, member: "Node | None") -> "Typed | None":
        """What the member or field called name of value's class holds, read without a call: its type, what its getter
        answers, or what the field holds in that class or a class it extends."""
        if member is not None and member.get_fact("value_type"):
            return self._hinted(value, member)
        getter = self._file.getter_of(member) if member is not None else None
        if getter is not None:
            return self._arguments.answer_on(value, getter)
        if member is not None and member.type == "Operation":
            return None
        held = (self._answers.held_in(owner, name) for owner in self.lineage_of(value.of))
        return next((found for found in held if found is not None), None)

    def _hinted(self, value: Typed, member: "Node") -> "Typed | None":
        """What member's type hint says it holds, with each type parameter value binds put in, else as the class that
        declares it writes the hint."""
        written = str(member.get_fact("value_type"))
        bound = self._arguments.typed_in(value, written)
        if bound is not None:
            return bound
        declaring = self._declaring(value.of, member)
        return self._index.file(declaring.source.file).hints.typed(written, declaring)

    def held_by_extending(self, holder: "Node", name: str) -> "Typed | None":
        """What the field called name holds in the first class extending holder that holds it: a mixin reads a field
        the class mixing it in keeps."""
        held = (self._answers.held_in(extending, name) for extending in self._index.subclasses_of(holder))
        return next((found for found in held if found is not None), None)

    def as_receiver(self, answer: "Typed | None", holder: "Node", member: "Node | None") -> "Typed | None":
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

    def item_of(self, value: Typed, written: str) -> "Typed | None":
        """What an item value takes is: a tuple's part by its position, a collection's element, a mapping's value, or
        what its class's `__getitem__` answers."""
        if value.items and _INTEGER.match(written.strip()):
            position = int(written.strip())
            return value.items[position] if -len(value.items) <= position < len(value.items) else None
        if (value.each or value.by_key) is not None:
            return _one_of_many(value.each or value.by_key)
        if value.of is not None:
            getitem = self.member_of(value.of, "__getitem__")
            return self._arguments.answer_on(value, getitem) if getitem is not None else None
        return None

    def element_of(self, value: "Typed | None") -> "Typed | None":
        """What each element a loop over value takes is: a collection's element, or what its class's `__iter__` yields."""
        if value is None:
            return None
        if value.each is not None:
            return _one_of_many(value.each)
        if value.of is not None:
            iterate = self.member_of(value.of, "__iter__")
            walked = self._arguments.answer_on(value, iterate) if iterate is not None else None
            return walked.each if walked is not None else None
        return None

    def overrides(self, value: Typed, name: str) -> "list[Node]":
        """The operation called name each class value may be declares: each class the code wrote a collection's items
        as, else each class extending the one a collection's type names, or each class satisfying a protocol."""
        if value.orders:
            return self._first_declared(value.orders, name)
        if not value.kinds and value.of is None:
            return []
        classes = value.kinds or tuple(self._index.subclasses_of(value.of))
        return [override for override in (self.member_of(each, name) for each in classes) if override is not None]


    def _first_declared(self, orders: tuple, name: str) -> "list[Node]":
        """The operation called name that the first class declaring it in each order declares."""
        found: list[Node] = []
        for order in orders:
            # A holder already seen answers only the member it declares itself.
            declared = (self.member_of(each, name, frozenset({each.node_id})) for each in order)
            member = next((each for each in declared if each is not None), None)
            if member is not None and member not in found:
                found.append(member)
        return found


class _Locals:
    """What each local a span names is, by its name, from its first assignment the code types, and how the code reaches
    it. A local the read cannot type is kept with why on the span's calls the read cannot join."""

    def __init__(self, unjoined: UnjoinedCalls) -> None:
        self._unjoined = unjoined
        self._types: dict[str, Typed] = {}
        self._reaches: dict[str, str] = {}
        # What a comprehension's own local is within its brackets, by where they open and close in the span's code.
        self._scoped: list[tuple[int, int, str, _Read]] = []

    def __contains__(self, name: str) -> bool:
        return name in self._types

    def scope(self, name: str, read: _Read, start: int, end: int) -> None:
        """Keep what read says the local name is between start and end of the span's code, as a comprehension's own
        local is within its brackets."""
        if read.value is not None:
            self._scoped.append((start, end, name, read))

    def at(self, name: str, position: int) -> "_Read | None":
        """What the local name is at position of the span's code, when a comprehension there has its own; the
        innermost one."""
        found = [read for start, end, scoped, read in self._scoped if scoped == name and start <= position <= end]
        return found[-1] if found else None

    def keep(self, name: str, read: _Read) -> None:
        """Keep what read says the local name is, the first time the code types it."""
        if name in _THE_OBJECT or name in self._types:
            return
        if read.value is None:
            self._unjoined.keep_local(name, read.cause)
            return
        self._types[name] = read.value
        self._reaches[name] = read.reach

    def narrow(self, name: str, read: _Read) -> None:
        """Keep what read says the local name is in place of what it was, as a check that it is of a class narrows it."""
        if name not in _THE_OBJECT:
            self._types[name] = read.value
            self._reaches[name] = read.reach

    def typed(self, name: str) -> "Typed | None":
        return self._types.get(name)

    def reach(self, name: str) -> str:
        return self._reaches[name]


class _Expressions:
    """What each expression a span's code writes is, where it ends, and how the code reaches it: one chain, a tuple, a
    list, a script's object or cast; and what each local the code declares, assigns, loops over, or opens a block on
    is. The span makes it once and keeps it, and it asks the span to walk each chain."""

    def __init__(self, span: "_SpanCalls", members: _ClassMembers, local: _Locals) -> None:
        self._span = span
        self._file = span.file
        self._index = span.index
        self._owner = span.owner
        self._members = members
        self._locals = local

    def typed_at(self, start: int, code: str | None = None) -> _Read:
        """What the expression that starts at start in code (the span's own by default) is, where it ends, and how the
        code reaches it: one chain, a tuple of chains separated by commas, or a script's chain cast `as` a class. None
        when it is anything else, such as a sum or a condition."""
        code = self._span.code if code is None else code
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

    def name_locals_in(self, code: str) -> None:
        """Type each local code declares, assigns, loops over, or opens a block on, in the order the code writes them:
        by its hint, else by what the expression assigned to it is, with how the code reaches it."""
        readers = (
            (_DECLARED_LOCAL, lambda match: [(match.group(1), self._hinted(match.group(2), _Read(None, 0)))]),
            (_ASSIGNMENT, lambda match: self._assigned(code, match)),
            (_DESTRUCTURED, lambda match: self._destructured(code, match)),
            (_LOOP, lambda match: self._looped(code, match)),
            (_WITH, lambda match: self._opened(code, match.end())),
            (_CHECKED, self._checked),
        )
        # Each is typed after the ones written before it, which its expression may use.
        found = sorted(((match.start(), read, match) for pattern, read in readers for match in pattern.finditer(code)), key=lambda item: item[0])
        for _position, read, match in found:
            for name, value in read(match):
                self._locals.keep(name, value)

    def _typed_chain_at(self, code: str, start: int) -> _Read:
        """What the one chain at start is, when the statement or tuple part ends with it."""
        read = self._chain_value(code, start)
        rest = code[read.end:].lstrip(" \t")
        if rest and rest[0] not in _ENDS and _ALTERNATIVE.match(rest) is None:
            # An expression that opens with a literal, `[1, 2]` or `"".join(parts)`, is a built-in object, and so is an
            # operator on an object from outside the code read, `root / "hooks.json"`.
            outside = read.end == start or (read.value is None and read.cause == ON_OUTSIDE_OBJECTS)
            return _Read(None, read.end, cause=read.cause if outside else OTHERWISE)
        return read

    def _chain_value(self, code: str, start: int) -> _Read:
        """What the chain at start is, after an `await` or `new`, and cast `as` a class in a script, and where it ends."""
        prefix = _PREFIX.match(code, start)
        position = prefix.end() if prefix else start
        built = self._built_at(code, position)
        if built is not None:
            return built
        chain = _chain_at(code, position)
        if chain is None:
            return _Read(None, start, cause=ON_OUTSIDE_OBJECTS if ReceiverCauses.is_literal(code, position) else OTHERWISE)
        found, reach, cause = self._span.walk(chain, None)
        cast = _CAST.match(code, chain.end) if self._file.is_script else None
        if cast is not None:
            return _Read(self._file.hints.typed(cast.group(1), self._owner), cast.end(), reach, self._file.receiver_causes.of_hint(cast.group(1)))
        return _Read(found, chain.end, reach, cause)

    def _built_at(self, code: str, position: int) -> "_Read | None":
        """What a value the code builds at position is: a script's object, a list or a tuple, or a copy of a collection
        `list(...)` makes; none for any other expression."""
        if code[position:position + 1] == "{" and self._file.is_script:
            return self._object_at(code, position)
        if code[position:position + 1] in ("(", "["):
            return self._collection_at(code, position)
        copies = _COPIES.match(code, position) if not self._file.is_script else None
        return self._copied_at(code, copies.end()) if copies is not None else None

    def _copied_at(self, code: str, start: int) -> _Read:
        """What `list(...)`, `sorted(...)` and the other built-ins that copy a collection answer: a collection of the
        elements of the one they are handed, `list(self._parts.items())`."""
        closing = _closing(code, start - 1)
        copied = self._typed_chain_at(code, _SPACE.match(code, start).end())
        element = self._members.element_of(copied.value)
        end = closing + 1 if closing is not None else copied.end
        return _Read(Typed(each=element) if element is not None else None, end, copied.reach, copied.cause)

    def _collection_at(self, code: str, opening: int) -> _Read:
        """What a list or a tuple the code writes at opening holds, `(Brakes(), Lights())`: each item one of the classes
        its items are, typed as the nearest class they all are or extend; a parenthesised expression with no comma is
        that expression. A list whose items the read cannot all type is a built-in object."""
        closing = _closing(code, opening)
        if closing is None:
            return _Read(None, opening, cause=ON_OUTSIDE_OBJECTS)
        first = _SPACE.match(code, opening + 1).end()
        items = self._items_at(code, first, closing)
        comprehension = _COMPREHENSION.match(code, items[0].end) if items else None
        if comprehension is not None:
            return self._comprehended(code, first, comprehension, closing)
        if code[opening] == "(" and len(items) == 1 and _NEXT_ITEM.match(code, items[0].end) is None:
            return _Read(items[0].value, closing + 1, items[0].reach, items[0].cause)
        return self._of_classes(items, closing)

    def _of_classes(self, items: "list[_Read]", closing: int) -> _Read:
        """A list whose every item is an object of a class of the code: each item one of those classes, typed as the
        nearest class they all are or extend; any other list is a built-in object."""
        classes = [read.value.of for read in items if read.value is not None and read.value.of is not None]
        if not classes or len(classes) != len(items):
            return _Read(None, closing + 1, cause=ON_OUTSIDE_OBJECTS)
        each = Typed(self._index.common_base(classes), kinds=tuple(dict.fromkeys(classes)))
        return _Read(Typed(each=each), closing + 1, items[0].reach)

    def _items_at(self, code: str, position: int, closing: int) -> "list[_Read]":
        """Each item a list or a tuple the code writes holds, from position up to its closing bracket."""
        items: list[_Read] = []
        while position < closing:
            read = self._typed_chain_at(code, position)
            items.append(read)
            following = _NEXT_ITEM.match(code, read.end)
            if following is None or read.end == position:
                break
            position = following.end()
        return items

    def _comprehended(self, code: str, start: int, comprehension: re.Match, closing: int) -> _Read:
        """What a comprehension builds, `[driver.licence for driver in drivers]`: each item is what the expression
        before its `for` is, once the loop's local is typed by what the loop walks; within the comprehension's brackets
        its local is that, whatever an earlier one of the same name was."""
        walked = self._element_read(self._typed_chain_at(code, comprehension.end()))
        self._locals.keep(comprehension.group(1), walked)
        if code is self._span.code:
            self._locals.scope(comprehension.group(1), walked, start, closing)
        item = self._typed_chain_at(code, start)
        if item.value is None:
            return _Read(None, closing + 1, item.reach, item.cause)
        return _Read(Typed(each=item.value), closing + 1, item.reach)

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
                value, end = self._locals.typed(named.group(1)), named.end()
            fields.append((named.group(1), value))
            following = _NEXT_FIELD.match(code, end)
            if following is None:
                break
            position = following.end()
        found = Typed(fields=tuple(fields)) if any(value is not None for _name, value in fields) else None
        return _Read(found, closing + 1)

    def _hinted(self, hint: str, read: _Read) -> _Read:
        """What a value a type hint types is, reached as read says, with why it has no class when the hint names none."""
        return _Read(self._file.hints.typed(hint, self._owner), read.end, read.reach, self._file.receiver_causes.of_hint(hint))

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

    def _checked(self, match: re.Match) -> "list[tuple[str, _Read]]":
        """Narrow a local a check names to the one class the check names, as the code that runs once the check holds
        sees it: a local the code typed no other way, or typed as a class the named one extends. It keeps no new local."""
        name, written = (match.group(1), match.group(2)) if match.group(1) else (match.group(3), match.group(4))
        named = self._file.class_named(written.split(".")[-1])
        if named is None:
            return []
        held = self._locals.typed(name)
        if held is None or (held.of is not None and held.of in self._members.lineage_of(named)):
            self._locals.narrow(name, _Read(Typed(named), match.end(), self._locals.reach(name) if held else REACHED_THROUGH_ANOTHER_OBJECT))
        return []

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

    def _looped(self, code: str, match: re.Match) -> "list[tuple[str, _Read]]":
        """Each local a loop takes: the element of what it walks, or, for a loop that takes two names or more
        (`for key, kind in kinds.items()`), each part of that element by its position."""
        read = self._element_read(self._typed_chain_at(code, match.end()))
        names = [name.strip() for name in match.group(1).strip("()").split(",")]
        if len(names) == 1:
            self._scope_comprehension(code, match.start(), names[0], read)
            return [(names[0], read)]
        items = read.value.items if read.value is not None else ()
        return [(name, _Read(items[position] if position < len(items) else None, read.end, read.reach, read.cause)) for position, name in enumerate(names)]

    def _scope_comprehension(self, code: str, start: int, name: str, read: _Read) -> None:
        """Keep what a comprehension's loop takes as its local within the comprehension's brackets, when the loop at
        start is a comprehension's, inside a bracket of the span's own code."""
        opening = _opening_at(code, start) if code is self._span.code else None
        closing = _closing(code, opening) if opening is not None and code[opening] in "([{" else None
        if closing is not None:
            self._locals.scope(name, read, opening, closing)

    def _element_read(self, read: _Read) -> _Read:
        """Each element a loop over what read is takes, reached as the collection is."""
        return _Read(self._members.element_of(read.value), read.end, read.reach, read.cause)


class _Heads:
    """What the first name of a chain a span's code writes is, the step its walk goes on from, and how the code reaches
    it: the object itself or the class it extends, a local, a class named outright, a module's object, a class built by
    a call, or what a function answers. The span makes it once and keeps it."""

    def __init__(self, span: "_SpanCalls") -> None:
        self._span = span
        self._file = span.file
        self._owner = span.owner
        self._members = span.members
        self._locals = span.locals

    def typed(self, head: str, steps: list, found: SpanReach | None, position: int = -1) -> "tuple[Typed | None, int, str]":
        """What head is, the step the walk goes on from, and how the code reaches it; a class or a function a module the
        file imports declares, `prompt_log.LoggedFile(path)` or `name_facts.opening_of(text)`, when head is that module."""
        scoped = self._locals.at(head, position)
        if scoped is not None:
            return scoped.value, 0, scoped.reach
        value, at, reach = self._typed(head, steps)
        if value is None and at == 0 and steps and steps[0].kind == "member" and head not in self._locals and head not in _OWN_OBJECT:
            return self._function_reached(head, steps, found) or self._through_module(head, steps, found)
        return value, at, reach

    def _function_reached(self, head: str, steps: list, found: SpanReach | None) -> "tuple[Typed | None, int, str] | None":
        """A module function the chain opens with and reaches a member of, `foldAt.bind(null, editor)`: the function is
        used, and what its member answers is not read; none when head names no such function."""
        function = self._file.function_named(head) if not self._span.unjoined.names_a_local(head) else None
        if function is None:
            return None
        if found is not None:
            found.members.append(function)
        return None, len(steps), _ITSELF

    def _typed(self, head: str, steps: list) -> "tuple[Typed | None, int, str]":
        called = bool(steps) and steps[0].kind == "call"
        if head in _BASE_OBJECT:
            return self._based(), (1 if called else 0), _ITSELF
        if called:
            return self._called(head, steps[0].text)
        if head in self._locals:
            return self._locals.typed(head), 0, self._locals.reach(head)
        if head in _OWN_OBJECT:
            # The object itself may be of any class that extends its own, whose override a call or a read on it reaches.
            return (Typed(self._owner, family=True) if self._owner is not None else None), 0, _ITSELF
        return self._named(head)

    def _based(self) -> "Typed | None":
        """What `super()` is in a class: the class that follows it in the method resolution order of each class that
        is or extends it, so a mixin's `super()` reaches the class each class mixing it in puts after it."""
        if self._owner is None:
            return None
        orders = self._members.following(self._owner)
        return Typed(orders[0][0], orders=orders) if orders else None

    def _named(self, head: str) -> "tuple[Typed | None, int, str]":
        """What a name that is no local is: a class named outright, else a module's object."""
        named = self._file.class_named(head) if _is_class_name(head) else None
        if named is not None:
            return Typed(named), 0, _THE_CLASS
        return self._file.module_value(head), 0, A_MODULES_OBJECT

    def _called(self, head: str, arguments: str) -> "tuple[Typed | None, int, str]":
        """What a chain that opens with a call is: an object of the class it builds, or what the function answers."""
        if head in self._locals:
            # A local that holds a class builds an object of it when called.
            return self._locals.typed(head), 1, self._locals.reach(head)
        if head == "cls":
            return (Typed(self._owner) if self._owner is not None else None), 1, _ITSELF
        built = self._file.class_named(head) if _is_class_name(head) else None
        if built is not None:
            return Typed(built), 1, self._span.creates
        function = self._file.function_named(head)
        answers = self._span.index.answers
        answer = answers.declared_function(self._file.relative, head) if function is None else answers.answer_of(function)
        return answer, 1, _reach_after(REACHED_THROUGH_ANOTHER_OBJECT, arguments)

    def _through_module(self, head: str, steps: list, found: SpanReach | None) -> "tuple[Typed | None, int, str]":
        """A class the file reaches through a module it imports: built when called, which runs its constructor, else
        the class itself; or a function that module declares, called or read and passed on."""
        named = self._file.class_named(steps[0].text) if _is_class_name(steps[0].text) else None
        if named is None:
            return self._module_function(head, steps, found)
        if len(steps) > 1 and steps[1].kind == "call":
            if found is not None:
                found.members.extend(self._span.index.constructors_of(named))
            return Typed(named), 2, self._span.creates
        return Typed(named), 1, _THE_CLASS

    def _module_function(self, head: str, steps: list, found: SpanReach | None) -> "tuple[Typed | None, int, str]":
        """The function the module head names declares, `polish.shine()`: joined whether it is called or read and passed
        on, and what it answers when called."""
        function = self._file.function_of_module(head, steps[0].text)
        if function is None:
            return None, 0, _ITSELF
        if found is not None:
            found.members.append(function)
        if len(steps) > 1 and steps[1].kind == "call":
            return self._span.index.answers.answer_of(function), 2, _reach_after(REACHED_THROUGH_ANOTHER_OBJECT, steps[1].text)
        return None, 1, _ITSELF


class _ChainWalk:
    """One walk along one chain of a span's code: what each part of it is and how the code reaches it, from its first
    name through each member, call, and item, adding to found, when given, each member it calls or reads, each class it
    reaches, and each call it cannot join. The span makes one for each chain it reads."""

    def __init__(self, span: "_SpanCalls", chain: _Chain, found: SpanReach | None) -> None:
        self._span = span
        self._members = span.members
        self._unjoined = span.unjoined
        self._head = chain.head
        self._steps = chain.steps
        self._found = found
        self._value, self._at, self._reach = span.heads.typed(chain.head, chain.steps, found, chain.start)
        called = bool(self._steps) and self._steps[0].kind == "call"
        self._cause = self._unjoined.of_head(chain.head, called) if self._value is None else OTHERWISE

    def run(self) -> "tuple[Typed | None, str, str]":
        """What the chain is, how the code reaches it, and, when the read cannot tell its class, why."""
        if self._guessed():
            guessed = self._span.guess(self._steps, self._value, self._found, self._cause)
            if not self._go_on_from(guessed):
                return None, self._reach, self._cause
            return self._walk_guessed()
        value = self._value
        if self._found is not None and value is not None and value.of is not None and self._reach in _CREATED:
            self._found.reach_class(value.of, self._reach)
        return self._walk()

    def _walk(self) -> "tuple[Typed | None, str, str]":
        """Take each step left; what the chain is at its end, how the code reaches it, and why its class is unknown."""
        while self._at < len(self._steps):
            if not self._take(self._steps[self._at]):
                return None, self._reach, self._cause
        return self._value, self._reach, self._cause

    def _walk_guessed(self) -> "tuple[Typed | None, str, str]":
        """Take each step left after a guessed first member: each member reached is joined by that guess too, and no
        class is kept as reached, since the code never says which class the chain runs through."""
        found = self._found
        if found is None:
            return self._walk()
        members, classes = len(found.members), len(found.classes)
        walked = self._walk()
        found.guessed.extend(found.members[members:])
        del found.classes[classes:]
        return walked

    def _guessed(self) -> bool:
        """Whether the chain opens with a local of no known class, or of a class that neither declares nor inherits the
        member it names, such as one a decorator gives its members: it reaches the one member of that name the file's
        reach declares. A chain of three or more parts on a local of a known class goes on through that class."""
        steps, value = self._steps, self._value
        opens = self._at == 0 and _is_local_name(self._head) and bool(steps) and steps[0].kind == "member"
        if not opens:
            return False
        if value is None and self._goes_on_past_a_guess():
            return True
        return not (len(steps) > 1 and steps[1].kind == "member") and (value is None or self._lacks_member(value, steps[0].text))

    def _goes_on_past_a_guess(self) -> bool:
        """Whether a chain of no known class goes on past its guessed first member: not when its first name is an
        object from outside the code read, such as a path, which no class of the code is."""
        return self._cause != ON_OUTSIDE_OBJECTS

    def _go_on_from(self, guessed: "Node | None") -> bool:
        """Go on along a chain of three or more parts from the member its first name was guessed to reach, as what
        that member answers or holds, `fixture.board.column("Backlog").cards`; whether any step is left to take."""
        steps = self._steps
        holder = self._span.index.class_declaring(guessed) if guessed is not None else None
        if holder is None or not self._goes_on_past_a_guess():
            return False
        name, calls = steps[0].text, len(steps) > 1 and steps[1].kind == "call"
        self._at = 2 if calls else 1
        if self._at >= len(steps):
            return False
        answer = self._members.answer_of(Typed(holder), name, guessed, calls)
        if answer is None:
            self._cause = self._unjoined.of_member([holder, *self._members.bases_of(holder)], name, guessed, calls)
        self._value = self._members.as_receiver(answer, holder, guessed)
        self._reach = _reach_after(self._reach, steps[1].text if calls else None)
        return True

    def _lacks_member(self, value: Typed, name: str) -> bool:
        """Whether value is of one class that neither declares nor inherits the member called name; a value that may
        be any of several classes is not, since each of them is asked for it."""
        return not (value.kinds or value.family) and value.of is not None and self._members.member_of(value.of, name) is None

    def _take(self, step: _Step) -> bool:
        """Take one step along the chain; whether the walk goes on."""
        value = self._value
        calls = self._at + 1 < len(self._steps) and self._steps[self._at + 1].kind == "call"
        if value is None:
            self._count_unjoined(step, calls)
            return False
        if self._took_part(value, step, calls):
            return True
        if step.kind == "call" and value.of is not None and not value.is_many:
            # A call of a value of one class builds it, as calling the class a call answers, `practice_class(name)()`.
            self._value = Typed(value.of)
            self._at += 1
            return True
        if step.kind == "call" or value.of is None:
            self._end_on(value, step, calls)
            return False
        self._member_step(value, step.text, calls)
        return True

    def _took_from_mapping(self, held: Typed, name: str, calls: bool) -> bool:
        """Go on with what a mapping's member name gives, when it gives its values: its values or items, or one value
        `get` looks up by its key; whether it did."""
        if name in _MAPPING_VIEWS:
            self._take_view(held, name, calls)
            return True
        if name not in _MAPPING_LOOKUPS or not calls:
            return False
        self._reach, self._value = LOOKED_UP_BY_NAME, held
        self._at += 2
        return True

    def _take_view(self, held: Typed, view: str, calls: bool) -> None:
        """Go on with a mapping's values, or its items, each a key and a value: what a loop over it takes."""
        value = _one_of_many(held)
        self._value = Typed(each=Typed(items=(None, value)) if view == "items" else value)
        self._at += 2 if calls else 1

    def _count_unjoined(self, step: _Step, calls: bool) -> None:
        """Count a call on a receiver the read could not type as one it cannot join."""
        if self._found is not None and step.kind == "member" and calls:
            self._unjoined.count(self._found.unresolved_calls, step.text, self._cause)

    def _took_part(self, value: Typed, step: _Step, calls: bool) -> bool:
        """Go on with a part of value, when step takes one: an item value takes, a mapping's looked up by its key, a
        field of a script's object, or a mapping's values or items; whether it did."""
        if step.kind == "member" and value.by_key is not None and self._took_from_mapping(value.by_key, step.text, calls):
            return True
        if step.kind == "item":
            self._reach = LOOKED_UP_BY_NAME if value.by_key is not None else self._reach
            self._value = self._members.item_of(value, step.text)
        elif step.kind == "member" and value.fields:
            self._value = dict(value.fields).get(step.text)
        else:
            return False
        self._at += 1
        return True

    def _end_on(self, value: Typed, step: _Step, calls: bool) -> None:
        """End the walk on a value of no class: a collection, a call of a call's answer, or an item of a list of classes
        that share no base, whose member each of those classes declares is still reached."""
        if self._found is not None and step.kind == "member" and value.kinds:
            self._span.reach_member(self._found, value, step.text, None, self._reach, calls)
        self._cause = ON_OUTSIDE_OBJECTS if value.is_many else OTHERWISE

    def _member_step(self, value: Typed, name: str, calls: bool) -> None:
        """Reach the member called name on value's class, and go on with what it answers."""
        member = self._members.member_of(value.of, name)
        if self._found is not None:
            self._span.reach_member(self._found, value, name, member, self._reach, calls)
        answer = self._members.answer_of(value, name, member, calls)
        if answer is None and value.family and member is None and not calls:
            answer = self._members.held_by_extending(value.of, name)
        if answer is None:
            self._cause = self._unjoined.of_member([value.of, *self._members.bases_of(value.of)], name, member, calls)
        self._value = self._members.as_receiver(answer, value.of, member)
        self._reach = _reach_after(self._reach, self._steps[self._at + 1].text if calls else None)
        self._at += 2 if calls else 1


class _SpanCalls:
    """One span of a file's code read for what it calls and reads: it knows the class it is written in, holds what each
    local it names is (*_Locals*), how its expressions read (*_Expressions*), what the first name of each chain is
    (*_Heads*), and what the classes it reaches declare (*_ClassMembers*), and walks each chain of its code
    (*_ChainWalk*) to the members it reaches."""

    def __init__(self, file: CodeFile, index: "CodeIndex", span: CodeSpan) -> None:
        self.file = file
        self.index = index
        self.code = span.text
        self.owner = span.owner
        # How the span reaches an object it builds: while its object is built, or on each call.
        self.creates = span.creates
        # The calls the span makes that the read cannot join, with why each name it writes has no class.
        self.unjoined = UnjoinedCalls(file, index)
        self.members = _ClassMembers(file, index)
        self.locals = _Locals(self.unjoined)
        self.expressions = _Expressions(self, self.members, self.locals)
        self.heads = _Heads(self)
        for name, hint in span.typed.items():
            self.locals.keep(name, _Read(file.hints.typed(hint, self.owner), 0, HANDED_IN_AS_A_PARAMETER, file.receiver_causes.of_hint(hint)))
        for code in (span.before, self.code):
            self.expressions.name_locals_in(code)

    def reach(self) -> SpanReach:
        """The members its code calls and the properties it reads, in the order the code names them, the classes it
        reaches and how, and the calls it could not join."""
        found = SpanReach()
        self._reach_through_receivers(found)
        found.members.extend(self._called_by_name(found))
        return found

    def walk(self, chain: _Chain, found: SpanReach | None) -> "tuple[Typed | None, str, str]":
        """What chain is, how the code reaches it, and, when the read cannot tell its class, why; adding to found, when
        given, what it reaches on the way."""
        return _ChainWalk(self, chain, found).run()

    def reach_member(self, found: SpanReach, value: Typed, name: str, member: "Node | None", reach: str, called: bool) -> None:
        """Keep the member called name a step reaches on value's class, the operation each class an item of a
        collection may be overrides, and value's class when the code reaches another object."""
        reached = [member] if member is not None else []
        found.members.extend(each for each in [*reached, *self.members.overrides(value, name)] if self._is_reached(each, called))
        if reach != _ITSELF and value.of is not None:
            found.reach_class(value.of, reach)

    def _is_reached(self, member: "Node", called: bool) -> bool:
        """Whether a step reaches member: a call reaches an operation, and a read a property or the getter that reads it."""
        return called or member.type == "Property" or self.file.getter_of(member) is member

    def guess(self, steps: list, value: "Typed | None", found: SpanReach | None, cause: str) -> "Node | None":
        """The one member of the step's name the file's reach declares, for a receiver of no known class, joined by a
        guess, and answered so a longer chain goes on from it; a call of a name more than one class declares, on a
        receiver of no known class, is counted under cause as a call the read cannot join."""
        called = len(steps) > 1 and steps[1].kind == "call"
        only = self.file.only_member_named(steps[0].text, called)
        if found is None:
            return only
        if only is not None:
            found.members.append(only)
            found.guessed.append(only)
        elif value is None and called:
            self.unjoined.count(found.unresolved_calls, steps[0].text, cause)
        return only

    def _reach_through_receivers(self, found: SpanReach) -> None:
        """Each member a chain reaches: every member it names after its first name is a member of what the part before
        it is, and a call's answer or an item it takes is what the next member is found on. A member with a call after
        it may be an operation; any other is a property read. A name of no known class followed by one member reaches
        the member the file's reach declares once. A class the code names alone, as a value, is reached that way."""
        # The code with each string blanked, where a bare name is read only outside a string.
        masked = _STRING.sub(_blanked, self.code)
        for head in _HEAD.finditer(self.code):
            chain = _chain_at(self.code, head.start())
            if chain is not None and chain.steps:
                self.walk(chain, found)
            elif chain is not None and masked[head.start()] != " ":
                self._name_value(found, chain.head, masked, head.start())

    def _name_value(self, found: SpanReach, head: str, masked: str, start: int) -> None:
        """Keep the class or the module function a bare name names, when it names it as a value and not as a type: a
        class an isinstance check or a list names, a function handed to a call, `ThrottledReporter(_report_line)`."""
        if head in self.locals or _names_a_type(masked, start):
            return
        named = self.file.class_named(head) if _is_class_name(head) else None
        if named is not None and named is not self.owner:
            found.reach_class(named, NAMED_AS_A_VALUE)
        function = self.file.function_named(head) if named is None else None
        if function is not None:
            found.members.append(function)

    def _called_by_name(self, found: SpanReach) -> "Iterator[Node]":
        """Each module function its code calls by name alone, the constructor of each class it builds by its name, and
        the constructor of the class it extends for a brace language's `super(...)`. A script's element names a
        component it renders, `<Boundary>`: a function component is called, and a class component is built on each
        render and its `render` called."""
        if self.file.is_script:
            yield from self._rendered(found)
        for name in dict.fromkeys(_BARE_CALL.findall(self.code)):
            if name == "super":
                base = self.members.base_of(self.owner)
                constructor = self.members.member_of(base, "constructor") if base is not None else None
                yield from [constructor] if constructor is not None else []
                continue
            function = self.file.function_named(name)
            if function is not None:
                yield function
            elif _is_class_name(name):
                yield from self.file.constructors_of(name)

    def _rendered(self, found: SpanReach) -> "Iterator[Node]":
        """The component each element of a script's code renders: a function component, or a class component's
        `render`, the class built on each render."""
        for name in dict.fromkeys(_ELEMENT.findall(self.code)):
            component = self.file.class_named(name)
            if component is not None:
                found.reach_class(component, self.creates)
            rendered = self.members.member_of(component, "render") if component is not None else self.file.function_named(name)
            if rendered is not None:
                yield rendered


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
    return _Chain(head.group(0), steps, position, start)


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


def _code_kept(found: re.Match) -> str:
    """What of a string or a comment is code: a string on one line, kept whole; each expression a triple-quoted
    f-string interpolates (`self.title` in a page's template); nothing of a doc string or a comment."""
    if found.group(1):
        return found.group(1)
    text = found.group(0)
    if text[:3] in ('"' * 3, "'" * 3) and found.string[found.start() - 1:found.start()].lower() == "f":
        return " ".join(_INTERPOLATED.findall(text))
    return ""


def _blanked(written: re.Match) -> str:
    """A string the code writes, blanked so no name in it is read as code, but for each `${...}` a script's template
    string holds, which is code."""
    text = written.group(0)
    if not text.startswith("`"):
        return " " * len(text)
    kept, depth = [], 0
    for position, character in enumerate(text):
        opens = character == "{" and text[position - 1:position] == "$"
        depth += 1 if opens or (character == "{" and depth) else 0
        depth -= 1 if character == "}" and depth else 0
        kept.append(character if depth and not opens else " ")
    return "".join(kept)


def _merged(orders: "list[list[Node]]") -> "list[Node]":
    """C3's merge: take, again and again, the first head of an order that is in no other order's tail; when none is,
    as for bases the code orders inconsistently, take the first head left."""
    orders = [list(order) for order in orders if order]
    merged: list[Node] = []
    while orders:
        head = next((order[0] for order in orders if not any(order[0] in other[1:] for other in orders)), orders[0][0])
        merged.append(head)
        orders = [[node for node in order if node is not head] for order in orders]
        orders = [order for order in orders if order]
    return merged


def _specialised_bases(declared: "Node") -> "list[tuple[str, list[str]]]":
    """Each base declared names with type arguments, `Shelving["Spanner"]`, as the base's name and each argument."""
    found = []
    for base in declared.get_fact("bases") or []:
        written = _SPECIALISED.match(str(base))
        if written is not None:
            arguments = [part.strip().strip("\"'").strip() for part in _top_level_parts(written.group(2))]
            found.append((written.group(1).rsplit(".", 1)[-1], arguments))
    return found


def _names_word(written: str, name: str) -> bool:
    """Whether a hint names name as a whole word."""
    return re.search(_WORD_OF.format(name=re.escape(name)), written) is not None


def _one_of_many(held: Typed) -> Typed:
    """An item a collection holds: one of the classes the code wrote its items as, else any class extending the class
    its type names."""
    return held if held.kinds or held.of is None else held._replace(family=True)


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
    opening = _opening_at(code, start)
    return code[opening] if opening is not None else None


def _opening_at(code: str, start: int) -> "int | None":
    """Where the bracket open around start opens: the nearest one before it that no bracket between them closes."""
    depth = 0
    for position in range(start - 1, -1, -1):
        character = code[position]
        if character in ")]}":
            depth += 1
        elif character in "([{<":
            if depth == 0:
                return position
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
