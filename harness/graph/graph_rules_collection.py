"""The rules that apply to one graph node, in the same collection shape as a practice's guidance rules. In the
explorer tree the collection is the node's rules entry and each rule is a child of it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.guidance.rule import Rule, RulesCollection
from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.location import Location
from harness.graph.violation import NodeViolation, Violation
from harness.installation.data_class import data_field

if TYPE_CHECKING:
    from harness.graph.graph import Filter, Node
    from harness.graph.rule_context import RuleCheckContext


class GraphRule(Rule):
    """One schema rule on one node: its slug, its prose, the graph check that runs it when one exists, whether that
    check runs here, and the violations it found there. It is a guidance rule held on a node; the check is a part it
    holds, not a kind of rule it is."""

    def __init__(self, node: Node, slug: str, check: PracticeGraphRule | None = None) -> None:
        """The rule slug on node, with the prose node's schema gives it, run by check when one exists."""
        super().__init__(slug=slug, body=node.schema.rule_prose.get(slug, ""))
        self.node = node
        self._check = check
        self.executable = check is not None
        self.runs = check is not None and any(check.applies_to(type_name) for type_name in self._applying_types())
        """Whether its check runs on this node: the check applies to the node's type, or to the type it is anchored to."""
        self._violations: list[Violation] = []

    def check(self, context: RuleCheckContext) -> list[str]:
        """The messages its check finds on its node; none when no check runs it."""
        return self._check.check(self.node, context) if self._check is not None else []

    def _applying_types(self) -> set[str]:
        """The node types whose checks apply to this rule's node: its own, and the type of the extended practice it is
        anchored to, such as a Clean Engineering class for a DDD entity."""
        node = self.node
        anchor = node.schema.anchor_type(node.type)
        return {node.type, anchor} if anchor else {node.type}

    @property
    @data_field
    def type(self) -> str:
        return "Rule"

    @property
    @data_field
    def name(self) -> str:
        return self.slug

    @property
    @data_field
    def node_id(self) -> str:
        return f"{self.node.node_id}:rules:{self.slug}"

    @property
    @data_field
    def children(self) -> list[GraphRule]:
        """None: a rule is a leaf of the explorer tree."""
        return []

    @property
    @data_field
    def status(self) -> str:
        """``violating`` when it found a violation here, ``prompt`` when no check runs it, else ``passing``."""
        if self._violations:
            return "violating"
        return "passing" if self.executable else "prompt"

    @property
    @data_field
    def violations(self) -> list[Violation]:
        return list(self._violations)

    def record(self, message: str) -> None:
        """Keep message as a violation of this rule at the node's place in its file; the same message is kept once."""
        violation = NodeViolation.at_node(self, message)
        if violation.message and all(kept.message != violation.message for kept in self._violations):
            self._violations.append(violation)

    def restore(self, violation: Violation) -> None:
        """Keep a violation a saved graph recorded, at the place it was saved with, as this rule's own."""
        restored = NodeViolation(self, violation.message, Location(violation.location, violation.line, violation.end_line))
        if restored not in self._violations:
            self._violations.append(restored)

    @property
    def is_failing(self) -> bool:
        return bool(self._violations)


class GraphRulesCollection(RulesCollection):
    """Schema rules for one node. Violations live on each GraphRule entry."""

    def __init__(self, node: Node, entries: dict[str, GraphRule] | None = None, kept: list[GraphRule] | None = None) -> None:
        super().__init__(entries)
        self.node = node
        # The rules a node filter kept under the node, when one did; otherwise the graph's own filter decides.
        self._kept = kept

    @classmethod
    def from_node(cls, node: Node) -> GraphRulesCollection:
        """The rules node's schema gives its type, with the overlays that add their rules to node, each with its prose,
        the check that runs it when one exists, and whether that check applies to node: the checks of node's practice,
        of the practice it extends, and of each pattern overlay its graph applies."""
        checks = dict(node.practice.reading.checks())
        return cls(node, {slug: GraphRule(node, slug, checks.get(slug)) for slug in node.schema.for_node(node).slugs_for(node.type)})

    @property
    @data_field
    def type(self) -> str:
        return "rules"

    @property
    @data_field
    def name(self) -> str:
        return "rules"

    @property
    @data_field
    def node_id(self) -> str:
        return f"{self.node.node_id}:rules"

    @property
    @data_field
    def children(self) -> list[GraphRule]:
        """The rules the graph's filter shows under the node."""
        return self.shown

    @property
    def shown(self) -> list[GraphRule]:
        """Every rule, or only the violating ones of the chosen rules when the graph's filter, or the node filter that
        kept these rules, asks for violations."""
        if self._kept is not None:
            return list(self._kept)
        graph = self.node.graph
        if graph is None:
            return self.chosen(False, [])
        return self.chosen(graph.explorer.filter.violations, list(graph.explorer.filter.rules))

    def kept_by(self, wanted: Filter) -> GraphRulesCollection:
        """These rules as the node filter wanted shows them under a node it keeps: only the broken ones of its chosen
        rules when it asks for violations, so the rules a person opens say why the node was kept."""
        return GraphRulesCollection(self.node, self.entries, self.chosen(wanted.violations, list(wanted.rules)))

    def chosen(self, violations_only: bool, selected: list[str]) -> list[GraphRule]:
        """Every rule; with violations_only, the violating ones, and of those only the selected slugs when any are."""
        if not violations_only:
            return self.graph_rules
        return [rule for rule in self.graph_rules if rule.is_failing and (not selected or rule.slug in selected)]

    @property
    def slugs(self) -> list[str]:
        return list(self.entries.keys())

    @property
    def violations(self) -> list[Violation]:
        """Every violation on this node, rule by rule."""
        return [violation for rule in self.graph_rules for violation in rule.violations]

    @property
    def failed_slugs(self) -> list[str]:
        return [rule.slug for rule in self.graph_rules if rule.is_failing]

    @property
    def passing_slugs(self) -> list[str]:
        failed = set(self.failed_slugs)
        return [slug for slug in self.slugs if slug not in failed]

    @property
    def graph_rules(self) -> list[GraphRule]:
        return [value for value in self.entries.values() if isinstance(value, GraphRule)]

    def record_violation(self, slug: str, message: str) -> None:
        """Keep message as a violation of the rule slug on this node. A slug this node has no rule for records nothing,
        since the rule does not apply to it."""
        entry = self.entries.get(slug)
        if isinstance(entry, GraphRule):
            entry.record(message)

    def restore(self, violation: Violation) -> None:
        entry = self.entries.get(violation.rule)
        if isinstance(entry, GraphRule):
            entry.restore(violation)
