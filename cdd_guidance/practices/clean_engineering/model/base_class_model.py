"""Canonical CleanEngineering class model - OoadNode base and typed nodes."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext, PublicSources
from cdd_guidance.practices.clean_engineering.model.ooad_node import OoadNode
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.script_imports import ClassReference, ScriptImports
from cdd_guidance.practices.clean_engineering.model.source_facts import ClassSourceFacts
from cdd_guidance.practices.clean_engineering.model.type_refs import domain_type_names


_EXAMPLE_EXTENSION_PREFIXES = ("Fake", "Isolated", "Production")
# A class with one of these stereotypes owns the peers it builds, so building them is not a hidden dependency.
_PEER_COMPOSING_STEREOTYPES = frozenset({"entity", "aggregate root"})


# The class a parser puts a file's module functions in, which no rule judges as a class of its own.
MODULE_FUNCTION_HOLDER = "_module"


class UnreadableSource(ValueError):
    """A source file its language cannot read, such as Python that does not parse. Reading it as an empty or partial
    model would drop its classes from every check without saying so."""


def path_parent(name: str) -> Optional[str]:
    """The path that holds a nested module path: `powers` for `powers/attack`; None at the top."""
    if "/" not in name:
        return None
    return name.rsplit("/", 1)[0]


def is_interface_name(name: str) -> bool:
    """True for I{Class} contract names (e.g. IShoppingCart)."""
    return len(name) > 1 and name[0] == "I" and name[1].isupper()


def interface_name_for(class_name: str) -> str:
    """Public seam name for a production type."""
    return class_name if is_interface_name(class_name) else f"I{class_name}"


def production_name_for(name: str) -> str:
    """Domain type name paired with an I{Class} contract."""
    return name[1:] if is_interface_name(name) else name


def example_extension_kind(name: str) -> str | None:
    """Return Fake|Isolated|Production when name is Fake{Type} / Isolated{Type} / Production{Type}."""
    for prefix in _EXAMPLE_EXTENSION_PREFIXES:
        rest = name[len(prefix) :]
        if name.startswith(prefix) and rest and rest[0].isupper():
            return prefix
    return None


def base_type_name_for(name: str) -> str:
    """Cart from FakeCart / IsolatedCart / ProductionCart / ICart / Cart."""
    kind = example_extension_kind(name)
    if kind:
        return name[len(kind) :]
    return production_name_for(name)


def companion_interface_name(class_name: str, known_names: Iterable[str]) -> str | None:
    """If class_name has a sibling I{Class} in known_names, return that name.

    Resolves production Class -> IClass and Fake|Isolated|Production{Type} -> I{Type}.
    """
    if is_interface_name(class_name):
        return None
    known = set(known_names)
    candidate = interface_name_for(class_name)
    if candidate in known:
        return candidate
    kind = example_extension_kind(class_name)
    if kind:
        iface = interface_name_for(base_type_name_for(class_name))
        if iface in known:
            return iface
    return None


class OoadClass(OoadNode):
    _semantic_type_name = "OoadClass"
    # The kinds of member this class holds; a format's class names its own, which spell their lines in that format.
    property_type: type = Property
    operation_type: type = Operation
    graph_facts = (
        "bases",
        "stereotypes",
        "method_count",
        "operation_shapes",
        "property_names",
        "held_fields",
        "constructs",
        "composes_peers",
        "peer_names",
        "module_helpers",
        "prose_comment",
        "prototype_swap",
        "bold_interaction_lines",
        "bold_invariant_lines",
    )

    def __init__(self, name: str, sequential_order: int, intent: str = "") -> None:
        super().__init__(name, sequential_order)
        self.intent = intent
        # The classes it works with, named on its card; its parser or a translation fills them.
        self.collaborators: List[str] = []
        # What this class does to another class at run time, each named by its interaction: `Repo ---<<runs>>--> Git`.
        self.dependencies: List[Relationship] = []
        self._start_declaration()
        self._properties = ModelChildren(self, "participants")
        self._operations = ModelChildren(self, "participants")

    def _start_declaration(self) -> None:
        """What the class's declaration says, empty until its parser or a translation fills it."""
        self.line: int | None = None
        self.end_line: int | None = None
        # Each stereotype as its words, such as `Aggregate Root`, whatever decorator or comment spelled it.
        self.stereotypes: List[str] = []
        # The modules the class says it is kept in, outermost first, when its source names them apart from where the
        # class sits, as a code file does in a class's doc comment: `Sales | custom`, `ShoppingCart`.
        self.module_path: List[str] = []
        self.bases: List[str] = []
        self.peer_names: List[str] = []
        self.module_helpers: List[list] = []
        # What its source says, as its parser reads it: the lines it spans and the facts they give.
        self.source_facts = ClassSourceFacts(self)
        # Where each relationship drawn from it lands: on the properties it types, or among its dependencies.
        self.arrows = ClassArrows(self)

    @property
    def properties(self) -> List["Property"]:
        return self._properties

    @properties.setter
    def properties(self, properties: List["Property"]) -> None:
        self._properties.refill(properties)

    @property
    def operations(self) -> List["Operation"]:
        return self._operations

    @operations.setter
    def operations(self, operations: List["Operation"]) -> None:
        self._operations.refill(operations)

    @property
    def composes_peers(self) -> bool:
        """An Entity or Aggregate Root owns the peers it builds, so building them is not a hidden dependency."""
        return bool(_PEER_COMPOSING_STEREOTYPES & {item.lower() for item in self.stereotypes})

    @property
    def held_fields(self) -> dict[str, str]:
        """Each field the class holds, with its type hint. It saves with the graph, so a rule that compares the
        classes' fields reads them from a class read back from a saved graph too."""
        return self.source_facts.held_fields()

    def declared_bases(self, known_names: Iterable[str]) -> List[str]:
        """The bases its declaration names: its own, then the I{Class} contract it implements when one is known."""
        bases = list(self.bases)
        contract = companion_interface_name(self.name, known_names)
        if contract and contract not in bases:
            bases.append(contract)
        return bases

    def update_self(self, source: "OoadNode") -> None:
        """Copy what the class itself says; its properties and operations are reconciled as children."""
        assert isinstance(source, OoadClass)
        self.intent = source.intent
        self.stereotypes = list(source.stereotypes)
        self.module_path = list(source.module_path)
        self.bases = list(source.bases)
        self.collaborators = list(source.collaborators)
        self.dependencies = [item.clone() for item in getattr(source, "dependencies", [])]

    def clone(self) -> "OoadClass":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.update_self(self)
        cloned.line = self.line
        cloned.properties = [item.clone() for item in self.properties]
        cloned.operations = [item.clone() for item in self.operations]
        return cloned

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "intent": self.intent,
            "stereotypes": list(self.stereotypes),
            "modulePath": list(self.module_path),
            "bases": list(self.bases),
            "properties": [item.as_record() for item in self.properties],
            "operations": [item.as_record() for item in self.operations],
            "relationships": [item.as_record() for item in self.relationships],
            "dependencies": [item.as_record() for item in self.dependencies],
            "collaborators": list(self.collaborators),
        }

    def load_property(self, source: Property) -> Property:
        """A new property of this class's own kind, filled from source."""
        loaded = self.property_type(source.name, source.sequential_order)
        loaded.update_self(source)
        return loaded

    def load_operation(self, source: Operation) -> Operation:
        """A new operation of this class's own kind, filled from source."""
        loaded = self.operation_type(source.name, source.sequential_order)
        loaded.update_self(source)
        return loaded

    def reconcile_children(self, source: "OoadNode") -> None:
        assert isinstance(source, OoadClass)
        self._properties.reconcile(source.properties, self.load_property)
        self._operations.reconcile(source.operations, self.load_operation)

    def declares(self, member: OoadNode) -> bool:
        """True when member is one of this class's own operations or properties."""
        return any(member is held for held in [*self._operations, *self._properties])

    @property
    def public_properties(self) -> List[Operation | Property]:
        """What its instances show as properties, each once, in line order: the fields it declares, then its getters,
        each an operation read as a property. A static field belongs to the class, not to its instances, and a name
        starting with `_` is private."""
        found: List[Operation | Property] = []
        seen: set = set()
        fields = [prop for prop in self.properties if not prop.is_static]
        getters = [operation for operation in self.operations if operation.is_property]
        for member in [*fields, *getters]:
            if str(member.name).startswith("_") or member.name in seen:
                continue
            seen.add(member.name)
            found.append(member)
        return sorted(found, key=lambda member: (member.line or 1, member.name))

    @property
    def relationships(self) -> List[Relationship]:
        """Relationships that live on properties whose type is a domain class."""
        return [
            prop.relationship
            for prop in self.properties
            if getattr(prop, "relationship", None) is not None
        ]


