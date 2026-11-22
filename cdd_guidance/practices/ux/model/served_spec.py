"""What a screen serves, in the one notation every text format lists it in, and the kind of navigation a transition is."""

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.nodes import Screen, Transition
from cdd_guidance.practices.ux.model.served import NavType

with description("what a screen serves"):
    with before.each:
        self.screen = Screen("Cart", 1)

    with context("read from a card's lines"):
        with before.each:
            self.screen.served.read_lines(["Stories: Browse Books · Check Out", "Steps: Cart › Pay › Then it is paid", "Domain terms: Cart"])

        with it("should serve each thing listed under each kind's heading"):
            expect((self.screen.story_keys, self.screen.step_keys)).to(equal((["Browse Books", "Check Out"], ["Cart › Pay › Then it is paid"])))

        with it("should write the same lines back, a line for each kind it serves any of"):
            expect(self.screen.served.as_lines(lambda link: link.written)).to(
                equal(["Stories: Browse Books · Check Out", "Steps: Cart › Pay › Then it is paid"]))

    with context("served by a callout line's heading in any case"):
        with it("should name the kind the heading lists"):
            self.screen.served.serve(self.screen.served.kind_headed("scenarios"), "Cart › Pay")
            expect(self.screen.scenario_keys).to(equal(["Cart › Pay"]))

with description("a transition's kind of navigation"):
    with it("should be an action when it is made"):
        expect(Transition("Open", 1).nav_type).to(equal("action"))

    with it("should save as the string it is written as"):
        transition = Transition("Open", 1)
        transition.nav_type = "top nav"
        expect((transition.nav_type, transition.nav_type.is_named_on_label)).to(equal(("top nav", True)))

    with it("should read a dashed line with no kind kept as a tab"):
        expect(NavType.from_drawn("", True).is_tab).to(be_true)

    with it("should name neither an action nor a tab on a drawing's label"):
        expect(NavType.ACTION.is_named_on_label or NavType.TAB.is_named_on_label).to(be_false)
