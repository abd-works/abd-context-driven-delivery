"""BDD spec — a session's violation history: the graph hits each validate found, how its judge judged them, and which a
later validate no longer finds."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, have_len
from mamba import after, before, context, description, it

from harness.graph.location import Location
from harness.graph.violation import FoundBy, FoundOn, Violation
from space.repo.mock_repo import MockGit
from space.session.violation_history import ViolationHistory

_FIRST = "clean-engineering-code-20261116T075749.md"
_SECOND = "clean-engineering-code-20261116T163159.md"
_THIRD = "clean-engineering-code-20261116T174226.md"
_GRAPH = "harness/graph/graph.py"
_TICKET = "space/kanban/ticket.py"
# A report as Validate saves it: a rule's heading, where its text is kept, and its graph hits.
_SAVED_REPORT = """# Graph rule validation

## Rules

### `keep-classes-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:330](clean_engineering.md#L330)

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\\dev\\cdd\\harness\\graph\\graph.py#L40): OoadClass `Graph`: Class 'Graph' has 61 operations.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\\dev\\cdd\\space\\kanban\\ticket.py#L12): OoadClass `Ticket`: Class 'Ticket' has 40 operations.

### `limit-operation-parameters`

Rule text: [clean_engineering/clean_engineering.md:322](clean_engineering.md#L322)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\\dev\\cdd\\space\\kanban\\ticket.py#L90): Operation `move_to`: takes 5 parameters.
"""
# The judgment the validating agent appends: a graph hit it upholds, a finding of its own, and a hit it calls noise.
_JUDGMENT = """
## Judgment — `harness/graph/graph.py`

### `keep-classes-single-responsibility` — Fail
- graph.py:40 `Graph`: loads, saves, and filters the graph, three reasons to change.
- graph.py:200 `GraphScope`: holds the folder and decides what a load reads.

## Graph hits judged noise

| File:line | Rule | Why it is noise |
|---|---|---|
| space/kanban/ticket.py:90 | limit-operation-parameters | A creation factory taking the fields it builds. |
"""


def _hit(rule: str, place: tuple[str, int], node: str) -> Violation:
    """A graph hit of rule at a file and line, on the class or operation called node."""
    file, line = place
    return Violation(FoundBy(rule, "clean_engineering", FoundOn(f"node:{node}", f"OoadClass `{node}`")), f"{node} breaks {rule}.", Location(file, line))


class _Session:
    """A session's folder with its reports folder, in a checkout on a commit."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-history-"))
        held = MockGit(self.root)
        held.make_clone()
        self.checkout = held.serve(self.root)
        self.folder = self.root / ".sessions" / "pet-visits"
        self.reports = self.folder / "validation-reports"
        self.reports.mkdir(parents=True)
        self.history = ViolationHistory(self.folder / "violation-history.jsonl", self.checkout)

    def recorded(self, name: str, hits: list[Violation], scope: list[str] | None = None) -> Path:
        report = self.reports / name
        report.write_text("# Graph rule validation\n", encoding="utf-8")
        self.history.record(report, hits, scope or [])
        return report

    def events(self, event: str, run: str = "") -> list[dict]:
        return [line for line in self.history.events if line["event"] == event and (not run or line["run"] == run)]

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


with description("a session's violation history") as self:
    with before.each:
        self.session = _Session()

    with after.each:
        self.session.close()

    with context("with a validate run recorded"):
        with before.each:
            self.session.recorded(_FIRST, [_hit("keep-classes-single-responsibility", (_GRAPH, 40), "Graph")])

        with it("should record each graph hit the run found, with its rule, file, line, node, and message"):
            found = self.session.events("found")
            expect([(line["rule"], line["file"], line["line"], line["node"], line["message"]) for line in found]).to(
                equal([("keep-classes-single-responsibility", _GRAPH, 40, "Graph", "Graph breaks keep-classes-single-responsibility.")])
            )

        with it("should name the run, its fidelity, its session, and when it ran on each line"):
            found = self.session.events("found")[0]
            expect((found["run"], found["fidelity"], found["session"], found["at"])).to(
                equal((_FIRST, "clean-engineering-code", "pet-visits", "2026-11-16T07:57:49Z"))
            )

        with it("should stamp each line with the commit the session's checkout has checked out"):
            expect(self.session.events("found")[0]["commit"]).to(equal(self.session.checkout.current_commit[:7]))

        with it("should record the run itself with how many hits it found"):
            expect(self.session.events("run")[0]["hits"]).to(equal(1))

        with it("should keep the history as one JSON object a line"):
            lines = self.session.history.file.read_text(encoding="utf-8").splitlines()
            expect([json.loads(line)["event"] for line in lines]).to(equal(["run", "found"]))

        with context("with a later run of the same fidelity that no longer finds the hit"):
            with before.each:
                self.session.recorded(_SECOND, [])

            with it("should record the hit fixed, naming the run it was last found in and the commit that fixed it"):
                fixed = self.session.events("fixed")
                expect([(line["rule"], line["file"], line["node"], line["last_found_in"], line["fixed_in"]) for line in fixed]).to(
                    equal([("keep-classes-single-responsibility", _GRAPH, "Graph", _FIRST, self.session.checkout.current_commit[:7])])
                )

        # An edit above a hit moves it down the file without fixing it.
        with context("with a later run that finds the hit on the same node at another line"):
            with before.each:
                self.session.recorded(_SECOND, [_hit("keep-classes-single-responsibility", (_GRAPH, 57), "Graph")])

            with it("should not record the hit fixed"):
                expect(self.session.events("fixed")).to(have_len(0))

        # A validate of a few files says nothing of the hits in the files it did not check.
        with context("with a later run that checked other files only"):
            with before.each:
                self.session.recorded(_SECOND, [], ["space/kanban"])

            with it("should not record a hit in a file it did not check fixed"):
                expect(self.session.events("fixed")).to(have_len(0))

        with context("with a later run of another fidelity that does not find the hit"):
            with before.each:
                self.session.recorded("clean-engineering-model-20261116T163159.md", [])

            with it("should not record the hit fixed"):
                expect(self.session.events("fixed")).to(have_len(0))

    # The judge appends its judgment after Validate saves the report, so the next run of the fidelity folds it in.
    with context("with a judgment appended to a run's report before the next run of its fidelity"):
        with before.each:
            hits = [
                _hit("keep-classes-single-responsibility", (_GRAPH, 40), "Graph"),
                _hit("limit-operation-parameters", (_TICKET, 90), "move_to"),
            ]
            report = self.session.recorded(_FIRST, hits)
            report.write_text(report.read_text(encoding="utf-8") + _JUDGMENT, encoding="utf-8")
            self.session.recorded(_SECOND, hits)
            self.judged = self.session.events("judged")

        with it("should record a finding that stands on a graph hit as matching it"):
            upheld = [line for line in self.judged if line["verdict"] == "stands" and line["node"] == "Graph"]
            expect([(line["rule"], line["file"], line["line"], line["matched"], line["run"]) for line in upheld]).to(
                equal([("keep-classes-single-responsibility", _GRAPH, 40, True, _FIRST)])
            )

        with it("should record a finding of the judge's own as matching no graph hit"):
            own = [line for line in self.judged if line["node"] == "GraphScope"]
            expect([(line["verdict"], line["line"], line["matched"]) for line in own]).to(equal([("stands", 200, False)]))

        with it("should keep the finding's text as its reason"):
            own = next(line for line in self.judged if line["node"] == "GraphScope")
            expect(own["reason"]).to(contain("decides what a load reads"))

        with it("should record a row of the noise table as noise on the hit it names"):
            noise = [line for line in self.judged if line["verdict"] == "noise"]
            expect([(line["rule"], line["file"], line["line"], line["node"], line["matched"]) for line in noise]).to(
                equal([("limit-operation-parameters", _TICKET, 90, "move_to", True)])
            )

        with context("with a third run of the fidelity"):
            with before.each:
                self.session.recorded(_THIRD, [])

            with it("should fold the earlier run's judgment in only once"):
                expect([line for line in self.session.events("judged") if line["run"] == _FIRST]).to(have_len(3))

    with context("that is rebuilt from its saved reports alone"):
        with before.each:
            (self.session.reports / _FIRST).write_text(_SAVED_REPORT + _JUDGMENT, encoding="utf-8")
            (self.session.reports / _SECOND).write_text(_SAVED_REPORT.split("### `limit-operation-parameters`")[0], encoding="utf-8")
            self.session.history.rebuild(sorted(self.session.reports.glob("*.md")), {_FIRST: "da77357"})

        with it("should record each hit the reports list, with its file, line, and node"):
            found = self.session.events("found", _FIRST)
            expect([(line["rule"], line["file"], line["line"], line["node"]) for line in found]).to(equal([
                ("keep-classes-single-responsibility", _GRAPH, 40, "Graph"),
                ("keep-classes-single-responsibility", _TICKET, 12, "Ticket"),
                ("limit-operation-parameters", _TICKET, 90, "move_to"),
            ]))

        with it("should keep the hit's message without the node it names"):
            expect(self.session.events("found", _FIRST)[0]["message"]).to(equal("Class 'Graph' has 61 operations."))

        with it("should stamp each run with the commit given for its report, and none for a report given none"):
            expect([line["commit"] for line in self.session.events("run")]).to(equal(["da77357", ""]))

        with it("should record the hits a later report no longer lists fixed"):
            expect([(line["rule"], line["node"], line["last_found_in"]) for line in self.session.events("fixed")]).to(
                equal([("limit-operation-parameters", "move_to", _FIRST)])
            )

        with it("should fold in each report's judgment"):
            expect(sorted(line["verdict"] for line in self.session.events("judged", _FIRST))).to(equal(["noise", "stands", "stands"]))

        with it("should write the history again rather than add to it"):
            self.session.history.rebuild(sorted(self.session.reports.glob("*.md")), {})
            expect(self.session.events("run")).to(have_len(2))

    with context("that is kept in a folder git does not know"):
        with before.each:
            folder = Path(tempfile.mkdtemp(prefix="cdd-history-loose-"))
            self.loose = folder
            history = ViolationHistory(folder / "violation-history.jsonl", MockGit(folder).serve(folder))
            (folder / _FIRST).write_text("# Graph rule validation\n", encoding="utf-8")
            history.record(folder / _FIRST, [_hit("keep-classes-single-responsibility", (_GRAPH, 40), "Graph")], [])
            self.loose_events = history.events

        with after.each:
            shutil.rmtree(self.loose, ignore_errors=True)

        with it("should record each run at no commit"):
            expect({line["commit"] for line in self.loose_events}).to(equal({""}))
