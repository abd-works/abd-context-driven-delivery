"""Display Session Card in a real browser: the chat bar's own code on its test page, asking a real cdd server about
checkout-flow with its five practices all writing under harness (chat_bar_browser.ChatBarStack).

Scenarios: see_work_in_chat_bar_story.test.md."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect, have_len
from mamba import after, before, context, description, it

from chat_bar_browser import ChatBarStack, open_card, seed_checkout_flow_under_harness

CELLS = '#above-prompt [data-box-key^="card-cell-"]'


def folder_chips(page) -> list[str]:
    """The folders the session card lists, each as its chip reads."""
    return page.locator('#above-prompt [data-box-key^="card-folder-chip-"]').evaluate_all("chips => chips.map(chip => chip.innerText.trim())")


with description("Story: Display Session Card") as self:
    with before.all:
        self.stack = ChatBarStack(seed=seed_checkout_flow_under_harness)

    with after.all:
        self.stack.close()

    with context("Scenario: List each folder once"):
        with context("Given checkout-flow is in Discovery with its five practices all writing under harness, When the Person opens the session card for checkout-flow"):
            with before.all:
                self.page = self.stack.open_on_checkout_flow()
                open_card(self.page)

            with after.all:
                self.page.close()

            with it("Then harness is listed once"):
                expect([chip for chip in folder_chips(self.page) if "harness" in chip]).to(have_len(1))

            with it("Then harness sits beside the first fidelity"):
                first = self.page.locator(CELLS).first.get_attribute("data-box-key").removeprefix("card-cell-")
                expect(self.page.locator(f'#above-prompt [data-box-key="card-folder-chip-{first}"]').count()).to(equal(1))

            with it("And every fidelity of Discovery is still listed"):
                expect(self.page.locator(CELLS).count()).to(equal(5))
