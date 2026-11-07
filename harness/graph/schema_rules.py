"""Rule slugs declared on each type in practice/model/schema.yaml.

DDD (and pattern overlays) extend Clean Engineering via ``is:`` supertypes in schema:
``module`` → Module, ``class`` → OoadClass, ``property`` → Property, etc.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from harness.graph.schema_edges import schema_key_for_type, semantic_type
from harness.guidance.schema import Schema

_ROOT = Path(__file__).resolve().parents[2]

# Practice → CE practice whose schema anchors ``is: module|class|…`` resolve against.
_CE_EXTENSION: dict[str, str] = {"ddd": "clean_engineering"}

# ``is:`` tokens that name a clean_engineering schema type (not a sibling DDD type).
_CE_IS_TOKENS: dict[str, str] = {
    "module": "Module",
    "class": "OoadClass",
    "property": "Property",
    "operation": "Operation",
    "parameter": "Parameter",
    "package": "Package",
}

_PATTERNS_ROOT = _ROOT / "cdd_guidance" / "patterns"


def active_overlay_patterns(overlays: tuple[str, ...]) -> tuple[str, ...]:
    """Pattern folder names (e.g. ``lern_domain_driven``) from overlay paths or aliases."""
    found: list[str] = []
    for item in overlays:
        text = str(item).strip()
        if not text:
            continue
        name = Path(text.replace("\\", "/")).name
        if name and (_PATTERNS_ROOT / name / "practices").is_dir() and name not in found:
            found.append(name)
            continue
        if (_PATTERNS_ROOT / text / "practices").is_dir() and text not in found:
            found.append(text)
    return tuple(found)


def _overlay_schema_paths(practice: str, active_patterns: tuple[str, ...]) -> list[Path]:
    if not active_patterns:
        return []
    paths: list[Path] = []
    for pattern in active_patterns:
        schema = _PATTERNS_ROOT / pattern / "practices" / practice / "model" / "schema.yaml"
        if schema.is_file():
            paths.append(schema)
    return sorted(paths)


def _overlay_rules_paths(practice: str, active_patterns: tuple[str, ...]) -> list[Path]:
    if not active_patterns:
        return []
    paths: list[Path] = []
    for pattern in active_patterns:
        rules = _PATTERNS_ROOT / pattern / "practices" / practice / "model" / "rules.yaml"
        if rules.is_file():
            paths.append(rules)
    return sorted(paths)


def _merge_parsed_rules(found: dict[str, tuple[str, ...]], overlay: dict[str, tuple[str, ...]]) -> None:
    for node_type, slugs in overlay.items():
        merged = list(found.get(node_type, ()))
        for slug in slugs:
            if slug not in merged:
                merged.append(slug)
        found[node_type] = tuple(merged)


@lru_cache(maxsize=None)
def _schema_fidelities(practice: str) -> dict[str, list[str]]:
    from harness.guidance.schema_map import load_node_fidelities

    return load_node_fidelities(_ROOT / "cdd_guidance" / "practices" / practice)


def fidelities_for_type(practice: str, node_type: str) -> list[str]:
    """The fidelity that creates this node type and every higher one; empty when the schema gives none."""
    return list(_schema_fidelities(practice).get(schema_key_for_type(node_type), []))


@lru_cache(maxsize=None)
def _direct_rules_for_practice(practice: str, active_patterns: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Rule slugs declared explicitly under ``rules:`` in schema (no inheritance)."""
    path = _practice_schema_path(practice)
    if not path.is_file():
        return {}
    found = _rules(Schema.load(path))
    for schema in _overlay_schema_paths(practice, active_patterns):
        _merge_parsed_rules(found, _rules(Schema.load(schema)))
    for rules_path in _overlay_rules_paths(practice, active_patterns):
        _merge_parsed_rules(found, _rules(Schema.load(rules_path)))
    return found


def _practice_schema_path(practice: str) -> Path:
    return _ROOT / "cdd_guidance" / "practices" / practice / "model" / "schema.yaml"


def _rules(schema: Schema) -> dict[str, tuple[str, ...]]:
    """Explorer node type → the rule slugs its schema types list; ``given``, ``when``, and ``then`` are each a Step."""
    found: dict[str, tuple[str, ...]] = {}
    for key, slugs in schema.rules().items():
        _merge_parsed_rules(found, {semantic_type(key): slugs})
    return found


