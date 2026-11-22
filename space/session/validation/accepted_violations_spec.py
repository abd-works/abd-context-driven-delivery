"""BDD spec - the violations a person accepts as they are, kept in a project's ``.context/violations-accepted.json``."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_false, be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.graph.location import Location
from harness.graph.violation import FoundBy, FoundOn, Violation
from space.session.validation.accepted_violations import ACCEPTED_VIOLATIONS_FILE, AcceptedViolations, AcceptedViolationsUnreadable

STORY_MAP = ".context/story-map.md"
STORY_MAP_TEXT = "# Check Out Order\n\n## Payment\n\n- Enter Card Details\n- Handle Payment\n- Confirm Order\n"
ONE_TIME_TASK = "Story 'Handle Payment' reads like a one-time task, not a repeatable behaviour"


def on_node(message: str = ONE_TIME_TASK, node_id: str = "stories:Story:handle-payment", line: int = 6) -> Violation:
    """A graph rule's hit on a story of the map."""
    return Violation(FoundBy("repeatable-behaviour", "stories", FoundOn(node_id, "Story `Handle Payment`")), message, Location(STORY_MAP, line, line))


def judged(message: str = "`Handle Payment`: no source names this story.", line: int | None = 6) -> Violation:
    """A judge's finding on a line of the map, which names no node."""
    return Violation(FoundBy("do-not-invent-requirements"), message, Location(STORY_MAP, line))


with description("a project's accepted violations"):
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        self.map = self.root / STORY_MAP
        self.map.parent.mkdir(parents=True)
        self.map.write_text(STORY_MAP_TEXT, encoding="utf-8")
        self.file = self.root / ".context" / ACCEPTED_VIOLATIONS_FILE
        self.accepted = AcceptedViolations(self.file, [self.root])

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with nothing accepted"):
        with it("should leave every violation open"):
            expect(self.accepted.open_among([on_node(), judged()])).to(equal([on_node(), judged()]))

        with it("should write no file"):
            self.accepted.open_among([on_node()])
            expect(self.file.exists()).to(be_false)

    with context("with a violation on a node accepted"):
        with before.each:
            self.accepted.accept(on_node())
            self.kept = json.loads(self.file.read_text(encoding="utf-8"))["accepted"]

        with it("should keep the rule, the node's id, and the message in the file"):
            expect([(entry["rule"], entry["node_id"], entry["message"]) for entry in self.kept]).to(
                equal([("repeatable-behaviour", "stories:Story:handle-payment", ONE_TIME_TASK)])
            )

        with it("should keep what the node is, its file, and when it was accepted, for a person reading the file"):
            entry = self.kept[0]
            expect((entry["subject"], entry["file"], bool(entry["accepted_at"]))).to(equal(("Story `Handle Payment`", STORY_MAP, True)))

        with it("should leave it out of the open violations"):
            expect(self.accepted.open_among([on_node(), judged()])).to(equal([judged()]))

        with it("should name it among the accepted ones"):
            expect(self.accepted.accepted_among([on_node(), judged()])).to(equal([on_node()]))

        with it("should still leave it out when its node moves to another line"):
            expect(self.accepted.open_among([on_node(line=40)])).to(equal([]))

        with it("should keep it once when it is accepted again"):
            self.accepted.accept(on_node())
            expect(len(json.loads(self.file.read_text(encoding="utf-8"))["accepted"])).to(equal(1))

        with it("should show it again when the finding's message changes"):
            changed = on_node("Story 'Take Payment' reads like a one-time task, not a repeatable behaviour")
            expect(self.accepted.open_among([changed])).to(equal([changed]))

        with it("should show it again when the node's id changes"):
            renamed = on_node(node_id="stories:Story:take-payment")
            expect(self.accepted.open_among([renamed])).to(equal([renamed]))

        with it("should show the same message of another rule"):
            other = Violation(FoundBy("verb-noun-format", "stories", FoundOn("stories:Story:handle-payment")), ONE_TIME_TASK, Location(STORY_MAP, 6))
            expect(self.accepted.open_among([other])).to(equal([other]))

        with context("that is opened again"):
            with before.each:
                self.accepted.reopen(on_node())

            with it("should show it again"):
                expect(self.accepted.open_among([on_node()])).to(equal([on_node()]))

            with it("should keep no acceptance of it in the file"):
                expect(json.loads(self.file.read_text(encoding="utf-8"))["accepted"]).to(equal([]))

    with context("with a judged finding on a line of a file accepted"):
        with before.each:
            self.accepted.accept(judged())
            self.kept = json.loads(self.file.read_text(encoding="utf-8"))["accepted"]

        with it("should keep the rule, the file, and the content of the judged line, and no line number"):
            entry = self.kept[0]
            expect((entry["rule"], entry["file"], entry["content"], "line" in entry)).to(
                equal(("do-not-invent-requirements", STORY_MAP, "- Handle Payment", False))
            )

        with it("should leave it out when the line has moved and the judge words it another way"):
            self.map.write_text("A new opening line.\n" + STORY_MAP_TEXT, encoding="utf-8")
            expect(self.accepted.open_among([judged("no source describes Handle Payment.", line=7)])).to(equal([]))

        with it("should show it again when the judged content changes"):
            self.map.write_text(STORY_MAP_TEXT.replace("Handle Payment", "Take Payment"), encoding="utf-8")
            expect(self.accepted.open_among([judged()])).to(equal([judged()]))

        with it("should show a finding of the same rule on another line"):
            expect(self.accepted.open_among([judged(line=7)])).to(equal([judged(line=7)]))

    with context("with a judged finding that names no line accepted"):
        with before.each:
            self.accepted.accept(judged(line=None))

        with it("should leave out the same message on the same file"):
            expect(self.accepted.open_among([judged(line=None)])).to(equal([]))

        with it("should show another message on that file"):
            other = judged("The map has no actor.", line=None)
            expect(self.accepted.open_among([other])).to(equal([other]))

    with context("whose file is not readable JSON"):
        with before.each:
            self.file.write_text("{ accepted: [", encoding="utf-8")

        with it("should refuse to say which violations are open, naming the file"):
            expect(lambda: self.accepted.open_among([on_node()])).to(raise_error(AcceptedViolationsUnreadable, contain(str(self.file))))

        with it("should refuse to accept a violation, leaving the file as the person wrote it"):
            expect(lambda: self.accepted.accept(on_node())).to(raise_error(AcceptedViolationsUnreadable))
            expect(self.file.read_text(encoding="utf-8")).to(equal("{ accepted: ["))

    with context("whose file lists something that is no acceptance"):
        with before.each:
            self.file.write_text('{"accepted": ["verb-noun-format"]}', encoding="utf-8")

        with it("should refuse to read it, naming the file"):
            expect(lambda: self.accepted.open_among([on_node()])).to(raise_error(AcceptedViolationsUnreadable, contain(str(self.file))))

    with context("asked whether it holds an acceptance"):
        with it("should say no before anything is accepted"):
            expect(self.accepted.holds_any).to(be_false)

        with it("should say yes once a violation is accepted"):
            self.accepted.accept(on_node())
            expect(self.accepted.holds_any).to(be_true)
