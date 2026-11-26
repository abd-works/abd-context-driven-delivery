"""Act On Files From File Menu, and the All files scope of Filter Files In Files App, in a real browser, on the Files
app served for real (files_app_browser.FilesStack): the twin of ``harness/files_app/app/files/file-menu.spec.ts``, which
stubs the Files server. Here each choice of the file menu reaches the real cdd server, which deletes, validates and adds
roots on the session's real folder and session.json.

Scenarios: act_on_files_from_file_menu_story.test.md, and List Every File In Session Folders in
filter_files_in_files_app_story.test.md."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_false, contain, equal, expect
from mamba import after, before, context, description, it

from files_app_browser import (
    GRAPH_READ_MILLISECONDS,
    REVIEW_MAP,
    REVIEW_NOTE,
    REVIEW_SCENARIOS,
    SHOWN_MILLISECONDS,
    STORY_REVIEW,
    UNDECLARED_NOTE,
    FilesStack,
)
from space.session import Sessions

STORY_MAP_FIDELITIES = "stories-story-map"


def all_files(page) -> None:
    """Every file in the session's folders listed, whatever the stages, practices and formats selected."""
    page.get_by_role("button", name="All files", exact=True).click()
    page.locator(".file-list, .file-tree").first.wait_for(timeout=SHOWN_MILLISECONDS)


def listed_titles(page) -> list[str]:
    return page.locator("button.file-entry").evaluate_all("entries => entries.map(entry => entry.title)")


def menu_choice(page, choice: str):
    """The file menu's choice named choice, on the menu a right-click opened."""
    return page.get_by_role("menu").first.get_by_role("menuitem", name=choice, exact=True)