def _supertypes(schema: Schema) -> dict[str, str]:
    """Explorer node type → the ``is:`` reference its schema type names."""
    return {semantic_type(key): kind.supertype for key, kind in schema.types.items() if kind.supertype}


def _type_names(schema: Schema) -> set[str]:
    return {semantic_type(key) for key in schema.types}


@lru_cache(maxsize=None)
def _is_supertypes_for_practice(practice: str, active_patterns: tuple[str, ...]) -> dict[str, str]:
    """Explorer node type → ``is:`` reference (local key, CE token, or practice.type)."""
    path = _practice_schema_path(practice)
    if not path.is_file():
        return {}
    found = _supertypes(Schema.load(path))
    for schema in _overlay_schema_paths(practice, active_patterns):
        overlay = _supertypes(Schema.load(schema))
        for node_type, ref in overlay.items():
            if _is_self_ddd_ref(practice, node_type, ref):
                continue
            found[node_type] = ref
    return found


def _is_self_ddd_ref(practice: str, node_type: str, ref: str) -> bool:
    """Pattern overlays use ``is: ddd.aggregate`` to extend a block, not replace CE ``module``."""
    if practice != "ddd" or "." not in ref:
        return False
    prefix, tail = ref.split(".", 1)
    return prefix == "ddd" and semantic_type(tail) == node_type


@lru_cache(maxsize=None)
def _schema_types_for_practice(practice: str, active_patterns: tuple[str, ...]) -> frozenset[str]:
    """Every type block named in schema.yaml (base + active overlays)."""
    types = _type_names(Schema.load(_practice_schema_path(practice)))
    for schema in _overlay_schema_paths(practice, active_patterns):
        types.update(_type_names(Schema.load(schema)))
    types.update(_direct_rules_for_practice(practice, active_patterns).keys())
    types.update(_is_supertypes_for_practice(practice, active_patterns).keys())
    return frozenset(types)


def schema_semantic_types_for_practice(practice: str, active_patterns: tuple[str, ...]) -> frozenset[str]:
    """Explorer node type names from schema (base practice + selected overlays)."""
    return _schema_types_for_practice(practice, active_patterns)


def ce_anchor_type(practice: str, node_type: str, active_patterns: tuple[str, ...] = ()) -> str | None:
    """Clean Engineering schema type this practice node extends (Module, OoadClass, …)."""
    if practice == "clean_engineering":
        return node_type if node_type in _CE_IS_TOKENS.values() else None
    ce_practice = _CE_EXTENSION.get(practice)
    if ce_practice is None:
        return None
    is_map = _is_supertypes_for_practice(practice, active_patterns)
    current = node_type
    seen: set[str] = set()
    while current and current not in seen:
        seen.add(current)
        ref = is_map.get(current)
        if not ref:
            return None
        if ref in _CE_IS_TOKENS:
            return _CE_IS_TOKENS[ref]
        if "." in ref:
            _, tail = ref.split(".", 1)
            current = semantic_type(tail)
            continue
        current = semantic_type(ref)
    return None


def _supertype_chain(practice: str, node_type: str, active_patterns: tuple[str, ...]) -> tuple[str, ...]:
    """Walk ``is:`` from this type through local supertypes (includes node_type first)."""
    is_map = _is_supertypes_for_practice(practice, active_patterns)
    chain: list[str] = []
    current: str | None = node_type
    seen: set[str] = set()
    while current and current not in seen:
        seen.add(current)
        chain.append(current)
        ref = is_map.get(current)
        if not ref or ref in _CE_IS_TOKENS:
            break
        if "." in ref:
            _, tail = ref.split(".", 1)
            current = semantic_type(tail)
        else:
            current = semantic_type(ref)
    return tuple(chain)


