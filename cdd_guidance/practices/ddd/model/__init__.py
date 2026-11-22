"""DDD practice model — building blocks on the clean engineering model."""

from .building_blocks import (
    DomainEvent,
    DomainService,
    Entity,
    Factory,
    InvariantObject,
    Repository,
    Specification,
    ValueObject,
)
from .nodes import Aggregate, BoundedContext, BoundedContextMap, Integration
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
