"""Mamba spec for `a scenarios Markdown document` rendered back to Markdown.

The fixture is a trimmed copy of a pml-web scenarios file: front matter, sub-epic, evidence,
domain terms, sub-epic examples, stories with backgrounds, scenarios, an outline with its own
examples, prose between scenarios, and a closing section.
"""

from pathlib import Path

from mamba import description, context, it, before
from expects import equal, contain, be_true, expect

from cdd_guidance.practices.stories.model.markdown.links import unlink
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel
from cdd_guidance.practices.stories.stories import Stories

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "get_sim_scenarios.md"
ONBOARDING_CART_LINK = "++[onboarding cart](../../../src/.context/domain-model.md#onboarding-entity)++"


def _steps(steps):
    rows = []
    for step in steps:
        rows.append((step.keyword, step.text))
        rows.extend((extra.keyword, extra.text) for extra in step.ands)
    return rows


def _content(story_map):
    """Everything a reader sees: names, background and scenario steps, examples, and prose."""
    rows = []
    for epic in story_map.epics:
        for sub in epic.epics:
            rows.append(("sub-epic", sub.name, tuple(sorted(getattr(sub, "examples", {}) or {}))))
            for story in sub.stories:
                rows.append(("story", story.name))
                for background in story.backgrounds:
                    rows.append(("background", tuple(_steps(background.steps))))
                for scenario in story.scenarios:
                    rows.append((
                        "scenario",
                        scenario.name,
                        scenario.is_outline,
                        tuple(_steps(scenario.steps)),
                        tuple(tuple(sorted(row.items())) for row in scenario.examples.table()),
                    ))
    return rows


with description("a scenarios Markdown document") as self:
    with before.each:
        self.text = FIXTURE.read_text(encoding="utf-8")
        self.parsed = MarkdownStoryModel().parse(self.text)
        self.rendered = MarkdownStoryModel().render(self.parsed)

    with context("rendered back to Markdown"):
        with it("should write the document it was parsed from"):
            expect(self.rendered).to(equal(self.text))

        with it("should parse to the same stories, backgrounds, scenarios, steps, and examples"):
            again = MarkdownStoryModel().parse(self.rendered)
            expect(_content(again)).to(equal(_content(self.parsed)))

        with it("should keep domain-term links in steps"):
            expect(self.rendered).to(contain(
                f"*Given* the Customer has the {ONBOARDING_CART_LINK} ++cart ready to choose SIM++  "
            ))

        with it("should keep evidence, domain terms, and the closing section"):
            expect(self.rendered).to(contain("### Evidence"))
            expect(self.rendered).to(contain(f"- {ONBOARDING_CART_LINK} — "))
            expect(self.rendered).to(contain("## Changed to follow pml-my"))

    with context("parsed"):
        with it("should name the sub-epic from its heading"):
            names = [sub.name for epic in self.parsed.epics for sub in epic.epics]
            expect(names).to(equal(["Get Sim"]))

        with it("should hold each story with its background and scenarios"):
            sub = self.parsed.epics[0].epics[0]
            expect([story.name for story in sub.stories]).to(equal(["Select Sim", "Enter Existing Sim"]))
            expect([s.name for s in sub.stories[1].scenarios]).to(
                equal(["Enter existing SIM", "Port the number is rejected"])
            )
            expect(_steps(sub.stories[0].backgrounds[0].steps)).to(equal([
                ("Given", "the Customer has the ++onboarding cart++ ++cart ready to choose SIM++"),
            ]))

        with it("should hold the sub-epic examples by name"):
            sub = self.parsed.epics[0].epics[0]
            expect(sorted(sub.examples)).to(contain("cart ready to choose SIM", "SIM selection failed"))

        with it("should keep step text free of links"):
            step = self.parsed.epics[0].epics[0].stories[0].scenarios[0].steps[0]
            expect(step.text).to(equal(unlink(step.text)))

    with context("with an edited scenario name and step"):
        with before.each:
            story = self.parsed.epics[0].epics[0].stories[0]
            scenario = story.scenarios[0]
            scenario.name = "Pick eSIM"
            scenario.steps[1].text = "the **Customer** picks the ++SIM choice++ ++eSIM++"
            self.rendered = MarkdownStoryModel().render(self.parsed)

        with it("should write the new name and step in the template form"):
            expect(self.rendered).to(contain("#### Scenario: Pick eSIM\n"))
            expect(self.rendered).to(contain("\n*When* the **Customer** picks the ++SIM choice++ ++eSIM++  \n"))

        with it("should leave every other line as written"):
            changed = {"#### Scenario: Choose eSIM", "*When* the **Customer** selects the ++SIM choice++ ++eSIM++  "}
            kept = [line for line in self.text.splitlines() if line not in changed]
            expect(all(line in self.rendered.splitlines() for line in kept)).to(be_true)

    with context("rendered through the stories render tool"):
        with it("should write the document it was given"):
            result = Stories(fidelity="scenarios").render("markdown", self.text, source="markdown")
            expect(result["content"]).to(equal(self.text))
