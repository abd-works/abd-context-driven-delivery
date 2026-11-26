"""Diagnose And Align Session Formats in a real browser, on the Files app served for real (files_app_browser.FilesStack):
Diagnose asks the real cdd server for the session's gaps (format-alignment.diagnose_alignment) and Align has it render the
missing formats (format-alignment.align_formats), which writes the drawing and the whiteboard into the project.

Scenarios: align_formats_in_files_app_story.test.md. With ``FILES_E2E_SHOTS`` naming a folder, each step's screen is
saved there."""

import json
import os
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from files_app_browser import SHOWN_MILLISECONDS, FilesStack

# Seed: fill-cart, a session in a plain folder with Discovery and Stories alone on and markdown, drawio and whiteboard
# chosen for its story map, which is written as markdown alone.
FILL_CART = "fill-cart"
STORY_MAP = ".context/story-map.md"
DRAWING = ".context/story-map.drawio"
BOARD = ".context/story-map.whiteboard"
STORY_MAP_TEXT = "# Story Map — Bookshop\n\n# (E) Fill Cart\n\n## (E) Review Cart\n\n### (S) Customer --> Change Cart Line Quantity\n\n### (S) Customer --> Remove Cart Line\n"
FIDELITY = "stories-story-map"
# Rendering a drawing and a whiteboard and reading the graphs takes the cdd server a few seconds.
ALIGNED_MILLISECONDS = 120_000
SHOTS = os.environ.get("FILES_E2E_SHOTS", "")


def _seed_fill_cart(root: Path) -> None:
    (root / STORY_MAP).parent.mkdir(parents=True, exist_ok=True)
    (root / STORY_MAP).write_text(STORY_MAP_TEXT, encoding="utf-8")
    practices = {key: {"enabled": False} for key in ("ux", "ddd", "bdd", "clean_engineering")}
    practices["stories"] = {"enabled": True, "formats": {"story_map": ["markdown", "drawio", "whiteboard"]}}
    session = {"name": FILL_CART, "title": "Fill cart", "guidance": {"stages": ["discovery"]}, "practices": practices, "outputs": {"stories": {"root": ".context"}}}
    (root / f".sessions/{FILL_CART}").mkdir(parents=True)
    (root / f".sessions/{FILL_CART}/session.json").write_text(json.dumps(session), encoding="utf-8")
    (root / f".sessions/{FILL_CART}/session.log").write_text("", encoding="utf-8")


def _opened(stack: FilesStack):
    page = stack.browser.new_page(viewport={"width": 1600, "height": 900})
    page.goto(f"http://127.0.0.1:{stack.port}/?{urllib.parse.urlencode({'files': FILL_CART, 'fidelity': FIDELITY, 'project': str(stack.project)})}")
    page.locator(".format-alignment-button").first.wait_for(timeout=SHOWN_MILLISECONDS)
    return page


def _shot(page, name: str) -> None:
    """Save the screen of one step, when a folder for the screens is named."""
    if SHOTS:
        Path(SHOTS).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(Path(SHOTS) / f"{name}.png"))


def _said(page, list_label: str) -> list[str]:
    return page.locator(f'.format-alignment-list[aria-label="{list_label}"] .format-alignment-said').all_inner_texts()


with description("Story: Diagnose And Align Session Formats") as self:
    with before.all:
        self.stack = FilesStack(seed=_seed_fill_cart)

    with after.all:
        self.stack.close()

    with context("Scenario: Diagnose and align from the Files app"):
        with before.all:
            self.page = _opened(self.stack)
            _shot(self.page, "1-files-app-with-diagnose-button")
            self.page.locator(".format-alignment-button", has_text="Diagnose").click()
            self.page.locator(".format-alignment-summary").wait_for(timeout=ALIGNED_MILLISECONDS)
            _shot(self.page, "2-diagnosed-two-missing-files")
            self.gaps = _said(self.page, "Gaps between the formats")
            self.notes = self.page.locator(".format-alignment-note").all_inner_texts()
            self.page.locator(".format-alignment-button.is-align").click()
            self.page.locator('.format-alignment-list[aria-label="Files aligned"]').wait_for(timeout=ALIGNED_MILLISECONDS)
            _shot(self.page, "3-aligned-drawing-and-whiteboard-rendered")
            self.aligned = _said(self.page, "Files aligned")
            self.summary = self.page.locator(".format-alignment-summary").inner_text()

        with after.all:
            self.page.close()

        with it("Then the Files app lists the two missing files as gaps"):
            expect([(DRAWING in self.gaps[0] and "is not there" in self.gaps[0]), (BOARD in self.gaps[1] and "is not there" in self.gaps[1])]).to(equal([True, True]))

        with it("And each gap is marked as one Align closes"):
            expect(self.notes).to(equal(["Align closes this", "Align closes this"]))

        with it("Then the Files app lists the drawing and the whiteboard as rendered from the markdown"):
            expect([self.aligned[0].startswith(f"Rendered {DRAWING} from {STORY_MAP}."), self.aligned[1].startswith(f"Rendered {BOARD} from {STORY_MAP}.")]).to(equal([True, True]))

        with it("And the drawing and the whiteboard are in the project"):
            expect((self.stack.project / DRAWING).is_file() and (self.stack.project / BOARD).is_file()).to(be_true)

        with it("And the Files app says no gap is left"):
            expect(self.summary).to(equal("No gap in 1 fidelity checked"))
