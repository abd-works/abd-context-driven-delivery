"""DDD node types — specialise CE Module and OoadClass."""

from __future__ import annotations

from practices.clean_engineering.model.base_class_model import Module, OoadClass


class BoundedContext(Module):
    _semantic_type_name = "BoundedContext"


class Aggregate(Module):
    _semantic_type_name = "Aggregate"


class Entity(OoadClass):
    _semantic_type_name = "Entity"


class EntityRoot(Entity):
    _semantic_type_name = "EntityRoot"


class ValueObject(OoadClass):
    _semantic_type_name = "ValueObject"


class Repository(OoadClass):
    _semantic_type_name = "Repository"


class DomainEvent(OoadClass):
    _semantic_type_name = "DomainEvent"


class DomainService(OoadClass):
    _semantic_type_name = "DomainService"
