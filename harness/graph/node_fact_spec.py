"""Node rows must not be edge query tuples mis-decoded into the graph."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import description, it

from graph import Node


with description("node facts"):
    with it("should reject building-block edge tuples masquerading as nodes"):
        edge_row = [
            "ddd:ValueObject:src/customer/account/account.ts:ValidationCode",
            "ddd:Aggregate:src/customer/account",
            "belongsTo",
            "4",
            "relationship",
        ]
        expect(Node.fact(edge_row)).to(equal(None))

    with it("should accept a ddd building-block node tuple"):
        node_row = [
            "ddd:Aggregate:src/customer/account",
            "account",
            "Aggregate",
            "ddd",
            "src/customer/account",
            "1",
            "1",
            "specification",
        ]
        fact = Node.fact(node_row)
        expect(fact is not None).to(equal(True))
        expect(fact["name"]).to(equal("account"))

