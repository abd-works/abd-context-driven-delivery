"""Filter Files In Files App in a real browser, on the Files app served for real (files_app_browser.FilesStack).

Scenarios: filter_files_in_files_app_story.test.md."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import CANVAS, CANVAS_LINK, DESIGN_REVIEW, NBSP, SHOWN_MILLISECONDS, FilesStack

FIDELITIES = "ux-mockup,stories-story-map"


with description("Story: Filter Files By Format In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Show a design canvas in its design-canvas folder"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, FIDELITIES)
            self.entry = self.page.locator(f'a.file-entry.is-published[title^="{CANVAS}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the design canvas is listed by the title it is published under, marked as a design canvas"):
            expect(self.entry.inner_text().replace(NBSP, " ").strip()).to(equal("ux-mockup.version-1 ↗ design canvas"))

        with it("And pressing it opens the design canvas at its link, not the text of canvas.json"):
            expect(self.entry.get_attribute("href")).to(equal(CANVAS_LINK))


with description("Story: Filter Files By Format In Files App, opened on another project") as self:
    with before.all:
        self.stack = FilesStack.on_another_project()

    with after.all:
        self.stack.close()

    with context("Scenario: Show a design canvas in its design-canvas folder, Example: another project"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, FIDELITIES)
            self.entry = self.page.locator(f'a.file-entry.is-published[title^="{CANVAS}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the design canvas is listed by the title it is published under, ux-mockup.version-1, marked as a design canvas"):
            expect(self.entry.inner_text().replace(NBSP, " ").strip()).to(equal("ux-mockup.version-1 ↗ design canvas"))

        with it("And pressing it opens the design canvas at the link that project keeps, not the text of canvas.json"):
            expect(self.entry.get_attribute("href")).to(equal(CANVAS_LINK))
