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
    stereotypes = class_stereotypes(name)
    if "system" in stereotypes:
        return False
    return "domain service" in stereotypes or "service" in stereotypes


def is_specification(name: str) -> bool:
    return "specification" in class_stereotypes(name)


def ddd_class_kind(name: str) -> Optional[str]:
    """Return DDD stereotype name when class name carries tactical tags."""
    stereotypes = class_stereotypes(name)
    if not stereotypes or "system" in stereotypes:
        return None
    if is_aggregate_root(name):
        return "EntityRoot"
    if is_specification(name):
        return "Specification"
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


_VALUE_OBJECT_SUFFIXES = (
    "Token",
    "Code",
    "Message",
    "Requirement",
    "Requirements",
    "Operation",
)
_NON_TACTICAL_SUFFIXES = (
    "Exception",
    "Error",
    "Client",
    "Node",
    "View",
    "Routes",
    "Router",
)
_KIND_TAGS = {
    "EntityRoot": "aggregate root",
    "Entity": "entity",
    "ValueObject": "value object",
    "Repository": "repository",
    "DomainEvent": "domain event",
    "DomainService": "domain service",
    "Specification": "specification",
}


def inferred_tactical_kind(name: str, class_names: Optional[set[str]] = None) -> Optional[str]:
    """Tactical kind from <<tags>> or from the class name in code."""
    tagged = ddd_class_kind(name)
    if tagged:
        return tagged
    plain = plain_class_name(name)
    names = class_names or set()
    if plain.endswith("Repository"):
        return "Repository"
    if any(plain.endswith(suffix) for suffix in _NON_TACTICAL_SUFFIXES):
        return None
    if any(plain.endswith(suffix) for suffix in _VALUE_OBJECT_SUFFIXES):
        return "ValueObject"
    if f"{plain}Repository" in names:
        return "EntityRoot"
    if names and plain[:1].isupper():
        return "Entity"
    return None


def tactical_tags(kind: str) -> List[str]:
    tag = _KIND_TAGS.get(kind)
    return [tag] if tag else []


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
