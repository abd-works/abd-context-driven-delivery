"""Canonical CleanEngineering class model - OoadNode base and typed nodes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext
from cdd_guidance.practices.clean_engineering.model.ooad_node import OoadNode
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.operation_metrics import SourceText
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.type_refs import domain_type_names
from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code


_EXAMPLE_EXTENSION_PREFIXES = ("Fake", "Isolated", "Production")
_SCRIPT_IMPORT = re.compile(r"""(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*\(?\s*)['"](\.{1,2}/[^'"]+)['"]""")
_PY_FROM_IMPORT = re.compile(r"^\s*from\s+[\w.]+\s+import\s+(\([^)]*\)|[^\n]+)", re.M)
_JS_IMPORT = re.compile(r"\bimport\s+(?:type\s+)?([\w$]+)?\s*,?\s*(?:\{([^}]*)\})?\s*from\b")
_QUALIFIED_CLASS = re.compile(r"\.([A-Z]\w*)\b")
_IMPORT_ALIAS = re.compile(r"\s+as\s+\w+")
_INTERNAL_MARKDOWN = re.compile(r"^##\s+Internal\b", re.MULTILINE | re.IGNORECASE)
# A class with one of these stereotypes owns the peers it builds, so building them is not a hidden dependency.
_PEER_COMPOSING_STEREOTYPES = frozenset({"entity", "aggregate root"})


class UnreadableSource(ValueError):
    """A source file its language cannot read, such as Python that does not parse. Reading it as an empty or partial
    model would drop its classes from every check without saying so."""


def class_names_imported_by(source_text: str) -> set:
    """The names a source file imports (`from x import A`, `import { A } from`) or reaches as `module.Class`."""
    names: set = set(_QUALIFIED_CLASS.findall(source_text))
    for match in _PY_FROM_IMPORT.finditer(source_text):
        names.update(_IMPORT_ALIAS.sub("", item).strip() for item in match.group(1).strip("()").split(","))
    for default, braced in _JS_IMPORT.findall(source_text):
        names.add(default)
        names.update(_IMPORT_ALIAS.sub("", item).strip() for item in (braced or "").split(","))
    names.discard("")
    return names


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
        "constructs",
        "composes_peers",
        "peer_names",
        "module_helpers",
        "prose_comment",
        "prototype_swap",
        "bold_interaction_lines",
        "bold_invariant_lines",
    )

    def __init__(
        self,
        name: str,
        sequential_order: int,
        intent: str = "",
        properties: List["Property"] | None = None,
        operations: List["Operation"] | None = None,
        relationships: List[Relationship] | None = None,
        collaborators: List[str] | None = None,
        line: int | None = None,
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.intent = intent
        self.line = line
        # The stereotypes the class carries, as words: `Aggregate Root`, `Value Object`.
        self.stereotypes: List[str] = []
        # Parser facts for the graph: last source line and declared base classes.
        self.end_line: int | None = None
        self.bases: List[str] = []
        self.peer_names: List[str] = []
        self.module_helpers: List[list] = []
        self.collaborators: List[str] = collaborators if collaborators is not None else []
        # The source this class spans in its file, kept once its parser reads the file.
        self.span = SourceText("")
        # What this class does to another class at run time, each named by its interaction: `Repo ---<<runs>>--> Git`.
        self.dependencies: List[Relationship] = []
        self._properties = ModelChildren(self, "participants")
        self._operations = ModelChildren(self, "participants")
        if properties:
            self._properties.extend(properties)
        if operations:
            self._operations.extend(operations)
        for relationship in relationships or []:
            self.place_relationship(relationship)

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

    def take_lines(self, lines: List[str]) -> None:
        """Keep the lines of its file this class spans, from its line to its end line, and each operation's."""
        start = self.line or 1
        self.span = SourceText("\n".join(lines[start - 1 : self.end_line or start]))
        for operation in self.operations:
            operation.take_lines(lines)

    def load_source_facts(self) -> None:
        """Fill the shape and source-span facts this class owns."""
        operations = list(self.operations)
        constructor = next((op for op in operations if op.name in {"__init__", "constructor"}), None)
        self.method_count = len(operations)
        self.operation_shapes = [
            {"name": op.name, "is_property": op.is_property, "callees": [callee for callee in op.callees if callee]}
            for op in operations
        ]
        self.property_names = sorted(prop.name for prop in self.properties)
        self.constructs = [type_name for type_name, _line in constructor.constructed_types] if constructor else []
        source = self.span
        self.prose_comment = source.has_prose_comment(hash_only=True)
        self.prototype_swap = source.prototype_swap(self.line or 1)
        bullets = source.markdown_bullet_lines()
        self.bold_interaction_lines = bullets.get("bold_interaction_lines", [])
        self.bold_invariant_lines = bullets.get("bold_invariant_lines", [])

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
        self.bases = list(source.bases)
        self.collaborators = list(source.collaborators)
        self.dependencies = [item.clone() for item in getattr(source, "dependencies", [])]

    def clone(self) -> "OoadClass":
        cloned = type(self)(
            self.name,
            self.sequential_order,
            intent=self.intent,
            collaborators=list(self.collaborators),
            line=self.line,
        )
        cloned.stereotypes = list(self.stereotypes)
        cloned.bases = list(self.bases)
        cloned.dependencies = [item.clone() for item in self.dependencies]
        cloned.properties = [item.clone() for item in self.properties]
        cloned.operations = [item.clone() for item in self.operations]
        return cloned

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "intent": self.intent,
            "stereotypes": list(self.stereotypes),
            "bases": list(self.bases),
            "properties": [item.as_record() for item in self.properties],
            "operations": [item.as_record() for item in self.operations],
            "relationships": [item.as_record() for item in self.relationships],
            "dependencies": [item.as_record() for item in self.dependencies],
            "collaborators": list(self.collaborators),
        }

    def load_relationship(self, source: Relationship) -> Relationship:
        loaded = Relationship(target=source.target)
        loaded.update_self(source)
        return loaded

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

    def place_relationship(self, relationship: Relationship) -> None:
        """Put this relationship on every property whose type names the target."""
        if (relationship.kind or "").lower() == "inheritance":
            return
        if (relationship.kind or "").lower() == "dependency":
            self.depend_on(relationship.target, relationship.label)
            return
        for prop in self.properties:
            if relationship.target not in domain_type_names(getattr(prop, "type_hint", "") or ""):
                continue
            prop.take_relationship(relationship)

    def depend_on(self, target: str, label: str) -> None:
        """Record that this class acts on target at run time, labelled by the interaction; the same pair and label once."""
        if any(item.target == target and item.label == label for item in self.dependencies):
            return
        self.dependencies.append(Relationship(target=target, kind="dependency", label=label))


