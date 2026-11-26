"""How UX takes part in the graph: each file a UX map is written in (its drawing, its board, its JSON, the mockup page
that carries it, its UX context) is read by its format into a map, whose screens, regions, controls, interactions,
transitions, content types, nav components, and context are added to the graph that holds UX as they are; then each
screen and each control is linked to the stories, scenarios, and steps it serves, and each screen to the domain classes
its domain terms name."""

from __future__ import annotations

import html
import json
import os
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from harness.agent_tools.progress import report_progress
from harness.graph.graph import Node
from harness.graph.location import Location
from harness.graph.model_node import schema_sync_paused
from harness.graph.schema_conformance import EXEMPT_FACT
from harness.graph.skipped_folders import skips_folder
from harness.graph.practice_node_types import PracticeNodeTypes
from harness.graph.practice_reading import PracticeReading
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

from cdd_guidance.practices.ux.model.nodes import Interaction, NavComponent, Screen, Transition
from cdd_guidance.practices.stories.model.story_tree import KEY_SEPARATOR, StoryTree, WrittenStoryNodes
from cdd_guidance.practices.ux.model.story_link import StoryLink
from cdd_guidance.practices.ux.model.ux_map import ScreenNotOnMap, UxMap
from cdd_guidance.practices.ux.model.ux_node import UxNode

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance

# Documents sit in a folder's `.context`, which a scan of code never enters; a UX map's drawing and context are there.
_CONTEXT_FOLDER = ".context"
# The fact the practice's root keeps of each UX file it could not read as a map, with the reason.
UNREAD_FILES_FACT = "unread_files"
# How a file writes a node's own name: a JSON record's name field, the text of a drawing's cell, plain or bold, or the
# words of a board's section or the first line of its card.
_NAME_MARKS = ('"name": "{}"', 'value="{}"', 'value="&lt;b&gt;{}&lt;/b&gt;"', '"text": "{}"', '"text": "**{}**')
# An aggregate groups the classes it holds and is named for its root, so a domain term names the root, not the group.
_GROUP_TYPES = frozenset({"Aggregate"})
# What joins the parts of a bound field's path: `order.shippingAddress.city`.
_PATH_SEPARATOR = "."
# The kind of story node a screen or a control serves under each of its edges, and the fact that keeps what it serves
# as its file writes it.
_SHOWN = (("Story", "shows", "story_keys"), ("Scenario", "showsScenarios", "scenario_keys"), ("Step", "showsSteps", "step_keys"))
# The node types that serve stories: a screen, and each kind of control on it.
_SERVING_TYPES = ("Screen", "Control", "StoryDemoControl")


class UxNodeTypes(PracticeNodeTypes):
    """UX's node types: a schema's ``map`` is a ``UxMap``, and a map lists its screens and a step its ``ands``."""

    schema_node_types = {"map": "UxMap"}
    child_lists = frozenset({"screens", "ands"})
    edge_order = {"screens": 1, "ands": 9}


class UxReading(PracticeReading):
    """How UX takes part in the graph: it reads each file a UX map is written in, after the practices its screens link
    to, adds the map's nodes to its graph, and links each screen and control to the stories, scenarios, and steps it
    serves and each screen to the domain classes its domain terms name. It checks its screen rules on those nodes."""

    reads_after = (Stories, CleanEngineering, Ddd)
    types = UxNodeTypes()
    node_types = (
        "UxMap",
        "Screen",
        "Region",
        "Control",
        "StoryDemoControl",
        "Interaction",
        "Transition",
        "ContentType",
        "NavComponent",
        "UxContext",
    )

    @property
    def root(self) -> Path:
        """The folder the practice reads its UX maps from."""
        return Path(self.in_graph.source_root)

    def read_working_copy(self) -> None:
        """Read each UX map file under the root, or among the edited files, onto the graph, then link every screen and
        control the graph holds to what it serves, and every screen to its domain classes: a node kept from an earlier
        read links again too, since the stories it names may have been read again."""
        if not self.root.is_dir():
            return
        map_files = _UxMapFiles(self)
        files = list(map_files.found())
        unread: list[dict[str, str]] = []
        with schema_sync_paused():
            for index, file in enumerate(files, start=1):
                report_progress(f"ux · maps · {index}/{len(files)} · {file.relative}")
                try:
                    _RecordedMap(self, file).record()
                except map_files.not_a_map_failures as reason:
                    unread.append({"file": file.relative, "reason": str(reason)})
        if unread:
            self.in_graph.root.set_fact(UNREAD_FILES_FACT, unread)
        _ServedStoryLinks(self).link()
        _DomainTermLinks(self).link()
        _StoryDemoControlLinks(self).link()


