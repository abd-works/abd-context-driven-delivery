"""Explore Graph In Files App in a real browser: the scenarios only the page and Monaco show, on the Files app served
for real (files_app_browser.FilesStack).

Scenarios: explore_graph_in_files_app_story.test.md. The Python tiers replay the rest from
explore-graph-in-files-app.story.shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_above, be_none, contain, equal, expect
from mamba import after, before, context, description, it

from files_app_browser import (
    CLOSE_LINES,
    GRAPH_READ_MILLISECONDS,
    SHOWN_MILLISECONDS,
    TICKET_CODE,
    FilesStack,
    callout_heights,
    callout_texts,
    graph_view,
    line,
    mark_on,
    marked_lines,
    open_branches,
    open_callout_on,
    open_files,
    select,
    settled,
)
from space.kanban.graph_view_examples import BOARD_CODE, CHECKOUT_FLOW

# Interaction: the lines of Board.reread, from board.py, as they open in place under the call that names them.
REREAD_LINES = "    def reread(self) -> None:"


def node_titles(page, kind: str) -> list[str]:
    return sorted(page.locator(f'button.graph-node[title^="{kind} "]').evaluate_all("nodes => nodes.map(node => node.title)"))


def filter_to_operations(page) -> None:
    """Filters the graph to operations and waits until the trees are read again for it, when the practice roots show
    without the classes the filter leaves out."""
    page.locator(".graph-filters-toggle").click()
    page.select_option('[data-testid="filter-node"]', ["Operation"])
    page.locator("ul.graph-tree").wait_for(timeout=GRAPH_READ_MILLISECONDS)
    page.wait_for_function("() => !document.querySelector('[data-testid=load-meter]')", timeout=GRAPH_READ_MILLISECONDS)


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

    with context("Scenario: A call to an operation in another file opens in place"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket")
            select(self.page, "Operation delete")
            line(self.page, "Board.reread(board)").wait_for(timeout=SHOWN_MILLISECONDS)
            self.page.locator(".callout-mark").first.wait_for(timeout=SHOWN_MILLISECONDS)
            open_callout_on(self.page, "Board.reread(board)")

        with after.all:
            self.page.close()

        with it("Then the lines of Board.reread, from board.py, show in place below the call"):
            expect([text.splitlines()[0] for text in callout_texts(self.page)]).to(equal([REREAD_LINES]))


with description("Story: Follow Relationships Under Node In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Selecting a related node opens the related node alone, in its own file"):
        with context("Given Ticket.delete is selected and ticket.py is open"):
            with before.all:
                self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
                graph_view(self.page)
                open_branches(self.page, "clean_engineering", "kanban", "Ticket", "delete", "invokes")
                select(self.page, "Operation delete")
                self.page.locator(f'section.open-file[aria-label="{TICKET_CODE}"]').wait_for(timeout=SHOWN_MILLISECONDS)

            with after.all:
                self.page.close()

            with context("When the Person selects Board.reread under Ticket.delete's invokes"):
                with before.all:
                    self.page.locator('li.graph-entry[data-kind="invokes"] button.graph-node[title="Operation reread"]').first.click()
                    self.page.locator(f'section.open-file[aria-label="{BOARD_CODE}"]').wait_for(timeout=SHOWN_MILLISECONDS)
                    line(self.page, REREAD_LINES.strip()).wait_for(timeout=SHOWN_MILLISECONDS)

                with it("Then board.py opens at Board.reread"):
                    expect(marked_lines(self.page, BOARD_CODE)).to(equal(["    def reread(self) -> None:", "        return None"]))

                with it("But ticket.py, which holds Ticket.delete, is no longer open"):
                    expect(open_files(self.page)).to(equal([BOARD_CODE]))


with description("Story: Filter Graph By Node Type And Connector In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Choosing a node type keeps only those nodes"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            filter_to_operations(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket", "Board")

        with after.all:
            self.page.close()

        with it("Then the Clean Engineering tree holds Ticket.close, Ticket.delete and Board.reread, and no other member"):
            expected = ["Operation close", "Operation delete", "Operation reread"]
            expect(settled(lambda: node_titles(self.page, "Operation"), lambda shown: shown == expected)).to(equal(expected))

    with context("Scenario: Changing the file list keeps the node filter"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            self.page.get_by_role("button", name="Graph", exact=True).click()
            self.page.locator("ul.graph-tree").wait_for(timeout=GRAPH_READ_MILLISECONDS)
            filter_to_operations(self.page)
            self.page.get_by_role("button", name="All session files").click()
            self.page.locator("ul.graph-tree").wait_for(timeout=GRAPH_READ_MILLISECONDS)
            open_branches(self.page, "clean_engineering", "kanban", "Board")

        with after.all:
            self.page.close()

        with it("Then Board.reread joins the Clean Engineering tree"):
            expect(settled(lambda: node_titles(self.page, "Operation"), lambda shown: shown == ["Operation reread"])).to(equal(["Operation reread"]))

        with it("And the graph stays filtered to operations"):
            expect(self.page.locator('[data-testid="filter-node"]').evaluate("select => [...select.selectedOptions].map(option => option.value)")).to(equal(["Operation"]))


with description("Story: Show Graph Load Steps In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: A failed load shows the server's reason, ready to copy for the chat"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            self.page.get_by_role("button", name="All session files").click()
            self.page.locator(".file-list, .file-tree").first.wait_for(timeout=SHOWN_MILLISECONDS)
            self.stack.cdd.stop()
            self.page.get_by_role("button", name="Graph", exact=True).click()
            self.page.locator(".files-note, .scan-error").first.wait_for(timeout=GRAPH_READ_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the graph view shows the server's reason instead of loading forever"):
            expect(self.page.locator(".files-note, .scan-error").first.inner_text()).to(contain("did not read"))

        with it("And offers a copy of it for the chat"):
            expect(self.page.get_by_role("button", name="Copy for AI").count()).to(equal(1))


with description("Story: Open Calls Across Files In Files App, opened on another project") as self:
    with before.all:
        self.stack = FilesStack.on_another_project()

    with after.all:
        self.stack.close()

    with context("Scenario: A method's call to another method of its class opens in place, Example: another project"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket")
            select(self.page, "Operation delete")
            line(self.page, "self.close()").wait_for(timeout=SHOWN_MILLISECONDS)
            self.page.locator(".callout-mark").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the call self.close() opens that project's Ticket.close in place below it, not the CDD checkout's"):
            open_callout_on(self.page, "self.close()")
            expect(callout_texts(self.page)).to(equal([CLOSE_LINES]))
