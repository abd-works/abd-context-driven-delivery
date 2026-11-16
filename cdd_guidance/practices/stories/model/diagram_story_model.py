"""Diagram epic and story. A nested epic is an epic whose parent is an epic."""

from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.stories.model.story_model import Epic, Increment, Story, StoryModel, StoryType


class DiagramStoryNode:
    """Placement shared by a diagram epic, story, and increment."""

    first_x = 0
    """Where the first top-level epic starts: a format draws its epics from the map's margin."""
    epic_spacing = 0
    """The space a format leaves between two top-level epics."""
    story_pitch = 0
    """How far each story an epic holds itself pushes its sub-epics right; a format whose sub-epics sit after the
    epic's own stories gives its story pitch."""

    def _owning_map(self) -> Optional[StoryModel]:
        node = self.parent
        while node is not None and not isinstance(node, StoryModel):
            node = node.parent
        return node

    def _story_line_y(self) -> int:
        """Top of the story line on the diagram map this node is drawn on; on no map yet, the line of a map with no
        sub-epics."""
        story_map = self._owning_map()
        if isinstance(story_map, DiagramStoryModel):
            return story_map.story_y
        return DiagramStoryModel.line_y(DiagramStory.row_y, DiagramEpic.nested_row_y, 0)

    def _sub_epic_bar_y(self, depth: int) -> int:
        """Top of this node's sub-epic bar at *depth* on the map it is drawn on."""
        story_map = self._owning_map()
        if isinstance(story_map, DiagramStoryModel):
            return story_map.sub_epic_y(depth)
        return DiagramStoryModel.bar_y(DiagramEpic.nested_row_y, depth)

    @property
    def width(self) -> int:
        if isinstance(self, Story):
            return self.pitch
        if not isinstance(self, Epic):
            return 0
        if isinstance(self.parent, Epic):
            return DiagramStoryModel.base_width * max(self.diagram_span_columns(), 1)
        return DiagramStoryModel.base_width * self.span_columns()

    @property
    def height(self) -> int:
        if isinstance(self, Story):
            return self.size
        if isinstance(self, Epic):
            return DiagramStoryModel.row_height
        return 0

    @property
    def y(self) -> int:
        if isinstance(self, Story):
            story_map = self._owning_map()
            if story_map is None:
                return 0
            return story_map.actor_y + DiagramStoryModel.row_height
        if isinstance(self, Epic) and isinstance(self.parent, Epic):
            return (self.depth + 1) * DiagramStoryModel.row_height
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
        if isinstance(parent, StoryModel):
            return self._after(parent.epics, self.first_x, self.epic_spacing)
        return self.first_x

    def _after(self, siblings: list, offset: int, spacing: int) -> int:
        """Where this node starts along siblings, from offset, each sibling before it taking its width and spacing."""
        for sibling in siblings:
            if sibling is self:
                return offset
            offset += sibling.width + spacing
        return offset

    def place(self, side: str, destination: "DiagramStoryNode") -> None:
        self._place_side = side
        self._place_destination = destination

    def add(self, child: "DiagramStoryNode") -> None:
        children = self._placed_children()
        previous = children[-1] if children else None
        if isinstance(child, Epic):
            self.append_epic(child)
        elif isinstance(child, Story):
            self.append_story(child)
        child.place("below", self)
        if previous is not None:
            child.place("after", previous)
        self.stretch()

    def stretch(self) -> None:
        parent = getattr(self, "parent", None)
        if isinstance(parent, DiagramStoryNode):
            parent.stretch()

    def role(self) -> str:
        if isinstance(self, Story):
            story_type = getattr(self, "story_type", StoryType.USER)
            value = getattr(story_type, "value", story_type)
            return f"story:{value}"
        if isinstance(self, Epic):
            if isinstance(self.parent, Epic):
                return f"subepic:{self.depth}"
            return "epic"
        return ""

    def _placed_children(self) -> list:
        children = []
        children.extend(getattr(self, "epics", []))
        children.extend(getattr(self, "stories", []))
        return children


class DiagramStoryCell:
    """One story-map element as it sits on a drawn map: its role (``epic``, ``subepic``, ``story`` or ``actor``), its
    bar depth, its story kind, its words, and its box. Each diagram format reads its own elements into cells; the map
    places them by where they sit, not by their order in the file, because people restack elements on a drawing."""

    def __init__(self) -> None:
        self.role = ""
        self.depth = -1
        self.kind = ""
        self.text = ""
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


