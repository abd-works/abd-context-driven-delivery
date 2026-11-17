"""Review Files In Files App in a real browser, on the Files app served for real and opened on another project
(files_app_browser.FilesStack.on_another_project): its server started for this CDD checkout, the draw.io viewer already
running from a folder of its own, and the page on a throwaway project.

Scenarios: review_files_in_files_app_story.test.md, each example named another project. The Python tiers replay the
rest from review-files-in-files-app.story.shared.py, and the page's own specs hold what only the page shows."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import (
    DESIGN_REVIEW,
    DIAGRAM,
    DIAGRAM_CELL,
    DIAGRAM_PAGE,
    DRAWIO_LOADS_MILLISECONDS,
    SHOWN_MILLISECONDS,
    TICKET_CODE,
    FilesStack,
    all_session_files,
    drawio_editor,
    lines_in_order,
)
from space.session.graph_view_examples import CHECKOUT_FLOW

STORY_MAP_FIDELITIES = "stories-story-map"
CODE_FIDELITIES = "stories-acceptance-tests,clean-engineering-code"
# Interaction: the first line of the project's ticket.py; the CDD checkout's own space/kanban/ticket.py opens with its
# docstring.
TICKET_FIRST_LINE = "class Ticket:"


def listed(page, path: str):
    """The entry of path, once every file under the session's root is listed."""
    all_session_files(page)
    entry = page.locator(f'button.file-entry[title="{path}"]')
    entry.wait_for(timeout=SHOWN_MILLISECONDS)
    return entry


with description("Review Files In Files App, opened on another project") as self:
    with before.all:
        self.stack = FilesStack.on_another_project()

    with after.all:
        self.stack.close()

    with context("Story: List This Session Or All Session Files, Scenario: List all session files, then this session's, Example: another project"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, STORY_MAP_FIDELITIES)
            listed(self.page, DIAGRAM)

        with after.all:
            self.page.close()

        with it("Then the file bar lists that project's story-map.drawio as the one story map file on disk, not a file of the CDD checkout"):
            expect(self.page.locator("button.file-entry:not(.is-missing)").evaluate_all("entries => entries.map(entry => entry.title)")).to(equal([DIAGRAM]))

    with context("Story: Open Diagram In Files App, Scenario: Open a diagram beside the file list, Example: another project"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, STORY_MAP_FIDELITIES)
            listed(self.page, DIAGRAM).click()
            self.editor = drawio_editor(self.page)
            self.editor.locator(".gePageTab.geActivePage").wait_for(timeout=DRAWIO_LOADS_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the draw.io editor shows the cell Place Order, from the project the Files app is opened on"):
            expect(self.editor.get_by_text(DIAGRAM_CELL, exact=True).count()).to(equal(1))

        with it("And its page is named Checkout Story Map, not a blank Page-1"):
            expect(self.editor.locator(".gePageTab.geActivePage").inner_text().strip()).to(equal(DIAGRAM_PAGE))

    with context("Story: View File In Source View, Scenario: Show a code file in the viewer with its lines numbered, Example: another project"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, CODE_FIDELITIES)
            listed(self.page, TICKET_CODE).click()
            self.page.locator(f'section.open-file[aria-label="{TICKET_CODE}"] .view-lines .view-line').first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the source view shows that project's ticket.py, its first line reading class Ticket:, not the CDD checkout's"):
            expect(lines_in_order(self.page, TICKET_CODE)[0]).to(equal(TICKET_FIRST_LINE))
