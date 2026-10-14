"""Rule slug → prose body from practice markdown (shared + fidelities)."""

from __future__ import annotations

from functools import lru_cache

_PRACTICE_GUIDANCE = {
    "clean_engineering": ("practices.clean_engineering.clean_engineering", "CleanEngineering"),
    "stories": ("practices.stories.stories", "Stories"),
    "ddd": ("practices.ddd.ddd", "Ddd"),
    "bdd": ("practices.bdd.bdd", "Bdd"),
    "ux": ("practices.ux.ux", "Ux"),
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


@lru_cache(maxsize=None)
def prose_by_slug(practice: str) -> dict[str, str]:
    spec = _PRACTICE_GUIDANCE.get(practice)
    if spec is None:
        return {}
    module_path, class_name = spec
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
