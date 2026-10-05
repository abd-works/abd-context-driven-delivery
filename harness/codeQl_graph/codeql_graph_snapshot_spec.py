"""A knowledge graph saved beside the working copy."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import after, before, context, description, it

from graph import CodeQLGraph

_SAMPLE = _HERE / "examples" / "input"


with description("a saved knowledge graph"):
    with context("with query packs unchanged since the save"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp())
            self.graph = CodeQLGraph()
            self.graph._bind(str(_SAMPLE), {"stories": str(_SAMPLE)}, database=str(self.folder))
            working = self.graph._working_copy("stories")
            working.mkdir(parents=True)
            (working / "codeql-database.yml").write_text("{}", encoding="utf-8")
            recorded = self.graph._watched_stamp("stories")["queries_ns"]
            payload = {
                "queries_ns": {"stories": recorded},
                "batches": [
                    {
                        "nodes": [
                            [
                                "stories",
                                "steps.ql",
                                [["stories:Step:a.ts:when ready:1", "when ready", "Step", "stories", "a.ts", "1", "2"]],
                            ]
                        ],
                        "edges": [],
                        "rules": [],
                    }
                ],
            }
            path = self.graph._snapshot_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload), encoding="utf-8")

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)

        with it("should load the saved step"):
            message = self.graph.load_working_copy(str(_SAMPLE), {"stories": str(_SAMPLE)}, database=str(self.folder))
            expect(message).to(equal("Loaded the saved knowledge graph."))
            expect(self.graph.practice("stories").by_id["stories:Step:a.ts:when ready:1"].name).to(equal("when ready"))

    with context("with a query pack newer than the save"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp())
            self.graph = CodeQLGraph()
            self.graph._bind(str(_SAMPLE), {"stories": str(_SAMPLE)}, database=str(self.folder))
            path = self.graph._snapshot_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"queries_ns": {"stories": 0}, "batches": [{"nodes": [], "edges": [], "rules": []}]}), encoding="utf-8")

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)

        with it("should treat the saved graph as stale"):
            expect(self.graph._queries_newer_than_graph()).to(equal(True))