class DiagramEpic(Epic, DiagramStoryNode):
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
            return max(self.diagram_span_columns(), 1) * self.story_pitch
        return self.span_columns() * self.story_pitch

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


class DiagramStoryModel(StoryModel):
    """Story map whose epics and stories are the diagram types."""

    base_width = 200
    row_height = 100
    epic_type = DiagramEpic
    story_type = DiagramStory

    def place_cells(self, cells: List[DiagramStoryCell]) -> List[DiagramStoryCell]:
        """Read the epics and stories cells draw into this map by where they sit: epics left to right, each sub-epic
        under the shallower bar above it, each story under the deepest bar over it with the actor just above it as its
        actor. Answers the cells that became epics and sub-epics, which a format places what else it draws under."""
        owners: List[DiagramStoryCell] = []
        for cell in sorted((c for c in cells if c.role == "epic"), key=lambda c: c.x):
            cell.node = self.epic_type(cell.text.strip(), len(self.epics) + 1)
            self.append_epic(cell.node)
            owners.append(cell)
        for cell in sorted((c for c in cells if c.role == "subepic"), key=lambda c: (c.depth, c.x)):
            owner = cell.beneath([o for o in owners if o.depth < cell.depth])
            if owner is not None:
                cell.node = self.epic_type(cell.text, len(owner.node.epics) + 1)
                owner.node.append_epic(cell.node)
                owners.append(cell)
        self._place_stories(cells, owners)
        return owners

    def _place_stories(self, cells: List[DiagramStoryCell], owners: List[DiagramStoryCell]) -> None:
        stories = sorted((c for c in cells if c.role == "story"), key=lambda c: (c.x, c.y))
        actors = {id(story): actor for actor in cells if actor.role == "actor"
                  for story in [actor.story_below(stories)] if story is not None}
        for cell in stories:
            owner = cell.beneath(owners)
            if owner is None:
                continue
            story = self.story_type(cell.text, len(owner.node.stories) + 1, cell.story_type)
            actor = actors[id(cell)].text.strip() if id(cell) in actors else cell.actor
            if actor:
                story.actors = [actor]
            owner.node.append_story(story)

    def thin_slice_columns(self) -> List[tuple]:
        """The thin slice's columns: one per sub-epic, or per epic with none, with its top epic, in map order."""
        return [(epic, sub) for epic in self.epics for sub in (epic.epics or [epic])]

    def thin_slice_lanes(self, columns: List[tuple]) -> List[tuple]:
        """Each increment with its stories under the column of the sub-epic that holds each, in the increment's order;
        a story the map lacks goes under the last column."""
        lanes = []
        for increment in self.increments:
            by_column: dict = {}
            for story in increment.stories:
                column = next((index for index, (_, sub) in enumerate(columns)
                               if any(held.name == story.name for held in sub.every_story())), len(columns) - 1)
                by_column.setdefault(column, []).append(story)
            lanes.append((increment, by_column))
        return lanes

    def thin_slice_widths(self, columns: List[tuple], lanes: List[tuple], pitch: int, gap: int) -> List[int]:
        """Each column widened to hold, side by side on one row, the most stories any one increment puts in it, so a
        lane is a single row of cards and a sub-epic is as wide as its fullest lane."""
        return [max([1] + [len(held.get(index, [])) for _, held in lanes]) * pitch + gap for index in range(len(columns))]

    @property
    def max_sub_epic_depth(self) -> int:
        deepest = 0
        for epic in self.epics:
            deepest = max(deepest, epic.tree_depth())
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
        return self.story_type.row_y

    def sub_epic_y(self, depth: int) -> int:
        """Top of a sub-epic bar at *depth*: each nested level stacks one bar lower."""
        return self.bar_y(self.sub_epic_top, depth)

    @property
    def story_y(self) -> int:
        return self.line_y(self.story_floor, self.sub_epic_top, self.max_sub_epic_depth)

    @staticmethod
    def bar_y(top: int, depth: int) -> int:
        return top + depth * (DiagramEpic.bar_height + DiagramEpic.depth_gap)

    @classmethod
    def line_y(cls, floor: int, top: int, max_sub_epic_depth: int) -> int:
        """Top of the story line: below the deepest sub-epic bar, leaving room for the actor drawn above each story,
        so a story at any depth keeps its actor and never sits on a bar."""
        story = cls.story_type
        deepest_bottom = cls.bar_y(top, max_sub_epic_depth) + DiagramEpic.bar_height
        return max(floor, deepest_bottom + story.actor_height + story.actor_gap + story.pad_below_sub_epic)
