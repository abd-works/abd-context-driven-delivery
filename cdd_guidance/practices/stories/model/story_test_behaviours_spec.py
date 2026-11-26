"""One story map, created from story files in each format, then one common set of examples on the graph it gives.

Each format's part is only the setup that creates the project from that format's files (Python, TypeScript,
JavaScript, and markdown scenarios, which hold the same stories). Every example after that is shared: it asks the
graph for stories, scenarios, steps, examples and the code they are joined to, and names no format. The trip to
another format and back is created the same way, then checked by the same examples."""

from expects import contain, equal, expect
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.stories.model.fixtures.pack_orders_project import pack_orders_in, pack_orders_taken, pack_orders_without_a_map

_PACK = "Pack a paid order"
_REFUSE = "Refuse to pack an unpaid order"
_CANCEL = "Cancel a paid order"
_SHOWN = "Show a packed order"

with shared_context("the story files of Pack Orders"):
    with it("should each sit at a path the scenarios or acceptance tests fidelity declares"):
        expect(self.project.undeclared_files()).to(equal([]))


with shared_context("the story map of Pack Orders"):
    with it("should hold the stories under their sub-epic, in the map's order"):
        expect(self.project.story_names("Pack Orders")).to(equal(["Pack Order", "Cancel Order"]))

    with it("should give a story the scenarios its own story file holds"):
        expect(self.project.scenario_names("Pack Order")[:2]).to(equal([_PACK, _REFUSE]))

    with it("should give a story the scenarios a file shared by its sub-epic holds"):
        expect(self.project.scenario_names("Cancel Order")).to(equal([_CANCEL]))

    with it("should hold a scenario's Given, When and Then in order, with their words"):
        expect(self.project.steps(_PACK)).to(equal([
            ("Given", "given the Shop keeps Order paid order", []),
            ("When", "when the Shop Clerk packs the Order", []),
            ("Then", "then the Order paid order has status packed", []),
        ]))

    with it("should chain an And onto the Then it continues"):
        expect(self.project.steps(_REFUSE)[2]).to(equal(
            ("Then", 'then the Shop refuses with "order 1002 is not paid"', ["and the Order unpaid order keeps status submitted"])
        ))

    with it("should save each step's phase, a chained step taking the phase of the step it continues"):
        expect(self.project.phases(_REFUSE)).to(equal(["given", "when", "then", "then"]))


with shared_context("the examples of Pack Orders"):
    with it("should hold each example the scenarios use"):
        expect(self.project.example_names()).to(equal(["paid order", "unpaid order"]))

    with it("should have a Then observe the example its Given names"):
        expect(self.project.observed_by(_PACK, "then the Order paid order has status packed")).to(equal(["paid order"]))

    with it("should have a Given observe the example it names"):
        expect(self.project.observed_by(_REFUSE, "given the Shop keeps Order unpaid order")).to(equal(["unpaid order"]))


with shared_context("the story tests of Pack Orders joined to the code they call"):
    with it("should have a When invoke the operation it calls on the class under test"):
        expect(self.project.invoked_by(_PACK, "when the Shop Clerk packs the Order")).to(contain("Order.pack"))

    with it("should have a Given invoke the operation that seeds its state"):
        expect(self.project.invoked_by(_PACK, "given the Shop keeps Order paid order")).to(equal(["OrderRepository.create"]))

    with it("should have a When of a shared story file invoke the operation it calls"):
        expect(self.project.invoked_by(_CANCEL, "when the Shop Clerk cancels the Order")).to(contain("Order.cancel"))

    with it("should say a When's calls reach the code under test"):
        expect(self.project.fact(_PACK, "when the Shop Clerk packs the Order", "calls_reach")).to(equal("tested"))

    with it("should keep the code a step holds"):
        expect(self.project.fact(_PACK, "when the Shop Clerk packs the Order", "body_text")).to(contain('.load("1001").pack()'))

    with it("should have an example demonstrate the class its examples file builds it as"):
        expect(self.project.demonstrated_by("paid order")).to(equal(["Order"]))


with shared_context("the screen spec of Pack Orders"):
    with it("should give the story the scenario its screen spec tests"):
        expect(self.project.scenario_names("Pack Order")).to(equal([_PACK, _REFUSE, _SHOWN]))

    with it("should read the test's seed as its Given, its actions as its When, and its check as its Then"):
        expect([kind for kind, _, _ in self.project.steps(_SHOWN)]).to(equal(["Given", "When", "Then"]))

    with it("should keep the statements a step is made of"):
        expect(self.project.fact(_SHOWN, 'when await page.goto("/orders/1001");', "body_text")).to(contain('name: "Pack order"'))


