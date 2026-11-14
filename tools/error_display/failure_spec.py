"""Failure: what failed and the context it failed in, the shape every failure is shown in."""
from expects import equal, expect
from mamba import describe, it

from tools.error_display.failure import Failure

with describe(Failure):
    with describe("a failure described"):
        with it("should say what failed"):
            expect(Failure.describe("Kanban did not open: npm install failed", "Opening an app from the health panel").failure).to(equal("Kanban did not open: npm install failed"))

        with it("should say the context it failed in"):
            expect(Failure.describe("Kanban did not open: npm install failed", "Opening an app from the health panel").context).to(equal("Opening an app from the health panel"))
