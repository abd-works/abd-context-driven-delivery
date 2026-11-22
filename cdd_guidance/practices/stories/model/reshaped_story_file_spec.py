"""A render written onto a story test that is already there: the file takes the scenarios' new shape and loses nothing.

Each language's part is only the setup: the format that reads and writes its story tests, and the Pack Order story
test as a person wrote it in that language, with a comment and a helper between its scenarios. Every example after
that is shared: the scenarios change (a step added, removed or renamed, a scenario added), the format renders them,
and the render is written onto the file. No example names a language."""

from expects import be_empty, contain, equal, expect
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.stories.model.fixtures.pack_orders_project import PACK_ORDERS_FILES, TESTS_ROOT
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel
from cdd_guidance.practices.stories.stories import Stories

_PACK = "Pack a paid order"
_REFUSE = "Refuse to pack an unpaid order"
_TWICE = "Pack an order twice"
_PACKS = "the Shop Clerk packs the Order"
_PACKS_RENAMED = "the Shop Clerk packs the paid Order"
_KEEPS = "the Order unpaid order keeps status submitted"
_LISTED = "the Shop Clerk sees the Order in the packed list"
_NO_LONGER = "no longer in the model"


def _scenario(name: str, order: int, steps: list[tuple[StepType, str, list[str]]]) -> Scenario:
    """A scenario of steps, each its phase, its words, and the words of the Ands chained onto it."""
    scenario = Scenario(name=name, sequential_order=order)
    for place, (phase, text, ands) in enumerate(steps, start=1):
        step = Step(text, phase, place)
        step.keyword = phase.value.capitalize()
        for and_place, and_text in enumerate(ands, start=1):
            chained = Step(and_text, phase, and_place)
            chained.keyword = "And"
            step.ands = [*step.ands, chained]
        scenario.steps.append(step)
    return scenario


def _pack_order(*, packs: str = _PACKS, listed: bool = False, keeps: bool = True, twice: bool = False) -> StoryModel:
    """The Pack Order story as its scenarios say it: as the story test has it, or with one change."""
    story = Story("Pack Order", 1)
    story.actors = ["Shop Clerk"]
    story.scenarios.append(_scenario(_PACK, 1, [
        (StepType.GIVEN, "the Shop keeps Order paid order", []),
        (StepType.WHEN, packs, []),
        (StepType.THEN, "the Order paid order has status packed", [_LISTED] if listed else []),
    ]))
    story.scenarios.append(_scenario(_REFUSE, 2, [
        (StepType.GIVEN, "the Shop keeps Order unpaid order", []),
        (StepType.WHEN, _PACKS, []),
        (StepType.THEN, 'the Shop refuses with "order 1002 is not paid"', [_KEEPS] if keeps else []),
    ]))
    if twice:
        story.scenarios.append(_scenario(_TWICE, 3, [(StepType.GIVEN, "the Shop keeps Order paid order", []), (StepType.WHEN, _PACKS, [])]))
    sub_epic = Epic("Pack Orders", 1)
    sub_epic.stories.append(story)
    epic = Epic("Fulfil Order", 1)
    epic.epics.append(sub_epic)
    story_map = StoryModel()
    story_map.epics.append(epic)
    return story_map


class StoryTestOnDisk:
    """The Pack Order story test a person wrote in one language, and the format that renders scenarios onto it."""

    def __init__(self, format_name: str, between_scenarios: str) -> None:
        self.adapter = Stories().formats.adapter(format_name)
        written = next(text for file, text in PACK_ORDERS_FILES[format_name].items() if "pack_order_story.test" in file)
        opening = next(line for line in written.splitlines() if _REFUSE in line)
        # What only the file holds: a comment and a helper between its two scenarios.
        self.between_scenarios = between_scenarios
        self.existing = written.replace(opening, f"{between_scenarios}\n\n{opening}")

    def reshaped_by(self, scenarios: StoryModel):
        """What the format answers when the scenarios are rendered and written onto the file."""
        return self.adapter.reshape(self._rendered(scenarios), self.existing)

    def reshaped_twice_by(self, scenarios: StoryModel) -> tuple[str, str]:
        """The text after the scenarios are written onto the file, and after they are written onto that text again."""
        rendered = self._rendered(scenarios)
        once = self.adapter.reshape(rendered, self.existing).text
        return once, self.adapter.reshape(rendered, once).text

    def lines_lost_in(self, text: str) -> list[str]:
        """Each line of the file that carried content and is in no line of text."""
        held = text.splitlines()
        return [line for line in self.existing.splitlines() if line.strip() and not any(line.strip() in kept for kept in held)]

    def steps_read_from(self, text: str, scenario: str) -> list[str]:
        """The words of each step the format reads back from text for the scenario, chained steps included."""
        story = self.adapter.story_file(f"{TESTS_ROOT}/fulfil-order/pack-orders/pack-order/pack_order_story.test", text).stories[0]
        found = next(each for each in story.scenarios if each.name == scenario)
        return [each.text for step in found.steps for each in (step, *step.ands)]

    def scenarios_read_from(self, text: str) -> list[str]:
        story = self.adapter.story_file(f"{TESTS_ROOT}/fulfil-order/pack-orders/pack-order/pack_order_story.test", text).stories[0]
        return [scenario.name for scenario in story.scenarios]

    def _rendered(self, scenarios: StoryModel) -> str:
        files = self.adapter.render(scenarios)
        return next(text for file, text in files.items() if self.adapter.is_story_file(file))