with shared_context("the story tests of Pack Orders with no story map"):
    with it("should hold the stories the story tests name"):
        expect(self.project.every_story_name()).to(equal(["Cancel Order", "Pack Order"]))

    with it("should give a story the scenarios a shared story file holds"):
        expect(self.project.scenario_names("Cancel Order")).to(equal([_CANCEL]))

    with it("should have a When invoke the operation it calls on the class under test"):
        expect(self.project.invoked_by(_CANCEL, "when the Shop Clerk cancels the Order")).to(contain("Order.cancel"))


with description("a story map created from story files") as self:
    with context("written as Python story tests"):
        with before.all:
            self.project = pack_orders_in("python")

        with included_context("the story files of Pack Orders"):
            pass

        with included_context("the story map of Pack Orders"):
            pass

        with included_context("the examples of Pack Orders"):
            pass

        with included_context("the story tests of Pack Orders joined to the code they call"):
            pass

        with context("that is taken to markdown scenarios and back"):
            with before.all:
                self.project = pack_orders_taken("python", "markdown")

            with included_context("the story files of Pack Orders"):
                pass

            with included_context("the story map of Pack Orders"):
                pass

            with included_context("the examples of Pack Orders"):
                pass

    with context("written as TypeScript story tests"):
        with before.all:
            self.project = pack_orders_in("typescript")

        with included_context("the story files of Pack Orders"):
            pass

        with included_context("the story map of Pack Orders"):
            pass

        with included_context("the examples of Pack Orders"):
            pass

        with included_context("the story tests of Pack Orders joined to the code they call"):
            pass

        with included_context("the screen spec of Pack Orders"):
            pass

        with context("with no story map, under the project's tests folder"):
            with before.all:
                self.project = pack_orders_without_a_map("typescript")

            with included_context("the story tests of Pack Orders with no story map"):
                pass

        with context("that is taken to markdown scenarios and back"):
            with before.all:
                self.project = pack_orders_taken("typescript", "markdown")

            with included_context("the story files of Pack Orders"):
                pass

            with included_context("the story map of Pack Orders"):
                pass

            with included_context("the examples of Pack Orders"):
                pass

        with context("that is taken to JavaScript and back"):
            with before.all:
                self.project = pack_orders_taken("typescript", "javascript")

            with included_context("the story files of Pack Orders"):
                pass

            with included_context("the story map of Pack Orders"):
                pass

            with included_context("the examples of Pack Orders"):
                pass

    with context("written as JavaScript story tests"):
        with before.all:
            self.project = pack_orders_in("javascript")

        with included_context("the story files of Pack Orders"):
            pass

        with included_context("the story map of Pack Orders"):
            pass

        with included_context("the examples of Pack Orders"):
            pass

        with included_context("the story tests of Pack Orders joined to the code they call"):
            pass

        with included_context("the screen spec of Pack Orders"):
            pass

        with context("with no story map, under the project's tests folder"):
            with before.all:
                self.project = pack_orders_without_a_map("javascript")

            with included_context("the story tests of Pack Orders with no story map"):
                pass

        with context("that is taken to markdown scenarios and back"):
            with before.all:
                self.project = pack_orders_taken("javascript", "markdown")

            with included_context("the story files of Pack Orders"):
                pass

            with included_context("the story map of Pack Orders"):
                pass

            with included_context("the examples of Pack Orders"):
                pass

        with context("that is taken to TypeScript and back"):
            with before.all:
                self.project = pack_orders_taken("javascript", "typescript")

            with included_context("the story files of Pack Orders"):
                pass

            with included_context("the story map of Pack Orders"):
                pass

            with included_context("the examples of Pack Orders"):
                pass

    with context("written as markdown scenarios"):
        with before.all:
            self.project = pack_orders_in("markdown")

        with included_context("the story files of Pack Orders"):
            pass

        with included_context("the story map of Pack Orders"):
            pass

        with included_context("the examples of Pack Orders"):
            pass

        with context("that is taken to Python story tests and back"):
            with before.all:
                self.project = pack_orders_taken("markdown", "python")

            with included_context("the story files of Pack Orders"):
                pass

            with included_context("the story map of Pack Orders"):
                pass