class Module(OoadNode):
    """A named module boundary grouping closely related classes."""

    _semantic_type_name = "Module"
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
        "imported_names",
    )

    def __init__(
        self,
        name: str,
        sequential_order: int,
        description: str = "",
        seam: str = "",
        constraint: str = "",
        seam_terms: List[str] | None = None,
        dependencies: List[str] | None = None,
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.description = description
        self.seam = seam
        self.constraint = constraint
        self.seam_terms: List[str] = list(seam_terms) if seam_terms is not None else []
        self.dependencies: List[str] = list(dependencies) if dependencies is not None else []
        self.preamble = CodeBody()
        # The text of the file this module was read from, which its parser keeps.
        self.source_text = ""
        # The class names this module's code imports or reaches as `module.Class`.
        self.imported_names: List[str] = []
        self._modules = ModelChildren(self, "participants")
        self._classes = ModelChildren(self, "participants")

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
        cloned = type(self)(
            self.name,
            self.sequential_order,
            description=self.description,
            seam=self.seam,
            constraint=self.constraint,
            seam_terms=list(self.seam_terms),
            dependencies=list(self.dependencies),
        )
        cloned.preamble = self.preamble
        cloned.modules = [module.clone() for module in self.modules]
        cloned.classes = [oclass.clone() for oclass in self.classes]
        return cloned

    def load_module(self, source: "Module") -> "Module":
        return Module(name=source.name, sequential_order=source.sequential_order)

    def load_class(self, source: OoadClass) -> OoadClass:
        return OoadClass(name=source.name, sequential_order=source.sequential_order)

    def take_lines(self, text: str) -> None:
        """Keep the text of the file this module was read from, and the span of each class in it."""
        self.source_text = text
        lines = text.split("\n")
        for oclass in self.classes:
            oclass.take_lines(lines)

    def load_source_facts(self, file: Path, root: Path) -> None:
        """Fill the facts the file this module was read from owns: what it imports, the class names it imports, and
        which classes share it. The graph keeps each class apart from its module, so each class keeps its peers' names."""
        self.dependencies = self.import_targets(file, root)
        self.imported_names = sorted(class_names_imported_by(self.source_text))
        peer_names = [oclass.name for oclass in self.classes]
        for oclass in self.classes:
            oclass.peer_names = peer_names

    def import_targets(self, file: Path, root: Path) -> List[str]:
        """Root-relative paths named by relative script imports (`./x`, `../y`)."""
        targets: List[str] = []
        for specifier in _SCRIPT_IMPORT.findall(self.source_text):
            resolved = (file.parent / specifier).resolve()
            if resolved.is_relative_to(root.resolve()):
                targets.append(resolved.relative_to(root.resolve()).as_posix())
        return targets

    def load_folder_facts(self, folder: Path) -> None:
        """Fill the facts a code folder's context files give: what its module card says, read once."""
        card = ModuleContext(folder)
        self.has_module_context = card.exists()
        self.has_bounded_context = (folder / ".context" / "bounded-context.md").is_file()
        self.modules_heading = card.has_modules_heading()
        self.names_seam = card.names_seam()
        self.names_constraint = card.names_constraint()
        self.model_blocks = card.model_blocks()
        self.is_a_in_context = card.says_is_a_type_of()
        self.child_parent_in_context = card.writes_child_parent_headings()

    def holds_public_source(self, file_name: str) -> bool:
        """True for a file of this folder other modules may read: production code whose name does not start with `_`."""
        return not file_name.startswith("_") and not is_test_code(file_name)

    def take_public_sources(self, sources: List["Module"]) -> None:
        """Fill the facts this folder's public source files give, each read into its module: how many there are, and
        whether their documentation carries internal design notes: 'heading' for an internal-design section heading,
        'mixed' for internal notes inline, else ''."""
        self.public_source_files = len(sources)
        text = "\n".join(source.documentation for source in sources)
        if _INTERNAL_MARKDOWN.search(text):
            self.public_source_internal = "heading"
        elif "## Internal" in text or "_ holds " in text:
            self.public_source_internal = "mixed"
        else:
            self.public_source_internal = ""

    @property
    def documentation(self) -> str:
        """The documentation the file this module was read from writes: its doc strings and comments. Only Python's
        is read; a string the code holds, such as a marker a rule looks for, is not documentation."""
        return ""

    def reconcile_children(self, source: "OoadNode") -> None:
        assert isinstance(source, Module)
        self._modules.reconcile(source.modules, self.load_module)
        self._classes.reconcile(source.classes, self.load_class)


class CleanEngineeringModel(OoadNode):
    _semantic_type_name = "CleanEngineeringModel"

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
        return Module(name=source.name, sequential_order=source.sequential_order)

    def reconcile_children(self, source: "OoadNode") -> None:
        assert isinstance(source, CleanEngineeringModel)
        self._modules.reconcile(source.modules, self.load_module)
