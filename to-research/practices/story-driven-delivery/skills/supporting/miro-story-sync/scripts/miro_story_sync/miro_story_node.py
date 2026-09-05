"""Miro story-node hierarchy.

Subclasses the platform-agnostic abstractions in
``common/diagram_story_sync.diagram_story_node``:

- ``MiroStoryNode``  (base)         -> ``DiagramStoryNode``
- ``MiroEpic``                       -> ``DiagramEpic``
- ``MiroSubEpic``                    -> ``DiagramSubEpic``
- ``MiroStory``                      -> ``DiagramStory``

Layout, comparison, and update-report code lives in ``common`` so the only
thing this file owns is "how does a node turn into a Miro item via the
transport". Each render method walks the domain model, places nodes using
``RowPositions`` from common, and returns a tree of ``MiroStoryNode`` ready
for ``MiroStoryMap`` to flush to the board.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from . import _bootstrap  # noqa: F401

from story_graph_ops.nodes import StoryNode, Epic, SubEpic, Story  # noqa: F401

from diagram_story_sync.diagram_story_node import (
    DiagramStoryNode,
    DiagramEpic,
    DiagramSubEpic,
    DiagramStory,
)
from diagram_story_sync.layout_constants import (
    CELL_SIZE,
    CELL_SPACING,
    EPIC_Y,
    EPIC_HEIGHT,
    SUB_EPIC_HEIGHT,
    BAR_PADDING,
)

AC_HEIGHT = 60
AC_GAP = 10
AC_MIN_WIDTH = 250
AC_WIDTH = AC_MIN_WIDTH
from diagram_story_sync.node_comparison import (
    RowPositions,
    max_sub_epic_depth,
    slug as _slug,
)
from diagram_story_sync.position import Position, Boundary

from .miro_element import MiroElement


__all__ = [
    'MiroStoryNode',
    'MiroEpic',
    'MiroSubEpic',
    'MiroStory',
    'MiroAC',
    'render_ac_for_story',
]


def _has_nested_sub_epics(sub_epic) -> bool:
    return any(isinstance(c, SubEpic) for c in sub_epic.children)


def _ordered_stories(sub_epic) -> List[Story]:
    stories = [c for c in sub_epic.children if isinstance(c, Story)]
    stories.sort(key=lambda s: getattr(s, 'sequential_order', 0) or 0)
    return stories


def _slug_occurrence_counts(stories: List[Story]) -> dict:
    counts: dict = {}
    for story in stories:
        slg = _slug(story.name)
        counts[slg] = counts.get(slg, 0) + 1
    return counts


def _disambiguated_slug(story, slug_counts: dict, seen_slug_counts: dict) -> str:
    slg = _slug(story.name)
    if slug_counts.get(slg, 0) <= 1:
        return slg
    seen_slug_counts[slg] = seen_slug_counts.get(slg, 0) + 1
    return f'{slg}-{seen_slug_counts[slg]}'


@dataclass
class MiroStoryNode(DiagramStoryNode):
    """Miro-specific node holding a ``MiroElement``.

    Mirrors ``DrawIOStoryNode``: position, boundary, fill, stroke, etc. all
    delegate to the held ``MiroElement``, which knows how to serialise to a
    Miro v2 items payload.
    """

    _element: MiroElement = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self._element is None:
            self._element = MiroElement(cell_id=_slug(self.name), value=self.name)

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    @property
    def element(self) -> MiroElement:
        return self._element

    @property
    def position(self) -> Position:
        return self._element.position

    @property
    def boundary(self) -> Boundary:
        return self._element.boundary

    @property
    def fill(self) -> Optional[str]:
        return self._element.fill

    @property
    def stroke(self) -> Optional[str]:
        return self._element.stroke

    @property
    def font_color(self) -> Optional[str]:
        return self._element.font_color

    @property
    def shape(self) -> Optional[str]:
        return self._element.shape

    @property
    def cell_id(self) -> str:
        return self._element.cell_id

    def set_position(self, x: float, y: float) -> None:
        self._element.set_position(x, y)

    def set_size(self, width: float, height: float) -> None:
        self._element.set_size(width, height)

    def add_child(self, child: 'MiroStoryNode') -> None:
        child._parent = self
        self._children.append(child)

    def containment_rules(self) -> dict:
        return {}

    def placement_rules(self) -> dict:
        return {}

    def formatting_rules(self) -> dict:
        return {}

    @classmethod
    def create(cls, domain_node: StoryNode,
               parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError("Subclass must implement create()")

    @classmethod
    def recognizes(cls, element: any) -> bool:
        # Recognition is delegated to ``MiroStoryNodeSerializer`` which keys
        # off the element role tag stored in metadata when reading items
        # back from a Miro board.
        raise NotImplementedError("Subclass must implement recognizes()")

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for child in self._children:
            if hasattr(child, 'collect_all_nodes'):
                nodes.extend(child.collect_all_nodes())
            else:
                nodes.append(child)
        return nodes


@dataclass
class MiroEpic(DiagramEpic, MiroStoryNode):
    """Miro representation of an Epic. Renders as a rounded shape."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: MiroElement = field(default=None, repr=False)

    Y_DEFAULT = EPIC_Y
    X_START = 20

    def __post_init__(self):
        if self.domain_concepts is None:
            self.domain_concepts = []
        DiagramStoryNode.__post_init__(self)
        if self._element is None:
            self._element = MiroElement(cell_id=_slug(self.name), value=self.name)
        self._element.apply_style_for_type('epic')

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    def get_sub_epics(self) -> List['MiroSubEpic']:
        return [c for c in self._children if isinstance(c, MiroSubEpic)]

    @property
    def sub_epics(self) -> List['MiroSubEpic']:
        return self.get_sub_epics()

    def get_stories(self) -> List['MiroStory']:
        stories = []
        for sub_epic in self.get_sub_epics():
            stories.extend(sub_epic.get_all_stories_recursive())
        return stories

    @property
    def all_stories(self) -> List['MiroStory']:
        return self.get_stories()

    def render_from_domain(self, epic: Epic, x_pos: float,
                            rows: Optional[RowPositions] = None,
                            layout_data=None,
                            story_widths: Optional[dict] = None) -> 'MiroEpic':
        """Render epic as a flat horizontal bar spanning its sub-epics."""
        from .miro_story_node_serializer import MiroStoryNodeSerializer

        if rows is None:
            depth = max_sub_epic_depth(epic)
            rows = RowPositions(depth)

        epic_slug = _slug(self.name)
        self._element._cell_id = epic_slug

        cursor_x = x_pos + BAR_PADDING
        for sub_epic in epic.sub_epics:
            miro_se = MiroStoryNodeSerializer.create_sub_epic(
                sub_epic.name, getattr(sub_epic, 'sequential_order', 0) or 0)
            cursor_x = miro_se.render_from_domain(
                sub_epic, cursor_x, depth=0, rows=rows,
                layout_data=layout_data, path_prefix=epic_slug,
                story_widths=story_widths)
            self.add_child(miro_se)
            cursor_x += CELL_SPACING

        if epic.sub_epics:
            cursor_x -= CELL_SPACING

        saved_pos = None
        if layout_data is not None:
            saved_pos = layout_data.position_for(f'EPIC|{self.name}')
        epic_x = saved_pos.x if saved_pos else x_pos
        epic_y = saved_pos.y if saved_pos else EPIC_Y
        self.set_position(epic_x, epic_y)
        self.set_size(max(cursor_x - x_pos + BAR_PADDING, 100), EPIC_HEIGHT)
        return self

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for se in self.get_sub_epics():
            nodes.extend(se.collect_all_nodes())
        return nodes


