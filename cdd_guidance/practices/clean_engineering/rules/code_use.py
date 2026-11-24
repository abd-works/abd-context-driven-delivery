"""How the production code of one graph uses itself: which classes and operations anything uses, which only a call the
read could not join may use, which are called only from their own folder, which classes are joined to others only by
inheritance, and which packages hold one class. The rules about unused and disconnected code read it
(``code_use_rules.py``); each makes it once for the practice it checks.

Use is an edge between two classes of the code (one extends, holds, creates, calls, reads, or is handed the other), a
call into a member from another member or from a module's function, or a way the project reaches code besides calls
and imports (``CodeReach``, the ``code_reach`` section of the project's ``.context/config.json``). A call from test code
is no use, since code only its own spec keeps alive is deleted with that spec."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from harness.graph.graph import READ_AT_FIDELITY

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.reading.code_read import CODE_FIDELITY
from cdd_guidance.practices.clean_engineering.reading.receiver_causes import ON_UNTYPED_VALUES, OTHERWISE, UNRESOLVED_CALLS_FACTS
from cdd_guidance.practices.source_code.code_reach import CodeReach
from cdd_guidance.practices.source_code.script_imports import ClassReference
from cdd_guidance.practices.source_code.test_files import TestFileName

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

# The edges that join two classes, each a use of one by the other.
CLASS_EDGES = ("baseClass", "composition", "aggregation", "association", "dependsOn")
# The bases a language gives a class to say what kind of class it is, which call none of its members.
_LANGUAGE_MARKERS = frozenset({"object", "ABC", "Protocol", "Generic", "NamedTuple", "TypedDict"})
# The edges from a class to its supertype: one it extends, and a protocol it satisfies by shape.
_SUBTYPE_EDGES = ("baseClass", "realizes")
# The relationships that connect a class to another beside inheritance: it holds, is handed, or reaches the other.
RELATIONSHIPS = ("composition", "aggregation", "association", "dependsOn")
# The calls the read could not join that may reach the project's own code: a call on a value no type says, and one
# that failed for another reason. A call on an object from outside the code read cannot reach it.
_UNSEEN_FACTS = (UNRESOLVED_CALLS_FACTS[ON_UNTYPED_VALUES], UNRESOLVED_CALLS_FACTS[OTHERWISE])
_FOLDER_TYPES = ("Module", "Package")
# Members a language calls by its own rules, never by name in the code: a constructor and every double-underscore one.
_CONSTRUCTOR = "constructor"
# The word that names a file as examples, which production may show or render.
_EXAMPLES = "examples"


def _names_examples(file: str) -> bool:
    """Whether the file is named as examples: its last word, a dotted role, or an examples folder."""
    name = TestFileName(file)
    return name.is_example or (name.words[-1:] == [_EXAMPLES] and not name.is_spec) or _EXAMPLES in name.roles


def _is_under(file: str | None, folder: str) -> bool:
    file = (file or "").replace("\\", "/")
    folder = folder.replace("\\", "/").strip("/")
    return not folder or file == folder or file.startswith(f"{folder}/")


class CodeUse:
    """The use of the production code of the practice context checks, worked out once from its nodes and edges."""

    def __init__(self, context: RuleCheckContext) -> None:
        self._context = context
        self._graph = context.graph
        self._reach = CodeReach.from_graph(context.graph)
        # The project's test code, as the reading of the practice checked tells it.
        self._test_code = context.practice.reading.test_code

    @cached_property
    def classes(self) -> list[Node]:
        """The production classes read at the code fidelity, but the holder of a module's functions."""
        return [node for node in self._context.nodes("OoadClass") if self._is_production(node) and node.name != MODULE_FUNCTION_HOLDER and node.is_read_at(CODE_FIDELITY)]

    @cached_property
    def operations(self) -> list[Node]:
        """The public production operations read at the code fidelity, module functions among them."""
        return [node for node in self.members if node.type == "Operation" and self._is_public(node)]

    @cached_property
    def members(self) -> list[Node]:
        """The production members read at the code fidelity whose use a rule asks about: every operation, private ones
        and module functions among them, and every property a class computes (``@property``); but a constructor and a
        member the language calls by its own rules (``__eq__``), and a property's setter, which an assignment calls. A
        field is not asked about: a write and a read of it are one edge to the read."""
        operations = [node for node in self._context.nodes("Operation") if not self._called_by_the_language(node) and not node.get_fact("is_setter")]
        properties = [node for node in self._context.nodes("Property") if node.get_fact("is_property")]
        return [node for node in [*operations, *properties] if self._is_production(node) and self._is_code(node)]

    def unused_classes(self) -> list[Node]:
        """The classes nothing uses, which use nothing, and which no call the read could not join may use."""
        return [node for node in self.classes if not self._is_used(node) and not self._may_be_used_unseen(node)]

    def classes_unseen_calls_may_use(self) -> list[Node]:
        """The classes nothing the graph sees uses, which a call the read could not join may use."""
        return [node for node in self.classes if not self._is_used(node) and self._may_be_used_unseen(node)]

    def unused_operations(self) -> list[Node]:
        """The public operations nothing calls, of classes that are used, which no call the read could not join may
        reach."""
        return [node for node in self._operations_of_used_classes if not self._is_called(node) and not self._may_be_used_unseen(node)]

    def operations_unseen_calls_may_reach(self) -> list[Node]:
        """The public operations of used classes nothing the graph sees calls, which a call the read could not join may
        reach."""
        return [node for node in self._operations_of_used_classes if not self._is_called(node) and self._may_be_used_unseen(node)]

    def operations_called_only_in_their_module(self) -> list[Node]:
        """The public operations of a class on its module's seam (one code outside the module names, registers or
        publishes, its ``public_classes``) that only code inside the module calls, which no way of the project's reaches,
        and which override no operation of a base."""
        return [node for node in self.operations if self._called_only_in_its_module(node)]

    def disconnected_classes(self) -> list[tuple[Node, list[Node]]]:
        """Each used class whose family (itself, its bases and the classes that extend it) has no relationship with
        another class beside inheritance, and which no way of the project's reaches, with the classes of its family it
        extends or is extended by. A class a registry, a publishing decorator or another way reaches is held by the
        framework that reaches it, so it stands alone by design."""
        used = [node for node in self.classes if self._is_used(node)]
        return [(node, self._family(node)) for node in used if not any(self._related(member) or id(member) in self._reached_classes for member in [node, *self._family(node)])]

    def one_class_packages(self) -> list[tuple[Node, Node]]:
        """Each package, a folder with no module card of its own, that holds no folder and one production class, with
        that class."""
        found = []
        for package in self._context.nodes("Package"):
            held = self._context.targets(package, "owns")
            classes = [node for node in held if node in self._class_set]
            if len(classes) == 1 and not any(node.type in _FOLDER_TYPES for node in held):
                found.append((package, classes[0]))
        return found

    def unseen_calls_near(self, declared: Node | None) -> int:
        """How many calls the read could not join, made in the files that could reach the class or the module function:
        its own file, and each production file that imports its name."""
        if declared is None:
            return 0
        files = {declared.source.file, *self._importers.get(declared.name, ())}
        return sum(self._unseen_calls_in.get(file, 0) for file in files)

    def is_imported_elsewhere(self, declared: Node) -> bool:
        """Whether a production file other than its own imports the name of the class or the module function."""
        return bool(set(self._importers.get(declared.name, ())) - {declared.source.file})

    @cached_property
    def _importers(self) -> dict[str, set[str]]:
        """Each class or function name a production file imports, with the files that import it; an import by test code
        is no use, as its call is none."""
        imported_by_file: dict[str, list] = {}
        for folder in [*self._context.nodes("Module"), *self._context.nodes("Package")]:
            imported_by_file.update(folder.get_fact("imported_classes_by_file") or {})
        outside = self._context.practice.reading.in_graph.root.get_fact("imported_classes_outside") or {}
        imported_by_file.update({file: imported.get("classes") or [] for file, imported in outside.items()})
        importers: dict[str, set[str]] = {}
        production = {file: references for file, references in imported_by_file.items() if not self._test_code.is_example_code(file)}
        for file, references in production.items():
            for reference in references:
                importers.setdefault(reference[1], set()).add(file)
        return importers

    @cached_property
    def _unseen_calls_in(self) -> dict[str, int]:
        """How many calls the read could not join each file makes, by the file."""
        counted: dict[str, int] = {}
        for node in self._context.nodes("OoadClass"):
            unseen = sum(int(node.get_fact(fact) or 0) for fact in _UNSEEN_FACTS)
            if unseen:
                counted[node.source.file] = counted.get(node.source.file, 0) + unseen
        return counted

    @cached_property
    def _class_set(self) -> set[Node]:
        return set(self.classes)

    @cached_property
    def _reached_classes(self) -> set[int]:
        return {id(node) for node in self._reach.classes(self.classes)}

    @cached_property
    def _reached_operations(self) -> set[int]:
        return {id(node) for node in self._reach.operations([*self._context.nodes("Operation"), *self._context.nodes("Property")])}

    @cached_property
    def _callers(self) -> dict[int, list[Node]]:
        """Each member's production callers, by the member: every ``invokes`` edge into it, a guessed one among them."""
        callers: dict[int, list[Node]] = {}
        for edge in self._context.edges("invokes"):
            if self._is_production(edge.parent):
                callers.setdefault(id(edge.child), []).append(edge.parent)
        return callers

    @cached_property
    def _class_neighbours(self) -> dict[int, set[int]]:
        """Each class's neighbours: the classes an edge of ``CLASS_EDGES`` joins it to, either way, from production code."""
        neighbours: dict[int, set[int]] = {}
        for kind in CLASS_EDGES:
            for edge in self._context.edges(kind):
                if edge.parent.type == "OoadClass" and edge.child.type == "OoadClass" and edge.parent is not edge.child and self._is_production(edge.parent):
                    neighbours.setdefault(id(edge.parent), set()).add(id(edge.child))
                    neighbours.setdefault(id(edge.child), set()).add(id(edge.parent))
        return neighbours

    @cached_property
    def _members(self) -> dict[int, list[Node]]:
        """Each class's operations and properties, by the class."""
        members: dict[int, list[Node]] = {}
        for kind in ("Operation", "Property"):
            for member in self._context.nodes(kind):
                owner = self._owner(member)
                if owner is not None:
                    members.setdefault(id(owner), []).append(member)
        return members

    @cached_property
    def _subclasses(self) -> dict[int, list[Node]]:
        """Each class's subtypes: the classes that extend it, and those that satisfy it by shape when it is a protocol."""
        found: dict[int, list[Node]] = {}
        for kind in _SUBTYPE_EDGES:
            for edge in self._context.edges(kind):
                found.setdefault(id(edge.child), []).append(edge.parent)
        return found

    @cached_property
    def _operations_of_used_classes(self) -> list[Node]:
        return [node for node in self.members if self._owner_is_used(node)]

    def unseen_calls_reaching(self, node: Node) -> int:
        """How many calls the read could not join may reach the class or member: those in the files that could reach it,
        or, for a member of a class, the files that could reach its class."""
        return self.unseen_calls_near(self._reached_through(node))

    def _may_be_used_unseen(self, node: Node) -> bool:
        """Whether a use the read could not see may reach the class or member: a call it could not join in a file that
        could reach it, or an import of its name in another file with no call the read joined."""
        target = self._reached_through(node)
        if node.type != "OoadClass" and self._extends_code_outside(self._owner(node)):
            return True
        return bool(self.unseen_calls_near(target)) or (target is node and self.is_imported_elsewhere(node))

    def _extends_code_outside(self, declared: Node | None) -> bool:
        """Whether the class, or a class it extends, extends a class from outside the code read, such as a library's,
        whose members the library may call as overrides the read cannot see."""
        if declared is None or declared.name == MODULE_FUNCTION_HOLDER:
            return False
        ancestors = [declared]
        for ancestor in ancestors:
            ancestors.extend(base for base in self._context.targets(ancestor, "baseClass") if base not in ancestors)
        return any(self._outside_bases(ancestor) for ancestor in ancestors)

    def _outside_bases(self, declared: Node) -> list[str]:
        """The bases the class names that the graph holds no class for, but the language's own markers of a kind of
        class (a protocol, an abstract base), which call nothing on it."""
        held = {base.name for base in self._context.targets(declared, "baseClass")}
        named = [str(base).split("[")[0].rsplit(".", 1)[-1] for base in declared.get_fact("bases") or []]
        return [name for name in named if name not in held and name not in _LANGUAGE_MARKERS]

    def _reached_through(self, node: Node) -> Node:
        """What another file names to reach node: a class or a module function itself, a member of a class its class."""
        owner = self._owner(node)
        return node if node.type == "OoadClass" or owner is None or owner.name == MODULE_FUNCTION_HOLDER else owner

    def _is_used(self, declared: Node) -> bool:
        """Whether the class uses or is used by another class, a member of another class or a module's function calls
        into it, or a way of the project's reaches it or one of its members."""
        if self._class_neighbours.get(id(declared)) or id(declared) in self._reached_classes:
            return True
        members = self._members.get(id(declared), [])
        if any(id(member) in self._reached_operations for member in members):
            return True
        return any(self._owner(caller) is not declared for member in members for caller in self._callers.get(id(member), []))

    def _owner_is_used(self, operation: Node) -> bool:
        owner = self._owner(operation)
        return owner is None or owner.name == MODULE_FUNCTION_HOLDER or owner not in self._class_set or self._is_used(owner)

    def _is_called(self, operation: Node) -> bool:
        """Whether a production member calls the operation, or the same operation of its family, which a call through
        a base or a subclass may reach; or a way of the project's reaches it."""
        if id(operation) in self._reached_operations:
            return True
        return any(self._callers.get(id(same)) for same in self._same_operation_in_family(operation))

    def _called_only_in_its_module(self, operation: Node) -> bool:
        callers = self._callers.get(id(operation), [])
        if not callers or id(operation) in self._reached_operations or len(self._same_operation_in_family(operation)) > 1:
            return False
        module = self._module_seam_of(self._owner(operation))
        return module is not None and all(_is_under(caller.source.file, module) for caller in callers)

    def _module_seam_of(self, declared: Node | None) -> str | None:
        """The folder of the nearest module above the class, when the class is on that module's seam; else none."""
        if declared is None:
            return None
        file = declared.source.file or ""
        enclosing = [module for module in self._context.nodes("Module") if _is_under(file, module.source.file or "")]
        if not enclosing:
            return None
        module = max(enclosing, key=lambda each: len(each.source.file or ""))
        public = module.get_fact("public_classes") or {}
        return module.source.file if f"{file}:{declared.name}" in public else None

    def _same_operation_in_family(self, operation: Node) -> list[Node]:
        """The operation, and each operation of the same name on a class its class extends or is extended by."""
        owner = self._owner(operation)
        if owner is None or owner.name == MODULE_FUNCTION_HOLDER:
            return [operation]
        family = [owner, *self._family(owner)]
        return [member for declared in family for member in self._members.get(id(declared), []) if member.name == operation.name and member.type == operation.type]

    def _family(self, declared: Node) -> list[Node]:
        """The classes declared extends or satisfies by shape (a protocol), and those that extend or satisfy it,
        followed both ways: a call through any of them may reach the same operation of each."""
        seen = {id(declared)}
        family: list[Node] = []
        waiting = [declared]
        while waiting:
            current = waiting.pop()
            for other in [*(target for kind in _SUBTYPE_EDGES for target in self._context.targets(current, kind)), *self._subclasses.get(id(current), [])]:
                if id(other) not in seen:
                    seen.add(id(other))
                    family.append(other)
                    waiting.append(other)
        return family

    def _related(self, declared: Node) -> bool:
        """Whether a relationship beside inheritance joins the class to another class, either way."""
        return id(declared) in self._relationship_ends

    @cached_property
    def _relationship_ends(self) -> set[int]:
        ends: set[int] = set()
        for kind in RELATIONSHIPS:
            for edge in self._context.edges(kind):
                if edge.parent.type == "OoadClass" and edge.child.type == "OoadClass" and edge.parent is not edge.child and self._is_production(edge.parent):
                    ends |= {id(edge.parent), id(edge.child)}
        return ends

    def _owner(self, member: Node | None) -> Node | None:
        """The class that declares member: an operation hangs under its class, and a property is grouped under it."""
        if member is None:
            return None
        parent = self._property_owners.get(id(member)) or self._graph.edges.direct_parent(member)
        return parent if parent is not None and parent.type == "OoadClass" else None

    @cached_property
    def _property_owners(self) -> dict[int, Node]:
        return {id(edge.child): edge.parent for edge in self._context.edges("properties")}

    def _folder_of(self, declared: Node | None) -> Node | None:
        parent = self._graph.edges.direct_parent(declared) if declared is not None else None
        return parent if parent is not None and parent.type in _FOLDER_TYPES else None

    def _is_production(self, node: Node) -> bool:
        """Whether node is production code: not test or example code, or example code a production file imports, which
        then runs in production."""
        file = node.source.file or ""
        return not self._test_code.is_example_code(file) or file in self._example_files_production_imports

    @cached_property
    def _example_files_production_imports(self) -> set[str]:
        """The files named as examples (``catalog_examples.py``, a file in an examples folder) that a production file
        imports a class or function from: examples production shows or renders. Test support a production file imports,
        such as a spec's helpers, stays test code: its name says only specs use it."""
        imported: set[str] = set()
        for folder in [*self._context.nodes("Module"), *self._context.nodes("Package")]:
            for file, references in (folder.get_fact("imported_classes_by_file") or {}).items():
                if not self._test_code.is_example_code(file):
                    imported.update(target for reference in references for target in ClassReference(*reference).files() if _names_examples(target))
        return imported

    def _is_code(self, member: Node) -> bool:
        """Whether the member is read at the code fidelity: as its reading recorded on it, such as a member only a model
        document declares, which is at the model fidelity under a class of code; else as its class is, since a property
        answers none of its own."""
        if member.has_fact(READ_AT_FIDELITY):
            return member.is_read_at(CODE_FIDELITY)
        owner = self._owner(member)
        return member.is_read_at(CODE_FIDELITY) or (owner is not None and owner.is_read_at(CODE_FIDELITY))

    def _is_public(self, operation: Node) -> bool:
        return not (operation.name.startswith("_") or operation.get_fact("is_private"))

    def _called_by_the_language(self, operation: Node) -> bool:
        name = operation.name
        return name == _CONSTRUCTOR or (name.startswith("__") and name.endswith("__"))
