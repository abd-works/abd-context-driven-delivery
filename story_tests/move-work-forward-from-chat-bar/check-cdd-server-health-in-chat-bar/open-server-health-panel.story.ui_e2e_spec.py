"""Open Server Health Panel in a real browser: the chat bar's own code on its test page, asking a real cdd server
(chat_bar_browser.ChatBarStack).

Scenarios: check_cdd_server_health_in_chat_bar_story.test.md. Which apps run is whatever this computer runs, so no
example here asks for an app to be running; Say what is wrong when cdd is down needs a stopped cdd server."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from chat_bar_browser import GREEN, ChatBarStack, box, colour_of, health_parts, open_card, shown_tips

with description("Story: Open Server Health Panel") as self:
    with before.all:
        self.stack = ChatBarStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Show every part running on one line"):
        with context("Given cdd is connected, When the Person opens the server health panel"):
            with before.all:
                self.page = self.stack.open_on_checkout_flow()
                open_card(self.page)

            with after.all:
                self.page.close()

            with it("Then the session card opens with the panel on its top line"):
                expect(box(self.page, "card-header").locator('[data-box-key="health-icons"]').count()).to(equal(1))

            with it("Then MCP host is green"):
                expect(colour_of(self.page, "MCP host")).to(equal(GREEN))

            with it("Then the panel holds a Tools part"):
                expect(health_parts(self.page)).to(contain("Tools"))

            with it("And no Hook server part shows"):
                expect("Hook server" in health_parts(self.page)).to(equal(False))

            with it("And each part's name shows on hover"):
                box(self.page, "MCP host").hover()
                expect(shown_tips(self.page, "MCP host")[0]).to(contain("MCP host"))

    with context("Scenario: Pin the panel open"):
        with context("Given cdd is connected and checkout-flow is the active session, When the Person presses the server health mark"):
            with before.all:
                self.page = self.stack.open_on_checkout_flow()
                open_card(self.page)

            with after.all:
                self.page.close()

            with it("Then the session card and its panel stay open after the pointer leaves the mark"):
                expect(box(self.page, "card-header").is_visible()).to(be_true)
