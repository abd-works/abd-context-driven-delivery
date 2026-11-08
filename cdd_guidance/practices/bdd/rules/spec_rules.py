"""BDD spec rules — read the facts each spec and describe-tree node recorded on its graph node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.bdd.model.spec_source import reads_like_code
from cdd_guidance.practices.bdd.rules.layer_isolation import LayerIsolation
from cdd_guidance.practices.bdd.rules.observable_behavior import ObservableBehavior
from cdd_guidance.practices.bdd.rules.shared_describe_subject import SharedDescribeSubject
from cdd_guidance.practices.bdd.rules.tree_rules import (
    DescribeSubjectNotInternal,
    NoImplementation,
    OneAssertionPerTest,
    StateNotWhen,
)

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class PlainEnglishOnly(PracticeGraphRule):
    """Each describe and context judges its own text, so a hit lands on the block that reads like code."""

    slug = "describe-is-plain-english"
    node_types = ("Description", "Context")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if not reads_like_code(node.name or ""):
            return []
        return [f"{node.type} {node.name!r} reads like code, not plain English."]


class SignatureMarkers(PracticeGraphRule):
    slug = "framework-syntax"
    node_types = ("Spec",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if node.get_fact("signature_marker", True):
            return []
        return ["Spec file is missing a BDD: SIGNATURE marker."]


SPEC_RULES: tuple[PracticeGraphRule, ...] = (
    ObservableBehavior(),
    PlainEnglishOnly(),
    SignatureMarkers(),
    LayerIsolation(),
    SharedDescribeSubject(),
    DescribeSubjectNotInternal(),
    StateNotWhen(),
    OneAssertionPerTest(),
    NoImplementation(),
)
