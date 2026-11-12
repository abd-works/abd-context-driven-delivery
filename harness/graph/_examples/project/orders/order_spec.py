"""Order behaviour. Known issues: one example reads private state instead of an observable outcome, and one names no
behaviour. It runs green, so a run of every spec in the repository passes over it."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, description, it

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orders.order import Order  # noqa: E402

with description("an order"):
    with before.each:
        self.order = Order("alice")

    with it("should be confirmed once it is placed"):
        self.order.place("cat", "dog", "", "", "")
        expect(self.order.confirm()).to(equal(True))

    with it("should keep its lines"):
        self.order.place("cat", "dog", "", "", "")
        expect(self.order.lines).to(equal(["cat", "dog", "", "", ""]))

    with it("should work"):
        expect(self.order._shopper_cache).to(equal(None))