class _UxMapFile:
    """One file a UX map is written in: where it is, its text, and the format that reads it."""

    def __init__(self, relative: str, text: str, format: UxMap) -> None:
        self.relative = relative
        self.text = text
        self.format = format
        self._lines = text.splitlines()
        # The line the node placed last is on: the file writes its nodes in the map's order, so the next is after it.
        self._placed = 0

    def parsed(self) -> UxMap:
        """The map the file holds, read by its format: detached, as every parsed map is."""
        return self.format.parse(self.text)

    @property
    def whole(self) -> Location:
        return Location(self.relative, 1, max(1, len(self._lines)))

    def place_of(self, name: str) -> Location:
        """The line that names a node called name: the first line that writes it as a node's own name, after the node
        placed before it when there is one there, since a file writes its nodes in the map's order; else the first line
        that mentions it; the whole file when no line does."""
        written = [html.escape(name), json.dumps(name)[1:-1]]
        declared = [mark.format(spelling) for spelling in written for mark in _NAME_MARKS]
        found = (
            self._line_holding(declared, self._placed) or self._line_holding(declared, 0)
            or self._line_holding([name, *written], 0)
        )
        if not name or not found:
            return self.whole
        self._placed = found
        return Location(self.relative, found, found)

    def _line_holding(self, spellings: list[str], after: int) -> int:
        """The number of the first line past line number after that holds one of spellings; 0 when none does."""
        return next(
            (number for number, line in enumerate(self._lines[after:], start=after + 1) if any(spelling in line for spelling in spellings)),
            0,
        )


class _UxMapFiles:
    """The files under a UX reading's root that hold a UX map: on a load of the whole folder, every file one of the
    practice's formats says is its own, in the folders a scan enters and in each folder's `.context`; on a load of
    edited files or a refresh, those among the files named."""

    def __init__(self, reading: UxReading) -> None:
        self._reading = reading
        self._formats = [
            adapter
            for adapter in (reading.practice.formats.adapter(name) for name in reading.practice.formats)
            if isinstance(adapter, UxMap) and adapter.map_file_suffixes
        ]

    @property
    def not_a_map_failures(self) -> tuple[type[Exception], ...]:
        """What reading a UX file that is not a map after all fails with: what each format says its own reading fails
        with for text that is not its format, and a link to a screen the map lacks."""
        return (*(failure for format in self._formats for failure in format.not_a_map_failures), ScreenNotOnMap)

    def found(self) -> Iterator[_UxMapFile]:
        root = self._reading.root.resolve()
        for path in self._candidates(root):
            format = self._format_of(path)
            if format is not None:
                yield _UxMapFile(path.relative_to(root).as_posix(), format[1], format[0])

    def _candidates(self, root: Path) -> list[Path]:
        """Each file under root with an ending some format reads, in a fixed order."""
        suffixes = {suffix for format in self._formats for suffix in format.map_file_suffixes}
        edited = self._reading.graph.scope.edited_files
        if edited is not None:
            named = (path.resolve() for path in edited)
            return sorted(path for path in named if path.suffix.lower() in suffixes and root in path.parents)
        found: list[Path] = []
        for folder, folders, names in os.walk(root):
            folders[:] = [name for name in folders if name == _CONTEXT_FOLDER or not skips_folder(name)]
            found.extend(Path(folder) / name for name in names if Path(name).suffix.lower() in suffixes)
        return sorted(found)

    def _format_of(self, path: Path) -> tuple[UxMap, str] | None:
        """The format that says path is its own, with the file's text, a byte that is not UTF-8 read as a replacement
        character, so a map saved in another code page is still read, or kept among the files that could not be; none
        for a file no format reads, or one gone since the scan listed it."""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        suffix = path.suffix.lower()
        reader = next((format for format in self._formats if suffix in format.map_file_suffixes and format.reads_file(path, text)), None)
        return None if reader is None else (reader, text)


