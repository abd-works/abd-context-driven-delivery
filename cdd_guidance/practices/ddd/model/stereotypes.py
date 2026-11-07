"""Detect DDD tactical stereotypes from decorated CE class names."""

from __future__ import annotations

import re
from typing import List, Optional

# The one reading of `<<Stereotype>>` marks in a class heading, a class name, or a doc comment.
_STEREOTYPE = re.compile(r"<<\s*([^>]+?)\s*>>")
_CLASS_DECL = re.compile(r"(?:export\s+)?(?:abstract\s+)?class\s+(\w+)\b")
_AT_STEREOTYPE = re.compile(r"^\s*@(\w+)\s*(?:\(|$)")

# Code-channel shorthand (tactics). Model/sketch canonical form remains <<Repository>>.
_AT_TO_STEREOTYPE: dict[str, str] = {
    "repository": "repository",
    "entity": "entity",
    "aggregateroot": "aggregate root",
    "aggregate_root": "aggregate root",
    "valueobject": "value object",
    "value_object": "value object",
    "domainservice": "domain service",
    "domain_service": "domain service",
    "domainevent": "domain event",
    "domain_event": "domain event",
    "specification": "specification",
    "factory": "factory",
}


# The stereotypes DDD gives a class, lower-cased; a class's other stereotypes, such as a dataclass mark, are not DDD's.
_TACTICAL_STEREOTYPES = frozenset(set(_AT_TO_STEREOTYPE.values()) | {"service", "system"})


def tactical_stereotypes(stereotypes: List[str]) -> List[str]:
    """The class's stereotypes that are DDD building blocks, as written."""
    return [item for item in stereotypes if item.lower() in _TACTICAL_STEREOTYPES]


def decorated_name(class_name: str, stereotypes: List[str]) -> str:
    """The class name followed by its DDD stereotypes as `<<Mark>>`s, the form the tactical kind readers take."""
    return " ".join([class_name] + [f"<<{item}>>" for item in tactical_stereotypes(stereotypes)])


def class_declaration_decorated_name(text: str, class_name: str) -> str:
    """Class name plus tactical markers from <<tags>>, @stereotype decorators, or # comments."""
    match = re.search(rf"(?:export\s+)?(?:abstract\s+)?class\s+{re.escape(class_name)}\b", text)
    if match is None:
        return class_name
    prefix = text[max(0, match.start() - 400) : match.start()]
    tags: list[str] = []
    for block in re.findall(r"/\*\*([\s\S]*?)\*/", prefix):
        tags.extend(f"<<{tag}>>" for tag in stereotypes_in(block))
    for line in prefix.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            tags.extend(stereotypes_in(stripped))
        at = _AT_STEREOTYPE.match(stripped)
        if at:
            mapped = _AT_TO_STEREOTYPE.get(at.group(1).lower())
            if mapped:
                tags.append(f"<<{mapped}>>")
    if not tags:
        return class_name
    normalized = []
    for tag in tags:
        normalized.append(tag if tag.startswith("<<") else f"<<{tag}>>")
    return f"{class_name} {' '.join(normalized)}"


def stereotypes_in(text: str) -> List[str]:
    """Each `<<Stereotype>>` in the text, as written."""
    return [item.strip() for item in _STEREOTYPE.findall(text)]


def without_stereotypes(text: str) -> str:
    return _STEREOTYPE.sub("", text).strip()


def class_stereotypes(name: str) -> List[str]:
    return [item.lower() for item in stereotypes_in(name)]


def plain_class_name(name: str) -> str:
    """The class name alone: no bold or code marks, stereotypes, or base classes."""
    plain = without_stereotypes(name.replace("*", "").replace("`", ""))
    return re.split(r"\s+extends\s+", plain, maxsplit=1)[0].strip()


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
    "Screen",
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


_TAGGED_KINDS = frozenset({"Entity", "EntityRoot", "ValueObject", "Repository", "DomainService", "Specification"})


def name_reflects_tactical_kind(class_name: str, kind: str, names: set[str]) -> bool:
    plain = plain_class_name(class_name)
    if kind == "Repository":
        return plain.endswith("Repository")
    if kind == "DomainService":
        return plain.endswith("Service")
    if kind == "Specification":
        return "Specification" in plain
    if kind == "ValueObject":
        return any(plain.endswith(suffix) for suffix in ("Token", "Code", "Message", "Value"))
    if kind == "EntityRoot":
        return plain.endswith("Root") or f"{plain}Repository" in names
    if kind == "Entity":
        return plain.endswith("Entity")
    return False


def declares_tactical_stereotype(class_name: str, stereotypes: List[str], graph_kind: str, peer_names: set[str]) -> bool:
    """True when the class carries a DDD stereotype, or its name itself says the tactical kind."""
    if tactical_stereotypes(stereotypes):
        return True
    kind = inferred_tactical_kind(class_name, peer_names) or graph_kind
    return name_reflects_tactical_kind(class_name, kind if kind in _TAGGED_KINDS else graph_kind, peer_names)
