"""CanvasComment. A comment a person left on a published design canvas, answered through the knowledge graph: the row of
the canvas's story explorer the comment is anchored to names a story, scenario, step or outline example on the graph;
the graph says which file holds it and which screens and interactions show it."""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from cdd_guidance.practices.stories.model.markdown.markup import plain_words
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles
from cdd_guidance.practices.stories.model.story_tree import EPIC_TYPES, EXAMPLE_TYPE, STEP_TYPES, StoryTree
from cdd_guidance.practices.ux.model.shown_places import ShownPlaces
from harness.design_canvas.versions import DESIGN_CANVAS_FOLDER, CanvasVersion, CanvasVersions

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node

# The record each design canvas keeps of the links its versions were published at.
VERSIONS_FILE = "versions.json"
# The fidelity of Stories that writes each kind of node: the story map writes epics and stories, scenarios the rest.
STORY_MAP = "story_map"
SCENARIOS = "scenarios"
_HEADING = re.compile(r"^#+\s*(?:Story|Scenario(?: Outline)?|Background)\s*:\s*(.+?)\s*$", re.IGNORECASE)
_STORY_FILE_ENDINGS = ("_story.test.md", "_story.spec.md")
# A placeholder an outline's step or scenario names: ``{lines}`` in markdown, ``${row.example}`` in a story test.
_PLACEHOLDER = re.compile(r"\$?\{[^}]+\}|<[^>\s]+>")


class CanvasCommentNeedsAnchor(ValueError):
    """A comment came from a design canvas with no anchor: without the row of the story explorer it sits on, nothing says
    which story, scenario or step it is about."""

    def __init__(self, board: str) -> None:
        super().__init__(
            f"{board} is a design canvas: pass anchor, the label of the story explorer row the comment sits on and its "
            "location, so the graph can find the story, scenario or step it names")
        self.board = board


class AnchorNamesNoStory(LookupError):
    """The anchor of a comment on a design canvas names no story, scenario, step or example the knowledge graph holds."""

    def __init__(self, board: str, anchor: str) -> None:
        super().__init__(
            f"The anchor {anchor!r} of the comment on {board} names no story, scenario, step or example on the knowledge "
            "graph: refresh the graph with the story files, or answer the comment as an ordinary request")
        self.board = board
        self.anchor = anchor


def canvas_published_at(work_root: Path, folders: List[Path], board: str) -> Optional[CanvasVersion]:
    """The version of a design canvas under work_root published at board: a canvas kept in one of folders, the UX
    practice's roots, else any ``design-canvas`` folder under work_root."""
    kept = [folder / DESIGN_CANVAS_FOLDER for folder in folders]
    found = [path.parent for path in work_root.glob(f"**/{DESIGN_CANVAS_FOLDER}/{VERSIONS_FILE}") if "node_modules" not in path.parts]
    for canvas in dict.fromkeys([*kept, *found]):
        if (canvas / VERSIONS_FILE).is_file():
            version = CanvasVersions(canvas).published_at(board)
            if version is not None:
                return version
    return None


