"""The walk of a story canvas's screens, without rendering: the values a step names, whether a screen's text shows
them, and the report the walk writes."""

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import ExplorerScenario
from cdd_guidance.practices.ux.model.claude_design.screen_walk import (
    ScreenWalkReport,
    ShownText,
    StepValues,
    StillAction,
    WalkedStep,
    _still_actions,
    _Stop,
)


def _written(text: str) -> list:
    return [value.written for value in StepValues(text).values]


with description("the values a step names") as self:
    with it("should take each quoted value"):
        expect(_written('the cart shows "Line 1 · Atlas" and “Line 2 · Ace”')).to(equal(['"Line 1 · Atlas"', '"Line 2 · Ace"']))

    with it("should take each dollar amount"):
        expect(_written("the total is $346/mo, and the first bill −$15 after a $1,000 deposit")).to(equal(["$346", "$15", "$1,000"]))

    with it("should take a code written in capitals with digits, and leave capital words such as SIM alone"):
        expect(_written("the Customer applies ALL10 to the SIM and ID")).to(equal(["ALL10"]))

    with it("should take a phone number whole"):
        expect(_written("the Customer ports +1 (441) 555-0106 to Paradise")).to(equal(["+1 (441) 555-0106"]))

    with it("should take a number of four or more digits, such as a validation code"):
        expect(_written("the Customer enters the code 123456")).to(equal(["123456"]))

    with it("should read through the markup a story map marks terms with"):
        expect(_written("the **Customer** enters ++voucher++ ++ALL10++ for *$10 off*")).to(equal(["ALL10", "$10"]))

    with it("should take a value inside quotes once"):
        expect(_written('the message reads "Pay $25 with TRAVEL25"')).to(equal(['"Pay $25 with TRAVEL25"']))

    with it("should name nothing in a step without values"):
        expect(_written("the Customer opens the catalog")).to(equal([]))


with description("the text a screen shows") as self:
    with before.each:
        self.shown = ShownText("Line 1 · Atlas $193/mo\nVoucher all10 applied\nCall +1 (441) 555-0106 or 4415550199")

    with it("should show a quoted value however its case and spaces are written"):
        expect(self.shown.shows(StepValues('"line 1 ·  atlas"').values[0])).to(equal(True))

    with it("should show a dollar amount the screen writes with a suffix"):
        expect(self.shown.shows(StepValues("$193").values[0])).to(equal(True))

    with it("should show an amount drawn right after another, as a struck-through price is"):
        expect(ShownText("$449$434/mo").shows(StepValues("$434").values[0])).to(equal(True))

    with it("should show an amount whose currency sign the screen draws apart"):
        expect(ShownText("$ 0 /mo").shows(StepValues("$0/mo").values[0])).to(equal(True))

    with it("should show a quoted line the screen draws across several elements"):
        expect(ShownText("Voucher TRAVEL25\nfirst bill only\n−$25").shows(StepValues('"Voucher TRAVEL25, first bill only, −$25"').values[0])).to(equal(True))

    with it("should not take a longer amount for a shorter one"):
        expect(ShownText("$1930/mo").shows(StepValues("$193").values[0])).to(equal(False))

    with it("should show a phone number written with other separators"):
        expect(self.shown.shows(StepValues("+1 441 555 0199").values[0])).to(equal(True))

    with it("should leave out a value the screen does not show"):
        expect(self.shown.shows(StepValues("HELLO5").values[0])).to(equal(False))


with description("a walk's report") as self:
    with before.each:
        self.report = ScreenWalkReport([
            WalkedStep("Apply Voucher", "Apply a voucher", "apply-voucher", "When the Customer applies ALL10", ["ALL10"], []),
            WalkedStep("Apply Voucher", "Apply a voucher", "apply-voucher", "Then the total is $346/mo", [], ["$346"]),
        ])

    with it("should name each value left out by story, scenario, and value"):
        expect(self.report.misses).to(equal(["Apply Voucher › Apply a voucher › $346"]))

    with it("should write a table with a line for each step it walked"):
        expect(self.report.markdown()).to(contain("| Apply Voucher › Apply a voucher | apply-voucher | Then the total is $346/mo |  | $346 |"))

    with context("of a screen that did not render"):
        with it("should name the screen as left out, with why"):
            report = ScreenWalkReport([WalkedStep("Pay", "Pay by card", "pay", "Then the order is paid", [], [], "PMLApp is not defined")])
            expect((report.misses, report.markdown())).to(equal((
                ["Pay › Pay by card › (screen did not render)"],
                "| Story › Scenario | Screen | Step | Found | Missing |\n| --- | --- | --- | --- | --- |\n"
                "| Pay › Pay by card | pay | Then the order is paid |  | (screen did not render: PMLApp is not defined) |\n",
            )))


