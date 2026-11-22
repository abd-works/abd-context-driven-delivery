"""The node types of one practice as the graph's shared tables ask them: the part of a practice's reading that answers
which relationships a node's evidence decides and whether one holds, and which of its types a session's stories scope."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.model_node import ModelNode


class PracticeNodeTypes:
    """What one practice says of its node types to the graph: the relationships whose edges a node's evidence decides,
    such as a step that ``invokes`` the operation its source calls (``evidence_kinds``), whether one holds between two
    nodes (``links``), and the types whose nodes a session's stories scope (``scope_types``), which a validate of a
    session working on some stories leaves out when they lie outside those stories. A practice's reading holds one
    (``PracticeReading.types``); one that names none takes this, which decides no relationship by evidence and scopes
    nothing by stories. Every other relationship a schema names is the nodes the owner holds in the list named for it."""

    evidence_kinds: frozenset[str] = frozenset()
    """The relationships a node of the practice is linked by from its evidence: its source text, the names it calls,
    and its type hints."""

    scope_types: frozenset[str] = frozenset()
    """The node types a session that names its stories scopes: a node of one of these that lies outside every story the
    session names is another increment's work."""

    def links(self, owner: ModelNode, kind: str, target: ModelNode) -> bool:
        """Whether owner, one of the practice's nodes, is linked to target by kind, one of ``evidence_kinds``, as its
        evidence shows; never, unless the practice says."""
        return False
