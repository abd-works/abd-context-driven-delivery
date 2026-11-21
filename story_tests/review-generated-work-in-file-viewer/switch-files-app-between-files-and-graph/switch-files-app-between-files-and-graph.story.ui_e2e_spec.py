"""Switch Files App Between Files And Graph in a real browser: the scenarios only the page and Monaco show, on the Files
app served for real (files_app_browser.FilesStack).

Scenarios: switch_files_app_between_files_and_graph_story.test.md. The Python tiers replay the rest from
switch-files-app-between-files-and-graph.story.shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import GRAPH_READ_MILLISECONDS, SHOWN_MILLISECONDS, TICKET_CODE, FilesStack, all_session_files, graph_view, line, lines_in_order, mark_on, open_branches, select, settled, shown_lines
from space.session.graph_view_examples import BOARD_CODE, CHECKOUT_FLOW, EXAMPLES_SCENARIOS, EXAMPLES_SCENARIOS_TEXT, SCENARIOS, SCENARIOS_TEXT, STEP_STORY, STORY_MAP, STORY_MAP_WITH_REOPEN_TEXT

FIDELITIES = "stories-acceptance-tests,clean-engineering-code"
GIVEN_STEP_LINES = ['    @s.given("a ticket on the board")', "    def _(world):", "        world.ticket = ticket_on_board(world)"]
# Interaction: the practice trees the graph view draws for checkout-flow's Stories and Clean Engineering files.
PRACTICE_TREES = ["Practice clean_engineering", "Practice stories"]
DELETE_LINES = ["        self.close()", "        reread_all(board)", "        Board.reread(board)"]
# Interaction: the first line of the project's ticket.py; the CDD checkout's own space/kanban/ticket.py opens with its
# docstring.
TICKET_FIRST_LINE = "class Ticket:"
# Interaction: the operations of the project's class Ticket, as its graph holds them.
TICKET_OPERATIONS = ["Operation close", "Operation delete"]
# Interaction: the first lines of Ticket.close and Ticket.delete, which show while their bodies are folded.
TICKET_FIRST_LINES = ["    def close(self) -> None:", "    def delete(self, board: Board) -> None:"]
# Interaction: the editor lines of Ticket.delete in ticket.py, 5 to 9, which a selected node's orange line runs beside.
DELETE_LINE_COUNT = 5


def open_files(page) -> list[str]:
    return page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")


def heads_expanded(page) -> list[str]:
    return page.locator(".open-file-head").evaluate_all("heads => heads.map(head => head.getAttribute('aria-expanded'))")


# Interaction: the fidelities the page lists for Filter Callouts Like The Graph: the story map, the scenarios and the code.
STORIES_AND_CODE_FIDELITIES = "stories-story-map,stories-scenarios,stories-acceptance-tests,clean-engineering-code"
# Interaction: the words of Delete Ticket's link to ticket.py, which name its callout on the rendered page.
TICKET_LINK = "ticket"
# Interaction: the examples Reopen Ticket's steps observe, which name their callouts on the rendered page.
OBSERVED_EXAMPLES = ["closed ticket", "open ticket"]


def show_every_format(page) -> None:
    """Turns off each format selected, such as code, which the seed's session selects: no format selected shows every
    format, the markdown scenarios beside the code."""
    page.locator(".format-toggle").first.wait_for(timeout=SHOWN_MILLISECONDS)
    selected = page.locator('.format-toggle[aria-pressed="true"]')
    while selected.count():
        selected.first.click()
        page.wait_for_timeout(500)


def listed_entry(page, path: str):
    """The file bar's entry of path, once every file under the session's root is listed, in every format."""
    all_session_files(page)
    show_every_format(page)
    entry = page.locator(f'button.file-entry[title="{path}"]')
    entry.wait_for(timeout=SHOWN_MILLISECONDS)
    return entry


def rendered_marks(page) -> list[str]:
    """What the callout marks of the rendered page name, each name once, in order."""
    return sorted(set(page.locator(".markdown-page .rendered-callout-mark").all_inner_texts()))


def practice_toggle(page, short_name: str):
    return page.locator(".practice-toggle", has_text=short_name).first


def leave_out_connector(page, connector: str) -> None:
    """Chooses every connector the graph view's node filter offers but connector."""
    if page.locator('[data-testid="filter-connector"]').count() == 0:
        page.locator(".graph-filters-toggle").click()
    connectors = page.locator('[data-testid="filter-connector"]')
    connectors.locator(f'option[value="{connector}"]').wait_for(state="attached", timeout=GRAPH_READ_MILLISECONDS)
    offered = connectors.locator("option").evaluate_all("options => options.map(option => option.value)")
    connectors.select_option([each for each in offered if each != connector])


