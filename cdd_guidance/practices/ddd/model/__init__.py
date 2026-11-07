"""DDD practice model — building blocks on the clean engineering model."""

from .nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
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
from .stereotypes import TacticalClass, plain_class_name


__all__ = [
    "Aggregate",
    "BoundedContext",
    "BoundedContextMap",
    "DomainEvent",
    "DomainService",
    "Entity",
    "Factory",
    "Integration",
    "InvariantObject",
    "Repository",
    "Specification",
    "ValueObject",
    "TacticalClass",
    "plain_class_name",
]
