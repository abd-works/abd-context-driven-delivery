"""CodeQL channel. Reads are the channel's own. No tree walk from a parent."""

from practices.ddd.model.nodes import (
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


class CodeqlDomainNode:
    def plain_name(self, text: str) -> str:
        return text.replace("**", "").strip()

    def building_block_type(self, kind: str) -> type:
        return {
            "Entity": Entity,
            "ValueObject": ValueObject,
            "Repository": Repository,
            "DomainEvent": DomainEvent,
            "DomainService": DomainService,
            "Specification": Specification,
            "Factory": Factory,
        }.get(kind, Entity)


class CodeqlBoundedContextMap(BoundedContextMap, CodeqlDomainNode):
    def __init__(self, source: BoundedContextMap | None = None) -> None:
        super().__init__(source)
        self.bounded_context_type = CodeqlBoundedContext
        self.aggregate_type = CodeqlAggregate


class CodeqlBoundedContext(BoundedContext, CodeqlDomainNode):
    pass


class CodeqlAggregate(Aggregate, CodeqlDomainNode):
    pass


class CodeqlIntegration(Integration, CodeqlDomainNode):
    pass


class CodeqlEntity(Entity, CodeqlDomainNode):
    pass


class CodeqlInvariantObject(InvariantObject, CodeqlDomainNode):
    pass


class CodeqlValueObject(ValueObject, CodeqlDomainNode):
    pass


class CodeqlRepository(Repository, CodeqlDomainNode):
    pass


class CodeqlDomainService(DomainService, CodeqlDomainNode):
    pass


class CodeqlDomainEvent(DomainEvent, CodeqlDomainNode):
    pass


class CodeqlSpecification(Specification, CodeqlDomainNode):
    pass


class CodeqlFactory(Factory, CodeqlDomainNode):
    pass
