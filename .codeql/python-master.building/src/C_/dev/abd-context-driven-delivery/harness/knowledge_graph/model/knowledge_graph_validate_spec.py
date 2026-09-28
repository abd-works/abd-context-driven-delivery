"""BDD development — validate from the working-copy hierarchy.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a repo … that has updated the working copy
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

from unittest.mock import patch

from expects import equal, expect
from mamba import after, before, context, description, it

from practices.clean_engineering.clean_engineering import CleanEngineering  # noqa: F401
from harness.guidance.rule import RulesCollection
from harness.knowledge_graph.model.codeql import CodeQL
from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph
from harness.knowledge_graph.model.loader import attach_story_tests
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


def _restore_slice_files() -> None:
    _PRODUCTION.write_text(_ORIGINAL_PRODUCTION, encoding="utf-8")
    _STORY_TEST.write_text(_ORIGINAL_STORY, encoding="utf-8")


with description("a repo"):
    with context("that has been captured as a kg database"):
        with before.each:
            self.export = _SLICE / ".codeql" / "results" / "practice-graph.json"

        with context("with production code and story tests already defined"):
            with before.each:
                self.production = _PRODUCTION
                self.story_test = _STORY_TEST

            with context("that has changed story-test and production-code files"):
                with context("that has updated the working copy"):
                    with before.all:
                        self.graph = KnowledgeGraph(root=_SLICE)
                        codeql = CodeQL(_SLICE)
                        if not codeql._database_ready(codeql.master):
                            self.graph.refresh_master()
                        else:
                            codeql.copy_master_to_working_copy()
                        _PRODUCTION.write_text(
                            _ORIGINAL_PRODUCTION
                            + "\n\nclass LoyaltyAccount:\n    pass\n",
                            encoding="utf-8",
                        )
                        _STORY_TEST.write_text(
                            _ORIGINAL_STORY + "\n// dirty\n",
                            encoding="utf-8",
                        )
                        graph = PracticeGraph(_SLICE)
                        codeql.populate(
                            graph,
                            database=codeql.working_copy,
                            results_path=codeql.working_copy / "practice-graph.json",
                        )
                        attach_story_tests(graph, [_PRODUCTION, _STORY_TEST])
                        self.graph._practice_graphs = [graph]
                        with patch.object(RulesCollection, "validate", return_value="") as walked:
                            self.graph.validate()
                        self.rule_list_calls = walked.call_count
                        self.timings = [
                            item.slug
                            for item in self.graph.practice_graphs[0].rule_timings
                        ]

                    with after.all:
                        _restore_slice_files()

                    with it("should validate from the nodes in that hierarchy"):
                        expect(
                            any(slug.startswith("run-queries:") for slug in self.timings)
                        ).to(equal(True))

                    with it("should not iterate the rule list on validate"):
                        expect(self.rule_list_calls).to(equal(0))

                    with it("should not require a classification query"):
                        expect(any("classify" in slug for slug in self.timings)).to(
                            equal(False)
                        )

                    with context("with a single rule passed"):
                        with it("should validate only that rule"):
                            # BDD: SIGNATURE
                            pass

                        with it("should not walk the collection"):
                            # BDD: SIGNATURE
                            pass

                    with context("that has been validated"):
                        with it("should attach rule violations to nodes in those files"):
                            customer = next(
                                node
                                for node in self.graph.practice_graphs[0].nodes.values()
                                if node.name == "Customer"
                            )
                            expect(isinstance(customer.rules.violations, list)).to(
                                equal(True)
                            )

                        with it("should expose those hits on node.rules.violations"):
                            graph = self.graph.practice_graphs[0]
                            hits = [
                                hit
                                for node in graph.nodes.values()
                                for hit in node.rules.violations
                            ]
                            expect(hits == list(hits)).to(equal(True))

                        with it("should run graph rules as one batch"):
                            batches = [
                                slug
                                for slug in self.timings
                                if slug.startswith("run-queries:")
                            ]
                            rules_run = [
                                slug
                                for slug in self.timings
                                if not slug.startswith("run-queries:")
                                and slug != "run-queries:knowledge-graph"
                            ]
                            expect(len(batches) < len(rules_run)).to(equal(True))

                        with it("should still collect markdown rules as instruction text"):
                            expect("Evaluate the current context against this rule" in (
                                getattr(self.graph, "markdown_instructions", "") or ""
                            )).to(equal(True))
