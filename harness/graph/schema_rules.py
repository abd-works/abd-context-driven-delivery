"""PracticeSchema. The rule slugs, types, and fidelities one practice's ``model/schema.yaml`` declares, with what each
applied pattern's schema adds.

A type also carries the rules of each type its schema says it is (``is:``). A practice that extends another, such as
DDD building on Clean Engineering, anchors its types to that practice's types with the ``is:`` words the other practice
declares (``class`` is a Clean Engineering class), and its types carry the anchored type's rules too. Each practice
declares what it extends and its anchor words on its *PracticeGuidance* class, so the schema reader names no practice.
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import ClassVar

from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.schema_edges import SchemaKey
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.guidance.schema import Schema

_ROOT = Path(__file__).resolve().parents[2]
_PRACTICES_ROOT = _ROOT / "cdd_guidance" / "practices"
_PATTERNS_ROOT = _ROOT / "cdd_guidance" / "patterns"
# Fields every schema type may carry that describe the type itself, not a relationship.
_TYPE_FIELDS = frozenset({"is", "fidelity", "name", "path"})


def _extended_by(practice: PracticeGuidance) -> PracticeGuidance:
    """The practice whose types practice's schema builds on, which its ``extends`` names. A schema is the same in every
    graph, so it reads the catalogue's own instance of that practice."""
    return PracticeCatalogue.practice(practice.extends)


