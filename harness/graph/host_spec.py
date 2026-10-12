"""GraphHost returns full tracebacks for failures."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import before, context, description, it

from app.host import GraphHost, dispatch


with description("GraphHost"):
    with context("when an operation fails"):
        with before.each:
            self.host = GraphHost()

        with it("should return a traceback for unknown operations"):
            response = dispatch({"operation": "missing"}, self.host)
            expect(response["ok"]).to(equal(False))
            expect(response["error"]).to(contain("Unknown operation missing"))
            expect(response["traceback"]).to(contain("Traceback (most recent call last)"))
            expect(response["diagnosis"]).to(contain("I just encountered an error doing missing on (unknown database)"))
            expect(response["diagnosis"]).to(contain("Please diagnose and fix"))