with description("Story: Delete File Or Folder From File Menu") as self:
    with before.all:
        self.stack = FilesStack.with_files_to_act_on()

    with after.all:
        self.stack.close()

    with context("Scenario: Delete a file after confirming"):
        with before.all:
            # Given the Files app lists review/.context/notes.md, under the session's roots
            self.page = self.stack.open(STORY_REVIEW, STORY_MAP_FIDELITIES)
            all_files(self.page)
            self.entry = self.page.locator(f'button.file-entry[title="{REVIEW_NOTE}"]')
            self.entry.wait_for(timeout=SHOWN_MILLISECONDS)
            # When the Person right-clicks notes.md and chooses Delete
            self.entry.click(button="right")
            menu_choice(self.page, "Delete…").click()
            self.asked = self.page.get_by_role("alertdialog", name="Confirm delete").locator("p").inner_text()
            # When the Person confirms
            self.page.get_by_role("alertdialog", name="Confirm delete").get_by_role("button", name="Delete", exact=True).click()
            self.entry.wait_for(state="detached", timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the page asks Delete review/.context/notes.md? This cannot be undone."):
            expect(self.asked).to(equal(f"Delete {REVIEW_NOTE}? This cannot be undone."))

        with it("Then the session deletes review/.context/notes.md"):
            expect((self.stack.project / REVIEW_NOTE).exists()).to(be_false)

        with it("And the file list is read again, without it"):
            expect(listed_titles(self.page)).not_to(contain(REVIEW_NOTE))


with description("Story: Validate File Or Folder From File Menu") as self:
    with before.all:
        self.stack = FilesStack.with_files_to_act_on()

    with after.all:
        self.stack.close()

    with context("Scenario: Validate a file a fidelity declares"):
        with before.all:
            # Given the session shows Stories' story map, which declares review/.context/story-map.md
            self.page = self.stack.open(STORY_REVIEW, STORY_MAP_FIDELITIES)
            all_files(self.page)
            entry = self.page.locator(f'button.file-entry[title="{REVIEW_MAP}"]')
            entry.wait_for(timeout=SHOWN_MILLISECONDS)
            # When the Person right-clicks story-map.md and chooses Validate
            entry.click(button="right")
            menu_choice(self.page, "Validate").click()
            toast = self.page.locator(".toast", has_text=f"Validated {REVIEW_MAP}")
            toast.wait_for(timeout=GRAPH_READ_MILLISECONDS)
            self.toast = toast.inner_text()

        with after.all:
            self.page.close()

        with it("Then the page says which fidelities checked it"):
            expect(self.toast).to(equal(f"Validated {REVIEW_MAP} with stories-story-map"))


with description("Story: Add File Or Folder To Practice") as self:
    with before.all:
        self.stack = FilesStack.with_files_to_act_on()

    with after.all:
        self.stack.close()

    with context("Scenario: Add a folder to a practice"):
        with before.all:
            # Given the Files app shows the session's files in their folders, review/checkout among them
            self.page = self.stack.open(STORY_REVIEW, STORY_MAP_FIDELITIES)
            all_files(self.page)
            self.page.get_by_role("button", name="Folders", exact=True).click()
            folder = self.page.locator(f'button.file-folder[title="{REVIEW_SCENARIOS}"]')
            folder.wait_for(timeout=SHOWN_MILLISECONDS)
            # When the Person right-clicks review/checkout and points at Add to practice
            folder.click(button="right")
            menu_choice(self.page, "Add to practice ▸").hover()
            # When the Person chooses Stories
            self.page.get_by_role("menu", name="Add to practice").get_by_role("menuitem", name="Stories", exact=True).click()
            toast = self.page.locator(".toast", has_text=f"{REVIEW_SCENARIOS} added to")
            toast.wait_for(timeout=SHOWN_MILLISECONDS)
            self.toast = toast.inner_text()

        with after.all:
            self.page.close()

        with it("Then review/checkout is a root of each Stories fidelity, kept in session.json"):
            expect(Sessions(self.stack.project).named(STORY_REVIEW).practice("stories").added_roots).to(equal([REVIEW_SCENARIOS]))

        with it("And the page says review/checkout added to Stories"):
            expect(self.toast).to(equal(f"{REVIEW_SCENARIOS} added to Stories"))

        with it("And the file bar shows checkout as a folder at the top of the tree"):
            top = self.page.locator("ul.file-tree > li > button.file-folder").evaluate_all("folders => folders.map(folder => folder.title)")
            expect(top[0]).to(equal(REVIEW_SCENARIOS))


with description("Story: List Every File In Session Folders") as self:
    with before.all:
        self.stack = FilesStack.with_files_to_act_on()

    with after.all:
        self.stack.close()

    with context("Scenario: List every file in the session's folders"):
        with before.all:
            # Given review/notes.txt is a file no fidelity declares, which the stages, practices and formats selected leave
            # out: story-review's chosen code format leaves out even its story map, so the selection lists no file
            self.page = self.stack.open(STORY_REVIEW, STORY_MAP_FIDELITIES)
            self.page.get_by_role("button", name="All session files").click()
            self.page.locator(".files-side").locator(".file-list, p.files-note:not(:has-text('Reading the files'))").first.wait_for(timeout=SHOWN_MILLISECONDS)
            self.selected = listed_titles(self.page)
            # When the Person lists all files, pressing All files, the first of the scope buttons
            self.first_scope = self.page.get_by_role("group", name="Files listed").get_by_role("button").first.get_attribute("aria-label")
            all_files(self.page)
            self.page.locator(f'button.file-entry[title="{UNDECLARED_NOTE}"]').wait_for(timeout=SHOWN_MILLISECONDS)
            self.everything = listed_titles(self.page)

        with after.all:
            self.page.close()

        with it("Given the selection does not list review/notes.txt"):
            expect(self.selected).not_to(contain(UNDECLARED_NOTE))

        with it("Then All files is the first of the scope buttons"):
            expect(self.first_scope).to(equal("All files"))

        with it("Then the file bar lists every file under review, notes.txt among them"):
            expect(self.everything).to(contain(UNDECLARED_NOTE, REVIEW_MAP, REVIEW_NOTE))

        with it("And each file is listed once"):
            expect(len(self.everything)).to(equal(len(set(self.everything))))
