"""The edges one read of the code draws between the members and classes it added: each call and read to the member its
receiver names, each class to the class it extends, and each class a model document describes to the class in code
that implements it. A name is joined to the node the file's own declarations and imports name, never to every node of
that name: two classes may both have a `total`, and a call on an order runs only the order's."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterator

from harness.graph.schema_conformance import EXEMPT_FACT

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.model.code_read import DESCRIBED_FACT
from cdd_guidance.practices.clean_engineering.model.script_imports import ClassReference

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.model.graph_reading import GraphReading

_ABSTRACT_MARK = re.compile(r"@abstractmethod|^\s*(?:public\s+|protected\s+)?abstract\s", re.MULTILINE)
_DOCSTRING = re.compile(r'(?s)\A\s*(?:"""|\'\'\').*?(?:"""|\'\'\')')
# The marker the source view puts after a line for each call on it, `/* call:show */`, which is no code.
_CALL_MARKER = re.compile(r"\s*/\* call:[^*]*\*/")
_NO_BODY = {"", "...", "pass", "raise NotImplementedError", "raise NotImplementedError()"}
# What is no code: a doc string, a block comment, and a line comment.
_NOT_CODE = re.compile(r'(?s)""".*?"""|\'\'\'.*?\'\'\'|/\*.*?\*/|(?m:(?:#|//).*$)')
# A member reached through a receiver: `self.order.payment.authorised`, `super().__init__`, `Book.is_in_stock`.
_CHAIN = re.compile(r"(?<![\w.$)\]])((?:super\(\)|[A-Za-z_$][\w$]*)(?:\.[A-Za-z_$][\w$]*)+)(\s*\()?")
# A function called by its name alone, and a brace language's call of its base constructor.
_BARE_CALL = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)\s*\(")
# A local the body binds to a new object (`order = Order(`, `const order = new Order(`), and one it binds to each
# element of a collection (`for line in self.lines`, `for (const line of this.lines)`).
_BUILT_LOCAL = re.compile(r"\b([A-Za-z_$][\w$]*)\s*(?::\s*[\w.\[\]<>, |]+?)?\s*=\s*(?:new\s+)?([A-Z][\w$]*)\s*\(")
_LOOP_LOCAL = re.compile(r"\bfor\s*\(?\s*(?:const\s+|let\s+|var\s+)?([A-Za-z_$][\w$]*)\s+(?:in|of)\s+([A-Za-z_$][\w$.]*)")
# A collection's type, with the type of what it holds: `list[CartLine]`, `Array<CartLine>`, `CartLine[]`.
_COLLECTION = re.compile(r"^(?:[A-Za-z_][\w.]*\s*[\[<]\s*([A-Za-z_]\w*)\s*[\]>]|([A-Za-z_]\w*)\s*\[\])$")
_OPTIONAL = re.compile(r"^(?:Optional\[(.+)\]|(.+?)\s*\|\s*(?:None|null|undefined)|(?:None|null|undefined)\s*\|\s*(.+))$")
_NAME = re.compile(r"^[A-Za-z_]\w*$")
_OWN_OBJECT = frozenset({"self", "this", "cls"})
_SCRIPT_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".jsx", ".mjs"})
# A local the body assigns: `lane = ...`, `const lane = ...`, `lane: Lane = ...`.
_ASSIGNED_LOCAL = re.compile(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*(?::[^=\n]+)?=(?!=)")
_BASE_OBJECT = frozenset({"super()", "super"})


def _language_of(file: str) -> str:
    """The language family a file is written in, by its extension: every script extension is one family."""
    suffix = "." + file.rsplit(".", 1)[-1].lower()
    return "script" if suffix in _SCRIPT_SUFFIXES else suffix


class ClassesInReach:
    """The classes and module functions each file can name: those it declares, then those it imports, each from the
    file its import names. Made once for a read's linking, it reads what each folder kept of its files' imports."""

    def __init__(self, reading: "GraphReading") -> None:
        self._index = reading.code_index
        self._in_graph = reading.in_graph
        self._imports: dict[str, list[ClassReference]] | None = None

    def class_named(self, name: str, file: str) -> "Node | None":
        """The class file means by name: the one it declares, else the one it imports; none when it names neither."""
        return self._in_reach(self._index.classes_named(name), name, file)

    def function_named(self, name: str, file: str) -> "Node | None":
        """The module function file means by name: its own, else the one it imports."""
        functions = [member for member in self._index.members_named(name) if member.get_fact("owner") == MODULE_FUNCTION_HOLDER]
        return self._in_reach(functions, name, file)

    def _in_reach(self, candidates: "list[Node]", name: str, file: str) -> "Node | None":
        own = next((node for node in candidates if node.source.file == file), None)
        if own is not None or not candidates:
            return own
        imported = {path for reference in self._imports_of(file) if name in reference.names() for path in reference.files()}
        found = next((node for node in candidates if node.source.file in imported), None)
        return found or self._in_same_package(candidates, file)

    def _in_same_package(self, candidates: "list[Node]", file: str) -> "Node | None":
        """The class a file names with no import, when exactly one file of its own folder, in its own language,
        declares it: a Python or script file whose annotation names a class
        it does not import means the one beside it, never a class of that name in another package."""
        beside = [node for node in candidates if self._beside(node.source.file, file)]
        return beside[0] if len(beside) == 1 else None

    def only_member_named(self, name: str, file: str, whole: bool) -> "Node | None":
        """The operation called name a receiver of no known class can be, in a call file makes: the one that exactly
        one class of file itself declares; else, in a graph that holds the whole working copy (whole), the one that
        exactly one class in file's reach declares, its reach being the files its imports name and the files of its
        own folder in its own language. None when no class there declares it or more than one does, since the name
        alone does not say which is called. A load of some files alone looks no further than the file, so it links
        what a load of the whole working copy links inside that file."""
        operations = [member for member in self._index.members_named(name) if member.type == "Operation" and member.get_fact("owner") != MODULE_FUNCTION_HOLDER]
        own = self._only([member for member in operations if member.source.file == file])
        if own is not None or not whole or any(member.source.file == file for member in operations):
            return own
        imported = {path for reference in self._imports_of(file) for path in reference.files()}
        return self._only([member for member in operations if member.source.file in imported or self._beside(member.source.file, file)])

    def _only(self, members: "list[Node]") -> "Node | None":
        """The one of members, when one class alone declares them."""
        return members[0] if len({(member.source.file, member.get_fact("owner")) for member in members}) == 1 else None

    def _beside(self, other: str, file: str) -> bool:
        """Whether other is another file of file's folder written in file's language."""
        return other != file and other.rsplit("/", 1)[0] == file.rsplit("/", 1)[0] and _language_of(other) == _language_of(file)

    def _imports_of(self, file: str) -> list[ClassReference]:
        if self._imports is None:
            self._imports = {}
            for kind in ("Module", "Package"):
                for folder in self._in_graph.nodes(kind):
                    kept = folder.get_fact("imported_classes_by_file") if folder.has_fact("imported_classes_by_file") else {}
                    for relative, references in kept.items():
                        self._imports[relative] = [ClassReference(*reference) for reference in references]
        return self._imports.get(file, [])


class ClassLinks:
    """The edges between the classes the graph holds: each class to the class it extends (``baseClass``), and each
    class in code to the class a model document of its own module describes under its name (``implements``), so the
    design and the code that implements it are two nodes a reader walks between."""

    def __init__(self, reading: "GraphReading", reach: ClassesInReach) -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._reach = reach

    def link(self) -> None:
        classes = list(self._in_graph.nodes("OoadClass"))
        described = [node for node in classes if node.has_fact(DESCRIBED_FACT)]
        for node in classes:
            for base in node.get_fact("bases") or []:
                extended = self._reach.class_named(str(base).split("[")[0].split("<")[0].strip(), node.source.file)
                if extended is not None and extended is not node:
                    self._graph.edges.relate("baseClass", node, extended)
            if not node.has_fact(DESCRIBED_FACT):
                design = self._design_of(node, described)
                if design is not None:
                    self._graph.edges.relate("implements", node, design)

    def _design_of(self, coded: "Node", described: "list[Node]") -> "Node | None":
        """The class a model document describes under coded's name, from the nearest folder at or above coded's file
        whose document describes one; none when no document above it does."""
        found = [
            (len(folder), node) for node in described
            if node.name == coded.name
            for folder in [self._described_folder(node)]
            if not folder or coded.source.file.startswith(f"{folder}/")
        ]
        return max(found, key=lambda pair: pair[0])[1] if found else None

    def _described_folder(self, design: "Node") -> str:
        """The folder a model document describes, the one holding its `.context`; empty for the source root."""
        parts = design.source.file.split("/")[:-2]
        return "/".join(parts)


class CallLinks:
    """The ``invokes`` edges of the code read: each operation and property to the operations it calls and the
    properties it reads, each found on the class its receiver is: the caller's own class for `self` and `this`, the
    class it extends for `super()`, the type of a field, a parameter, or a local for any other object, and the class
    the file declares or imports for a class named outright. A call whose receiver's class the code does not say is
    joined to nothing."""

    def __init__(self, reading: "GraphReading", reach: ClassesInReach) -> None:
        self._reading = reading
        self._graph = reading.graph
        self._reach = reach

    def link(self) -> None:
        """Record an ``invokes`` edge from every member the graph holds to each member it calls."""
        in_graph = self._reading.in_graph
        for caller in [*in_graph.nodes("Operation"), *in_graph.nodes("Property")]:
            called = list(dict.fromkeys(CallerBody(self._reading, self._reach, caller).called()))
            for member in called:
                self._graph.edges.relate("invokes", caller, member)
            if not called and self._calls_nothing_by_design(caller):
                caller.set_fact(EXEMPT_FACT, ["invokes"])

    def _calls_nothing_by_design(self, caller: "Node") -> bool:
        """Whether caller is a member that has nothing to call: an abstract one, whose subclasses do the work, or one
        that takes nothing and answers a value, which is a property in all but name."""
        return self._is_abstract(caller) or not self._graph.edges.from_parent("hasParameter", caller)

    def _is_abstract(self, caller: "Node") -> bool:
        """An abstract member: marked so (`@abstractmethod`, `abstract`), or with no body but `...`, `pass`, or a raise of
        NotImplementedError under its signature and docstring."""
        text = caller.source.text if caller.source.file else ""
        if _ABSTRACT_MARK.search(text) or self._declared_without_body(text):
            return True
        return _DOCSTRING.sub("", self._python_body(text)).strip() in _NO_BODY

    def _declared_without_body(self, text: str) -> bool:
        """A C-family member with no body: its signature ends in `;` and no brace opens a body (an interface's method,
        `draw(scale: number): void;`)."""
        code = _CALL_MARKER.sub("", text).strip()
        return bool(code) and "{" not in code and code.endswith(";")

    def _python_body(self, text: str) -> str:
        """What follows a Python member's signature, the line that ends its `def` with a colon; none for other code."""
        lines = text.splitlines()
        if not any(line.lstrip().startswith(("def ", "async def ")) for line in lines[:4]):
            return ""
        end = next((index for index, line in enumerate(lines) if line.rstrip().endswith(":")), len(lines))
        return "\n".join(lines[end + 1:])


class CallerBody:
    """The source of one operation or property, read for what it calls and reads: it knows the class that declares it,
    the type of each parameter and local it names, and through them the class each receiver in its body is."""

    def __init__(self, reading: "GraphReading", reach: ClassesInReach, caller: "Node") -> None:
        self._index = reading.code_index
        self._graph = reading.graph
        self._reach = reach
        self._caller = caller
        self._file = caller.source.file
        self._code = _NOT_CODE.sub("", _CALL_MARKER.sub("", caller.source.text if caller.source.file else ""))
        self._owner = self._class_declaring(caller)
        # The class each local is, by its name; a local that is a collection is kept by what it holds once looped over.
        self._locals: dict[str, "Node"] = {}
        # The parameters and locals whose class no line of the body or signature gives.
        self._untyped: set[str] = set()

    def called(self) -> "list[Node]":
        """The members its body calls and the properties it reads, in the order the body names them."""
        self._name_locals()
        found = [member for member in self._reached_through_receivers() if member is not self._caller]
        found.extend(function for function in self._called_by_name() if function is not self._caller)
        return found

    def _class_declaring(self, member: "Node") -> "Node | None":
        owner = member.get_fact("owner")
        return next((node for node in self._index.classes_named(owner) if node.source.file == member.source.file), None) if owner else None

    def _name_locals(self) -> None:
        """Type each parameter by its hint, each local built from a class by that class, and each loop's local by what
        the collection it walks holds."""
        for edge in self._graph.edges.from_parent("hasParameter", self._caller):
            self._keep_local(edge.child.name, self._class_of_hint(edge.child.get_fact("type_hint"), self._file))
        for name, built in _BUILT_LOCAL.findall(self._code):
            self._keep_local(name, self._reach.class_named(built, self._file))
        for name, walked in _LOOP_LOCAL.findall(self._code):
            self._keep_local(name, self._held_by(walked.split(".")))
        parameters = {edge.child.name for edge in self._graph.edges.from_parent("hasParameter", self._caller)}
        self._untyped = (parameters | set(_ASSIGNED_LOCAL.findall(self._code))) - set(self._locals) - _OWN_OBJECT

    def _keep_local(self, name: str, found: "Node | None") -> None:
        if found is not None:
            self._locals.setdefault(name, found)

    def _reached_through_receivers(self) -> "Iterator[Node]":
        """Each member a dotted chain reaches: every part after the first is a member of the class the part before it
        is. A part with a call after it may be an operation; any other is a property read."""
        for chain in _CHAIN.finditer(self._code):
            parts = chain.group(1).split(".")
            holder = self._class_of_head(parts[0])
            if holder is None and len(parts) == 2 and chain.group(2) and parts[0] in self._untyped:
                only = self._reach.only_member_named(parts[1], self._file, self._graph.scope.over_whole)
                if only is not None:
                    yield only
            for position, name in enumerate(parts[1:], start=1):
                if holder is None:
                    break
                member = self._member_of(holder, name)
                last_and_called = position == len(parts) - 1 and bool(chain.group(2))
                if member is not None and (member.type == "Property" or last_and_called):
                    yield member
                holder = self._class_of_hint(self._hint_of(holder, name, member), holder.source.file)

    def _called_by_name(self) -> "Iterator[Node]":
        """Each module function its body calls by name alone, and the constructor of the class it extends for a brace
        language's `super(...)`."""
        for name in dict.fromkeys(_BARE_CALL.findall(self._code)):
            if name == "super":
                base = self._class_of_head("super")
                constructor = self._member_of(base, "constructor") if base is not None else None
                if constructor is not None:
                    yield constructor
                continue
            function = self._reach.function_named(name, self._file)
            if function is not None:
                yield function

    def _class_of_head(self, head: str) -> "Node | None":
        """The class the first part of a chain is: the caller's own, the one it extends, a local's, or a class named
        outright."""
        if head in _OWN_OBJECT:
            return self._owner
        if head in _BASE_OBJECT:
            return next(iter(self._bases_of(self._owner)), None) if self._owner is not None else None
        if head in self._locals:
            return self._locals[head]
        return self._reach.class_named(head, self._file) if head[:1].isupper() else None

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
        return self._reach.class_named(held, holder.source.file) if held else None

    def _hint_of(self, holder: "Node", name: str, member: "Node | None") -> str:
        """The type holder's member called name has: the member's own, else the type of the field holder keeps."""
        if member is not None and member.get_fact("value_type"):
            return str(member.get_fact("value_type"))
        return str((holder.get_fact("held_fields") or {}).get(name) or "")

    def _class_of_hint(self, hint: str | None, file: str) -> "Node | None":
        """The class a type hint names as one object, an optional one included; none for a collection or a built-in."""
        written = (hint or "").strip()
        optional = _OPTIONAL.match(written)
        if optional:
            written = next(group for group in optional.groups() if group).strip()
        return self._reach.class_named(written, file) if _NAME.match(written) else None

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
        named = (self._reach.class_named(str(base).split("[")[0].split("<")[0].strip(), holder.source.file) for base in holder.get_fact("bases") or [])
        return [base for base in named if base is not None and base is not holder]
