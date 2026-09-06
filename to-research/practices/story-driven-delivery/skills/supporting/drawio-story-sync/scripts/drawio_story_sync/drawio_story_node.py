"""DrawIO-specific story node hierarchy and structural diff plumbing.

Builds on the platform-agnostic abstractions in
``common/diagram_story_sync``: ``DiagramStoryNode`` / ``DiagramEpic`` /
``DiagramSubEpic`` / ``DiagramStory`` / ``DiagramIncrement`` provide
positioning, formatting, and containment rules; ``node_comparison`` provides
``compare_node_lists`` / ``collect_all_names`` / ``RowPositions`` /
``max_sub_epic_depth``.

This module adds the DrawIO XML serialization layer (via ``DrawIOElement``)
and a DrawIO-specific predicate (``_drawio_is_manual_subtree_root``) that
recognises manually drawn cells whose ``cell_id`` lacks a ``/`` path prefix.
"""
from typing import List, Optional, Set
from dataclasses import dataclass, field

from . import _bootstrap  # noqa: F401

from story_graph_ops.nodes import StoryNode, Epic, SubEpic, Story  # noqa: F401
from story_graph_ops.domain import DomainConcept, StoryUser  # noqa: F401

from diagram_story_sync.diagram_story_node import (
    DiagramStoryNode,
    DiagramEpic,
    DiagramSubEpic,
    DiagramStory,
    DiagramIncrement,
)
from diagram_story_sync.layout_constants import (
    CELL_SIZE,
    CELL_SPACING,
    EPIC_Y,
    EPIC_HEIGHT,
    SUB_EPIC_HEIGHT,
    ROW_GAP,
    ACTOR_GAP,
    BAR_PADDING,
    SPACING,
    CONTAINER_PADDING,
)
from diagram_story_sync.node_comparison import (
    RowPositions as _CommonRowPositions,
    collect_all_names as _common_collect_all_names,
    compare_node_lists as _common_compare_node_lists,
    max_sub_epic_depth as _common_max_sub_epic_depth,
    report_leaf_story_group_reorder_if_needed as _common_report_leaf_story_group_reorder_if_needed,
    report_sub_epic_sibling_reorder_if_needed as _common_report_sub_epic_sibling_reorder_if_needed,
    slug as _common_slug,
)

from .drawio_element import DrawIOElement, STYLE_DEFAULTS
from .story_io_position import Position, Boundary
from .update_report import UpdateReport


_slug = _common_slug


# Backward-compat aliases kept so ``drawio_story_map.py`` and tests that import
# private names from this module keep working unchanged.
_RowPositions = _CommonRowPositions
_collect_all_names = _common_collect_all_names
_max_sub_epic_depth = _common_max_sub_epic_depth


def _drawio_is_manual_subtree_root(ext_node) -> bool:
    """Spot DrawIO epics / sub-epics that the user drew by hand.

    Sub-epics and epics whose ``cell_id`` lacks a ``/`` were created in the
    DrawIO canvas (DrawIO assigns numeric IDs), not produced by our renderer
    (which builds ``epic-name/sub-epic-name`` paths). Such nodes must not be
    paired as renames against unmatched originals — they are genuinely new.

    Stories are excluded because test helpers and simplified diagrams may use
    flat IDs even for valid renames.
    """
    cell_id = getattr(ext_node, 'cell_id', '') or ''
    if not cell_id:
        return False
    if '/' in cell_id:
        return False
    return isinstance(ext_node, (DrawIOEpic, DrawIOSubEpic))


def _compare_node_lists(extracted, original, report, parent_name='',
                         recurse=False,
                         all_extracted_names: Set[str] = None,
                         all_original_names: Set[str] = None,
                         extracted_story_to_inc: dict = None,
                         original_story_to_inc: dict = None) -> None:
    """DrawIO wrapper around the common comparison routine.

    Adds the DrawIO predicate that vetoes rename pairing for manually drawn
    cells; everything else is delegated.
    """
    _common_compare_node_lists(
        extracted, original, report,
        parent_name=parent_name,
        recurse=recurse,
        all_extracted_names=all_extracted_names,
        all_original_names=all_original_names,
        extracted_story_to_inc=extracted_story_to_inc,
        original_story_to_inc=original_story_to_inc,
        is_manual_subtree_root=_drawio_is_manual_subtree_root,
    )


def _report_sub_epic_sibling_reorder_if_needed(parent_name, extracted_sub_epics,
                                                original_sub_epics, report):
    _common_report_sub_epic_sibling_reorder_if_needed(
        parent_name, extracted_sub_epics, original_sub_epics, report
    )


