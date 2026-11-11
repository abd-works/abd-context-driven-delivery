"""The board's tools as specs call them: a project with a sessions folder whose board tools run on a McpServer,
and the examples the board tools specs share."""
import json
import os
import tempfile
from pathlib import Path


from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.installation.data_class import data_of  # noqa: E402
from space.kanban.session_board_examples import saved_graph, saved_practice  # noqa: E402
from space.kanban.story_test import progress_in  # noqa: E402
from harness.mcp.mcp_server import McpServer  # noqa: E402

TOOLSETS = (
    "space.kanban.board:Board",
    "space.kanban.board:Stage",
    "space.kanban.ticket:Ticket",
    "space.kanban.ticket:FidelityProgress",
    "space.kanban.backlog_item:BacklogItem",
    "space.session.session:Session",
    "space.session.sessions:Sessions",
    "space.session.practice_session_output:PracticeSessionOutput",
)


def session_file_of(ticket: str) -> str:
    """The session.json of ticket, as a path from the project: how the session tools name a ticket's session."""
    return f".sessions/{ticket}/session.json"


def reports_of(ticket: dict) -> dict[str, str]:
    """Each fidelity's latest report on a ticket's JSON, by its slug, leaving out the fidelities with none."""
    return {progress["fidelity"]["slug"]: progress["report_file"] for progress in ticket["progress"] if progress["report_file"]}


def violation_counts_of(ticket: dict) -> dict[str, int]:
    """How many violations each fidelity's latest report names on a ticket's JSON, leaving out the ones with none."""
    return {progress["fidelity"]["slug"]: progress["violation_count"] for progress in ticket["progress"] if progress["violation_count"]}


def next_action_of(ticket: dict) -> str:
    """The action Run next sends on a ticket's JSON: its next fidelity's next action, none when it has no next fidelity."""
    return progress_in(ticket, ticket["next"]["fidelity"]["slug"])["next_action"] if ticket["next"] else ""
STAGE_COLUMNS = {"Discovery": 1, "Specification": 2, "Implementation": 3}

DISCOVERY_DONE = [
    line
    for practice, practice_class, fidelity in (
        ("stories", "Stories", "story_map"), ("ddd", "Ddd", "bounded_context"), ("ux", "Ux", "ia"),
        ("clean_engineering", "CleanEngineering", "modules"), ("bdd", "Bdd", "behavior"),
    )
    for line in (
        f"2026-10-31T01:00:00Z generate /work {practice} {fidelity} markdown {practice} no-chat",
        f"2026-10-31T01:00:01Z validate {practice_class} {fidelity} no-chat",
    )
]
CHECKED_GRAPH = saved_graph(
    saved_practice("clean_engineering", "node-1", "docs/map.md", 12, ("domain-nouns-only", "Name the story with a verb"), ("domain-nouns-only", "Name the epic with a verb")),
    saved_practice("stories", "node-2", "docs/other.md", 3, ("actor-named-in-step", "Name the actor")),
)
STORY_MAP_GRAPH = saved_graph(saved_practice("stories", "node-1", "docs/map.md", 12, ("verb-noun-format", "Name the story with a verb"), ("verb-noun-format", "Name the epic with a verb")))
# A report as validate saves it, with the judgment the validating agent added: a rule the graph already hit, a failed rule
# with two findings in the map and one in its drawio, and a rule with one finding followed by a list of passing rules.
JUDGED_REPORT = """# Graph rule validation

## Judgment — `docs/map.md`

| Rule | Verdict |
|---|---|
| verb-noun-format | **Fail** (graph rule) |

### `verb-noun-format` — Fail
Graph rule: the story at line 12 opens with a noun.

### `do-not-invent-requirements` — Fail
- map.md:7 `Open Board`: no source names the board command.
- map.md:9 `Close Board`: invented.

### `story-name-captures-system-mechanic` — Fail
- map.md:3 `Do Stuff` does not say what it does.

**Passes:**
- verb-noun-format: every name is a verb and a noun.

## Judgment — `docs/map.drawio`

### `do-not-invent-requirements` — Fail
- map.drawio:2 `Open Board`: no source names the board command.

### Passes
Everything else.
"""

# One hit each on a story map rule and a scenarios rule.
WHOLE_STORIES_GRAPH = saved_graph(saved_practice("stories", "node-1", "docs/map.md", 12, ("verb-noun-format", "Name the story with a verb"), ("plain-english-gwt-steps", "Write the step in plain English")))


class ProjectTools:
    """A project with a sessions folder, and the board's tools called through the MCP server."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="kanban-tools-"))
        self.sessions = self.root / ".sessions"
        self.sessions.mkdir()
        (self.root / ".git").mkdir()
        os.environ["CDD_PROJECT"] = str(self.root)
        self.server = McpServer(project=self.root)
        self.server.start(TOOLSETS)

    def ticket(self, name: str, *log_lines: str, **fields) -> Path:
        folder = self.sessions / name
        folder.mkdir()
        (folder / "session.json").write_text(json.dumps({"name": name, **fields}), encoding="utf-8")
        (folder / "session.log").write_text("".join(f"{line}\n" for line in log_lines), encoding="utf-8")
        return folder

    def report(self, ticket: str, name: str, graph: dict | None = None) -> None:
        reports = self.sessions / ticket / "validation-reports"
        reports.mkdir(exist_ok=True)
        (reports / f"{name}.md").write_text("# Graph rule validation\n", encoding="utf-8")
        if graph:
            (reports / f"{name}.json").write_text(json.dumps(graph), encoding="utf-8")

    def backlog_item(self, file_name: str, heading: str) -> None:
        folder = self.sessions / "_backlog"
        folder.mkdir(exist_ok=True)
        (folder / file_name).write_text(f"# {heading}\n\nAn idea.\n", encoding="utf-8")

    def call(self, tool: str, **arguments):
        result = self.server.invoke_tool(tool, arguments)
        return json.loads(json.dumps(result, default=data_of))

    def column(self, name: str) -> dict:
        return next(column for column in self.call("board.show")["columns"] if column["name"] == name)

    def tickets_in(self, name: str) -> list:
        column = self.column(name)
        return [ticket["name"] for key in ("in_progress", "done", "tickets") for ticket in column.get(key, [])]

    def ticket_json(self, name: str) -> dict:
        columns = self.call("board.show")["columns"]
        return next(ticket for column in columns for key in ("in_progress", "done", "tickets")
                    for ticket in column.get(key, []) if ticket["name"] == name)


