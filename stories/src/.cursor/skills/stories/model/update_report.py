"""UpdateReport, NodeSnapshot, ChildCollectionPair and supporting types.

Produced by StoryNode.translate_from; reversible via UpdateReport.reverse_on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from .story_node import StoryNode


class TranslationError(Exception):
    """Raised when translate_from or reverse is called with an invalid source/report."""


class ChangeKind(str, Enum):
    EXACT_MATCH = "exact_match"
    RENAME = "rename"
    ADD = "add"
    REMOVE = "remove"
    REORDER = "reorder"


@dataclass(frozen=True)
class Change:
    kind: ChangeKind
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    node_name: Optional[str] = None
    parent_name: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class ChildCollectionPair:
    """A pair of self/source child lists plus the factory that creates fresh children.

    self_children is a live reference — reconcileCollection mutates it in place so the
    change persists on the owning node.
    """

    self_children: List["StoryNode"]
    source_children: List["StoryNode"]
    create_child: Callable[["StoryNode"], "StoryNode"]


@dataclass
class NodeSnapshot:
    """Recursive before-state of a StoryNode captured at the start of translate_from.

    Immutable value: two snapshots with the same fields are interchangeable.
    """

    node_id: int  # identity of the captured node — used to guard reverse against a foreign report
    name: str
    sequential_order: int
    extra_fields: dict = field(default_factory=dict)
    child_snapshots: List["NodeSnapshot"] = field(default_factory=list)

    @classmethod
    def of(cls, node: "StoryNode") -> "NodeSnapshot":
        return cls(
            node_id=id(node),
            name=node.name,
            sequential_order=node.sequential_order,
            extra_fields=node.snapshot_fields(),
            child_snapshots=[cls.of(child) for child in node.children()],
        )

    def restore_into(self, node: "StoryNode") -> None:
        node.name = self.name
        node.sequential_order = self.sequential_order
        node.restore_snapshot_fields(self.extra_fields)
        children = node.children()
        for i, child_snapshot in enumerate(self.child_snapshots):
            if i < len(children):
                child_snapshot.restore_into(children[i])


@dataclass
class UpdateReport:
    """Ordered log of adds, removes, renames, exact matches, and reorders from one
    translate_from call, plus a NodeSnapshot for reversal.
    """

    changes: List[Change] = field(default_factory=list)
    snapshot: Optional[NodeSnapshot] = None
    owning_node_id: Optional[int] = None

    def capture_snapshot(self, node: "StoryNode") -> None:
        self.snapshot = NodeSnapshot.of(node)
        self.owning_node_id = id(node)

    def add_exact_match(self, self_name: str, source_name: str) -> None:
        self.changes.append(
            Change(kind=ChangeKind.EXACT_MATCH, from_name=self_name, to_name=source_name)
        )

    def add_rename(self, from_name: str, to_name: str, confidence: float) -> None:
        self.changes.append(
            Change(
                kind=ChangeKind.RENAME,
                from_name=from_name,
                to_name=to_name,
                confidence=confidence,
            )
        )

    def add_new(self, node: "StoryNode", parent_name: Optional[str] = None) -> None:
        self.changes.append(
            Change(kind=ChangeKind.ADD, node_name=node.name, parent_name=parent_name)
        )

    def add_removed(self, node: "StoryNode", parent_name: Optional[str] = None) -> None:
        self.changes.append(
            Change(kind=ChangeKind.REMOVE, node_name=node.name, parent_name=parent_name)
        )

    def add_reorder(self, from_name: str, to_name: str) -> None:
        self.changes.append(
            Change(kind=ChangeKind.REORDER, from_name=from_name, to_name=to_name)
        )

    def reverse_on(self, node: "StoryNode") -> None:
        if self.owning_node_id is None or id(node) != self.owning_node_id:
            raise TranslationError(
                "reverse must be called on the node that produced the report"
            )
        if self.snapshot is None:
            raise TranslationError("report has no snapshot to reverse from")
        self.snapshot.restore_into(node)

    def has_changes(self) -> bool:
        return any(c.kind != ChangeKind.EXACT_MATCH for c in self.changes)

    def adds(self) -> List[Change]:
        return [c for c in self.changes if c.kind == ChangeKind.ADD]

    def removes(self) -> List[Change]:
        return [c for c in self.changes if c.kind == ChangeKind.REMOVE]

    def renames(self) -> List[Change]:
        return [c for c in self.changes if c.kind == ChangeKind.RENAME]

    def reorders(self) -> List[Change]:
        return [c for c in self.changes if c.kind == ChangeKind.REORDER]
