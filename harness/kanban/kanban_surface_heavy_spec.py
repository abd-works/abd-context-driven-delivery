"""The session board on the real desktop surface, measured where it landed, organised by story.

Each signature here has a test of the same name in `pane/hooks/register.test.tsx`: that test proves the pane asks for
the right thing and this one proves the surface drew it. Open the Board pane in the Claude desktop app first. These
specs press only what changes the view; the dialog is cancelled, because it would act on the open repository."""
import time

from expects import be_above_or_equal, be_below_or_equal, be_empty, equal, expect
from mamba import before, context, description, it

from harness.kanban.desktop_pane import DesktopPane

_SETTLE_SECONDS = 2
_PANE_FOOTER_PIXELS = 160
_SAME_LINE_PIXELS = 20
_ACCENT = "#E5531A"


def _settled_press(pane, element):
    pane.press(element)
    time.sleep(_SETTLE_SECONDS)


def _opened_card(pane):
    marks = [mark for mark in pane.card_marks() if mark.name == "▴"]
    if not marks:
        _settled_press(pane, pane.card_marks()[0])
        marks = [mark for mark in pane.card_marks() if mark.name == "▴"]
    return marks[0]


with description("the session board on the desktop surface"):
    with before.all:
        self.pane = DesktopPane()
        self.elements = self.pane.elements()

    with context("with the board drawn"):
        with it("should fill the pane's height"):
            lowest = max(element.bottom for element in self.elements)
            expect(lowest).to(be_above_or_equal(self.pane.window_bottom - _PANE_FOOTER_PIXELS))

        with it("should keep a card's controls inside the card"):
            overflowing = [
                f"{control.name} ends at {control.right}, card at {mark.right}"
                for mark in self.pane.card_marks()
                for control in self.pane.controls_of_card(mark)
                if control.right > mark.right
            ]
            expect(overflowing).to(be_empty)

    with context("with a card opened"):
        with before.all:
            self.mark = _opened_card(self.pane)

        with it("should offer the action list and Run on an opened card"):
            expect(self.pane.named("Run")).not_to(be_empty)

        with it("should show the whole opened card"):
            shown = [button for button in self.pane.named("Close") if button.left > self.mark.left - 700]
            expect(max(button.bottom for button in shown)).to(be_below_or_equal(self.pane.window_bottom))

    with context("with the files list pressed on a card"):
        with before.all:
            buttons = [button for button in self.pane.named("list") if not button.is_offscreen]
            _settled_press(self.pane, buttons[-1])

        with it("should open the files list beside the board"):
            expect(self.pane.named("drawio") + self.pane.named("markdown") + self.pane.named("python")).not_to(be_empty)

    with context("with the activation dialog open"):
        with before.all:
            # Only a card's Activate opens the dialog. The dialog's own Activate commits and pushes, so it is never pressed.
            if not self.pane.named("Cancel"):
                _settled_press(self.pane, next(button for button in self.pane.named("Activate") if not button.is_offscreen))
            cancel = self.pane.named("Cancel")[0]
            confirm = next(button for button in self.pane.named("Activate") if abs(button.top - cancel.top) < _SAME_LINE_PIXELS)
            self.colour = self.pane.colour_at(confirm.left + 8, confirm.top + confirm.height // 2)
            _settled_press(self.pane, cancel)

        with it("should draw the primary action in the accent colour"):
            expect(self.colour).to(equal(_ACCENT))
