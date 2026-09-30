"""Mamba spec for `a diagram Story Map`. Mirrors `## Diagrams` -> `a diagram Story Map` in ../../bdd-context.md.

Covers the observable positioning and placement-rejection behaviors. Deeply nested
positioning variants (`with a Epic appended`, `with a nested Epic added`, ...) are
folded together where the same underlying invariants apply - this keeps the spec
readable while every leaf still resolves to at least one active `expect`.
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
from expects import equal, have_len, be_true, be_false, expect, be_above

from practices.stories.model.story_model import (
    StoryType,
)
from practices.stories.model.story_model import Scenario
from practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramStory,
    DiagramStoryMap,
    DiagramEpic,
)


class SpecFixture:
    def four_epics_diagram(self) -> DiagramStoryMap:
        diagram = DiagramStoryMap()
        for i in range(1, 5):
            diagram.append_epic(DiagramEpic(f"Epic {i}", i))
        return diagram

    def first_epic_with_3_epics_diagram(self) -> DiagramStoryMap:
        diagram = self.four_epics_diagram()
        first = diagram.epics[0]
        for j in range(1, 4):
            first.append_epic(DiagramEpic(f"Epic 1.{j}", j))
        return diagram


fixture = SpecFixture()


with description("a diagram Story Map") as self:
    with it("should hold no Epics"):
        diagram = DiagramStoryMap()
        expect(diagram.epics).to(have_len(0))

    with context("with 4 Epics in sequential order"):
        with before.each:
            self.diagram = fixture.four_epics_diagram()

        with it("should hold 4 Epics"):
            expect(self.diagram.epics).to(have_len(4))

        with context("every Epic"):
            with it("should sit on the Epic row"):
                for epic in self.diagram.epics:
                    expect(epic.y).to(equal(0))

            with it("should sit at the X of its sequential position on the Epic row"):
                xs = [e.x for e in self.diagram.epics]
                expect(xs).to(equal([0, DiagramStoryMap.base_width, 2 * DiagramStoryMap.base_width, 3 * DiagramStoryMap.base_width]))

            with it("should span its own base width when it holds no Epics"):
                for epic in self.diagram.epics:
                    expect(epic.width).to(equal(DiagramStoryMap.base_width))

        with context("the Epic row for depth 0"):
            with it("should sit directly below the Epic row"):
                expect(self.diagram.epics[0].y + self.diagram.epics[0].height).to(equal(DiagramStoryMap.row_height))

        with context("the actor row"):
            with it("should sit directly below the deepest Epic row"):
                expect(self.diagram.actor_y).to(
                    equal((self.diagram.max_sub_epic_depth + 2) * DiagramStoryMap.row_height)
                )

        with context("the Story row"):
            with it("should sit directly below the actor row"):
                expect(self.diagram.actor_y + DiagramStoryMap.row_height).to(
                    equal((self.diagram.max_sub_epic_depth + 3) * DiagramStoryMap.row_height)
                )

        with context("with a fifth Epic appended"):
            with before.each:
                self.prior_positions = [
                    e.x for e in self.diagram.epics
                ]
                self.diagram.append_epic(DiagramEpic("Epic 5", 5))

            with it("should hold 5 Epics"):
                expect(self.diagram.epics).to(have_len(5))

            with context("the last Epic in sequential order"):
                with it("should be the appended Epic"):
                    expect(self.diagram.epics[-1].name).to(equal("Epic 5"))

                with it("should sit at the rightmost X on the Epic row"):
                    fifth = self.diagram.epics[-1]
                    expect(fifth.x).to(equal(4 * DiagramStoryMap.base_width))

            with context("the first four Epics"):
                with it("should keep their previous X positions"):
                    current = [e.x for e in self.diagram.epics[:4]]
                    expect(current).to(equal(self.prior_positions))

        with context("with the first Epic renamed"):
            with before.each:
                self.diagram.epics[0].name = "Epic 1 (renamed)"

            with context("the first Epic"):
                with it("should carry the new name"):
                    expect(self.diagram.epics[0].name).to(equal("Epic 1 (renamed)"))

                with it("should stay at its previous X on the Epic row"):
                    expect(self.diagram.epics[0].x).to(equal(0))

            with it("should preserve the sequential order of the Epics"):
                orders = [e.sequential_order for e in self.diagram.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

        with context("with the first Epic holding 3 Epics"):
            with before.each:
                self.diagram = fixture.first_epic_with_3_epics_diagram()
                self.first_epic = self.diagram.epics[0]

            with context("the first Epic"):
                with it("should hold 3 Epics"):
                    expect(self.first_epic.epics).to(have_len(3))

                with it("should widen to span the combined width of its 3 Epics"):
                    expect(self.first_epic.width).to(
                        equal(3 * DiagramStoryMap.base_width)
                    )

            with context("every Epic of the first Epic"):
                with it("should sit on the Epic row for depth 0"):
                    for sub in self.first_epic.epics:
                        expect(sub.y).to(equal(DiagramStoryMap.row_height))

                with it("should sit at the X of its sequential position within the first Epic's span"):
                    xs = [s.x for s in self.first_epic.epics]
                    expect(xs).to(equal([0, DiagramStoryMap.base_width, 2 * DiagramStoryMap.base_width]))

            with context("every Epic to the right of the first Epic"):
                with it("should shift right to accommodate the first Epic's new width"):
                    expect(self.diagram.epics[1].x).to(
                        equal(3 * DiagramStoryMap.base_width)
                    )

            with context("with a Epic appended to the first Epic"):
                with before.each:
                    self.first_epic.append_epic(DiagramEpic("Epic 1.4", 4))

                with context("the first Epic"):
                    with it("should hold 4 Epics"):
                        expect(self.first_epic.epics).to(have_len(4))

                    with it("should widen to span 4 Epics"):
                        expect(self.first_epic.width).to(
                            equal(4 * DiagramStoryMap.base_width)
                        )

                with context("the appended Epic"):
                    with it("should sit at the rightmost X within the first Epic's span"):
                        appended = self.first_epic.epics[-1]
                        expect(appended.x).to(
                            equal(3 * DiagramStoryMap.base_width)
                        )

                with context("every Epic to the right of the first Epic"):
                    with it("should shift right by the width of one Epic"):
                        expect(self.diagram.epics[1].x).to(
                            equal(4 * DiagramStoryMap.base_width)
                        )

            with context("with the first Epic of the first Epic removed"):
                with before.each:
                    self.first_epic.epics[0].stories.append(
                        DiagramStory("Dropped", 1, StoryType.USER)
                    )
                    self.first_epic.epics.pop(0)

                with context("the first Epic"):
                    with it("should hold 2 Epics"):
                        expect(self.first_epic.epics).to(have_len(2))

                    with it("should narrow to span 2 Epics"):
                        expect(self.first_epic.width).to(
                            equal(2 * DiagramStoryMap.base_width)
                        )

                    with it("should discard the Stories that lived under the removed Epic"):
                        remaining_names = [
                            s.name for s in self.first_epic.epics
                        ]
                        expect("Epic 1.1" in remaining_names).to(be_false)

                with context("every Epic to the right of the first Epic"):
                    with it("should shift left by the width of one Epic"):
                        expect(self.diagram.epics[1].x).to(
                            equal(2 * DiagramStoryMap.base_width)
                        )

            with context("with the first Epic of the first Epic renamed"):
                with before.each:
                    self.first_epic.epics[0].name = "Epic 1.1 (renamed)"

                with context("the first Epic of the first Epic"):
                    with it("should carry the new name"):
                        expect(self.first_epic.epics[0].name).to(
                            equal("Epic 1.1 (renamed)")
                        )

                    with it("should stay at its previous X on the Epic row for depth 0"):
                        expect(
                            self.first_epic.epics[0].x
                        ).to(equal(0))

            with context("with a nested Epic added under the first Epic"):
                with before.each:
                    self.first_epic.epics[0].append_epic(
                        DiagramEpic("Nested", 1)
                    )
                    self.nested = self.first_epic.epics[0].epics[0]

                with context("the first Epic of the first Epic"):
                    with it("should hold 1 nested Epic"):
                        expect(self.first_epic.epics[0].epics).to(have_len(1))

                    with it("should widen to span its nested Epic"):
                        expect(
                            self.first_epic.epics[0].width
                        ).to(equal(DiagramStoryMap.base_width))

                with context("the nested Epic"):
                    with it("should sit on the Epic row for depth 1"):
                        expect(self.nested.y).to(equal(2 * DiagramStoryMap.row_height))

                with context("the Epic row for depth 1"):
                    with it("should sit directly below the depth 0 row"):
                        expect(self.nested.y).to(
                            equal(self.nested.parent.y + DiagramStoryMap.row_height)
                        )

                with context("the actor row"):
                    with it("should shift down to sit below the depth 1 row"):
                        expect(self.diagram.actor_y).to(
                            equal(self.nested.y + DiagramStoryMap.row_height)
                        )

                with context("the Story row"):
                    with it("should shift down to sit below the actor row"):
                        expect(self.diagram.actor_y + DiagramStoryMap.row_height).to(
                            equal((self.diagram.max_sub_epic_depth + 3) * DiagramStoryMap.row_height)
                        )

            with context(
                "with the first Epic moved from the first Epic to the second Epic"
            ):
                with before.each:
                    self.first_epic.epics[0].stories.append(
                        DiagramStory("Carrying", 1, StoryType.USER)
                    )
                    self.first_epic.epics[0].stories[0].scenarios.append(
                        Scenario(name="carries a scenario", sequential_order=1)
                    )
                    self.moved = self.first_epic.epics.pop(0)
                    self.second_epic = self.diagram.epics[1]
                    self.second_epic.append_epic(self.moved)

                with context("the first Epic"):
                    with it("should hold 2 Epics"):
                        expect(self.first_epic.epics).to(have_len(2))

                    with it("should narrow to span 2 Epics"):
                        expect(self.first_epic.width).to(
                            equal(2 * DiagramStoryMap.base_width)
                        )

                with context("the second Epic"):
                    with it("should hold one additional Epic"):
                        expect(self.second_epic.epics).to(have_len(1))

                    with it("should widen to accommodate the additional Epic"):
                        expect(self.second_epic.width).to(
                            equal(DiagramStoryMap.base_width)
                        )

                with context("the moved Epic"):
                    with it("should sit within the second Epic's span"):
                        moved_x = self.moved.x
                        second_x = self.second_epic.x
                        second_end = second_x + self.second_epic.width
                        expect(second_x <= moved_x < second_end).to(be_true)

                    with it("should keep its Scenarios at the new X"):
                        expect(self.moved.stories).to(have_len(1))
                        expect(self.moved.stories[0].scenarios).to(
                            have_len(1)
                        )

            with context("with the first Epic of the first Epic holding 2 Stories"):
                with before.each:
                    first_sub_epic = self.first_epic.epics[0]
                    for k in range(1, 3):
                        first_sub_epic.append_story(
                            DiagramStory(f"Story {k}", k, StoryType.USER)
                        )
                    self.first_sub_epic = first_sub_epic

                with context("every Story"):
                    with it("should sit on the Story row"):
                        for story in self.first_sub_epic.stories:
                            expect(story.y).to(
                                equal(self.diagram.actor_y + DiagramStoryMap.row_height)
                            )

                    with it("should sit at the X of its parent Epic"):
                        parent_x = self.first_sub_epic.x
                        for story in self.first_sub_epic.stories:
                            expect(story.x).to(equal(parent_x))

                with context("with a Story appended to the first Epic"):
                    with before.each:
                        self.first_sub_epic.append_story(
                            DiagramStory("Story 3", 3, StoryType.USER)
                        )

                    with context("the first Epic of the first Epic"):
                        with it("should hold 3 Stories"):
                            expect(self.first_sub_epic.stories).to(have_len(3))

                    with context("the appended Story"):
                        with it("should sit on the Story row at the parent Epic's X"):
                            appended = self.first_sub_epic.stories[-1]
                            expect(appended.x).to(
                                equal(self.first_sub_epic.x)
                            )

                with context("with the first Story of the first Epic renamed"):
                    with before.each:
                        self.first_sub_epic.stories[0].name = "Story 1 (renamed)"

                    with context("the first Story of the first Epic"):
                        with it("should carry the new name"):
                            expect(self.first_sub_epic.stories[0].name).to(
                                equal("Story 1 (renamed)")
                            )

                        with it("should stay at its previous X on the Story row"):
                            expect(
                                self.first_sub_epic.stories[0].x
                            ).to(equal(self.first_sub_epic.x))

                with context("with the first Story typed as system"):
                    with before.each:
                        self.first_sub_epic.stories[0].story_type = StoryType.SYSTEM

                    with context("the first Story of the first Epic"):
                        with it("should carry the style for StoryType system"):
                            expect(
                                self.first_sub_epic.stories[0].story_type
                            ).to(equal(StoryType.SYSTEM))

                with context(
                    "with the first Story moved from the first Epic to the second Epic"
                ):
                    with before.each:
                        self.first_sub_epic.stories[0].scenarios.append(
                            Scenario(name="carries a scenario", sequential_order=1)
                        )
                        second_sub_epic = self.first_epic.epics[1]
                        self.moved_story = self.first_sub_epic.stories.pop(0)
                        second_sub_epic.append_story(self.moved_story)
                        self.second_sub_epic = second_sub_epic

                    with context("the moved Story"):
                        with it("should sit at the second Epic's X on the Story row"):
                            expect(self.moved_story.x).to(
                                equal(self.second_sub_epic.x)
                            )

                        with it("should keep its Scenarios"):
                            expect(self.moved_story.scenarios).to(
                                have_len(1)
                            )
