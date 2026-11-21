"""Specs for diagnosing and aligning a session's formats on a real project: a story map written as markdown, a draw.io
drawing and a whiteboard, each gap made by hand in the files, read by the real graph and closed by the real Render
action; and the same diagnosis as the cdd server answers it for a page. Heavy: every example renders drawings and reads
graphs, and the last context starts a cdd server of its own from a throwaway ``~/.cdd``. The rules one object decides
are in format_alignment_spec.py."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_empty, be_true, contain, equal, expect
from mamba import after, before, context, description, it

import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from harness.mcp.spec_support import SpecChat, SpecServer
from space.session import Sessions
from space.session.format_alignment import SessionAlignment
from space.session.throwaway_project import ExampleHome

TOOLSETS = ("space.session.session:Session", "space.session.practice_session_output:FidelitySessionOutput", "space.session.sessions:Sessions", "cdd_guidance.actions.render.render:Render")
STORY_MAP = ".context/story-map.md"
DRAWING = ".context/story-map.drawio"
BOARD = ".context/story-map.whiteboard"
STORY_MAP_TEXT = """\
# Story Map — Bookshop

# (E) Fill Cart

## (E) Review Cart

### (S) Customer --> Change Cart Line Quantity

### (S) Customer --> Remove Cart Line
"""
DOMAIN_MODEL = ".context/domain-model.md"
CART_CODE = "ordering/cart/cart.py"
ORDER_CODE = "ordering/order/order.py"
DOMAIN_MODEL_TEXT = """# Domain Model — Bookshop

---

## Ordering | custom

### Cart

A cart holds one line per book.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
----
+ total(): Money

### Order

An order is a cart a customer submitted.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
----
+ submit(): void
"""
STORY_TEST = "story_tests/fill-cart/review-cart/remove_cart_line_story.test.md"
STORY_TEST_TEXT = """## Story: Remove Cart Line

**Story type:** website

### Behaviors

#### Scenario: Remove the only line

