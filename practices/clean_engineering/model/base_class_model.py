"""Canonical CleanEngineering class model - OoadNode base and typed nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

from practices.clean_engineering.model.field_types import Relationship
from practices.clean_engineering.model.update_report import ChildCollectionPair, TranslationError, UpdateReport

if TYPE_CHECKING:
    from practices.clean_engineering.model.operation import Operation
    from practices.clean_engineering.model.property import Property


_EXAMPLE_EXTENSION_PREFIXES = ("Fake", "Isolated", "Production")


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
        properties: List["Property"] | None = None,
        operations: List["Operation"] | None = None,
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
        self.properties: List["Property"] = properties if properties is not None else []
        self.operations: List["Operation"] = operations if operations is not None else []
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

    def clone(self) -> "OoadClass":
        cloned = type(self)(
            self.name,
            self.sequential_order,
            intent=self.intent,
            collaborators=list(self.collaborators),
            line=self.line,
        )
        cloned.docstring_parrots_name = self.docstring_parrots_name
        cloned.narration_comment_lines = list(self.narration_comment_lines)
        cloned.commented_code_lines = list(self.commented_code_lines)
        cloned.properties = [item.clone() for item in self.properties]
        cloned.operations = [item.clone() for item in self.operations]
        cloned.relationships = [item.clone() for item in self.relationships]
        cloned.property_nodes = [item.clone() for item in self.property_nodes]
        cloned.operation_nodes = [item.clone() for item in self.operation_nodes]
        return cloned

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

    def load_property_field(self, source: "Property") -> "Property":
        return self.load_property(source)

    def load_operation_field(self, source: "Operation") -> "Operation":
        return self.load_operation(source)

    def load_relationship(self, source: Relationship) -> Relationship:
        loaded = Relationship(target=source.target)
        loaded.update_self(source)
        return loaded

    def load_property(self, source: "Property") -> "Property":
        from practices.clean_engineering.model.property import Property as PropertyNode

        loaded = PropertyNode(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )
        loaded.access = getattr(source, "access", "both")
        loaded.stereotype = getattr(source, "stereotype", "") or ""
        loaded.cardinality = getattr(source, "cardinality", "") or ""
        loaded.origin = getattr(source, "origin", "") or ""
        loaded.invariants = [item.clone() for item in getattr(source, "invariants", [])]
        return loaded

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
        node.invariants = [item.clone() for item in getattr(source, "invariants", [])]
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

    def load_relationships(self) -> None:
        while self.has_more_relationship():
            self.relationships.append(self.load_next_relationship())

    def has_more_relationship(self) -> bool:
        return False

    def load_next_relationship(self) -> Relationship:
        return self.get_next_relationship_from_file()

    def get_next_relationship_from_file(self) -> Relationship:
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_relationship_from_file")

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
        self.properties = list(self.property_nodes)
        self.operations = list(self.operation_nodes)


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
        self.modules: List["Module"] = []
        self.classes: List[OoadClass] = []
        self._class_blocks: List[str] = []

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

    def __init__(self, name: str = "", sequential_order: int = 1) -> None:
        super().__init__(name, sequential_order)
        self.path = ""
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

    def clone(self) -> "CleanEngineeringModel":
        cloned = type(self)(self.name, self.sequential_order)
        for module in self.modules:
            cloned.modules.append(module.clone())
        return cloned

    module_type: type = None  # type: ignore[assignment]

    def load(self, path: str) -> "CleanEngineeringModel":
        self.path = path
        self.modules = []
        self.load_model_content()
        self.load_modules()
        return self

    def save(self) -> str:
        raise NotImplementedError(f"{type(self).__name__} must implement save")

    def load_model_content(self) -> None:
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


class CleanEngineeringModelFactory:
    """Pick the channel model from a file or a folder and return a CleanEngineeringModel."""

    @staticmethod
    def load(path: str) -> CleanEngineeringModel:
        from pathlib import Path

        target = Path(path)
        if target.is_dir() or target.suffix.lower() == ".py":
            from practices.clean_engineering.model.python.python_class_model import (
                PythonCleanEngineeringModel,
            )

            model = PythonCleanEngineeringModel()
            if target.is_file():
                return model.parse(target.read_text(encoding="utf-8"))
            return model.load(str(target))
        text = target.read_text(encoding="utf-8")
        suffix = target.suffix.lower()
        if suffix == ".drawio":
            from practices.clean_engineering.model.drawio.drawio_class_model import (
                DrawIOCleanEngineeringModel,
            )

            return DrawIOCleanEngineeringModel().load(text)
        if suffix == ".json":
            from practices.clean_engineering.model.json.json_class_model import (
                JsonCleanEngineeringModel,
            )

            return JsonCleanEngineeringModel().parse(text)
        if suffix in {".svg", ".html"}:
            from practices.clean_engineering.model.miro.miro_class_model import (
                MiroCleanEngineeringModel,
            )

            return MiroCleanEngineeringModel().load(text)
        from practices.clean_engineering.model.markdown.markdown_class_model import (
            MarkdownCleanEngineeringModel,
        )

        loaded = MarkdownCleanEngineeringModel()
        loaded.path = str(target)
        return loaded.load(str(target))


def __getattr__(name: str):
    if name == "Property":
        from practices.clean_engineering.model.property import Property

        return Property
    if name in ("Operation", "Parameter"):
        from practices.clean_engineering.model.operation import Operation, Parameter

        return Operation if name == "Operation" else Parameter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
