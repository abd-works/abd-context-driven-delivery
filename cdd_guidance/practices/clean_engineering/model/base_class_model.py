"""Canonical CleanEngineering class model - OoadNode base and typed nodes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional

from harness.graph.model_node import ModelChildren, ModelNode
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation_metrics import SourceText
from cdd_guidance.practices.clean_engineering.model.update_report import ChildCollectionPair, TranslationError, UpdateReport

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.operation import Operation
    from cdd_guidance.practices.clean_engineering.model.property import Property


_EXAMPLE_EXTENSION_PREFIXES = ("Fake", "Isolated", "Production")
_CODE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx")
_SCRIPT_IMPORT = re.compile(r"""(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*\(?\s*)['"](\.{1,2}/[^'"]+)['"]""")
_IS_A = re.compile(r"\*is a type of\*", re.I)
_CHILD_PARENT = re.compile(r"^\s*#{1,6}\s+\S.+\s+:\s+\S", re.MULTILINE)
_INTERNAL_MARKDOWN = re.compile(r"^##\s+Internal\b", re.MULTILINE | re.IGNORECASE)
# A class with one of these stereotypes owns the peers it builds, so building them is not a hidden dependency.
_PEER_COMPOSING_STEREOTYPES = frozenset({"entity", "aggregate root"})


class UnreadableSource(ValueError):
    """A source file its language cannot read, such as Python that does not parse. Reading it as an empty or partial
    model would drop its classes from every check without saying so."""


def _internal_design_in(paths: List[Path]) -> str:
    """'heading' for an `## Internal` section, 'mixed' for internal notes inline, else ''."""
    text = "\n".join(_readable_text(path) for path in sorted(paths))
    if _INTERNAL_MARKDOWN.search(text):
        return "heading"
    if "## Internal" in text or "_ holds " in text:
        return "mixed"
    return ""


def _readable_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


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


class OoadNode(ModelNode):
    _graph_practice = "clean_engineering"
    _semantic_type_name: str = "OoadNode"
    _belongs = {
        ("OoadClass", "Module"),
        ("OoadClass", "CleanEngineeringModel"),
        ("Module", "Module"),
        ("Module", "CleanEngineeringModel"),
        ("Operation", "OoadClass"),
        ("Property", "OoadClass"),
        ("Parameter", "Operation"),
        ("Invariant", "Operation"),
        ("Invariant", "Property"),
    }

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)

    def translate_from(self, source: "OoadNode") -> UpdateReport:
        if self.semantic_type() != source.semantic_type():
            raise TranslationError(
                f"Cannot translate from {source.semantic_type()} into {self.semantic_type()}"
            )
        report = UpdateReport()
        self.update_self(source)
        for pair in self.child_collections(source):
            self._reconcile_collection(pair, report)
        return report

    def update_self(self, source: "OoadNode") -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement update_self")

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        raise NotImplementedError(f"{type(self).__name__} must implement child_collections")

    def _reconcile_collection(self, pair: ChildCollectionPair, report: UpdateReport) -> None:
        consumed_ids: set = set()
        reconciled: List[OoadNode] = []

        for source_child in pair.source_children:
            match = self._find_match(source_child, pair.self_children, consumed_ids)
            if match is not None:
                consumed_ids.add(id(match))
                match.translate_from(source_child)
                reconciled.append(match)
                report.add_exact_match(match.name)
            else:
                new_child = pair.load(source_child)
                new_child.translate_from(source_child)
                reconciled.append(new_child)
                report.add_new(new_child, parent_name=self.name)

        for existing in pair.self_children:
            if id(existing) not in consumed_ids:
                report.add_removed(existing, parent_name=self.name)

        pair.self_children[:] = reconciled

    @staticmethod
    def _find_match(
        source: "OoadNode",
        candidates: List["OoadNode"],
        consumed_ids: set,
    ) -> Optional["OoadNode"]:
        for c in candidates:
            if id(c) not in consumed_ids and c.name == source.name:
                return c
        for c in candidates:
            if id(c) not in consumed_ids and c.sequential_order == source.sequential_order:
                return c
        return None


class OoadClass(OoadNode):
    _semantic_type_name = "OoadClass"
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
        # What this class does to another class at run time, each named by its interaction: `---<<stops>>--> RunningProcess`.
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
        self._refill(self._properties, properties)

    @property
    def operations(self) -> List["Operation"]:
        return self._operations

    @operations.setter
    def operations(self, operations: List["Operation"]) -> None:
        self._refill(self._operations, operations)

    def load_source_facts(self, class_text: str) -> None:
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
        source = SourceText(class_text)
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

    def load_property(self, source: "Property") -> "Property":
        """A new property for this class's channel, filled from source."""
        from cdd_guidance.practices.clean_engineering.model.property import Property as PropertyNode

        loaded = PropertyNode(source.name, source.sequential_order)
        loaded.update_self(source)
        return loaded

    def load_operation(self, source: "Operation") -> "Operation":
        """A new operation for this class's channel, filled from source."""
        from cdd_guidance.practices.clean_engineering.model.operation import Operation as OperationNode

        loaded = OperationNode(source.name, source.sequential_order)
        loaded.update_self(source)
        return loaded

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(self.properties, source.properties, self.load_property),
            ChildCollectionPair(self.operations, source.operations, self.load_operation),
        ]

    def load_properties(self) -> None:
        while self.has_more_property():
            self.properties.append(self.load_next_property())

    def has_more_property(self) -> bool:
        return False

    def load_next_property(self) -> "Property":
        return self.get_next_property_from_file()

    def get_next_property_from_file(self) -> "Property":
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_property_from_file")

    def load_operations(self) -> None:
        while self.has_more_operation():
            operation = self.load_next_operation()
            self.operations.append(operation)

    def has_more_operation(self) -> bool:
        return False

    def load_next_operation(self) -> "Operation":
        operation = self.get_next_operation_from_file()
        operation.load_parameters()
        return operation

    def get_next_operation_from_file(self) -> "Operation":
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_operation_from_file")

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
        from cdd_guidance.practices.clean_engineering.model.type_refs import domain_type_names

        if (relationship.kind or "").lower() == "inheritance":
            return
        if (relationship.kind or "").lower() == "dependency":
            self.depend_on(relationship.target, relationship.label)
            return
        for prop in self.properties:
            if relationship.target not in domain_type_names(getattr(prop, "type_hint", "") or ""):
                continue
            if relationship.kind:
                prop.stereotype = relationship.kind
            if relationship.cardinality:
                prop.cardinality = relationship.cardinality
            if relationship.description and not getattr(prop, "origin", ""):
                prop.origin = relationship.description
            prop.derive_relationship()

    def depend_on(self, target: str, label: str) -> None:
        """Record that this class acts on target at run time, labelled by the interaction; the same pair and label once."""
        if any(item.target == target and item.label == label for item in self.dependencies):
            return
        self.dependencies.append(Relationship(target=target, kind="dependency", label=label))

    def load_relationships(self) -> None:
        while self.has_more_relationship():
            self.place_relationship(self.load_next_relationship())

    def has_more_relationship(self) -> bool:
        return False

    def load_next_relationship(self) -> Relationship:
        return self.get_next_relationship_from_file()

    def get_next_relationship_from_file(self) -> Relationship:
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_relationship_from_file")


