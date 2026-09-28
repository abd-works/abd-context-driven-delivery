"""BDD development — refresh master from codeql-slice.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a repo … that is ready to become the master
"""
from pathlib import Path
import sys

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

_SLICE = _REPO_ROOT / "harness" / "knowledge_graph" / "examples" / "codeql-slice"


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

            with context("that is ready to become the master"):
                with before.all:
                    self.graph = KnowledgeGraph(root=_SLICE)
                    self.graph.refresh_master()
                    self.master = _SLICE / ".codeql" / "python-master"

                with it("should rewrite the master"):
                    expect((self.master / "db-python").is_dir()).to(equal(True))

                with it("should populate the master"):
                    names = [
                        node.name
                        for graph in self.graph.practice_graphs
                        for node in graph.nodes.values()
                    ]
                    expect("CustomerRepository" in names).to(equal(True))

                with it("should copy the master to working copy"):
                    working = _SLICE / ".codeql" / "python-working-copy" / "db-python"
                    expect(working.is_dir()).to(equal(True))

                with it("should not read the master after the copy"):
                    expect((_SLICE / ".codeql" / "python-db").exists()).to(equal(False))