with shared_context("a render written onto the story test already there"):
    with context("with the scenarios as the story test has them"):
        with before.all:
            self.reshaped = self.story_test.reshaped_by(_pack_order())

        with it("should leave the file as it is"):
            expect(self.reshaped.text).to(equal(self.story_test.existing))

        with it("should keep nothing apart and add nothing"):
            expect((self.reshaped.kept, self.reshaped.added)).to(equal(([], [])))

    with context("with a step the scenarios gained"):
        with before.all:
            self.reshaped = self.story_test.reshaped_by(_pack_order(listed=True))

        with it("should lose no line the file holds"):
            expect(self.story_test.lines_lost_in(self.reshaped.text)).to(be_empty)

        with it("should name the step as added"):
            expect(self.reshaped.added).to(equal([f"Pack Order.{_PACK}.{_LISTED}"]))

        with it("should keep nothing apart"):
            expect(self.reshaped.kept).to(be_empty)

        with it("should write the step into its scenario, after the steps the scenario had"):
            expect(self.story_test.steps_read_from(self.reshaped.text, _PACK)[-1]).to(equal(_LISTED))

        with it("should leave the comment and the helper between the scenarios where they were"):
            text = self.reshaped.text
            expect(text.index(_PACK) < text.index(self.story_test.between_scenarios) < text.index(_REFUSE)).to(equal(True))

        with it("should change nothing when the same scenarios are rendered onto it again"):
            once, twice = self.story_test.reshaped_twice_by(_pack_order(listed=True))
            expect(twice).to(equal(once))

    with context("with a step the scenarios lost"):
        with before.all:
            self.reshaped = self.story_test.reshaped_by(_pack_order(keeps=False))

        with it("should lose no line the file holds"):
            expect(self.story_test.lines_lost_in(self.reshaped.text)).to(be_empty)

        with it("should name the step as kept"):
            expect(self.reshaped.kept).to(equal([f"Pack Order.{_REFUSE}.{_KEEPS}"]))

        with it("should mark the step as no longer in the model"):
            marked = [line for line in self.reshaped.text.splitlines() if _NO_LONGER in line]
            expect([_KEEPS in line for line in marked]).to(equal([True]))

        with it("should keep the step in its scenario, with its code"):
            expect(self.story_test.steps_read_from(self.reshaped.text, _REFUSE)).to(contain(_KEEPS))

        with it("should change nothing when the same scenarios are rendered onto it again"):
            once, twice = self.story_test.reshaped_twice_by(_pack_order(keeps=False))
            expect(twice).to(equal(once))

    with context("with a step the scenarios renamed"):
        with before.all:
            self.reshaped = self.story_test.reshaped_by(_pack_order(packs=_PACKS_RENAMED))

        with it("should lose no line the file holds"):
            expect(self.story_test.lines_lost_in(self.reshaped.text)).to(be_empty)

        with it("should keep the step under its old words, for its code to be moved"):
            expect(self.reshaped.kept).to(equal([f"Pack Order.{_PACK}.{_PACKS}"]))

        with it("should add the step under its new words, empty"):
            expect(self.reshaped.added).to(equal([f"Pack Order.{_PACK}.{_PACKS_RENAMED}"]))

        with it("should write the marking line directly above the step it keeps, not above the step it adds"):
            lines = self.reshaped.text.splitlines()
            below = lines[next(index for index, line in enumerate(lines) if _NO_LONGER in line) + 1]
            expect((_PACKS in below, _PACKS_RENAMED in below)).to(equal((True, False)))

        with it("should hold both steps in the scenario"):
            steps = self.story_test.steps_read_from(self.reshaped.text, _PACK)
            expect([_PACKS in steps, _PACKS_RENAMED in steps]).to(equal([True, True]))

    with context("with a scenario the scenarios gained"):
        with before.all:
            self.reshaped = self.story_test.reshaped_by(_pack_order(twice=True))

        with it("should lose no line the file holds"):
            expect(self.story_test.lines_lost_in(self.reshaped.text)).to(be_empty)

        with it("should name the scenario as added"):
            expect(self.reshaped.added).to(equal([f"Pack Order.{_TWICE}"]))

        with it("should write the scenario after the scenarios the story had"):
            expect(self.story_test.scenarios_read_from(self.reshaped.text)).to(equal([_PACK, _REFUSE, _TWICE]))

        with it("should change nothing when the same scenarios are rendered onto it again"):
            once, twice = self.story_test.reshaped_twice_by(_pack_order(twice=True))
            expect(twice).to(equal(once))

    with context("with a file that holds no story, such as a step library"):
        with it("should leave the file as it is"):
            library = "the step library a person changed\n"
            expect(self.story_test.adapter.reshape("the step library as it is seeded\n", library).text).to(equal(library))


with description("scenarios rendered onto a story test") as self:
    with context("written in Python"):
        with before.all:
            self.story_test = StoryTestOnDisk("python", "    # the shop packs at most three orders a day\n    daily_limit = 3")

        with included_context("a render written onto the story test already there"):
            pass

    with context("written in TypeScript"):
        with before.all:
            self.story_test = StoryTestOnDisk("typescript", "  // the shop packs at most three orders a day\n  const dailyLimit = 3;")

        with included_context("a render written onto the story test already there"):
            pass

    with context("written in JavaScript"):
        with before.all:
            self.story_test = StoryTestOnDisk("javascript", "  // the shop packs at most three orders a day\n  const dailyLimit = 3;")

        with included_context("a render written onto the story test already there"):
            pass
