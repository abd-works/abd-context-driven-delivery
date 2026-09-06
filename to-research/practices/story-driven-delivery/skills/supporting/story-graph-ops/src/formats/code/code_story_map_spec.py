"""Mamba spec for `a code Story Map`. Mirrors bdd-context.md `## Code` -> `a code Story Map`.

Uses a thin concrete backend `_MinimalCodeBackend` to observe the abstract folder-tree
behavior — the language-specific leaf content is covered by the TS/Python/Java specs.

Exercises the Uniform Callable Surface: the backend is stateless — every call
passes the canonical StoryMap explicitly through `render(canonical, previous=None)`,
`parse(external)`, and `sync(external, canonical)`.
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
from expects import equal, have_len, be_true, be_false, expect, raise_error

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.formats.code.code_story_map import CodeStoryMap, CodeStoryMapError, to_kebab


class _MinimalCodeBackend(CodeStoryMap):
    LEAF_EXTENSION = ".txt"
    LANGUAGE_LINE_COMMENT = "#"

    def _render_leaf_file(self, sub_epic: SubEpic, owning_epic: Epic) -> str:
        lines = [f"# leaf: {sub_epic.name}"]
        for story in sub_epic.stories:
            lines.append(f"## story: {story.name}")
            for ac in story.acceptance_criteria:
                lines.append(f"- scenario: {ac.text or ac.name}")
        return "\n".join(lines) + "\n"


def _story_map_with_4_epics_and_3_leaf_sub_epics() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story(f"Story {j}", 1, StoryType.USER)
        story.acceptance_criteria.append(
            AcceptanceCriteria(name="AC 1", sequential_order=1, text=f"scenario {j}")
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a code Story Map") as self:
    with before.each:
        self.backend_cls = _MinimalCodeBackend
        self.code_map = self.backend_cls()

    with it("should hold no folders under the tests root when rendered from an empty canonical Story Map"):
        tree = self.code_map.render(StoryMap())
        expect(tree).to(equal({}))

    with context("with a canonical Story Map that has Epics but no SubEpics"):
        with before.each:
            self.canonical = StoryMap()
            for i in range(1, 5):
                self.canonical.append_epic(Epic(f"Epic {i}", i))
            self.tree = self.code_map.render(self.canonical)
            self.parsed = self.code_map.parse(self.tree)

        with it("should preserve Epic count after render/parse"):
            expect(self.parsed.epics).to(have_len(4))

    with context("with a canonical Story Map of 4 Epics in sequential order"):
        with before.each:
            self.canonical = StoryMap()
            for i in range(1, 5):
                self.canonical.append_epic(Epic(f"Epic {i}", i))

        with context("every Epic"):
            with it("should produce a folder under the tests root, named after the Epic slug"):
                # Epics with no sub-epics generate no leaf files, so the tree is
                # empty — we synthesise the empty case by adding a sub-epic here.
                for epic in self.canonical.epics:
                    epic.sub_epics.append(SubEpic("child", 1))
                tree = self.code_map.render(self.canonical)
                folders = self.code_map.folders_of(tree)
                epic_folders = [f for f in folders if f.count("/") == 1]
                expected = sorted(
                    f"{self.code_map.tests_root}/{to_kebab(e.name)}"
                    for e in self.canonical.epics
                )
                expect(sorted(epic_folders)).to(equal(expected))

        with context("with a fifth Epic appended to the canonical"):
            with before.each:
                for epic in self.canonical.epics:
                    epic.sub_epics.append(SubEpic("child", 1))
                self.previous_tree = self.code_map.render(self.canonical)
                self.canonical.append_epic(Epic("Epic 5", 5))
                self.canonical.epics[-1].sub_epics.append(SubEpic("child", 1))
                self.new_tree = self.code_map.render(self.canonical)

            with context("the appended Epic"):
                with it("should produce a new folder under the tests root"):
                    folders = self.code_map.folders_of(self.new_tree)
                    expect(
                        f"{self.code_map.tests_root}/{to_kebab('Epic 5')}" in folders
                    ).to(be_true)

            with context("the folders for the first four Epics"):
                with it("should be byte-identical to before"):
                    for path, content in self.previous_tree.items():
                        expect(path in self.new_tree).to(be_true)
                        expect(self.new_tree[path]).to(equal(content))

        with context("with the first Epic removed from the canonical"):
            with before.each:
                for epic in self.canonical.epics:
                    epic.sub_epics.append(SubEpic("child", 1))
                self.previous_tree = self.code_map.render(self.canonical)
                self.canonical.remove_epic("Epic 1")
                self.new_tree = self.code_map.render(self.canonical)

            with context("the folder for the removed Epic and everything under it"):
                with it("should be gone"):
                    removed_prefix = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/"
                    expect(
                        any(p.startswith(removed_prefix) for p in self.new_tree)
                    ).to(be_false)

            with context("the folders for the remaining Epics"):
                with it("should be byte-identical to before"):
                    for path, content in self.previous_tree.items():
                        if path.startswith(
                            f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/"
                        ):
                            continue
                        expect(path in self.new_tree).to(be_true)
                        expect(self.new_tree[path]).to(equal(content))

        with context("with the first Epic renamed in the canonical"):
            with before.each:
                for epic in self.canonical.epics:
                    epic.sub_epics.append(SubEpic("child", 1))
                self.previous_leaf = self.code_map.render(self.canonical)[
                    f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/child/child{self.code_map.LEAF_EXTENSION}"
                ]
                self.canonical.epics[0].name = "Epic 1 (renamed)"
                self.new_tree = self.code_map.render(self.canonical)

            with context("the folder for the first Epic"):
                with it("should carry the new slug"):
                    new_prefix = (
                        f"{self.code_map.tests_root}/{to_kebab('Epic 1 (renamed)')}/"
                    )
                    expect(any(p.startswith(new_prefix) for p in self.new_tree)).to(
                        be_true
                    )

                with context("its contents"):
                    with it("should be byte-identical to before"):
                        new_leaf = self.new_tree[
                            f"{self.code_map.tests_root}/{to_kebab('Epic 1 (renamed)')}/child/child{self.code_map.LEAF_EXTENSION}"
                        ]
                        expect(new_leaf).to(equal(self.previous_leaf))

        with context("with the first Epic holding 3 leaf SubEpics"):
            with before.each:
                self.canonical = _story_map_with_4_epics_and_3_leaf_sub_epics()
                self.first_epic = self.canonical.epics[0]
                self.tree = self.code_map.render(self.canonical)

            with context("the folder for the first Epic"):
                with it("should contain 3 sub-folders (one per leaf SubEpic)"):
                    epic_prefix = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/"
                    sub_folders = {
                        p.split("/")[2]
                        for p in self.tree
                        if p.startswith(epic_prefix)
                    }
                    expect(sub_folders).to(have_len(3))

            with context("every leaf SubEpic of the first Epic"):
                with it(
                    "should produce a sub-folder under the first Epic's folder, named after the SubEpic slug"
                ):
                    for sub in self.first_epic.sub_epics:
                        prefix = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab(sub.name)}/"
                        expect(any(p.startswith(prefix) for p in self.tree)).to(
                            be_true
                        )

                with it(
                    "should produce exactly one leaf file inside its own sub-folder, named after the SubEpic slug"
                ):
                    for sub in self.first_epic.sub_epics:
                        expected = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab(sub.name)}/{to_kebab(sub.name)}{self.code_map.LEAF_EXTENSION}"
                        expect(expected in self.tree).to(be_true)

            with context("with a leaf SubEpic appended to the first Epic"):
                with before.each:
                    self.previous_tree = dict(self.tree)
                    new_sub = SubEpic("SubEpic 1.4", 4)
                    new_sub.stories.append(Story("Story 1", 1, StoryType.USER))
                    self.first_epic.sub_epics.append(new_sub)
                    self.new_tree = self.code_map.render(self.canonical)

                with context("the folder for the first Epic"):
                    with it("should contain 4 sub-folders"):
                        epic_prefix = (
                            f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/"
                        )
                        sub_folders = {
                            p.split("/")[2]
                            for p in self.new_tree
                            if p.startswith(epic_prefix)
                        }
                        expect(sub_folders).to(have_len(4))

                with context("the appended SubEpic"):
                    with it("should produce a new sub-folder holding a new leaf file"):
                        expected = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.4')}/{to_kebab('SubEpic 1.4')}{self.code_map.LEAF_EXTENSION}"
                        expect(expected in self.new_tree).to(be_true)

                with context("the leaf files for the first three SubEpics"):
                    with it("should be byte-identical to before"):
                        for path, content in self.previous_tree.items():
                            expect(self.new_tree[path]).to(equal(content))

            with context("with the first SubEpic of the first Epic renamed"):
                with before.each:
                    self.previous_leaf = self.tree[
                        f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1')}/{to_kebab('SubEpic 1.1')}{self.code_map.LEAF_EXTENSION}"
                    ]
                    self.first_epic.sub_epics[0].name = "SubEpic 1.1 (renamed)"
                    self.new_tree = self.code_map.render(self.canonical)

                with context("the sub-folder for the first SubEpic"):
                    with it("should carry the new slug"):
                        prefix = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1 (renamed)')}/"
                        expect(any(p.startswith(prefix) for p in self.new_tree)).to(
                            be_true
                        )

                with context("the leaf file inside it"):
                    with it("should carry the new slug in its filename"):
                        expected = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1 (renamed)')}/{to_kebab('SubEpic 1.1 (renamed)')}{self.code_map.LEAF_EXTENSION}"
                        expect(expected in self.new_tree).to(be_true)

                    with context("its Story blocks"):
                        with it("should be unchanged"):
                            new_leaf = self.new_tree[
                                f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1 (renamed)')}/{to_kebab('SubEpic 1.1 (renamed)')}{self.code_map.LEAF_EXTENSION}"
                            ]
                            expect("Story 1" in new_leaf).to(be_true)

            with context(
                "with a nested SubEpic added under the first (previously leaf) SubEpic"
            ):
                with before.each:
                    first_sub = self.first_epic.sub_epics[0]
                    first_sub.sub_epics.append(SubEpic("Nested", 1))
                    first_sub.sub_epics[0].stories.append(
                        Story("Nested Story", 1, StoryType.USER)
                    )
                    self.new_tree = self.code_map.render(self.canonical)

                with context("the sub-folder for the first SubEpic"):
                    with it("should hold a further sub-folder for the nested SubEpic"):
                        nested_prefix = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1')}/{to_kebab('Nested')}/"
                        expect(
                            any(p.startswith(nested_prefix) for p in self.new_tree)
                        ).to(be_true)

                    with context("the nested sub-folder"):
                        with it("should hold a leaf file for the nested SubEpic"):
                            nested_leaf = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1')}/{to_kebab('Nested')}/{to_kebab('Nested')}{self.code_map.LEAF_EXTENSION}"
                            expect(nested_leaf in self.new_tree).to(be_true)

                with context("the leaf file that previously sat at the first SubEpic level"):
                    with it("should still exist when the first SubEpic still has Stories"):
                        previous_leaf = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1')}/{to_kebab('SubEpic 1.1')}{self.code_map.LEAF_EXTENSION}"
                        expect(previous_leaf in self.new_tree).to(be_true)

    with context(
        "that holds hand-written regions in a leaf file outside the generated Story blocks"
    ):
        with before.each:
            self.canonical = _story_map_with_4_epics_and_3_leaf_sub_epics()
            first_leaf_path = f"{self.code_map.tests_root}/{to_kebab('Epic 1')}/{to_kebab('SubEpic 1.1')}/{to_kebab('SubEpic 1.1')}{self.code_map.LEAF_EXTENSION}"
            initial_tree = self.code_map.render(self.canonical)
            hand_written = (
                initial_tree[first_leaf_path]
                + "\n# HAND-WRITTEN START custom-block\nmy_setup_variable = 42\n# HAND-WRITTEN END\n"
            )
            self.first_leaf_path = first_leaf_path
            self.previous_tree = dict(initial_tree)
            self.previous_tree[first_leaf_path] = hand_written

        with context("with the leaf file regenerated"):
            with before.each:
                self.new_tree = self.code_map.render(
                    self.canonical, previous=self.previous_tree
                )

            with context("the leaf file"):
                with it("should preserve every hand-written region byte-for-byte"):
                    expect("my_setup_variable = 42" in self.new_tree[self.first_leaf_path]).to(be_true)

            with context("the generated Story blocks"):
                with it("should be the only regions rewritten"):
                    generated_leaf = self.new_tree[self.first_leaf_path]
                    expect("## story: Story 1" in generated_leaf).to(be_true)

    with context(
        "that has been asked to parse a value that is not a valid code Story Map tree"
    ):
        with context("the parse"):
            with it("should be rejected"):
                expect(lambda: self.code_map.parse("not a mapping")).to(
                    raise_error(CodeStoryMapError)
                )
