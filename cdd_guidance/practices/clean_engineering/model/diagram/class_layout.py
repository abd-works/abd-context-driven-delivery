"""Places class cards and routes the arrows between them. Shared by every class-shaped diagram view.

Arrows search a 10px grid, so each one finds its own way around the cards and around the arrows already drawn,
rather than picking from a list of route shapes. An arrow never passes through a card, never runs along another
arrow, and leaves and arrives at its own point on the card. It crosses another arrow only when no other way exists.

The one exception is an inheritance trunk: when several subclasses share one base, their arrows join, the standard
UML tree, and all of them arrive on one side of the base, so it shows one arrowhead. Each subclass drops a short line to a shared horizontal bar, and one line with the hollow triangle runs from
the bar to the base, so a reader sees one family instead of a fan of arrowheads.
"""
from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import DiagramNode
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry, segments_cross

Point = Tuple[int, int]
Heading = Tuple[int, int]
GridCell = Tuple[int, int]

GRID_STEP = 10
CARD_CLEARANCE = 20
# What each step inside another card's clearance costs: enough that an arrow keeps clear when it can, but a way out
# between cards a person placed close together, where a wall would leave the arrow no way at all.
CLEARANCE_PRICE = 60
PORT_STUB_STEPS = 3
PORT_APPROACH_STEPS = 6
ARROW_SPACING_STEPS = 1
# How far the bar of an inheritance trunk sits from its subclasses: just past the cells kept open beside their ports,
# so other arrows leaving the same side of a subclass still get out.
TRUNK_BAR_STEPS = PORT_STUB_STEPS + 2 * ARROW_SPACING_STEPS
TURN_PRICE = 40
# How far past an arrow's ends its first search reaches, in grid steps.
SEARCH_WINDOW_STEPS = 30
CROSSING_PRICE = 150
REROUTING_ROUNDS = 4
UNROUTED_TROUBLE = 1000
ROW_GUTTER = 100
ROW_GUTTER_PER_ARROW = 8
COLUMN_GUTTER = 130
PAGE_MARGIN = 60
ROUTING_MARGIN = 200
GRID_WIDTH_BIAS = 1.3
ESTIMATE_WEIGHT = 2
SPARE_GRID_LINES = 3
LAYOUT_SEED = 7
STARTING_TOLERANCE = 150
MOST_LAYOUT_TRIES = 12000
LAYOUT_TRIES_PER_CARD_PAIR = 40
LENGTH_WEIGHT = 10
INHERITANCE_LENGTH_WEIGHT = 50
BASE_BELOW_CHILD_WEIGHT = 2000
OWNED_ABOVE_OWNER_WEIGHT = 300
PASSES_CARD_WEIGHT = 300
CROSSING_WEIGHT = 250
GROUP_WEIGHT = 10
SMALLEST_PORT_SPACING = 30
INHERITANCE = "inheritance"
GROUP_FILL_COLORS = ("#d6e4f5", "#d5e8d4", "#fff2cc", "#ffe6cc", "#e1d5e7", "#f8cecc", "#d0ece7", "#e6e6e6")

_HEADINGS = {"top": (0, -1), "bottom": (0, 1), "right": (1, 0), "left": (-1, 0)}
_VERTICAL_SIDES = ("bottom", "top")
_HORIZONTAL_SIDES = ("right", "left")


@dataclass
class DiagramArrow:
    """The line drawn between two cards for every relationship one class has to another.

    Several properties can stand behind one arrow, so it carries their names as its label, not one Relationship.
    Routing fills in its sides, its two end points, and the corners between them."""

    source: str
    target: str
    kind: str = "association"
    label: str = ""
    exit_side: str = ""
    entry_side: str = ""
    exit_point: Point = (0, 0)
    entry_point: Point = (0, 0)
    corners: List[Point] = field(default_factory=list)
    cells: List[Point] = field(default_factory=list)
    routed: bool = False

    @property
    def path(self) -> List[Point]:
        return [self.exit_point] + self.corners + [self.entry_point]