class File(OoadNode):
    """A source file inside a module. Holds the properties and operations that sit
    at file scope rather than on a class."""

    _semantic_type_name = "File"

    def __init__(self, name: str, sequential_order: int) -> None:
        super().__init__(name, sequential_order)
        self.properties: List = []
        self.operations: List = []

    def update_self(self, source: OoadNode) -> None:
        self.name = source.name

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        return []


class Module(OoadNode):
    """A named module boundary grouping closely related classes."""

    _semantic_type_name = "Module"
    graph_facts = (
        "has_module_context",
        "has_bounded_context",
        "modules_heading",
        "model_blocks",
        "is_a_in_context",
        "child_parent_in_context",
        "public_source_internal",
        "public_source_files",
        "dependencies",
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
        self._modules = ModelChildren(self, "participants")
        self._classes = ModelChildren(self, "participants")
        self._class_blocks: List[str] = []

    @property
    def modules(self) -> List["Module"]:
        return self._modules

    @modules.setter
    def modules(self, modules: List["Module"]) -> None:
        self._refill(self._modules, modules)

    @property
    def classes(self) -> List[OoadClass]:
        return self._classes

    @classes.setter
    def classes(self, classes: List[OoadClass]) -> None:
        self._refill(self._classes, classes)

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

    def load(self) -> None:
        self.load_modules()
        self.load_classes()

    def load_modules(self) -> None:
        while self.has_more_module():
            self.append_module(self.load_next_module())

    def has_more_module(self) -> bool:
        return False

    def load_next_module(self) -> "Module":
        child = self.get_next_module_from_file()
        child.load()
        return child

    def get_next_module_from_file(self) -> "Module":
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_module_from_file")

    def append_module(self, module: "Module") -> None:
        self.modules.append(module)

    def append_class(self, oclass: OoadClass) -> None:
        self.classes.append(oclass)

    def load_classes(self) -> None:
        while self.has_more_class():
            self.append_class(self.load_next_class())

    def has_more_class(self) -> bool:
        return bool(self._class_blocks)

    def load_next_class(self) -> OoadClass:
        oclass = self.get_next_class_from_file()
        oclass.load_properties()
        oclass.load_operations()
        oclass.load_relationships()
        return oclass

    def get_next_class_from_file(self) -> OoadClass:
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_class_from_file")

    def load_source_facts(self, text: str, file: Path, root: Path) -> None:
        """Fill the facts one parsed source file owns: what it imports, which classes share it,
        and which of them carry the Entity or Aggregate Root stereotype, which may build the peers they own."""
        self.dependencies = self.import_targets(text, file, root)
        peer_names = [oclass.name for oclass in self.classes]
        for oclass in self.classes:
            oclass.peer_names = peer_names
            oclass.composes_peers = bool(_PEER_COMPOSING_STEREOTYPES & {item.lower() for item in oclass.stereotypes})

    def import_targets(self, text: str, file: Path, root: Path) -> List[str]:
        """Root-relative paths named by relative script imports (`./x`, `../y`)."""
        targets: List[str] = []
        for specifier in _SCRIPT_IMPORT.findall(text):
            resolved = (file.parent / specifier).resolve()
            if resolved.is_relative_to(root.resolve()):
                targets.append(resolved.relative_to(root.resolve()).as_posix())
        return targets

    def load_folder_facts(self, folder: Path) -> None:
        """Fill the facts a code folder owns: its context files and its own source files."""
        from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext

        module_context = ModuleContext(folder)
        content = module_context.read()
        sources = [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in _CODE_SUFFIXES]
        self.has_module_context = module_context.exists()
        self.has_bounded_context = (folder / ".context" / "bounded-context.md").is_file()
        self.modules_heading = module_context.has_modules_heading()
        self.model_blocks = module_context.model_blocks()
        self.is_a_in_context = bool(_IS_A.search(content))
        self.child_parent_in_context = bool(_CHILD_PARENT.search(content))
        self.public_source_internal = _internal_design_in(
            [path for path in sources if path.suffix == ".py" and not path.name.startswith("_")]
        )
        self.public_source_files = len([path for path in sources if not path.name.startswith(("_", "test_"))])

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, Module)
        return [
            ChildCollectionPair(
                self_children=self.modules,
                source_children=source.modules,
                load=self.load_module,
            ),
            ChildCollectionPair(
                self_children=self.classes,
                source_children=source.classes,
                load=self.load_class,
            ),
        ]


