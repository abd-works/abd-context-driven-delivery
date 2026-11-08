"""OoadNode — the base of every Clean Engineering model object: a module, a class, a member, a parameter, an invariant.

It sits in its own module so the members (``property``, ``operation``) and the classes and modules that hold them
(``base_class_model``) all build on it, and the dependency runs one way: ``base_class_model`` imports the members, and
no member imports ``base_class_model``."""

from __future__ import annotations

from typing import Optional

from harness.graph.graph import Graph
from harness.graph.model_node import ModelNode

from cdd_guidance.practices.clean_engineering.model.translation import TranslationError


class OoadNode(ModelNode):
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

    def translate_from(self, source: "OoadNode") -> None:
        """Become source, which is this node's kind or a kind built on it, such as a DDD entity for a class."""
        kinds = {getattr(kind, "_semantic_type_name", None) for kind in type(source).__mro__}
        if self.semantic_type() not in kinds:
            raise TranslationError(
                f"Cannot translate from {source.semantic_type()} into {self.semantic_type()}"
            )
        self.update_self(source)
        self.reconcile_children(source)

    def update_self(self, source: "OoadNode") -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement update_self")

    def reconcile_children(self, source: "OoadNode") -> None:
        """Make each child list this node holds the matching list of source's; a node with no children has none."""

    def declares(self, member: "OoadNode") -> bool:
        """True when member is one of this node's own operations or properties; only a class declares members."""
        return False
