"""A session's record: its session.json read into typed fields, an older file upgraded as it is read, and the fields an
owner outside the session keeps there changed by that owner alone."""
import json
import threading

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.json_file import JsonFileUnreadable
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

    # Two chats changing one session's record at once each read it, changed it and wrote it with nothing held, so the
    # later write dropped the earlier change. The real processes are in session_record_processes_heavy_spec.py.
    with context("changed by two callers at the same moment, each through its own sessions"):
        with before.each:
            def tag(word):
                Sessions(self.project.root).named("refund-order").add_tag(word)

            callers = [threading.Thread(target=tag, args=(word,)) for word in ("urgent", "billing", "refund", "legal")]
            for caller in callers:
                caller.start()
            for caller in callers:
                caller.join()

        with it("should keep every caller's change"):
            expect(sorted(json.loads(self.file.read_text(encoding="utf-8"))["tags"])).to(equal(["billing", "legal", "refund", "urgent"]))

    with context("changed while another change holds it"):
        with it("should wait for that change, and keep both"):
            def held_change(fields):
                waiting.start()
                fields.title = "Refund in full"

            waiting = threading.Thread(target=lambda: Sessions(self.project.root).named("refund-order").add_tag("urgent"))
            self.session.record.update(held_change, "title")
            waiting.join()
            saved = json.loads(self.file.read_text(encoding="utf-8"))
            expect((saved["title"], saved["tags"])).to(equal(("Refund in full", ["urgent"])))

    with context("whose file a writer killed partway left half written"):
        with before.each:
            self.half = '{"name": "refund-order", "title": "Refund an or'
            self.file.write_text(self.half, encoding="utf-8")

        with it("should refuse a change, naming the file"):
            expect(lambda: self.session.add_tag("urgent")).to(raise_error(JsonFileUnreadable, contain("session.json")))

        with it("should leave the file as it is, never written over as if it were empty"):
            try:
                self.session.add_tag("urgent")
            except JsonFileUnreadable:
                pass
            expect(self.file.read_text(encoding="utf-8")).to(equal(self.half))

    with context("with the text a killed writer staged still beside its file"):
        with it("should change the file itself and keep what it held"):
            self.file.with_name("session.json.4242.1.tmp").write_text('{"name": "refund-or', encoding="utf-8")
            self.session.add_tag("urgent")
            saved = json.loads(self.file.read_text(encoding="utf-8"))
            expect((saved["title"], saved["tags"])).to(equal(("Refund an order", ["urgent"])))

