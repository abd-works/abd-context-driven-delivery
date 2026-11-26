"""The test tiers a session records for each module: which tiers the module's tests use and the test tool of each,
kept in its session.json."""
import json

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a published session tool makes its session with
from harness.agent_tools.agent_tools import ToolsetReference
from space.session import Session, Sessions
from space.session.session_record import MisshapenTestTiersError
from space.session.spec_support.throwaway_project import ThrowawayProject
from space.session.test_tiers import UnknownTestTierError


with description("the test tiers a session records for its modules") as self:
    with before.each:
        self.project = ThrowawayProject()
        folder = self.project.root / ".sessions" / "refund-order"
        folder.mkdir(parents=True)
        self.file = folder / "session.json"
        self.file.write_text(json.dumps({"name": "refund-order", "title": "Refund an order"}), encoding="utf-8")
        self.session = Sessions(self.project.root).named("refund-order")

    with after.each:
        self.project.close()

    with context("in a session.json that holds none"):
        with it("should read as no tiers chosen yet"):
            expect(self.session.test_tiers.recorded).to(equal({}))

        with it("should read a module as using no tier yet"):
            expect(self.session.test_tiers.of("space/kanban")).to(equal({}))

        with it("should leave the file without a record when something else is saved"):
            self.session.record.update(lambda fields: setattr(fields, "title", "Refund in full"), "title")
            expect("test_tiers" in json.loads(self.file.read_text(encoding="utf-8"))).to(equal(False))

    with context("with the unit and server tiers recorded for a module"):
        with before.each:
            self.session.test_tiers.record("space/kanban", {"unit": "mamba", "server": "mamba"})
            self.saved = json.loads(self.file.read_text(encoding="utf-8"))

        with it("should keep, in session.json, each module's tiers with the test tool of each"):
            expect(self.saved["test_tiers"]).to(equal({"space/kanban": {"unit": "mamba", "server": "mamba"}}))

        with it("should keep the fields the file already held"):
            expect(self.saved["title"]).to(equal("Refund an order"))

        with it("should read the module's tiers back"):
            expect(self.session.test_tiers.of("space/kanban")).to(equal({"unit": "mamba", "server": "mamba"}))

        with it("should read the tiers from the file in another process's sessions"):
            expect(Sessions(self.project.root).named("refund-order").test_tiers.recorded).to(equal({"space/kanban": {"unit": "mamba", "server": "mamba"}}))

        with context("then the web tier recorded for the same module, and the unit tier for another"):
            with before.each:
                self.session.test_tiers.record("space\\kanban/", {"web": "playwright"})
                self.session.test_tiers.record("harness/graph", {"unit": "mamba"})

            with it("should add the tier to the module's own, under the module's one path"):
                expect(self.session.test_tiers.of("space/kanban")).to(equal({"unit": "mamba", "server": "mamba", "web": "playwright"}))

            with it("should hold each module apart"):
                expect(sorted(self.session.test_tiers.recorded)).to(equal(["harness/graph", "space/kanban"]))

        with context("then another tool recorded for a tier it holds"):
            with it("should keep the tool recorded last"):
                self.session.test_tiers.record("space/kanban", {"unit": "pytest"})
                expect(self.session.test_tiers.of("space/kanban")["unit"]).to(equal("pytest"))

    with context("asked to record a tier that is none of unit, server and web"):
        with it("should refuse it, naming the tier and the tiers there are"):
            expect(lambda: self.session.test_tiers.record("space/kanban", {"heavy": "mamba"})).to(
                raise_error(UnknownTestTierError, contain("heavy", "unit, server, web"))
            )

        with it("should record nothing"):
            try:
                self.session.test_tiers.record("space/kanban", {"heavy": "mamba"})
            except UnknownTestTierError:
                pass
            expect(self.session.test_tiers.recorded).to(equal({}))

    with context("in a session.json whose record is wrongly shaped"):
        with it("should refuse a record that is a list, naming the record"):
            self.file.write_text(json.dumps({"name": "refund-order", "test_tiers": ["unit"]}), encoding="utf-8")
            session = Sessions(self.project.root).named("refund-order")
            expect(lambda: session.test_tiers.recorded).to(raise_error(MisshapenTestTiersError, contain("test_tiers", "['unit']")))

        with it("should refuse a module whose tiers are a list, not a tool for each tier"):
            self.file.write_text(json.dumps({"name": "refund-order", "test_tiers": {"space/kanban": ["unit", "server"]}}), encoding="utf-8")
            session = Sessions(self.project.root).named("refund-order")
            expect(lambda: session.test_tiers.of("space/kanban")).to(raise_error(MisshapenTestTiersError))

        with it("should refuse a tier it does not know"):
            self.file.write_text(json.dumps({"name": "refund-order", "test_tiers": {"space/kanban": {"heavy": "mamba"}}}), encoding="utf-8")
            session = Sessions(self.project.root).named("refund-order")
            expect(lambda: session.test_tiers.recorded).to(raise_error(MisshapenTestTiersError, contain("heavy")))

    with context("recorded through the session's tool"):
        with it("should record the tier and answer the module's tiers"):
            answered = self.session.record_test_tier("space/kanban", "web", "playwright")
            expect((answered, self.session.test_tiers.of("space/kanban"))).to(equal(({"space/kanban": {"web": "playwright"}}, {"web": "playwright"})))

    with context("recorded by a call to the published tool, naming the session's session.json and the tool's own arguments"):
        with before.each:
            tool = ToolsetReference.of(Session).made().tools["record_test_tier"]
            arguments = {"session": ".sessions/refund-order/session.json", "module": "space/kanban", "tier": "server", "tool": "mamba"}
            self.answered = tool.invoke(arguments, project=self.project.root)

        with it("should keep the tier in that session's session.json"):
            expect(json.loads(self.file.read_text(encoding="utf-8"))["test_tiers"]).to(equal({"space/kanban": {"server": "mamba"}}))

        with it("should answer the module's tiers"):
            expect(self.answered).to(equal({"space/kanban": {"server": "mamba"}}))
