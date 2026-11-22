"""Select Fidelity in a real browser: the chat bar's own code on its test page, asking a real cdd server
(chat_bar_browser.ChatBarStack).

Scenarios: see_work_in_chat_bar_story.test.md. The seeded session's Discovery holds clean-engineering-modules, which
stands for the scenario's clean-engineering-model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import be_above_or_equal, equal, expect
from mamba import after, before, context, description, it

from chat_bar_browser import CHECKOUT_CHAT, SESSION_FILE, ChatBarStack, box, open_card

FIDELITY = "clean-engineering-modules"
# How far inside the line's right end the press lands, on its state words.
INSIDE_PIXELS = 6
PRESS_SETTLES_MILLISECONDS = 3000

with description("Story: Select Fidelity") as self:
    with before.all:
        self.stack = ChatBarStack()

    with after.all:
        self.stack.close()

    with context("Scenario: Pick a fidelity from anywhere on its line"):
        with context("Given the session card for checkout-flow is open, When the Person presses the line of its Clean Engineering fidelity on its state"):
            with before.all:
                self.page = self.stack.open_on_checkout_flow()
                open_card(self.page)
                self.line = box(self.page, f"card-cell-{FIDELITY}").bounding_box()
                self.button = self.page.locator(f'#above-prompt button[data-key="card-pick-{FIDELITY}"]').bounding_box()
                self.page.mouse.click(self.line["x"] + self.line["width"] - INSIDE_PIXELS, self.line["y"] + self.line["height"] / 2)
                self.page.wait_for_timeout(PRESS_SETTLES_MILLISECONDS)

            with after.all:
                self.page.close()

            with it("Then the press covers the square, the name and the state, the whole line"):
                expect(self.button["width"]).to(be_above_or_equal(self.line["width"] - 2))

            with it("And that fidelity is the fidelity the action button acts on"):
                selection = self.stack.as_chat(CHECKOUT_CHAT, "session.guidance_selection", session=SESSION_FILE)
                expect(selection["fidelities"]).to(equal([FIDELITY]))