def _report_leaf_story_group_reorder_if_needed(drawio_sub_epic, original_sub_epic,
                                                unique_stories_in_diagram_order, report):
    _common_report_leaf_story_group_reorder_if_needed(
        drawio_sub_epic, original_sub_epic, unique_stories_in_diagram_order, report
    )


# ---------------------------------------------------------------------------
# DrawIO Story Nodes
# ---------------------------------------------------------------------------

@dataclass
class DrawIOStoryNode(DiagramStoryNode):
    """DrawIO-specific node handling XML read/write.

    Inherits from ``DiagramStoryNode`` (platform-agnostic positioning /
    formatting) and adds DrawIO XML serialization via ``DrawIOElement``.
    """
    _element: DrawIOElement = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self._element is None:
            self._element = DrawIOElement(cell_id=_slug(self.name), value=self.name)

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    @property
    def element(self) -> DrawIOElement:
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

    def set_position(self, x: float, y: float):
        self._element.set_position(x, y)

    def set_size(self, width: float, height: float):
        self._element.set_size(width, height)

    def add_child(self, child: 'DrawIOStoryNode'):
        child._parent = self
        self._children.append(child)

    def compute_container_dimensions_from_children(self, spacing: float = SPACING) -> Boundary:
        return self._element.boundary

    def containment_rules(self) -> dict:
        return {}

    def placement_rules(self) -> dict:
        return {}

    def formatting_rules(self) -> dict:
        return {}

    @classmethod
    def create(cls, domain_node: StoryNode, parent: Optional['DiagramStoryNode'] = None):
        raise NotImplementedError("Subclass must implement create()")

    @classmethod
    def recognizes(cls, element: any) -> bool:
        raise NotImplementedError("Subclass must implement recognizes()")

    def _saved_position_for(self, key: str, layout_data) -> Optional[Position]:
        if layout_data:
            return layout_data.position_for(key)
        return None

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for child in self._children:
            if hasattr(child, 'collect_all_nodes'):
                nodes.extend(child.collect_all_nodes())
            else:
                nodes.append(child)
        return nodes


@dataclass
class DrawIOEpic(DiagramEpic, DrawIOStoryNode):
    """DrawIO representation of an Epic with XML serialization."""
    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: DrawIOElement = field(default=None, repr=False)

    Y_DEFAULT = EPIC_Y
    X_START = 20
    SUB_EPIC_Y_OFFSET = ROW_GAP + EPIC_HEIGHT

    def __post_init__(self):
        if self.domain_concepts is None:
            self.domain_concepts = []
        DiagramStoryNode.__post_init__(self)
        if self._element is None:
            self._element = DrawIOElement(cell_id=_slug(self.name), value=self.name)
        self._element.apply_style_for_type('epic')

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    def get_sub_epics(self) -> List['DrawIOSubEpic']:
        return [c for c in self._children if isinstance(c, DrawIOSubEpic)]

    @property
    def sub_epics(self) -> List['DrawIOSubEpic']:
        return self.get_sub_epics()

    def get_stories(self) -> List['DrawIOStory']:
        stories = []
        for sub_epic in self.get_sub_epics():
            stories.extend(sub_epic.get_all_stories_recursive())
        return stories

    @property
    def all_stories(self) -> List['DrawIOStory']:
        return self.get_stories()

    def render_from_domain(self, epic: Epic, x_pos: float,
                            rows: _RowPositions = None,
                            layout_data=None,
                            skip_stories: bool = False,
                            story_widths: dict = None,
                            render_ac: bool = False) -> 'DrawIOEpic':
        """Render epic as a flat horizontal bar spanning its sub-epics.

        The epic does NOT visually contain its sub-epics; it sits on its own
        row and its width spans from the first to the last sub-epic
        underneath it.

        When *skip_stories* is True sub-epics are rendered without story cells
        (used by increments view). When *story_widths* is provided
        (exploration view), stories are spaced apart based on their widest AC
        box width.
        """
        from .drawio_story_node_serializer import DrawIOStoryNodeSerializer

        if rows is None:
            depth = _max_sub_epic_depth(epic)
            rows = _RowPositions(depth)

        epic_slug = _slug(self.name)
        self._element._cell_id = epic_slug

        cursor_x = x_pos + BAR_PADDING
        for sub_epic in epic.sub_epics:
            drawio_se = DrawIOStoryNodeSerializer.create_sub_epic(
                sub_epic.name, getattr(sub_epic, 'sequential_order', 0) or 0)
            cursor_x = drawio_se.render_from_domain(
                sub_epic, cursor_x, depth=0, rows=rows,
                layout_data=layout_data, path_prefix=epic_slug,
                skip_stories=skip_stories,
                story_widths=story_widths,
                render_ac=render_ac)
            self.add_child(drawio_se)
            cursor_x += CELL_SPACING

        if epic.sub_epics:
            cursor_x -= CELL_SPACING

        saved = self._saved_position_for(f'EPIC|{self.name}', layout_data)
        epic_x = saved.x if saved else x_pos
        epic_y = saved.y if saved else EPIC_Y
        self.set_position(epic_x, epic_y)
        self.set_size(max(cursor_x - x_pos + BAR_PADDING, 100), EPIC_HEIGHT)
        return self

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for se in self.get_sub_epics():
            nodes.extend(se.collect_all_nodes())
        return nodes

    def _compare_children(self, original_epic, report: UpdateReport, *,
                          all_extracted_names: Set[str] = None,
                          all_original_names: Set[str] = None,
                          extracted_story_to_inc: dict = None,
                          original_story_to_inc: dict = None):
        _compare_node_lists(self.get_sub_epics(), original_epic.sub_epics,
                            report, parent_name=self.name, recurse=True,
                            all_extracted_names=all_extracted_names,
                            all_original_names=all_original_names,
                            extracted_story_to_inc=extracted_story_to_inc,
                            original_story_to_inc=original_story_to_inc)
        _report_sub_epic_sibling_reorder_if_needed(
            self.name,
            self.get_sub_epics(),
            list(original_epic.sub_epics),
            report,
        )


