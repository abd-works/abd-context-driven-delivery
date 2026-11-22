"""Diagram epic and story. A nested epic is an epic whose parent is an epic."""

from __future__ import annotations

from functools import cached_property
from typing import Dict, List, NamedTuple, Optional

from cdd_guidance.practices.stories.model.story_map import Epic, Increment, Story, StoryMap, StoryType

# A leaf epic with an estimate widens by a column for about this many characters of the estimate: wider for an epic
# that has stories beside it, as its estimate shares their columns.
_ESTIMATE_CHARACTERS_PER_COLUMN = 18
_ESTIMATE_CHARACTERS_PER_EXTRA_COLUMN = 22
_ESTIMATE_LEAD_CHARACTERS = 12
_ESTIMATE_EXTRA_LEAD_CHARACTERS = 15
_EMPTY_EPIC_COLUMNS = (2, 8)
_EXTRA_EPIC_COLUMNS = (1, 5)


class DiagramStoryNode:
    """Placement shared by a diagram epic, story, and increment."""

    first_x = 0
    """Where the first top-level epic starts: a format draws its epics from the map's margin."""
    epic_spacing = 0
    """The space a format leaves between two top-level epics."""
    story_pitch = 0
    """How far each story an epic holds itself pushes its sub-epics right; a format whose sub-epics sit after the
    epic's own stories gives its story pitch."""

    def _owning_map(self) -> Optional[StoryMap]:
        node = self.parent
        while node is not None and not isinstance(node, StoryMap):
            node = node.parent
        return node

    def _story_line_y(self) -> int:
        """Top of the story line on the diagram map this node is drawn on; on no map yet, the line of a map with no
        sub-epics."""
        story_map = self._owning_map()
        if isinstance(story_map, DiagramStoryMap):
            return story_map.story_y
        return DiagramStoryMap().story_y

    def _sub_epic_bar_y(self, depth: int) -> int:
        """Top of this node's sub-epic bar at *depth* on the map it is drawn on."""
        story_map = self._owning_map()
        if isinstance(story_map, DiagramStoryMap):
            return story_map.sub_epic_y(depth)
        return DiagramStoryMap().sub_epic_y(depth)

    @property
    def width(self) -> int:
        if isinstance(self, Story):
            return self.pitch
        if not isinstance(self, Epic):
            return 0
        if isinstance(self.parent, Epic):
            return DiagramStoryMap.base_width * max(self.columns.diagram_span(), 1)
        return DiagramStoryMap.base_width * self.columns.span()

    @property
    def height(self) -> int:
        if isinstance(self, Story):
            return self.size
        if isinstance(self, Epic):
            return DiagramStoryMap.row_height
        return 0

    @property
    def y(self) -> int:
        if isinstance(self, Story):
            story_map = self._owning_map()
            if story_map is None:
                return 0
            return story_map.actor_y + DiagramStoryMap.row_height
        if isinstance(self, Epic) and isinstance(self.parent, Epic):
            return (self.depth + 1) * DiagramStoryMap.row_height
        return 0

    @property
    def x(self) -> int:
        """A story sits at its epic's left edge. A sub-epic sits after the epic's own stories and the sub-epics before
        it; a top-level epic after the format's margin and the epics before it, each with the format's spacing."""
        parent = self.parent
        if isinstance(self, Story):
            return parent.x if isinstance(parent, Epic) else 0
        if isinstance(parent, Epic):
            return self._after(parent.epics, parent.x + len(parent.stories) * self.story_pitch, 0)
        if isinstance(parent, StoryMap):
            return self._after(parent.epics, self.first_x, self.epic_spacing)
        return self.first_x

    def _after(self, siblings: list, offset: int, spacing: int) -> int:
        """Where this node starts along siblings, from offset, each sibling before it taking its width and spacing."""
        for sibling in siblings:
            if sibling is self:
                return offset
            offset += sibling.width + spacing
        return offset


