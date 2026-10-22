"""Rule slug → prose body from practice markdown (shared + fidelities)."""

from __future__ import annotations

from functools import lru_cache

_PRACTICE_GUIDANCE = {
    "clean_engineering": ("cdd_guidance.practices.clean_engineering.clean_engineering", "CleanEngineering"),
    "stories": ("cdd_guidance.practices.stories.stories", "Stories"),
    "ddd": ("cdd_guidance.practices.ddd.ddd", "Ddd"),
    "bdd": ("cdd_guidance.practices.bdd.bdd", "Bdd"),
    "ux": ("cdd_guidance.practices.ux.ux", "Ux"),
}

_PATTERN_GUIDANCE = {
    "lern_domain_driven": ("cdd_guidance.patterns.lern_domain_driven.lern_domain_driven", "LernDomainDriven"),
}


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


def _guidance_prose(module_path: str, class_name: str) -> dict[str, str]:
    try:
        import importlib

        module = importlib.import_module(module_path)
        guidance = getattr(module, class_name)()
    except Exception:
        return {}
    merged: dict[str, str] = {}
    merged.update(_collect_rules(getattr(guidance, "rules", None)))
    fidelities = getattr(guidance, "fidelities", None)
    for child in (getattr(fidelities, "entries", None) or {}).values():
        merged.update(_collect_rules(getattr(child, "rules", None)))
    return merged


@lru_cache(maxsize=None)
def prose_by_slug(practice: str, active_patterns: tuple[str, ...] = ()) -> dict[str, str]:
    spec = _PRACTICE_GUIDANCE.get(practice)
    if spec is None:
        merged: dict[str, str] = {}
    else:
        merged = dict(_guidance_prose(*spec))
    for pattern in active_patterns:
        pattern_spec = _PATTERN_GUIDANCE.get(pattern)
        if pattern_spec is None:
            continue
        merged.update(_guidance_prose(*pattern_spec))
    return merged
