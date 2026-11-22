"""A session's record: its session.json read into typed fields, an older file upgraded as it is read, and the fields an
owner outside the session keeps there changed by that owner alone."""
import json

from expects import equal, expect, raise_error
from mamba import after, before, context, description, it

from space.session import Sessions
from space.session.session_record import SessionFieldOwnedError
from space.session.spec_support.throwaway_project import ThrowawayProject

# Seed: a session.json as a server before the typed record wrote it: a practice's on-switch and formats under
# ``practices``, its roots and file names apart under ``outputs``, and the checkout's folder it never read.
_OLD_SHAPE = {
    "name": "refund-order",
    "title": "Refund an order",
    "stage": "Specification",
    "stage_mark": "done",
    "repo_path": "C:/somewhere",
    "practices": {"stories": {"enabled": False, "formats": {"story_map": "drawio", "scenarios": ["markdown", "python"]}}},
    "outputs": {"stories": {"root": "docs/stories", "scenarios": {"roots": ["story_tests/refund", "story_tests/returns"]}, "story_map": {"root": ".context", "markdown": "refund-map.md"}}},
}


with description("a session's record") as self:
    with before.each:
        self.project = ThrowawayProject()
        folder = self.project.root / ".sessions" / "refund-order"
        folder.mkdir(parents=True)
        self.file = folder / "session.json"
        self.file.write_text(json.dumps(_OLD_SHAPE), encoding="utf-8")
        self.session = Sessions(self.project.root).named("refund-order")

    with after.each:
        self.project.close()

    with context("kept in the shape an older server wrote"):
        with it("should read the practice as turned off"):
            expect(self.session.record.fields.practice("stories").enabled).to(equal(False))

        with it("should read the practice's chosen root"):
            expect(self.session.record.fields.practice("stories").root).to(equal("docs/stories"))

        with it("should read a format kept as one word as a list of one"):
            expect(self.session.record.fields.practice("stories").fidelity("story_map").formats).to(equal(["drawio"]))

        with it("should read a fidelity's one root as its roots"):
            expect(self.session.record.fields.practice("stories").fidelity("story_map").roots).to(equal([".context"]))

        with it("should read a fidelity's several roots"):
            expect(self.session.record.fields.practice("stories").fidelity("scenarios").roots).to(equal(["story_tests/refund", "story_tests/returns"]))

        with it("should read the file name chosen for a format"):
            expect(self.session.record.fields.practice("stories").fidelity("story_map").file_names).to(equal({"markdown": "refund-map.md"}))

        with context("that is saved again"):
            with before.each:
                self.session.record.update(lambda fields: setattr(fields, "title", "Refund an order in full"), "title")
                self.saved = json.loads(self.file.read_text(encoding="utf-8"))

            with it("should keep each practice's state in one entry"):
                expect(self.saved["practices"]["stories"]).to(equal({
                    "enabled": False,
                    "root": "docs/stories",
                    "fidelities": {
                        "story_map": {"formats": ["drawio"], "roots": [".context"], "file_names": {"markdown": "refund-map.md"}},
                        "scenarios": {"formats": ["markdown", "python"], "roots": ["story_tests/refund", "story_tests/returns"]},
                    },
                }))

            with it("should keep no outputs and no repository path"):
                expect([key in self.saved for key in ("outputs", "repo_path")]).to(equal([False, False]))

            with it("should keep the board's stage and mark where they were"):
                expect((self.saved["stage"], self.saved["stage_mark"])).to(equal(("Specification", "done")))

    with context("whose board fields the board changes"):
        with before.each:
            self.session.record.extra("ticket").save(stage="Discovery", stage_mark="")

        with it("should keep them at the top of session.json"):
            expect(json.loads(self.file.read_text(encoding="utf-8"))["stage"]).to(equal("Discovery"))

        with it("should refuse the board a field of the session's own"):
            expect(lambda: self.session.record.extra("ticket").save(title="Taken")).to(raise_error(SessionFieldOwnedError))

    with context("whose checkout records the chat a person assigned"):
        with before.each:
            self.session.checkout.assign_chat("picked")

        with it("should answer that chat"):
            expect(self.session.checkout.assigned_chat).to(equal("picked"))

        with it("should keep it in session.json as chat"):
            expect(json.loads(self.file.read_text(encoding="utf-8"))["chat"]).to(equal("picked"))