class DiagramStoryCell:
    """One story-map element as it sits on a drawn map: its role (``epic``, ``subepic``, ``story`` or ``actor``), its
    bar depth, its story kind, its words, and its box. Each diagram format reads its own elements into cells; the map
    places them by where they sit, not by their order in the file, because people restack elements on a drawing."""

    def __init__(self) -> None:
        self.role = ""
        self.depth = -1
        self.kind = ""
        self.text = ""
        # The id a format gave the cell when it drew it: the ids of the bars over it, then its own, joined by "/".
        self.cell_id = ""
        # The actor a story cell names on itself, for a format that writes it on the card rather than in a cell above.
        self.actor = ""
        self.x = self.y = self.width = self.height = 0.0
        self.node: Optional[Epic] = None

    @property
    def center(self) -> float:
        return self.x + self.width / 2

    @property
    def story_type(self) -> StoryType:
        return StoryType.from_mark(self.kind or None)

    def spans(self, across: float) -> bool:
        return self.x <= across < self.x + self.width

    def story_below(self, stories: List["DiagramStoryCell"]) -> Optional["DiagramStoryCell"]:
        """The story an actor names: the nearest one beneath it in the same column."""
        column = [story for story in stories if story.spans(self.center) and story.y > self.y]
        return min(column, key=lambda story: story.y, default=None)

    def beneath(self, bars: List["DiagramStoryCell"], across: Optional[float] = None) -> Optional["DiagramStoryCell"]:
        """The deepest bar spanning this cell's center, or ``across`` when given; the nearest bar when the cell was
        dragged past every bar's edge."""
        where = self.center if across is None else across
        spanning = [bar for bar in bars if bar.spans(where)]
        if spanning:
            return max(spanning, key=lambda bar: bar.depth)
        return min(bars, key=lambda bar: abs(bar.center - where), default=None)

    def owner_among(self, bars: List["DiagramStoryCell"]) -> Optional["DiagramStoryCell"]:
        """The bar that holds this story. The bar its id names holds it while the story sits under that bar, under one
        of the bars over that bar, or under no bar at all, so a story drawn past its bar's edge stays where it was
        written. A story a person dragged under another bar, and one whose id names no bar, goes by where it sits."""
        named_id = self.cell_id.rpartition("/")[0]
        named = next((bar for bar in bars if named_id and bar.cell_id == named_id), None)
        over = max((bar for bar in bars if bar.spans(self.center)), key=lambda bar: bar.depth, default=None)
        if named is not None and (over is None or over is named or named_id.startswith(f"{over.cell_id}/")):
            return named
        return self.beneath(bars)


class DiagramStory(Story, DiagramStoryNode):
    pitch = 60
    size = 50
    row_y = 345
    actor_height = size
    actor_gap = 4
    pad_below_sub_epic = 16
    fill = "#fff2cc"
    stroke = "#d6b656"
    actor_fill = "#dae8fc"
    actor_stroke = "#6c8ebf"


class DiagramEpic(Epic, DiagramStoryNode):
    story_class = DiagramStory
    row_y = 120
    nested_row_y = 195
    bar_height = 60
    content_inset = 10
    gap = 10
    left_margin = 20
    depth_gap = 8
    tighten = 5
    fill = "#e1d5e7"
    nested_fill = "#d5e8d4"
    stroke = "#9673a6"
    nested_stroke = "#82b366"

    @cached_property
    def columns(self) -> EpicColumns:
        """How many story columns the epic spans on the drawn map, and how deep its sub-epics nest."""
        return EpicColumns(self)


class LaidOutStory(DiagramStory):
    """A story card in a drawn map's story line: in its epic's column after the epic's inset, the stories before it in
    the epic each taking one pitch. Every drawn format places its stories this way, with its own pitch and padding."""

    column_pad = 0

    @property
    def x(self) -> int:
        parent = self.parent
        if not isinstance(parent, Epic):
            return 0
        return parent.x + type(parent).tighten + self.column_pad + parent.stories.index(self) * self.pitch

    @property
    def y(self) -> int:
        return self._story_line_y()


class LaidOutEpic(DiagramEpic):
    """An epic bar in a drawn map: as wide as the story columns it spans at its format's story pitch, a sub-epic one
    bar lower for each level it is nested. Every drawn format places its bars this way, with its own pitch."""

    @property
    def width(self) -> int:
        if isinstance(self.parent, Epic):
            return max(self.columns.diagram_span(), 1) * self.story_pitch
        return self.columns.span() * self.story_pitch

    @property
    def height(self) -> int:
        return self.bar_height

    @property
    def y(self) -> int:
        if isinstance(self.parent, Epic):
            return self._sub_epic_bar_y(self.depth)
        return self.row_y

class DiagramIncrement(Increment, DiagramStoryNode):
    label_width = 160
    lane_height = 70
    lane_gap = 5
    fill = "#f5f5f5"
    stroke = "#666666"