def _stills(groups: list, texts: list, played: str = "") -> list:
    """The actions the walk finds leave the screen as it was, for a scenario of groups rendered to texts."""
    scenario = ExplorerScenario("Enter Validation Code", "Enter the code", False, "enter-code", tuple(groups))
    stops = [_Stop(scenario, None, group.split("\n"), index, played) for index, group in enumerate(groups)]
    return [still.step for still in _still_actions(stops, [{"text": text} for text in texts])]


with description("the walk's check that each action changes its screen") as self:
    with it("should pass an action whose outcome the screen shows differently"):
        expect(_stills(["Given a code was sent\nWhen the Customer enters 123456", "Then the account is verified"], ["Code ______", "Verified"])).to(equal([]))

    with it("should name an action after which the screen shows what it showed before"):
        expect(_stills(["Given a code was sent\nWhen the Customer enters 123456", "Then the account is verified"], ["Code", "Code"])).to(
            equal(["When the Customer enters 123456"]))

    with it("should name an action whose scenario has one state for all its steps"):
        expect(_stills(["Given a code was sent\nWhen the Customer enters 123456\nThen the account is verified"], ["Verified"])).to(
            equal(["When the Customer enters 123456"]))

    with it("should compare an action inside a step group, followed by its outcome, with the group before it"):
        groups = ["Given a code was sent\nWhen the Customer opens the screen", "Then the code is asked for\nWhen the Customer enters 123456\nThen the account is verified"]
        expect((_stills(groups, ["Empty", "Verified"]), _stills(groups, ["Same", "Same"]))).to(
            equal(([], ["When the Customer opens the screen", "When the Customer enters 123456"])))

    with it("should name an outline's row by the name the screen loads it by"):
        scenario = ExplorerScenario("Enter Validation Code", "Enter a wrong code", False, "enter-code", ("Given a code\nWhen the Customer enters {code}",))
        stop = _Stop(scenario, None, ["Given a code", "When the Customer enters 999999"], 0, "Enter a wrong code: 999999")
        expect([still.miss for still in _still_actions([stop], [{"text": "Code"}])]).to(
            equal(["Enter Validation Code › Enter a wrong code: 999999 › (screen stays as it was after): When the Customer enters 999999"]))


with description("a walk's report of actions that leave the screen as it was") as self:
    with it("should name each as a miss, so publishing refuses it unless the person accepts it by name"):
        report = ScreenWalkReport([], [StillAction("Enter Validation Code", "Enter the code", "enter-code", "When the Customer enters 123456")])
        expect(report.misses).to(equal(["Enter Validation Code › Enter the code › (screen stays as it was after): When the Customer enters 123456"]))

    with it("should list each in walk.md under why it matters"):
        report = ScreenWalkReport([], [StillAction("Enter Validation Code", "Enter the code", "enter-code", "When the Customer enters 123456")])
        expect(report.markdown()).to(contain("| Enter Validation Code › Enter the code | enter-code | When the Customer enters 123456 |"))


with description("an outline the explorer lists with its Examples table") as self:
    with before.each:
        self.outline = ExplorerScenario("Create Credentials", "Enter Invalid credentials", False, "create-credentials",
                                        ("Given the Customer has entered {example}\nWhen the Customer registers", "Then the {message} message is shown"),
                                        ("when", "then"),
                                        (("missing email", {"example": "missing email", "message": "email required"}),
                                         ("password missing letters", {"example": "password missing letters", "message": "password rule"})))

    with it("should play each row, by the name the fixtures bundle gives it, with that row's values in its steps"):
        expect([(played.name, played.groups[1]) for played in self.outline.played()]).to(equal([
            ("Enter Invalid credentials: missing email", "Then the email required message is shown"),
            ("Enter Invalid credentials: password missing letters", "Then the password rule message is shown"),
        ]))

    with it("should name a row of an outline named with a placeholder by the outline's name with the row's value in it"):
        outline = ExplorerScenario("Add Line To Cart", "Add a line with ${plan}", False, "cart", ("When the Customer adds ${plan}",), ("when",),
                                   (("Atlas", {"plan": "Atlas"}),))
        expect([played.name for played in outline.played()]).to(equal(["Add a line with Atlas"]))

    with it("should play a scenario that is no outline as itself"):
        plain = ExplorerScenario("Add Line To Cart", "Add one more line", False, "cart", ("When the Customer adds Ace",))
        expect([(played.name, played.groups) for played in plain.played()]).to(equal([("Add one more line", ("When the Customer adds Ace",))]))
