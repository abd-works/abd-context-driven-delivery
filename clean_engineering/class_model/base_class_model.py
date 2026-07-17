"""Canonical CleanEngineering class model — OoadNode base and typed nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from clean_engineering.class_model.update_report import ChildCollectionPair, TranslationError, UpdateReport


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
                new_child = pair.create_child(source_child)
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


@dataclass
class Property:
    name: str
    type_hint: str = ""
    description: str = ""


@dataclass
class Operation:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    description: str = ""
    # Code facts — filled by language channel parse; formats may omit on render.
    line: int | None = None
    line_count: int = 0
    nesting_depth: int = 0
    callees: List[str] = field(default_factory=list)
    literals: List[str] = field(default_factory=list)
    param_count: int = 0
    has_calculation: bool = False
    has_validation: bool = False
    bare_except_lines: List[int] = field(default_factory=list)
    swallowed_except_lines: List[int] = field(default_factory=list)
    assigned_names: List[tuple[str, int]] = field(default_factory=list)
    loop_target_names: List[tuple[str, int]] = field(default_factory=list)
    body_fingerprint: str = ""
    constructed_types: List[tuple[str, int]] = field(default_factory=list)
    public_attr_assigns: List[tuple[str, int]] = field(default_factory=list)
    is_property: bool = False
    returns_private_attr: bool = False
    magic_numbers: List[tuple[float, int]] = field(default_factory=list)
    docstring_parrots_name: bool = False


@dataclass
class Relationship:
    target: str
    kind: str = ""
    cardinality: str = ""
    description: str = ""


class OoadClass(OoadNode):
    _semantic_type_name = "OoadClass"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        intent: str = "",
        properties: List[Property] | None = None,
        operations: List[Operation] | None = None,
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
        self.properties: List[Property] = properties if properties is not None else []
        self.operations: List[Operation] = operations if operations is not None else []
        self.relationships: List[Relationship] = relationships if relationships is not None else []
        self.collaborators: List[str] = collaborators if collaborators is not None else []

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, OoadClass)
        self.intent = source.intent
        self.properties = list(source.properties)
        self.operations = list(source.operations)
        self.relationships = list(source.relationships)
        self.collaborators = list(source.collaborators)

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        return []


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
    ) -> None:
        super().__init__(name, sequential_order)
        self.description = description
        self.seam = seam
        self.constraint = constraint
        self.classes: List[OoadClass] = []

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, Module)
        self.description = source.description
        self.seam = source.seam
        self.constraint = source.constraint

    def create_child_class(self, source: OoadClass) -> OoadClass:
        return OoadClass(name=source.name, sequential_order=source.sequential_order)

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, Module)
        return [
            ChildCollectionPair(
                self_children=self.classes,
                source_children=source.classes,
                create_child=self.create_child_class,
            )
        ]


class CleanEngineeringModel(OoadNode):
    _semantic_type_name = "CleanEngineeringModel"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name, sequential_order)
        self.modules: List[Module] = []

    @property
    def classes(self) -> List[OoadClass]:
        """Flat view of all classes across all modules — for backward compat."""
        return [cls for module in self.modules for cls in module.classes]

    def update_self(self, source: "OoadNode") -> None:
        assert isinstance(source, CleanEngineeringModel)
        self.name = source.name

    def create_child_module(self, source: Module) -> Module:
        return Module(name=source.name, sequential_order=source.sequential_order)

    def child_collections(self, source: "OoadNode") -> List[ChildCollectionPair]:
        assert isinstance(source, CleanEngineeringModel)
        return [
            ChildCollectionPair(
                self_children=self.modules,
                source_children=source.modules,
                create_child=self.create_child_module,
            )
        ]
