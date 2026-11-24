"""What a model object's source shows, and the relationships Clean Engineering's nodes are linked by from it."""
from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING

from harness.graph.practice_node_types import PracticeNodeTypes

if TYPE_CHECKING:
    from harness.graph.model_node import ModelNode


class NodeEvidence:
    """What a model object's source shows: the names it mentions, calls, and reads, and the module it sits in. Clean
    Engineering's node types read it, and so do the practices that link their nodes to its code, such as Stories'
    steps."""

    def __init__(self, node: ModelNode) -> None:
        self.node = node

    @cached_property
    def text(self) -> str:
        source = getattr(self.node, "source", None)
        stored = getattr(source, "__dict__", {}).get("text") if source is not None else None
        return stored if isinstance(stored, str) else ""

    @property
    def callees(self) -> list[str]:
        return list(getattr(self.node, "callees", []) or [])

    def mentions(self, name: str) -> bool:
        return bool(self.text and name) and re.search(rf"\b{re.escape(name)}\b", self.text) is not None

    def reads(self, name: str) -> bool:
        """True when the source reads a property called name: ``.name`` not followed by a call."""
        return bool(self.text and name) and re.search(rf"\.{re.escape(name)}\b(?!\s*\()", self.text) is not None

    def calls(self, name: str) -> bool:
        """True when the source, or the source of a step under it, calls name."""
        if not self.text or not name:
            return False
        text = "\n".join([self.text, *(NodeEvidence(step).text for step in self._steps_under())])
        return re.search(rf"(?<![\w]){re.escape(name)}\s*\(", text) is not None

    def invokes(self, name: str) -> bool:
        return self.calls(name) or name in self.callees

    @property
    def module(self) -> ModelNode | None:
        """The Module node this object sits under, through its parents; none when it sits under none."""
        current, seen = self.node, set()
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if getattr(current, "semantic_type", lambda: "")() == "Module":
                return current
            current = getattr(current, "parent", None)
        return None

    def _steps_under(self) -> list[ModelNode]:
        if not hasattr(self.node, "subtree"):
            return []
        return [node for node in self.node.subtree() if node is not self.node and node.semantic_type() == "Step"]


class CodeNodeTypes(PracticeNodeTypes):
    """Clean Engineering's node types: an operation ``invokes`` what its source calls, a class ``dependsOn`` the
    collaborators and dependencies it names, and a property or operation ``hasType`` or ``returnType`` the class its
    type hint or return type names. A schema's ``class`` is an ``OoadClass``; a class lists its members and an operation
    its parameters."""

    schema_node_types = {"class": "OoadClass"}
    child_lists = frozenset({"participants", "parameters"})
    edge_order = {
        "participants": 1, "parameters": 2, "properties": 3, "hasParameter": 6, "hasType": 7, "returnType": 7,
        "demonstratedThrough": 8, "invokedBy": 9, "returns": 10, "invokes": 12, "dependsOn": 13, "usedBy": 14,
    }
    evidence_kinds = frozenset({"invokes", "dependsOn", "hasType", "returnType"})

    def links(self, owner: ModelNode, kind: str, target: ModelNode) -> bool:
        if kind == "invokes":
            return NodeEvidence(owner).invokes(target.name)
        if kind == "dependsOn":
            return target.name in [*(getattr(owner, "collaborators", []) or []), *(getattr(owner, "dependencies", []) or [])]
        if kind in {"hasType", "returnType"}:
            hint = getattr(owner, "type_hint" if kind == "hasType" else "return_type", "") or ""
            return re.search(rf"\b{re.escape(target.name)}\b", str(hint)) is not None if target.name else False
        return False
