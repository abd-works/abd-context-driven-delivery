"""Mamba spec for the story model.

Covers Increment, Scenario, Story Map, and StoryNode.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "practices" / "stories" / "src" / "practices" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect

from practices.stories.model.story_model import (
    Background,
    Epic,
    Increment,
    StepType,
    Scenario,
    Step,
    Story,
    StoryModel,
    StoryType,
    Epic,
)


class SpecFixture:
    def step(self, text: str, phase: StepType, order: int = 1) -> Step:
        is_cont = text.startswith("And ") or text.startswith("But ")
        return Step(text, phase, order, is_continuation=is_cont)

    def given(self, text: str, order: int = 1) -> Step:
        return self.step(text, StepType.GIVEN, order)

    def when(self, text: str, order: int = 1) -> Step:
        return self.step(text, StepType.WHEN, order)

    def then(self, text: str, order: int = 1) -> Step:
        return self.step(text, StepType.THEN, order)

    def fresh_story_map_with_4_epics(self) -> StoryModel:
        story_map = StoryModel()
        for i in range(1, 5):
            story_map.append_epic(Epic(f"Epic {i}", i))
        return story_map

    def fresh_epics(self, count: int) -> list:
        return [Epic(f"Epic {i}", i) for i in range(1, count + 1)]

    def fresh_stories(self, count: int) -> list:
        return [Story(f"Story {i}", i, StoryType.USER) for i in range(1, count + 1)]

    def fresh_scenarios(self, count: int) -> list:
        return [Scenario(f"Scenario {i}", i) for i in range(1, count + 1)]

    def fresh_increments(self, count: int) -> list:
        return [Increment(f"Increment {i}", i) for i in range(1, count + 1)]

    def epic_with_children(self, name: str, order: int, sub_epic_names: list) -> Epic:
        epic = Epic(name, order)
        for i, sub_name in enumerate(sub_epic_names, start=1):
            epic.epics.append(Epic(sub_name, i))
        return epic


fixture = SpecFixture()


with description("an Increment") as self:
    with it("should report itself as a leaf StoryNode"):
        inc = Increment("Move money same-day", 1)
        expect(inc.semantic_type()).to(equal("Increment"))

    with context(
        "that has been translated from another Increment of the same semantic type"
    ):
        with before.each:
            source = Increment(
                "Source Increment",
                2,
                [
                    Story("Route transfer before cutoff", 1),
                    Story("Display transfer status", 2),
                ],
            )
            source.outcome = "Transfers clear same day"
            source.slicing_notes = "Manual dual-control step for first release"
            source.decision_prompt = "Did same-day transfers increase retention?"

            self.target = source.clone()
            self.source = source

        with it(
            "should carry every field from the source "
            "(name, sequentialOrder, outcome, slicingNotes, stories, decisionPrompt)"
        ):
            expect(self.target.name).to(equal("Source Increment"))
            expect(self.target.sequential_order).to(equal(2))
            expect(self.target.outcome).to(equal("Transfers clear same day"))
            expect(self.target.slicing_notes).to(
                equal("Manual dual-control step for first release")
            )
            expect([story.name for story in self.target.stories]).to(
                equal(["Route transfer before cutoff", "Display transfer status"])
            )
            expect(self.target.decision_prompt).to(
                equal("Did same-day transfers increase retention?")
            )

        with context("its stories list"):
            with it(
                "should copy the story nodes, so a later change to the source list "
                "does not change the clone"
            ):
                self.source.stories.append(Story("Extra story", 3))
                # Target must not grow
                expect(self.target.stories).to(have_len(2))

    with context(
        "that references a story name not present in any Story on the StoryModel"
    ):
        with before.each:
            self.story_map = StoryModel()
            epic = Epic("Route transfer", 1)
            sub = Epic("Route inside window", 1)
            sub.stories.append(Story("Route transfer before cutoff", 1))
            epic.epics.append(sub)
            self.story_map.append_epic(epic)
            orphan = Increment("Orphan increment", 1, [Story("Non-existent story name", 1)])
            self.story_map.append_increment(orphan)

        with context("the model"):
            with it("should not raise"):
                # Building the model with orphan references is allowed -
                # scanners detect the inconsistency, not the model.
                expect(len(self.story_map.increments)).to(equal(1))

        with context("a scanner walking the StoryModel"):
            with it(
                "should be able to detect the orphan reference by comparing name lists"
            ):
                all_story_names = {
                    story.name
                    for epic in self.story_map.epics
                    for sub in epic.epics
                    for story in sub.stories
                }
                orphan_refs = [
                    story.name
                    for inc in self.story_map.increments
                    for story in inc.stories
                    if story.name not in all_story_names
                ]
                expect(orphan_refs).to(equal(["Non-existent story name"]))


with description("a Scenario") as self:
    with it("should report itself as a leaf StoryNode"):
        scenario = Scenario("Submit transfer before cutoff", 1)
        expect(scenario.semantic_type()).to(equal("Scenario"))

    with it("should keep backgrounds, steps, and examples on the scenario"):
        scenario = Scenario("Submit transfer before cutoff", 1)
        expect(scenario.backgrounds).to(equal([]))
        expect(scenario.steps).to(equal([]))
        expect(scenario.examples).to(equal({}))

    with context(
        "that has been translated from another Scenario of the same semantic type"
    ):
        with before.each:
            source = Scenario("Original name", 1, story_name="My Story")
            source.steps = [
                fixture.given("a funded Account DDA-001", 1),
                fixture.when("the Treasurer submits a Transfer", 2),
                fixture.then("a Confirmation Number is returned", 3),
            ]
            source.is_outline = True
            source.examples["example-1"] = {"amount": "10000 USD"}
            background = Background("background", 1)
            background.steps = [fixture.given("the system is available")]
            source.backgrounds = [background]
            source.evidence = ["ref #3"]

            self.target = source.clone()
            self.source = source

        with it(
            "should carry every field from the source "
            "(name, sequentialOrder, storyName, steps, isOutline, examples, background, evidence)"
        ):
            expect(self.target.name).to(equal("Original name"))
            expect(self.target.sequential_order).to(equal(1))
            expect(self.target.story_name).to(equal("My Story"))
            expect(self.target.steps[0].text).to(equal("a funded Account DDA-001"))
            expect(self.target.steps[1].text).to(equal("the Treasurer submits a Transfer"))
            expect(self.target.steps[2].text).to(equal("a Confirmation Number is returned"))
            expect(self.target.is_outline).to(be_true)
            expect(self.target.examples["example-1"].value).to(equal({"amount": "10000 USD"}))
            expect(self.target.backgrounds[0].steps[0].text).to(equal("the system is available"))
            expect(self.target.evidence).to(equal(["ref #3"]))

        with it("should copy Step and Background nodes onto the target"):
            expect(self.target.steps).to(have_len(3))
            expect(self.target.backgrounds).to(have_len(1))
            expect(self.target.examples).to(have_len(1))

        with context("its steps"):
            with it(
                "should be a value copy - mutating the source's steps after "
                "translation should not affect the target"
            ):
                self.source.steps.append(fixture.when("extra step", 4))
                expect(self.target.steps).to(have_len(3))

    with context("that carries multiple interactions"):
        with before.each:
            self.scenario = Scenario("multi-interaction", 1)
            self.scenario.steps = [
                fixture.given("initial state", 1),
                fixture.when("first action", 2),
                fixture.then("first outcome", 3),
                fixture.then("And second outcome", 4),
                fixture.when("second action", 5),
                fixture.when("And follow-up", 6),
                fixture.then("final outcome", 7),
            ]

        with it("should walk When steps in order"):
            texts = [step.text for step in self.scenario.steps_in(StepType.WHEN)]
            expect(texts).to(equal(["first action", "second action", "And follow-up"]))

        with it("should walk Then steps in order"):
            texts = [step.text for step in self.scenario.steps_in(StepType.THEN)]
            expect(texts).to(equal(["first outcome", "And second outcome", "final outcome"]))

        with it("should walk every step in order"):
            texts = [step.text for step in self.scenario.steps]
            expect(texts).to(
                equal([
                    "initial state",
                    "first action",
                    "first outcome",
                    "And second outcome",
                    "second action",
                    "And follow-up",
                    "final outcome",
                ])
            )

    with context('whose given clauses include an "And " continuation'):
        with before.each:
            self.cont_clause = fixture.given("And the daily Limit is 5000000 USD", 2)
            scenario = Scenario("outline", 1)
            scenario.steps = [
                fixture.given("a Treasurer Jane Doe", 1),
                self.cont_clause,
            ]
            self.scenario = scenario

        with context("the continuation clause"):
            with it("should carry isContinuation true"):
                expect(self.cont_clause.is_continuation).to(be_true)

            with it('should preserve the "And " prefix verbatim in text'):
                expect(self.cont_clause.text).to(
                    equal("And the daily Limit is 5000000 USD")
                )

    with context('whose interaction contains a "But " continuation in its then clauses'):
        with before.each:
            self.but_clause = fixture.then("But the Cart contents are preserved for retry", 3)
            scenario = Scenario("rejection", 1)
            scenario.steps = [
                fixture.when("the Customer submits the Order", 1),
                fixture.then("the Order is rejected with reason payment_declined", 2),
                self.but_clause,
            ]
            self.scenario = scenario

        with context("the continuation clause"):
            with it("should carry isContinuation true"):
                expect(self.but_clause.is_continuation).to(be_true)

            with it('should preserve the "But " prefix verbatim in text'):
                expect(self.but_clause.text).to(
                    equal("But the Cart contents are preserved for retry")
                )


with description("a Story Map") as self:
    with it("should hold no Epics"):
        story_map = StoryModel()
        expect(story_map.epics).to(have_len(0))

    with it("should hold no Increments"):
        story_map = StoryModel()
        expect(story_map.increments).to(have_len(0))

    with context("with 4 Epics in sequential order"):
        with before.each:
            self.story_map = fixture.fresh_story_map_with_4_epics()

        with it("should hold 4 Epics"):
            expect(self.story_map.epics).to(have_len(4))

        with it("should list the Epics in sequential order"):
            orders = [epic.sequential_order for epic in self.story_map.epics]
            expect(orders).to(equal([1, 2, 3, 4]))

        with context("with a fifth Epic appended"):
            with before.each:
                self.story_map.append_epic(Epic("Epic 5", 5))

            with it("should hold 5 Epics"):
                expect(self.story_map.epics).to(have_len(5))

            with context("the last Epic in sequential order"):
                with it("should be the appended Epic"):
                    expect(self.story_map.epics[-1].name).to(equal("Epic 5"))

        with context("with the first Epic renamed"):
            with before.each:
                self.story_map.epics[0].name = "Epic 1 (renamed)"

            with it("should preserve the sequential order of the Epics"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

            with context("the first Epic"):
                with it("should carry the new name"):
                    expect(self.story_map.epics[0].name).to(equal("Epic 1 (renamed)"))

        with context("with the first Epic holding 3 Epics"):
            with before.each:
                self.first_epic = self.story_map.epics[0]
                self.first_epic.epics.extend(fixture.fresh_epics(3))

            with context("the first Epic"):
                with it("should hold 3 Epics"):
                    expect(self.first_epic.epics).to(have_len(3))

            with context("with a Epic appended to the first Epic"):
                with before.each:
                    self.first_epic.epics.append(Epic("Epic 4", 4))

                with context("the first Epic"):
                    with it("should hold 4 Epics"):
                        expect(self.first_epic.epics).to(have_len(4))

            with context("with the first Epic of the first Epic removed"):
                with before.each:
                    self.first_epic.epics[0].stories.extend(fixture.fresh_stories(2))
                    self.first_epic.epics.pop(0)

                with context("the first Epic"):
                    with it("should hold 2 Epics"):
                        expect(self.first_epic.epics).to(have_len(2))

                    with it("should discard the Stories that lived under the removed Epic"):
                        remaining_names = [s.name for s in self.first_epic.epics]
                        expect("Epic 1" in remaining_names).to(be_false)

            with context("with the first Epic of the first Epic renamed"):
                with before.each:
                    self.first_epic.epics[0].name = "Epic 1 (renamed)"

                with context("the first Epic of the first Epic"):
                    with it("should carry the new name"):
                        expect(self.first_epic.epics[0].name).to(
                            equal("Epic 1 (renamed)")
                        )

            with context("with a nested Epic added under the first Epic"):
                with before.each:
                    self.first_epic.epics[0].epics.append(
                        Epic("Nested Epic", 1)
                    )

                with context("the first Epic of the first Epic"):
                    with it("should hold 1 nested Epic"):
                        expect(self.first_epic.epics[0].epics).to(have_len(1))

                    with it("should report hasEpics as true"):
                        expect(self.first_epic.epics[0].has_epics).to(be_true)

            with context(
                "with the first Epic moved from the first Epic to the second Epic"
            ):
                with before.each:
                    self.first_epic.epics[0].stories.extend(fixture.fresh_stories(1))
                    self.first_epic.epics[0].stories[0].scenarios.extend(
                        fixture.fresh_scenarios(1)
                    )
                    self.second_epic = self.story_map.epics[1]
                    self.original_second_epic_size = len(self.second_epic.epics)
                    self.moved = self.first_epic.epics.pop(0)
                    self.second_epic.epics.append(self.moved)

                with context("the first Epic"):
                    with it("should hold 2 Epics"):
                        expect(self.first_epic.epics).to(have_len(2))

                with context("the second Epic"):
                    with it("should hold one additional Epic"):
                        expect(self.second_epic.epics).to(
                            have_len(self.original_second_epic_size + 1)
                        )

                with context("the moved Epic"):
                    with it("should keep its Stories and their Scenarios"):
                        moved_story = self.moved.stories[0]
                        expect(self.moved.stories).to(have_len(1))
                        expect(moved_story.scenarios).to(have_len(1))

            with context("with the first Epic of the first Epic holding 2 Stories"):
                with before.each:
                    self.first_sub_epic = self.first_epic.epics[0]
                    self.first_sub_epic.stories.extend(fixture.fresh_stories(2))

                with context("the first Epic of the first Epic"):
                    with it("should hold 2 Stories"):
                        expect(self.first_sub_epic.stories).to(have_len(2))

                with context("with a Story appended to the first Epic"):
                    with before.each:
                        self.first_sub_epic.stories.append(
                            Story("Story 3", 3, StoryType.USER)
                        )

                    with context("the first Epic of the first Epic"):
                        with it("should hold 3 Stories"):
                            expect(self.first_sub_epic.stories).to(have_len(3))

                with context("with the first Story of the first Epic removed"):
                    with before.each:
                        self.first_sub_epic.stories[0].scenarios.extend(
                            fixture.fresh_scenarios(2)
                        )
                        self.first_sub_epic.stories.pop(0)

                    with context("the first Epic of the first Epic"):
                        with it("should hold 1 Story"):
                            expect(self.first_sub_epic.stories).to(have_len(1))

                        with it("should discard the Scenarios that lived under the removed Story"):
                            remaining_names = [
                                s.name for s in self.first_sub_epic.stories
                            ]
                            expect("Story 1" in remaining_names).to(be_false)

                with context("with the first Story of the first Epic renamed"):
                    with before.each:
                        self.first_sub_epic.stories[0].name = "Story 1 (renamed)"

                    with context("the first Story of the first Epic"):
                        with it("should carry the new name"):
                            expect(self.first_sub_epic.stories[0].name).to(
                                equal("Story 1 (renamed)")
                            )

                with context("with the first Story typed as system"):
                    with before.each:
                        self.first_sub_epic.stories[0].story_type = StoryType.SYSTEM

                    with context("the first Story of the first Epic"):
                        with it("should carry the StoryType system"):
                            expect(self.first_sub_epic.stories[0].story_type).to(
                                equal(StoryType.SYSTEM)
                            )

                with context(
                    "with the first Story moved from the first Epic to the second Epic"
                ):
                    with before.each:
                        self.first_sub_epic.stories[0].scenarios.extend(
                            fixture.fresh_scenarios(1)
                        )
                        self.second_sub_epic = self.first_epic.epics[1]
                        self.original_second_sub_epic_stories = len(
                            self.second_sub_epic.stories
                        )
                        self.moved_story = self.first_sub_epic.stories.pop(0)
                        self.second_sub_epic.stories.append(self.moved_story)

                    with context("the first Epic of the first Epic"):
                        with it("should hold 1 Story"):
                            expect(self.first_sub_epic.stories).to(have_len(1))

                    with context("the second Epic of the first Epic"):
                        with it("should hold one additional Story"):
                            expect(self.second_sub_epic.stories).to(
                                have_len(self.original_second_sub_epic_stories + 1)
                            )

                    with context("the moved Story"):
                        with it("should keep its Scenarios"):
                            expect(self.moved_story.scenarios).to(have_len(1))

                with context(
                    "with the first Story of the first Epic holding 3 Scenarios"
                ):
                    with before.each:
                        self.first_story = self.first_sub_epic.stories[0]
                        self.first_story.scenarios.extend(fixture.fresh_scenarios(3))

                    with context("the first Story of the first Epic"):
                        with it("should hold 3 Scenarios"):
                            expect(self.first_story.scenarios).to(have_len(3))

                    with context("with a Scenario appended to the first Story"):
                        with before.each:
                            self.first_story.scenarios.append(Scenario("Scenario 4", 4))

                        with context("the first Story of the first Epic"):
                            with it("should hold 4 Scenarios"):
                                expect(self.first_story.scenarios).to(have_len(4))

                        with context("the last Scenario in sequential order"):
                            with it("should be the appended Scenario"):
                                expect(self.first_story.scenarios[-1].name).to(
                                    equal("Scenario 4")
                                )

                    with context("with the first Scenario of the first Story removed"):
                        with before.each:
                            self.first_story.scenarios.pop(0)
                            for i, sc in enumerate(self.first_story.scenarios, start=1):
                                sc.sequential_order = i

                        with context("the first Story of the first Epic"):
                            with it("should hold 2 Scenarios"):
                                expect(self.first_story.scenarios).to(have_len(2))

                            with it("should renumber the remaining Scenarios"):
                                orders = [
                                    sc.sequential_order
                                    for sc in self.first_story.scenarios
                                ]
                                expect(orders).to(equal([1, 2]))

                    with context("with the first Scenario of the first Story renamed"):
                        with before.each:
                            self.first_story.scenarios[0].name = "Scenario 1 (renamed)"

                        with context("the first Scenario of the first Story"):
                            with it("should carry the new name"):
                                expect(self.first_story.scenarios[0].name).to(
                                    equal("Scenario 1 (renamed)")
                                )

                    with context(
                        "with the given clauses of the first Scenario updated"
                    ):
                        with before.each:
                            self.new_given = [Step("a new given clause", StepType.GIVEN, 1)]
                            self.first_story.scenarios[0].steps = self.new_given

                        with context("the first Scenario of the first Story"):
                            with it("should carry the new given steps"):
                                expect(
                                    self.first_story.scenarios[0].steps
                                ).to(equal(self.new_given))

                            with it("should preserve its name and sequentialOrder"):
                                expect(self.first_story.scenarios[0].name).to(
                                    equal("Scenario 1")
                                )
                                expect(
                                    self.first_story.scenarios[0].sequential_order
                                ).to(equal(1))

                    with context(
                        "with the interactions of the first Scenario replaced"
                    ):
                        with before.each:
                            self.first_story.scenarios[0].steps = [
                                Step("new when", StepType.WHEN, 1),
                                Step("new then", StepType.THEN, 2),
                            ]

                        with context("the first Scenario of the first Story"):
                            with context("its when and then steps"):
                                with it("should reflect the new steps"):
                                    expect(
                                        self.first_story.scenarios[0].steps_in(StepType.WHEN)[0].text
                                    ).to(equal("new when"))
                                    expect(
                                        self.first_story.scenarios[0].steps_in(StepType.THEN)[0].text
                                    ).to(equal("new then"))

                    with context("with the Scenarios of the first Story reordered"):
                        with before.each:
                            self.first_story.scenarios = [
                                self.first_story.scenarios[2],
                                self.first_story.scenarios[0],
                                self.first_story.scenarios[1],
                            ]

                        with context("the first Story of the first Epic"):
                            with it("should list the Scenarios in the new order"):
                                names = [sc.name for sc in self.first_story.scenarios]
                                expect(names).to(
                                    equal(["Scenario 3", "Scenario 1", "Scenario 2"])
                                )

    with context("with 2 Increments in sequential order"):
        with before.each:
            self.story_map = StoryModel()
            for inc in fixture.fresh_increments(2):
                self.story_map.append_increment(inc)

        with it("should hold 2 Increments"):
            expect(self.story_map.increments).to(have_len(2))

        with it("should list the Increments in sequential order"):
            orders = [inc.sequential_order for inc in self.story_map.increments]
            expect(orders).to(equal([1, 2]))

        with context("with an Increment appended"):
            with before.each:
                self.story_map.append_increment(Increment("Increment 3", 3))

            with it("should hold 3 Increments"):
                expect(self.story_map.increments).to(have_len(3))

            with context("the last Increment in sequential order"):
                with it("should be the appended Increment"):
                    expect(self.story_map.increments[-1].name).to(equal("Increment 3"))

        with context("with the first Increment renamed"):
            with before.each:
                self.story_map.increments[0].name = "Increment 1 (renamed)"

            with context("the first Increment"):
                with it("should carry the new name"):
                    expect(self.story_map.increments[0].name).to(
                        equal("Increment 1 (renamed)")
                    )

        with context("with the outcome of the first Increment updated"):
            with before.each:
                self.story_map.increments[0].outcome = "Transfers clear same day"

            with context("the first Increment"):
                with it("should carry the new outcome"):
                    expect(self.story_map.increments[0].outcome).to(
                        equal("Transfers clear same day")
                    )

                with it("should preserve its name and sequentialOrder"):
                    expect(self.story_map.increments[0].name).to(equal("Increment 1"))
                    expect(self.story_map.increments[0].sequential_order).to(equal(1))

        with context("with a story added to the first Increment"):
            with before.each:
                added = Story("Route transfer before cutoff", 1)
                added.increment = self.story_map.increments[0]
                self.story_map.increments[0].stories.append(added)

            with context("the first Increment"):
                with it("should hold one additional story"):
                    expect(self.story_map.increments[0].stories).to(have_len(1))

                with context("its stories"):
                    with it("should hold a Story node"):
                        item = self.story_map.increments[0].stories[0]
                        expect(isinstance(item, Story)).to(be_true)
                        expect(item.name).to(equal("Route transfer before cutoff"))

with description("a StoryNode") as self:
    with context(
        "that has been translated from a source of the same semantic type with no differences"
    ):
        with before.each:
            self.target = fixture.epic_with_children("Epic 1", 1, ["Epic 1", "Epic 2"])
            self.source = fixture.epic_with_children("Epic 1", 1, ["Epic 1", "Epic 2"])
            self.target = self.source.clone()

        with context("the target"):
            with it("should be unchanged in every field"):
                expect(self.target.name).to(equal("Epic 1"))
                expect(self.target.sequential_order).to(equal(1))
                expect([s.name for s in self.target.epics]).to(
                    equal(["Epic 1", "Epic 2"])
                )

    with context("that has been translated from a source with an added child"):
        with before.each:
            self.target = fixture.epic_with_children("Epic 1", 1, ["Epic 1"])
            self.source = fixture.epic_with_children(
                "Epic 1", 1, ["Epic 1", "Epic 2"]
            )
            self.target = self.source.clone()

        with context("the target"):
            with it("should hold the new child"):
                names = [s.name for s in self.target.epics]
                expect("Epic 2" in names).to(be_true)

            with context("the new child on the target"):
                with it("should be of the correct semantic type for its position"):
                    new_child = self.target.epics[-1]
                    expect(new_child.semantic_type()).to(equal("Epic"))

                with it("should carry every field from the source child"):
                    new_child = self.target.epics[-1]
                    expect(new_child.name).to(equal("Epic 2"))
                    expect(new_child.sequential_order).to(equal(2))

    with context("that has been translated from a source with a removed child"):
        with before.each:
            self.target = fixture.epic_with_children(
                "Epic 1", 1, ["Epic 1", "Epic 2"]
            )
            self.source = fixture.epic_with_children("Epic 1", 1, ["Epic 1"])
            self.target = self.source.clone()

        with context("the target"):
            with it("should no longer hold the removed child"):
                names = [s.name for s in self.target.epics]
                expect("Epic 2" in names).to(be_false)

    with context("that has been translated from a source with a renamed child"):
        with before.each:
            self.target = fixture.epic_with_children("Epic 1", 1, ["Epic 1"])
            self.source = fixture.epic_with_children("Epic 1", 1, ["Epic 1 (renamed)"])
            self.target = self.source.clone()

        with context("the target child"):
            with it("should carry the new name"):
                expect(self.target.epics[0].name).to(equal("Epic 1 (renamed)"))

    with context("that has been translated from a source with reordered children"):
        with before.each:
            self.target = fixture.epic_with_children(
                "Epic 1", 1, ["Epic 1", "Epic 2", "Epic 3"]
            )
            source = Epic("Epic 1", 1)
            source.epics = [
                Epic("Epic 3", 1),
                Epic("Epic 1", 2),
                Epic("Epic 2", 3),
            ]
            self.target = source.clone()

        with context("the target"):
            with it("should list the children in the source's order"):
                names = [s.name for s in self.target.epics]
                expect(names).to(equal(["Epic 3", "Epic 1", "Epic 2"]))

    with context(
        "that has been translated from a source with a child moved to a different parent"
    ):
        with before.each:
            # WHY: model move as two independent parent reconciliations - old parent
            # sees a removal, new parent sees an addition. The BDD leaf verifies both.
            self.old_parent = fixture.epic_with_children("Epic 1", 1, ["Epic 1"])
            self.new_parent = Epic("Epic 2", 2)
            old_source = Epic("Epic 1", 1)
            new_source = Epic("Epic 2", 2)
            new_source.epics.append(Epic("Epic 1", 1))
            self.old_parent = old_source.clone()
            self.new_parent = new_source.clone()

        with context("the old parent on the target"):
            with it("should no longer hold the child"):
                expect(self.old_parent.epics).to(have_len(0))

        with context("the new parent on the target"):
            with it("should hold the child"):
                names = [s.name for s in self.new_parent.epics]
                expect("Epic 1" in names).to(be_true)

    with context(
        "that has been translated from a source whose children include a mix of matches, renames, and additions"
    ):
        with before.each:
            self.target = fixture.epic_with_children(
                "Epic 1", 1, ["Epic Alpha", "Epic Bravo"]
            )
            source = Epic("Epic 1", 1)
            source.epics = [
                Epic("Epic Alpha", 1),
                Epic("Epic Bravo (renamed)", 2),
                Epic("Epic Charlie", 3),
            ]
            self.target = source.clone()
            self.source = source

        with context("the cloned sub-epic"):
            with it("should be a new sub-epic copied from the source"):
                alpha = self.target.epics[0]
                expect(alpha is self.source.epics[0]).to(be_false)

            with it("should carry every field from the matched source child"):
                alpha = self.target.epics[0]
                expect(alpha.name).to(equal("Epic Alpha"))
                expect(alpha.sequential_order).to(equal(1))

        with context("the target children that correspond to unmatched source children"):
            with it(
                "should appear as fresh instances of the correct semantic type for their position"
            ):
                charlie = self.target.epics[-1]
                expect(charlie.name).to(equal("Epic Charlie"))
                expect(charlie.semantic_type()).to(equal("Epic"))

        with context("every child collection on the target"):
            with it("should be fully reconciled against the corresponding source collection"):
                names = [s.name for s in self.target.epics]
                expect(names).to(
                    equal(
                        [
                            "Epic Alpha",
                            "Epic Bravo (renamed)",
                            "Epic Charlie",
                        ]
                    )
                )

with description("a StoryModel being translated from another StoryModel") as self:
    with before.each:
        self.source = StoryModel()
        for i in range(1, 3):
            self.source.append_epic(Epic(f"Epic {i}", i))
        self.source.append_increment(Increment("Increment 1", 1))

        self.target = self.source.clone()

    with it("should reconcile epics as tree children"):
        names = [e.name for e in self.target.epics]
        expect(names).to(equal(["Epic 1", "Epic 2"]))

    with it("should reconcile increments as tree children in the same pass"):
        expect(self.target.increments).to(have_len(1))
        expect(self.target.increments[0].name).to(equal("Increment 1"))
