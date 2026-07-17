"""UpdateReport and ChildCollectionPair for UxNode reconciliation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from .ux_node import UxNode


class TranslationError(Exception):
    """Raised when translate_from is called with an incompatible source."""


class ChangeKind(str, Enum):
    EXACT_MATCH = "exact_match"
    ADD = "add"
    REMOVE = "remove"


@dataclass(frozen=True)
class Change:
    kind: ChangeKind
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    node_name: Optional[str] = None
    parent_name: Optional[str] = None


@dataclass
class ChildCollectionPair:
    self_children: List["UxNode"]
    source_children: List["UxNode"]
    create_child: Callable[["UxNode"], "UxNode"]


@dataclass
class UpdateReport:
    changes: List[Change] = field(default_factory=list)

    def add_exact_match(self, name: str) -> None:
        self.changes.append(Change(kind=ChangeKind.EXACT_MATCH, from_name=name, to_name=name))

    def add_new(self, node: "UxNode", parent_name: Optional[str] = None) -> None:
        self.changes.append(
            Change(kind=ChangeKind.ADD, node_name=node.name, parent_name=parent_name)
        )

    def add_removed(self, node: "UxNode", parent_name: Optional[str] = None) -> None:
        self.changes.append(
            Change(kind=ChangeKind.REMOVE, node_name=node.name, parent_name=parent_name)
        )
