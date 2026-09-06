"""Skill-inject hook — re-export from ``dispatch``."""

from hooks.dispatch import (
    already_injected,
    mark_injected,
    parse_payload,
    scan_tag,
    skill_digest,
    skill_inject,
    skill_inject_compact,
)

__all__ = [
    "already_injected",
    "mark_injected",
    "parse_payload",
    "scan_tag",
    "skill_digest",
    "skill_inject",
    "skill_inject_compact",
]

if __name__ == "__main__":
    from hooks.dispatch import main

    main()
