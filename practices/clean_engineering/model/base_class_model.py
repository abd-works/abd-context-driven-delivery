"""Canonical CleanEngineering class model - OoadNode base and typed nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

from practices.clean_engineering.model.field_types import OperationField, PropertyField, Relationship
from practices.clean_engineering.model.update_report import ChildCollectionPair, TranslationError, UpdateReport

if TYPE_CHECKING:
    from practices.clean_engineering.model.operation import Operation
    from practices.clean_engineering.model.property import Property

# Legacy aliases — format channels still emit field rows, not tree nodes.
Property = PropertyField
Operation = OperationField


_EXAMPLE_EXTENSION_PREFIXES = ("Fake", "Isolated", "Production")
_EXAMPLE_FACTORY_SUFFIX = "ExampleFactory"


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
    if is_example_factory_name(name):
        core = name[: -len(_EXAMPLE_FACTORY_SUFFIX)]
        return production_name_for(core) if is_interface_name(core) else core
    return production_name_for(name)


def is_example_factory_name(name: str) -> bool:
    """True for {Type}ExampleFactory or I{Type}ExampleFactory."""
    return name.endswith(_EXAMPLE_FACTORY_SUFFIX) and len(name) > len(_EXAMPLE_FACTORY_SUFFIX)


def example_factory_name_for(type_name: str) -> str:
    """Cart or ICart -> CartExampleFactory."""
    return f"{base_type_name_for(type_name)}{_EXAMPLE_FACTORY_SUFFIX}"


def companion_interface_name(class_name: str, known_names: Iterable[str]) -> str | None:
    """If class_name has a sibling I{Class} in known_names, return that name.

    Resolves production Class -> IClass and Fake|Isolated|Production{Type} -> I{Type}.
    """
    if is_interface_name(class_name) or is_example_factory_name(class_name):
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


def ensure_example_factory_family(module: "Module", type_name: str) -> list["OoadClass"]:
    """Ensure I{Type}, production {Type}, and {Type}ExampleFactory exist.

    Does **not** add Fake/Isolated/Production subclasses - those are factory modes
    (mock framework / ctor injection / real collaborators), not types.
    ``type_name`` may be Cart, ICart, or a legacy FakeCart name (base is stripped).
    Returns the classes that were added.
    """
    base = base_type_name_for(type_name)
    iface = interface_name_for(base)
    factory = example_factory_name_for(base)
    wanted: list[tuple[str, str]] = [
        (iface, f"Public seam for {base}."),
        (base, f"Production {base} implementing {iface}."),
        (
            factory,
            f"Loads examples[{{example_key}}] - Fake via mock framework; "
            f"Isolated via {base} ctor injection; Production via real {base}.",
        ),
    ]
    existing = {c.name for c in module.classes}
    added: list[OoadClass] = []
    order = max((c.sequential_order for c in module.classes), default=0) + 1
    for name, intent in wanted:
        if name in existing:
            continue
        oclass = module.load_class(
            OoadClass(name=name, sequential_order=order, intent=intent)
        )
        oclass.intent = intent
        if name == factory:
            oclass.operations = [
                OperationField(name="load_example_key", parameters=[], return_type=iface)
            ]
        module.classes.append(oclass)
        added.append(oclass)
        existing.add(name)
        order += 1
    return added


class OoadNode:
    _semantic_type_name: str = "OoadNode"

    def __init__(self, name: str, sequential_order: int) -> None:
        self.name = name
        self.sequential_order = sequential_order

    def semantic_type(self) -> str:
        return self._semantic_type_name

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

    def __init__(
        self,
        name: str,
        sequential_order: int,
        intent: str = "",
        properties: List[PropertyField] | None = None,
        operations: List[OperationField] | None = None,
        relationships: List[Relationship] | None = None,
        collaborators: List[str] | None = None,
        line: int | None = None,
    ) -> None:
        super().__init__(name, sequential_order)
        self.intent = intent
        self.line = line
        self.docstring_parrots_name: bool = False
        self.narration_comment_lines: List[int] = []
        self.commented_code_lines: List[int] = []
        self.properties: List[PropertyField] = properties if properties is not None else []
        self.operations: List[OperationField] = operations if operations is not None else []
        self.relationships: List[Relationship] = relationships if relationships is not None else []
        self.collaborators: List[str] = collaborators if collaborators is not None else []
        self.property_nodes: List["Property"] = []
        self.operation_nodes: List["Operation"] = []

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, OoadClass)
        self.intent = source.intent
        self.properties = list(source.properties)
        self.operations = list(source.operations)
        self.relationships = list(source.relationships)
        self.collaborators = list(source.collaborators)
        if not source.property_nodes and not source.operation_nodes:
            self.sync_tree_from_legacy()
        elif not source.properties and not source.operations:
            self.sync_legacy_from_tree()

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "sequentialOrder": self.sequential_order,
            "intent": self.intent,
            "properties": [item.as_record() for item in self.properties],
            "operations": [item.as_record() for item in self.operations],
            "relationships": [item.as_record() for item in self.relationships],
            "collaborators": list(self.collaborators),
        }

    def load_property_field(self, source: PropertyField) -> PropertyField:
        loaded = PropertyField(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation_field(self, source: OperationField) -> OperationField:
        loaded = OperationField(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_relationship(self, source: Relationship) -> Relationship:
        loaded = Relationship(target=source.target)
        loaded.update_self(source)
        return loaded

    def load_property(self, source: "Property") -> "Property":
        from practices.clean_engineering.model.property import Property as PropertyNode

        return PropertyNode(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: "Operation") -> "Operation":
        from practices.clean_engineering.model.operation import Operation as OperationNode

        node = OperationNode(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        return node

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(
                self_children=self.property_nodes,
                source_children=source.property_nodes,
                load=self.load_property,
            ),
            ChildCollectionPair(
                self_children=self.operation_nodes,
                source_children=source.operation_nodes,
                load=self.load_operation,
            ),
        ]

    def sync_tree_from_legacy(self) -> None:
        from practices.clean_engineering.model.operation import Operation as OperationNode
        from practices.clean_engineering.model.property import Property as PropertyNode

        self.property_nodes = [
            PropertyNode.from_field(field, index)
            for index, field in enumerate(self.properties, start=1)
        ]
        self.operation_nodes = [
            OperationNode.from_field(field, index)
            for index, field in enumerate(self.operations, start=1)
        ]

    def sync_legacy_from_tree(self) -> None:
        self.properties = [node.to_field() for node in self.property_nodes]
        self.operations = [node.to_field() for node in self.operation_nodes]


class Module(OoadNode):
    """A named module boundary grouping closely related classes."""

    _semantic_type_name = "Module"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        description: str = "",
        seam: str = "",
        constraint: str = "",
        seam_terms: List[str] | None = None,
        dependencies: List[str] | None = None,
    ) -> None:
        super().__init__(name, sequential_order)
        self.description = description
        self.seam = seam
        self.constraint = constraint
        self.seam_terms: List[str] = list(seam_terms) if seam_terms is not None else []
        self.dependencies: List[str] = list(dependencies) if dependencies is not None else []
        self.classes: List[OoadClass] = []

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

    def load_class(self, source: OoadClass) -> OoadClass:
        return OoadClass(name=source.name, sequential_order=source.sequential_order)

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, Module)
        return [
            ChildCollectionPair(
                self_children=self.classes,
                source_children=source.classes,
                load=self.load_class,
            )
        ]


class CleanEngineeringModel(OoadNode):
    _semantic_type_name = "CleanEngineeringModel"

    def __init__(self, name: str = "", sequential_order: int = 1) -> None:
        super().__init__(name, sequential_order)
        self.modules: List[Module] = []

    @property
    def classes(self) -> List[OoadClass]:
        """Flat view of all classes across all modules - for backward compat."""
        return [cls for module in self.modules for cls in module.classes]

    def as_record(self) -> dict:
        if self.modules:
            return {
                "name": self.name,
                "modules": [module.as_record() for module in self.modules],
            }
        return {
            "name": self.name,
            "classes": [loaded.as_record() for loaded in self.classes],
        }

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, CleanEngineeringModel)
        self.name = source.name

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
