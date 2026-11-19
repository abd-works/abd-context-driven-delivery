"""Open Files In Files App in a real browser, on the Files app served for real (files_app_browser.FilesStack).

Scenarios: open_files_in_files_app_story.test.md; and, for files that changed on disk since the page listed them and a
project folder that is not there, review_files_in_files_app_story.test.md (List Files The Link Names, List This Session
Or All Session Files, View File In Source View)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import urllib.parse

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from files_app_browser import BOARD_LINK, BOARD_STORY, DESIGN_REVIEW, NBSP, SHOWN_MILLISECONDS, WHITEBOARD, FilesStack, all_session_files
from space.session.graph_view_examples import BOARD_CODE, BOARD_TEXT, CHECKOUT_FLOW
from space.session.session_file import VIEWER_SHOWS_LINES

FIDELITIES = "ux-mockup,stories-story-map"
CODE_FIDELITIES = "stories-acceptance-tests,clean-engineering-code"
# Interaction: the name board.py is given on disk after the page listed it.
RENAMED_BOARD = str(Path(BOARD_CODE).with_name("basket.py").as_posix())
# Seed: a code file one line longer than the viewer shows.
LONG_CODE = str(Path(BOARD_CODE).with_name("big.py").as_posix())
LONG_TEXT = "pass" + chr(10) * VIEWER_SHOWS_LINES + "pass"


with description("Story: Open Whiteboard In Files App") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Open a whiteboard file as a canvas"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, FIDELITIES)
            diagram = self.page.locator('.format-toggle[title^="diagram:"]')
            diagram.wait_for(timeout=SHOWN_MILLISECONDS)
            if diagram.get_attribute("aria-pressed") != "true":
                diagram.click()
            self.page.locator('.format-toggle[title^="diagram:"][aria-pressed="true"]').wait_for(timeout=SHOWN_MILLISECONDS)
            self.entry = self.page.locator(f'button.file-entry.is-whiteboard[title^="{WHITEBOARD}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the whiteboard is listed as story-map, marked as a whiteboard"):
            expect(self.entry.inner_text().replace(NBSP, " ").strip()).to(equal("story-map whiteboard"))

        with it("And pressing it draws the board on a canvas, not the text of the file"):
            self.entry.click()
            canvas = self.page.locator("svg.whiteboard-canvas")
            canvas.wait_for(timeout=SHOWN_MILLISECONDS)
            expect(BOARD_STORY in canvas.text_content()).to(equal(True))

        with it("And the board in Claude is a press away, at its board's address"):
            link = self.page.locator(f'a.board-link[title^="{WHITEBOARD}"]').first
            expect(link.get_attribute("href")).to(equal(BOARD_LINK))


with description("Story: Open Whiteboard In Files App, opened on another project") as self:
    with before.all:
        self.stack = FilesStack.on_another_project()

    with after.all:
        self.stack.close()

    with context("Scenario: Open a whiteboard file as a canvas, Example: another project"):
        with before.all:
            self.page = self.stack.open(DESIGN_REVIEW, FIDELITIES)
            diagram = self.page.locator('.format-toggle[title^="diagram:"]')
            diagram.wait_for(timeout=SHOWN_MILLISECONDS)
            if diagram.get_attribute("aria-pressed") != "true":
                diagram.click()
            self.page.locator('.format-toggle[title^="diagram:"][aria-pressed="true"]').wait_for(timeout=SHOWN_MILLISECONDS)
            self.entry = self.page.locator(f'button.file-entry.is-whiteboard[title^="{WHITEBOARD}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the whiteboard is listed as story-map, marked as a whiteboard"):
            expect(self.entry.inner_text().replace(NBSP, " ").strip()).to(equal("story-map whiteboard"))

        with it("And its board is at the address that project keeps, not one the CDD checkout keeps"):
            expect(self.page.locator(f'a.board-link[title^="{WHITEBOARD}"]').first.get_attribute("href")).to(equal(BOARD_LINK))


def _all_files_again(page, path: str):
    """The entry of path once the Person lists All session files again, which reads the files as they are on disk."""
    all_session_files(page)
    entry = page.locator(f'button.file-entry[title^="{path}"]')
    entry.wait_for(timeout=SHOWN_MILLISECONDS)
    return entry


def _problem(page) -> str:
    """What the page says went wrong, once it says so."""
    shown = page.locator(".files-problem")
    shown.wait_for(timeout=SHOWN_MILLISECONDS)
    return shown.inner_text()


with description("Open Files In Files App, with files that changed on disk since the page listed them") as self:
    with before.all:
        self.stack = FilesStack()

    with after.all:
        self.stack.close()

    with context("Story: View File In Source View, Scenario: Say so when a listed file is gone"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, CODE_FIDELITIES)
            entry = _all_files_again(self.page, BOARD_CODE)
            (self.stack.project / BOARD_CODE).unlink()
            entry.click()
            self.said = _problem(self.page)

        with after.all:
            self.page.close()
            (self.stack.project / BOARD_CODE).write_text(BOARD_TEXT, encoding="utf-8")

        with it("Then the Files app says board.py did not open because nothing is at that path"):
            expect(self.said).to(contain(f"{BOARD_CODE} did not open", f"nothing at {BOARD_CODE}"))

        with it("And shows no editor for it, so nothing can be saved over it"):
            expect(self.page.locator(".view-lines").count()).to(equal(0))

    with context("Story: List This Session Or All Session Files, Scenario: List the files again on each press"):
        with before.all:
            self.page = self.stack.open(CHECKOUT_FLOW.name, CODE_FIDELITIES)
            _all_files_again(self.page, BOARD_CODE)
            (self.stack.project / BOARD_CODE).rename(self.stack.project / RENAMED_BOARD)
            _all_files_again(self.page, RENAMED_BOARD)

        with after.all:
            self.page.close()
            (self.stack.project / RENAMED_BOARD).rename(self.stack.project / BOARD_CODE)

        with it("Then the file bar lists the file under its new name"):
            expect(self.page.locator(f'button.file-entry[title="{RENAMED_BOARD}"]').count()).to(equal(1))

        with it("And lists its old name no longer as a file to open"):
            expect(self.page.locator(f'button.file-entry[title^="{BOARD_CODE}"]:not(.is-missing)').count()).to(equal(0))

    with context("Story: View File In Source View, Scenario: Refuse a file longer than the viewer shows"):
        with before.all:
            (self.stack.project / LONG_CODE).write_text(LONG_TEXT, encoding="utf-8")
            self.page = self.stack.open(CHECKOUT_FLOW.name, CODE_FIDELITIES)
            _all_files_again(self.page, LONG_CODE).click()
            self.said = _problem(self.page)

        with after.all:
            self.page.close()
            (self.stack.project / LONG_CODE).unlink()

        with it("Then the Files app says big.py did not open, naming its lines and the most the viewer shows"):
            expect(self.said).to(contain(f"{LONG_CODE} did not open", f"{VIEWER_SHOWS_LINES + 1:,} lines", f"at most {VIEWER_SHOWS_LINES:,}"))

        with it("And the next file the Person views opens as before"):
            self.page.locator(f'button.file-entry[title="{BOARD_CODE}"]').click()
            self.page.locator(".view-lines .view-line").first.wait_for(timeout=SHOWN_MILLISECONDS)
            expect(self.page.locator(".files-problem").count()).to(equal(0))

    with context("Story: List Files The Link Names, Scenario: Say so when the project folder the link names is not there"):
        with before.all:
            self.removed = self.stack.top / "removed-worktree"
            self.page = self.stack.browser.new_page()
            query = urllib.parse.urlencode({"files": CHECKOUT_FLOW.name, "fidelity": CODE_FIDELITIES, "project": str(self.removed)})
            self.page.goto(f"http://127.0.0.1:{self.stack.port}/?{query}")
            self.said = _problem(self.page)

        with after.all:
            self.page.close()

        with it("Then it says the files did not list because that project folder is not there, naming the folder"):
            expect(self.said).to(contain("The files did not list", f"The project folder {self.removed} is not there"))

        with it("But the page holds no word of Python or of the cdd server"):
            expect([word for word in ("python", "cdd server") if word in self.said.lower()]).to(equal([]))
