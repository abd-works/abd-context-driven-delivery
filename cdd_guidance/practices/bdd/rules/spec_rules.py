"""BDD spec rules — read the facts each spec and describe-tree node recorded on its graph node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.bdd.rules.layer_isolation import LayerIsolation
from cdd_guidance.practices.bdd.rules.observable_behavior import ObservableBehavior
from cdd_guidance.practices.bdd.rules.shared_describe_subject import SharedDescribeSubject
from cdd_guidance.practices.bdd.rules.tree_rules import (
    DescribeSubjectNotInternal,
    NoImplementation,
    OneAssertionPerTest,
    StateNotWhen,
)


class PlainEnglishOnly(PracticeGraphRule):
    slug = "describe-is-plain-english"
    node_types = ("Spec",)

    def check(self, node, context) -> list[str]:
        return [
            f"Line {line}: describe/it text looks like code, not plain English."
            for line in node.get_fact("code_like_describe_lines", [])
        ][:1]


class SignatureMarkers(PracticeGraphRule):
    slug = "framework-syntax"
    node_types = ("Spec",)

    def check(self, node, context) -> list[str]:
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
