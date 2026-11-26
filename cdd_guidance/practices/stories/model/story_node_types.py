"""Stories' node types as the graph's shared tables ask them: the relationships a story node's evidence decides, and
the story map's types a session's stories scope."""
from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_node_types import PracticeNodeTypes

from cdd_guidance.practices.clean_engineering.reading.node_evidence import NodeEvidence
from cdd_guidance.practices.stories.model.story_tree import EXAMPLE_TYPE, STORY_MAP_TYPES

if TYPE_CHECKING:
    from harness.graph.model_node import ModelNode


class StoryNodeTypes(PracticeNodeTypes):
    """Stories' node types. A step ``invokes`` the operations its source calls, ``observes`` and ``demonstrates`` what it
    names, and is ``retrievedUsing`` a property it reads or calls; an epic ``uses`` a module whose classes its examples
    name or whose members its steps call; a story is ``specifiedBy`` what bears its name; and a scenario's ``given`` is
    one of its own Given steps. A session that names its stories scopes every node of the story map itself. A schema's
    ``subEpic`` is an ``Epic``, and its ``given``, ``when`` and ``then`` are each a ``Step``."""

    schema_node_types = {"subEpic": "Epic", "given": "Step", "when": "Step", "then": "Step"}
    child_lists = frozenset({"decomposedInto", "background", "scenarios", "steps", "examples", "increments", "stories", "ands"})
    edge_order = {
        "decomposedInto": 1, "background": 2, "given": 2, "scenarios": 3, "steps": 4, "demonstrates": 4, "shownOn": 4,
        "specifiedBy": 4, "examples": 5, "increments": 6, "stories": 7, "observes": 8, "ands": 9, "uses": 9,
        "retrievedUsing": 11, "invokes": 12,
    }
    evidence_kinds = frozenset({"invokes", "observes", "demonstrates", "retrievedUsing", "uses", "specifiedBy", "given"})
    scope_types = STORY_MAP_TYPES

    def links(self, owner: ModelNode, kind: str, target: ModelNode) -> bool:
        evidence = NodeEvidence(owner)
        if kind == "invokes":
            return evidence.invokes(target.name)
        if kind in {"observes", "demonstrates"}:
            return evidence.mentions(target.name)
        if kind == "retrievedUsing":
            return evidence.reads(target.name) or evidence.calls(target.name)
        if kind == "uses":
            return self._epic_uses(owner, target)
        if kind == "specifiedBy":
            return owner.name.casefold() == target.name.casefold()
        if kind == "given":
            return target.semantic_type() == "Step" and target.phase == "given" and target in list(getattr(owner, "steps", []) or [])
        return False

    def _epic_uses(self, epic: ModelNode, module: ModelNode) -> bool:
        """True when an epic's examples name a class of the module, or its steps call one of the module's members."""
        if epic.semantic_type() != "Epic" or module.semantic_type() != "Module":
            return False
        members = [node for node in module.subtree() if NodeEvidence(node).module is module]
        classes = [node for node in members if node.semantic_type() == "OoadClass"]
        operations = [node for node in members if node.semantic_type() in {"Operation", "Property"}]
        for node in epic.subtree():
            evidence = NodeEvidence(node)
            if node.semantic_type() == EXAMPLE_TYPE and any(evidence.mentions(found.name) for found in classes):
                return True
            if node.semantic_type() == "Step" and any(evidence.invokes(member.name) for member in operations):
                return True
        return False
