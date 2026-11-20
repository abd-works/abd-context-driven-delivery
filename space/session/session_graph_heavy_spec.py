"""Specs for the session's graph operations as the cdd server answers them for a chat's page, where the graph is built
in a worker process: what session.graph_trees answers the Files app's graph view for a session whose practices are all
turned off. The same operations in process are in session_graph_spec.py."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from space.session import Sessions
from space.session.throwaway_project import ExampleHome

PRACTICE_CATALOGUE.create_all()

# Seed: one code file the session's root holds, as the Files app lists it from the project.
TICKET_FILE = "work/kanban/ticket.py"
TICKET_TEXT = "class Ticket:\n    def activate(self) -> None:\n        return None\n"
# A call the cdd server answers for a chat, which builds the graph in a worker process.
FROM_A_CHAT = ToolCall(request=ToolRequest(answers_a_chat=True))


def _session_with_every_practice_off():
    """A session working in work/, whose kanban folder holds the ticket code, with every practice turned off."""
    repo = Path(tempfile.mkdtemp())
    (repo / ".git").mkdir()
    (repo / "work" / "kanban").mkdir(parents=True)
    (repo / TICKET_FILE).write_text(TICKET_TEXT, encoding="utf-8")
    Sessions(repo).switch("checkout-flow", repo / "work")
    session = Sessions(repo).current()
    for practice in session.own_practices.values():
        practice.enable(False)
    return session


with description("a session's graph, read for a chat's page"):
    with before.each:
        self.home = ExampleHome()

    with after.each:
        self.home.close()

    with context("with every practice of the session turned off"):
        with before.each:
            self.session = _session_with_every_practice_off()

        with it("should answer no tree for the files listed, since no practice reads them"):
            expect(self.session.graph_trees([TICKET_FILE], call=FROM_A_CHAT)).to(equal([]))