class ClassArrows:
    """Where each relationship drawn from a class lands, which the class makes once and keeps (``oclass.arrows``): a
    composition, aggregation, or association becomes the properties whose type names its target; a dependency, what
    the class does to another class at run time, joins the class's dependencies; inheritance is the class's bases."""

    def __init__(self, oclass: OoadClass) -> None:
        self._class = oclass

    def place(self, relationship: Relationship) -> None:
        """Put the relationship on every property whose type names its target, or keep it as a dependency."""
        kind = (relationship.kind or "").lower()
        if kind == "inheritance":
            return
        if kind == "dependency":
            self._keep_dependency(relationship)
            return
        for prop in self._class.properties:
            if relationship.target in domain_type_names(getattr(prop, "type_hint", "") or ""):
                prop.arrow.take(relationship)

    def depend_on(self, target: str, label: str) -> None:
        """Record that the class acts on target at run time, labelled by the interaction; the same pair and label once."""
        self._keep_dependency(Relationship(target=target, kind="dependency", label=label))

    def _keep_dependency(self, dependency: Relationship) -> None:
        """Keep the dependency as read, with its details; the same target and label once."""
        held = self._class.dependencies
        if any(item.target == dependency.target and item.label == dependency.label for item in held):
            return
        held.append(dependency)