*Given* the Customer has a cart with one line
*When* the Customer removes the line
*Then* the cart is empty
"""
REMOVE_CART_LINE = "### (S) Customer --> Remove Cart Line\n"
CHANGE_QUANTITY = "### (S) Customer --> Change Cart Line Quantity\n\n"
# A link from the story map to a heading its target does not hold.
BROKEN_LINK = "\nThe classes are in [Cart](domain-model.md#cart-that-is-not-there).\n"
# One card of a draw.io story map: the link that carries the story's name, with the cell inside it.
CARD = r'<UserObject label="{name}".*?</UserObject>'


def _project() -> Path:
    """A git project whose story map is written as markdown alone."""
    project = Path(tempfile.mkdtemp(prefix="cdd-format-alignment-"))
    subprocess.run(["git", "init", "-b", "main"], cwd=project, capture_output=True, text=True, check=True)
    (project / ".context").mkdir()
    (project / STORY_MAP).write_text(STORY_MAP_TEXT, encoding="utf-8")
    return project


def _session(project: Path):
    """The project's session working on Stories alone, with the story map's drawing and whiteboard chosen beside its
    markdown."""
    Sessions(project).switch("fill-cart", project)
    session = Sessions(project).current()
    for practice in session.own_practices.values():
        practice.enable(practice.name == "stories")
    story_map = session.practice("stories").guidance.fidelities.called("story_map").session_output
    story_map.choose_format("drawio", True)
    story_map.choose_format("whiteboard", True)
    return session


def _without_card(drawing: str, name: str) -> str:
    return re.sub(CARD.format(name=name), "", drawing, flags=re.S)


def _with_card_moved(drawing: str, name: str, x: str) -> str:
    card = re.search(CARD.format(name=name), drawing, flags=re.S).group(0)
    return drawing.replace(card, re.sub(r'<mxGeometry x="[^"]*"', f'<mxGeometry x="{x}"', card, count=1))


def _kinds(gaps) -> list[tuple[str, str]]:
    return [(gap.kind, gap.file) for gap in gaps]


# (E) Review Generated Work In File Viewer
# (E) Align Formats In Files App
# (S) Person --> Diagnose And Align Session Formats
with description("a session's story map with its markdown, drawing and whiteboard chosen") as self:
    with before.each:
        self.home = ExampleHome()
        self.project = _project()
        self.session = _session(self.project)
        self.alignment = SessionAlignment(self.session)

    with after.each:
        self.home.close()

    with context("whose practice writes under the project's .context folder, with only the markdown written"):
        with before.each:
            self.session.practice("stories").choose_root(".context")

        with it("should report the drawing and the whiteboard as missing beside the markdown"):
            expect(_kinds(self.alignment.diagnose().gaps)).to(equal([("missing_file", DRAWING), ("missing_file", BOARD)]))

        with context("that is aligned"):
            with it("should render both beside the markdown"):
                expect([done.file for done in self.alignment.align().aligned]).to(equal([DRAWING, BOARD]))

    with context("with only the markdown written"):
        with it("should report the drawing and the whiteboard as missing, each aligned from the markdown"):
            gaps = self.alignment.diagnose().gaps
            expect([(gap.kind, gap.file, gap.source, gap.is_alignable) for gap in gaps]).to(equal([("missing_file", DRAWING, STORY_MAP, True), ("missing_file", BOARD, STORY_MAP, True)]))

        with context("that is aligned"):
            with before.each:
                self.result = self.alignment.align()

            with it("should render the drawing and the whiteboard from the markdown"):
                expect([(done.file, done.source) for done in self.result.aligned]).to(equal([(DRAWING, STORY_MAP), (BOARD, STORY_MAP)]))

            with it("should say the whiteboard still goes on its board in Claude"):
                expect(self.result.aligned[1].follow_up).to(contain("render.publish_board"))

            with it("should leave no gap"):
                expect(self.result.diagnosis.is_aligned).to(be_true)

    with context("with every format written from the markdown"):
        with before.each:
            self.alignment.align()
            self.drawing = self.project / DRAWING

        with it("should find the formats aligned"):
            expect(self.alignment.diagnose().gaps).to(be_empty)

        with context("that the whiteboard was deleted from and a story's card was dropped from the drawing"):
            with before.each:
                (self.project / BOARD).unlink()
                moved = _with_card_moved(self.drawing.read_text(encoding="utf-8"), "Change Cart Line Quantity", "777")
                self.drawing.write_text(_without_card(moved, "Remove Cart Line"), encoding="utf-8")

            with it("should report the whiteboard missing and the drawing lacking the story"):
                expect(_kinds(self.alignment.diagnose().gaps)).to(equal([("missing_file", BOARD), ("format_lacks", DRAWING)]))

            with it("should name the story and the edge the drawing lacks"):
                lacking = self.alignment.diagnose().gaps[1]
                expect((lacking.missing_nodes, lacking.missing_edges)).to(equal((["Story 'Remove Cart Line'"], ["SubEpic 'Review Cart' decomposedInto Story 'Remove Cart Line'"])))

            with it("should say in plain words which file lacks what, and which file it is aligned from"):
                expect(self.alignment.diagnose().gaps[1].message).to(equal(
                    f"{DRAWING} lacks Story 'Remove Cart Line', the edge SubEpic 'Review Cart' decomposedInto Story 'Remove Cart Line', "
                    f"which {STORY_MAP} holds. Align renders {DRAWING} from {STORY_MAP}."
                ))

            with context("that is aligned"):
                with before.each:
                    self.result = self.alignment.align()

                with it("should leave no gap and meet no failure"):
                    expect((self.result.diagnosis.gaps, self.result.failures)).to(equal(([], [])))

                with it("should draw the dropped story again"):
                    expect(self.drawing.read_text(encoding="utf-8")).to(contain('label="Remove Cart Line"'))

                with it("should keep the card a person moved where they put it"):
                    card = re.search(CARD.format(name="Change Cart Line Quantity"), self.drawing.read_text(encoding="utf-8"), flags=re.S).group(0)
                    expect(card).to(contain('<mxGeometry x="777"'))

        with context("that a story was added to in the markdown alone"):
            with before.each:
                story_map = self.project / STORY_MAP
                story_map.write_text(STORY_MAP_TEXT + "\n### (S) Customer --> Empty Cart\n", encoding="utf-8")

            with it("should report the drawing and the whiteboard as lacking it"):
                expect(_kinds(self.alignment.diagnose().gaps)).to(equal([("format_lacks", DRAWING), ("format_lacks", BOARD)]))

        with context("that a story was dropped from in the drawing alone, and another in the markdown alone"):
            with before.each:
                self.drawing.write_text(_without_card(self.drawing.read_text(encoding="utf-8"), "Remove Cart Line"), encoding="utf-8")
                (self.project / STORY_MAP).write_text(STORY_MAP_TEXT.replace(CHANGE_QUANTITY, ""), encoding="utf-8")
                self.files = [self.project / path for path in (STORY_MAP, DRAWING, BOARD)]
                self.before = [file.read_text(encoding="utf-8") for file in self.files]

            with it("should report the two as a person's decision, with no file to align from"):
                conflict = next(gap for gap in self.alignment.diagnose().gaps if gap.file == DRAWING)
                expect((conflict.kind, conflict.source, conflict.is_alignable)).to(equal(("formats_conflict", "", False)))

            with it("should leave the whiteboard, which holds more than the markdown, to the person too"):
                gaps = self.alignment.diagnose().gaps
                expect([(gap.kind, gap.file, gap.is_alignable) for gap in gaps]).to(equal([("formats_conflict", DRAWING, False), ("format_lacks", STORY_MAP, False)]))

            with it("should name what each file holds alone"):
                conflict = next(gap for gap in self.alignment.diagnose().gaps if gap.file == DRAWING)
                expect(conflict.message).to(contain(f"only {STORY_MAP} holds Story 'Remove Cart Line'", f"only {DRAWING} holds Story 'Change Cart Line Quantity'"))

            with context("that is aligned"):
                with before.each:
                    self.alignment.align()

                with it("should leave every file of the story map as it is"):
                    expect([file.read_text(encoding="utf-8") for file in self.files] == self.before).to(be_true)

        with context("whose markdown was emptied and whose whiteboard was deleted"):
            with before.each:
                (self.project / STORY_MAP).write_text("", encoding="utf-8")
                (self.project / BOARD).unlink()
                self.result = self.alignment.align()

            with it("should answer the render it could not make as a failure naming the file"):
                expect([(failure.kind, failure.file) for failure in self.result.failures]).to(contain(("render_failed", BOARD)))

            with it("should say what the render said"):
                failure = next(failure for failure in self.result.failures if failure.file == BOARD)
                expect(failure.message).to(contain("NothingToRender", "is empty"))

        with context("whose drawing no longer reads as a drawing"):
            with before.each:
                self.drawing.write_text("<mxfile><diagram", encoding="utf-8")

            with it("should report the drawing as unreadable, with what the render said"):
                gaps = [(gap.kind, gap.file, gap.is_alignable) for gap in self.alignment.diagnose().gaps if gap.file == DRAWING]
                expect(gaps).to(equal([("unreadable_format", DRAWING, False)]))

        with context("whose story has scenarios in a story test nothing links, and whose markdown links a heading of a model no practice reads"):
            with before.each:
                self.session.practice("stories").guidance.fidelities.called("scenarios").session_output.choose_format("markdown", True)
                (self.project / STORY_TEST).parent.mkdir(parents=True)
                (self.project / STORY_TEST).write_text(STORY_TEST_TEXT, encoding="utf-8")
                (self.project / ".context" / "domain-model.md").write_text("# Domain Model\n\n## Cart\n\nA cart holds books.\n", encoding="utf-8")
                (self.project / STORY_MAP).write_text(STORY_MAP_TEXT + "\nThe cart is the [Cart](domain-model.md#cart).\n", encoding="utf-8")
                self.gaps = self.alignment.diagnose().gaps

            with it("should report the edge from the story to its scenario as one no callout shows"):
                unshown = [gap.message for gap in self.gaps if gap.kind == "edge_without_callout"]
                expect(unshown).to(equal([f"{STORY_MAP}: the graph joins Story 'Remove Cart Line' to Scenario 'Remove the only line' in {STORY_TEST} (scenarios), but no callout on either opens the other's file."]))

            with it("should report the link to the model as a callout no edge matches"):
                unmatched = [(gap.file, "the callout 'Cart' opens .context/domain-model.md" in gap.message) for gap in self.gaps if gap.kind == "callout_without_edge"]
                expect(unmatched).to(equal([(STORY_MAP, True)]))

        with context("whose markdown links a heading its target does not hold"):
            with before.each:
                (self.project / ".context" / "domain-model.md").write_text("# Domain Model\n", encoding="utf-8")
                (self.project / STORY_MAP).write_text(STORY_MAP_TEXT + BROKEN_LINK, encoding="utf-8")

            with it("should report the callout that opens nothing"):
                gaps = [gap for gap in self.alignment.diagnose().gaps if gap.kind == "callout_target_missing"]
                expect([(gap.file, "has no heading #cart-that-is-not-there" in gap.message) for gap in gaps]).to(equal([(STORY_MAP, True)]))


# The person's answer (2026-11-20): every render ends in a saved file, so an alignment renders code formats too.
with description("a session's domain model with its markdown and Python chosen") as self:
    with before.each:
        self.home = ExampleHome()
        self.project = _project()
        (self.project / DOMAIN_MODEL).write_text(DOMAIN_MODEL_TEXT, encoding="utf-8")
        Sessions(self.project).switch("fill-cart", self.project)
        self.session = Sessions(self.project).current()
        for practice in self.session.own_practices.values():
            practice.enable(practice.name == "ddd")
        self.session.practice("ddd").guidance.fidelities.called("model").session_output.choose_format("python", True)
        self.alignment = SessionAlignment(self.session)

    with after.each:
        self.home.close()

    with context("with only the markdown written"):
        with it("should report the Python as missing, aligned from the markdown"):
            gaps = [gap for gap in self.alignment.diagnose().gaps if gap.format == "python"]
            expect([(gap.kind, gap.source, gap.is_alignable) for gap in gaps]).to(equal([("missing_file", DOMAIN_MODEL, True)]))

        with context("that is aligned"):
            with before.each:
                self.result = self.alignment.align()

            with it("should save a Python file for each aggregate where the fidelity declares it"):
                expect([(done.file, done.source) for done in self.result.aligned]).to(equal([(CART_CODE, DOMAIN_MODEL), (ORDER_CODE, DOMAIN_MODEL)]))

            with it("should write the aggregate's class into its file"):
                expect((self.project / CART_CODE).read_text(encoding="utf-8")).to(contain("class Cart"))

            with it("should leave no Python gap"):
                expect([gap.message for gap in self.result.diagnosis.gaps if gap.format == "python"]).to(be_empty)


with description("a session's formats diagnosed and aligned through the cdd server") as self:
    with before.all:
        self.server = SpecServer(TOOLSETS)
        self.server.start()
        self.project = _project()
        self.chat = SpecChat(self.server, self.project)
        self.chat.answer("sessions.switch", name="fill-cart")
        self.session_file = ".sessions/fill-cart/session.json"
        for format in ("drawio", "whiteboard"):
            self.chat.answer("fidelity-session-output.choose_format", session=self.session_file, practice="stories", fidelity="story_map", format=format, is_chosen=True)

    with after.all:
        self.server.stop()

    with context("with only the markdown written"):
        with it("should answer a page the missing drawing and whiteboard"):
            diagnosis = self.chat.answer("session.diagnose_alignment", session=self.session_file)
            missing = [(gap["kind"], gap["file"]) for gap in diagnosis["gaps"] if gap["fidelity"] == "stories-story-map"]
            expect(missing).to(equal([("missing_file", DRAWING), ("missing_file", BOARD)]))

        with context("that a page aligns"):
            with it("should answer the files rendered"):
                result = self.chat.answer("session.align_formats", session=self.session_file)
                expect([done["file"] for done in result["aligned"]]).to(equal([DRAWING, BOARD]))