@dataclass
class DrawIOSubEpic(DiagramSubEpic, DrawIOStoryNode):
    """DrawIO representation of a SubEpic with XML serialization."""
    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: DrawIOElement = field(default=None, repr=False)

    Y_OFFSET_FROM_PARENT = SUB_EPIC_HEIGHT + ROW_GAP
    STORY_Y_OFFSET = 0

    def __post_init__(self):
        if self.domain_concepts is None:
            self.domain_concepts = []
        DiagramStoryNode.__post_init__(self)
        if self._element is None:
            self._element = DrawIOElement(cell_id=_slug(self.name), value=self.name)
        self._element.apply_style_for_type('sub_epic')
        if not hasattr(self, 'test_file'):
            self.test_file = None

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    def get_sub_epics(self) -> List['DrawIOSubEpic']:
        return [c for c in self._children if isinstance(c, DrawIOSubEpic)]

    def get_stories(self) -> List['DrawIOStory']:
        return sorted([c for c in self._children if isinstance(c, DrawIOStory)],
                       key=lambda s: s.sequential_order or 0)

    def get_all_stories_recursive(self) -> List['DrawIOStory']:
        stories = list(self.get_stories())
        for nested_se in self.get_sub_epics():
            stories.extend(nested_se.get_all_stories_recursive())
        return stories

    @property
    def all_stories(self) -> List['DrawIOStory']:
        return self.get_stories()

    def render_from_domain(self, sub_epic, x_cursor: float, depth: int,
                            rows: _RowPositions,
                            layout_data=None,
                            path_prefix: str = '',
                            skip_stories: bool = False,
                            story_widths: dict = None,
                            render_ac: bool = False) -> float:
        """Render sub-epic as a flat horizontal bar.

        Returns the X coordinate of the right edge of this sub-epic's content
        so the caller knows where to place the next sibling.

        ``skip_stories=True`` computes width from the number of domain
        stories without creating cells (increments view). ``story_widths``
        causes per-story spacing to use the widest AC box (exploration view).
        """
        from .drawio_story_node_serializer import DrawIOStoryNodeSerializer

        se_path = f'{path_prefix}/{_slug(self.name)}' if path_prefix else _slug(self.name)
        self._element._cell_id = se_path

        nested = [c for c in sub_epic.children if isinstance(c, SubEpic)]
        start_x = x_cursor

        if nested:
            inner_x = x_cursor + BAR_PADDING
            for n in nested:
                drawio_n = DrawIOStoryNodeSerializer.create_sub_epic(
                    n.name, getattr(n, 'sequential_order', 0) or 0)
                inner_x = drawio_n.render_from_domain(
                    n, inner_x, depth + 1, rows, layout_data,
                    path_prefix=se_path,
                    skip_stories=skip_stories,
                    story_widths=story_widths,
                    render_ac=render_ac)
                self.add_child(drawio_n)
                inner_x += CELL_SPACING
            inner_x -= CELL_SPACING
            end_x = inner_x + BAR_PADDING
        else:
            stories = [c for c in sub_epic.children if isinstance(c, Story)]
            stories.sort(key=lambda s: getattr(s, 'sequential_order', 0) or 0)

            slug_counts: dict = {}
            for s in stories:
                slg = _slug(s.name)
                slug_counts[slg] = slug_counts.get(slg, 0) + 1

            if skip_stories:
                story_count = len(stories)
                if story_count:
                    content_width = story_count * CELL_SIZE + (story_count - 1) * CELL_SPACING
                else:
                    content_width = CELL_SIZE
                end_x = x_cursor + BAR_PADDING + content_width + BAR_PADDING
            else:
                se_saved = self._saved_position_for(f'SUB_EPIC|{self.name}', layout_data)
                se_right = (se_saved.x + layout_data.boundary_for(f'SUB_EPIC|{self.name}').width) if (se_saved and layout_data and layout_data.boundary_for(f'SUB_EPIC|{self.name}')) else None
                se_left = x_cursor + BAR_PADDING

                story_x = se_left
                story_y = rows.story_y
                seen_actors: set = set()
                seen_slugs: dict = {}
                for story in stories:
                    story_type = getattr(story, 'story_type', 'user') or 'user'
                    drawio_story = DrawIOStoryNodeSerializer.create_story(
                        story.name, getattr(story, 'sequential_order', 0) or 0, story_type)
                    slg = _slug(drawio_story.name)
                    if slug_counts.get(slg, 0) > 1:
                        seen_slugs[slg] = seen_slugs.get(slg, 0) + 1
                        base = f'{slg}-{seen_slugs[slg]}'
                    else:
                        base = slg
                    story_path = f'{se_path}/{base}' if se_path else base
                    has_saved = layout_data and layout_data.position_for(story_path)
                    if has_saved:
                        drawio_story.render_from_domain(
                            story, story_x, story_y, rows.actor_y,
                            path_prefix=se_path, seen_actors=seen_actors,
                            layout_data=layout_data, render_ac=render_ac,
                            cell_id_override=story_path)
                    else:
                        if se_right and story_x + CELL_SIZE > se_right:
                            story_x = se_left
                            story_y += CELL_SIZE + CELL_SPACING
                        drawio_story.render_from_domain(
                            story, story_x, story_y, rows.actor_y,
                            path_prefix=se_path, seen_actors=seen_actors,
                            layout_data=None, render_ac=render_ac,
                            cell_id_override=story_path)
                    self.add_child(drawio_story)
                    ac_w = story_widths.get(story.name, CELL_SIZE) if story_widths else CELL_SIZE
                    story_x += max(CELL_SIZE, ac_w) + CELL_SPACING
                if stories:
                    story_x -= CELL_SPACING
                end_x = story_x + BAR_PADDING

        se_y = rows.sub_epic_y(depth)
        self.set_position(start_x, se_y)
        self.set_size(max(end_x - start_x, CELL_SIZE + 2 * BAR_PADDING),
                       SUB_EPIC_HEIGHT)
        return end_x

    def collect_all_nodes(self) -> list:
        nodes = [self]
        for se in self.get_sub_epics():
            nodes.extend(se.collect_all_nodes())
        for story in self.get_stories():
            nodes.extend(story.collect_all_nodes())
        return nodes

    def _compare_children(self, original_sub_epic, report: UpdateReport, *,
                          all_extracted_names: Set[str] = None,
                          all_original_names: Set[str] = None,
                          extracted_story_to_inc: dict = None,
                          original_story_to_inc: dict = None):
        orig_nested = [c for c in original_sub_epic._children if isinstance(c, SubEpic)]
        _compare_node_lists(self.get_sub_epics(), orig_nested,
                            report, parent_name=self.name, recurse=True,
                            all_extracted_names=all_extracted_names,
                            all_original_names=all_original_names,
                            extracted_story_to_inc=extracted_story_to_inc,
                            original_story_to_inc=original_story_to_inc)
        _report_sub_epic_sibling_reorder_if_needed(
            self.name, self.get_sub_epics(), orig_nested, report)

        # Deduplicate extracted stories by name (a story can appear in multiple
        # increment lanes; keep the first occurrence).
        seen_names: set = set()
        unique_stories: list = []
        for s in self.get_stories():
            if s.name not in seen_names:
                seen_names.add(s.name)
                unique_stories.append(s)

        orig_stories = [c for c in original_sub_epic.children if isinstance(c, Story)]
        _compare_node_lists(unique_stories, orig_stories,
                            report, parent_name=self.name, recurse=False,
                            all_extracted_names=all_extracted_names,
                            all_original_names=all_original_names,
                            extracted_story_to_inc=extracted_story_to_inc,
                            original_story_to_inc=original_story_to_inc)
        _report_leaf_story_group_reorder_if_needed(
            self, original_sub_epic, unique_stories, report)