class Module(OoadNode):
    """A named module boundary grouping closely related classes."""

    _semantic_type_name = "Module"
    # The kind of class this module holds; a format's module names its own.
    class_type: type = OoadClass
    graph_facts = (
        "has_module_context",
        "has_bounded_context",
        "modules_heading",
        "names_seam",
        "names_constraint",
        "model_blocks",
        "is_a_in_context",
        "child_parent_in_context",
        "public_source_internal",
        "public_source_files",
        "dependencies",
        "imported_classes",
    )

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        # What its module card says: its purpose, its public seam and the terms it names, its constraint, and the
        # modules it depends on. Its parser or a translation fills them.
        self.description = ""
        self.seam = ""
        self.constraint = ""
        self.seam_terms: List[str] = []
        self.dependencies: List[str] = []
        self._start_source()
        self._modules = ModelChildren(self, "participants")
        self._classes = ModelChildren(self, "participants")

    def _start_source(self) -> None:
        """The source this module is read from, empty until its parser keeps the file's text."""
        self.preamble = CodeBody()
        self.source_text = ""
        # The classes this module's code imports, re-exports, or reaches as `module.Class`, each with the module it
        # names it from.
        self.imported_classes: List[ClassReference] = []
        # What the file and folder it was read from say, as its parser reads them.
        self.source_facts = ModuleSourceFacts(self)

    @property
    def modules(self) -> List["Module"]:
        return self._modules

    @modules.setter
    def modules(self, modules: List["Module"]) -> None:
        self._modules.refill(modules)

    @property
    def classes(self) -> List[OoadClass]:
        return self._classes

    @classes.setter
    def classes(self, classes: List[OoadClass]) -> None:
        self._classes.refill(classes)

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "description": self.description,
            "seam": self.seam,
            "seamTerms": list(self.seam_terms),
            "dependencies": list(self.dependencies),
            "constraint": self.constraint,
            "classes": [loaded.as_record() for loaded in self.classes],
        }

    @property
    def path_parent(self) -> Optional[str]:
        """The module whose path holds this one: `powers` for `powers/attack`; None at the top."""
        return path_parent(self.name)

    def external_deps(self) -> List[str]:
        """The modules this one depends on, leaving out the path parent that contains it."""
        return [dependency for dependency in self.dependencies if dependency != self.path_parent]

    def public_terms(self) -> List[str]:
        """Seam bullets for modules fidelity: explicit terms, else thin class names, else seam string."""
        if self.seam_terms:
            return list(self.seam_terms)
        if self.classes:
            return [c.name for c in self.classes]
        if self.seam:
            return [t.strip() for t in self.seam.replace(";", ",").split(",") if t.strip()]
        return []

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, Module)
        self.description = source.description
        self.seam = source.seam
        self.constraint = source.constraint
        self.seam_terms = list(source.seam_terms)
        self.dependencies = list(source.dependencies)
        self.preamble = source.preamble

    def clone(self) -> "Module":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.update_self(self)
        cloned.modules = [module.clone() for module in self.modules]
        cloned.classes = [oclass.clone() for oclass in self.classes]
        return cloned

    def load_module(self, source: "Module") -> "Module":
        """A module of this one's own kind for source, named and placed as it is; translating it fills the rest."""
        return type(self)(name=source.name, sequential_order=source.sequential_order)

    def load_class(self, source: OoadClass) -> OoadClass:
        """A class of the kind this module holds (``class_type``) for source, named and placed as it is; translating
        it fills the rest."""
        return self.class_type(name=source.name, sequential_order=source.sequential_order)

    def import_targets(self, file: Path, root: Path) -> List[str]:
        """Root-relative paths the relative script imports of its file reach; a language that reads its imports
        another way, as Python reads its syntax tree, names its own."""
        return ScriptImports(self.source_text).targets(file, root)

    @property
    def documentation(self) -> str:
        """The documentation the file this module was read from writes: its doc strings and comments. Only Python's
        is read; a string the code holds, such as a marker a rule looks for, is not documentation."""
        return ""

    def reconcile_children(self, source: "OoadNode") -> None:
        assert isinstance(source, Module)
        self._modules.reconcile(source.modules, self.load_module)
        self._classes.reconcile(source.classes, self.load_class)


