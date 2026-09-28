"""BDD spec for CodeQL report-runner speed seams."""

import inspect
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import mcp.types  # SDK, before harness/mcp is on PYTHONPATH
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model.codeql import CodeQL, _RUN_QUERIES_FLAGS
from harness.knowledge_graph.model.dot_graph import (
    _hierarchy_violations,
    graph_name_matches,
    violation_row_indexes,
)
from harness.knowledge_graph.model.graph_rules import RuleViolation
from harness.knowledge_graph.model.practice_graph import PracticeGraph

_KG = _REPO_ROOT / "harness" / "knowledge_graph"
_PACK = _REPO_ROOT / "practices" / "clean_engineering" / "model" / "codeql"


with description("CodeQL report runner"):
    with it("should evaluate the query batch on every core"):
        expect("--threads=0" in _RUN_QUERIES_FLAGS).to(equal(True))

    with it("should drop catalog prefix harness and keep inner modules"):
        prefixes = CodeQL(_REPO_ROOT)._first_class_module_prefixes(_REPO_ROOT)
        expect("harness" in prefixes).to(equal(False))
        expect("." in prefixes).to(equal(False))
        expect("harness/knowledge_graph" in prefixes).to(equal(True))
        expect("harness/guidance" in prefixes).to(equal(True))

    with it("should not rewrite subject_filter.qll when the generated text already matches"):
        codeql = CodeQL(_KG)
        codeql._write_subject_filter(_PACK, path_root=_REPO_ROOT)
        target = _PACK / "subject_filter.qll"
        before = target.stat().st_mtime_ns
        codeql._write_subject_filter(_PACK, path_root=_REPO_ROOT)
        expect(target.stat().st_mtime_ns).to(equal(before))

    with it("should match a subject path without joining every File in the database"):
        codeql = CodeQL(_KG)
        codeql._write_subject_filter(_PACK, path_root=_REPO_ROOT)
        text = (_PACK / "subject_filter.qll").read_text(encoding="utf-8")
        expect("exists(File f, string prefix" in text).to(equal(False))
        expect("bindingset[path]" in text).to(equal(True))
        expect("subjectFilterPrefix(filterPrefix)" in text).to(equal(True))

    with it("should write only the requested rule slugs"):
        codeql = CodeQL(_KG)
        with tempfile.TemporaryDirectory() as folder:
            pack = Path(folder)
            codeql._write_requested_rules(pack, ["deep-module", "one-way-deps"])
            text = (pack / "requested_rules.qll").read_text(encoding="utf-8")
        expect('slug = "deep-module"' in text).to(equal(True))
        expect('slug = "keep-operations-small-focused"' in text).to(equal(False))

    with it("should not rewrite requested_rules.qll when the generated text already matches"):
        codeql = CodeQL(_KG)
        with tempfile.TemporaryDirectory() as folder:
            pack = Path(folder)
            codeql._write_requested_rules(pack, ["deep-module"])
            target = pack / "requested_rules.qll"
            before = target.stat().st_mtime_ns
            codeql._write_requested_rules(pack, ["deep-module"])
            expect(target.stat().st_mtime_ns).to(equal(before))

    with it("should group combined query rows by rule slug"):
        grouped = CodeQL(_KG)._rows_by_slug(
            [
                ["Class A", "msg", "op", "deep-module"],
                ["Class B", "other", "op2", "one-way-deps"],
            ],
            ["deep-module", "one-way-deps"],
        )
        expect(len(grouped["deep-module"])).to(equal(1))
        expect(grouped["deep-module"][0][0]).to(equal("Class A"))
        expect(len(grouped["one-way-deps"])).to(equal(1))

    with it("should map CodeQL operation location onto file and line range"):
        rows = list(
            CodeQL(_KG).operation_rows(
                [
                    [
                        "PracticeGraph",
                        "_evaluate_graph_rules",
                        "",
                        251,
                        "harness/knowledge_graph/model/practice_graph.py",
                        300,
                    ]
                ]
            )
        )
        expect(rows[0]["file"]).to(
            equal("harness/knowledge_graph/model/practice_graph.py")
        )
        expect(rows[0]["line"]).to(equal(251))
        expect(rows[0]["end_line"]).to(equal(300))

    with it("should expand a class header to the whole class body"):
        from practices.clean_engineering.model.codeql.codeql_model import SourceLocation, SourceSpan

        path = "harness/knowledge_graph/model/codeql.py"
        lines = (_REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
        class_line = next(
            index
            for index, line in enumerate(lines, 1)
            if line.startswith("class CodeQLRunError")
        )
        location = SourceSpan(_REPO_ROOT).read(
            SourceLocation(
                file=path,
                line=class_line,
                end_line=class_line,
            )
        )
        start, end, text = location.line, location.end_line, location.text
        expect("class CodeQLRunError" in text).to(equal(True))
        expect('"""' in text).to(equal(True))
        expect(end > start).to(equal(True))
        expect("class QueryServerDown" in text).to(equal(False))

    with it("should expand a multi-line def header through the body"):
        from practices.clean_engineering.model.codeql.codeql_model import SourceLocation, SourceSpan

        path = "harness/knowledge_graph/model/codeql.py"
        lines = (_REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
        lo = next(
            index
            for index, line in enumerate(lines, 1)
            if line.startswith("    def populate(")
        )
        location = SourceSpan(_REPO_ROOT).read(SourceLocation(file=path, line=lo, end_line=lo))
        start, end, text = location.line, location.end_line, location.text
        expect("self._apply_fact_batch" in text).to(equal(True))
        expect("def load_existing_facts" in text).to(equal(False))
        expect(end - start + 1 < 43).to(equal(True))

    with it("should populate by default"):
        expect(
            inspect.signature(CodeQL.populate).parameters["populate"].default
        ).to(equal(True))
        expect(
            inspect.signature(PracticeGraph.load).parameters["populate"].default
        ).to(equal(True))

    with it("should include every practice graph unless named"):
        expect(graph_name_matches("harness.knowledge_graph", None)).to(equal(True))
        expect(graph_name_matches("harness.knowledge_graph", [])).to(equal(True))
        expect(
            graph_name_matches("harness.knowledge_graph", ["knowledge_graph"])
        ).to(equal(True))
        expect(graph_name_matches("harness.knowledge_graph", ["stories"])).to(
            equal(False)
        )

    with it("should keep violating rows and their ancestors"):
        expect(violation_row_indexes([(0, False), (1, False), (2, True)])).to(
            equal([0, 1, 2])
        )
        expect(violation_row_indexes([(0, False), (1, False)])).to(equal([]))
        expect(
            violation_row_indexes([(0, False), (1, True), (1, False), (2, True)])
        ).to(equal([0, 1, 2, 3]))

    with it("should mark hierarchy lines from stored hits without walking every node"):
        class _Graph:
            _violations_by_node = {
                "op": [
                    RuleViolation(
                        "keep-operations-small-focused",
                        "too long",
                        "clean_engineering",
                        node_id="op",
                    )
                ]
            }

            def record_partial_failure(self, *args):
                raise AssertionError("hierarchy should not walk inherited rules")

        class _Node:
            node_id = "op"
            name = "op"
            graph = _Graph()

            @property
            def rules(self):
                raise AssertionError("hierarchy should not query node.rules")

        mark = _hierarchy_violations(_Node())
        expect("keep-operations-small-focused" in mark).to(equal(True))
