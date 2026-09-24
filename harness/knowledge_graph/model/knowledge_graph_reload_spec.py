"""BDD development — reload working copy and repopulate master.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a repo … that has a working copy to reload
"""
from pathlib import Path
import sys
import time

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import before, context, description, it

from practices.clean_engineering.clean_engineering import CleanEngineering  # noqa: F401
from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph


with description("KnowledgeGraph.reload_working_copy"):
    with it("should be marked for mcp skill and agent tool"):
        fn = KnowledgeGraph.reload_working_copy
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(True))

_SLICE = _REPO_ROOT / "harness" / "knowledge_graph" / "examples" / "codeql-slice"
_MASTER = _SLICE / ".codeql" / "python-master"
_WORKING = _SLICE / ".codeql" / "python-working-copy"


with description("a repo"):
    with context("that has been captured as a kg database"):
        with before.each:
            self.export = _SLICE / ".codeql" / "results" / "practice-graph.json"

        with context("with production code and story tests already defined"):
            with before.each:
                self.production = _SLICE / "domain" / "customer" / "customer.py"
                self.story_test = (
                    _SLICE
                    / "stories"
                    / "onboard-a-customer"
                    / "create-customer"
                    / "load-customer"
                    / "load_customer_story.test.ts"
                )

            with context("that has a working copy to reload"):
                with before.all:
                    self.graph = KnowledgeGraph(root=_SLICE)
                    if not (_WORKING / "db-python").is_dir():
                        self.graph.refresh_master()
                    self.started = time.time()
                    self.graph.reload_working_copy()

                with it("should reload the working copy"):
                    expect(
                        (_WORKING / "codeql-database.yml").stat().st_mtime
                        >= self.started
                    ).to(equal(True))

                with it("should populate from the working copy"):
                    names = [
                        node.name
                        for graph in self.graph.practice_graphs
                        for node in graph.nodes.values()
                    ]
                    expect("CustomerRepository" in names).to(equal(True))

                with it("should repopulate the master"):
                    expect(
                        (_MASTER / "codeql-database.yml").stat().st_mtime
                        >= self.started
                    ).to(equal(True))