class ModuleSourceFacts:
    """What the file and the folder a module was read from say, which the module makes once and keeps
    (``module.source_facts``): the file's text and the lines each class spans, what the file imports, the facts the
    folder's context files give, and what its public source files document."""

    def __init__(self, module: Module) -> None:
        self._module = module

    def take_lines(self, text: str) -> None:
        """Keep the text of the file the module was read from, and the span of each class in it."""
        self._module.source_text = text
        lines = text.split("\n")
        for oclass in self._module.classes:
            oclass.source_facts.take_lines(lines)

    def load(self, file: Path, root: Path) -> None:
        """Fill the facts the file the module was read from owns: what it imports, the classes it imports with the
        module each comes from, and which classes share it. The graph keeps each class apart from its module, so each class keeps its peers' names."""
        module = self._module
        module.dependencies = module.import_targets(file, root)
        module.imported_classes = ScriptImports(module.source_text).class_references(file, root)
        peer_names = [oclass.name for oclass in module.classes]
        for oclass in module.classes:
            oclass.peer_names = peer_names

    def load_folder(self, folder: Path) -> None:
        """Keep the facts a code folder's context files give, what its module card says, as the module's graph facts."""
        for name, fact in ModuleContext(folder).folder_facts().items():
            setattr(self._module, name, fact)

    def take_public_sources(self, sources: List[Module]) -> None:
        """Keep the facts the folder's public source files give, each read into its module: how many there are, and
        whether their documentation carries internal design notes."""
        public = PublicSources([source.documentation for source in sources])
        self._module.public_source_files = public.count
        self._module.public_source_internal = public.internal_notes()


class CleanEngineeringModel(OoadNode):
    _semantic_type_name = "CleanEngineeringModel"
    # The kind of module this model holds; a format's model names its own.
    module_type: type = Module

    def __init__(self, name: str | Graph = "", sequential_order: int = 1, graph: Optional[Graph] = None) -> None:
        opened = isinstance(name, Graph)
        if opened:
            graph = name
            name = "model"
        super().__init__(name, sequential_order, graph)
        self._modules = ModelChildren(self, "participants")

    @property
    def modules(self) -> List[Module]:
        return self._modules

    @modules.setter
    def modules(self, modules: List[Module]) -> None:
        self._modules.refill(modules)

    @property
    def modules_title(self) -> str:
        """The title a modules view is drawn under: the system's name, then what the view shows."""
        return f"{self.name or 'System'} - Modules Context"

    @property
    def is_modules_view(self) -> bool:
        """True when the model shows modules only: no class carries a member or a drawn relationship."""
        if not self.modules:
            return False
        classes = [oclass for module in self.modules for oclass in module.classes]
        for oclass in classes:
            if oclass.properties or oclass.operations:
                return False
            if any(relationship.kind for relationship in oclass.relationships):
                return False
        if any(module.dependencies or module.seam_terms for module in self.modules):
            return True
        if not classes:
            return True
        return all(not oclass.properties and not oclass.operations and not oclass.relationships for oclass in classes)

    def described_member(self, owner: str, name: str) -> Operation | Property | None:
        """The operation or property this model's class owner describes as name; none when it describes no such member.
        An operation is the one a call runs, so it comes before a property of the same name."""
        for oclass in self.every_class():
            if oclass.name != owner:
                continue
            found = next((member for member in [*oclass.operations, *oclass.properties] if member.name == name), None)
            if found is not None:
                return found
        return None

    def every_class(self) -> List[OoadClass]:
        """Every class in every module, nested modules included, in module order."""
        found: List[OoadClass] = []
        pending = list(self.modules)
        while pending:
            module = pending.pop(0)
            found.extend(module.classes)
            pending[:0] = module.modules
        return found

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "modules": [module.as_record() for module in self.modules],
        }

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, CleanEngineeringModel)
        self.name = source.name

    def clone(self) -> "CleanEngineeringModel":
        cloned = type(self)(self.name, self.sequential_order)
        for module in self.modules:
            cloned.modules.append(module.clone())
        return cloned

    def save(self) -> str:
        raise NotImplementedError(f"{type(self).__name__} must implement save")

    def parse(self, text: str) -> "CleanEngineeringModel":
        raise NotImplementedError(f"{type(self).__name__} must implement parse")

    def load_module(self, source: Module) -> Module:
        """A module of the kind this model holds (``module_type``) for source, named and placed as it is; translating
        it fills the rest."""
        return self.module_type(name=source.name, sequential_order=source.sequential_order)

    def reconcile_children(self, source: "OoadNode") -> None:
        assert isinstance(source, CleanEngineeringModel)
        self._modules.reconcile(source.modules, self.load_module)