@dataclass
class DrawIOStory(DiagramStory, DrawIOStoryNode):
    """DrawIO representation of a Story with XML serialization."""
    _parent: Optional[StoryNode] = field(default=None, repr=False)
    _element: DrawIOElement = field(default=None, repr=False)

    WIDTH = CELL_SIZE
    HEIGHT = CELL_SIZE
    ACTOR_HEIGHT = CELL_SIZE
    ACTOR_SPACING = 2
    AC_MIN_WIDTH = 250
    AC_HEIGHT = 60
    AC_SPACING_Y = 10
    AC_CHAR_WIDTH = 6
    AC_PADDING = 10

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
            self._element = DrawIOElement(cell_id=_slug(self.name), value=self.name)
        style_key = self.STORY_TYPE_STYLES.get(self.story_type, 'story_user')
        self._element.apply_style_for_type(style_key)
        self._actor_elements: List[DrawIOElement] = []
        self._ac_elements: List[DrawIOElement] = []

    @property
    def children(self) -> List['StoryNode']:
        return list(self._children)

    def render_from_domain(self, story, x_pos: float, story_y: float,
                            actor_y: float = 0,
                            path_prefix: str = '',
                            seen_actors: set = None,
                            layout_data=None,
                            render_ac: bool = False,
                            cell_id_override: str = None) -> 'DrawIOStory':
        story_path = cell_id_override if cell_id_override else (
            f'{path_prefix}/{_slug(self.name)}' if path_prefix else _slug(self.name))
        self._element._cell_id = story_path

        saved = self._saved_position_for(story_path, layout_data)
        final_x = saved.x if saved else x_pos
        final_y = saved.y if saved else story_y
        self.set_position(final_x, final_y)
        self.set_size(CELL_SIZE, CELL_SIZE)

        # Actors directly above this story; ``seen_actors`` (per sub-epic row)
        # skips duplicate persona names so the outline stays compact.
        users = getattr(story, 'users', []) or []
        for user in users:
            user_name = user.name if hasattr(user, 'name') else str(user)
            if seen_actors is not None:
                if user_name in seen_actors:
                    continue
                seen_actors.add(user_name)
            actor = DrawIOElement(
                cell_id=f'{story_path}/actor-{_slug(user_name)}',
                value=user_name)
            actor.apply_style_for_type('actor')
            actor.set_position(x_pos, actor_y)
            actor.set_size(CELL_SIZE, CELL_SIZE)
            self._actor_elements.append(actor)

        if render_ac:
            self.render_ac_boxes(story)

        return self

    @staticmethod
    def compute_ac_width(domain_story) -> float:
        """Return the horizontal space needed for AC boxes of this story.

        All AC boxes use ``AC_MIN_WIDTH`` because text wraps inside the box.
        Returns ``CELL_SIZE`` if the story has no AC.
        """
        ac_list = getattr(domain_story, 'acceptance_criteria', []) or []
        if not ac_list:
            return CELL_SIZE
        return DrawIOStory.AC_MIN_WIDTH

    @staticmethod
    def _raw_ac_plain(ac) -> str:
        if hasattr(ac, 'name') and ac.name:
            return ac.name
        if isinstance(ac, str):
            return ac
        if isinstance(ac, dict):
            return ac.get('name', ac.get('description', ''))
        return str(ac) if ac else ''

    def render_ac_boxes(self, domain_story) -> List[DrawIOElement]:
        """Create acceptance-criteria ``DrawIOElement`` boxes below this story."""
        from .ac_text_format import ac_cell_height_px, format_ac_diagram_html

        ac_list = getattr(domain_story, 'acceptance_criteria', []) or []
        if not ac_list:
            return []

        elements = []
        ac_y = self.position.y + self.HEIGHT + self.AC_SPACING_Y
        font_size = 8
        line_px = max(13.0, float(font_size) * 1.4)

        for idx, ac in enumerate(ac_list):
            raw = self._raw_ac_plain(ac)
            if not raw or not str(raw).strip():
                continue
            text = format_ac_diagram_html(raw)
            if not text:
                continue
            ac_elem = DrawIOElement(
                cell_id=f'{self.cell_id}/ac-{idx}',
                value=text)
            ac_elem.apply_style_for_type('acceptance_criteria')
            ac_elem.set_position(self.position.x, ac_y)
            h = ac_cell_height_px(
                text,
                min_px=float(self.AC_HEIGHT),
                line_px=line_px,
                pad_px=float(self.AC_PADDING) * 2.0 + 18.0,
            )
            ac_elem.set_size(self.AC_MIN_WIDTH, h)
            elements.append(ac_elem)
            ac_y += h + self.AC_SPACING_Y

        self._ac_elements = elements
        return elements

    def collect_all_nodes(self) -> list:
        nodes = [self]
        nodes.extend(self._actor_elements)
        nodes.extend(self._ac_elements)
        return nodes


