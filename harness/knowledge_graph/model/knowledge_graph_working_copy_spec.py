"""BDD development — update working copy from dirty slice files.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a repo … that has changed… file-type nests
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
from mamba import after, before, context, description, it

from practices.clean_engineering.clean_engineering import CleanEngineering  # noqa: F401
from harness.knowledge_graph.model.codeql import CodeQL
from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph
from harness.knowledge_graph.model.practice_graph import PracticeGraph

_SLICE = _REPO_ROOT / "harness" / "knowledge_graph" / "examples" / "codeql-slice"
_PRODUCTION = _SLICE / "domain" / "customer" / "customer.py"
_STORY_TEST = (
    _SLICE
    / "stories"
    / "onboard-a-customer"
    / "create-customer"
    / "load-customer"
    / "load_customer_story.test.ts"
)
_ORIGINAL_PRODUCTION = _PRODUCTION.read_text(encoding="utf-8")
_ORIGINAL_STORY = _STORY_TEST.read_text(encoding="utf-8")
_MASTER = _SLICE / ".codeql" / "python-master"
_WORKING = _SLICE / ".codeql" / "python-working-copy"


def _restore_slice_files() -> None:
    _PRODUCTION.write_text(_ORIGINAL_PRODUCTION, encoding="utf-8")
    _STORY_TEST.write_text(_ORIGINAL_STORY, encoding="utf-8")


with description("KnowledgeGraph.update_working_copy"):
    with it("should be marked for mcp skill and agent tool"):
        fn = KnowledgeGraph.update_working_copy
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(True))


with description("a repo"):
    with context("that has been captured as a kg database"):
        with before.each:
            self.export = _SLICE / ".codeql" / "results" / "practice-graph.json"

        with context("with production code and story tests already defined"):
            with before.each:
                self.production = _PRODUCTION
                self.story_test = _STORY_TEST

            with context("that has changed story-test and production-code files"):
                with before.all:
                    self.graph = KnowledgeGraph(root=_SLICE)
                    if not (_MASTER / "db-python").is_dir():
                        self.graph.refresh_master()
                        master_graph = self.graph.practice_graphs[0]
                    else:
                        master_graph = PracticeGraph(_SLICE)
                        CodeQL(_SLICE).populate(
                            master_graph,
                            database=_MASTER,
                            results_path=_MASTER / "practice-graph.json",
                        )
                    self.master_kinds = {
                        node.name: type(node).__name__
                        for node in master_graph.nodes.values()
                    }
                    self.master_stamp = (_MASTER / "codeql-database.yml").stat().st_mtime
                    _PRODUCTION.write_text(
                        _ORIGINAL_PRODUCTION + "\n\nclass LoyaltyAccount:\n    pass\n",
                        encoding="utf-8",
                    )
                    _STORY_TEST.write_text(
                        _ORIGINAL_STORY + "\n// dirty\n",
                        encoding="utf-8",
                    )
                    self.started = time.time()
                    self.graph.update_working_copy([_PRODUCTION, _STORY_TEST])

                with after.all:
                    _restore_slice_files()

                with it("should update the working copy from those paths"):
                    expect(
                        (_WORKING / "codeql-database.yml").stat().st_mtime >= self.started
                    ).to(equal(True))

                with it("should keep the same practice-graph hierarchy"):
                    working = self.graph.practice_graphs[0]
                    expect(
                        {
                            node.name: type(node).__name__
                            for node in working.nodes.values()
                            if node.name in self.master_kinds
                        }
                    ).to(equal(self.master_kinds))

                with it("should keep rules on those nodes"):
                    customer = next(
                        node
                        for node in self.graph.practice_graphs[0].nodes.values()
                        if node.name == "Customer"
                    )
                    expect(len(customer.rules.applicable_rule_slugs) > 0).to(equal(True))

                with it("should include story and scenario nodes from the tests"):
                    names = {
                        node.name
                        for node in self.graph.practice_graphs[0].nodes.values()
                    }
                    expect(
                        {"Load Customer", "Load My Paradise customer and store in session"}.issubset(
                            names
                        )
                    ).to(equal(True))

                with it("should include module or class nodes from the production files"):
                    names = [
                        node.name
                        for node in self.graph.practice_graphs[0].nodes.values()
                    ]
                    expect("LoyaltyAccount" in names).to(equal(True))

                with it("should extract onto the working copy"):
                    import zipfile

                    with zipfile.ZipFile(_WORKING / "src.zip") as archive:
                        extracted = b"".join(
                            archive.read(name) for name in archive.namelist()
                        )
                    expect(b"LoyaltyAccount" in extracted).to(equal(True))

                with it("should not rewrite the master"):
                    expect(
                        (_MASTER / "codeql-database.yml").stat().st_mtime
                    ).to(equal(self.master_stamp))

            with context("that has changed a story-test file"):
                with before.all:
                    self.graph = KnowledgeGraph(root=_SLICE)
                    if not (_MASTER / "db-python").is_dir():
                        self.graph.refresh_master()
                    _STORY_TEST.write_text(
                        _ORIGINAL_STORY + "\n// dirty-story\n",
                        encoding="utf-8",
                    )
                    self.graph.update_working_copy([_STORY_TEST])

                with after.all:
                    _restore_slice_files()

                with it("should include story nodes whose location is that file"):
                    files = {
                        getattr(getattr(node, "source", None), "file", "")
                        for node in self.graph.practice_graphs[0].nodes.values()
                        if node.semantic_type() == "Story"
                    }
                    expect(
                        "stories/onboard-a-customer/create-customer/load-customer/load_customer_story.test.ts"
                        in files
                    ).to(equal(True))

                with it("should include scenario nodes whose location is that file"):
                    files = {
                        getattr(getattr(node, "source", None), "file", "")
                        for node in self.graph.practice_graphs[0].nodes.values()
                        if node.semantic_type() == "Scenario"
                    }
                    expect(
                        "stories/onboard-a-customer/create-customer/load-customer/load_customer_story.test.ts"
                        in files
                    ).to(equal(True))

            with context("that has changed a python module file"):
                with before.all:
                    self.graph = KnowledgeGraph(root=_SLICE)
                    if not (_MASTER / "db-python").is_dir():
                        self.graph.refresh_master()
                    _PRODUCTION.write_text(
                        _ORIGINAL_PRODUCTION + "\n\nclass LoyaltyAccount:\n    pass\n",
                        encoding="utf-8",
                    )
                    self.graph.update_working_copy([_PRODUCTION])

                with after.all:
                    _restore_slice_files()

                with it("should include module or class nodes whose location is that file"):
                    files = {
                        getattr(getattr(node, "source", None), "file", "")
                        for node in self.graph.practice_graphs[0].nodes.values()
                        if node.name == "LoyaltyAccount"
                    }
                    expect(
                        any(
                            str(path).replace("\\", "/").endswith("domain/customer/customer.py")
                            for path in files
                        )
                    ).to(equal(True))

                with it("should not treat the file as a story"):
                    story_files = {
                        getattr(getattr(node, "source", None), "file", "")
                        for node in self.graph.practice_graphs[0].nodes.values()
                        if node.semantic_type() == "Story"
                    }
                    expect(
                        any(
                            str(path).replace("\\", "/").endswith("customer.py")
                            for path in story_files
                        )
                    ).to(equal(False))
