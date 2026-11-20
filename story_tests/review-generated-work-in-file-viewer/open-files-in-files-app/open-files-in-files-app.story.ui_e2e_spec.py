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


# Seed: one file of each form the page renders, beside board.py, and the text each reads
# (review_files_in_files_app_story.test.md, View File In Source View).
README = str(Path(BOARD_CODE).with_name("README.md").as_posix())
README_TEXT = "# Checkout\n\nPlace an order from a [cart](cart.md).\n"
RENDERED_FILES = {
    README: README_TEXT,
    str(Path(BOARD_CODE).with_name("page.html").as_posix()): "<h1>Checkout</h1><script>parent.hacked = 1</script>",
    str(Path(BOARD_CODE).with_name("cart.svg").as_posix()): '<svg xmlns="http://www.w3.org/2000/svg"><circle r="4"/><script>alert(1)</script></svg>',
    str(Path(BOARD_CODE).with_name("cart.json").as_posix()): '{"items":[1,2]}',
    str(Path(BOARD_CODE).with_name("broken.json").as_posix()): '{"items":',
}


def _view(stack, path: str):
    """A page on checkout-flow's files opened on path, as a link naming the file to open first opens it."""
    page = stack.browser.new_page(viewport={"width": 1600, "height": 900})
    query = urllib.parse.urlencode({"files": CHECKOUT_FLOW.name, "fidelity": CODE_FIDELITIES, "project": str(stack.project), "file": path})
    page.goto(f"http://127.0.0.1:{stack.port}/?{query}")
    page.locator(f'section.open-file[aria-label="{path}"]').wait_for(timeout=SHOWN_MILLISECONDS)
    return page


def _pressed(page, name: str) -> str | None:
    return page.get_by_role("button", name=name, exact=True).get_attribute("aria-pressed")