class PracticeSchema:
    """One practice's schema with the applied patterns' schemas on top: which rules each node type carries, which type
    of the extended practice it is, and the fidelities that create it."""

    # One schema per practice class and patterns: a practice's schema is the same whichever graph holds it.
    _loaded: ClassVar[dict[tuple[type, tuple[str, ...]], PracticeSchema]] = {}

    def __init__(self, practice: PracticeGuidance, patterns: tuple[str, ...] = ()) -> None:
        self.guidance = practice
        self.practice = practice.key
        self.patterns = tuple(patterns)
        self._declared = practice

    @classmethod
    def load(cls, practice: PracticeGuidance, patterns: tuple[str, ...] = ()) -> PracticeSchema:
        """The schema of practice with patterns applied; each is read once per process."""
        key = (type(practice), tuple(patterns))
        if key not in cls._loaded:
            cls._loaded[key] = cls(practice, tuple(patterns))
        return cls._loaded[key]

    @cached_property
    def types(self) -> frozenset[str]:
        """Every node type the practice's schema and the patterns' schemas name."""
        found = set(self._type_names(self._base))
        for schema in self._overlay_schemas:
            found.update(self._type_names(schema))
        found.update(self._direct_rules)
        found.update(self._supertypes)
        return frozenset(found)

    @cached_property
    def rules(self) -> dict[str, tuple[str, ...]]:
        """Each node type with the rule slugs it carries: its own, its supertypes', and its anchored type's."""
        extended = self._declared.extends
        if not extended:
            return dict(self._direct_rules)
        anchored_rules = PracticeSchema.load(_extended_by(self.guidance), self.patterns)._direct_rules
        return {node_type: self._carried_rules(node_type, anchored_rules) for node_type in sorted(self.types)}

    def slugs_for(self, node_type: str) -> tuple[str, ...]:
        """The rule slugs a node of this type carries, with those of each type its practice says it also carries."""
        table = self.rules
        listed = self._declared.rule_types.get(node_type, ())
        return self._merged(table.get(node_type, ()), *(table.get(other, ()) for other in listed))

    def anchor_type(self, node_type: str) -> str | None:
        """The extended practice's type this node type is, such as ``OoadClass`` for a DDD entity; a practice's own
        anchor type is itself."""
        own = self._declared.anchor_types
        if own:
            return node_type if node_type in own.values() else None
        extended = self._declared.extends
        if not extended:
            return None
        anchors = _extended_by(self.guidance).anchor_types
        last = self._supertype_chain(node_type)[-1]
        return anchors.get(self._supertypes.get(last, ""))

    def fidelities_for(self, node_type: str) -> list[str]:
        """The fidelity that creates this node type and every higher one; empty when the schema gives none."""
        return list(self._fidelities.get(SchemaKey.from_node_type(node_type).key, []))

    def apply_to(self, practice_graph) -> None:
        """Register every rule slug against the node types it applies to on practice_graph."""
        for node_type, slugs in self.rules.items():
            for slug in slugs:
                practice_graph.apply_rule(slug, [node_type])
        for node_type in self._declared.rule_types:
            for slug in self.slugs_for(node_type):
                practice_graph.apply_rule(slug, [node_type])

    def rule_label(self, node_type: str, slug: str) -> str:
        """``practice.node.rule``, or ``lern.domain.driven.practice.node.rule`` for a rule a pattern adds."""
        body = f"{self.practice}.{node_type}.{slug}"
        owner = self._pattern_owning_rule(node_type, slug)
        return body if owner is None else f"{owner.replace('_', '.')}.{body}"

    def rule_labels(self, types_by_rule: dict[str, list[str]]) -> list[str]:
        return sorted({self.rule_label(node_type, slug) for slug, types in types_by_rule.items() for node_type in types})

    @cached_property
    def overlay_relationship_kinds(self) -> frozenset[str]:
        """The relationship fields the applied patterns' schemas give this practice's types, such as ``route``."""
        return frozenset(
            name for schema in self._overlay_schemas for kind in schema.types.values() for name, value in kind.fields if value and name not in _TYPE_FIELDS
        )

    @cached_property
    def rule_prose(self) -> dict[str, str]:
        """Each rule slug with its prose from the practice's guidance (shared and per fidelity) and the patterns'."""
        guidances = [self.guidance]
        guidances.extend(guidance for guidance in (GraphOverlay.of(pattern).guidance() for pattern in self.patterns) if guidance is not None)
        merged: dict[str, str] = {}
        for guidance in guidances:
            fidelities = getattr(getattr(guidance, "fidelities", None), "entries", None) or {}
            for collection in (getattr(guidance, "rules", None), *(getattr(fidelity, "rules", None) for fidelity in fidelities.values())):
                merged.update(self._longest_prose(collection))
        return merged

    @cached_property
    def _base(self) -> Schema:
        return Schema.load(_PRACTICES_ROOT / self.practice / "model" / "schema.yaml")

    @cached_property
    def _overlay_schemas(self) -> list[Schema]:
        return [Schema.load(path) for path in self._overlay_files("schema.yaml")]

    @cached_property
    def _overlay_rule_files(self) -> list[Schema]:
        return [Schema.load(path) for path in self._overlay_files("rules.yaml")]

    def _overlay_files(self, name: str) -> list[Path]:
        found = (_PATTERNS_ROOT / pattern / "practices" / self.practice / "model" / name for pattern in self.patterns)
        return sorted(path for path in found if path.is_file())

    @cached_property
    def _direct_rules(self) -> dict[str, tuple[str, ...]]:
        """Rule slugs each type's ``rules:`` block lists, in the practice's schema and the patterns' schemas."""
        found = self._rules_of(self._base)
        for node_type, slugs in self._overlay_rules.items():
            found[node_type] = self._merged(found.get(node_type, ()), slugs)
        return found

    @cached_property
    def _supertypes(self) -> dict[str, str]:
        """Each node type with the ``is:`` reference its schema type names: a local type, an anchor word, or
        ``practice.type``. A pattern's ``is:`` naming the same practice's same type extends it rather than replacing it."""
        found = self._supertypes_of(self._base)
        for schema in self._overlay_schemas:
            for node_type, reference in self._supertypes_of(schema).items():
                if not self._names_itself(node_type, reference):
                    found[node_type] = reference
        return found

    @cached_property
    def _fidelities(self) -> dict[str, list[str]]:
        return self.guidance.schema_node_fidelities()

    def _carried_rules(self, node_type: str, anchored_rules: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
        inherited = [self._direct_rules.get(step, ()) for step in self._supertype_chain(node_type)]
        anchor = self.anchor_type(node_type)
        if anchor:
            inherited.append(anchored_rules.get(anchor, ()))
        return self._merged(self._direct_rules.get(node_type, ()), *inherited)

    def _supertype_chain(self, node_type: str) -> tuple[str, ...]:
        """node_type, then each local supertype its ``is:`` names, up to the first anchor word."""
        anchors = _extended_by(self.guidance).anchor_types if self._declared.extends else {}
        chain: list[str] = []
        current = node_type
        while current and current not in chain:
            chain.append(current)
            reference = self._supertypes.get(current)
            if not reference or reference in anchors:
                break
            current = SchemaKey(reference.split(".", 1)[-1]).node_type
        return tuple(chain)

    def _names_itself(self, node_type: str, reference: str) -> bool:
        prefix, _, tail = reference.partition(".")
        return bool(tail) and prefix == self.practice and SchemaKey(tail).node_type == node_type

    def _pattern_owning_rule(self, node_type: str, slug: str) -> str | None:
        """The applied pattern whose schema declares the rule on this type, or declares a type the practice lacks."""
        base_types = PracticeSchema.load(self.guidance).types
        for pattern in self.patterns:
            declared = PracticeSchema.load(self.guidance, (pattern,))
            if slug in declared._overlay_rules.get(node_type, ()):
                return pattern
            if node_type in declared._overlay_types and node_type not in base_types:
                return pattern
        return None

    @cached_property
    def _overlay_rules(self) -> dict[str, tuple[str, ...]]:
        """The rules the applied patterns' schemas declare, without the practice's own."""
        found: dict[str, tuple[str, ...]] = {}
        for schema in [*self._overlay_schemas, *self._overlay_rule_files]:
            for node_type, slugs in self._rules_of(schema).items():
                found[node_type] = self._merged(found.get(node_type, ()), slugs)
        return found

    @cached_property
    def _overlay_types(self) -> set[str]:
        return {node_type for schema in self._overlay_schemas for node_type in self._type_names(schema)}

    def _rules_of(self, schema: Schema) -> dict[str, tuple[str, ...]]:
        """Node type with the rule slugs its schema types list; ``given``, ``when``, and ``then`` are each a Step."""
        found: dict[str, tuple[str, ...]] = {}
        for key, slugs in schema.rules().items():
            node_type = SchemaKey(key).node_type
            found[node_type] = self._merged(found.get(node_type, ()), slugs)
        return found

    def _supertypes_of(self, schema: Schema) -> dict[str, str]:
        return {SchemaKey(key).node_type: kind.supertype for key, kind in schema.types.items() if kind.supertype}

    def _type_names(self, schema: Schema) -> set[str]:
        return {SchemaKey(key).node_type for key in schema.types}

    def _merged(self, *slug_lists: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(slug for slugs in slug_lists for slug in slugs))

    def _longest_prose(self, collection) -> dict[str, str]:
        """Each rule slug in one rules collection with its longest prose body; a later collection's prose wins."""
        found: dict[str, str] = {}
        for rule in (getattr(collection, "entries", None) or {}).values():
            slug, body = str(getattr(rule, "slug", "") or "").strip(), str(getattr(rule, "body", "") or "").strip()
            if slug and (slug not in found or len(body) > len(found[slug])):
                found[slug] = body
        return found
