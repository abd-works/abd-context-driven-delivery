"""Detect DDD tactical stereotypes from decorated CE class names."""

from __future__ import annotations

import re
from typing import List, Optional

_STEREOTYPE_RE = re.compile(r"<<([^>]+)>>")


def class_stereotypes(name: str) -> List[str]:
    return [s.strip().lower() for s in _STEREOTYPE_RE.findall(name)]


def plain_class_name(name: str) -> str:
    n = re.sub(r"\*+", "", name)
    n = _STEREOTYPE_RE.sub("", n).strip()
    n = re.split(r"\s+extends\s+", n, maxsplit=1)[0].strip()
    return n


def is_aggregate_root(name: str) -> bool:
    return "aggregate root" in class_stereotypes(name)


def is_entity(name: str) -> bool:
    return "entity" in class_stereotypes(name)


def is_value_object(name: str) -> bool:
    return "value object" in class_stereotypes(name)


def is_repository(name: str) -> bool:
    return "repository" in class_stereotypes(name)


def is_domain_event(name: str) -> bool:
    return "domain event" in class_stereotypes(name)


def is_domain_service(name: str) -> bool:
    return "domain service" in class_stereotypes(name)


def ddd_class_kind(name: str) -> Optional[str]:
    """Return DDD stereotype name when class name carries tactical tags."""
    stereotypes = class_stereotypes(name)
    if not stereotypes:
        return None
    if is_aggregate_root(name):
        return "EntityRoot"
    if is_entity(name):
        return "Entity"
    if is_value_object(name):
        return "ValueObject"
    if is_repository(name):
        return "Repository"
    if is_domain_event(name):
        return "DomainEvent"
    if is_domain_service(name):
        return "DomainService"
    return None


def repository_root_name(repo_name: str) -> Optional[str]:
    plain = plain_class_name(repo_name)
    if plain.endswith("Repository"):
        return plain[: -len("Repository")]
    return None


def is_identity_property(name: str, type_hint: str = "") -> bool:
    """True when a property carries entity identity (id, identity, or << identifier >>)."""
    if name in ("id", "identity"):
        return True
    return "<< identifier >>" in type_hint or "<<identifier>>" in type_hint.lower()
