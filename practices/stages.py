"""CDD stage keys and fidelity resolution — not a host class."""

from __future__ import annotations

from typing import ClassVar

SHAPING: str = "shaping"
DISCOVERY: str = "discovery"
SPEC: str = "spec"
ENGINEER: str = "engineer"

STAGE_ALIASES: ClassVar[dict[str, str]] = {
    "scaffold": SHAPING,
    "discovery": DISCOVERY,
    "specification": SPEC,
    "spec": SPEC,
    "engineering": ENGINEER,
    "engineer": ENGINEER,
}


def resolve_stage_fidelity(name: str, stage_to_fidelity: dict[str, str]) -> str:
    """Map a CDD stage name to this practice's concrete fidelity key.

    Accepts stage command names (``discovery`` / ``specification`` /
    ``engineering``), short stage keys (``spec`` / ``engineer``), or an
    already-concrete fidelity. Stage names look up ``stage_to_fidelity``.
    """
    stage = STAGE_ALIASES.get(name, name)
    if stage in stage_to_fidelity:
        return stage_to_fidelity[stage]
    if name in stage_to_fidelity.values():
        return name
    return name
