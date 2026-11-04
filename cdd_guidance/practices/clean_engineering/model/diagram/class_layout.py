"""Places class cards and routes the arrows between them. Shared by every class-shaped diagram view.

Arrows search a 10px grid, so each one finds its own way around the cards and around the arrows already drawn,
rather than picking from a list of route shapes. An arrow never passes through a card, never runs along another
arrow, and leaves and arrives at its own point on the card. It crosses another arrow only when no other way exists.
"""
from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry

Point = Tuple[int, int]
Heading = Tuple[int, int]
GridCell = Tuple[int, int]

GRID_STEP = 10
CARD_CLEARANCE = 20
PORT_STUB_STEPS = 3
PORT_APPROACH_STEPS = 6
ARROW_SPACING_STEPS = 1
TURN_PRICE = 40
CROSSING_PRICE = 600
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
class DiagramCard:
    """One class card: its size is fixed before layout, and layout sets where it sits."""

    cell_id: str
    width: float
    height: float
    group: str = ""
    x: float = 0
    y: float = 0

    @property
    def geometry(self) -> Geometry:
        return Geometry(self.x, self.y, self.width, self.height)

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)


@dataclass
class DiagramArrow:
    """One relationship. Routing fills in its sides, its two end points, and the corners between them."""

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

    Swapping cards and keeping each swap that scores better is what a person does when tidying a diagram by hand.
    The score holds a base above what derives from it and an owner above what it owns, and keeps a module's cards
    together. The search is seeded, so the same model always gives the same diagram.
    """

    def __init__(self, cards: List[DiagramCard], arrows: List[DiagramArrow]) -> None:
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
                if not shares_card and _lines_cross(grid[first.source], grid[first.target], grid[second.source], grid[second.target]):
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
            card = cards[cell_id]
            card.x = (lefts[column] + (widths[column] - card.width) / 2) // GRID_STEP * GRID_STEP
            card.y = (tops[line] + (heights[line] - card.height) / 2) // GRID_STEP * GRID_STEP

    def _column_extents(self, grid, cards) -> Tuple[List[float], List[float]]:
        widths = [0.0] * (max(position[0] for position in grid.values()) + 1)
        for cell_id, position in grid.items():
            widths[position[0]] = max(widths[position[0]], cards[cell_id].width)
        lefts = []
        left = float(PAGE_MARGIN)
        for width in widths:
            lefts.append(left)
            left += width + COLUMN_GUTTER
        return lefts, widths

    def _line_extents(self, grid, cards) -> Tuple[List[float], List[float]]:
        heights = [0.0] * (max(position[1] for position in grid.values()) + 1)
        for cell_id, position in grid.items():
            heights[position[1]] = max(heights[position[1]], cards[cell_id].height)
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
        self.blocked: Set[Point] = set()
        for box in obstacles:
            self.blocked |= self._cells_around(box)
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

    def _cells_around(self, box: Geometry) -> Set[Point]:
        left, right = int(box.x - CARD_CLEARANCE) // GRID_STEP, int(box.x + box.width + CARD_CLEARANCE) // GRID_STEP
        top, bottom = int(box.y - CARD_CLEARANCE) // GRID_STEP, int(box.y + box.height + CARD_CLEARANCE) // GRID_STEP
        return {(x, y) for x in range(left, right + 1) for y in range(top, bottom + 1)}

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
    ) -> None:
        self._grid = grid
        self._owner = owner
        self._respect_held_ports = respect_held_ports
        self._begin = begin
        self._end = end
        self._heading_out = heading_out
        self._heading_in = heading_in
        self._came_from: Dict[Tuple[Point, Heading], Tuple[Point, Heading]] = {}

    def run(self) -> Optional[List[Point]]:
        start = (self._begin, self._heading_out)
        best = {start: 0}
        frontier = [(0, 0, self._begin, self._heading_out)]
        while frontier:
            _estimate, cost, cell, heading = heapq.heappop(frontier)
            if cost > best[(cell, heading)]:
                continue
            if cell == self._end and heading == self._heading_in:
                return self._walk_back((cell, heading))
            for step in self._steps(cell, heading):
                following = (cell[0] + step[0], cell[1] + step[1])
                total = cost + self._price(following, heading, step)
                key = (following, step)
                if total < best.get(key, float("inf")):
                    best[key] = total
                    self._came_from[key] = (cell, heading)
                    heapq.heappush(frontier, (total + ESTIMATE_WEIGHT * self._distance_left(following), total, following, step))
        return None

    def _distance_left(self, cell: Point) -> int:
        return abs(cell[0] - self._end[0]) + abs(cell[1] - self._end[1])

    def _steps(self, cell: Point, heading: Heading) -> List[Heading]:
        reverse = (-heading[0], -heading[1])
        return [step for step in _HEADINGS.values() if step != reverse and self._can_step(cell, heading, step)]

    def _can_step(self, cell: Point, heading: Heading, step: Heading) -> bool:
        grid = self._grid
        following = (cell[0] + step[0], cell[1] + step[1])
        if not grid.contains(following) or (following in grid.blocked and following != self._end):
            return False
        if self._respect_held_ports and grid.is_held_against(following, step, self._owner):
            return False
        along = grid.horizontal if step[0] else grid.vertical
        if following in along or cell in along:
            return False
        return step == heading or not grid.carries_arrow(cell)

    def _price(self, following: Point, heading: Heading, step: Heading) -> int:
        across = self._grid.vertical if step[0] else self._grid.horizontal
        return 1 + (TURN_PRICE if step != heading else 0) + (CROSSING_PRICE if following in across else 0)

    def _walk_back(self, last: Tuple[Point, Heading]) -> List[Point]:
        steps = [last]
        while steps[-1] in self._came_from:
            steps.append(self._came_from[steps[-1]])
        return [cell for cell, _heading in reversed(steps)]


class ArrowRouter:
    """Routes every arrow, retrying the ones that crossed until a pass finds nothing better."""

    def __init__(
        self,
        cards: List[DiagramCard],
        arrows: List[DiagramArrow],
        obstacles: Iterable[Geometry] = (),
        kept_paths: Iterable[List[Point]] = (),
    ) -> None:
        self._cards = {card.cell_id: card for card in cards}
        self._arrows = [arrow for arrow in arrows if self._draws(arrow)]
        self._obstacles = list(obstacles)
        self._kept_paths = list(kept_paths)

    def route(self) -> List[DiagramArrow]:
        for arrow in self._arrows:
            arrow.exit_side, arrow.entry_side = self._facing_sides(arrow)
        self._assign_ports()
        grid = self._grid_without(None)
        for arrow in sorted(self._arrows, key=self._length_between_cards):
            self._route_one(arrow, grid)
        for _ in range(REROUTING_ROUNDS):
            if not self._reroute_troubled():
                break
        return self._arrows

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
        source, target = self._cards[arrow.source].center, self._cards[arrow.target].center
        return abs(source[0] - target[0]) + abs(source[1] - target[1])

    def _facing_sides(self, arrow: DiagramArrow) -> Tuple[str, str]:
        source, target = self._cards[arrow.source], self._cards[arrow.target]
        if arrow.kind == INHERITANCE or target.y + target.height <= source.y:
            return ("top", "bottom") if target.y < source.y else ("bottom", "top")
        if target.y >= source.y + source.height:
            return ("bottom", "top")
        if self._card_between(source, target):
            return ("bottom", "bottom")
        return ("right", "left") if target.center[0] >= source.center[0] else ("left", "right")

    def _card_between(self, source: DiagramCard, target: DiagramCard) -> bool:
        """True when two cards in one row have a third between them, so the arrow has to go under it."""
        left, right = sorted((source, target), key=lambda card: card.x)
        top, bottom = max(left.y, right.y), min(left.y + left.height, right.y + right.height)
        return any(
            card.x >= left.x + left.width and card.x + card.width <= right.x and card.y < bottom and card.y + card.height > top
            for card in self._cards.values()
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
                grid.hold_port(self._stub_end(point, _HEADINGS[side]), _HEADINGS[side], id(arrow))
            if arrow is not lifted:
                grid.claim(arrow.cells)
        return grid

    def _assign_ports(self) -> None:
        """Give every arrow its own point on the side it uses, ordered by where the far end sits, so arrows on one side do not cross."""
        sides: Dict[Tuple[str, str], List[Tuple[DiagramArrow, bool]]] = {}
        for arrow in self._arrows:
            sides.setdefault((arrow.source, arrow.exit_side), []).append((arrow, True))
            sides.setdefault((arrow.target, arrow.entry_side), []).append((arrow, False))
        for (cell_id, side), users in sides.items():
            card = self._cards[cell_id]
            users.sort(key=lambda user: self._far_end_position(user, side))
            for position, (arrow, leaving) in enumerate(users):
                point = self._port(card, side, (position + 1) / (len(users) + 1))
                if leaving:
                    arrow.exit_point = point
                else:
                    arrow.entry_point = point
        for arrow in self._arrows:
            if len(sides[(arrow.source, arrow.exit_side)]) == 1 and len(sides[(arrow.target, arrow.entry_side)]) == 1:
                self._straighten(arrow)

    def _straighten(self, arrow: DiagramArrow) -> None:
        """Two cards that face each other with one arrow between them get a straight line, not a small step."""
        source, target = self._cards[arrow.source], self._cards[arrow.target]
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
        arrow, leaving = user
        far = self._cards[arrow.target if leaving else arrow.source].center
        return far[0] if side in _VERTICAL_SIDES else far[1]

    def _port(self, card: DiagramCard, side: str, fraction: float) -> Point:
        """On the grid along the side, so the arrow's first run stays straight wherever a person left the card."""
        if side in _VERTICAL_SIDES:
            along = round((card.x + card.width * fraction) / GRID_STEP) * GRID_STEP
            return (int(along), int(card.y + (card.height if side == "bottom" else 0)))
        along = round((card.y + card.height * fraction) / GRID_STEP) * GRID_STEP
        return (int(card.x + (card.width if side == "right" else 0)), int(along))

    def _route_one(self, arrow: DiagramArrow, grid: _RouteGrid) -> None:
        out, into = _HEADINGS[arrow.exit_side], _HEADINGS[arrow.entry_side]
        begin = self._stub_end(arrow.exit_point, out)
        end = self._stub_end(arrow.entry_point, into)
        heading_in = (-into[0], -into[1])
        cells = _ArrowSearch(grid, id(arrow), begin, end, out, heading_in).run()
        if cells is None:
            cells = _ArrowSearch(grid, id(arrow), begin, end, out, heading_in, respect_held_ports=False).run()
        arrow.routed = cells is not None
        arrow.corners = []
        arrow.cells = cells or []
        if cells is None:
            return
        grid.claim(cells)
        arrow.corners = self._corners(arrow.exit_point, cells, arrow.entry_point)

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
        trouble = [arrow for arrow in self._arrows if not arrow.routed]
        for index, first in enumerate(self._arrows):
            for second in self._arrows[index + 1:]:
                if first.routed and second.routed and paths_cross(first.path, second.path):
                    trouble.extend(arrow for arrow in (first, second) if arrow not in trouble)
        return trouble


def _shared_middle(start: float, length: float, other_start: float, other_length: float) -> Optional[int]:
    low, high = max(start, other_start), min(start + length, other_start + other_length)
    if high - low < 2 * GRID_STEP:
        return None
    return int((low + high) / 2 // GRID_STEP * GRID_STEP)


def _lines_cross(a: GridCell, b: GridCell, c: GridCell, d: GridCell) -> bool:
    """True when the straight lines a-b and c-d cross, used while cards are still being placed."""
    return _turn(a, b, c) * _turn(a, b, d) < 0 and _turn(c, d, a) * _turn(c, d, b) < 0


def _turn(a: GridCell, b: GridCell, c: GridCell) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


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
