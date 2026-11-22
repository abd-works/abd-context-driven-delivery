"""A graph rule checks one loaded node using the practice model where possible."""

from __future__ import annotations

import copy

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.violation import Finding
    from harness.graph.rule_context import RuleCheckContext
    from harness.guidance.guidance import PracticeGuidance


# What a rule's text says of how it is decided, written into the practice's document from the rule's own property.
CHECKED = "Checked: the graph decides this rule, and what it finds is a violation."
JUDGED = "Judged: the graph only lists candidates for this rule, and a judge or a person reads each to decide."


def decided_values(rules: Iterable[PracticeGraphRule]) -> dict[str, str]:
    """How each of rules is decided, for the marker its text carries in its practice's document
    (``{{decided.verb_noun_format}}``, the slug with underscores): a practice adds these to its ``markdown_values``, so
    whether a rule is checked or judged is declared once, on the rule."""
    return {f"decided.{rule.slug.replace('-', '_')}": rule.how_decided for rule in rules if rule.slug}


class PracticeGraphRule:
    """The check of one graph rule: the node types it judges, and what it finds on one node (check) or across the whole
    practice (check_practice), each a *Finding* that names the node it was found on."""

    slug = ""
    node_types: tuple[str, ...] = ()
    requires_judge = False
    """Whether deciding the rule takes a reading no program can make, such as whether a name says what its story does.
    A rule that leaves this false is checked: its check decides, and what it finds is a violation. A rule that sets it
    is judged: its check only lists candidates for a judge or a person to read, and each is reported as a candidate,
    never as an error."""

    @property
    def how_decided(self) -> str:
        """What its rule text says of how it is decided: checked by the graph, or judged from the candidates it lists."""
        return JUDGED if self.requires_judge else CHECKED

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return []

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        """Optional whole-practice pass: each finding on the node it names."""
        return []

    def applies_to(self, node_type: str) -> bool:
        return node_type in self.node_types


class SharedPracticeGraphRule(PracticeGraphRule):
    """One rule an overlay checks on several practices' nodes, such as TDD's one-outcome-per-test on BDD observations
    and Stories Thens. It lives once, in the overlay's ``rules`` package; each practice runs a copy bound to its own
    node types. Its check reads only facts every practice it names records on its nodes."""

    node_types_by_practice: dict[type, tuple[str, ...]] = {}
    """Each practice's class to the node types the rule checks there."""

    def for_practice(self, practice: PracticeGuidance) -> PracticeGraphRule | None:
        """A copy whose node types are practice's, matched by its class; none for a practice it does not name."""
        node_types = next(
            (types for practice_class, types in self.node_types_by_practice.items() if isinstance(practice, practice_class)),
            None,
        )
        if node_types is None:
            return None
        bound = copy.copy(self)
        bound.node_types = node_types
        return bound
