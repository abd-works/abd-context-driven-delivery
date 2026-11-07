"""The rules that apply to one graph node, in the same collection shape as a practice's guidance rules. In the
explorer tree the collection is the node's rules entry and each rule is a child of it."""

from __future__ import annotations

from typing import Any

from harness.guidance.rule import Rule, RulesCollection
from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Violation
from harness.installation.destination import data_field


class GraphRule(PracticeGraphRule, Rule):
    """One schema rule on one node: its slug, its prose, whether a check runs it, and the violations it found there."""

    def __init__(
        self,
        node: Any,
        slug: str,
        body: str = "",
        node_types: tuple[str, ...] = (),
        *,
        check: PracticeGraphRule | None = None,
        runs: bool = False,
    ) -> None:
        PracticeGraphRule.__init__(self)
        Rule.__init__(self, slug=slug, body=body)
        self.node = node
        self.node_types = node_types
        self.executable = check is not None
        self.runs = runs and check is not None
        """Whether its check runs on this node: the check applies to the node's type, or to the type it is anchored to."""
        if check is not None:
            self.check = check.check  # type: ignore[method-assign]
        self._violations: list[Violation] = []

    @property
    @data_field
    def slug(self) -> str:
        """The guidance rule's slug; a check's own class attribute would hide it."""
        return Rule.slug.fget(self)

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
    def children(self) -> list:
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
        violation = Violation.on_node(self.slug, message, self.node)
        if violation.message and all(kept.message != violation.message for kept in self._violations):
            self._violations.append(violation)

    def restore(self, violation: Violation) -> None:
        """Keep a violation a saved graph recorded, at the place it was saved with."""
        if violation not in self._violations:
            self._violations.append(violation)

    def clear_violations(self) -> None:
        self._violations.clear()

    @property
    def is_failing(self) -> bool:
        return bool(self._violations)


class GraphRulesCollection(RulesCollection):
    """Schema rules for one node. Violations live on each GraphRule entry."""

    def __init__(self, node: Any, entries: dict[str, GraphRule] | None = None) -> None:
        super().__init__(entries)
        self.node = node

    @classmethod
    def from_node(cls, node: Any) -> GraphRulesCollection:
        """The rules node's schema gives its type, each with its prose, the check that runs it when one exists, and
        whether that check applies to node; node says which checks it has and which apply to it."""
        schema = node.practice.schema
        checks = node.rule_checks()
        applying = node.applying_rule_types()
        entries: dict[str, GraphRule] = {}
        for slug in schema.slugs_for(node.type):
            check = checks.get(slug)
            node_types = tuple(check.node_types) if check is not None else (node.type,)
            runs = check is not None and any(check.applies_to(type_name) for type_name in applying)
            entries[slug] = GraphRule(node, slug, body=schema.rule_prose.get(slug, ""), node_types=node_types, check=check, runs=runs)
        return cls(node, entries)

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
        """Every rule, or only the violating ones of the chosen rules when the graph's filter asks for violations."""
        graph = self.node.practice.graph
        if graph is None:
            return self.chosen(False, [])
        return self.chosen(graph.filter.violations, list(graph.filter.rules))

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

    def clear_violations(self) -> None:
        for rule in self.graph_rules:
            rule.clear_violations()