class _RecordedMap:
    """One UX map file's map on the graph: every node of the map named for its file and its place in the map, placed
    at the line of the file that names it, with the edges between the nodes of the map."""

    def __init__(self, reading: UxReading, file: _UxMapFile) -> None:
        self._reading = reading
        self._file = file
        self._ids: set[str] = set()

    def record(self) -> None:
        ux_map = self._file.parsed()
        nodes = ux_map.subtree()
        paths = {id(ux_map): ""}
        for node in nodes[1:]:
            paths[id(node)] = ".".join(part for part in (paths.get(id(node.parent), ""), node.name) if part)
            node.node_id = self._unused_id(node, paths[id(node)])
        ux_map.node_id = self._unused_id(ux_map, ux_map.name)
        ux_map.context.node_id = self._unused_id(ux_map.context, ux_map.context.name)
        ux_map.join(self._reading.practice)
        if not self._file.format.holds_screens:
            ux_map.set_fact(EXEMPT_FACT, ["screens"])
        self._place(ux_map, nodes)
        graph = self._reading.graph
        graph.edges.link("owns", self._reading.in_graph.root, ux_map)
        for node in nodes:
            for kind, target in self._links_of(node):
                graph.edges.relate(kind, node, target)

    def _unused_id(self, node: UxNode, path: str) -> str:
        """The id of node in this file's map: its type, the file, and its place in the map, numbered when two nodes of
        one type share a place, such as two transitions with one trigger."""
        base = f"{self._reading.practice.key}:{node.type}:{self._file.relative}:{path}"
        node_id, number = base, 1
        while node_id in self._ids:
            number += 1
            node_id = f"{base} {number}"
        self._ids.add(node_id)
        return node_id

    def _place(self, ux_map: UxMap, nodes: list[UxNode]) -> None:
        """Put the map and its context on the whole file, and each other node on the line that names it."""
        ux_map.place(self._file.whole)
        ux_map.context.place(self._file.whole)
        for node in nodes[1:]:
            node.place(self._file.place_of(node.name))

    def _links_of(self, node: UxNode) -> list[tuple[str, UxNode]]:
        """The screens node refers to without holding them, each under the relationship the schema names for it."""
        if isinstance(node, Transition):
            return [(kind, screen) for kind, screen in (("from", node.from_screen), ("to", node.to_screen)) if screen is not None]
        if isinstance(node, Interaction):
            return [("destination", node.destination)] if node.destination is not None else []
        if isinstance(node, NavComponent):
            return [("destinations", screen) for screen in node.destinations]
        if isinstance(node, Screen):
            return [("chromeOf", node.chrome_of)] if node.chrome_of is not None else []
        return []


class _LinksAcrossPractices:
    """The edges one kind of UX node has to the nodes of the other practices its graph reads, made for one UX reading."""

    def __init__(self, reading: UxReading) -> None:
        self._reading = reading
        self._graph = reading.graph
        # The story map the graph reads beside UX, found once and handed to each link; none while it reads no Stories.
        self._story_tree = StoryTree.of_graph(reading.graph)


class _ServedStoryLinks(_LinksAcrossPractices):
    """The edges from UX's screens and controls to the stories, scenarios, and steps each serves, each of which is
    shown on that screen or control. An association written as a link is followed to the file its target names, the
    path taken from the folder of the UX file it is written in (and, for a file in a `.context`, the folder that `.context` belongs to), then from the folders the graph reads, and to the node
    read from the heading the target names; one written as a key alone leads to the node with that key. A graph that
    reads no Stories, or not the file a link names, gets no edge. They are read from the facts every screen and control
    saves with the graph, so a node kept from an earlier read, a plain node in a worker process, links the same way as
    one just parsed."""

    @cached_property
    def _written(self) -> WrittenStoryNodes | None:
        """Where each link's target leads on this graph, read once for every screen and control."""
        return self._story_tree.written_nodes() if self._story_tree is not None else None

    def link(self) -> None:
        for node_type in _SERVING_TYPES:
            for node in self._reading.in_graph.nodes(node_type):
                self._link_served(node)

    def _link_served(self, node: Node) -> None:
        folders = self._folders_written_from(node)
        for kind, edge, fact in _SHOWN:
            for written in node.get_fact(fact) or []:
                link = StoryLink.from_shown(kind, written)
                shown = link.found_in(self._written, self._story_tree, folders) if self._story_tree is not None else None
                if shown is not None:
                    self._graph.edges.relate(edge, node, shown)
                    self._graph.edges.relate("shownOn", shown, node)


    def _folders_written_from(self, node: Node) -> list[Path]:
        """The folders a link on node may be written from: the folder of node's file, and, for a file in a `.context`,
        the folder that `.context` belongs to, since a drawing or a board saved there keeps the links of the mockup
        beside it, which were written from that folder."""
        if node.source is None or not node.source.file:
            return []
        folder = (self._reading.root / node.source.file).parent
        return [folder, folder.parent] if folder.name == _CONTEXT_FOLDER else [folder]