with description("Story: View File In Source View, files with a rendered form") as self:
    with before.all:
        self.stack = FilesStack()
        for path, text in RENDERED_FILES.items():
            (self.stack.project / path).write_text(text, encoding="utf-8")

    with after.all:
        self.stack.close()

    with context("Scenario: Render a markdown file as the page it describes"):
        with before.all:
            self.page = _view(self.stack, README)

        with after.all:
            self.page.close()

        with it("Then the Files app shows Checkout rendered as a heading, not as # Checkout"):
            heading = self.page.locator(".file-rendered").get_by_role("heading", name="Checkout", level=1)
            heading.wait_for(timeout=SHOWN_MILLISECONDS)
            expect((heading.count(), self.page.get_by_text("# Checkout").count())).to(equal((1, 0)))

        with it("And its Rendered toggle is pressed and its Source toggle is not"):
            expect((_pressed(self.page, "Rendered"), _pressed(self.page, "Source"))).to(equal(("true", "false")))

        with it("And a link to a file that is not there keeps the Files app where it is, README.md the one open file"):
            self.page.locator(".file-rendered a", has_text="cart").click()
            expect(self.page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")).to(equal([README]))

    with context("Scenario: Switch a rendered file to its source and back"):
        with before.all:
            self.page = _view(self.stack, README)
            self.page.get_by_role("button", name="Source", exact=True).click()
            self.page.locator(".view-lines .view-line").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the source view shows README.md's text, its first line reading # Checkout, with Wrap lines beside the toggle"):
            first = self.page.locator(".view-lines .view-line").evaluate_all("lines => lines.sort((one, other) => one.offsetTop - other.offsetTop)[0].innerText")
            expect((first.replace(NBSP, " "), self.page.get_by_role("button", name="Wrap lines").count())).to(equal(("# Checkout", 1)))

        with it("And pressing Rendered shows Checkout as a heading again"):
            self.page.get_by_role("button", name="Rendered", exact=True).click()
            heading = self.page.locator(".file-rendered").get_by_role("heading", name="Checkout", level=1)
            heading.wait_for(timeout=SHOWN_MILLISECONDS)
            expect(self.page.locator(".view-lines").count()).to(equal(0))

    with context("Scenario: Render each format the page can draw"):
        with before.all:
            self.pages = []

        with after.all:
            for page in self.pages:
                page.close()

        with it("Then page.html shows in a frame that runs no script, Checkout as its heading"):
            page = _view(self.stack, "space/kanban/page.html")
            self.pages.append(page)
            page.frame_locator("iframe.rendered-html").get_by_role("heading", name="Checkout").wait_for(timeout=SHOWN_MILLISECONDS)
            expect(page.evaluate("window.hacked === undefined")).to(equal(True))

        with it("And cart.svg shows its circle and no script"):
            page = _view(self.stack, "space/kanban/cart.svg")
            self.pages.append(page)
            drawing = page.locator(".file-rendered.rendered-svg")
            drawing.locator("circle").wait_for(state="attached", timeout=SHOWN_MILLISECONDS)
            expect(drawing.locator("script").count()).to(equal(0))

        with it('And cart.json is laid out two spaces to a level, "items": [ on its second line'):
            page = _view(self.stack, "space/kanban/cart.json")
            self.pages.append(page)
            laid_out = page.locator(".file-rendered.rendered-json pre")
            laid_out.wait_for(timeout=SHOWN_MILLISECONDS)
            expect(laid_out.inner_text().split(chr(10))[1]).to(equal('  "items": ['))

        with it("And broken.json shows its text and says it is not valid JSON"):
            page = _view(self.stack, "space/kanban/broken.json")
            self.pages.append(page)
            problem = page.locator(".rendered-problem")
            problem.wait_for(timeout=SHOWN_MILLISECONDS)
            expect((problem.inner_text().startswith("Not valid JSON"), page.locator(".file-rendered.rendered-json pre").inner_text())).to(equal((True, '{"items":')))

    with context("Scenario: Show only the source view for a file with no rendered form"):
        with before.all:
            self.page = _view(self.stack, BOARD_CODE)
            self.page.locator(".view-lines .view-line").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the Files app shows board.py in the source view, with no Rendered or Source toggle"):
            expect(self.page.locator(".file-render-toggle").count()).to(equal(0))


# Seed: a story map whose story links its scenario file, whose Given links the domain term Book to the domain model's
# Book section and Cart Line to a heading the model does not have (review_files_in_files_app_story.test.md, View File In
# Source View, the callouts and links of a rendered page).
NOTES = str(Path(BOARD_CODE).with_name("notes").as_posix())
LINKED_MAP = f"{NOTES}/story-map.md"
LINKED_SCENARIOS = f"{NOTES}/add_book_to_cart_story.test.md"
LINKED_MODEL = f"{NOTES}/domain-model.md"
LINKED_FILES = {
    LINKED_MAP: "# Story Map\n\n### (S) Customer --> [Add Book To Cart](add_book_to_cart_story.test.md)\n",
    LINKED_SCENARIOS: "## Story: Add Book To Cart\n\n*Given* the Bookshop sells ++[Book](domain-model.md#book-entity)++ ++Tiny Tales++\n*And* a ++[Cart Line](domain-model.md#cartline-entity)++\n",
    LINKED_MODEL: "# Domain Model\n\n#### Book <<Entity>>\n\n+ reprice(amount: Money): void\n",
}
RENDERED_MARK = ".file-rendered .rendered-callout-mark"


def _open_files(page) -> list[str]:
    return page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")


with description("Story: View File In Source View, the callouts and links of a rendered page") as self:
    with before.all:
        self.stack = FilesStack()
        for path, text in LINKED_FILES.items():
            (self.stack.project / path).parent.mkdir(parents=True, exist_ok=True)
            (self.stack.project / path).write_text(text, encoding="utf-8")

    with after.all:
        self.stack.close()

    with context("Scenario: Open a callout in place on a rendered page"):
        with before.all:
            self.page = _view(self.stack, LINKED_MAP)
            self.story = self.page.locator(RENDERED_MARK, has_text="Add Book To Cart").first
            self.story.wait_for(timeout=SHOWN_MILLISECONDS)
            self.story.click()
            self.scenario = self.page.locator(".file-rendered .callout-section").first
            self.scenario.locator(".rendered-callout-mark", has_text="Book").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the scenario file shows under the story's line, rendered as a page, headed by its file and lines"):
            shown = (self.scenario.locator(".callout-go-to").first.inner_text(), self.scenario.get_by_role("heading", level=2).inner_text())
            expect(shown).to(equal((f"{LINKED_SCENARIOS} lines 1 to 4", "Story: Add Book To Cart")))

        with it("And pressing the mark at the end of the Given's line shows the Book section of the domain model under the Given"):
            self.scenario.locator(".rendered-callout-mark", has_text="Book").first.click()
            expect(self.scenario.locator(".callout-section").get_by_role("heading", level=4).inner_text()).to(equal("Book <<Entity>>"))

        with it("And a second press on the story's mark closes what it opened"):
            self.story.click()
            expect(self.page.locator(".file-rendered .callout-section").count()).to(equal(0))

    with context("Scenario: Follow a link on a rendered page"):
        with before.all:
            self.page = _view(self.stack, LINKED_MAP)
            self.page.locator(".file-rendered a", has_text="Add Book To Cart").click()
            self.page.locator(f'section.open-file[aria-label="{LINKED_SCENARIOS}"]').wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the Files app opens the scenario file"):
            expect(_open_files(self.page)).to(contain(LINKED_SCENARIOS))

    with context("Scenario: Say what is not there for a link to a heading or a file that is missing"):
        with before.all:
            self.page = _view(self.stack, LINKED_SCENARIOS)
            self.missing = self.page.locator(f"{RENDERED_MARK}.callout-missing")
            self.missing.wait_for(timeout=SHOWN_MILLISECONDS)
            self.missing.click()

        with after.all:
            self.page.close()

        with it("Then the line's mark, opened, says the domain model has no heading #cartline-entity"):
            expect(self.page.locator(".file-rendered .callout-section.callout-missing").inner_text()).to(equal(f"{LINKED_MODEL} has no heading #cartline-entity"))

        with it("And pressing the link opens no file"):
            self.page.locator(".file-rendered a", has_text="Cart Line").click()
            expect(_open_files(self.page)).to(equal([LINKED_SCENARIOS]))

        with it("And the source view marks the same lines, the Given's and the missing link's"):
            self.page.get_by_role("button", name="Source", exact=True).click()
            self.page.locator(".callout-mark").first.wait_for(timeout=SHOWN_MILLISECONDS)
            expect(self.page.locator(".callout-mark").count()).to(equal(2))