class CleanEngineeringModel(OoadNode):
    _semantic_type_name = "CleanEngineeringModel"

    def __init__(self, name: str | Graph = "", sequential_order: int = 1, graph: Optional[Graph] = None) -> None:
        opened = isinstance(name, Graph)
        if opened:
            graph = name
            name = "model"
        super().__init__(name, sequential_order, graph)
        self.path = ""
        self._modules = ModelChildren(self, "participants")
        if opened:
            self._copy_modules_on_graph()

    @property
    def modules(self) -> List[Module]:
        return self._modules

    @modules.setter
    def modules(self, modules: List[Module]) -> None:
        self._refill(self._modules, modules)

    def _copy_modules_on_graph(self) -> None:
        others = [
            node
            for node in self._copies_on_graph("CleanEngineeringModel")
            if getattr(node, "modules", None)
        ]
        if not others:
            return
        for module in others[0].modules:
            self.modules.append(module.clone())

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

    module_type: type = None  # type: ignore[assignment]

    def load(self, path: str) -> "CleanEngineeringModel":
        self.path = path
        self.modules = []
        self.load_content()
        self.load_modules()
        return self

    def save(self) -> str:
        raise NotImplementedError(f"{type(self).__name__} must implement save")

    def parse(self, text: str) -> "CleanEngineeringModel":
        raise NotImplementedError(f"{type(self).__name__} must implement parse")

    def sync(self, text: str, canonical: "CleanEngineeringModel") -> UpdateReport:
        """Bring canonical up to date with the model this channel reads from text."""
        return canonical.translate_from(self.parse(text))

    def load_content(self) -> None:
        return None

    def load_modules(self) -> None:
        while self.has_more_module():
            self.modules.append(self.load_next_module())

    def has_more_module(self) -> bool:
        return False

    def load_next_module(self) -> "Module":
        module = self.get_next_module_from_file()
        module.load()
        return module

    def get_next_module_from_file(self) -> "Module":
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_module_from_file")

    def load_module(self, source: Module) -> Module:
        return Module(name=source.name, sequential_order=source.sequential_order)

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, CleanEngineeringModel)
        return [
            ChildCollectionPair(
                self_children=self.modules,
                source_children=source.modules,
                load=self.load_module,
            )
        ]
