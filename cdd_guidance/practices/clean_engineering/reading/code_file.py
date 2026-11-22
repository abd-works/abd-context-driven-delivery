"""One file of the code read, as the code written in it names things, and the members a span of that code calls.

*CodeIndex.file* answers a *CodeFile*, the one seam every practice asks to resolve a name its code writes: the class or
module function the file declares, imports, or finds beside itself in its own folder and language, and each member a
span of its code calls and reads (*CodeSpan*: the code, the class it is written in, and the type of each local it knows).
Clean Engineering asks it for each operation's and property's own body, and BDD for each observation and the setups
around it, so an `invokes` edge means the same member whichever practice draws it. A name is joined to the node the
file's own declarations and imports name, never to every node of that name: two classes may both have a `total`, and a
call on an order runs only the order's."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterator, NamedTuple

from cdd_guidance.practices.clean_engineering.model import CONSTRUCTOR_NAMES, MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.source_code import ClassReference

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import CodeIndex

# The marker the source view puts after a line for each call on it, `/* call:show */`, which is no code.
_CALL_MARKER = re.compile(r"\s*/\* call:[^*]*\*/")
# What is no code: a doc string, a block comment, and a line comment.
_NOT_CODE = re.compile(r'(?s)""".*?"""|\'\'\'.*?\'\'\'|/\*.*?\*/|(?m:(?:#|//).*$)')
# A member reached through a receiver: `self.order.payment.authorised`, `super().__init__`, `Book.is_in_stock`.
_CHAIN = re.compile(r"(?<![\w.$)\]])((?:super\(\)|[A-Za-z_$][\w$]*)(?:\.[A-Za-z_$][\w$]*)+)(\s*\()?")
# A function called by its name alone, and a brace language's call of its base constructor.
_BARE_CALL = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)\s*\(")
# A local the body binds to a new object (`order = Order(`, `const order = new Order(`), and one it binds to each
# element of a collection (`for line in self.lines`, `for (const line of this.lines)`).
_BUILT_LOCAL = re.compile(r"\b([A-Za-z_$][\w$]*)[ \t]*(?::[ \t]*[\w.\[\]<>, |]+?)?[ \t]*=\s*(?:new\s+)?([A-Z][\w$]*)\s*\(")
# A local a script declares as one class: `let order: Order`.
_DECLARED_LOCAL = re.compile(r"\b(?:let|const|var)\s+([A-Za-z_$][\w$]*)\s*:\s*([A-Z][\w$]*)")
_LOOP_LOCAL = re.compile(r"\bfor\s*\(?\s*(?:const\s+|let\s+|var\s+)?([A-Za-z_$][\w$]*)\s+(?:in|of)\s+([A-Za-z_$][\w$.]*)")
# A collection's type, with the type of what it holds: `list[CartLine]`, `Array<CartLine>`, `CartLine[]`.
_COLLECTION = re.compile(r"^(?:[A-Za-z_][\w.]*\s*[\[<]\s*([A-Za-z_]\w*)\s*[\]>]|([A-Za-z_]\w*)\s*\[\])$")
_OPTIONAL = re.compile(r"^(?:Optional\[(.+)\]|(.+?)\s*\|\s*(?:None|null|undefined)|(?:None|null|undefined)\s*\|\s*(.+))$")
_NAME = re.compile(r"^[A-Za-z_]\w*$")
_OWN_OBJECT = frozenset({"self", "this", "cls"})
_BASE_OBJECT = frozenset({"super()", "super"})
_SCRIPT_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".jsx", ".mjs"})
# A local the body assigns: `lane = ...`, `const lane = ...`, `lane: Lane = ...`.
_ASSIGNED_LOCAL = re.compile(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*(?::[^=\n]+)?=(?!=)")
# A local the body assigns what a call answers: `line = cart.add(book)`, `const line = cart.add(book)`.
_CALL_LOCAL = re.compile(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*=\s*(?:await\s+)?((?:[A-Za-z_$][\w$]*)(?:\.[A-Za-z_$][\w$]*)+)\s*\(")


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
        return _NOT_CODE.sub("", _CALL_MARKER.sub("", text))


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
        if found is None:
            return []
        return [
            member for constructor in sorted(CONSTRUCTOR_NAMES) for member in self._index.members_named(constructor)
            if member.type == "Operation" and member.get_fact("owner") == found.name and member.source.file == found.source.file
        ]

    @property
    def imported_classes(self) -> "list[Node]":
        """The classes this file's imports name, in the order it imports them."""
        found = (self.class_named(name) for reference in self._imports for name in reference.names())
        return list(dict.fromkeys(node for node in found if node is not None and node.source.file != self.relative))

    def members_called_in(self, span: CodeSpan) -> "list[Node]":
        """The members span calls and the properties it reads, in the order its code names them, each once."""
        return list(dict.fromkeys(_SpanCalls(self, self._index, span).called()))

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
        imported = self._imported_files(name)
        found = next((node for node in candidates if node.source.file in imported), None)
        return found or self._in_same_package(candidates)

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


