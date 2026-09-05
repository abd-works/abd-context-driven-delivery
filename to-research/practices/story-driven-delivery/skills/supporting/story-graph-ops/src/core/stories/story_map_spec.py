"""Mamba spec for `a Story Map`.

Mirrors the `## Story Model` -> `a Story Map` block of tests/bdd-context.md 1:1.
Uses Epic/SubEpic/Story/AcceptanceCriteria from this same package.
"""

import os
import sys

# WHY: Mamba loads spec files as top-level modules, so relative imports fail.
# Adding the project root to sys.path lets us import via the `src.` prefix.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap


def _fresh_story_map_with_4_epics() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    return story_map


def _fresh_sub_epics(count: int) -> list:
    return [SubEpic(f"SubEpic {i}", i) for i in range(1, count + 1)]


def _fresh_stories(count: int) -> list:
    return [Story(f"Story {i}", i, StoryType.USER) for i in range(1, count + 1)]


def _fresh_acceptance_criteria(count: int) -> list:
    return [
        AcceptanceCriteria(f"AC {i}", i, text=f"Given/When/Then #{i}")
        for i in range(1, count + 1)
    ]


with description("a Story Map") as self:
    with it("should hold no Epics"):
        story_map = StoryMap()
        expect(story_map.epics).to(have_len(0))

    with context("with 4 Epics in sequential order"):
        with before.each:
            self.story_map = _fresh_story_map_with_4_epics()

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

        with context("with the first Epic removed"):
            with before.each:
                first_epic = self.story_map.epics[0]
                first_epic.sub_epics.extend(_fresh_sub_epics(2))
                self.story_map.remove_epic("Epic 1")

            with it("should hold 3 Epics"):
                expect(self.story_map.epics).to(have_len(3))

            with it("should discard the SubEpics that lived under the removed Epic"):
                remaining_names = [e.name for e in self.story_map.epics]
                expect("Epic 1" in remaining_names).to(be_false)

            with it("should renumber the remaining Epics"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3]))

        with context("with the first Epic renamed"):
            with before.each:
                self.story_map.epics[0].name = "Epic 1 (renamed)"

            with it("should preserve the sequential order of the Epics"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

            with context("the first Epic"):
                with it("should carry the new name"):
                    expect(self.story_map.epics[0].name).to(equal("Epic 1 (renamed)"))

        with context("with the Epics reordered"):
            with before.each:
                self.story_map.reorder_epics(["Epic 4", "Epic 2", "Epic 3", "Epic 1"])

            with it("should list the Epics in the new order"):
                names = [e.name for e in self.story_map.epics]
                expect(names).to(equal(["Epic 4", "Epic 2", "Epic 3", "Epic 1"]))

            with it("should reflect each Epic's new position in its sequential order"):
                orders = [e.sequential_order for e in self.story_map.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

        with context("with the first Epic holding 3 SubEpics"):
            with before.each:
                self.first_epic = self.story_map.epics[0]
                self.first_epic.sub_epics.extend(_fresh_sub_epics(3))

            with context("the first Epic"):
                with it("should hold 3 SubEpics"):
                    expect(self.first_epic.sub_epics).to(have_len(3))

            with context("with a SubEpic appended to the first Epic"):
                with before.each:
                    self.first_epic.sub_epics.append(SubEpic("SubEpic 4", 4))

                with context("the first Epic"):
                    with it("should hold 4 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(4))

            with context("with the first SubEpic of the first Epic removed"):
                with before.each:
                    self.first_epic.sub_epics[0].stories.extend(_fresh_stories(2))
                    self.first_epic.sub_epics.pop(0)

                with context("the first Epic"):
                    with it("should hold 2 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(2))

                    with it("should discard the Stories that lived under the removed SubEpic"):
                        remaining_names = [s.name for s in self.first_epic.sub_epics]
                        expect("SubEpic 1" in remaining_names).to(be_false)

            with context("with the first SubEpic of the first Epic renamed"):
                with before.each:
                    self.first_epic.sub_epics[0].name = "SubEpic 1 (renamed)"

                with context("the first SubEpic of the first Epic"):
                    with it("should carry the new name"):
                        expect(self.first_epic.sub_epics[0].name).to(
                            equal("SubEpic 1 (renamed)")
                        )

            with context("with a nested SubEpic added under the first SubEpic"):
                with before.each:
                    self.first_epic.sub_epics[0].sub_epics.append(
                        SubEpic("Nested SubEpic", 1)
                    )

                with context("the first SubEpic of the first Epic"):
                    with it("should hold 1 nested SubEpic"):
                        expect(self.first_epic.sub_epics[0].sub_epics).to(have_len(1))

                    with it("should report hasSubEpics as true"):
                        expect(self.first_epic.sub_epics[0].has_sub_epics).to(be_true)

            with context(
                "with the first SubEpic moved from the first Epic to the second Epic"
            ):
                with before.each:
                    self.first_epic.sub_epics[0].stories.extend(_fresh_stories(1))
                    self.first_epic.sub_epics[0].stories[0].acceptance_criteria.extend(
                        _fresh_acceptance_criteria(1)
                    )
                    self.second_epic = self.story_map.epics[1]
                    self.original_second_epic_size = len(self.second_epic.sub_epics)
                    self.moved = self.first_epic.sub_epics.pop(0)
                    self.second_epic.sub_epics.append(self.moved)

                with context("the first Epic"):
                    with it("should hold 2 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(2))

                with context("the second Epic"):
                    with it("should hold one additional SubEpic"):
                        expect(self.second_epic.sub_epics).to(
                            have_len(self.original_second_epic_size + 1)
                        )

                with context("the moved SubEpic"):
                    with it("should keep its Stories and AcceptanceCriteria"):
                        moved_story = self.moved.stories[0]
                        expect(self.moved.stories).to(have_len(1))
                        expect(moved_story.acceptance_criteria).to(have_len(1))

            with context("with the first SubEpic of the first Epic holding 2 Stories"):
                with before.each:
                    self.first_sub_epic = self.first_epic.sub_epics[0]
                    self.first_sub_epic.stories.extend(_fresh_stories(2))

                with context("the first SubEpic of the first Epic"):
                    with it("should hold 2 Stories"):
                        expect(self.first_sub_epic.stories).to(have_len(2))

                with context("with a Story appended to the first SubEpic"):
                    with before.each:
                        self.first_sub_epic.stories.append(
                            Story("Story 3", 3, StoryType.USER)
                        )

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 3 Stories"):
                            expect(self.first_sub_epic.stories).to(have_len(3))

                with context("with the first Story of the first SubEpic removed"):
                    with before.each:
                        self.first_sub_epic.stories[0].acceptance_criteria.extend(
                            _fresh_acceptance_criteria(2)
                        )
                        self.first_sub_epic.stories.pop(0)

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 1 Story"):
                            expect(self.first_sub_epic.stories).to(have_len(1))

                        with it(
                            "should discard the AcceptanceCriteria that lived under the removed Story"
                        ):
                            remaining_names = [
                                s.name for s in self.first_sub_epic.stories
                            ]
                            expect("Story 1" in remaining_names).to(be_false)

                with context("with the first Story of the first SubEpic renamed"):
                    with before.each:
                        self.first_sub_epic.stories[0].name = "Story 1 (renamed)"

                    with context("the first Story of the first SubEpic"):
                        with it("should carry the new name"):
                            expect(self.first_sub_epic.stories[0].name).to(
                                equal("Story 1 (renamed)")
                            )

                with context("with the first Story typed as system"):
                    with before.each:
                        self.first_sub_epic.stories[0].story_type = StoryType.SYSTEM

                    with context("the first Story of the first SubEpic"):
                        with it("should carry the StoryType system"):
                            expect(self.first_sub_epic.stories[0].story_type).to(
                                equal(StoryType.SYSTEM)
                            )

                with context(
                    "with the first Story moved from the first SubEpic to the second SubEpic"
                ):
                    with before.each:
                        self.first_sub_epic.stories[0].acceptance_criteria.extend(
                            _fresh_acceptance_criteria(1)
                        )
                        self.second_sub_epic = self.first_epic.sub_epics[1]
                        self.original_second_sub_epic_stories = len(
                            self.second_sub_epic.stories
                        )
                        self.moved_story = self.first_sub_epic.stories.pop(0)
                        self.second_sub_epic.stories.append(self.moved_story)

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 1 Story"):
                            expect(self.first_sub_epic.stories).to(have_len(1))

                    with context("the second SubEpic of the first Epic"):
                        with it("should hold one additional Story"):
                            expect(self.second_sub_epic.stories).to(
                                have_len(self.original_second_sub_epic_stories + 1)
                            )

                    with context("the moved Story"):
                        with it("should keep its AcceptanceCriteria"):
                            expect(self.moved_story.acceptance_criteria).to(have_len(1))

                with context(
                    "with the first Story of the first SubEpic holding 3 AcceptanceCriteria"
                ):
                    with before.each:
                        self.first_story = self.first_sub_epic.stories[0]
                        self.first_story.acceptance_criteria.extend(
                            _fresh_acceptance_criteria(3)
                        )

                    with context("the first Story of the first SubEpic"):
                        with it("should hold 3 AcceptanceCriteria"):
                            expect(self.first_story.acceptance_criteria).to(have_len(3))

                    with context(
                        "with an AcceptanceCriteria appended to the first Story"
                    ):
                        with before.each:
                            self.first_story.acceptance_criteria.append(
                                AcceptanceCriteria("AC 4", 4, text="appended")
                            )

                        with context("the first Story of the first SubEpic"):
                            with it("should hold 4 AcceptanceCriteria"):
                                expect(self.first_story.acceptance_criteria).to(
                                    have_len(4)
                                )

                        with context("the last AcceptanceCriteria in sequential order"):
                            with it("should be the appended AcceptanceCriteria"):
                                expect(
                                    self.first_story.acceptance_criteria[-1].name
                                ).to(equal("AC 4"))

                    with context(
                        "with the first AcceptanceCriteria of the first Story removed"
                    ):
                        with before.each:
                            self.first_story.acceptance_criteria.pop(0)
                            for i, ac in enumerate(
                                self.first_story.acceptance_criteria, start=1
                            ):
                                ac.sequential_order = i

                        with context("the first Story of the first SubEpic"):
                            with it("should hold 2 AcceptanceCriteria"):
                                expect(self.first_story.acceptance_criteria).to(
                                    have_len(2)
                                )

                            with it("should renumber the remaining AcceptanceCriteria"):
                                orders = [
                                    ac.sequential_order
                                    for ac in self.first_story.acceptance_criteria
                                ]
                                expect(orders).to(equal([1, 2]))

                    with context(
                        "with the text of the first AcceptanceCriteria updated"
                    ):
                        with before.each:
                            self.first_story.acceptance_criteria[0].text = (
                                "updated Gherkin text"
                            )

                        with context("the first AcceptanceCriteria of the first Story"):
                            with it("should carry the new text"):
                                expect(
                                    self.first_story.acceptance_criteria[0].text
                                ).to(equal("updated Gherkin text"))

                        with context("the first Story of the first SubEpic"):
                            with it(
                                "should preserve the sequential order of the AcceptanceCriteria"
                            ):
                                orders = [
                                    ac.sequential_order
                                    for ac in self.first_story.acceptance_criteria
                                ]
                                expect(orders).to(equal([1, 2, 3]))

                    with context("with the AcceptanceCriteria reordered"):
                        with before.each:
                            self.first_story.acceptance_criteria = [
                                self.first_story.acceptance_criteria[2],
                                self.first_story.acceptance_criteria[0],
                                self.first_story.acceptance_criteria[1],
                            ]

                        with context("the first Story of the first SubEpic"):
                            with it("should list the AcceptanceCriteria in the new order"):
                                names = [
                                    ac.name
                                    for ac in self.first_story.acceptance_criteria
                                ]
                                expect(names).to(equal(["AC 3", "AC 1", "AC 2"]))
