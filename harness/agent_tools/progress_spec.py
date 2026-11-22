"""Specs for the progress a long tool call reports: it belongs to the call, which tells whoever listens to it."""

from expects import equal, expect
from mamba import before, context, description, it

from harness.agent_tools.progress import report_progress
from harness.agent_tools.tool_call import CALLS_BEING_ANSWERED, ToolCall


with description("the progress of a tool call"):

    with before.each:
        self.heard = []

    with context("that a caller listens to"):

        with it("should tell the caller each step the call reports"):
            ToolCall(reporter=self.heard.append).report_progress("reading stories")
            expect(self.heard).to(equal(["reading stories"]))

        with it("should tell the caller each step the operation reports while the call is answered"):
            with CALLS_BEING_ANSWERED.answering(ToolCall(reporter=self.heard.append)):
                report_progress("reading stories")
            expect(self.heard).to(equal(["reading stories"]))

        with context("and that answers another call made in process inside it"):

            with it("should tell its own caller the inner call's steps"):
                with CALLS_BEING_ANSWERED.answering(ToolCall(reporter=self.heard.append)):
                    with CALLS_BEING_ANSWERED.answering(ToolCall()):
                        report_progress("checking rules")
                expect(self.heard).to(equal(["checking rules"]))

    with context("that has finished"):

        with it("should tell the caller nothing more"):
            with CALLS_BEING_ANSWERED.answering(ToolCall(reporter=self.heard.append)):
                pass
            report_progress("reading stories")
            expect(self.heard).to(equal([]))

    with context("made in process with no one listening"):

        with it("should stay silent"):
            with CALLS_BEING_ANSWERED.answering(ToolCall()):
                report_progress("reading stories")
            expect(self.heard).to(equal([]))
