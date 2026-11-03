"""Specs for the progress a long tool call reports."""

from expects import equal, expect
from mamba import before, context, description, it

from harness.agent_tools.progress import report_progress, reporting_to


with description("the progress of a tool call"):

    with before.each:
        self.heard = []

    with context("that a caller listens to"):

        with it("should tell the caller each step"):
            with reporting_to(self.heard.append):
                report_progress("reading stories")
            expect(self.heard).to(equal(["reading stories"]))

    with context("that has finished"):

        with it("should tell the caller nothing more"):
            with reporting_to(self.heard.append):
                pass
            report_progress("reading stories")
            expect(self.heard).to(equal([]))
