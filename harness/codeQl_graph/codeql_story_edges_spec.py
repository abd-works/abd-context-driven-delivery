"""Story edge queries, then the serialized graph those rows build."""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, query_pack

_SAMPLE = _HERE / "examples" / "input"
_DATABASE = _SAMPLE / ".codeql" / "clean_engineering" / "typescript-working-copy"
_PACK = query_pack("stories", "typescript") / "edges"
_NODES = query_pack("stories", "typescript") / "nodes"
_CLASSES = query_pack("clean_engineering", "typescript") / "nodes"


def query_rows(rows: dict, name: str) -> list:
    path = str(_PACK / name)
    return rows[path]


def node_rows(rows: dict, folder: Path, name: str) -> list:
    return rows[str(folder / name)]


with description("story relationship queries"):
    with context("run on the account credentials working copy"):
        with before.all:
            self.graph = CodeQLGraph()
            self.rows = self.graph.run_queries(
                [
                    str(_NODES / "steps.ql"),
                    str(_NODES / "examples.ql"),
                    str(_CLASSES / "operations.ql"),
                    str(_CLASSES / "classes.ql"),
                    str(_PACK / "step-invokes-operations.ql"),
                    str(_PACK / "step-observes-examples.ql"),
                    str(_PACK / "example-demonstrates-class.ql"),
                ],
                _DATABASE,
                reuse=False,
            )

        with it("should return invokes to operations"):
            kinds = {row[2] for row in query_rows(self.rows, "step-invokes-operations.ql")}
            expect(kinds).to(equal({"invokes"}))
            expect(json.dumps(query_rows(self.rows, "step-invokes-operations.ql"))).to(contain("register"))

        with it("should return observes to examples"):
            kinds = {row[2] for row in query_rows(self.rows, "step-observes-examples.ql")}
            expect(kinds).to(equal({"observes"}))
            expect(json.dumps(query_rows(self.rows, "step-observes-examples.ql"))).to(contain("unverifiedAccountCredentials"))

        with it("should return demonstrates to classes"):
            kinds = {row[2] for row in query_rows(self.rows, "example-demonstrates-class.ql")}
            expect(kinds).to(equal({"demonstrates"}))
            expect(json.dumps(query_rows(self.rows, "example-demonstrates-class.ql"))).to(contain("AccountCredentials"))

        with it("should leave scopes out of the query results"):
            packed = json.dumps(self.rows)
            expect("scopes" in packed).to(equal(False))

    with context("with those rows written into the serialized graph"):
        with before.all:
            self.graph = CodeQLGraph()
            self.rows = self.graph.run_queries(
                [
                    str(_NODES / "steps.ql"),
                    str(_NODES / "examples.ql"),
                    str(_CLASSES / "operations.ql"),
                    str(_CLASSES / "classes.ql"),
                    str(_PACK / "step-invokes-operations.ql"),
                    str(_PACK / "step-observes-examples.ql"),
                    str(_PACK / "example-demonstrates-class.ql"),
                ],
                _DATABASE,
                reuse=True,
            )
            self.stories = self.graph.practice("stories")
            self.clean = self.graph.practice("clean_engineering")
            self.stories.graph = self.graph
            self.clean.graph = self.graph
            self.stories.source_root = str(_SAMPLE)
            self.clean.source_root = str(_SAMPLE)
            for practice, folder, names in (
                (self.stories, _NODES, ["steps.ql", "examples.ql"]),
                (self.clean, _CLASSES, ["operations.ql", "classes.ql"]),
            ):
                for name in names:
                    practice.apply_nodes(node_rows(self.rows, folder, name))
            self.stories.apply_edges(query_rows(self.rows, "step-invokes-operations.ql"))
            self.stories.apply_edges(query_rows(self.rows, "step-observes-examples.ql"))
            self.stories.apply_edges(query_rows(self.rows, "example-demonstrates-class.ql"))
            for node in list(self.stories.by_id.values()):
                if node.type == "Step":
                    node.populate()
            self.stream = json.dumps([node.serialize() for node in self.stories.by_id.values() if node.type == "Step"])
            self.steps = json.loads(self.stream)

        with it("should put register under invokes on the registering step"):
            step = next(item for item in self.steps if item["name"] == "when the User registers already-registered account credentials")
            invokes = next(child for child in step["children"] if child["name"] == "invokes")
            expect([child["name"] for child in invokes["children"]]).to(contain("register"))

        with it("should put the example under observes on the valid credentials step"):
            step = next(item for item in self.steps if item["name"] == "when the User enters valid account credentials")
            observes = next(child for child in step["children"] if child["name"] == "observes")
            expect([child["name"] for child in observes["children"]]).to(contain("unverifiedAccountCredentials"))

        with it("should put the class under demonstrates on the observed example"):
            step = next(item for item in self.steps if item["name"] == "when the User enters valid account credentials")
            observes = next(child for child in step["children"] if child["name"] == "observes")
            example = next(child for child in observes["children"] if child["name"] == "unverifiedAccountCredentials")
            demonstrates = next(child for child in example["children"] if child["name"] == "demonstrates")
            expect([child["name"] for child in demonstrates["children"]]).to(contain("AccountCredentials"))

        with it("should leave scopes out of the serialized steps"):
            expect("scopes" in self.stream).to(equal(False))
