"""Display Server Health Mark in a real browser: the chat bar's own code on its test page, asking a real cdd server
(chat_bar_browser.ChatBarStack).

Scenarios: check_cdd_server_health_in_chat_bar_story.test.md. The disconnected and tools missing marks need a cdd server
that is stopped or from another checkout, which the page's one server cannot be."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_below, equal, expect
from mamba import after, before, context, description, it

from chat_bar_browser import GREEN, ChatBarStack, box, colour_of

with description("Story: Display Server Health Mark") as self:
    with before.all:
        self.stack = ChatBarStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Show the connected mark"):
        with context("Given cdd answers server-health.report, When the Chat Bar draws the active session checkout-flow"):
            with before.all:
                self.page = self.stack.open_on_checkout_flow()

            with after.all:
                self.page.close()

            with it("Then the mark on the chat bar's line is ✓"):
                expect(box(self.page, "health-icon-mark").inner_text().strip()).to(equal("✓"))

            with it("Then the ✓ is green"):
                expect(colour_of(self.page, "health-icon-mark")).to(equal(GREEN))

            with it("Then the ✓ sits left of checkout-flow"):
                expect(box(self.page, "health-icon-mark").bounding_box()["x"]).to(be_below(box(self.page, "session-name").bounding_box()["x"]))