class _DomainTermLinks(_LinksAcrossPractices):
    """The edges from UX's screens to the domain model: a screen's domain terms lead to the domain class each names.
    They are read from the facts every screen saves with the graph, as what it serves is."""

    def link(self) -> None:
        for screen in self._reading.in_graph.nodes("Screen"):
            for term in screen.get_fact("domain_terms") or []:
                named = self._class_named(term)
                if named is not None:
                    self._graph.edges.relate("domainTerms", screen, named)
                    self._graph.edges.relate("domainTerms", named, screen)

    def _class_named(self, term: str) -> Node | None:
        """The one class a domain term names: the DDD class of that name when the graph reads DDD and holds one, else
        the Clean Engineering class of that name. A name several classes share says which of them to nobody, so it
        leads to none."""
        for practice in self._domain_practices():
            reading = practice.reading
            kinds = [kind for kind in reading.class_types if kind not in _GROUP_TYPES]
            named = [node for kind in kinds for node in reading.in_graph.nodes(kind) if node.name == term]
            if named:
                return named[0] if len(named) == 1 else None
        return None

    def _domain_practices(self) -> list[PracticeGuidance]:
        """The practices open in the graph whose classes a domain term can name: DDD first, then Clean Engineering."""

        loaded = (self._graph.practices.loaded(kind) for kind in (Ddd, CleanEngineering))
        return [practice for practice in loaded if practice is not None]


class _StoryDemoControlLinks(_LinksAcrossPractices):
    """The edges from UX's Story Demo controls to the other practices: a control runs the story steps whose text it
    holds, and shows the property its bound field names. They are read from the facts every control saves with the
    graph, as a screen's links are."""

    def link(self) -> None:
        for control in self._reading.in_graph.nodes("StoryDemoControl"):
            for label in control.get_fact("story_step_labels") or []:
                for step in self._steps_reading(label, control):
                    self._graph.edges.relate("storySteps", control, step)
            bound = self._property_at(control.get_fact("bound_field") or "")
            if bound is not None:
                self._graph.edges.relate("boundField", control, bound)

    def _steps_reading(self, label: str, control: Node) -> list[Node]:
        """The steps whose text is label: those of the stories the control's screen shows, when it shows any that have
        one; else every such step when only one story has it."""

        if self._story_tree is None:
            return []
        steps = self._story_tree.steps_saying(label)
        shown = {StoryLink.from_shown("Story", written).key for written in self._screen_of(control).get_fact("story_keys") or []}
        on_screen = [step for step in steps if StoryTree.key_of(step).split(KEY_SEPARATOR)[0] in shown]
        return on_screen or (steps if len(steps) == 1 else [])

    def _screen_of(self, control: Node) -> Node:
        """The screen whose region holds control."""
        above = self._graph.edges.direct_parent(control)
        while above is not None and above.type != "Screen":
            above = self._graph.edges.direct_parent(above)
        return above if above is not None else control

    def _property_at(self, path: str) -> Node | None:
        """The property a bound field's path ends on: the Clean Engineering property called by the path's last part on
        the class called by the part before it, as ``book.title`` is ``title`` on ``Book``. A path of one part, or one
        no single property answers, leads to none."""

        clean = self._graph.practices.loaded(CleanEngineering)
        parts = [part for part in path.split(_PATH_SEPARATOR) if part]
        if clean is None or len(parts) < 2:
            return None
        owner, name = parts[-2].replace("_", "").casefold(), parts[-1]
        found = [
            member
            for member in clean.reading.in_graph.nodes("Property")
            if member.name == name and str(member.get_fact("owner") or "").replace("_", "").casefold() == owner
        ]
        return found[0] if len(found) == 1 else None
