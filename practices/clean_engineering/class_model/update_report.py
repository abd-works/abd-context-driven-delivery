"""UpdateReport, ChildCollectionPair and supporting types for CleanEngineering model reconciliation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from clean_engineering.class_model.base_class_model import OoadNode


class TranslationError(Exception):
    """Raised when translate_from is called with an incompatible source."""


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


@dataclass
class ChildCollectionPair:
    self_children: List["OoadNode"]
    source_children: List["OoadNode"]
    create_child: Callable[["OoadNode"], "OoadNode"]


@dataclass
class UpdateReport:
    changes: List[Change] = field(default_factory=list)

    def add_exact_match(self, name: str) -> None:
        self.changes.append(Change(kind=ChangeKind.EXACT_MATCH, from_name=name, to_name=name))

    def add_new(self, node: "OoadNode", parent_name: Optional[str] = None) -> None:
        self.changes.append(Change(kind=ChangeKind.ADD, node_name=node.name, parent_name=parent_name))

    def add_removed(self, node: "OoadNode", parent_name: Optional[str] = None) -> None:
        self.changes.append(Change(kind=ChangeKind.REMOVE, node_name=node.name, parent_name=parent_name))

    def adds(self) -> List[Change]:
        return [c for c in self.changes if c.kind == ChangeKind.ADD]

    def removes(self) -> List[Change]:
        return [c for c in self.changes if c.kind == ChangeKind.REMOVE]