class CanvasComment:
    """A comment anchored to a row of a published canvas version's story explorer, read against the graph: the Stories
    nodes the anchor names (*StoryTree.nodes_labelled*), the file of each to change, with the story test that holds it in
    code, and the places on the UX map that show it (*ShownPlaces*)."""

    def __init__(self, version: CanvasVersion, anchor: str, graph: "Graph", stories_root: Path, work_root: Path) -> None:
        self.version = version
        self.anchor = anchor
        self._graph = graph
        self._stories_root = stories_root
        self._work_root = work_root.resolve()
        self._tree = StoryTree.of_graph(graph)

    @cached_property
    def named(self) -> List["Node"]:
        """The Stories nodes the anchor names; refused when it names none."""
        named = self._tree.nodes_labelled(self.anchor) if self._tree is not None else []
        if not named:
            raise AnchorNamesNoStory(self.version.link or self.version.title, self.anchor)
        return named

    @property
    def fidelity(self) -> str:
        """The fidelity of Stories that writes what the anchor names: the story map for epics and stories, scenarios for
        a scenario, a step or an example."""
        return STORY_MAP if all(node.type in ("Story", *EPIC_TYPES) for node in self.named) else SCENARIOS

    @property
    def answer(self) -> str:
        """What the anchor names, each with the file to change and where it is shown, then which of them to change."""
        folder = self._from_root(self.version.folder)
        lines = [f"The comment is on {self.version.title}, the design canvas in {folder}, drawn from the story map, its "
                 f"scenarios and the UX map, so change the file the graph says holds what the comment names, never the canvas alone."]
        lines.extend(f"- {self._described(node)}" for node in self.named)
        if len(self.named) > 1:
            lines.append(f"The anchor names {len(self.named)} nodes; the comment's row is one of them: read the comment to tell "
                         "which, and ask the person when it does not say.")
        return "\n".join(lines)

    def _described(self, node: "Node") -> str:
        """node, where it sits on the story map, the file to change at the line that holds it, the story test that holds it
        in code, and each place that shows it."""
        parts = [f"{self._kind_of(node)} {self._label_of(node)!r}{self._under(node)}"]
        written = self._written_in(node)
        parts.append(f"change {written}" if written else "no markdown story file holds it")
        code = self._code_file(node)
        if code and code != written.split("#", 1)[0]:
            parts.append(f"the story test {code}#L{node.source.start_line} holds it in code: keep it in step")
        places = ShownPlaces(self._graph).of(node)
        if places:
            through = places[0].through
            reached = "" if through is node else f", through its {through.type.lower()} {through.name!r}"
            parts.append("shown on " + " and ".join(place.described for place in places) + reached)
        else:
            parts.append("no screen of the UX map shows it")
        return "; ".join(parts) + "."

    def _kind_of(self, node: "Node") -> str:
        if node.type in STEP_TYPES:
            return "Step"
        if node.type == EXAMPLE_TYPE:
            return "Outline example"
        return "Sub-epic" if node.type == "SubEpic" else node.type

    def _label_of(self, node: "Node") -> str:
        if node.type in STEP_TYPES:
            keyword = str(node.get_fact("keyword") or node.type)
            return f"{keyword} {plain_words(self._tree.step_text(node))}"
        return node.name

    def _under(self, node: "Node") -> str:
        scenario = self._tree.scenario_of(node) if node.type != EXAMPLE_TYPE else self._graph.edges.direct_parent(node)
        story = self._tree.story_of(node)
        parts = []
        if scenario is not None and scenario is not node and scenario.type in ("Scenario", "Background"):
            parts.append(f"scenario {scenario.name!r}")
        if story is not None and story is not node:
            parts.append(f"story {story.name!r}")
        return f" of {' in '.join(parts)}" if parts else ""

    def _written_in(self, node: "Node") -> str:
        """The markdown file that writes node, from the work root, with the line it is written on: its story's own
        scenarios file, or the story map for an epic and for a story with no file of its own."""
        story = node if node.type == "Story" else self._tree.story_of(node)
        files = StoryMapFiles(self._stories_root)
        file = self._story_file(files, story.name) if story is not None else None
        if file is None:
            maps = files.markdown_below()
            file = maps[0] if maps else None
        if file is None:
            return ""
        line = _line_holding(file, node, self._tree)
        return f"{self._from_root(file)}#L{line}" if line else self._from_root(file)

    @staticmethod
    def _story_file(files: StoryMapFiles, story: str) -> Optional[Path]:
        wanted = _letters(story)
        for path in files.story_files_below():
            stem = next((path.name[: -len(ending)] for ending in _STORY_FILE_ENDINGS if path.name.endswith(ending)), path.stem)
            if _letters(stem) == wanted:
                return path
        return None

    def _code_file(self, node: "Node") -> str:
        """The file the graph read node from, from the work root, when it is not markdown: the story test in code."""
        if node.source is None or not node.source.file or node.source.file.endswith(".md"):
            return ""
        source_root = Path(self._tree.stories.in_graph.source_root)
        return self._from_root(source_root / node.source.file)

    def _from_root(self, path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(self._work_root).as_posix()
        except ValueError:
            return resolved.as_posix()


def _letters(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _line_holding(file: Path, node: "Node", tree: StoryTree) -> int:
    """The line of file that writes node: the heading of its story, scenario or background, the step's line under its
    scenario's heading, the example's row under it; 0 when none does."""
    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    if node.type in ("Story", "Scenario", "Background", *EPIC_TYPES):
        return _heading_line(lines, node.name)
    scenario = tree.scenario_of(node) if node.type != EXAMPLE_TYPE else tree.stories.graph.edges.direct_parent(node)
    start = _heading_line(lines, scenario.name) if scenario is not None else 0
    words = _fixed_words(tree.step_text(node)) if node.type in STEP_TYPES else node.name
    for number in range(max(start, 1), len(lines) + 1):
        if number > start and start and _HEADING.match(lines[number - 1]):
            break
        if words and words in plain_words(lines[number - 1]):
            return number
    return start


def _heading_line(lines: List[str], name: str) -> int:
    """The line of the heading that names name; a name a story test fills with an outline's row, such as
    ``Pay later: ${row.example}``, is matched by the words before its placeholder, as the markdown outline is headed."""
    wanted = _fixed_words(name)
    for number, line in enumerate(lines, start=1):
        found = _HEADING.match(line)
        if found and _fixed_words(found.group(1)) == wanted:
            return number
    return 0


def _fixed_words(text: str) -> str:
    """text's plain words before the first placeholder an outline fills, without the punctuation that leads to it."""
    return _PLACEHOLDER.split(plain_words(text))[0].strip().rstrip(":·-").strip()
