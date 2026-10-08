"""Master, working copy, and graph cache staleness, with the dates compared."""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from app.host import dispatch
from graph import CodeQLGraph, QueryFailure


def _stamp(path: Path, seconds: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")
    nanos = seconds * 1_000_000_000
    os.utime(path, ns=(nanos, nanos))


with description("database staleness"):
    with context("with a working copy newer than the master and the code newer than both"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp())
            self.source = Path(tempfile.mkdtemp())
            _stamp(self.source / "account.ts", 1_700_000_900)
            self.graph = CodeQLGraph()
            self.graph._bind(str(self.source), {"stories": str(self.source)}, database=str(self.folder))
            _stamp(self.graph._master("stories") / "codeql-database.yml", 1_700_000_100)
            _stamp(self.graph._working_copy("stories") / "codeql-database.yml", 1_700_000_200)
            _stamp(self.graph._snapshot_path(), 1_700_000_050)

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)
            shutil.rmtree(self.source, ignore_errors=True)

        with it("should mark the master older than the working copy and the code"):
            master = self.graph.master_stale
            expect(master["older_than_worktree"]["older"]).to(equal(True))
            expect(master["older_than_worktree"]["dates"]["master"]).to(contain("2023-11-14"))
            expect(master["older_than_worktree"]["dates"]["worktree"]).to(contain("2023-11-14"))
            expect(master["older_than_code"]["older"]).to(equal(True))
            expect(master["older_than_code"]["dates"]["code"]).to(contain("2023-11-14T22:28:20"))

        with it("should mark the working copy older than the code and current against the master"):
            worktree = self.graph.worktree_stale
            expect(worktree["older_than_code"]["older"]).to(equal(True))
            expect(worktree["older_than_code"]["dates"]["worktree"]).to(contain("T22:16:40"))
            expect(worktree["older_than_master"]["older"]).to(equal(False))
            expect(worktree["older_than_master"]["dates"]["master"]).to(contain("T22:15:00"))

        with it("should mark the graph cache older than the working copy, the master, and the code"):
            cache = self.graph.graph_cache_stale
            expect(cache["older_than_worktree"]["older"]).to(equal(True))
            expect(cache["older_than_worktree"]["dates"]["graph_cache"]).to(contain("T22:14:10"))
            expect(cache["older_than_master"]["older"]).to(equal(True))
            expect(cache["older_than_code"]["older"]).to(equal(True))
            expect(cache["older_than_code"]["dates"]["code"]).to(contain("T22:28:20"))

        with it("should list every compared date"):
            listed = self.graph.dates
            expect(listed["graph_cache"]).to(contain("T22:14:10"))
            expect(listed["practices"][0]["practice"]).to(equal("stories"))
            expect(listed["practices"][0]["master"]).to(contain("T22:15:00"))
            expect(listed["practices"][0]["worktree"]).to(contain("T22:16:40"))
            expect(listed["practices"][0]["code"]).to(contain("T22:28:20"))

        with it("should return the same report from the host"):
            response = dispatch(
                {
                    "operation": "staleness",
                    "folder": str(self.source),
                    "practices": {"stories": str(self.source)},
                    "database": str(self.folder),
                }
            )
            expect(response["ok"]).to(equal(True))
            expect(response["result"]["master_stale"]["older_than_worktree"]["older"]).to(equal(True))
            expect(response["result"]["dates"]["practices"][0]["code"]).to(contain("T22:28:20"))

    with context("with a loaded graph and a cache older than the code"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp())
            self.source = Path(tempfile.mkdtemp())
            _stamp(self.source / "account.ts", 1_700_000_900)
            self.graph = CodeQLGraph()
            self.graph._bind(str(self.source), {"stories": str(self.source)}, database=str(self.folder))
            self.graph._query_rows = [{"nodes": [], "edges": [], "rules": []}]

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)
            shutil.rmtree(self.source, ignore_errors=True)

        with it("should write the graph cache when asked"):
            message = self.graph.serialize_graph_cache()
            expect(message).to(contain("Serialized the graph cache"))
            saved = json.loads(self.graph._snapshot_path().read_text(encoding="utf-8"))
            expect(saved["batches"]).to(equal(self.graph._query_rows))
            expect(self.graph.graph_cache_stale["older_than_code"]["older"]).to(equal(False))

        with it("should refuse to serialize when nothing is loaded"):
            self.graph._query_rows = []
            try:
                self.graph.serialize_graph_cache()
            except QueryFailure as error:
                expect(str(error)).to(contain("Load a graph before serializing"))
            else:
                raise AssertionError("serialize_graph_cache should fail when the graph is empty")
