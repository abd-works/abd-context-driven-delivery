"""Mamba spec: a story map copied into another format's model keeps what a clone keeps; a copy makes each part in the
format it is copied into, while a clone keeps each part's own class."""

from expects import be, equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.json.nodes import JsonBackground, JsonScenario, JsonStep, JsonStory, JsonStoryMap
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownStep
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownEpic, MarkdownScenario, MarkdownStory, MarkdownStoryMap
from cdd_guidance.practices.stories.model.story_map import Background, Epic, Scenario, Step, StepType, Story


def _paying_scenario(scenario: Scenario, step: Step) -> Scenario:
    """scenario, holding a background of one step and step under it."""
    background = Background("background", 1)
    background.steps = [Step("a customer", StepType.GIVEN, 1)]
    scenario.backgrounds.append(background)
    scenario.steps.append(step)
    return scenario


with description("a story map copied into another format's model") as self:
    with before.each:
        self.story_map = round_trip_story_map()
        self.story_map.examples["open account"] = {"balance": "120"}
        self.story_map.epics[0].examples["due bill"] = {"amount": "40"}
        self.copied = JsonStoryMap().copy_of(self.story_map)

    with it("should keep every epic, story, background, and scenario"):
        expect(outline(self.copied)).to(equal(outline(self.story_map)))

    with it("should keep the examples an epic shares"):
        expect(self.copied.epics[0].examples["due bill"].cells()).to(equal({"amount": "40"}))

    with it("should keep the examples the story map shares"):
        expect(self.copied.examples["open account"].cells()).to(equal({"balance": "120"}))

    with it("should keep the same examples as a clone of the story map"):
        expect(sorted(self.copied.examples)).to(equal(sorted(self.story_map.clone().examples)))

    with it("should make every story the format's story"):
        expect({type(story) for story in self.copied.descendants.stories()}).to(equal({JsonStory}))


with description("an epic copied into another format") as self:
    with before.each:
        self.epic = Epic("Pay Bills", 1)
        self.epic.stories.append(Story("Review Statement", 1))
        self.epic.epics.append(Epic("Enter Payment", 1))
        self.epic.epics[0].stories.append(Story("Submit Payment", 1))
        self.copied = MarkdownEpic.copy_of(self.epic)

    with it("should make its own stories the stories that format's epics hold"):
        expect(type(self.copied.stories[0])).to(be(MarkdownStory))

    with it("should make its sub-epics epics of that format"):
        expect(type(self.copied.epics[0])).to(be(MarkdownEpic))

    with it("should make its sub-epics' stories the stories that format's epics hold"):
        expect(type(self.copied.epics[0].stories[0])).to(be(MarkdownStory))


with description("an epic cloned") as self:
    with before.each:
        self.epic = Epic("Pay Bills", 1)
        self.epic.stories.append(MarkdownStory("Review Statement", 1))
        self.cloned = self.epic.clone()

    with it("should keep a story of another format the class it has"):
        expect(type(self.cloned.stories[0])).to(be(MarkdownStory))

    with it("should keep its own class"):
        expect(type(self.cloned)).to(be(Epic))


with description("a scenario copied into another format") as self:
    with before.each:
        self.copied = JsonScenario.copy_of(_paying_scenario(Scenario("Pay by card", 1), Step("pays by card", StepType.WHEN, 1)))

    with it("should make its steps that format's steps"):
        expect(type(self.copied.steps[0])).to(be(JsonStep))

    with it("should make its backgrounds that format's backgrounds"):
        expect(type(self.copied.backgrounds[0])).to(be(JsonBackground))

    with it("should make its backgrounds' steps that format's steps"):
        expect(type(self.copied.backgrounds[0].steps[0])).to(be(JsonStep))


with description("a scenario cloned") as self:
    with before.each:
        self.scenario = _paying_scenario(MarkdownScenario("Pay by card", 1), MarkdownStep("pays by card", StepType.WHEN, 1))
        self.cloned = self.scenario.clone()

    with it("should keep a step of another class the class it has"):
        expect(type(self.cloned.steps[0])).to(be(MarkdownStep))

    with it("should keep its own class"):
        expect(type(self.cloned)).to(be(MarkdownScenario))

    with it("should keep what its steps say"):
        expect([step.text for step in self.cloned.steps]).to(equal(["pays by card"]))


with description("a story map cloned") as self:
    with before.each:
        self.story_map = MarkdownStoryMap().copy_of(round_trip_story_map())
        self.story_map.epics[0].stories.append(Story("Export Statement", 2))
        self.cloned = self.story_map.clone()

    with it("should keep every story the class it has"):
        expect([type(story) for story in self.cloned.descendants.stories()]).to(equal([type(story) for story in self.story_map.descendants.stories()]))

    with it("should keep the same outline"):
        expect(outline(self.cloned)).to(equal(outline(self.story_map)))
