"""BQRS files resolve per query path, not by filename stem."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import description, it

from graph import CodeQLGraph, QueryFailure


with description("CodeQL bqrs paths"):
    with it("should map each query to its pack-relative bqrs file"):
        root = _HERE.parents[1]
        graph = CodeQLGraph()
        database = Path("/tmp/db")
        nodes = root / "practices/ddd/model/typescript/codeql/nodes/building-blocks.ql"
        edges = root / "practices/ddd/model/typescript/codeql/edges/building-blocks.ql"
        nodes_bqrs = graph._bqrs_path(database, nodes)
        edges_bqrs = graph._bqrs_path(database, edges)
        expect(nodes_bqrs.name).to(equal("building-blocks.bqrs"))
        expect(edges_bqrs.name).to(equal("building-blocks.bqrs"))
        expect(nodes_bqrs).not_to(equal(edges_bqrs))
        expect("nodes" in nodes_bqrs.parts).to(equal(True))
        expect("edges" in edges_bqrs.parts).to(equal(True))

    with it("should not fall back to another query file with the same stem"):
        root = _HERE.parents[1]
        graph = CodeQLGraph()
        database = Path("/tmp/db")
        nodes = root / "practices/ddd/model/typescript/codeql/nodes/building-blocks.ql"
        try:
            graph._bqrs_for(database, nodes)
            expect(True).to(equal(False))
        except QueryFailure:
            pass
