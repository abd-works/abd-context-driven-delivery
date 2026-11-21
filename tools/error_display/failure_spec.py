"""Failure: what failed and the context it failed in, the shape every failure is shown in, with the most common causes
of its kind and the command its Fix sends to the chat."""
import json

from expects import be_empty, contain, equal, expect, raise_error, start_with
from mamba import before, describe, it

from tools.error_display.failure import FAILURE_KINDS, Failure, FailureKindUnknownError

OPENING = "Opening src/order.py in the Files app"

with describe(Failure):
    with describe("a failure described"):
        with it("should say what failed"):
            expect(Failure.describe("Kanban did not open: npm install failed", "Opening an app from the health panel").failure).to(equal("Kanban did not open: npm install failed"))

        with it("should say the context it failed in"):
            expect(Failure.describe("Kanban did not open: npm install failed", "Opening an app from the health panel").context).to(equal("Opening an app from the health panel"))

        with it("should list no causes while no kind is named"):
            expect(Failure.describe("Kanban did not open: npm install failed", "Opening an app from the health panel").causes).to(be_empty)

        with it("should still send the chat the failure and its context to fix"):
            expect(Failure.describe("Kanban did not open: npm install failed", "Opening an app from the health panel").fix_command).to(equal('/space-session-debug-session choice=fix details="Failure: Kanban did not open: npm install failed Context: Opening an app from the health panel"'))

    with describe("that is a file the page could not show"):
        with before.each:
            self.failure = Failure.describe("src/order.py did not open: it is not there", OPENING, "file_display")

        with it("should name its kind"):
            expect(self.failure.kind).to(equal("file_display"))

        with it("should list the most common causes of a file that cannot be shown"):
            expect(self.failure.causes[0]).to(start_with("The file was moved, renamed or deleted"))

        with it("should send the chat the debug session command with the fix chosen"):
            expect(self.failure.fix_command).to(start_with("/space-session-debug-session choice=fix details="))

        with it("should send the failure, its context and each cause as the command's details"):
            details = json.loads(self.failure.fix_command.split("details=", 1)[1])
            expect([part in details for part in ("src/order.py did not open: it is not there", OPENING, *self.failure.causes)]).to(equal([True] * (2 + len(self.failure.causes))))

    with describe("that names each kind a page or an action can meet"):
        with it("should offer a link that leads nowhere, a graph view, a render, a generate and the session's roots beside a file"):
            expect([kind.name for kind in FAILURE_KINDS.every]).to(equal(["file_display", "missing_link", "graph_view", "render", "generate", "session_roots"]))

        with it("should list several causes for every kind"):
            expect([len(kind.causes) >= 3 for kind in FAILURE_KINDS.every]).to(equal([True] * 6))

    with describe("that names a kind no failure has"):
        with it("should refuse the kind by name"):
            expect(lambda: Failure.describe("It broke", "Doing it", "weather")).to(raise_error(FailureKindUnknownError, contain("weather")))
