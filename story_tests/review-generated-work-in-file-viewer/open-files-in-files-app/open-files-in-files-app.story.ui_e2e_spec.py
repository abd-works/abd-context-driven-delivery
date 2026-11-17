"""Open Files In Files App in a real browser, on the Files app served for real (files_app_browser.FilesStack).

Scenarios: open_files_in_files_app_story.test.md."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import BOARD_LINK, DESIGN_REVIEW, NBSP, SHOWN_MILLISECONDS, WHITEBOARD, FilesStack

FIDELITIES = "ux-mockup,stories-story-map"


with description("Story: Open Whiteboard In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Open a whiteboard file's board"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, FIDELITIES)
            diagram = self.page.locator('.format-toggle[title^="diagram:"]')
            diagram.wait_for(timeout=SHOWN_MILLISECONDS)
            if diagram.get_attribute("aria-pressed") != "true":
                diagram.click()
            self.page.locator('.format-toggle[title^="diagram:"][aria-pressed="true"]').wait_for(timeout=SHOWN_MILLISECONDS)
            self.entry = self.page.locator(f'a.file-entry.is-published[title^="{WHITEBOARD}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the whiteboard is listed as story-map, marked as a whiteboard"):
            expect(self.entry.inner_text().replace(NBSP, " ").strip()).to(equal("story-map ↗ whiteboard"))

        with it("And pressing it opens the board in Claude, not the text of the file"):
            expect(self.entry.get_attribute("href")).to(equal(BOARD_LINK))


with description("Story: Open Whiteboard In Files App, opened on another project") as self:
    with before.all:
        self.stack = FilesStack.on_another_project()

    with after.all:
        self.stack.close()

    with context("Scenario: Open a whiteboard file's board, Example: another project"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, FIDELITIES)
            diagram = self.page.locator('.format-toggle[title^="diagram:"]')
            diagram.wait_for(timeout=SHOWN_MILLISECONDS)
            if diagram.get_attribute("aria-pressed") != "true":
                diagram.click()
            self.page.locator('.format-toggle[title^="diagram:"][aria-pressed="true"]').wait_for(timeout=SHOWN_MILLISECONDS)
            self.entry = self.page.locator(f'a.file-entry.is-published[title^="{WHITEBOARD}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the whiteboard is listed as story-map, marked as a whiteboard"):
            expect(self.entry.inner_text().replace(NBSP, " ").strip()).to(equal("story-map ↗ whiteboard"))

        with it("And pressing it opens the board at the address that project keeps, not one the CDD checkout keeps"):
            expect(self.entry.get_attribute("href")).to(equal(BOARD_LINK))