class DiagramStoryMap(StoryMap):
    """Story map whose epics and stories are the diagram types."""

    base_width = 200
    row_height = 100
    epic_class = DiagramEpic

    def place_cells(self, cells: List[DiagramStoryCell]) -> List[DiagramStoryCell]:
        """Read the epics and stories cells draw into this map by where they sit: epics left to right, each sub-epic
        under the shallower bar above it, each story under the bar its cell names or sits under (``owner_among``) with
        the actor just above it as its actor. Answers the cells that became epics and sub-epics, which a format places what else it draws under."""
        owners: List[DiagramStoryCell] = []
        for cell in sorted((c for c in cells if c.role == "epic"), key=lambda c: c.x):
            cell.node = self.epic_class(cell.text.strip(), len(self.epics) + 1)
            self.epics.append(cell.node)
            owners.append(cell)
        for cell in sorted((c for c in cells if c.role == "subepic"), key=lambda c: (c.depth, c.x)):
            owner = cell.beneath([o for o in owners if o.depth < cell.depth])
            if owner is not None:
                cell.node = self.epic_class(cell.text, len(owner.node.epics) + 1)
                owner.node.epics.append(cell.node)
                owners.append(cell)
        self._place_stories(cells, owners)
        return owners

    def _place_stories(self, cells: List[DiagramStoryCell], owners: List[DiagramStoryCell]) -> None:
        stories = sorted((c for c in cells if c.role == "story"), key=lambda c: (c.x, c.y))
        actors = {id(story): actor for actor in cells if actor.role == "actor"
                  for story in [actor.story_below(stories)] if story is not None}
        for cell in stories:
            owner = cell.owner_among(owners)
            if owner is None:
                continue
            story = self.story_class(cell.text, len(owner.node.stories) + 1, cell.story_type)
            actor = actors[id(cell)].text.strip() if id(cell) in actors else cell.actor
            if actor:
                story.actors = [actor]
            owner.node.stories.append(story)

    def save_thin_slice(self) -> str:
        """This map's increments drawn as the format's thin slice: one lane for each increment, holding the stories it
        delivers under their sub-epics' columns. Each diagram format draws its own."""
        raise NotImplementedError(f"{type(self).__name__} must draw its thin slice")

    @property
    def max_sub_epic_depth(self) -> int:
        deepest = 0
        for epic in self.epics:
            deepest = max(deepest, epic.columns.tree_depth())
        return deepest

    @property
    def actor_y(self) -> int:
        return (self.max_sub_epic_depth + 2) * self.row_height

    @property
    def sub_epic_top(self) -> int:
        """Top of the first nested level of sub-epic bars."""
        return DiagramEpic.nested_row_y

    @property
    def story_floor(self) -> int:
        """The highest a story may sit, however shallow the map."""
        return self.story_class.row_y

    def sub_epic_y(self, depth: int) -> int:
        """Top of a sub-epic bar at *depth*: each nested level stacks one bar lower."""
        return self.sub_epic_top + depth * (DiagramEpic.bar_height + DiagramEpic.depth_gap)

    @property
    def story_y(self) -> int:
        """Top of the story line: below the deepest sub-epic bar, leaving room for the actor drawn above each story,
        so a story at any depth keeps its actor and never sits on a bar."""
        story = self.story_class
        deepest_bottom = self.sub_epic_y(self.max_sub_epic_depth) + DiagramEpic.bar_height
        return max(self.story_floor, deepest_bottom + story.actor_height + story.actor_gap + story.pad_below_sub_epic)


