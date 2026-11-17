"""Explore Graph In Files App in a real browser: the scenarios only the page and Monaco show, on the Files app served
for real (files_app_browser.FilesStack).

Scenarios: explore_graph_in_files_app_story.test.md. The Python tiers replay the rest from
explore-graph-in-files-app.story.shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_above, be_none, equal, expect
from mamba import after, before, context, description, it

from files_app_browser import (
    CLOSE_LINES,
    SHOWN_MILLISECONDS,
    TICKET_CODE,
    FilesStack,
    callout_heights,
    callout_texts,
    graph_view,
    line,
    mark_on,
    open_branches,
    open_callout_on,
    select,
    settled,
)
from space.session.graph_view_examples import CHECKOUT_FLOW

FIDELITIES = "stories-acceptance-tests,clean-engineering-code"


with description("Story: Open Calls Across Files In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Given the Files app shows ticket.py at Ticket.delete, opened from the graph, and the graph is read"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket")
            select(self.page, "Operation delete")
            line(self.page, "self.close()").wait_for(timeout=SHOWN_MILLISECONDS)
            self.page.locator(".callout-mark").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with context("Scenario: A class never opens itself in place"):
            with it("Then no line inside Ticket opens Ticket in place"):
                expect(mark_on(self.page, "class Ticket:")).to(be_none)

        with context("Scenario: A method's call to another method of its class opens in place"):
            with it("Then the call self.close() opens Ticket.close in place below it"):
                open_callout_on(self.page, "self.close()")
                expect(callout_texts(self.page)).to(equal([CLOSE_LINES]))

            with it("And the call reread_all(board) opens the function reread_all in place below it"):
                open_callout_on(self.page, "reread_all(board)")
                expect([text for text in callout_texts(self.page) if text.startswith("def reread_all")]).to(equal(["def reread_all(board) -> None:\n    board.reread()"]))

    with context("Scenario: A call inside a folded method opens in place once the method is unfolded"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            self.page.get_by_role("button", name="List", exact=True).click()
            self.page.locator(f'button.file-entry[title="{TICKET_CODE}"]').click()
            self.page.locator(".callout-mark").first.wait_for(timeout=SHOWN_MILLISECONDS)
            line(self.page, "def delete(self, board: Board) -> None:").click()
            self.page.keyboard.press("Control+Shift+BracketRight")
            line(self.page, "self.close()").wait_for(timeout=SHOWN_MILLISECONDS)
            open_callout_on(self.page, "self.close()")

        with after.all:
            self.page.close()

        with it("Then the lines of Ticket.close show in place below the call, at their full height"):
            heights = settled(lambda: callout_heights(self.page), lambda shown: bool(shown) and min(shown) > 0)
            expect(min(heights or [0.0])).to(be_above(0))
