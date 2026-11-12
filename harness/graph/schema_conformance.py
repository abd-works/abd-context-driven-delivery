"""ConformsToSchema. The framework's own graph rule, which every practice checks on every graph build: content conforms
to its schema, so every node has each relationship its schema type requires, up to the fidelity being worked.

A practice's schema, with the schemas of the patterns its graph applies, says which relationships each of its types
requires (*RequiredRelationship*, made by ``PracticeSchema.requirements``). The rule is on for every practice without a
schema naming it in a ``rules:`` block: the graph's pattern overlays add it to the checks of every practice
(``PatternOverlays.checks_of``), and the practice's schema gives it to every node type and gives it its prose.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.schema_edges import CHILD_LISTS, SchemaKey
from harness.guidance.rule import Rule

if TYPE_CHECKING:
    from harness.graph.rule_context import RuleCheckContext


@dataclass(frozen=True)
class RequiredRelationship:
    """One relationship a schema type requires of its nodes: the owner type, the field naming the relationship, the
    node types it may lead to, the schema that requires it (``clean_engineering practice``, ``lern_domain_driven
    pattern``), and the stage of the fidelity that creates the owner and the earliest target; a stage is none when no
    schema says which fidelity creates the type."""

    owner: SchemaKey
    field: str
    targets: tuple[str, ...]
    source: str
    owner_stage: int | None
    target_stage: int | None

    def required_at(self, current_stage: int | None) -> bool:
        """Whether a node must have it while its practice works at current_stage: when its target is created by then;
        with no current fidelity, only when the target is created at the owner's own fidelity. A target no schema gives
        a fidelity is always required."""
        if self.target_stage is None:
            return True
        if current_stage is None:
            return self.target_stage == self.owner_stage
        return self.target_stage <= current_stage

    def owners(self, context: RuleCheckContext) -> list[Any]:
        """The checked practice's nodes of the owner type, read as either of its node types; a step's phase key
        (``when``) holds a ``Step`` only when the step is of that phase."""
        phase, general = self.owner.phase, self.owner.node_type
        nodes = [node for node_type in self.owner.node_types for node in context.nodes(node_type)]
        return [node for node in nodes if not phase or node.type != general or getattr(node, "phase", "") == phase]

    def gap_on(self, node: Any, context: RuleCheckContext) -> str:
        """What node lacks of this relationship: none when an edge of the field leads from it to a node of a target type,
        or, for a child list, when it holds a node of a target type under any kind its practice records it."""
        linked = context.held_by(node) if self.field in CHILD_LISTS else context.targets(node, self.field)
        if any(target.type in self.targets for target in linked):
            return ""
        return (
            f"{node.type} '{node.name}' has no {self.field} relationship to {' | '.join(self.targets)}, "
            f"which the {self.source} schema requires."
        )


class ConformsToSchema(PracticeGraphRule):
    """Every node has each relationship its schema type requires, up to the fidelity its practice works at now."""

    slug = "conforms-to-schema"
    rule = Rule(
        slug=slug,
        body=(
            "Content conforms to its schema: every node has each relationship its schema type requires, up to the "
            "fidelity being worked. It checks only what the schema requires (a field written `name?:` is optional) and "
            "only for the fidelities worked so far: a relationship whose target a later fidelity creates is not "
            "required yet. Validate keeps only the findings inside the work's scope: the session's stories and "
            "everything under them, and the files the call names."
        ),
    )

    def applies_to(self, node_type: str) -> bool:
        """Every node type: every type a schema names may require a relationship."""
        return True

    def check_practice(self, context: RuleCheckContext) -> list[tuple[str, str]]:
        """Each node missing a relationship its schema requires at the practice's current fidelity, with what it lacks."""
        schema = context.practice.reading.in_graph.rule_run.schema
        stage = schema.current_stage
        due = [requirement for requirement in schema.requirements if requirement.required_at(stage)]
        found = ((node, requirement.gap_on(node, context)) for requirement in due for node in requirement.owners(context))
        return [(node.node_id, gap) for node, gap in found if gap]


FRAMEWORK_RULES: dict[str, ConformsToSchema] = {ConformsToSchema.slug: ConformsToSchema()}
"""The graph rules every practice checks, by slug, whatever its schema lists."""
