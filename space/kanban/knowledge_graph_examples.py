"""The named examples of the knowledge graph scenarios of Integrate Practice Content Editor Apps, one fixture per example.

**Seed** examples are state the repository owns: each ticket's session folder, whose `session.json` names the folder of
each practice it works on (its practice roots) and turns the others off, the session open in the project, and a story
map in each Stories root for the graph to read. The repository is the storage boundary, so `SessionsProject` writes
them where the session and the board read them.

**Interaction** examples are what the Graph app shows: the practice trees it loads, each read from its practice root.

Scenarios: harness/.context/stories/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/
and the Graph app's scenarios of .../move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness.graph.graph import Graph
from space.kanban.session_board_examples import SessionSeed, SessionsProject

STORIES, DDD, UX, CLEAN_ENGINEERING, BDD = "stories", "ddd", "ux", "clean_engineering", "bdd"
EVERY_PRACTICE = (STORIES, DDD, UX, CLEAN_ENGINEERING, BDD)
STORY_MAP = "story-map.md"


@dataclass(frozen=True)
class TicketScope:
    """Seed: a ticket's session as the tickets table has it, with the folder it names for each practice it works on;
    every other practice is turned off for it."""

    name: str
    title: str
    roots: dict[str, str]
    story_map: str

    @property
    def seed(self) -> SessionSeed:
        outputs = {practice: {"root": root} for practice, root in self.roots.items()}
        turned_off = {practice: {"enabled": False} for practice in EVERY_PRACTICE if practice not in self.roots}
        return SessionSeed(self.name, self.title, fields={"outputs": outputs, "practices": turned_off})

    @property
    def practices(self) -> list[str]:
        """Interaction: the practice trees the graph shows for this ticket, in the order the approach walks them."""
        return [practice for practice in EVERY_PRACTICE if practice in self.roots]

    def seed_into(self, project: SessionsProject) -> None:
        """Seed: its session folder, the folder of each of its practice roots, and a story map in its Stories root."""
        project.seed_session(self.seed)
        project.seed_folders(*self.roots.values())
        project.seed_file(f"{self.roots[STORIES]}/{STORY_MAP}", self.story_map)


# The tickets table: checkout-flow works on Stories, UX and Clean Engineering, billing-report on Stories and DDD.
CHECKOUT_FLOW = TicketScope(
    "checkout-flow",
    "Checkout Flow",
    {STORIES: "harness/.context/stories", UX: "harness/.context/ux", CLEAN_ENGINEERING: "harness/.context"},
    "# Move Work Forward From Chat Bar\n\n## Integrate Practice Content Editor Apps In Chat Bar\n\n- Open Story UI Side Panel From Chat Bar\n- Open Kanban Side Panel From Chat Bar\n",
)
BILLING_REPORT = TicketScope(
    "billing-report",
    "Billing Report",
    {STORIES: "billing/.context/stories", DDD: "billing/.context"},
    "# Report Billing\n\n## Monthly Billing\n\n- Report Billing By Month\n",
)


def roots_loaded(graph: Graph, project: Path) -> dict[str, str]:
    """Interaction: each practice tree the graph loaded, by practice, with the folder it was read from, from the project."""
    return {key: root.relative_to(project).as_posix() for key, root in graph.practices.roots_by_key.items()}


def files_read(graph: Graph, project: Path) -> list[str]:
    """Interaction: every file a node the graph shows was read from, from the project."""
    sources = (node.source for practice in graph.practices.opened.values() for node in practice.reading.in_graph.nodes())
    files = (Path(source.root, source.file).resolve() for source in sources if source.file and source.root)
    return sorted({file.relative_to(project.resolve()).as_posix() for file in files if file.is_file()})