@dataclass
class MiroSubEpic(DiagramSubEpic, MiroStoryNode):
    """Miro representation of a SubEpic."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: MiroElement = field(default=None, repr=False)

    def __post_init__(self):
        if self.domain_concepts is None:
            self.domain_concepts = []
        DiagramStoryNode.__post_init__(self)
        if self._element is None:
            self._element = MiroElement(cell_id=_slug(self.name), value=self.name)
        self._element.apply_style_for_type('sub_epic')

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    def get_sub_epics(self) -> List['MiroSubEpic']:
        return [c for c in self._children if isinstance(c, MiroSubEpic)]

    def get_stories(self) -> List['MiroStory']:
        return sorted([c for c in self._children if isinstance(c, MiroStory)],
                       key=lambda s: s.sequential_order or 0)

    def get_all_stories_recursive(self) -> List['MiroStory']:
        stories = list(self.get_stories())
        for nested_se in self.get_sub_epics():
            stories.extend(nested_se.get_all_stories_recursive())
        return stories

    def render_from_domain(self, sub_epic, x_cursor: float, depth: int,
                            rows: RowPositions,
                            layout_data=None,
                            path_prefix: str = '',
                            story_widths: Optional[dict] = None) -> float:
        """Render sub-epic as a flat horizontal bar; return right-edge X."""
        se_path = self._build_path(path_prefix)
        self._element._cell_id = se_path

        if _has_nested_sub_epics(sub_epic):
            end_x = self._render_nested_sub_epics(sub_epic, x_cursor, depth, rows,
                                                    layout_data, se_path,
                                                    story_widths=story_widths)
        else:
            end_x = self._render_leaf_stories(sub_epic, x_cursor, rows, se_path,
                                               story_widths=story_widths)

        self.set_position(x_cursor, rows.sub_epic_y(depth))
        self.set_size(max(end_x - x_cursor, CELL_SIZE + 2 * BAR_PADDING),
                       SUB_EPIC_HEIGHT)
        return end_x

    def _build_path(self, path_prefix: str) -> str:
        own_slug = _slug(self.name)
        return f'{path_prefix}/{own_slug}' if path_prefix else own_slug

    def _render_nested_sub_epics(self, sub_epic, x_cursor: float, depth: int,
                                   rows: RowPositions, layout_data,
                                   se_path: str,
                                   story_widths: Optional[dict] = None) -> float:
        from .miro_story_node_serializer import MiroStoryNodeSerializer

        inner_x = x_cursor + BAR_PADDING
        for nested in (c for c in sub_epic.children if isinstance(c, SubEpic)):
            miro_nested = MiroStoryNodeSerializer.create_sub_epic(
                nested.name, getattr(nested, 'sequential_order', 0) or 0)
            inner_x = miro_nested.render_from_domain(
                nested, inner_x, depth + 1, rows, layout_data,
                path_prefix=se_path, story_widths=story_widths,
            )
            self.add_child(miro_nested)
            inner_x += CELL_SPACING
        inner_x -= CELL_SPACING
        return inner_x + BAR_PADDING

    def _render_leaf_stories(self, sub_epic, x_cursor: float,
                              rows: RowPositions, se_path: str,
                              story_widths: Optional[dict] = None) -> float:
        stories = _ordered_stories(sub_epic)
        if not stories:
            return x_cursor + BAR_PADDING + BAR_PADDING

        slug_counts = _slug_occurrence_counts(stories)
        seen_slug_counts: dict = {}
        story_x = x_cursor + BAR_PADDING
        for story in stories:
            base_slug = _disambiguated_slug(story, slug_counts, seen_slug_counts)
            self._add_story_at(story, story_x, rows.story_y, se_path, base_slug)
            ac_w = story_widths.get(story.name, CELL_SIZE) if story_widths else CELL_SIZE
            story_x += max(CELL_SIZE, ac_w) + CELL_SPACING
        story_x -= CELL_SPACING
        return story_x + BAR_PADDING

    def _add_story_at(self, story, story_x: float, story_y: float,
                       se_path: str, base_slug: str) -> None:
        from .miro_story_node_serializer import MiroStoryNodeSerializer

        story_type = getattr(story, 'story_type', 'user') or 'user'
        miro_story = MiroStoryNodeSerializer.create_story(
            story.name,
            getattr(story, 'sequential_order', 0) or 0,
            story_type,
        )
        story_path = f'{se_path}/{base_slug}' if se_path else base_slug
        miro_story.render_from_domain(
            story, story_x, story_y,
            path_prefix=se_path,
            cell_id_override=story_path,
        )
        self.add_child(miro_story)

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for se in self.get_sub_epics():
            nodes.extend(se.collect_all_nodes())
        for story in self.get_stories():
            nodes.extend(story.collect_all_nodes())
        return nodes


@dataclass
class MiroStory(DiagramStory, MiroStoryNode):
    """Miro representation of a Story (sticky note in production)."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: MiroElement = field(default=None, repr=False)

    WIDTH = CELL_SIZE
    HEIGHT = CELL_SIZE

    STORY_TYPE_STYLES = {
        'user': 'story_user',
        None: 'story_user',
        '': 'story_user',
        'system': 'story_system',
        'technical': 'story_technical',
    }

    def __post_init__(self):
        if self.users is None:
            self.users = []
        DiagramStoryNode.__post_init__(self)
        if self._element is None:
            self._element = MiroElement(cell_id=_slug(self.name), value=self.name)
        style_key = self.STORY_TYPE_STYLES.get(self.story_type, 'story_user')
        self._element.apply_style_for_type(style_key)

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    def render_from_domain(self, story, x_pos: float, story_y: float,
                            path_prefix: str = '',
                            cell_id_override: Optional[str] = None) -> 'MiroStory':
        story_path = cell_id_override if cell_id_override else (
            f'{path_prefix}/{_slug(self.name)}' if path_prefix else _slug(self.name))
        self._element._cell_id = story_path
        self.set_position(x_pos, story_y)
        self.set_size(CELL_SIZE, CELL_SIZE)
        return self

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for child in self._children:
            if hasattr(child, 'collect_all_nodes'):
                nodes.extend(child.collect_all_nodes())
        return nodes