class _SpanCalls:
    """One span of a file's code read for what it calls and reads: it knows the class it is written in, the class of
    each local it names, and through them the class each receiver in it is."""

    def __init__(self, file: CodeFile, index: "CodeIndex", span: CodeSpan) -> None:
        self._file = file
        self._index = index
        self._code = span.text
        self._owner = span.owner
        # The class each local is, by its name; a local that is a collection is kept by what it holds once looped over.
        self._locals: dict[str, "Node"] = {}
        for name, hint in span.typed.items():
            self._keep_local(name, self._class_of_hint(hint, file.relative))
        for code in (span.before, self._code):
            self._name_locals_in(code)

    def _name_locals_in(self, code: str) -> None:
        """Type each local code builds or declares by its class, each it assigns a call's answer by what the called
        operation returns, and each loop's local by what the collection it walks holds."""
        for name, built in _DECLARED_LOCAL.findall(code) + _BUILT_LOCAL.findall(code):
            self._keep_local(name, self._file.class_named(built))
        for name, chain in _CALL_LOCAL.findall(code):
            self._keep_local(name, self._returned_by(chain.split(".")))
        for name, walked in _LOOP_LOCAL.findall(code):
            self._keep_local(name, self._held_by(walked.split(".")))

    def called(self) -> "list[Node]":
        """The members its code calls and the properties it reads, in the order the code names them."""
        return [*self._reached_through_receivers(), *self._called_by_name()]

    def _keep_local(self, name: str, found: "Node | None") -> None:
        if found is not None:
            self._locals.setdefault(name, found)

    def _reached_through_receivers(self) -> "Iterator[Node]":
        """Each member a dotted chain reaches: every part after the first is a member of the class the part before it
        is. A part with a call after it may be an operation; any other is a property read. A two-part chain whose head
        is a name of no known class reaches the member the file's reach declares once."""
        for chain in _CHAIN.finditer(self._code):
            parts = chain.group(1).split(".")
            holder = self._class_of_head(parts[0])
            if holder is None and len(parts) == 2 and _is_local_name(parts[0]):
                only = self._file.only_member_named(parts[1], bool(chain.group(2)))
                if only is not None:
                    yield only
            for position, name in enumerate(parts[1:], start=1):
                if holder is None:
                    break
                member = self._member_of(holder, name)
                last_and_called = position == len(parts) - 1 and bool(chain.group(2))
                if member is not None and (member.type == "Property" or last_and_called or self._file.getter_of(member) is member):
                    yield member
                holder = self._class_of_hint(self._hint_of(holder, name, member), holder.source.file)

    def _returned_by(self, parts: list[str]) -> "Node | None":
        """The class the operation a call's chain reaches returns, such as `CartLine` for `cart.add(book)`."""
        holder = self._class_of_head(parts[0])
        member = None
        for name in parts[1:]:
            if holder is None:
                return None
            member = self._member_of(holder, name)
            if member is None:
                return None
            hint = str(member.get_fact("return_type") or "") if name == parts[-1] else self._hint_of(holder, name, member)
            holder = self._class_of_hint(hint, holder.source.file)
        return holder

    def _called_by_name(self) -> "Iterator[Node]":
        """Each module function its code calls by name alone, the constructor of each class it builds by its name, and
        the constructor of the class it extends for a brace language's `super(...)`."""
        for name in dict.fromkeys(_BARE_CALL.findall(self._code)):
            if name == "super":
                base = self._class_of_head("super")
                constructor = self._member_of(base, "constructor") if base is not None else None
                if constructor is not None:
                    yield constructor
                continue
            function = self._file.function_named(name)
            if function is not None:
                yield function
            elif name[:1].isupper():
                yield from self._file.constructors_of(name)

    def _class_of_head(self, head: str) -> "Node | None":
        """The class the first part of a chain is: the span's own, the one it extends, a local's, or a class named
        outright."""
        if head in _OWN_OBJECT:
            return self._owner
        if head in _BASE_OBJECT:
            return next(iter(self._bases_of(self._owner)), None) if self._owner is not None else None
        if head in self._locals:
            return self._locals[head]
        return self._file.class_named(head) if head[:1].isupper() else None

    def _held_by(self, parts: list[str]) -> "Node | None":
        """The class a collection named by a chain holds, such as `CartLine` for `self.lines: list[CartLine]`."""
        holder = self._class_of_head(parts[0])
        for name in parts[1:-1]:
            if holder is None:
                return None
            holder = self._class_of_hint(self._hint_of(holder, name, self._member_of(holder, name)), holder.source.file)
        if holder is None or len(parts) < 2:
            return None
        collection = _COLLECTION.match((self._hint_of(holder, parts[-1], self._member_of(holder, parts[-1])) or "").strip())
        held = (collection.group(1) or collection.group(2)) if collection else ""
        return self._file_of(holder).class_named(held) if held else None

    def _hint_of(self, holder: "Node", name: str, member: "Node | None") -> str:
        """The type holder's member called name has: the member's own, else the type of the field holder keeps."""
        if member is not None and member.get_fact("value_type"):
            return str(member.get_fact("value_type"))
        return str((holder.get_fact("held_fields") or {}).get(name) or "")

    def _class_of_hint(self, hint: str | None, file: str) -> "Node | None":
        """The class a type hint names as one object, an optional one included, as the file the hint is written in
        names it; none for a collection or a built-in."""
        written = (hint or "").strip()
        optional = _OPTIONAL.match(written)
        if optional:
            written = next(group for group in optional.groups() if group).strip()
        return self._file_named(file).class_named(written) if _NAME.match(written) else None

    def _file_of(self, node: "Node") -> CodeFile:
        return self._file_named(node.source.file)

    def _file_named(self, relative: str) -> CodeFile:
        """The file of the span itself, which knows the imports it was given, else the index's file."""
        return self._file if relative == self._file.relative else self._index.file(relative)

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
        file = self._file_of(holder)
        named = (file.class_named(str(base).split("[")[0].split("<")[0].strip()) for base in holder.get_fact("bases") or [])
        return [base for base in named if base is not None and base is not holder]


def _is_local_name(head: str) -> bool:
    """Whether a chain's head is a variable's name: a lower-case name that is neither the object itself nor its base."""
    return head[:1].islower() and head not in _OWN_OBJECT and head not in _BASE_OBJECT


def _language_of(file: str) -> str:
    """The language family a file is written in, by its extension: every script extension is one family."""
    suffix = "." + file.rsplit(".", 1)[-1].lower()
    return "script" if suffix in _SCRIPT_SUFFIXES else suffix
