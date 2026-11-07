"""Rule slug → prose body from practice markdown (shared + fidelities)."""

from __future__ import annotations

from functools import lru_cache

from harness.graph.graph_practice import GraphPractices


def _collect_rules(collection) -> dict[str, str]:
    found: dict[str, str] = {}
    if collection is None:
        return found
    entries = getattr(collection, "entries", None) or {}
    for value in entries.values():
        if hasattr(value, "slug") and hasattr(value, "body"):
            slug = str(value.slug or "").strip()
            body = str(value.body or "").strip()
            if slug and (slug not in found or len(body) > len(found[slug])):
                found[slug] = body
    return found


def _guidance_prose(guidance) -> dict[str, str]:
    merged: dict[str, str] = {}
    merged.update(_collect_rules(getattr(guidance, "rules", None)))
    fidelities = getattr(guidance, "fidelities", None)
    for child in (getattr(fidelities, "entries", None) or {}).values():
        merged.update(_collect_rules(getattr(child, "rules", None)))
    return merged


@lru_cache(maxsize=None)
def prose_by_slug(practice: str, active_patterns: tuple[str, ...] = ()) -> dict[str, str]:
    from harness.guidance.practice_catalogue import PracticeCatalogue

    merged = _guidance_prose(PracticeCatalogue.practice(practice)) if PracticeCatalogue.has(practice) else {}
    for pattern in active_patterns:
        guidance = GraphPractices.overlay(pattern).guidance()
        if guidance is not None:
            merged.update(_guidance_prose(guidance))
    return merged