@dataclass
class MiroAC(MiroStoryNode):
    """One acceptance-criteria text box rendered below a story."""

    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: MiroElement = field(default=None, repr=False)

    WIDTH = AC_WIDTH
    HEIGHT = AC_HEIGHT

    def __post_init__(self):
        DiagramStoryNode.__post_init__(self)
        if self._element is None:
            self._element = MiroElement(cell_id=_slug(self.name), value=self.name)
        self._element.apply_style_for_type('ac')

    def render_from_domain(self, text: str, x: float, y: float,
                            cell_id: str) -> 'MiroAC':
        self._element._cell_id = cell_id
        self._element._value = text
        self.set_position(x, y)
        self.set_size(AC_WIDTH, AC_HEIGHT)
        return self

    def collect_all_nodes(self) -> list:
        return [self]

    @classmethod
    def create(cls, domain_node: StoryNode,
               parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError('MiroAC is created via render_ac_for_story')

    @classmethod
    def recognizes(cls, element: any) -> bool:
        raise NotImplementedError('MiroAC read-back is not supported')


def render_ac_for_story(story_node: MiroStory, ac_texts: List[str]) -> None:
    """Add MiroAC children below story_node for each AC text."""
    from .miro_story_node_serializer import MiroStoryNodeSerializer

    x = story_node.position.x
    y = story_node.position.y + CELL_SIZE + AC_GAP
    for i, text in enumerate(ac_texts):
        if not text or not str(text).strip():
            continue
        cell_id = f'{story_node.cell_id}/ac-{i}'
        ac_node = MiroStoryNodeSerializer.create_ac(str(text).strip(), float(i))
        ac_node.render_from_domain(str(text).strip(), x, y, cell_id)
        story_node.add_child(ac_node)
        y += AC_HEIGHT + AC_GAP
