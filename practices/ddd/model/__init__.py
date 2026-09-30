"""DDD practice model — building blocks on the clean engineering model."""

from .nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
    DDDModelFactory,
    DomainEvent,
    DomainService,
    Entity,
    Factory,
    Integration,
    InvariantObject,
    Repository,
    Specification,
    ValueObject,
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
    "BoundedContext",
    "BoundedContextMap",
    "DDDModelFactory",
    "DomainEvent",
    "DomainService",
    "Entity",
    "Factory",
    "Integration",
    "InvariantObject",
    "Repository",
    "Specification",
    "ValueObject",
    "class_stereotypes",
    "ddd_class_kind",
    "is_identity_property",
    "plain_class_name",
    "repository_root_name",
]