class DrawIOIncrementLane:
    """A horizontal increment lane in the DrawIO story map diagram.

    Lanes are intentionally compact — just enough vertical space for one row
    of story sticky notes.  The label sits at the same vertical offset as the
    stories so the two elements align side-by-side rather than stacking.

    Actors are NOT rendered inside lanes.  The outline above already carries
    persona information via actor chips; duplicating them in every lane makes
    compact lanes taller than necessary.
    """

    # Compact single-row layout: top-padding + CELL_SIZE + bottom-padding
    _LANE_PADDING = 10
    LANE_HEIGHT = CELL_SIZE + 2 * _LANE_PADDING   # 70 (was 155)

    # Label sits flush with the story row (left side of the lane)
    LABEL_Y_OFFSET = _LANE_PADDING                 # 10 (was 5)
    LABEL_HEIGHT = CELL_SIZE                       # 50 (was 30) — same as story square
    LABEL_WIDTH = 150

    # Stories start at the same Y offset as the label
    STORY_Y_OFFSET = _LANE_PADDING                 # 10 (was 95)

    def __init__(self, name: str, priority: int, story_names: list):
        self.name = name
        self.priority = priority
        self.story_names = set(story_names)
        self._lane_element: Optional[DrawIOElement] = None
        self._label_element: Optional[DrawIOElement] = None
        self._story_copies: List[DrawIOElement] = []
        self._actor_elements: List[DrawIOElement] = []

    def render(self, index: int, y_start: float, total_width: float,
               stories: List['DrawIOStory'],
               domain_stories: Optional[list] = None) -> float:
        """Render a compact increment lane containing one row of story sticky notes.

        ``stories`` are ``DrawIOStory`` objects from the outline render (used
        for position and style).  ``domain_stories`` is accepted for API
        compatibility but is no longer used — actors live in the outline above
        the lanes rather than inside each lane.
        """
        lane_y = y_start + index * self.LANE_HEIGHT

        lane_slug = _slug(self.name)
        self._lane_element = DrawIOElement(cell_id=f'inc-lane/{lane_slug}', value='')
        self._lane_element.apply_style_for_type('increment_lane')
        self._lane_element.set_position(0, lane_y)
        self._lane_element.set_size(total_width + 40, self.LANE_HEIGHT)

        self._label_element = DrawIOElement(cell_id=f'inc-label/{lane_slug}', value=self.name)
        self._label_element.apply_style_for_type('increment_lane')
        self._label_element.set_position(5, lane_y + self.LABEL_Y_OFFSET)
        self._label_element.set_size(self.LABEL_WIDTH, self.LABEL_HEIGHT)

        self._story_copies = []
        self._actor_elements = []  # always empty — actors live in the outline above
        for story in stories:
            if story.name in self.story_names:
                copy = DrawIOElement(
                    cell_id=f'inc-lane/{lane_slug}/{story.cell_id}',
                    value=story.name)
                style_key = DrawIOStory.STORY_TYPE_STYLES.get(story.story_type, 'story_user')
                copy.apply_style_for_type(style_key)
                copy.set_position(story.position.x, lane_y + self.STORY_Y_OFFSET)
                copy.set_size(CELL_SIZE, CELL_SIZE)
                self._story_copies.append(copy)

        return self.LANE_HEIGHT

    def collect_all_elements(self) -> list:
        elements = []
        if self._lane_element:
            elements.append(self._lane_element)
        if self._label_element:
            elements.append(self._label_element)
        elements.extend(self._actor_elements)
        elements.extend(self._story_copies)
        return elements
