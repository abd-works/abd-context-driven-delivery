"""PracticeSchema. The rule slugs, types, and fidelities one practice's ``model/schema.yaml`` declares, with what each
applied pattern's schema adds.

A type also carries the rules of each type its schema says it is (``is:``). A practice that extends another, such as
DDD building on Clean Engineering, anchors its types to that practice's types with the ``is:`` words the other practice
declares (``class`` is a Clean Engineering class), and its types carry the anchored type's rules too. Each practice
declares what it extends on its *PracticeGuidance* class and its anchor words on its reading part, so the schema reader names no practice.
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path

from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.schema_conformance import FRAMEWORK_RULES, RequiredRelationship
from harness.graph.schema_edges import SchemaKey
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.schema import Schema

# Fields every schema type may carry that describe the type itself, not a relationship.
_TYPE_FIELDS = frozenset({"is", "fidelity", "name", "path"})


class PracticeSchema:
    """One practice's schema with the applied patterns' schemas on top: which rules each node type carries, which type
    of the extended practice it is, and the fidelities that create it. A practice's part of a graph makes one for each
    set of overlays and keeps it (``practice.reading.in_graph.rule_run.schema_with(overlays)``), so a schema reads only the practice it
    was made for, never another session's practice of the same class."""

    def __init__(self, practice: PracticeGuidance, overlays: tuple[GraphOverlay, ...] = ()) -> None:
        self.practice = practice
        self.key = practice.key
        self.overlays = tuple(overlays)
        # What the applied patterns' schemas add to this practice's.
        self._added = SchemaOverlays(self.key, self.overlays)

    @cached_property
    def types(self) -> frozenset[str]:
        """Every node type the practice's schema and the patterns' schemas name."""
        found = type_names(self._base) | self._added.types
        found.update(self._direct_rules)
        found.update(self._supertypes)
        return frozenset(found)

    @cached_property
    def rules(self) -> dict[str, tuple[str, ...]]:
        """Each node type with the rule slugs it carries: its own, its supertypes', and its anchored type's."""
        extended = self.practice.extended
        if extended is None:
            return dict(self._direct_rules)
        anchored_rules = self._extended_schema._direct_rules
        return {node_type: self._carried_rules(node_type, anchored_rules) for node_type in sorted(self.types)}

    @cached_property
    def _extended_schema(self) -> PracticeSchema:
        return self._schema_of(self.practice.extended, self.overlays)

    @cached_property
    def _without_overlays(self) -> PracticeSchema:
        return self if not self.overlays else self._schema_of(self.practice, ())

    def _schema_of(self, practice: PracticeGuidance, overlays: tuple[GraphOverlay, ...]) -> PracticeSchema:
        """practice's schema with overlays, as its part of the graph keeps it; one of its own for a practice no graph
        holds."""
        part = practice.reading.in_graph
        return part.rule_run.schema_with(overlays) if part is not None else PracticeSchema(practice, overlays)

    def slugs_for(self, node_type: str) -> tuple[str, ...]:
        """The rule slugs a node of this type carries, with those of each type its practice says it also carries."""
        table = self.rules
        listed = self.practice.reading.rule_types.get(node_type, ())
        return merged(table.get(node_type, ()), *(table.get(other, ()) for other in listed), tuple(FRAMEWORK_RULES))

    def anchor_type(self, node_type: str) -> str | None:
        """The extended practice's type this node type is, such as ``OoadClass`` for a DDD entity; a practice's own
        anchor type is itself."""
        own = self.practice.reading.anchor_types
        if own:
            return node_type if node_type in own.values() else None
        extended = self.practice.extended
        if extended is None:
            return None
        anchors = extended.reading.anchor_types
        last = self._supertype_chain(node_type)[-1]
        return anchors.get(self._supertypes.get(last, ""))

    def fidelities_for(self, node_type: str) -> list[str]:
        """The fidelity that creates this node type and every higher one; empty when the schema gives none."""
        return list(self._fidelities.get(SchemaKey.from_node_type(node_type).key, []))

    @cached_property
    def applicable(self) -> dict[str, list[str]]:
        """Each rule slug with the node types it applies to: the types that carry it, and those the practice says also
        carry it."""
        found: dict[str, list[str]] = {}
        carried = [(node_type, slugs) for node_type, slugs in self.rules.items()]
        carried.extend((node_type, self.slugs_for(node_type)) for node_type in self.practice.reading.rule_types)
        carried.extend((node_type, tuple(FRAMEWORK_RULES)) for node_type in sorted(self.types))
        for node_type, slugs in carried:
            for slug in slugs:
                types = found.setdefault(slug, [])
                if node_type not in types:
                    types.append(node_type)
        return found

    def rule_label(self, node_type: str, slug: str) -> str:
        """``practice.node.rule``, or ``lern.domain.driven.practice.node.rule`` for a rule a pattern adds."""
        body = f"{self.key}.{node_type}.{slug}"
        owner = self._added.pattern_adding(node_type, slug, self._without_overlays.types)
        return body if owner is None else f"{owner.replace('_', '.')}.{body}"

    def rule_labels(self, types_by_rule: dict[str, list[str]]) -> list[str]:
        return sorted({self.rule_label(node_type, slug) for slug, types in types_by_rule.items() for node_type in types})

    @property
    def overlay_relationship_kinds(self) -> frozenset[str]:
        """The relationship fields the applied patterns' schemas give this practice's types, such as ``route``."""
        return self._added.relationship_kinds

    @cached_property
    def rule_prose(self) -> dict[str, str]:
        """Each rule slug with its prose from the practice's guidance (shared and per fidelity) and the patterns'."""
        guidances = [self.practice]
        guidances.extend(overlay.pattern for overlay in self.overlays)
        merged = {slug: check.rule.body for slug, check in FRAMEWORK_RULES.items()}
        for guidance in guidances:
            fidelities = getattr(getattr(guidance, "fidelities", None), "entries", None) or {}
            for collection in (getattr(guidance, "rules", None), *(getattr(fidelity, "rules", None) for fidelity in fidelities.values())):
                merged.update(self._longest_prose(collection))
        return merged

    @cached_property
    def requirements(self) -> list[RequiredRelationship]:
        """Every relationship the practice's schema and each applied pattern's schema for it require of a node of one
        of their types, with the stage of the fidelity that creates the owner and the earliest target."""
        sources = [(f"{self.key} practice", self._base), *((f"{name} pattern", schema) for name, schema in self._added.named_schemas)]
        return [
            RequiredRelationship(
                SchemaKey(key), field, self._node_types_named(references),
                source, self.stage_of(key), self._earliest_stage(references),
            )
            for source, schema in sources
            for key, kind in schema.types.items()
            for field, references in kind.required_relationships.items()
        ]

    @property
    def current_stage(self) -> int | None:
        """The place of the fidelity the practice works at now among its fidelities; none when it works at none."""
        current = self.practice.fidelities.current
        order = list(self.practice.fidelities.entries.values())
        return next((index for index, fidelity in enumerate(order) if fidelity is current), None)

    def stage_of(self, reference: str) -> int | None:
        """The place among its practice's fidelities of the fidelity that creates the type reference names: a key of
        this practice's schemas (``route``) or ``practice.type`` (``ddd.entityRoot``), read from that practice's schema
        when another practice of the graph holds it. None when no schema says which fidelity creates it."""
        practice_key, _, key = reference.rpartition(".")
        if practice_key and practice_key != self.key:
            graph = self.practice.reading.graph
            other = graph.practices.held.get(practice_key) if graph is not None else None
            return self._schema_of(other, self.overlays).stage_of(key) if other is not None else None
        fidelity = self._fidelity_named(key, frozenset())
        order = list(self.practice.fidelities.entries)
        return order.index(fidelity) if fidelity in order else None

    def _earliest_stage(self, references: tuple[str, ...]) -> int | None:
        """The earliest stage among the types references names; none when any of them has none, so it is always due."""
        stages = [self.stage_of(reference) for reference in references]
        return None if None in stages else min(stages)

    @staticmethod
    def _node_types_named(references: tuple[str, ...]) -> tuple[str, ...]:
        """Every node type a node of the types references names may be read as, once each."""
        return tuple(dict.fromkeys(node_type for reference in references for node_type in SchemaKey(reference.rpartition(".")[2]).node_types))

    def _fidelity_named(self, key: str, seen: frozenset[str]) -> str:
        """The fidelity the practice's or the patterns' schemas give the type key, else the one its ``is:`` supertype in
        this practice has; empty when none says."""
        kinds = [schema.types[key] for schema in (self._base, *self._added.schemas) if key in schema.types]
        fidelity = next((kind.fidelity for kind in kinds if kind.fidelity), "")
        prefix, _, supertype = next((kind.supertype for kind in kinds if kind.supertype), "").rpartition(".")
        if fidelity or not supertype or (prefix and prefix != self.key) or supertype in seen:
            return fidelity
        return self._fidelity_named(supertype, seen | {key})

    @cached_property
    def _base(self) -> Schema:
        """The practice's own schema, as the practice reads it."""
        return self.practice.schema

    @cached_property
    def _direct_rules(self) -> dict[str, tuple[str, ...]]:
        """Rule slugs each type's ``rules:`` block lists, in the practice's schema and the patterns' schemas."""
        found = rules_of(self._base)
        for node_type, slugs in self._added.rules.items():
            found[node_type] = merged(found.get(node_type, ()), slugs)
        return found

    @cached_property
    def _supertypes(self) -> dict[str, str]:
        """Each node type with the ``is:`` reference its schema type names: a local type, an anchor word, or
        ``practice.type``. A pattern's ``is:`` naming the same practice's same type extends it rather than replacing it."""
        found = supertypes_of(self._base)
        for schema in self._added.schemas:
            for node_type, reference in supertypes_of(schema).items():
                if not self._names_itself(node_type, reference):
                    found[node_type] = reference
        return found

    @cached_property
    def _fidelities(self) -> dict[str, list[str]]:
        return self.practice.schema.node_fidelities(list(self.practice.fidelities.entries))

    def _carried_rules(self, node_type: str, anchored_rules: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
        inherited = [self._direct_rules.get(step, ()) for step in self._supertype_chain(node_type)]
        anchor = self.anchor_type(node_type)
        if anchor:
            inherited.append(anchored_rules.get(anchor, ()))
        return merged(self._direct_rules.get(node_type, ()), *inherited)

    def _supertype_chain(self, node_type: str) -> tuple[str, ...]:
        """node_type, then each local supertype its ``is:`` names, up to the first anchor word."""
        anchors = self.practice.extended.reading.anchor_types if self.practice.extended is not None else {}
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
        return bool(tail) and prefix == self.key and SchemaKey(tail).node_type == node_type

    def _longest_prose(self, collection) -> dict[str, str]:
        """Each rule slug in one rules collection with its longest prose body; a later collection's prose wins."""
        found: dict[str, str] = {}
        for rule in (getattr(collection, "entries", None) or {}).values():
            slug, body = str(getattr(rule, "slug", "") or "").strip(), str(getattr(rule, "body", "") or "").strip()
            if slug and (slug not in found or len(body) > len(found[slug])):
                found[slug] = body
        return found


class SchemaOverlays:
    """What the applied patterns' schemas add to one practice's schema: the types they name, the rules they give its
    types, the relationship fields they add, and which pattern adds each rule. The practice's schema holds one for its
    overlays."""

    def __init__(self, key: str, overlays: tuple[GraphOverlay, ...]) -> None:
        self._key = key
        self._overlays = overlays

    @cached_property
    def schemas(self) -> list[Schema]:
        """Each pattern's schema for the practice."""
        return [Schema.load(path) for path in self._files("schema.yaml")]

    @cached_property
    def named_schemas(self) -> list[tuple[str, Schema]]:
        """Each applied pattern's name with its schema for the practice, for the patterns that keep one."""
        return [(overlay.name, schema) for overlay, added in self._each for schema in added.schemas]

    @cached_property
    def types(self) -> set[str]:
        """Every node type the patterns' schemas name."""
        return {node_type for schema in self.schemas for node_type in type_names(schema)}

    @cached_property
    def rules(self) -> dict[str, tuple[str, ...]]:
        """The rules the patterns' schemas and rule files declare, without the practice's own."""
        found: dict[str, tuple[str, ...]] = {}
        for schema in [*self.schemas, *(Schema.load(path) for path in self._files("rules.yaml"))]:
            for node_type, slugs in rules_of(schema).items():
                found[node_type] = merged(found.get(node_type, ()), slugs)
        return found

    @cached_property
    def relationship_kinds(self) -> frozenset[str]:
        """The relationship fields the patterns' schemas give the practice's types, such as ``route``."""
        return frozenset(
            name for schema in self.schemas for kind in schema.types.values() for name, value in kind.fields if value and name not in _TYPE_FIELDS
        )

    def pattern_adding(self, node_type: str, slug: str, base_types: frozenset[str]) -> str | None:
        """The name of the applied pattern whose schema declares the rule on this type, or declares a type the
        practice's own schema, whose types are base_types, lacks."""
        for overlay, added in self._each:
            if slug in added.rules.get(node_type, ()) or (node_type in added.types and node_type not in base_types):
                return overlay.name
        return None

    @cached_property
    def _each(self) -> list[tuple[GraphOverlay, SchemaOverlays]]:
        """Each overlay with what it alone adds."""
        return [(overlay, SchemaOverlays(self._key, (overlay,))) for overlay in self._overlays]

    def _files(self, name: str) -> list[Path]:
        found = (overlay.practice_file(self._key, name) for overlay in self._overlays)
        return sorted(path for path in found if path.is_file())


def rules_of(schema: Schema) -> dict[str, tuple[str, ...]]:
    """Node type with the rule slugs its schema types list; ``given``, ``when``, and ``then`` are each a Step."""
    found: dict[str, tuple[str, ...]] = {}
    for key, slugs in schema.rules().items():
        node_type = SchemaKey(key).node_type
        found[node_type] = merged(found.get(node_type, ()), slugs)
    return found


def supertypes_of(schema: Schema) -> dict[str, str]:
    """Each node type with the ``is:`` reference its schema type names."""
    return {SchemaKey(key).node_type: kind.supertype for key, kind in schema.types.items() if kind.supertype}


def type_names(schema: Schema) -> set[str]:
    """Every node type a schema names."""
    return {SchemaKey(key).node_type for key in schema.types}


def merged(*slug_lists: tuple[str, ...]) -> tuple[str, ...]:
    """The slugs of each list in order, each once."""
    return tuple(dict.fromkeys(slug for slugs in slug_lists for slug in slugs))