def callout_state(page) -> tuple[int, int]:
    """How many fold-outs are open, and how many closed labels show."""
    return (page.locator(".callout-block").count(), page.locator(".callout-label").count())


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
                    unfolded = lambda: [shown for shown in shown_lines(self.page) if shown in DELETE_LINES]
                    expect(settled(unfolded, lambda shown: shown == DELETE_LINES)).to(equal(DELETE_LINES))

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
            unfolded = lambda: [shown for shown in shown_lines(self.page) if shown.strip() in {text.strip() for text in GIVEN_STEP_LINES}][:3]
            expect(settled(unfolded, lambda shown: shown == GIVEN_STEP_LINES)).to(equal(GIVEN_STEP_LINES))

        with it("And the scenario's other step functions stay folded"):
            others = lambda: [shown for shown in shown_lines(self.page) if "world.ticket.delete(world.board)" in shown or "assert ticket_left(world)" in shown]
            expect(settled(others, lambda shown: shown == [])).to(equal([]))


with description("Fold Open Files To Selected Nodes and Open Several Files From Graph Nodes, in a real browser, more") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Story: Fold Open Files To Selected Nodes, Scenario: A code file opens with its classes open and their members folded"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            self.page.get_by_role("button", name="List", exact=True).click()
            self.page.locator(f'button.file-entry[title="{TICKET_CODE}"]').click()
            line(self.page, "class Ticket:").wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then Ticket is unfolded, showing the first lines of its operations"):
            firsts = lambda: [shown for shown in shown_lines(self.page) if shown.strip().startswith("def ")][:2]
            expect(settled(firsts, lambda shown: shown == TICKET_FIRST_LINES)).to(equal(TICKET_FIRST_LINES))

        with it("And Ticket.close and Ticket.delete are folded to their first lines"):
            bodies = lambda: [shown for shown in shown_lines(self.page) if shown in ("        return None", *DELETE_LINES)]
            expect(settled(bodies, lambda shown: shown == [])).to(equal([]))

    with context("Story: Fold Open Files To Selected Nodes, Scenario: A selected node is marked by one orange line beside its lines"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket")
            select(self.page, "Operation delete")
            self.page.locator(".file-selected-range").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then one orange line runs beside the lines of Ticket.delete, in the margin between the line numbers and the text"):
            lefts = self.page.locator(".file-selected-range").evaluate_all("marks => marks.map(mark => Math.round(mark.getBoundingClientRect().left))")
            expect((len(lefts), len(set(lefts)))).to(equal((DELETE_LINE_COUNT, 1)))

        with it("And the text of those lines is not shaded"):
            expect(self.page.locator(".view-overlays .file-selected-range").count()).to(equal(0))

    with context("Story: Open Several Files From Graph Nodes, Scenario: Selecting a scenario opens only its own lines, not the examples module its example comes from"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "stories", "Manage Tickets", "Remove Tickets", "Delete Ticket", "Delete Ticket")
            select(self.page, "Scenario a ticket on the board is deleted")
            self.page.locator("section.open-file").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then only the story test opens"):
            expect(settled(lambda: open_files(self.page), lambda shown: shown == [STEP_STORY])).to(equal([STEP_STORY]))

    with context("Story: Open Several Files From Graph Nodes, Scenario: Collapse one open file, then every open file"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket", "Board")
            select(self.page, "Operation delete")
            self.page.locator('button.graph-node[title="Operation reread"]').first.click(modifiers=["Control"])
            self.page.locator(f'section.open-file[aria-label="{BOARD_CODE}"]').wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then board.py shows only its name once the Person collapses it, and ticket.py stays whole"):
            self.page.get_by_title(f"Collapse {BOARD_CODE} to its name").click()
            expect(settled(lambda: heads_expanded(self.page), lambda shown: shown == ["true", "false"])).to(equal(["true", "false"]))

        with it("And every open file shows only its name once the Person presses Collapse all"):
            self.page.get_by_role("button", name="Collapse all").click()
            expect(settled(lambda: heads_expanded(self.page), lambda shown: shown == ["false", "false"])).to(equal(["false", "false"]))

        with it("And every open file shows whole again once the Person presses Expand all"):
            self.page.get_by_role("button", name="Expand all").click()
            expect(settled(lambda: heads_expanded(self.page), lambda shown: shown == ["true", "true"])).to(equal(["true", "true"]))

    # The seed's checkout-flow has no story map, so the callout here is a call's, which the same mark opens and closes; a
    # call carries no label, so the label hidden and brought back is left to the Graph app's own spec (harness/graph/app/app.test.tsx).
    with context("Story: Open Linked Sections In Place, Scenario: A callout opens and closes from its mark beside the line"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)
            graph_view(self.page)
            open_branches(self.page, "clean_engineering", "kanban", "Ticket")
            select(self.page, "Operation delete")
            line(self.page, "self.close()").wait_for(timeout=SHOWN_MILLISECONDS)
            self.page.locator(".callout-mark").first.wait_for(timeout=SHOWN_MILLISECONDS)
            self.closed = callout_state(self.page)
            mark_on(self.page, "self.close()").click()
            self.opened = settled(lambda: callout_state(self.page), lambda shown: shown[0] == 1)
            mark_on(self.page, "self.close()").click()
            self.closed_again = settled(lambda: callout_state(self.page), lambda shown: shown == self.closed)

        with after.all:
            self.page.close()

        with it("Then the call's lines show under it"):
            expect(self.opened[0]).to(equal(1))

        with it("And a second press closes them again"):
            expect(self.closed_again).to(equal(self.closed))

    # Each read of a file sends the file view's filters and the session answers the callouts they show (session.file
    # paths and node_filter); here the page, its server and the cdd server do it for real.
    with context("Story: Filter Callouts Like The Graph"):
        with before.all:
            for path, text in ((STORY_MAP, STORY_MAP_WITH_REOPEN_TEXT), (SCENARIOS, SCENARIOS_TEXT), (EXAMPLES_SCENARIOS, EXAMPLES_SCENARIOS_TEXT)):
                (self.stack.project / path).parent.mkdir(parents=True, exist_ok=True)
                (self.stack.project / path).write_text(text, encoding="utf-8")

        with context("Scenario: A practice turned off leaves out the callouts into its files"):
            with before.all:
                self.page = self.stack.open(CHECKOUT_FLOW.name, STORIES_AND_CODE_FIDELITIES)
                listed_entry(self.page, SCENARIOS).click()
                self.turned_on = settled(lambda: rendered_marks(self.page), lambda marks: TICKET_LINK in marks, SHOWN_MILLISECONDS / 1000)
                practice_toggle(self.page, "CE").click()
                self.turned_off = settled(lambda: rendered_marks(self.page), lambda marks: TICKET_LINK not in marks)
                practice_toggle(self.page, "CE").click()
                self.turned_on_again = settled(lambda: rendered_marks(self.page), lambda marks: TICKET_LINK in marks)

            with after.all:
                self.page.close()

            with it("Given the scenarios file carries its callout into ticket.py, a file of Clean Engineering"):
                expect(TICKET_LINK in self.turned_on).to(equal(True))

            with it("Then with Clean Engineering turned off the Given's line carries no callout into ticket.py"):
                expect(TICKET_LINK in self.turned_off).to(equal(False))

            with it("Then with Clean Engineering on again the Given's line carries its callout into ticket.py"):
                expect(TICKET_LINK in self.turned_on_again).to(equal(True))

        with context("Scenario: A connector left out of the node filter leaves out what a step reaches by it"):
            with before.all:
                self.page = self.stack.open(CHECKOUT_FLOW.name, STORIES_AND_CODE_FIDELITIES)
                listed_entry(self.page, EXAMPLES_SCENARIOS)
                graph_view(self.page)
                self.page.get_by_role("button", name="Rules", exact=True).click()
                self.page.get_by_role("button", name="List", exact=True).click()
                self.page.locator(f'button.file-entry[title="{EXAMPLES_SCENARIOS}"]').click()
                self.every_connector = settled(lambda: rendered_marks(self.page), lambda marks: marks == OBSERVED_EXAMPLES, SHOWN_MILLISECONDS / 1000)
                self.page.get_by_role("button", name="Graph", exact=True).click()
                leave_out_connector(self.page, "observes")
                self.page.get_by_role("button", name="List", exact=True).click()
                self.without_observes = settled(lambda: rendered_marks(self.page), lambda marks: marks == [], SHOWN_MILLISECONDS / 1000)

            with after.all:
                self.page.close()

            with it("Given the steps' lines carry the examples they observe, closed ticket and open ticket"):
                expect(self.every_connector).to(equal(OBSERVED_EXAMPLES))

            with it("Then with observes left out of the graph view's connectors no step carries the example it observes"):
                expect(self.without_observes).to(equal([]))


with description("Switch Files App Between Files And Graph, in a real browser, opened on another project") as self:
    with before.all:
        self.stack = FilesStack.on_another_project()

    with after.all:
        self.stack.close()

    with context("Given the Files app is opened on another project and lists checkout-flow's Stories and Clean Engineering files"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, FIDELITIES)

        with after.all:
            self.page.close()

        with context("Story: Switch Files App To Graph View, Scenario: The graph view shows the practice trees of the listed files, Example: another project"):
            with before.all:
                graph_view(self.page)

            with it("Then the file bar shows the Stories and Clean Engineering practice trees"):
                expect(sorted(self.page.locator('button.graph-node[title^="Practice "]').evaluate_all("nodes => nodes.map(node => node.title)"))).to(equal(PRACTICE_TREES))

            with it("And they are that project's graph, whose class Ticket holds close and delete alone, not the CDD checkout's Ticket"):
                open_branches(self.page, "clean_engineering", "kanban", "Ticket")
                operations = lambda: sorted(self.page.locator('button.graph-node[title^="Operation "]').evaluate_all("nodes => nodes.map(node => node.title)"))
                expect(settled(operations, lambda shown: bool(shown))).to(equal(TICKET_OPERATIONS))

        with context("Story: Open Several Files From Graph Nodes, Scenario: Selecting a node opens its file, Example: another project"):
            with before.all:
                select(self.page, "Operation delete")
                line(self.page, "self.close()").wait_for(timeout=SHOWN_MILLISECONDS)

            with it("Then that project's ticket.py opens in the source view, not the CDD checkout's"):
                expect(lines_in_order(self.page, TICKET_CODE)[0]).to(equal(TICKET_FIRST_LINE))