class EpicColumns:
    """How many story columns an epic spans on a drawn map, and how deep its sub-epics nest: what a diagram format
    lays its bars out by."""

    def __init__(self, epic: DiagramEpic) -> None:
        self._epic = epic

    def estimate_label(self) -> str:
        """The epic's estimate as a bar writes it, `* {estimate}`; empty for an epic with none."""
        estimate = (self._epic.estimate or "").strip()
        if not estimate:
            return ""
        if estimate.startswith("*"):
            return estimate
        return f"* {estimate}"

    def has_estimate(self) -> bool:
        """The epic or a sub-epic under it gives an estimate."""
        if (self._epic.estimate or "").strip():
            return True
        return any(child.columns.has_estimate() for child in self._epic.epics)

    def span(self) -> int:
        """Story-grid columns a top-level epic occupies: its own stories, then each nested epic. An empty epic is one
        column."""
        nested = sum(max(child.columns.diagram_span(), 1) for child in self._epic.epics)
        return max(len(self._epic.stories) + nested, 1)

    def diagram_span(self) -> int:
        """Bar width in story-pitch columns. Stories and nested epics both take columns; an estimate widens a leaf
        epic."""
        nested = sum(child.columns.diagram_span() for child in self._epic.epics)
        story_columns = len(self._epic.stories)
        if self._epic.epics:
            return max(nested + story_columns, 1)
        estimate = self._epic.estimate.strip()
        if not estimate:
            return max(story_columns, 1)
        if story_columns == 0:
            fewest, most = _EMPTY_EPIC_COLUMNS
            return max(fewest, min(most, (len(estimate) + _ESTIMATE_LEAD_CHARACTERS) // _ESTIMATE_CHARACTERS_PER_COLUMN))
        fewest, most = _EXTRA_EPIC_COLUMNS
        return story_columns + max(fewest, min(most, (len(estimate) + _ESTIMATE_EXTRA_LEAD_CHARACTERS) // _ESTIMATE_CHARACTERS_PER_EXTRA_COLUMN))

    def tree_depth(self) -> int:
        """The depth of the deepest sub-epic under the epic; its own depth when it has none."""
        if not self._epic.epics:
            return self._epic.depth
        return max(child.columns.tree_depth() for child in self._epic.epics)


class ThinSliceColumn(NamedTuple):
    """One column of a thin slice: the sub-epic it is, or the epic with none, under its top epic, where it starts, and
    how wide it is."""

    epic: Epic
    sub: Epic
    x: float
    width: float


class ThinSliceLane(NamedTuple):
    """One increment's lane of a thin slice: its stories, by the index of the column of the sub-epic that holds each."""

    increment: Increment
    stories: Dict[int, List[Story]]


class ThinSliceLayout:
    """A story map's increments laid out as a thin slice, the one layout every drawn format draws: a column for each
    sub-epic, or epic with none, in map order, each wide enough for the most stories any one increment puts in it side
    by side, and a lane for each increment holding its stories under their sub-epics' columns. A format draws it on a
    surface of its own (``draw_on``), at its own pitch and from its own left edge."""

    def __init__(self, story_map: "DiagramStoryMap", pitch: float, gap: float, left: float) -> None:
        pairs = [(epic, sub) for epic in story_map.epics for sub in (epic.epics or [epic])]
        self.lanes = [ThinSliceLane(increment, self._by_column(increment, pairs)) for increment in story_map.increments]
        widths = [max([1] + [len(lane.stories.get(index, [])) for lane in self.lanes]) * pitch + gap for index in range(len(pairs))]
        starts = [left + sum(widths[:index]) for index in range(len(pairs))]
        self.columns = [ThinSliceColumn(epic, sub, x, width) for (epic, sub), x, width in zip(pairs, starts, widths)]

    def _by_column(self, increment: Increment, pairs: List[tuple]) -> Dict[int, List[Story]]:
        """The increment's stories by the column of the sub-epic that holds each, in the increment's order; a story the
        map lacks goes under the last column."""
        by_column: Dict[int, List[Story]] = {}
        for story in increment.stories:
            column = next((index for index, (_, sub) in enumerate(pairs)
                           if any(held.name == story.name for held in sub.descendants.stories())), len(pairs) - 1)
            by_column.setdefault(column, []).append(story)
        return by_column

    @property
    def width(self) -> float:
        return sum(column.width for column in self.columns)

    def epic_headers(self) -> List[tuple]:
        """Each top epic with where its header starts and how wide it is: over every column it holds."""
        return [(column.epic, column.x, sum(held.width for held in self.columns if held.epic is column.epic))
                for index, column in enumerate(self.columns) if index == 0 or self.columns[index - 1].epic is not column.epic]

    def sub_epic_headers(self) -> List[ThinSliceColumn]:
        """Each column that is a sub-epic, which draws a header of its own under its epic's."""
        return [column for column in self.columns if column.sub is not column.epic]

    def draw_on(self, surface: "ThinSliceSurface") -> None:
        """Draw the layout on surface: each epic's header, then each of its sub-epics' headers, column by column, then
        each lane in the increments' order."""
        headers = iter(self.epic_headers())
        previous = None
        for column in self.columns:
            if column.epic is not previous:
                surface.epic_header(*next(headers))
                previous = column.epic
            if column.sub is not column.epic:
                surface.sub_epic_header(column)
        for lane in self.lanes:
            surface.lane(lane, self)


class ThinSliceSurface:
    """Where a format draws a thin slice: a header for each epic and sub-epic, and each lane."""

    def epic_header(self, epic: Epic, x: float, width: float) -> None:
        raise NotImplementedError(f"{type(self).__name__} must draw an epic's header")

    def sub_epic_header(self, column: ThinSliceColumn) -> None:
        raise NotImplementedError(f"{type(self).__name__} must draw a sub-epic's header")

    def lane(self, lane: ThinSliceLane, layout: ThinSliceLayout) -> None:
        raise NotImplementedError(f"{type(self).__name__} must draw a lane")
