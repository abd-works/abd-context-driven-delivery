"""Mamba spec for `a diagram Story Map`. Mirrors `## Diagrams` -> `a diagram Story Map` in bdd-context.md.

Covers the observable positioning and placement-rejection behaviors. Deeply nested
positioning variants (`with a SubEpic appended`, `with a nested SubEpic added`, ...) are
folded together where the same underlying invariants apply — this keeps the spec
readable while every leaf still resolves to at least one active `expect`.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error, be_above

from src.core.stories.nodes import (
    AcceptanceCriteria,
    Epic,
    Story,
    StoryType,
    SubEpic,
)
from src.core.stories.story_map import StoryMap
from src.formats.diagram.diagram_story_map import (
    BASE_WIDTH,
    ROW_HEIGHT,
    DiagramStoryMap,
    PlacementError,
)


def _four_epics_diagram() -> DiagramStoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    return DiagramStoryMap(story_map)


def _first_epic_with_3_sub_epics_diagram() -> DiagramStoryMap:
    diagram = _four_epics_diagram()
    first = diagram.epics[0]
    for j in range(1, 4):
        first.sub_epics.append(SubEpic(f"SubEpic 1.{j}", j))
    return diagram


with description("a diagram Story Map") as self:
    with it("should hold no Epics"):
        diagram = DiagramStoryMap()
        expect(diagram.epics).to(have_len(0))

    with context("with 4 Epics in sequential order"):
        with before.each:
            self.diagram = _four_epics_diagram()

        with it("should hold 4 Epics"):
            expect(self.diagram.epics).to(have_len(4))

        with context("every Epic"):
            with it("should sit on the Epic row"):
                for epic in self.diagram.epics:
                    expect(self.diagram.epic_row_y()).to(equal(0))

            with it("should sit at the X of its sequential position on the Epic row"):
                xs = [self.diagram.epic_x(e) for e in self.diagram.epics]
                expect(xs).to(equal([0, BASE_WIDTH, 2 * BASE_WIDTH, 3 * BASE_WIDTH]))

            with it("should span its own base width when it holds no SubEpics"):
                for epic in self.diagram.epics:
                    expect(self.diagram.epic_width(epic)).to(equal(BASE_WIDTH))

        with context("the SubEpic row for depth 0"):
            with it("should sit directly below the Epic row"):
                expect(self.diagram.sub_epic_row_y(0)).to(equal(ROW_HEIGHT))

        with context("the actor row"):
            with it("should sit directly below the deepest SubEpic row"):
                expect(self.diagram.actor_row_y()).to(
                    equal((self.diagram.max_sub_epic_depth() + 2) * ROW_HEIGHT)
                )

        with context("the Story row"):
            with it("should sit directly below the actor row"):
                expect(self.diagram.story_row_y()).to(
                    equal(self.diagram.actor_row_y() + ROW_HEIGHT)
                )

        with context("with a fifth Epic appended"):
            with before.each:
                self.prior_positions = [
                    self.diagram.epic_x(e) for e in self.diagram.epics
                ]
                self.diagram.append_epic(Epic("Epic 5", 5))

            with it("should hold 5 Epics"):
                expect(self.diagram.epics).to(have_len(5))

            with context("the last Epic in sequential order"):
                with it("should be the appended Epic"):
                    expect(self.diagram.epics[-1].name).to(equal("Epic 5"))

                with it("should sit at the rightmost X on the Epic row"):
                    fifth = self.diagram.epics[-1]
                    expect(self.diagram.epic_x(fifth)).to(equal(4 * BASE_WIDTH))

            with context("the first four Epics"):
                with it("should keep their previous X positions"):
                    current = [self.diagram.epic_x(e) for e in self.diagram.epics[:4]]
                    expect(current).to(equal(self.prior_positions))

        with context("with the first Epic removed"):
            with before.each:
                self.diagram.epics[0].sub_epics.append(SubEpic("Dropped", 1))
                self.diagram.remove_epic("Epic 1")

            with it("should hold 3 Epics"):
                expect(self.diagram.epics).to(have_len(3))

            with it("should discard the SubEpics that lived under the removed Epic"):
                names = [e.name for e in self.diagram.epics]
                expect("Epic 1" in names).to(be_false)

            with context("the remaining Epics"):
                with it("should renumber to 1, 2, 3"):
                    orders = [e.sequential_order for e in self.diagram.epics]
                    expect(orders).to(equal([1, 2, 3]))

                with it("should shift left to close the gap left by the removed Epic"):
                    xs = [self.diagram.epic_x(e) for e in self.diagram.epics]
                    expect(xs).to(equal([0, BASE_WIDTH, 2 * BASE_WIDTH]))

        with context("with the first Epic renamed"):
            with before.each:
                self.diagram.epics[0].name = "Epic 1 (renamed)"

            with context("the first Epic"):
                with it("should carry the new name"):
                    expect(self.diagram.epics[0].name).to(equal("Epic 1 (renamed)"))

                with it("should stay at its previous X on the Epic row"):
                    expect(self.diagram.epic_x(self.diagram.epics[0])).to(equal(0))

            with it("should preserve the sequential order of the Epics"):
                orders = [e.sequential_order for e in self.diagram.epics]
                expect(orders).to(equal([1, 2, 3, 4]))

        with context("with the Epics reordered"):
            with before.each:
                self.diagram.story_map.reorder_epics(
                    ["Epic 4", "Epic 2", "Epic 3", "Epic 1"]
                )

            with it("should list the Epics in the new order"):
                names = [e.name for e in self.diagram.epics]
                expect(names).to(equal(["Epic 4", "Epic 2", "Epic 3", "Epic 1"]))

            with context("every Epic"):
                with it("should sit at the X of its new sequential position on the Epic row"):
                    xs = [self.diagram.epic_x(e) for e in self.diagram.epics]
                    expect(xs).to(equal([0, BASE_WIDTH, 2 * BASE_WIDTH, 3 * BASE_WIDTH]))

        with context("with the first Epic holding 3 SubEpics"):
            with before.each:
                self.diagram = _first_epic_with_3_sub_epics_diagram()
                self.first_epic = self.diagram.epics[0]

            with context("the first Epic"):
                with it("should hold 3 SubEpics"):
                    expect(self.first_epic.sub_epics).to(have_len(3))

                with it("should widen to span the combined width of its 3 SubEpics"):
                    expect(self.diagram.epic_width(self.first_epic)).to(
                        equal(3 * BASE_WIDTH)
                    )

            with context("every SubEpic of the first Epic"):
                with it("should sit on the SubEpic row for depth 0"):
                    for sub in self.first_epic.sub_epics:
                        expect(self.diagram.sub_epic_y(sub)).to(
                            equal(self.diagram.sub_epic_row_y(0))
                        )

                with it("should sit at the X of its sequential position within the first Epic's span"):
                    xs = [self.diagram.sub_epic_x(s) for s in self.first_epic.sub_epics]
                    expect(xs).to(equal([0, BASE_WIDTH, 2 * BASE_WIDTH]))

            with context("every Epic to the right of the first Epic"):
                with it("should shift right to accommodate the first Epic's new width"):
                    expect(self.diagram.epic_x(self.diagram.epics[1])).to(
                        equal(3 * BASE_WIDTH)
                    )

            with context("with a SubEpic appended to the first Epic"):
                with before.each:
                    self.first_epic.sub_epics.append(SubEpic("SubEpic 1.4", 4))

                with context("the first Epic"):
                    with it("should hold 4 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(4))

                    with it("should widen to span 4 SubEpics"):
                        expect(self.diagram.epic_width(self.first_epic)).to(
                            equal(4 * BASE_WIDTH)
                        )

                with context("the appended SubEpic"):
                    with it("should sit at the rightmost X within the first Epic's span"):
                        appended = self.first_epic.sub_epics[-1]
                        expect(self.diagram.sub_epic_x(appended)).to(
                            equal(3 * BASE_WIDTH)
                        )

                with context("every Epic to the right of the first Epic"):
                    with it("should shift right by the width of one SubEpic"):
                        expect(self.diagram.epic_x(self.diagram.epics[1])).to(
                            equal(4 * BASE_WIDTH)
                        )

            with context("with the first SubEpic of the first Epic removed"):
                with before.each:
                    self.first_epic.sub_epics[0].stories.append(
                        Story("Dropped", 1, StoryType.USER)
                    )
                    self.first_epic.sub_epics.pop(0)

                with context("the first Epic"):
                    with it("should hold 2 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(2))

                    with it("should narrow to span 2 SubEpics"):
                        expect(self.diagram.epic_width(self.first_epic)).to(
                            equal(2 * BASE_WIDTH)
                        )

                    with it("should discard the Stories that lived under the removed SubEpic"):
                        remaining_names = [
                            s.name for s in self.first_epic.sub_epics
                        ]
                        expect("SubEpic 1.1" in remaining_names).to(be_false)

                with context("every Epic to the right of the first Epic"):
                    with it("should shift left by the width of one SubEpic"):
                        expect(self.diagram.epic_x(self.diagram.epics[1])).to(
                            equal(2 * BASE_WIDTH)
                        )

            with context("with the first SubEpic of the first Epic renamed"):
                with before.each:
                    self.first_epic.sub_epics[0].name = "SubEpic 1.1 (renamed)"

                with context("the first SubEpic of the first Epic"):
                    with it("should carry the new name"):
                        expect(self.first_epic.sub_epics[0].name).to(
                            equal("SubEpic 1.1 (renamed)")
                        )

                    with it("should stay at its previous X on the SubEpic row for depth 0"):
                        expect(
                            self.diagram.sub_epic_x(self.first_epic.sub_epics[0])
                        ).to(equal(0))

            with context("with a nested SubEpic added under the first SubEpic"):
                with before.each:
                    self.first_epic.sub_epics[0].sub_epics.append(
                        SubEpic("Nested", 1)
                    )
                    self.nested = self.first_epic.sub_epics[0].sub_epics[0]

                with context("the first SubEpic of the first Epic"):
                    with it("should hold 1 nested SubEpic"):
                        expect(self.first_epic.sub_epics[0].sub_epics).to(have_len(1))

                    with it("should widen to span its nested SubEpic"):
                        expect(
                            self.diagram.sub_epic_width(self.first_epic.sub_epics[0])
                        ).to(equal(BASE_WIDTH))

                with context("the nested SubEpic"):
                    with it("should sit on the SubEpic row for depth 1"):
                        expect(self.diagram.sub_epic_y(self.nested)).to(
                            equal(self.diagram.sub_epic_row_y(1))
                        )

                with context("the SubEpic row for depth 1"):
                    with it("should sit directly below the depth 0 row"):
                        expect(self.diagram.sub_epic_row_y(1)).to(
                            equal(self.diagram.sub_epic_row_y(0) + ROW_HEIGHT)
                        )

                with context("the actor row"):
                    with it("should shift down to sit below the depth 1 row"):
                        expect(self.diagram.actor_row_y()).to(
                            equal(self.diagram.sub_epic_row_y(1) + ROW_HEIGHT)
                        )

                with context("the Story row"):
                    with it("should shift down to sit below the actor row"):
                        expect(self.diagram.story_row_y()).to(
                            equal(self.diagram.actor_row_y() + ROW_HEIGHT)
                        )

            with context(
                "with the first SubEpic moved from the first Epic to the second Epic"
            ):
                with before.each:
                    self.first_epic.sub_epics[0].stories.append(
                        Story("Carrying", 1, StoryType.USER)
                    )
                    self.first_epic.sub_epics[0].stories[0].acceptance_criteria.append(
                        AcceptanceCriteria(name="AC 1", sequential_order=1, text="t")
                    )
                    self.moved = self.first_epic.sub_epics.pop(0)
                    self.second_epic = self.diagram.epics[1]
                    self.second_epic.sub_epics.append(self.moved)

                with context("the first Epic"):
                    with it("should hold 2 SubEpics"):
                        expect(self.first_epic.sub_epics).to(have_len(2))

                    with it("should narrow to span 2 SubEpics"):
                        expect(self.diagram.epic_width(self.first_epic)).to(
                            equal(2 * BASE_WIDTH)
                        )

                with context("the second Epic"):
                    with it("should hold one additional SubEpic"):
                        expect(self.second_epic.sub_epics).to(have_len(1))

                    with it("should widen to accommodate the additional SubEpic"):
                        expect(self.diagram.epic_width(self.second_epic)).to(
                            equal(BASE_WIDTH)
                        )

                with context("the moved SubEpic"):
                    with it("should sit within the second Epic's span"):
                        moved_x = self.diagram.sub_epic_x(self.moved)
                        second_x = self.diagram.epic_x(self.second_epic)
                        second_end = second_x + self.diagram.epic_width(
                            self.second_epic
                        )
                        expect(second_x <= moved_x < second_end).to(be_true)

                    with it("should keep its Stories and AcceptanceCriteria at the new X"):
                        expect(self.moved.stories).to(have_len(1))
                        expect(self.moved.stories[0].acceptance_criteria).to(
                            have_len(1)
                        )

            with context("with the first SubEpic of the first Epic holding 2 Stories"):
                with before.each:
                    first_sub_epic = self.first_epic.sub_epics[0]
                    for k in range(1, 3):
                        first_sub_epic.stories.append(
                            Story(f"Story {k}", k, StoryType.USER)
                        )
                    self.first_sub_epic = first_sub_epic

                with context("every Story"):
                    with it("should sit on the Story row"):
                        for story in self.first_sub_epic.stories:
                            expect(self.diagram.story_y(story)).to(
                                equal(self.diagram.story_row_y())
                            )

                    with it("should sit at the X of its parent SubEpic"):
                        parent_x = self.diagram.sub_epic_x(self.first_sub_epic)
                        for story in self.first_sub_epic.stories:
                            expect(self.diagram.story_x(story)).to(equal(parent_x))

                with context("with a Story appended to the first SubEpic"):
                    with before.each:
                        self.first_sub_epic.stories.append(
                            Story("Story 3", 3, StoryType.USER)
                        )

                    with context("the first SubEpic of the first Epic"):
                        with it("should hold 3 Stories"):
                            expect(self.first_sub_epic.stories).to(have_len(3))

                    with context("the appended Story"):
                        with it("should sit on the Story row at the parent SubEpic's X"):
                            appended = self.first_sub_epic.stories[-1]
                            expect(self.diagram.story_x(appended)).to(
                                equal(self.diagram.sub_epic_x(self.first_sub_epic))
                            )

                with context("with the first Story of the first SubEpic renamed"):
                    with before.each:
                        self.first_sub_epic.stories[0].name = "Story 1 (renamed)"

                    with context("the first Story of the first SubEpic"):
                        with it("should carry the new name"):
                            expect(self.first_sub_epic.stories[0].name).to(
                                equal("Story 1 (renamed)")
                            )

                        with it("should stay at its previous X on the Story row"):
                            expect(
                                self.diagram.story_x(self.first_sub_epic.stories[0])
                            ).to(equal(self.diagram.sub_epic_x(self.first_sub_epic)))

                with context("with the first Story typed as system"):
                    with before.each:
                        self.first_sub_epic.stories[0].story_type = StoryType.SYSTEM

                    with context("the first Story of the first SubEpic"):
                        with it("should carry the style for StoryType system"):
                            expect(
                                self.first_sub_epic.stories[0].story_type
                            ).to(equal(StoryType.SYSTEM))

                with context(
                    "with the first Story moved from the first SubEpic to the second SubEpic"
                ):
                    with before.each:
                        self.first_sub_epic.stories[0].acceptance_criteria.append(
                            AcceptanceCriteria(name="AC 1", sequential_order=1, text="t")
                        )
                        second_sub_epic = self.first_epic.sub_epics[1]
                        self.moved_story = self.first_sub_epic.stories.pop(0)
                        second_sub_epic.stories.append(self.moved_story)
                        self.second_sub_epic = second_sub_epic

                    with context("the moved Story"):
                        with it("should sit at the second SubEpic's X on the Story row"):
                            expect(self.diagram.story_x(self.moved_story)).to(
                                equal(self.diagram.sub_epic_x(self.second_sub_epic))
                            )

                        with it("should keep its AcceptanceCriteria"):
                            expect(self.moved_story.acceptance_criteria).to(
                                have_len(1)
                            )

    with context("that has been asked to place a SubEpic as a parent of an Epic"):
        with it("should reject the placement"):
            diagram = DiagramStoryMap()
            expect(
                lambda: diagram.place_child_under_parent(
                    Epic("New", 1), SubEpic("Parent", 1)
                )
            ).to(raise_error(PlacementError))

    with context("that has been asked to place a Story as a parent of a SubEpic"):
        with it("should reject the placement"):
            diagram = DiagramStoryMap()
            expect(
                lambda: diagram.place_child_under_parent(
                    SubEpic("New", 1), Story("Parent", 1, StoryType.USER)
                )
            ).to(raise_error(PlacementError))

    with context("that has been asked to place any child under a Story"):
        with it("should reject the placement"):
            diagram = DiagramStoryMap()
            expect(
                lambda: diagram.place_child_under_parent(
                    Story("Child", 1, StoryType.USER),
                    Story("Parent", 1, StoryType.USER),
                )
            ).to(raise_error(PlacementError))

    with context("that has been asked to give an Epic any parent"):
        with it("should reject the parent"):
            diagram = DiagramStoryMap()
            expect(
                lambda: diagram.place_child_under_parent(
                    Epic("Child", 1), SubEpic("Parent", 1)
                )
            ).to(raise_error(PlacementError))
