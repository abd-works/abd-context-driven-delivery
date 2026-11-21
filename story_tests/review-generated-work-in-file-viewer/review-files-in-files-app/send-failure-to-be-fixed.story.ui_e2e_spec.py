"""Send A Failure To Be Fixed in a real browser, on the Files app served for real (files_app_browser.FilesStack): the
failure band's Fix asks the real cdd server for the failure's most common causes (failure.describe) and sends the fix
command to the chat that opened the page (chat.send), which a chat checking in with that server takes from its mailbox.
No Claude chat runs here: the command the chat takes is what its chat bar would run.

Scenarios: send_failure_to_be_fixed_story.test.md."""

import json
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import contain, equal, expect, start_with
from mamba import after, before, context, description, it

from files_app_browser import SHOWN_MILLISECONDS, FilesStack, all_session_files
from harness.mcp.spec_support import SpecChat
from tools.error_display.failure import FAILURE_KINDS

# Seed: bookshop, a session in a plain folder with Discovery and Stories alone on, whose story map links to a returns
# policy that is not there, beside its thin slice.
BOOKSHOP = "bookshop"
STORY_MAP = ".context/story-map.md"
THIN_SLICE = ".context/thin-slice.md"
STORY_MAP_TEXT = "# Story Map\n\n# (E) Browse Books\n\n## (S) Customer --> Search Books\n\nSee the [returns policy](returns-policy.md).\n"
MISSING_POLICY = f"{STORY_MAP} has a link that leads nowhere: .context/returns-policy.md is not there"
# Seed: the chat that opened the Files app, checked in with the cdd server as its chat bar checks in.
LENS_CHAT = "lens-chat"
FIDELITY = "stories-story-map"


def _seed_bookshop(root: Path) -> None:
    for path, text in ((STORY_MAP, STORY_MAP_TEXT), (THIN_SLICE, "# Thin Slice\n")):
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    practices = {key: {"enabled": False} for key in ("ux", "ddd", "bdd", "clean_engineering")}
    practices["stories"] = {"enabled": True, "formats": {"story_map": ["markdown"]}}
    session = {"name": BOOKSHOP, "title": "Bookshop", "guidance": {"stages": ["discovery"]}, "practices": practices, "outputs": {"stories": {"root": ".context"}}}
    (root / f".sessions/{BOOKSHOP}").mkdir(parents=True)
    (root / f".sessions/{BOOKSHOP}/session.json").write_text(json.dumps(session), encoding="utf-8")
    (root / f".sessions/{BOOKSHOP}/session.log").write_text("", encoding="utf-8")


def _opened(stack: FilesStack, ticket: str, chat: str = ""):
    """The Files app on ticket's story map files, opened by chat, or by no chat."""
    page = stack.browser.new_page(viewport={"width": 1600, "height": 900})
    named = {"files": ticket, "fidelity": FIDELITY, "project": str(stack.project), **({"chat": chat} if chat else {})}
    page.goto(f"http://127.0.0.1:{stack.port}/?{urllib.parse.urlencode(named)}")
    return page


def _checked_in(stack: FilesStack) -> list[dict]:
    """The commands lens-chat takes as it checks in, as its chat bar does every second. The browser holds this thread's
    event loop, so the chat calls the cdd server from a thread of its own."""
    chat = SpecChat(stack.cdd, stack.project, LENS_CHAT)
    with ThreadPoolExecutor(1) as pool:
        return pool.submit(chat.answer, "chat.check_in", chat=LENS_CHAT, is_busy=False, name="Lens", folder=str(stack.project)).result()


def _failure_saying(page, said: str):
    """The failure of the failure band that says said, or whose context does."""
    shown = page.locator(".failure-fix", has_text=said).first
    shown.wait_for(timeout=SHOWN_MILLISECONDS)
    return shown


def _fix_commands(taken: list[dict]) -> list[str]:
    return [command["text"] for command in taken if command["kind"] == "command"]


def _details_of(command: str) -> str:
    return json.loads(command.split("details=", 1)[1])


