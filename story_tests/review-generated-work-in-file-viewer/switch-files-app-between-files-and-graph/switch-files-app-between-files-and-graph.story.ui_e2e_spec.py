"""Switch Files App Between Files And Graph in a real browser: the scenarios only the page and Monaco show, on the Files
app served for real (files_app_browser.FilesStack).

Scenarios: switch_files_app_between_files_and_graph_story.test.md. The Python tiers replay the rest from
switch-files-app-between-files-and-graph.story.shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import SHOWN_MILLISECONDS, FilesStack, graph_view, line, open_branches, select, settled, shown_lines
from space.session.graph_view_examples import CHECKOUT_FLOW

FIDELITIES = "stories-acceptance-tests,clean-engineering-code"
GIVEN_STEP_LINES = ['    @s.given("a ticket on the board")', "    def _(world):", "        world.ticket = ticket_on_board(world)"]


with description("Story: Fold Open Files To Selected Nodes") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Selecting a step in a Python story test unfolds its function"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "stories", "Manage Tickets", "Remove Tickets", "Delete Ticket", "Delete Ticket", "a ticket on the board is deleted")
            select(self.page, "Given given a ticket on the board")
            line(self.page, "world.ticket = ticket_on_board(world)").wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the function under the step's decorator is unfolded, showing its body"):
            expect([shown for shown in shown_lines(self.page) if shown.strip() in {text.strip() for text in GIVEN_STEP_LINES}][:3]).to(equal(GIVEN_STEP_LINES))

        with it("And the scenario's other step functions stay folded"):
            others = lambda: [shown for shown in shown_lines(self.page) if "world.ticket.delete(world.board)" in shown or "assert ticket_left(world)" in shown]
            expect(settled(others, lambda shown: shown == [])).to(equal([]))
