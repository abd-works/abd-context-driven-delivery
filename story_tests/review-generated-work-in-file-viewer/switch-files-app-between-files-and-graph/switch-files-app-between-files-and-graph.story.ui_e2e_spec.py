"""Switch Files App Between Files And Graph in a real browser: the scenarios only the page and Monaco show, on the Files
app served for real (files_app_browser.FilesStack).

Scenarios: switch_files_app_between_files_and_graph_story.test.md. The Python tiers replay the rest from
switch-files-app-between-files-and-graph.story.shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import SHOWN_MILLISECONDS, TICKET_CODE, FilesStack, graph_view, line, open_branches, select, settled, shown_lines
from space.session.graph_view_examples import CHECKOUT_FLOW

FIDELITIES = "stories-acceptance-tests,clean-engineering-code"
GIVEN_STEP_LINES = ['    @s.given("a ticket on the board")', "    def _(world):", "        world.ticket = ticket_on_board(world)"]
# Interaction: the practice trees the graph view draws for checkout-flow's Stories and Clean Engineering files.
PRACTICE_TREES = ["Practice clean_engineering", "Practice stories"]
DELETE_LINES = ["        self.close()", "        reread_all(board)", "        Board.reread(board)"]


with description("Switch Files App Between Files And Graph, in a real browser") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Given the Files app lists checkout-flow's Stories and Clean Engineering files"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)

        with after.all:
            self.page.close()

        with context("Story: Switch Files App To Graph View"):
            with context("Scenario: The graph view shows the practice trees of the listed files"):
                with before.all:
                    graph_view(self.page)

                with it("Then the file bar shows the Stories and Clean Engineering practice trees"):
                    expect(sorted(self.page.locator('button.graph-node[title^="Practice "]').evaluate_all("nodes => nodes.map(node => node.title)"))).to(equal(PRACTICE_TREES))

        with context("Story: Open Several Files From Graph Nodes"):
            with context("Scenario: Selecting a node opens its file"):
                with before.all:
                    open_branches(self.page, "clean_engineering", "kanban", "Ticket")
                    select(self.page, "Operation delete")
                    line(self.page, "self.close()").wait_for(timeout=SHOWN_MILLISECONDS)

                with it("Then ticket.py opens beside the file bar"):
                    expect(self.page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")).to(equal([TICKET_CODE]))

        with context("Story: Fold Open Files To Selected Nodes"):
            with context("Scenario: An open file unfolds only the selected node"):
                with it("Then the lines of Ticket.delete are unfolded"):
                    expect([shown for shown in shown_lines(self.page) if shown in DELETE_LINES]).to(equal(DELETE_LINES))

                with it("And Ticket.close is folded to its first line"):
                    hidden = lambda: [shown for shown in shown_lines(self.page) if shown == "        return None"]
                    expect(settled(hidden, lambda shown: len(shown) == 1)).to(equal(["        return None"]))

    with context("Story: Fold Open Files To Selected Nodes, Scenario: Selecting a step in a Python story test unfolds its function"):
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
