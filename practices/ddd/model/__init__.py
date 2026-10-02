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

def load_bounded_context_map(root):
    """Load bounded contexts from a workspace bounded-context-map.md. Empty when the file is absent."""
    from pathlib import Path

    workspace = Path(root)
    preferred = (
        workspace / "domain" / ".context" / "bounded-context-map.md",
        workspace / "domain" / "bounded-context-map.md",
        workspace / ".context" / "bounded-context-map.md",
        workspace / "bounded-context-map.md",
    )
    path = next((item for item in preferred if item.is_file()), None)
    if path is None:
        return []
    from practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

    return MarkdownBoundedContextMap().load(str(path)).contexts


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
    "load_bounded_context_map",
]
