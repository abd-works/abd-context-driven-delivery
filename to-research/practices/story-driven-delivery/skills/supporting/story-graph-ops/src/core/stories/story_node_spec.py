"""Mamba spec for `a StoryNode`.

Uses Epic as the concrete representative of the abstract StoryNode contract.
Mirrors the `## Story Model` -> `a StoryNode` block of tests/bdd-context.md 1:1.
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
from expects import equal, have_len, be_true, be_false, expect, raise_error

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.update_report import ChangeKind, TranslationError


def _epic_with_children(name: str, order: int, sub_epic_names: list) -> Epic:
    epic = Epic(name, order)
    for i, sub_name in enumerate(sub_epic_names, start=1):
        epic.sub_epics.append(SubEpic(sub_name, i))
    return epic


with description("a StoryNode") as self:
    with context(
        "that has been translated from a source of the same semantic type with no differences"
    ):
        with before.each:
            self.target = _epic_with_children("Epic 1", 1, ["SubEpic 1", "SubEpic 2"])
            self.source = _epic_with_children("Epic 1", 1, ["SubEpic 1", "SubEpic 2"])
            self.report = self.target.translate_from(self.source)

        with context("the UpdateReport"):
            with it("should record no adds, removes, renames, or reorders"):
                significant = [
                    c for c in self.report.changes if c.kind != ChangeKind.EXACT_MATCH
                ]
                expect(significant).to(have_len(0))

            with it("should hold a NodeSnapshot of the target captured before translation"):
                expect(self.report.snapshot is not None).to(be_true)
                expect(self.report.snapshot.name).to(equal("Epic 1"))

        with context("the target"):
            with it("should be unchanged in every field"):
                expect(self.target.name).to(equal("Epic 1"))
                expect(self.target.sequential_order).to(equal(1))
                expect([s.name for s in self.target.sub_epics]).to(
                    equal(["SubEpic 1", "SubEpic 2"])
                )

    with context(
        "that has been asked to translate from a source of a different semantic type"
    ):
        with it("should reject the translation"):
            target = Epic("Epic 1", 1)
            wrong_source = SubEpic("SubEpic 1", 1)
            expect(lambda: target.translate_from(wrong_source)).to(
                raise_error(TranslationError)
            )

    with context("that has been translated from a source with an added child"):
        with before.each:
            self.target = _epic_with_children("Epic 1", 1, ["SubEpic 1"])
            self.source = _epic_with_children(
                "Epic 1", 1, ["SubEpic 1", "SubEpic 2"]
            )
            self.report = self.target.translate_from(self.source)

        with context("the target"):
            with it("should hold the new child"):
                names = [s.name for s in self.target.sub_epics]
                expect("SubEpic 2" in names).to(be_true)

            with context("the new child on the target"):
                with it("should be of the correct semantic type for its position"):
                    new_child = self.target.sub_epics[-1]
                    expect(new_child.semantic_type()).to(equal("SubEpic"))

                with it("should carry every field from the source child"):
                    new_child = self.target.sub_epics[-1]
                    expect(new_child.name).to(equal("SubEpic 2"))
                    expect(new_child.sequential_order).to(equal(2))

        with context("the UpdateReport"):
            with it("should record the new child"):
                adds = self.report.adds()
                expect(adds).to(have_len(1))
                expect(adds[0].node_name).to(equal("SubEpic 2"))

    with context("that has been translated from a source with a removed child"):
        with before.each:
            self.target = _epic_with_children(
                "Epic 1", 1, ["SubEpic 1", "SubEpic 2"]
            )
            self.source = _epic_with_children("Epic 1", 1, ["SubEpic 1"])
            self.report = self.target.translate_from(self.source)

        with context("the target"):
            with it("should no longer hold the removed child"):
                names = [s.name for s in self.target.sub_epics]
                expect("SubEpic 2" in names).to(be_false)

        with context("the UpdateReport"):
            with it("should record the removed child"):
                removes = self.report.removes()
                expect(removes).to(have_len(1))
                expect(removes[0].node_name).to(equal("SubEpic 2"))

    with context("that has been translated from a source with a renamed child"):
        with before.each:
            self.target = _epic_with_children("Epic 1", 1, ["SubEpic 1"])
            self.source = _epic_with_children("Epic 1", 1, ["SubEpic 1 (renamed)"])
            self.report = self.target.translate_from(self.source)

        with context("the target child"):
            with it("should carry the new name"):
                expect(self.target.sub_epics[0].name).to(equal("SubEpic 1 (renamed)"))

        with context("the UpdateReport"):
            with it("should record the rename with a confidence score"):
                renames = self.report.renames()
                expect(renames).to(have_len(1))
                expect(renames[0].confidence is not None).to(be_true)

    with context("that has been translated from a source with reordered children"):
        with before.each:
            self.target = _epic_with_children(
                "Epic 1", 1, ["SubEpic 1", "SubEpic 2", "SubEpic 3"]
            )
            source = Epic("Epic 1", 1)
            source.sub_epics = [
                SubEpic("SubEpic 3", 1),
                SubEpic("SubEpic 1", 2),
                SubEpic("SubEpic 2", 3),
            ]
            self.report = self.target.translate_from(source)

        with context("the target"):
            with it("should list the children in the source's order"):
                names = [s.name for s in self.target.sub_epics]
                expect(names).to(equal(["SubEpic 3", "SubEpic 1", "SubEpic 2"]))

        with context("the UpdateReport"):
            with it("should record the reorder"):
                reorders = self.report.reorders()
                expect(len(reorders) >= 1).to(be_true)

    with context(
        "that has been translated from a source with a child moved to a different parent"
    ):
        with before.each:
            # WHY: model move as two independent parent reconciliations — old parent
            # sees a removal, new parent sees an addition. The BDD leaf verifies both.
            self.old_parent = _epic_with_children("Epic 1", 1, ["SubEpic 1"])
            self.new_parent = Epic("Epic 2", 2)
            old_source = Epic("Epic 1", 1)  # source: SubEpic 1 has moved away
            new_source = Epic("Epic 2", 2)
            new_source.sub_epics.append(SubEpic("SubEpic 1", 1))
            self.old_report = self.old_parent.translate_from(old_source)
            self.new_report = self.new_parent.translate_from(new_source)

        with context("the old parent on the target"):
            with it("should no longer hold the child"):
                expect(self.old_parent.sub_epics).to(have_len(0))

        with context("the new parent on the target"):
            with it("should hold the child"):
                names = [s.name for s in self.new_parent.sub_epics]
                expect("SubEpic 1" in names).to(be_true)

        with context("the UpdateReport"):
            with it(
                "should record one removed child under the old parent and one added child under the new parent"
            ):
                expect(self.old_report.removes()).to(have_len(1))
                expect(self.new_report.adds()).to(have_len(1))

    with context(
        "that has been translated from a source whose children include a mix of matches, renames, and additions"
    ):
        with before.each:
            self.target = _epic_with_children(
                "Epic 1", 1, ["SubEpic Alpha", "SubEpic Bravo"]
            )
            self.target_children_before = list(self.target.sub_epics)
            source = Epic("Epic 1", 1)
            source.sub_epics = [
                SubEpic("SubEpic Alpha", 1),  # exact match
                SubEpic("SubEpic Bravo (renamed)", 2),  # rename by position
                SubEpic("SubEpic Charlie", 3),  # addition
            ]
            self.report = self.target.translate_from(source)

        with context("the target children matched to a source child by name and sequential order"):
            with it("should keep its identity through reconciliation"):
                # WHY: Alpha was matched by name; it must be the same object instance.
                alpha = self.target.sub_epics[0]
                expect(alpha is self.target_children_before[0]).to(be_true)

            with it("should carry every field from the matched source child"):
                alpha = self.target.sub_epics[0]
                expect(alpha.name).to(equal("SubEpic Alpha"))
                expect(alpha.sequential_order).to(equal(1))

        with context("the target children that correspond to unmatched source children"):
            with it(
                "should appear as fresh instances of the correct semantic type for their position"
            ):
                charlie = self.target.sub_epics[-1]
                expect(charlie.name).to(equal("SubEpic Charlie"))
                expect(charlie.semantic_type()).to(equal("SubEpic"))

        with context("every child collection on the target"):
            with it("should be fully reconciled against the corresponding source collection"):
                names = [s.name for s in self.target.sub_epics]
                expect(names).to(
                    equal(
                        [
                            "SubEpic Alpha",
                            "SubEpic Bravo (renamed)",
                            "SubEpic Charlie",
                        ]
                    )
                )

    with context("that has been reversed against the UpdateReport it produced"):
        with before.each:
            self.target = _epic_with_children(
                "Epic 1", 1, ["SubEpic 1", "SubEpic 2"]
            )
            source = _epic_with_children(
                "Epic 1 (renamed)", 1, ["SubEpic 1 (renamed)", "SubEpic 2"]
            )
            self.report = self.target.translate_from(source)
            self.target.reverse(self.report)

        with it(
            "should be restored to the name and sequential order captured in the NodeSnapshot"
        ):
            expect(self.target.name).to(equal("Epic 1"))
            expect(self.target.sequential_order).to(equal(1))

        with context("every descendant"):
            with it("should be restored to its captured state by position"):
                expect(self.target.sub_epics[0].name).to(equal("SubEpic 1"))

    with context(
        "that has been asked to reverse against a report produced by a different node"
    ):
        with it("should reject the reverse"):
            producer = _epic_with_children("Epic 1", 1, ["SubEpic 1"])
            source = _epic_with_children("Epic 1", 1, ["SubEpic 1", "SubEpic 2"])
            report = producer.translate_from(source)

            foreign = Epic("Epic 2", 2)
            expect(lambda: foreign.reverse(report)).to(raise_error(TranslationError))
