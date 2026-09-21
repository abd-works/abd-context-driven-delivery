"""DDD practice model — specialisations of Clean Engineering Module and Class."""

from .bounded_context_map import (
    AggregateEntry,
    BoundedContextEntry,
    load_bounded_context_map,
    parse_bounded_context_map,
)
from .nodes import (
    Aggregate,
    BoundedContext,
    DomainEvent,
    DomainService,
    Entity,
    EntityRoot,
    Repository,
    ValueObject,
    ddd_class_for,
)
from .stereotypes import (
    class_stereotypes,
    ddd_class_kind,
    is_identity_property,
    plain_class_name,
    repository_root_name,
)

__all__ = [
    "Aggregate",
    "AggregateEntry",
    "BoundedContext",
    "BoundedContextEntry",
    "DomainEvent",
    "DomainService",
    "Entity",
    "EntityRoot",
    "Repository",
    "ValueObject",
    "class_stereotypes",
    "ddd_class_for",
    "ddd_class_kind",
    "is_identity_property",
    "load_bounded_context_map",
    "parse_bounded_context_map",
    "plain_class_name",
    "repository_root_name",
]
