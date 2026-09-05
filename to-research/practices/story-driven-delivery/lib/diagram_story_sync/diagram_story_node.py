"""Platform-agnostic diagram node hierarchy.

Sits between the domain model (``story_graph_ops.nodes``) and platform-specific
diagram nodes (``DrawIOStoryNode``, ``MiroStoryNode``, ...). Holds positioning,
containment, and formatting **rules** that do not depend on a specific
diagramming tool. Backends subclass ``DiagramEpic`` / ``DiagramSubEpic`` /
``DiagramStory`` / ``DiagramIncrement`` and implement element creation,
serialization, and recognition.
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from . import bootstrap  # noqa: F401

from story_graph_ops.nodes import StoryNode, Epic, SubEpic, Story  # noqa: E402

from .position import Position, Boundary
from .layout_constants import EPIC_Y, EPIC_HEIGHT, SUB_EPIC_HEIGHT, SPACING
from .style_defaults import STYLE_DEFAULTS, STORY_TYPE_STYLE_KEYS

if TYPE_CHECKING:
    from story_graph_ops.nodes import Increment


@dataclass
class DiagramStoryNode(StoryNode):
    """Platform-agnostic diagram node with positioning and formatting rules.

    Inherits from ``StoryNode`` and adds diagram-specific properties and
    methods for positioning, containment, and formatting. Subclasses
    (``DiagramEpic`` etc.) provide rules per node kind; backend-specific
    implementations layer on read/write capabilities.
    """

    @property
    @abstractmethod
    def position(self) -> Position:
        """Get the node's position in the diagram."""

    @property
    @abstractmethod
    def boundary(self) -> Boundary:
        """Get the node's boundary (position plus size)."""

    @abstractmethod
    def containment_rules(self) -> dict:
        """Return containment rules for this node type.

        ``{'allowed_parents': [...], 'contains_check': fn(point) -> bool}``.
        """

    @abstractmethod
    def placement_rules(self) -> dict:
        """Return placement rules (X/Y calculation, sibling spacing)."""

    @abstractmethod
    def formatting_rules(self) -> dict:
        """Return formatting rules (fill, stroke, font, shape)."""

    def compute_container_dimensions_from_children(
        self, spacing: float = SPACING
    ) -> Boundary:
        """Compute container boundary from children positions.

        Default returns the current boundary; subclasses override when they
        need a width that spans their children.
        """
        return self.boundary

    @classmethod
    @abstractmethod
    def create(cls, domain_node: StoryNode,
               parent: Optional['DiagramStoryNode'] = None):
        """Create a diagram node from a domain node.

        Mirrors ``StoryNode.create``; each subclass picks the correct
        diagram-node type for the supplied domain node.
        """

    def add_child(self, child: 'DiagramStoryNode') -> None:
        child._parent = self
        self._children.append(child)

    def move_to(self, new_parent: 'DiagramStoryNode') -> None:
        if self._parent:
            self._parent._children.remove(self)
        new_parent.add_child(self)

    def delete(self) -> None:
        if self._parent:
            self._parent._children.remove(self)
            self._parent = None

    def rename(self, new_name: str) -> None:
        self.name = new_name

    @classmethod
    @abstractmethod
    def recognizes(cls, element: any) -> bool:
        """Return ``True`` when ``element`` represents this node kind.

        Used by backends during diagram loading; the ``element`` argument is
        backend-specific (``DrawIOElement``, Miro item dict, ...).
        """


@dataclass
class DiagramEpic(Epic, DiagramStoryNode):
    """Diagram representation of an Epic with positioning and formatting."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def containment_rules(self) -> dict:
        return {
            'allowed_parents': [],
            'contains_sub_epics': True,
            'contains_stories': False,
        }

    def placement_rules(self) -> dict:
        return {
            'y': EPIC_Y,
            'height': EPIC_HEIGHT,
            'span_children': True,
        }

    def formatting_rules(self) -> dict:
        return dict(STYLE_DEFAULTS['epic'])

    @classmethod
    def create(cls, domain_node: Epic,
               parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError("Subclass must implement create()")

    @classmethod
    def recognizes(cls, element: any) -> bool:
        raise NotImplementedError("Subclass must implement recognizes()")


@dataclass
class DiagramSubEpic(SubEpic, DiagramStoryNode):
    """Diagram representation of a SubEpic with positioning and formatting."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def containment_rules(self) -> dict:
        return {
            'allowed_parents': [DiagramEpic, DiagramSubEpic],
            'contains_sub_epics': True,
            'contains_stories': True,
        }

    def placement_rules(self) -> dict:
        return {
            'y_offset': 75,
            'height': SUB_EPIC_HEIGHT,
            'span_children': True,
        }

    def formatting_rules(self) -> dict:
        return dict(STYLE_DEFAULTS['sub_epic'])

    @classmethod
    def create(cls, domain_node: SubEpic,
               parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError("Subclass must implement create()")

    @classmethod
    def recognizes(cls, element: any) -> bool:
        raise NotImplementedError("Subclass must implement recognizes()")


@dataclass
class DiagramStory(Story, DiagramStoryNode):
    """Diagram representation of a Story with positioning and formatting."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def containment_rules(self) -> dict:
        return {
            'allowed_parents': [DiagramSubEpic],
            'contains_sub_epics': False,
            'contains_stories': False,
        }

    def placement_rules(self) -> dict:
        from .layout_constants import CELL_SIZE, CELL_SPACING

        return {
            'size': CELL_SIZE,
            'spacing': CELL_SPACING,
            'layout': 'left-to-right',
        }

    def formatting_rules(self) -> dict:
        story_type = getattr(self, 'story_type', 'user')
        style_key = STORY_TYPE_STYLE_KEYS.get(story_type, 'story_user')
        return dict(STYLE_DEFAULTS[style_key])

    @classmethod
    def create(cls, domain_node: Story,
               parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError("Subclass must implement create()")

    @classmethod
    def recognizes(cls, element: any) -> bool:
        raise NotImplementedError("Subclass must implement recognizes()")


@dataclass
class DiagramIncrement(DiagramStoryNode):
    """Diagram representation of an Increment lane.

    ``Increment`` is not yet a full ``StoryNode`` in the domain model, so this
    class does not inherit a domain Increment type. Backends layer on the
    rendering pieces.
    """

    _parent: Optional[StoryNode] = field(default=None, repr=False)
    priority: int = 1
    stories: List = field(default_factory=list)

    @property
    def children(self) -> List[StoryNode]:
        return []

    def containment_rules(self) -> dict:
        return {
            'allowed_parents': [],
            'contains_sub_epics': False,
            'contains_stories': False,
        }

    def placement_rules(self) -> dict:
        return {
            'layout': 'horizontal-lane',
            'ordered_by': 'priority',
            'fixed_height': True,
        }

    def formatting_rules(self) -> dict:
        return dict(STYLE_DEFAULTS['increment_lane'])

    @classmethod
    def create(cls, domain_node: 'Increment',
               parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError("Subclass must implement create()")

    @classmethod
    def recognizes(cls, element: any) -> bool:
        raise NotImplementedError("Subclass must implement recognizes()")
