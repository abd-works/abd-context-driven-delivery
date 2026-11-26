"""Places class cards and routes the arrows between them. Shared by every class-shaped diagram view.

Arrows search a 10px grid, so each one finds its own way around the cards and around the arrows already drawn,
rather than picking from a list of route shapes. An arrow never passes through a card, never runs along another
arrow, and leaves and arrives at its own point on the card. It crosses another arrow only when no other way exists.

The one exception is inheritance: the arrows from a base's subclasses are drawn as one fan, the standard UML tree. A
short stem leaves the single arrowhead in the middle of the base's side, and a straight line runs from the end of the
stem to each subclass, at whatever angle it lies, so a reader sees one family with one arrowhead.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import DiagramNode
from harness.whiteboard import Box
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import segments_cross

Point = Tuple[int, int]
Heading = Tuple[int, int]
# One straight stretch of an orthogonal path, from one corner to the next.
Run = Tuple[Point, Point]

GRID_STEP = 10
CARD_CLEARANCE = 20
# What each step inside another card's clearance costs: enough that an arrow keeps clear when it can, but a way out
# between cards a person placed close together, where a wall would leave the arrow no way at all.
CLEARANCE_PRICE = 60
PORT_STUB_STEPS = 3
PORT_APPROACH_STEPS = 6
ARROW_SPACING_STEPS = 1
# How long the stem of an inheritance fan is, from the arrowhead on the base to where the lines to the subclasses part.
FAN_STEM_STEPS = 3
TURN_PRICE = 40
# How far past an arrow's ends its first search reaches, in grid steps.
SEARCH_WINDOW_STEPS = 30
CROSSING_PRICE = 150
REROUTING_ROUNDS = 4
UNROUTED_TROUBLE = 1000
# The room between one row of cards and the next: space for the lines that fan out between them.
ROW_GAP = 140
PAGE_MARGIN = 60
ROUTING_MARGIN = 200
# How much wider than tall a page of cards is laid out.
PAGE_WIDTH_BIAS = 4
# How many times the layers are re-sorted under the cards they are joined to, down and up.
ORDERING_SWEEPS = 6
ESTIMATE_WEIGHT = 2
# How near a line between two rows passes a card on a row between them, in card places, to count as running into it.
NEAR_A_CARD = 0.25
SMALLEST_PORT_SPACING = 30
INHERITANCE = "inheritance"
GROUP_FILL_COLORS = ("#d6e4f5", "#d5e8d4", "#fff2cc", "#ffe6cc", "#e1d5e7", "#f8cecc", "#d0ece7", "#e6e6e6")

_HEADINGS = {"top": (0, -1), "bottom": (0, 1), "right": (1, 0), "left": (-1, 0)}
# Every step an arrow can take from a cell, in the order the search tries them.
_STEPS = tuple(_HEADINGS.values())
# The cost of a cell and heading no way has reached yet.
_UNREACHED = float("inf")
_VERTICAL_SIDES = ("bottom", "top")
_HORIZONTAL_SIDES = ("right", "left")


# How many decimal places an arrow's anchor fractions keep.
_ANCHOR_DIGITS = 4

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
    # Drawn as straight slanted lines between its corners, as an inheritance fan is, rather than at right angles.
    straight: bool = False

    @property
    def path(self) -> List[Point]:
        return [self.exit_point] + self.corners + [self.entry_point]

    def anchors_on(self, source: Box, target: Box) -> Tuple[float, float, float, float]:
        """Where it leaves the card it starts on and reaches the card it ends on, each as fractions of that card's
        width and height: (exit x, exit y, entry x, entry y)."""
        return (
            round((self.exit_point[0] - source.x) / source.w, _ANCHOR_DIGITS),
            round((self.exit_point[1] - source.y) / source.h, _ANCHOR_DIGITS),
            round((self.entry_point[0] - target.x) / target.w, _ANCHOR_DIGITS),
            round((self.entry_point[1] - target.y) / target.h, _ANCHOR_DIGITS),
        )

    def bends_from_middles(self, source: Box, target: Box) -> Optional[List[object]]:
        """Its route as offsets from its cards' middles: the way it leaves (`h` or `v`), then where each middle leg
        runs, the first half from the middle of the card it leaves, the rest from the middle of the card it reaches.
        Moving both cards together keeps the offsets; none for a route with no middle leg."""
        path = self.path
        if len(path) < 3:
            return None
        middles = [(path[index], path[index + 1]) for index in range(1, len(path) - 2)]
        from_side_count = math.ceil(len(middles) / 2)
        bends: List[object] = ["h" if path[0][1] == path[1][1] else "v"]
        for index, (start, end) in enumerate(middles):
            level = start[1] == end[1]
            middle = (source if index < from_side_count else target).center
            bends.append(round(start[1] - middle[1]) if level else round(start[0] - middle[0]))
        return bends




class CardPlacement:
    """Lays the cards out in layers: a base above the classes that derive from it, an owner above what it owns, so
    inheritance fans out downwards and most arrows run down the page.

    Each layer is a row, ordered so a card sits under the cards it is joined to and a module's cards stay together; a
    layer too wide for the page wraps onto further rows. The order is worked out, not searched for, so the same model
    always gives the same diagram.
    """

    def __init__(self, cards: List[DiagramNode], arrows: List[DiagramArrow]) -> None:
        self._cards = cards
        self._by_id = {card.cell_id: card for card in cards}
        self._links = [arrow for arrow in arrows if arrow.source != arrow.target and arrow.source in self._by_id and arrow.target in self._by_id]
        self._spacing = CardSpacing(cards, self._links)

    def place(self) -> None:
        if not self._cards:
            return
        layers = self._ordered(self._layers())
        self._set_positions([row for layer in layers for row in self._wrapped(layer)])

    def _downward_links(self) -> List[Tuple[str, str]]:
        """Each link as (upper card, lower card), inheritance first, leaving out any that would close a loop."""
        below: Dict[str, Set[str]] = {card.cell_id: set() for card in self._cards}
        kept: List[Tuple[str, str]] = []
        for link in sorted(self._links, key=lambda link: link.kind != INHERITANCE):
            upper, lower = (link.target, link.source) if link.kind == INHERITANCE else (link.source, link.target)
            if upper == lower or self._reaches(below, lower, upper):
                continue
            below[upper].add(lower)
            kept.append((upper, lower))
        return kept

    def _reaches(self, below: Dict[str, Set[str]], start: str, goal: str) -> bool:
        seen, waiting = {start}, [start]
        while waiting:
            here = waiting.pop()
            if here == goal:
                return True
            for lower in below[here] - seen:
                seen.add(lower)
                waiting.append(lower)
        return False

    def _layers(self) -> List[List[str]]:
        """Every card one layer below the lowest card above it; a card nothing joins sits on the top layer. A subclass
        sits right under its base, whatever owns it, so the lines fanning out from the base stay short."""
        depth = {card.cell_id: 0 for card in self._cards}
        subclasses = {link.source for link in self._links if link.kind == INHERITANCE}
        bases = {(link.target, link.source) for link in self._links if link.kind == INHERITANCE}
        links = [(upper, lower) for upper, lower in self._downward_links() if lower not in subclasses or (upper, lower) in bases]
        for _ in range(len(self._cards)):
            moved = False
            for upper, lower in links:
                if depth[lower] <= depth[upper]:
                    depth[lower], moved = depth[upper] + 1, True
            if not moved:
                break
        layers: List[List[str]] = [[] for _ in range(max(depth.values()) + 1)]
        for card in self._cards:
            layers[depth[card.cell_id]].append(card.cell_id)
        return [layer for layer in layers if layer]

    def _ordered(self, layers: List[List[str]]) -> List[List[str]]:
        """Each layer sorted under the cards it is joined to, sweeping down and up the layers a few times."""
        neighbours: Dict[str, List[str]] = {card.cell_id: [] for card in self._cards}
        for link in self._links:
            neighbours[link.source].append(link.target)
            neighbours[link.target].append(link.source)
        groups = sorted({card.group for card in self._cards})
        layers = [sorted(layer, key=lambda cell_id: groups.index(self._by_id[cell_id].group)) for layer in layers]
        for sweep in range(ORDERING_SWEEPS):
            place = {cell_id: index / max(1, len(layer) - 1) for layer in layers for index, cell_id in enumerate(layer)}
            sweep_layers = layers if sweep % 2 == 0 else list(reversed(layers))
            for layer in sweep_layers:
                layer.sort(key=lambda cell_id: self._middle_of(neighbours[cell_id], place, place[cell_id]))
                place.update({cell_id: index / max(1, len(layer) - 1) for index, cell_id in enumerate(layer)})
        return self._with_fewer_crossings(layers)

    def _with_fewer_crossings(self, layers: List[List[str]]) -> List[List[str]]:
        """Swap neighbours in a row while that leaves fewer straight lines between joined cards crossing."""
        crossings = self._crossings(layers)
        for _ in range(ORDERING_SWEEPS):
            fewer = self._swap_neighbours(layers, crossings)
            if fewer == crossings:
                break
            crossings = fewer
        return layers

    def _swap_neighbours(self, layers: List[List[str]], crossings: int) -> int:
        """One pass over every row, keeping each swap of two neighbours that leaves fewer crossings; the crossings left."""
        for layer in layers:
            for index in range(len(layer) - 1):
                layer[index], layer[index + 1] = layer[index + 1], layer[index]
                swapped = self._crossings(layers)
                if swapped < crossings:
                    crossings = swapped
                else:
                    layer[index], layer[index + 1] = layer[index + 1], layer[index]
        return crossings

    def _crossings(self, layers: List[List[str]]) -> int:
        """Lines between joined cards that cross, plus each card a line passes on a row between its ends, which its
        arrow has to go round across the arrows leaving that row."""
        spot = {cell_id: (index, depth) for depth, layer in enumerate(layers) for index, cell_id in enumerate(layer)}
        lines = [(spot[link.source], spot[link.target], {link.source, link.target}) for link in self._links]
        crossed = sum(
            1 for index, (start, end, ends) in enumerate(lines) for other_start, other_end, other_ends in lines[index + 1:]
            if not ends & other_ends and segments_cross((start, end), (other_start, other_end))
        )
        return crossed + sum(self._cards_passed(start, end, layers) for start, end, _ends in lines)

    def _cards_passed(self, start: Tuple[int, int], end: Tuple[int, int], layers: List[List[str]]) -> int:
        (start_index, start_depth), (end_index, end_depth) = sorted((start, end), key=lambda spot: spot[1])
        passed = 0
        for depth in range(start_depth + 1, end_depth):
            along = start_index + (end_index - start_index) * (depth - start_depth) / (end_depth - start_depth)
            if abs(along - round(along)) < NEAR_A_CARD and 0 <= round(along) < len(layers[depth]):
                passed += 1
        return passed

    def _middle_of(self, cell_ids: List[str], place: Dict[str, float], otherwise: float) -> float:
        return sum(place[cell_id] for cell_id in cell_ids) / len(cell_ids) if cell_ids else otherwise

    def _wrapped(self, layer: List[str]) -> List[List[str]]:
        """A layer as rows no wider than the page, each a run of the layer in order."""
        rows: List[List[str]] = [[]]
        width = 0.0
        for cell_id in layer:
            card_width = self._by_id[cell_id].geometry.w
            if rows[-1] and width + card_width > self._page_width():
                rows.append([])
                width = 0.0
            rows[-1].append(cell_id)
            width += card_width + CardSpacing.GAP_ACROSS
        return rows

    def _page_width(self) -> float:
        """Wide enough for the cards to fill a page somewhat wider than it is tall."""
        area = sum(card.geometry.w * card.geometry.h * 4 for card in self._cards)
        widest = max(card.geometry.w for card in self._cards)
        return max(widest, math.sqrt(area * PAGE_WIDTH_BIAS))

    def _set_positions(self, rows: List[List[str]]) -> None:
        """Rows top to bottom, each centred on the widest, cards in a row spaced by the arrows between them; then each
        card stood in line under the one card above it that it is joined to, where the room beside it allows."""
        self._set_rows(rows)
        for upper, lower in zip(rows, rows[1:]):
            for index in range(len(lower)):
                self._line_up(lower, index, upper)

    def _line_up(self, row: List[str], index: int, upper: List[str]) -> None:
        """Move the card at index in row so its middle is under the middle of the one card of the row above it is
        joined to, so the arrow between them runs straight down; a card joined to several, or with a neighbour in the
        way, stays where it is."""
        cell_id = row[index]
        joined = [other for other in upper if any({link.source, link.target} == {cell_id, other} for link in self._links)]
        if len(joined) != 1:
            return
        card = self._by_id[cell_id]
        wanted = round((self._by_id[joined[0]].geometry.center[0] - card.geometry.w / 2) / GRID_STEP) * GRID_STEP
        if not self._room_for(row, index, wanted):
            return
        card.geometry = card.geometry.moved_to(wanted, card.geometry.y)

    def _room_for(self, row: List[str], index: int, left: float) -> bool:
        """Whether the card at index in row can stand at left, keeping the page's margin and the gap to each neighbour."""
        width = self._by_id[row[index]].geometry.w
        if left < PAGE_MARGIN:
            return False
        if index > 0:
            before = self._by_id[row[index - 1]].geometry
            if left < before.x + before.w + self._spacing.gap_between(row[index - 1], row[index], across=True):
                return False
        if index + 1 < len(row):
            after = self._by_id[row[index + 1]].geometry
            if left + width + self._spacing.gap_between(row[index], row[index + 1], across=True) > after.x:
                return False
        return True

    def _set_rows(self, rows: List[List[str]]) -> None:
        """Rows top to bottom, each centred on the widest, cards in a row spaced by the arrows between them."""
        widths = [self._row_width(row) for row in rows]
        page_width = max(widths)
        top = float(PAGE_MARGIN)
        for row, width in zip(rows, widths):
            left = PAGE_MARGIN + (page_width - width) / 2
            for index, cell_id in enumerate(row):
                card = self._by_id[cell_id]
                card.geometry = card.geometry.moved_to(left // GRID_STEP * GRID_STEP, top)
                left += card.geometry.w
                if index + 1 < len(row):
                    left += self._spacing.gap_between(cell_id, row[index + 1], across=True)
            top += max(self._by_id[cell_id].geometry.h for cell_id in row) + ROW_GAP
            top = math.ceil(top / GRID_STEP) * GRID_STEP

    def _row_width(self, row: List[str]) -> float:
        gaps = sum(self._spacing.gap_between(first, second, across=True) for first, second in zip(row, row[1:]))
        return sum(self._by_id[cell_id].geometry.w for cell_id in row) + gaps


class CardSpacing:
    """Closes up the empty space on a page without rearranging it, so a reader sees the cards side by side rather than
    islands on a mostly empty page.

    Every card keeps its place relative to its neighbours: what was left of it stays left, what was above stays above.
    Only the gaps shrink, to the room the arrows between two cards need: a few grid lines, and one more lane for each
    arrow either card sends or takes, up to MOST_GAP. A gap a person left smaller than that stays as it was.
    """

    GAP_ACROSS = 60
    GAP_DOWN = 80
    LANE_ROOM = 2 * GRID_STEP
    MOST_GAP = 300

    def __init__(self, cards: List[DiagramNode], arrows: List[DiagramArrow]) -> None:
        self._cards = cards
        self._arrow_counts: Dict[str, int] = {card.cell_id: 0 for card in cards}
        for arrow in arrows:
            for end in {arrow.source, arrow.target} & set(self._arrow_counts):
                self._arrow_counts[end] += 1

    def gap_between(self, first: str, second: str, across: bool) -> int:
        """The room two cards next to each other keep between them, across the page or down it."""
        lanes = self._arrow_counts.get(first, 0) + self._arrow_counts.get(second, 0)
        return min(self.MOST_GAP, (self.GAP_ACROSS if across else self.GAP_DOWN) + self.LANE_ROOM * lanes)

    def close_gaps(self) -> bool:
        """Moves the cards closer together; True when any card moved."""
        before = {card.cell_id: card.geometry for card in self._cards}
        if len(self._cards) < 2:
            return False
        lefts = _GapAxis(self, across=True).closed_up(before, before)
        for card in self._cards:
            card.geometry = card.geometry.moved_to(lefts[card.cell_id], card.geometry.y)
        across = {card.cell_id: card.geometry for card in self._cards}
        tops = _GapAxis(self, across=False).closed_up(across, before)
        for card in self._cards:
            card.geometry = card.geometry.moved_to(card.geometry.x, tops[card.cell_id])
        return any(card.geometry != before[card.cell_id] for card in self._cards)


class _GapAxis:
    """One axis CardSpacing closes the gaps along: across the page, or down it."""

    def __init__(self, spacing: CardSpacing, across: bool) -> None:
        self._spacing = spacing
        self._across = across
        # The sides of a box this axis reads: its start and size along the axis, then across it.
        self._start, self._size = ("x", "w") if across else ("y", "h")
        self._side_start, self._side_size = ("y", "h") if across else ("x", "w")

    def closed_up(self, boxes: Dict[str, Box], order: Dict[str, Box]) -> Dict[str, float]:
        """Each card's new start along this axis: as near the page's start as the cards before it on this axis allow.
        ``order`` is where the cards were before any moved, which decides what comes before what."""
        start, size = self._start, self._size
        page_start = min(getattr(box, start) for box in order.values())
        placed: Dict[str, float] = {}
        for cell_id in sorted(boxes, key=lambda name: getattr(order[name], start)):
            was = order[cell_id]
            new_start = page_start
            for other_id, other_start in placed.items():
                other_was = order[other_id]
                if getattr(other_was, start) + getattr(other_was, size) > getattr(was, start) or not self._side_by_side(boxes, cell_id, other_id):
                    continue
                kept_gap = min(self._spacing.gap_between(cell_id, other_id, self._across), getattr(was, start) - getattr(other_was, start) - getattr(other_was, size))
                new_start = max(new_start, other_start + getattr(boxes[other_id], size) + kept_gap)
            placed[cell_id] = math.ceil(new_start / GRID_STEP) * GRID_STEP
        return placed

    def _side_by_side(self, boxes: Dict[str, Box], cell_id: str, other_id: str) -> bool:
        """Two cards close enough on the other axis that closing the gap on this one would bring them too close."""
        box, other = boxes[cell_id], boxes[other_id]
        side_start, side_size = self._side_start, self._side_size
        apart = max(getattr(other, side_start) - getattr(box, side_start) - getattr(box, side_size), getattr(box, side_start) - getattr(other, side_start) - getattr(other, side_size))
        return apart < self._spacing.gap_between(cell_id, other_id, not self._across)


class _RouteGrid:
    """The page as grid cells: which are inside a card's clearance, and which already carry an arrow."""

    def __init__(self, obstacles: Iterable[Box], width: float, height: float) -> None:
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

    def cells_held_against(self, owner: int) -> Tuple[Set[Point], Set[Point]]:
        """The cells another arrow's port or its approach closes to owner's arrow, for a vertical step and for a
        horizontal one."""
        ports = {cell for cell, holders in self._held_for.items() if owner not in holders}
        vertical = ports | {cell for cell, holders in self._approach_vertical.items() if owner not in holders}
        horizontal = ports | {cell for cell, holders in self._approach_horizontal.items() if owner not in holders}
        return vertical, horizontal

    def cells_around(self, box: Box, clearance: int = CARD_CLEARANCE) -> Set[Point]:
        left, right = int(box.x - clearance) // GRID_STEP, int(box.x + box.w + clearance) // GRID_STEP
        top, bottom = int(box.y - clearance) // GRID_STEP, int(box.y + box.h + clearance) // GRID_STEP
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


class _SearchedArrow(NamedTuple):
    """The arrow a search finds a way for: whose ports it may use, the cells it runs between, and how it leaves and
    arrives."""

    owner: int
    begin: Point
    end: Point
    heading_out: Heading
    heading_in: Heading


class _SearchAttempt(NamedTuple):
    """How freely one try of the search may go: the cells it may use, as left, top, right, bottom (the whole page when
    None); whether it keeps clear of other arrows' ports; and, as a last resort when cards a person placed close
    together leave the only gap already taken, whether it may run along or turn on another arrow at the price of a
    crossing."""

    window: Optional[Tuple[int, int, int, int]]
    respect_held_ports: bool
    may_run_along: bool


class _Move(NamedTuple):
    """One step a search may take out of a cell: onto the cell following, in the heading of the step, and whether it
    goes straight on from the heading the search came in by or turns."""

    following: Point
    step: Heading
    straight: bool


class _ArrowSearch:
    """One arrow's cheapest way across the grid, paying for each corner and far more for each crossing."""

    def __init__(self, grid: _RouteGrid, arrow: _SearchedArrow, attempt: _SearchAttempt) -> None:
        self._grid = grid
        self._arrow = arrow
        self._attempt = attempt
        self._window = attempt.window if attempt.window is not None else (0, 0, grid.columns - 1, grid.lines - 1)
        self._came_from: Dict[Tuple[Point, Heading], Tuple[Point, Heading]] = {}
        self._held_vertical, self._held_horizontal = self._cells_held_against()
        # A card a person placed right against the port leaves no cell to come straight in from, so the arrow may
        # come in from the side for its last step.
        end, heading_in = arrow.end, arrow.heading_in
        self._any_heading_in = (end[0] - heading_in[0], end[1] - heading_in[1]) in grid.inside_cards
        self._best: Dict[Tuple[Point, Heading], int] = {(arrow.begin, arrow.heading_out): 0}
        self._frontier: List[Tuple[int, int, Point, Heading]] = [(0, 0, arrow.begin, arrow.heading_out)]
        # The cost each cell and heading was searched from at. The estimate counts the distance left twice over, so a
        # cheaper way to a cell can turn up after it was searched from. It is searched from again only when the new way
        # saves a crossing: saving a turn or a few steps cost far more time than it gained.
        self._expanded: Dict[Tuple[Point, Heading], int] = {}

    def run(self) -> Optional[List[Point]]:
        """The cheapest way from the arrow's begin to its end, searched from the cheapest cell and heading first; none
        when no way is open."""
        frontier, best, expanded = self._frontier, self._best, self._expanded
        while frontier:
            _estimate, cost, cell, heading = heapq.heappop(frontier)
            here = (cell, heading)
            if cost > best[here] or cost > expanded.get(here, _UNREACHED) - CROSSING_PRICE:
                continue
            expanded[here] = cost
            if self._arrives(cell, heading):
                return self._walk_back(here)
            self._expand(cell, heading, cost)
        return None

    def _arrives(self, cell: Point, heading: Heading) -> bool:
        return cell == self._arrow.end and (heading == self._arrow.heading_in or self._any_heading_in)

    def _expand(self, cell: Point, heading: Heading, cost: int) -> None:
        """Price each step out of cell but the one straight back, and offer each the arrow may take."""
        grid = self._grid
        carries = (cell in grid.horizontal, cell in grid.vertical)
        for step in _STEPS:
            if step[0] == -heading[0] and step[1] == -heading[1]:
                continue
            move = _Move((cell[0] + step[0], cell[1] + step[1]), step, step == heading)
            price = self._price(move, carries)
            if price is not None:
                self._offer(move, cost + price, (cell, heading))

    def _price(self, move: _Move, carries: Tuple[bool, bool]) -> Optional[int]:
        """What the step onto following costs: one, a turn's price, a crossing's for crossing or running along another
        arrow, and the clearance price beside a card. None where the arrow may not go: outside the window, into a card
        but its own end, onto a cell held for another arrow's port, or along another arrow while the attempt forbids it."""
        grid, end = self._grid, self._arrow.end
        following, step = move.following, move.step
        left, top, right, bottom = self._window
        if not (left <= following[0] <= right and top <= following[1] <= bottom):
            return None
        if following in grid.inside_cards and following != end:
            return None
        if following in (self._held_horizontal if step[0] else self._held_vertical):
            return None
        running_along = self._runs_along(move, carries)
        if running_along and not self._attempt.may_run_along:
            return None
        crossing = following in (grid.vertical if step[0] else grid.horizontal)
        price = 1 + (0 if move.straight else TURN_PRICE) + (CROSSING_PRICE if crossing or running_along else 0)
        return price + (CLEARANCE_PRICE if following in grid.blocked and following != end else 0)

    def _runs_along(self, move: _Move, carries: Tuple[bool, bool]) -> bool:
        """Whether the move runs along an arrow already drawn, or turns on one."""
        grid = self._grid
        if move.step[0]:
            along = move.following in grid.horizontal or carries[0]
        else:
            along = move.following in grid.vertical or carries[1]
        return along or (not move.straight and (carries[0] or carries[1]))

    def _offer(self, move: _Move, total: int, came_from: Tuple[Point, Heading]) -> None:
        """Keep the way to the cell the move reaches at total when it is cheaper than any found before, to search from
        later."""
        following, step = move.following, move.step
        key = (following, step)
        if total >= self._best.get(key, _UNREACHED) or total > self._expanded.get(key, _UNREACHED) - CROSSING_PRICE:
            return
        self._best[key] = total
        self._came_from[key] = came_from
        end = self._arrow.end
        distance = abs(end[0] - following[0]) + abs(end[1] - following[1])
        heapq.heappush(self._frontier, (total + ESTIMATE_WEIGHT * distance, total, following, step))

    def _cells_held_against(self) -> Tuple[Set[Point], Set[Point]]:
        """The cells other arrows' ports and approaches close to this arrow, for a vertical step and for a horizontal one; none when
        the arrow may pass other arrows' ports."""
        if not self._attempt.respect_held_ports:
            return set(), set()
        return self._grid.cells_held_against(self._arrow.owner)

    def _walk_back(self, last: Tuple[Point, Heading]) -> List[Point]:
        steps = [last]
        while steps[-1] in self._came_from:
            steps.append(self._came_from[steps[-1]])
        return [cell for cell, _heading in reversed(steps)]


class _InheritanceFan:
    """The arrows from a base's subclasses drawn as one fan: a short stem from the single arrowhead on the base, then a
    straight line from the end of the stem to each subclass, the standard UML tree drawn at angles.

    Each arrow still runs from its own subclass to the base, so a diagram read back gives every subclass its base. The
    stem is the same for all of them, so the base shows one arrowhead however many subclasses it has."""

    def __init__(self, arrows: List[DiagramArrow], cards: Dict[str, DiagramNode]) -> None:
        self.arrows = arrows
        self._cards = cards

    def holds(self, arrow: DiagramArrow) -> bool:
        return any(member is arrow for member in self.arrows)

    @property
    def entry_point(self) -> Point:
        """The middle of the base's side, where the one arrowhead sits."""
        base = self._cards[self.arrows[0].target].geometry
        middle = round((base.x + base.w / 2) / GRID_STEP) * GRID_STEP
        return (int(middle), int(base.y + (base.h if self.arrows[0].entry_side == "bottom" else 0)))

    @property
    def joint(self) -> Point:
        """Where the stem ends and the lines to the subclasses part."""
        entry = self.entry_point
        outward = _HEADINGS[self.arrows[0].entry_side][1]
        return (entry[0], entry[1] + outward * FAN_STEM_STEPS * GRID_STEP)

    def face_the_joint(self) -> None:
        """Each subclass sends its line from the side that faces the end of the stem."""
        joint_x, joint_y = self.joint
        for arrow in self.arrows:
            card = self._cards[arrow.source].geometry
            if card.y >= joint_y:
                arrow.exit_side = "top"
            elif card.y + card.h <= joint_y:
                arrow.exit_side = "bottom"
            else:
                arrow.exit_side = "left" if card.center[0] > joint_x else "right"

    def draw(self) -> None:
        """Every arrow takes the stem's point on the base and bends once, at the end of the stem."""
        entry, joint = self.entry_point, self.joint
        stem = self._cells_along([joint, entry])
        for arrow in self.arrows:
            arrow.entry_point, arrow.corners, arrow.cells = entry, [joint], stem
            arrow.routed = arrow.straight = True

    def _cells_along(self, path: List[Point]) -> List[Point]:
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


class ArrowRouter:
    """Routes every arrow, retrying the ones that crossed until a pass finds nothing better."""

    def __init__(self, cards: List[DiagramNode], arrows: List[DiagramArrow], kept_paths: Iterable[List[Point]] = ()) -> None:
        self._cards = {card.cell_id: card for card in cards}
        self._arrows = [arrow for arrow in arrows if self._draws(arrow)]
        self._kept_paths = list(kept_paths)
        self._fans: List[_InheritanceFan] = []

    def route(self) -> List[DiagramArrow]:
        if not self._arrows:
            return []
        for arrow in self._arrows:
            arrow.exit_side, arrow.entry_side = self._facing_sides(arrow)
        self._one_side_per_base()
        grid = self._grid_with_fans()
        for arrow in sorted(self._arrows_alone(), key=self._length_between_cards):
            self._route_one(arrow, grid)
        for _ in range(REROUTING_ROUNDS):
            if not self._reroute_troubled():
                break
        return self._arrows

    def _grid_with_fans(self) -> _RouteGrid:
        """Draw every inheritance fan before the other arrows, so they find their way around its stem."""
        self._fans = self._families()
        for fan in self._fans:
            fan.face_the_joint()
        self._assign_ports()
        for fan in self._fans:
            fan.draw()
        return self._grid_without(None)

    def _search_cells(self, arrow: DiagramArrow, grid: _RouteGrid, owner: int) -> Optional[List[Point]]:
        """The cells of this arrow's cheapest way, keeping clear of other arrows' ports when it can."""
        out, into = _HEADINGS[arrow.exit_side], _HEADINGS[arrow.entry_side]
        begin, end = self._clear_stub_end(arrow.exit_point, out, grid), self._clear_stub_end(arrow.entry_point, into, grid)
        heading_in = (-into[0], -into[1])
        window = self._window_around(grid, [begin, end])
        # In the window round the arrow: clear of other arrows' ports, then past them, then along other arrows; only then
        # over the whole page. A search that finds no way walks its whole area, so the page is searched last.
        searched = _SearchedArrow(owner, begin, end, out, heading_in)
        for attempt in self._attempts_in(window):
            cells = _ArrowSearch(grid, searched, attempt).run()
            if cells is not None:
                return cells
        return None

    def _attempts_in(self, window: Tuple[int, int, int, int]) -> Tuple[_SearchAttempt, ...]:
        """Each search an arrow tries, in order, until one finds a way."""
        return (
            _SearchAttempt(window, respect_held_ports=True, may_run_along=False),
            _SearchAttempt(window, respect_held_ports=False, may_run_along=False),
            _SearchAttempt(window, respect_held_ports=False, may_run_along=True),
            _SearchAttempt(None, respect_held_ports=False, may_run_along=False),
            _SearchAttempt(None, respect_held_ports=False, may_run_along=True),
        )

    def _window_around(self, grid: _RouteGrid, cells: List[Point]) -> Tuple[int, int, int, int]:
        """The part of the page an arrow is searched in first: the box round its ends, with room to go
        round what is in between. Searching the whole page for every arrow took hours on a large diagram; a way that
        leaves this box is one a reader would not follow anyway."""
        left, top = min(x for x, _ in cells), min(y for _, y in cells)
        right, bottom = max(x for x, _ in cells), max(y for _, y in cells)
        spare = SEARCH_WINDOW_STEPS + (right - left + bottom - top) // 2
        return (max(0, left - spare), max(0, top - spare), min(grid.columns - 1, right + spare), min(grid.lines - 1, bottom + spare))

    def _families(self) -> List[_InheritanceFan]:
        """One fan for each base, holding the arrows from all its subclasses."""
        families: Dict[str, List[DiagramArrow]] = {}
        for arrow in self._arrows:
            if arrow.kind == INHERITANCE:
                families.setdefault(arrow.target, []).append(arrow)
        return [_InheritanceFan(arrows, self._cards) for arrows in families.values()]

    def _fan_of(self, arrow: DiagramArrow) -> Optional[_InheritanceFan]:
        return next((fan for fan in self._fans if fan.holds(arrow)), None)

    def _port_owner(self, arrow: DiagramArrow) -> int:
        """Who a port is kept open for: the whole fan for its arrows, since they share the stem."""
        fan = self._fan_of(arrow)
        return id(fan if fan is not None else arrow)

    def _arrows_alone(self) -> List[DiagramArrow]:
        """The arrows routed one by one: every arrow that is not part of a fan."""
        return [arrow for arrow in self._arrows if self._fan_of(arrow) is None]

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
        return sum(1 for other in self._arrows if other is not arrow and other.routed and not other.straight and paths_cross(arrow.path, other.path))

    def _draws(self, arrow: DiagramArrow) -> bool:
        return arrow.source != arrow.target and arrow.source in self._cards and arrow.target in self._cards

    def _length_between_cards(self, arrow: DiagramArrow) -> float:
        source, target = self._cards[arrow.source].geometry.center, self._cards[arrow.target].geometry.center
        return abs(source[0] - target[0]) + abs(source[1] - target[1])

    def _facing_sides(self, arrow: DiagramArrow) -> Tuple[str, str]:
        source, target = self._cards[arrow.source].geometry, self._cards[arrow.target].geometry
        if arrow.kind == INHERITANCE or target.y + target.h <= source.y:
            return ("top", "bottom") if target.y < source.y else ("bottom", "top")
        if target.y >= source.y + source.h:
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
                    arrow.exit_side = "top" if source.y >= base.y + base.h else "bottom"
                else:
                    arrow.exit_side = "bottom" if source.y + source.h <= base.y else "top"
                arrow.entry_side = side

    def _card_between(self, source: Box, target: Box) -> bool:
        """True when two cards in one row have a third between them, so the arrow has to go under it."""
        left, right = sorted((source, target), key=lambda card: card.x)
        top, bottom = max(left.y, right.y), min(left.y + left.h, right.y + right.h)
        return any(
            card.x >= left.x + left.w and card.x + card.w <= right.x and card.y < bottom and card.y + card.h > top
            for card in (node.geometry for node in self._cards.values())
        )

    def _grid_without(self, lifted: Optional[DiagramArrow]) -> _RouteGrid:
        boxes = [card.geometry for card in self._cards.values()]
        width = max(box.x + box.w for box in boxes) + ROUTING_MARGIN
        height = max(box.y + box.h for box in boxes) + ROUTING_MARGIN
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
        A fan sets its own point on its base, the middle of the side."""
        sides: Dict[Tuple[str, str], List[Tuple[DiagramArrow, bool]]] = {}
        for arrow in self._arrows:
            sides.setdefault((arrow.source, arrow.exit_side), []).append((arrow, True))
            if self._fan_of(arrow) is None:
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
        for arrow in self._arrows_alone():
            if len(sides[(arrow.source, arrow.exit_side)]) == 1 and len(sides[(arrow.target, arrow.entry_side)]) == 1:
                self._straighten(arrow)

    def _straighten(self, arrow: DiagramArrow) -> None:
        """Two cards that face each other with one arrow between them get a straight line, not a small step."""
        source, target = self._cards[arrow.source].geometry, self._cards[arrow.target].geometry
        across = arrow.exit_side in _VERTICAL_SIDES
        shared = self._shared_middle(source, target, across)
        if shared is None:
            return
        if across:
            arrow.exit_point = (shared, arrow.exit_point[1])
            arrow.entry_point = (shared, arrow.entry_point[1])
        else:
            arrow.exit_point = (arrow.exit_point[0], shared)
            arrow.entry_point = (arrow.entry_point[0], shared)

    def _shared_middle(self, source: Box, target: Box, across: bool) -> Optional[int]:
        """The grid line in the middle of where two cards overlap, across the page or down it; None when they overlap
        too little for a straight line between them."""
        start, length, other_start, other_length = (
            (source.x, source.w, target.x, target.w) if across else (source.y, source.h, target.y, target.h)
        )
        low, high = max(start, other_start), min(start + length, other_start + other_length)
        if high - low < 2 * GRID_STEP:
            return None
        return int((low + high) / 2 // GRID_STEP * GRID_STEP)

    def _far_end_position(self, user: Tuple[DiagramArrow, bool], side: str) -> float:
        """Where the far end sits along this side."""
        arrow, leaving = user
        far_end = self._cards[arrow.target if leaving else arrow.source].geometry.center
        return far_end[0 if side in _VERTICAL_SIDES else 1]

    def _port(self, card: Box, side: str, fraction: float) -> Point:
        """On the grid along the side, so the arrow's first run stays straight wherever a person left the card."""
        if side in _VERTICAL_SIDES:
            along = round((card.x + card.w * fraction) / GRID_STEP) * GRID_STEP
            return (int(along), int(card.y + (card.h if side == "bottom" else 0)))
        along = round((card.y + card.h * fraction) / GRID_STEP) * GRID_STEP
        return (int(card.x + (card.w if side == "right" else 0)), int(along))

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
        """Arrows routed alone that are unrouted or cross another. A fan stays as drawn, and its slanted lines are not
        counted: no arrow can go round them all."""
        alone = self._arrows_alone()
        trouble = [arrow for arrow in alone if not arrow.routed]
        for index, first in enumerate(self._arrows):
            for second in self._arrows[index + 1:]:
                if first.routed and second.routed and not (first.straight or second.straight) and paths_cross(first.path, second.path):
                    trouble.extend(arrow for arrow in (first, second) if arrow in alone and arrow not in trouble)
        return trouble


def paths_cross(first: List[Point], second: List[Point]) -> bool:
    """True when a run of one orthogonal path crosses a run of the other at a right angle."""
    return any(
        _runs_cross(run, other_run)
        for run in zip(first, first[1:])
        for other_run in zip(second, second[1:])
    )


def _runs_cross(run: Run, other_run: Run) -> bool:
    run_is_level, other_is_level = run[0][1] == run[1][1], other_run[0][1] == other_run[1][1]
    if run_is_level == other_is_level:
        return False
    (left, right), (top, bottom) = (run, other_run) if run_is_level else (other_run, run)
    return (
        min(left[0], right[0]) <= top[0] <= max(left[0], right[0])
        and min(top[1], bottom[1]) <= left[1] <= max(top[1], bottom[1])
    )