def _merge_slugs(*slug_lists: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    for slugs in slug_lists:
        for slug in slugs:
            if slug not in merged:
                merged.append(slug)
    return tuple(merged)


@lru_cache(maxsize=None)
def rules_for_practice(practice: str, active_patterns: tuple[str, ...] = ()) -> dict[str, tuple[str, ...]]:
    """Map explorer node type → rule slugs (explicit schema rules + CE inheritance)."""
    direct = _direct_rules_for_practice(practice, active_patterns)
    ce_practice = _CE_EXTENSION.get(practice)
    ce_rules = _direct_rules_for_practice(ce_practice, active_patterns) if ce_practice else {}
    types = _schema_types_for_practice(practice, active_patterns)
    if not ce_practice:
        return dict(direct)

    effective: dict[str, tuple[str, ...]] = {}
    for node_type in sorted(types):
        own = direct.get(node_type, ())
        inherited: list[tuple[str, ...]] = []
        for step in _supertype_chain(practice, node_type, active_patterns):
            inherited.append(direct.get(step, ()))
        anchor = ce_anchor_type(practice, node_type, active_patterns)
        if anchor:
            inherited.append(ce_rules.get(anchor, ()))
        effective[node_type] = _merge_slugs(own, *inherited)
    for node_type, slugs in direct.items():
        if node_type not in effective:
            effective[node_type] = slugs
    return effective


def slugs_for_type(practice: str, node_type: str, active_patterns: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Schema slugs for this explorer type.

    A sub-epic is stored as its own type and carries the epic rules.
    Epic, sub-epic, and story are story nodes, so they also carry the
    storyNode rules.
    """
    table = rules_for_practice(practice, active_patterns)
    key = "Epic" if practice == "stories" and node_type == "SubEpic" else node_type
    found = list(table.get(key, ()))
    if practice == "stories" and node_type in {"Epic", "SubEpic", "Story"}:
        for slug in table.get("StoryNode", ()):
            if slug not in found:
                found.append(slug)
    return tuple(found)


def _active_patterns_for_practice_graph(practice_graph) -> tuple[str, ...]:
    graph = getattr(practice_graph, "graph", None)
    if graph is None:
        return ()
    return active_overlay_patterns(tuple(graph.overlays))


def apply_practice_rules(practice_graph) -> None:
    """Register every schema rule slug against the node types it applies to.

    Epic, sub-epic, and story are story nodes. Their filter list includes the
    storyNode slugs, including the prompt-only rules.
    """
    active = _active_patterns_for_practice_graph(practice_graph)
    for node_type, slugs in rules_for_practice(practice_graph.name, active).items():
        for slug in slugs:
            practice_graph.apply_rule(slug, [node_type])
    if practice_graph.name != "stories":
        return
    for node_type in ("Epic", "SubEpic", "Story"):
        for slug in slugs_for_type(practice_graph.name, node_type, active):
            practice_graph.apply_rule(slug, [node_type])


def qualified_rule_label(practice: str, node_type: str, slug: str, patterns: tuple[str, ...] = ()) -> str:
    """``practice.node.rule``, or ``lern.domain.driven.practice.node.rule`` for a pattern rule."""
    body = f"{practice}.{node_type}.{slug}"
    owner = _pattern_owning_rule(practice, node_type, slug, patterns)
    if owner is None:
        return body
    return f"{owner.replace('_', '.')}.{body}"


def qualified_rule_labels(practice: str, types_by_rule: dict[str, list[str]], patterns: tuple[str, ...] = ()) -> list[str]:
    labels = [
        qualified_rule_label(practice, node_type, slug, patterns)
        for slug, types in types_by_rule.items()
        for node_type in types
    ]
    return sorted(set(labels))


def _pattern_owning_rule(practice: str, node_type: str, slug: str, patterns: tuple[str, ...]) -> str | None:
    base_types = _schema_types_for_practice(practice, ())
    for pattern in patterns:
        if slug in _overlay_declared_rules(practice, pattern).get(node_type, ()):
            return pattern
        if node_type in _overlay_types(practice, pattern) and node_type not in base_types:
            return pattern
    return None


@lru_cache(maxsize=None)
def _overlay_declared_rules(practice: str, pattern: str) -> dict[str, tuple[str, ...]]:
    model = _PATTERNS_ROOT / pattern / "practices" / practice / "model"
    found = _rules(Schema.load(model / "schema.yaml"))
    _merge_parsed_rules(found, _rules(Schema.load(model / "rules.yaml")))
    return found


@lru_cache(maxsize=None)
def _overlay_types(practice: str, pattern: str) -> frozenset[str]:
    return frozenset(_type_names(Schema.load(_PATTERNS_ROOT / pattern / "practices" / practice / "model" / "schema.yaml")))

