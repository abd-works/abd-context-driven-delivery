from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeclaredMember:
    name: str
    label: str | None = None
    target: str | None = None