class CardPlacement:
    """Finds the grid position for every card that leaves the fewest crossings and the shortest arrows.

    A card is any placed diagram node: placement reads its size and group and sets its geometry.
    Swapping cards and keeping each swap that scores better is what a person does when tidying a diagram by hand.
    The score holds a base above what derives from it and an owner above what it owns, and keeps a module's cards
    together. The search is seeded, so the same model always gives the same diagram.
    """

    def __init__(self, cards: List[DiagramNode], arrows: List[DiagramArrow]) -> None:
        self._cards = cards
        ids = {card.cell_id for card in cards}
        self._links = [arrow for arrow in arrows if arrow.source != arrow.target and arrow.source in ids and arrow.target in ids]
        self._groups = {card.cell_id: card.group for card in cards}
        self._columns = max(1, math.ceil(math.sqrt(len(cards) * GRID_WIDTH_BIAS)))
        self._lines = max(1, math.ceil(len(cards) / self._columns) + SPARE_GRID_LINES)

    def place(self) -> None:
        if not self._cards:
            return
        grid = self._best_grid()
        self._set_positions(self._without_empty_lines(grid))

    def _starting_grid(self) -> Dict[str, GridCell]:
        return {
            card.cell_id: (index % self._columns, index // self._columns)
            for index, card in enumerate(self._cards)
        }

    def _best_grid(self) -> Dict[str, GridCell]:
        grid = self._starting_grid()
        score = self._score(grid)
        best, best_score = grid, score
        chooser = random.Random(LAYOUT_SEED)
        ids = [card.cell_id for card in self._cards]
        all_cells = [(column, line) for column in range(self._columns) for line in range(self._lines)]
        tries = min(MOST_LAYOUT_TRIES, LAYOUT_TRIES_PER_CARD_PAIR * len(ids) ** 2)
        for attempt in range(tries):
            trial = self._with_card_moved(grid, chooser.choice(ids), chooser.choice(all_cells))
            trial_score = self._score(trial)
            allowance = STARTING_TOLERANCE * (1 - attempt / tries) * chooser.random()
            if trial_score <= score + allowance:
                grid, score = trial, trial_score
            if score < best_score:
                best, best_score = grid, score
        return best

    def _with_card_moved(self, grid: Dict[str, GridCell], cell_id: str, cell: GridCell) -> Dict[str, GridCell]:
        trial = dict(grid)
        for other, position in grid.items():
            if position == cell:
                trial[other] = grid[cell_id]
        trial[cell_id] = cell
        return trial

    def _score(self, grid: Dict[str, GridCell]) -> float:
        occupied = {position: cell_id for cell_id, position in grid.items()}
        score = sum(self._link_score(link, grid, occupied) for link in self._links)
        score += self._crossing_score(grid) + self._group_score(grid)
        return score

    def _link_score(self, link: DiagramArrow, grid: Dict[str, GridCell], occupied: Dict[GridCell, str]) -> float:
        source, target = grid[link.source], grid[link.target]
        across, down = target[0] - source[0], target[1] - source[1]
        length_weight = INHERITANCE_LENGTH_WEIGHT if link.kind == INHERITANCE else LENGTH_WEIGHT
        score = length_weight * (abs(across) + abs(down))
        if link.kind == INHERITANCE and down >= 0:
            score += BASE_BELOW_CHILD_WEIGHT
        elif link.kind != INHERITANCE and down < 0:
            score += OWNED_ABOVE_OWNER_WEIGHT
        steps = max(abs(across), abs(down))
        for step in range(1, steps):
            passed = (round(source[0] + across * step / steps), round(source[1] + down * step / steps))
            if passed in occupied:
                score += PASSES_CARD_WEIGHT
        return score

    def _crossing_score(self, grid: Dict[str, GridCell]) -> float:
        crossings = 0
        for index, first in enumerate(self._links):
            for second in self._links[index + 1:]:
                shares_card = {first.source, first.target} & {second.source, second.target}
                if not shares_card and segments_cross((grid[first.source], grid[first.target]), (grid[second.source], grid[second.target])):
                    crossings += 1
        return CROSSING_WEIGHT * crossings

    def _group_score(self, grid: Dict[str, GridCell]) -> float:
        members: Dict[str, List[GridCell]] = {}
        for cell_id, position in grid.items():
            members.setdefault(self._groups[cell_id], []).append(position)
        score = 0.0
        for positions in members.values():
            middle_column = sum(position[0] for position in positions) / len(positions)
            middle_line = sum(position[1] for position in positions) / len(positions)
            score += sum(abs(position[0] - middle_column) + abs(position[1] - middle_line) for position in positions)
        return GROUP_WEIGHT * score

    def _without_empty_lines(self, grid: Dict[str, GridCell]) -> Dict[str, GridCell]:
        columns = {column: index for index, column in enumerate(sorted({position[0] for position in grid.values()}))}
        lines = {line: index for index, line in enumerate(sorted({position[1] for position in grid.values()}))}
        return {cell_id: (columns[position[0]], lines[position[1]]) for cell_id, position in grid.items()}

    def _set_positions(self, grid: Dict[str, GridCell]) -> None:
        cards = {card.cell_id: card for card in self._cards}
        lefts, widths = self._column_extents(grid, cards)
        tops, heights = self._line_extents(grid, cards)
        for cell_id, (column, line) in grid.items():
            box = cards[cell_id].geometry
            x = (lefts[column] + (widths[column] - box.width) / 2) // GRID_STEP * GRID_STEP
            y = (tops[line] + (heights[line] - box.height) / 2) // GRID_STEP * GRID_STEP
            cards[cell_id].geometry = box.moved_to(x, y)

    def _column_extents(self, grid, cards) -> Tuple[List[float], List[float]]:
        widths = [0.0] * (max(position[0] for position in grid.values()) + 1)
        for cell_id, position in grid.items():
            widths[position[0]] = max(widths[position[0]], cards[cell_id].geometry.width)
        lefts = []
        left = float(PAGE_MARGIN)
        for width in widths:
            lefts.append(left)
            left += width + COLUMN_GUTTER
        return lefts, widths

    def _line_extents(self, grid, cards) -> Tuple[List[float], List[float]]:
        heights = [0.0] * (max(position[1] for position in grid.values()) + 1)
        for cell_id, position in grid.items():
            heights[position[1]] = max(heights[position[1]], cards[cell_id].geometry.height)
        tops = []
        top = float(PAGE_MARGIN)
        for line, height in enumerate(heights):
            tops.append(top)
            top += height + self._gutter_below(grid, line)
        return tops, heights

    def _gutter_below(self, grid: Dict[str, GridCell], line: int) -> int:
        """Each arrow leaving this line or entering the next needs its own lane through the gap between them."""
        touching = {cell_id for cell_id, position in grid.items() if position[1] in (line, line + 1)}
        lanes = sum(1 for link in self._links if link.source in touching or link.target in touching)
        return ROW_GUTTER + ROW_GUTTER_PER_ARROW * lanes


class _RouteGrid:
    """The page as grid cells: which are inside a card's clearance, and which already carry an arrow."""

    def __init__(self, obstacles: Iterable[Geometry], width: float, height: float) -> None:
        self.columns = int(width) // GRID_STEP
        self.lines = int(height) // GRID_STEP
        # Cells inside a card or its clearance, and the cells of the cards themselves, which no arrow ever enters.
        self.blocked: Set[Point] = set()
        self.inside_cards: Set[Point] = set()
        for box in obstacles:
            self.blocked |= self.cells_around(box)
            self.inside_cards |= self.cells_around(box, clearance=0)
        self.horizontal: Set[Point] = set()
        self.vertical: Set[Point] = set()
        self._held_for: Dict[Point, Set[int]] = {}
        self._approach_vertical: Dict[Point, Set[int]] = {}
        self._approach_horizontal: Dict[Point, Set[int]] = {}

    def hold_port(self, cell: Point, heading: Heading, owner: int) -> None:
        """Keep the way into a port open, so an arrow routed earlier cannot shut out the arrow that ends there.

        The cells beside the port are closed to every other arrow. Further out, others may cross the approach but
        may not run along it, because a run beside the approach blocks it just as surely."""
        spread = range(-ARROW_SPACING_STEPS, ARROW_SPACING_STEPS + 1)
        for across in spread:
            for along in spread:
                self._held_for.setdefault((cell[0] + across, cell[1] + along), set()).add(owner)
        table = self._approach_vertical if heading[0] == 0 else self._approach_horizontal
        for distance in range(1, PORT_APPROACH_STEPS + 1):
            for across in spread:
                reached = (cell[0] + heading[0] * distance + heading[1] * across, cell[1] + heading[1] * distance + heading[0] * across)
                table.setdefault(reached, set()).add(owner)

    def is_held_against(self, cell: Point, step: Heading, owner: int) -> bool:
        approach = self._approach_vertical if step[0] == 0 else self._approach_horizontal
        return any(holders and owner not in holders for holders in (self._held_for.get(cell), approach.get(cell)))

    def cells_around(self, box: Geometry, clearance: int = CARD_CLEARANCE) -> Set[Point]:
        left, right = int(box.x - clearance) // GRID_STEP, int(box.x + box.width + clearance) // GRID_STEP
        top, bottom = int(box.y - clearance) // GRID_STEP, int(box.y + box.height + clearance) // GRID_STEP
        return {(x, y) for x in range(left, right + 1) for y in range(top, bottom + 1)}

    def is_open_for(self, cells: List[Point], owner: int, own_cards: Set[Point]) -> bool:
        """True when a line laid along these cells stays out of every card but its own two, keeps clear of other
        arrows' ports, and runs along no arrow already drawn."""
        for before, here in zip(cells, cells[1:]):
            step = (here[0] - before[0], here[1] - before[1])
            along = self.horizontal if step[0] else self.vertical
            if not self.contains(here) or (here in self.blocked and here not in own_cards):
                return False
            if self.is_held_against(here, step, owner) or here in along:
                return False
        return True

    def claim(self, cells: List[Point]) -> None:
        """Keep other arrows clear of this one's runs, so two parallel arrows never sit on each other."""
        for before, here in zip(cells, cells[1:]):
            lengthwise = before[1] == here[1]
            table = self.horizontal if lengthwise else self.vertical
            for cell in (before, here):
                for spread in range(-ARROW_SPACING_STEPS, ARROW_SPACING_STEPS + 1):
                    table.add((cell[0], cell[1] + spread) if lengthwise else (cell[0] + spread, cell[1]))

    def contains(self, cell: Point) -> bool:
        return 0 <= cell[0] < self.columns and 0 <= cell[1] < self.lines

    def carries_arrow(self, cell: Point) -> bool:
        return cell in self.horizontal or cell in self.vertical


class _ArrowSearch:
    """One arrow's cheapest way across the grid, paying for each corner and far more for each crossing."""

    def __init__(
        self,
        grid: _RouteGrid,
        owner: int,
        begin: Point,
        end: Point,
        heading_out: Heading,
        heading_in: Heading,
        respect_held_ports: bool = True,
        trunk: Iterable[Point] = (),
        window: Optional[Tuple[int, int, int, int]] = None,
        may_run_along: bool = False,
    ) -> None:
        self._grid = grid
        # A last resort: the arrow may run along or turn on another arrow, at the price of a crossing, when cards a person
        # placed close together leave the only gap already taken.
        self._may_run_along = may_run_along
        # The cells the search may use, as left, top, right, bottom; the whole page when None.
        self._window = window if window is not None else (0, 0, grid.columns - 1, grid.lines - 1)
        self._owner = owner
        self._respect_held_ports = respect_held_ports
        # The lines of the arrow's own inheritance trunk: the search ends where it meets them, and may come up to them.
        self._trunk = set(trunk)
        self._beside_trunk = {(x + across, y + along) for x, y in self._trunk for across in (-1, 0, 1) for along in (-1, 0, 1)}
        goals = self._trunk | {end}
        self._goal_box = (min(x for x, _ in goals), min(y for _, y in goals), max(x for x, _ in goals), max(y for _, y in goals))
        self._begin = begin
        self._end = end
        self._heading_out = heading_out
        self._heading_in = heading_in
        self._came_from: Dict[Tuple[Point, Heading], Tuple[Point, Heading]] = {}

    def run(self) -> Optional[List[Point]]:
        """The search, written as one loop over local names: it visits hundreds of thousands of cells on a large page,
        so each check is done here once rather than through a method call. It takes the same steps at the same prices
        as `_steps` and `_price`, so it finds the same way they would."""
        grid, trunk, beside_trunk, end = self._grid, self._trunk, self._beside_trunk, self._end
        window_left, window_top, window_right, window_bottom = self._window
        near_cards, inside_cards, horizontal, vertical = grid.blocked, grid.inside_cards, grid.horizontal, grid.vertical
        held_vertical, held_horizontal = self._cells_held_against()
        left, top, right, bottom = self._goal_box
        heading_in, came_from = self._heading_in, self._came_from
        may_run_along = self._may_run_along
        # A card a person placed right against the port leaves no cell to come straight in from, so the arrow may
        # come in from the side for its last step.
        any_heading_in = (end[0] - heading_in[0], end[1] - heading_in[1]) in inside_cards
        headings = tuple(_HEADINGS.values())
        push, pop, infinity = heapq.heappush, heapq.heappop, float("inf")
        best = {(self._begin, self._heading_out): 0}
        frontier = [(0, 0, self._begin, self._heading_out)]
        # The cost each cell and heading was searched from at. The estimate counts the distance left twice over, so a
        # cheaper way to a cell can turn up after it was searched from. It is searched from again only when the new way
        # saves a crossing: saving a turn or a few steps cost far more time than it gained.
        expanded: Dict[Tuple[Point, Heading], int] = {}
        while frontier:
            _estimate, cost, cell, heading = pop(frontier)
            if cost > best[(cell, heading)] or cost > expanded.get((cell, heading), infinity) - CROSSING_PRICE:
                continue
            expanded[(cell, heading)] = cost
            if (cell == end and (heading == heading_in or any_heading_in)) or cell in trunk:
                return self._walk_back((cell, heading))
            x, y = cell
            cell_in_horizontal, cell_in_vertical = cell in horizontal, cell in vertical
            cell_carries_arrow = cell_in_horizontal or cell_in_vertical
            for step in headings:
                step_x, step_y = step
                if step_x == -heading[0] and step_y == -heading[1]:
                    continue
                following = (x + step_x, y + step_y)
                fx, fy = following
                if not (window_left <= fx <= window_right and window_top <= fy <= window_bottom):
                    continue
                straight = step == heading
                running_along = False
                if following not in trunk:
                    if following in inside_cards and following != end:
                        continue
                    if following in (held_horizontal if step_x else held_vertical):
                        continue
                    if following in beside_trunk:
                        if not (straight and self._heads_into_trunk(following, step)):
                            continue
                    else:
                        if (following in horizontal or cell_in_horizontal) if step_x else (following in vertical or cell_in_vertical):
                            if not may_run_along:
                                continue
                            running_along = True
                        if not straight and cell_carries_arrow:
                            if not may_run_along:
                                continue
                            running_along = True
                crossing = following in (vertical if step_x else horizontal) and following not in beside_trunk
                total = cost + 1 + (0 if straight else TURN_PRICE) + (CROSSING_PRICE if crossing or running_along else 0)
                if following in near_cards and following not in trunk and following != end:
                    total += CLEARANCE_PRICE
                key = (following, step)
                if total < best.get(key, infinity) and total <= expanded.get(key, infinity) - CROSSING_PRICE:
                    best[key] = total
                    came_from[key] = (cell, heading)
                    distance = max(left - fx, 0, fx - right) + max(top - fy, 0, fy - bottom)
                    push(frontier, (total + ESTIMATE_WEIGHT * distance, total, following, step))
        return None

    def _cells_held_against(self) -> Tuple[Set[Point], Set[Point]]:
        """The cells `is_held_against` closes to this arrow, for a vertical step and for a horizontal one; none when
        the arrow may pass other arrows' ports."""
        if not self._respect_held_ports:
            return set(), set()
        grid, owner = self._grid, self._owner
        ports = {cell for cell, holders in grid._held_for.items() if owner not in holders}
        vertical = ports | {cell for cell, holders in grid._approach_vertical.items() if owner not in holders}
        horizontal = ports | {cell for cell, holders in grid._approach_horizontal.items() if owner not in holders}
        return vertical, horizontal

    def _heads_into_trunk(self, cell: Point, step: Heading) -> bool:
        """True when going on straight meets the trunk within its spacing, so the arrow joins it head-on instead of
        running alongside it."""
        reach = range(1, ARROW_SPACING_STEPS + 2)
        return any((cell[0] + step[0] * distance, cell[1] + step[1] * distance) in self._trunk for distance in reach)

    def _walk_back(self, last: Tuple[Point, Heading]) -> List[Point]:
        steps = [last]
        while steps[-1] in self._came_from:
            steps.append(self._came_from[steps[-1]])
        return [cell for cell, _heading in reversed(steps)]


class _InheritanceTrunk:
    """The arrows from several subclasses to one base, drawn as one tree: a short drop from each subclass to a shared
    horizontal bar, and one line from the bar to a single point on the base.

    Each arrow still runs from its own subclass to the base, so a diagram read back gives every subclass its base."""

    def __init__(self, arrows: List[DiagramArrow], cards: Dict[str, DiagramNode]) -> None:
        self.arrows = arrows
        # The base and its subclasses, the only cards the trunk's lines may come near.
        self._cards = {cell_id: cards[cell_id] for arrow in arrows for cell_id in (arrow.source, arrow.target)}

    def holds(self, arrow: DiagramArrow) -> bool:
        return any(member is arrow for member in self.arrows)

    def share_entry_point(self) -> None:
        """The first arrow is given the trunk's point on the base; every other arrow ends there too."""
        for arrow in self.arrows[1:]:
            arrow.entry_point = self.arrows[0].entry_point

    def draw(self, grid: _RouteGrid) -> bool:
        """Lay the tree on this pass's grid when every line of it is open; otherwise leave the grid untouched and return
        False, so the arrows are routed one by one."""
        bar = self._bar_line()
        if bar is None:
            return False
        paths = [self._path(arrow, bar) for arrow in self.arrows]
        walks = [_cells_along(path) for path in paths]
        for arrow, walk in zip(self.arrows, walks):
            own_cards = grid.cells_around(self._cards[arrow.source].geometry) | grid.cells_around(self._cards[arrow.target].geometry)
            if not grid.is_open_for(walk, id(self), own_cards):
                return False
        for arrow, path, walk in zip(self.arrows, paths, walks):
            arrow.corners, arrow.cells, arrow.routed = path[1:-1], walk, True
            grid.claim(walk)
        return True

    def _bar_line(self) -> Optional[int]:
        """Where the bar runs: just clear of the subclass nearest the base, and still clear of the base itself."""
        entry = self.arrows[0].entry_point[1]
        outward = _HEADINGS[self.arrows[0].entry_side][1]
        nearest = min((arrow.exit_point[1] for arrow in self.arrows), key=lambda line: abs(line - entry))
        on_grid = math.floor(nearest / GRID_STEP) if outward > 0 else math.ceil(nearest / GRID_STEP)
        bar = (on_grid - outward * TRUNK_BAR_STEPS) * GRID_STEP
        if (bar - entry) * outward < PORT_STUB_STEPS * GRID_STEP:
            return None
        return bar

    def _path(self, arrow: DiagramArrow, bar: int) -> List[Point]:
        joining = (arrow.entry_point[0], bar)
        points = [arrow.exit_point, (arrow.exit_point[0], bar), joining, arrow.entry_point]
        return [point for index, point in enumerate(points) if index == 0 or point != points[index - 1]]


class ArrowRouter:
    """Routes every arrow, retrying the ones that crossed until a pass finds nothing better."""

    def __init__(
        self,
        cards: List[DiagramNode],
        arrows: List[DiagramArrow],
        obstacles: Iterable[Geometry] = (),
        kept_paths: Iterable[List[Point]] = (),
    ) -> None:
        self._cards = {card.cell_id: card for card in cards}
        self._arrows = [arrow for arrow in arrows if self._draws(arrow)]
        self._obstacles = list(obstacles)
        self._kept_paths = list(kept_paths)
        self._trunks: List[_InheritanceTrunk] = []

    def route(self) -> List[DiagramArrow]:
        if not self._arrows:
            return []
        for arrow in self._arrows:
            arrow.exit_side, arrow.entry_side = self._facing_sides(arrow)
        self._one_side_per_base()
        grid = self._grid_with_trunks()
        for arrow in sorted(self._arrows_alone(), key=self._length_between_cards):
            self._route_one(arrow, grid)
        for _ in range(REROUTING_ROUNDS):
            if not self._reroute_troubled():
                break
        return self._arrows

    def _grid_with_trunks(self) -> _RouteGrid:
        """Lay every inheritance trunk before the other arrows, so they find their way around it.

        A trunk whose straight bar would cross a card or run along another arrow is searched instead, around what is in
        its way. Only a trunk no search can lay breaks up into its own arrows, each with its own point on the base, and
        the ports are shared out again."""
        self._trunks = self._shared_bases()
        while True:
            self._assign_ports()
            for arrow in self._arrows:
                arrow.routed, arrow.corners, arrow.cells = False, [], []
            grid = self._grid_without(None)
            broken = [trunk for trunk in self._trunks if not trunk.draw(grid) and not self._search_trunk(trunk, grid)]
            if not broken:
                return grid
            self._trunks = [trunk for trunk in self._trunks if trunk not in broken]

    def _search_trunk(self, trunk: _InheritanceTrunk, grid: _RouteGrid) -> bool:
        """Grow the tree one subclass at a time, nearest the base first: the first arrow searches its way to the base,
        and each later one searches until it meets a line already laid, then follows that line to the base."""
        to_base: Dict[Point, List[Point]] = {}
        for arrow in sorted(trunk.arrows, key=self._length_between_cards):
            cells = self._search_cells(arrow, grid, id(trunk), to_base)
            if cells is None:
                return False
            whole = cells + to_base.get(cells[-1], [cells[-1]])[1:]
            for index, cell in enumerate(whole):
                to_base.setdefault(cell, whole[index:])
            grid.claim(cells)
            arrow.cells, arrow.routed = whole, True
            arrow.corners = self._corners(arrow.exit_point, whole, arrow.entry_point)
        return True

    def _search_cells(self, arrow: DiagramArrow, grid: _RouteGrid, owner: int, trunk: Iterable[Point] = ()) -> Optional[List[Point]]:
        """The cells of this arrow's cheapest way, keeping clear of other arrows' ports when it can."""
        out, into = _HEADINGS[arrow.exit_side], _HEADINGS[arrow.entry_side]
        begin, end = self._clear_stub_end(arrow.exit_point, out, grid), self._clear_stub_end(arrow.entry_point, into, grid)
        heading_in = (-into[0], -into[1])
        trunk = list(trunk)
        window = self._window_around(grid, [begin, end] + trunk)
        # In the window round the arrow: clear of other arrows' ports, then past them, then along other arrows; only then
        # over the whole page. A search that finds no way walks its whole area, so the page is searched last.
        tries = ((window, True, False), (window, False, False), (window, False, True), (None, False, False))
        for area, respect_held_ports, may_run_along in tries:
            cells = _ArrowSearch(grid, owner, begin, end, out, heading_in, respect_held_ports, trunk, area, may_run_along).run()
            if cells is not None:
                return cells
        return _ArrowSearch(grid, owner, begin, end, out, heading_in, False, trunk, None, True).run()

    def _window_around(self, grid: _RouteGrid, cells: List[Point]) -> Tuple[int, int, int, int]:
        """The part of the page an arrow is searched in first: the box round its ends and its trunk, with room to go
        round what is in between. Searching the whole page for every arrow took hours on a large diagram; a way that
        leaves this box is one a reader would not follow anyway."""
        left, top = min(x for x, _ in cells), min(y for _, y in cells)
        right, bottom = max(x for x, _ in cells), max(y for _, y in cells)
        spare = SEARCH_WINDOW_STEPS + (right - left + bottom - top) // 2
        return (max(0, left - spare), max(0, top - spare), min(grid.columns - 1, right + spare), min(grid.lines - 1, bottom + spare))

    def _shared_bases(self) -> List[_InheritanceTrunk]:
        """One trunk for each base two or more subclasses reach from the same side. One subclass keeps its own arrow."""
        families: Dict[Tuple[str, str], List[DiagramArrow]] = {}
        for arrow in self._arrows:
            if arrow.kind == INHERITANCE and arrow.entry_side in _VERTICAL_SIDES:
                families.setdefault((arrow.target, arrow.entry_side), []).append(arrow)
        return [_InheritanceTrunk(arrows, self._cards) for arrows in families.values() if len(arrows) > 1]

    def _trunk_of(self, arrow: DiagramArrow) -> Optional[_InheritanceTrunk]:
        return next((trunk for trunk in self._trunks if trunk.holds(arrow)), None)

    def _port_owner(self, arrow: DiagramArrow) -> int:
        """Who a port is kept open for: the whole trunk for its arrows, since they run along each other's ports."""
        trunk = self._trunk_of(arrow)
        return id(trunk if trunk is not None else arrow)

    def _arrows_alone(self) -> List[DiagramArrow]:
        """The arrows routed one by one: every arrow that is not part of a trunk."""
        return [arrow for arrow in self._arrows if self._trunk_of(arrow) is None]

    def _reroute_troubled(self) -> bool:
        """Lift each troubled arrow and search again with every other arrow in place, keeping the new way only if it is better."""
        improved = False
        for arrow in self._troubled():
            before = (arrow.routed, arrow.corners, arrow.cells)
            trouble_before = self._trouble_on(arrow)
            self._route_one(arrow, self._grid_without(arrow))
            if self._trouble_on(arrow) < trouble_before:
                improved = True
            else:
                arrow.routed, arrow.corners, arrow.cells = before
        return improved

    def _trouble_on(self, arrow: DiagramArrow) -> int:
        if not arrow.routed:
            return UNROUTED_TROUBLE
        return sum(1 for other in self._arrows if other is not arrow and other.routed and paths_cross(arrow.path, other.path))

    def _draws(self, arrow: DiagramArrow) -> bool:
        return arrow.source != arrow.target and arrow.source in self._cards and arrow.target in self._cards

    def _length_between_cards(self, arrow: DiagramArrow) -> float:
        source, target = self._cards[arrow.source].geometry.center, self._cards[arrow.target].geometry.center
        return abs(source[0] - target[0]) + abs(source[1] - target[1])

    def _facing_sides(self, arrow: DiagramArrow) -> Tuple[str, str]:
        source, target = self._cards[arrow.source].geometry, self._cards[arrow.target].geometry
        if arrow.kind == INHERITANCE or target.y + target.height <= source.y:
            return ("top", "bottom") if target.y < source.y else ("bottom", "top")
        if target.y >= source.y + source.height:
            return ("bottom", "top")
        if self._card_between(source, target):
            return ("bottom", "bottom")
        return ("right", "left") if target.center[0] >= source.center[0] else ("left", "right")

    def _one_side_per_base(self) -> None:
        """Every subclass of a base arrives on the same side of it, the side most of them face, so the family ends in
        one arrowhead. A subclass on the other side leaves the way it has to go to come round to that side."""
        families: Dict[str, List[DiagramArrow]] = {}
        for arrow in self._arrows:
            if arrow.kind == INHERITANCE:
                families.setdefault(arrow.target, []).append(arrow)
        for target, arrows in families.items():
            below = sum(1 for arrow in arrows if arrow.entry_side == "bottom")
            side = "bottom" if 2 * below >= len(arrows) else "top"
            base = self._cards[target].geometry
            for arrow in arrows:
                source = self._cards[arrow.source].geometry
                if side == "bottom":
                    arrow.exit_side = "top" if source.y >= base.y + base.height else "bottom"
                else:
                    arrow.exit_side = "bottom" if source.y + source.height <= base.y else "top"
                arrow.entry_side = side

    def _card_between(self, source: Geometry, target: Geometry) -> bool:
        """True when two cards in one row have a third between them, so the arrow has to go under it."""
        left, right = sorted((source, target), key=lambda card: card.x)
        top, bottom = max(left.y, right.y), min(left.y + left.height, right.y + right.height)
        return any(
            card.x >= left.x + left.width and card.x + card.width <= right.x and card.y < bottom and card.y + card.height > top
            for card in (node.geometry for node in self._cards.values())
        )

    def _grid_without(self, lifted: Optional[DiagramArrow]) -> _RouteGrid:
        boxes = [card.geometry for card in self._cards.values()] + self._obstacles
        width = max(box.x + box.width for box in boxes) + ROUTING_MARGIN
        height = max(box.y + box.height for box in boxes) + ROUTING_MARGIN
        grid = _RouteGrid(boxes, width, height)
        for path in self._kept_paths:
            grid.claim([(x // GRID_STEP, y // GRID_STEP) for x, y in path])
        for arrow in self._arrows:
            for point, side in ((arrow.exit_point, arrow.exit_side), (arrow.entry_point, arrow.entry_side)):
                grid.hold_port(self._stub_end(point, _HEADINGS[side]), _HEADINGS[side], self._port_owner(arrow))
            if arrow is not lifted:
                grid.claim(arrow.cells)
        return grid

    def _assign_ports(self) -> None:
        """Give every arrow its own point on the side it uses, ordered by where the far end sits, so arrows on one side do not cross.
        A trunk takes one point on its base, shared by all its arrows."""
        sides: Dict[Tuple[str, str], List[Tuple[DiagramArrow, bool]]] = {}
        for arrow in self._arrows:
            sides.setdefault((arrow.source, arrow.exit_side), []).append((arrow, True))
            trunk = self._trunk_of(arrow)
            if trunk is None or trunk.arrows[0] is arrow:
                sides.setdefault((arrow.target, arrow.entry_side), []).append((arrow, False))
        for (cell_id, side), users in sides.items():
            card = self._cards[cell_id].geometry
            users.sort(key=lambda user: self._far_end_position(user, side))
            for position, (arrow, leaving) in enumerate(users):
                point = self._port(card, side, (position + 1) / (len(users) + 1))
                if leaving:
                    arrow.exit_point = point
                else:
                    arrow.entry_point = point
        for trunk in self._trunks:
            trunk.share_entry_point()
        for arrow in self._arrows_alone():
            if len(sides[(arrow.source, arrow.exit_side)]) == 1 and len(sides[(arrow.target, arrow.entry_side)]) == 1:
                self._straighten(arrow)

    def _straighten(self, arrow: DiagramArrow) -> None:
        """Two cards that face each other with one arrow between them get a straight line, not a small step."""
        source, target = self._cards[arrow.source].geometry, self._cards[arrow.target].geometry
        if arrow.exit_side in _VERTICAL_SIDES:
            shared = _shared_middle(source.x, source.width, target.x, target.width)
            if shared is not None:
                arrow.exit_point = (shared, arrow.exit_point[1])
                arrow.entry_point = (shared, arrow.entry_point[1])
            return
        shared = _shared_middle(source.y, source.height, target.y, target.height)
        if shared is not None:
            arrow.exit_point = (arrow.exit_point[0], shared)
            arrow.entry_point = (arrow.entry_point[0], shared)

    def _far_end_position(self, user: Tuple[DiagramArrow, bool], side: str) -> float:
        """Where the far end sits along this side; a trunk's far end is the middle of its subclasses."""
        arrow, leaving = user
        trunk = None if leaving else self._trunk_of(arrow)
        sources = [member.source for member in trunk.arrows] if trunk is not None else [arrow.source]
        far_ends = [self._cards[arrow.target].geometry.center] if leaving else [self._cards[source].geometry.center for source in sources]
        axis = 0 if side in _VERTICAL_SIDES else 1
        return sum(far[axis] for far in far_ends) / len(far_ends)

    def _port(self, card: Geometry, side: str, fraction: float) -> Point:
        """On the grid along the side, so the arrow's first run stays straight wherever a person left the card."""
        if side in _VERTICAL_SIDES:
            along = round((card.x + card.width * fraction) / GRID_STEP) * GRID_STEP
            return (int(along), int(card.y + (card.height if side == "bottom" else 0)))
        along = round((card.y + card.height * fraction) / GRID_STEP) * GRID_STEP
        return (int(card.x + (card.width if side == "right" else 0)), int(along))

    def _route_one(self, arrow: DiagramArrow, grid: _RouteGrid) -> None:
        cells = self._search_cells(arrow, grid, id(arrow))
        arrow.routed = cells is not None
        arrow.corners = []
        arrow.cells = cells or []
        if cells is None:
            return
        grid.claim(cells)
        arrow.corners = self._corners(arrow.exit_point, cells, arrow.entry_point)

    def _clear_stub_end(self, point: Point, heading: Heading, grid: _RouteGrid) -> Point:
        """Where the arrow's straight run from its port ends: the usual stub, or a shorter one when a card a person
        placed close by sits within it, so the search starts outside that card and can find its way out."""
        start = (point[0] // GRID_STEP, point[1] // GRID_STEP)
        reached = start
        for steps in range(1, PORT_STUB_STEPS + 1):
            cell = (start[0] + heading[0] * steps, start[1] + heading[1] * steps)
            if cell in grid.inside_cards:
                break
            reached = cell
        return reached if reached != start else (start[0] + heading[0], start[1] + heading[1])

    def _stub_end(self, point: Point, heading: Heading) -> Point:
        return (point[0] // GRID_STEP + heading[0] * PORT_STUB_STEPS, point[1] // GRID_STEP + heading[1] * PORT_STUB_STEPS)

    def _corners(self, start: Point, cells: List[Point], goal: Point) -> List[Point]:
        walked = [start] + [(x * GRID_STEP, y * GRID_STEP) for x, y in cells] + [goal]
        kept = []
        for before, here, after in zip(walked, walked[1:], walked[2:]):
            straight = (before[0] == here[0] == after[0]) or (before[1] == here[1] == after[1])
            if not straight:
                kept.append(here)
        return kept

    def _troubled(self) -> List[DiagramArrow]:
        """Arrows routed alone that are unrouted or cross another. A trunk stays as laid, so the arrow crossing it moves."""
        alone = self._arrows_alone()
        trouble = [arrow for arrow in alone if not arrow.routed]
        for index, first in enumerate(self._arrows):
            for second in self._arrows[index + 1:]:
                if first.routed and second.routed and paths_cross(first.path, second.path):
                    trouble.extend(arrow for arrow in (first, second) if arrow in alone and arrow not in trouble)
        return trouble


def _cells_along(path: List[Point]) -> List[Point]:
    """Every grid cell an orthogonal path passes, one step at a time, so the grid can check and claim each of them."""
    corners = [(x // GRID_STEP, y // GRID_STEP) for x, y in path]
    cells = corners[:1]
    for target in corners[1:]:
        while cells[-1] != target:
            here = cells[-1]
            if here[0] != target[0]:
                cells.append((here[0] + (1 if target[0] > here[0] else -1), here[1]))
            else:
                cells.append((here[0], here[1] + (1 if target[1] > here[1] else -1)))
    return cells


def _shared_middle(start: float, length: float, other_start: float, other_length: float) -> Optional[int]:
    low, high = max(start, other_start), min(start + length, other_start + other_length)
    if high - low < 2 * GRID_STEP:
        return None
    return int((low + high) / 2 // GRID_STEP * GRID_STEP)


def paths_cross(first: List[Point], second: List[Point]) -> bool:
    """True when a run of one orthogonal path crosses a run of the other at a right angle."""
    return any(
        _runs_cross(a, b, c, d)
        for a, b in zip(first, first[1:])
        for c, d in zip(second, second[1:])
    )


def _runs_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    if (a[1] == b[1]) == (c[1] == d[1]):
        return False
    (left, right), (top, bottom) = ((a, b), (c, d)) if a[1] == b[1] else ((c, d), (a, b))
    return (
        min(left[0], right[0]) <= top[0] <= max(left[0], right[0])
        and min(top[1], bottom[1]) <= left[1] <= max(top[1], bottom[1])
    )