with description("Story: Send Failure To Be Fixed") as self:
    with before.all:
        self.stack = FilesStack(seed=_seed_bookshop)
        _checked_in(self.stack)

    with after.all:
        self.stack.close()

    with context("Scenario: Send links that lead nowhere to be fixed"):
        with before.all:
            self.page = _opened(self.stack, BOOKSHOP, LENS_CHAT)
            self.shown = _failure_saying(self.page, MISSING_POLICY)
            self.before_fix = self.shown.locator(".failure-fix-button").inner_text()
            _checked_in(self.stack)
            self.shown.locator(".failure-fix-button").click()
            self.page.locator(".failure-fix.is-sent").wait_for(timeout=SHOWN_MILLISECONDS)
            self.causes = self.shown.locator(".failure-fix-causes ol li").all_inner_texts()
            self.sent = _fix_commands(_checked_in(self.stack))

        with after.all:
            self.page.close()

        with it("Then the failure band shows that the story map has a link that leads nowhere, with a Fix button"):
            expect(self.before_fix).to(equal("Fix"))

        with it("Then the failure band lists the most common causes of a link to a file or heading that is not there"):
            expect(self.causes).to(equal(list(FAILURE_KINDS.named("missing_link").causes)))

        with it("And the chat lens-chat is sent the fix command with those causes"):
            expect(_details_of(self.sent[0])).to(contain(MISSING_POLICY, *self.causes))

        with it("And the fix command is the debug session command with the fix chosen"):
            expect(self.sent[0]).to(start_with("/space-session-debug-session choice=fix details="))

    with context("Scenario: Send a file that cannot be shown to be fixed"):
        with before.all:
            self.page = _opened(self.stack, BOOKSHOP, LENS_CHAT)
            all_session_files(self.page)
            entry = self.page.locator(f'button.file-entry[title^="{THIN_SLICE}"]')
            entry.wait_for(timeout=SHOWN_MILLISECONDS)
            (self.stack.project / THIN_SLICE).unlink()
            entry.click()
            self.context_said = f"Opening {THIN_SLICE} in the Files app"
            self.shown = _failure_saying(self.page, self.context_said)
            self.problem = self.page.locator(".files-problem").inner_text()
            _checked_in(self.stack)
            self.shown.locator(".failure-fix-button").click()
            self.shown.locator(".failure-fix-note").wait_for(timeout=SHOWN_MILLISECONDS)
            self.causes = self.shown.locator(".failure-fix-causes ol li").all_inner_texts()
            self.note = self.shown.locator(".failure-fix-note").inner_text()
            self.sent = _fix_commands(_checked_in(self.stack))

        with after.all:
            self.page.close()
            (self.stack.project / THIN_SLICE).write_text("# Thin Slice\n", encoding="utf-8")

        with it("Then the failure band shows the failure with the context it failed in and a Fix button"):
            expect(self.problem).to(contain(f"{THIN_SLICE} did not open"))

        with it("Then the failure band lists the most common causes of a file that cannot be shown, the first that the file was moved, renamed or deleted"):
            expect(self.causes[0]).to(start_with("The file was moved, renamed or deleted after the page listed it"))

        with it("And the chat lens-chat is sent the fix command, whose details hold the failure, its context and each of those causes"):
            expect(_details_of(self.sent[0])).to(contain(f"did not open {THIN_SLICE}", self.context_said, *self.causes))

        with it("And the failure band says the fix was sent"):
            expect(self.note).to(start_with("Sent to the chat that opened this page"))

    with context("Scenario: Dismiss a failure"):
        with before.all:
            self.page = _opened(self.stack, BOOKSHOP, LENS_CHAT)
            _failure_saying(self.page, MISSING_POLICY).locator(".failure-fix-dismiss").click()
            self.page.locator(".failure-fix").first.wait_for(state="detached", timeout=SHOWN_MILLISECONDS)
            all_session_files(self.page)
            self.page.locator(f'button.file-entry[title^="{STORY_MAP}"]').click()
            self.page.locator(".file-rendered, .view-lines").first.wait_for(timeout=SHOWN_MILLISECONDS)

        with after.all:
            self.page.close()

        with it("Then the failure band no longer shows it, and reading the same file again does not bring it back"):
            expect(self.page.locator(".failure-fix").count()).to(equal(0))

    with context("Scenario: Show the causes on a page no chat opened"):
        with before.all:
            self.page = _opened(self.stack, "no-such-session")
            self.shown = _failure_saying(self.page, "Opening the Files app on")
            _checked_in(self.stack)
            self.shown.locator(".failure-fix-button").click()
            self.shown.locator(".failure-fix-note").wait_for(timeout=SHOWN_MILLISECONDS)
            self.causes = self.shown.locator(".failure-fix-causes ol li").all_inner_texts()
            self.note = self.shown.locator(".failure-fix-note").inner_text()
            self.shown.locator(".failure-fix-command summary").click()
            self.command = self.shown.locator(".failure-fix-command pre").inner_text()
            self.sent = _fix_commands(_checked_in(self.stack))

        with after.all:
            self.page.close()

        with it("Then the failure band lists the most common causes of session roots that are wrong or missing"):
            expect(self.causes).to(equal(list(FAILURE_KINDS.named("session_roots").causes)))

        with it("And it shows the fix command"):
            expect(_details_of(self.command)).to(contain("did not list the files", *self.causes))

        with it("And says to copy it into a chat, since no chat opened the page"):
            expect(self.note).to(start_with("No chat opened this page, so nothing was sent"))

        with it("And nothing is sent"):
            expect(self.sent).to(equal([]))
