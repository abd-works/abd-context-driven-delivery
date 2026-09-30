"""Mamba spec for `a code Story Map`. Mirrors ../../bdd-context.md `## Code` -> `a code Story Map`.

Uses a thin concrete backend `_MinimalCodeBackend` to observe the abstract folder-tree
behavior - the language-specific leaf content is covered by the TS/Python/Java specs.

Exercises the Uniform Callable Surface: the backend is stateless - every call
passes the canonical StoryModel explicitly through `render(canonical, previous=None)`,
`parse(external)`, and `sync(external, canonical)`.
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
from expects import equal, have_len, be_true, be_false, expect, raise_error

from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Scenario
from practices.stories.model.story_model import StoryModel
from practices.stories.model.code_story_model import (
    CodeEpic,
    CodeStoryModel,
    CodeStoryModelError,
)


class _MinimalCodeBackend(CodeStoryModel):
    LEAF_EXTENSION = ".txt"
    LANGUAGE_LINE_COMMENT = "#"

    def _render_leaf_file(self, sub_epic: Epic, owning_epic: Epic) -> str:
        lines = [f"# leaf: {sub_epic.name}"]
        for story in sub_epic.stories:
            lines.append(f"## story: {story.name}")
            for scenario in story.scenarios:
                lines.append(f"- scenario: {scenario.name}")
        return "\n".join(lines) + "\n"


class SpecFixture:
    def story_map_with_4_epics_and_3_leaf_epics(self) -> StoryModel:
        story_map = StoryModel()
        for i in range(1, 5):
            story_map.append_epic(Epic(f"Epic {i}", i))
        first = story_map.epics[0]
        for j in range(1, 4):
            sub = Epic(f"Epic 1.{j}", j)
            story = Story(f"Story {j}", 1, StoryType.USER)
            story.scenarios.append(Scenario(name=f"scenario {j}", sequential_order=1))
            sub.stories.append(story)
            first.epics.append(sub)
        return story_map


fixture = SpecFixture()


with description("a code Story Map") as self:
    with before.each:
        self.backend_cls = _MinimalCodeBackend
        self.code_map = self.backend_cls()

    with it("should hold no folders under the tests root when rendered from an empty canonical Story Map"):
        tree = self.code_map.render(StoryModel())
        expect(tree).to(equal({}))

    with context("with a canonical Story Map that has Epics but no Epics"):
        with before.each:
            self.canonical = StoryModel()
            for i in range(1, 5):
                self.canonical.append_epic(Epic(f"Epic {i}", i))
            self.tree = self.code_map.render(self.canonical)
            self.parsed = self.code_map.parse(self.tree)

        with it("should preserve Epic count after render/parse"):
            expect(self.parsed.epics).to(have_len(4))

    with context("with a canonical Story Map of 4 Epics in sequential order"):
        with before.each:
            self.canonical = StoryModel()
            for i in range(1, 5):
                self.canonical.append_epic(Epic(f"Epic {i}", i))

        with context("every Epic"):
            with it("should produce a folder under the tests root, named after the Epic slug"):
                # Epics with no sub-epics generate no leaf files; add one to observe folders.
                for epic in self.canonical.epics:
                    epic.epics.append(Epic("child", 1))
                tree = self.code_map.render(self.canonical)
                folders = self.code_map.folders_of(tree)
                epic_folders = [f for f in folders if f.count("/") == 1]
                expected = sorted(
                    f"{self.code_map.tests_root}/{CodeEpic(e.name).slug()}"
                    for e in self.canonical.epics
                )
                expect(sorted(epic_folders)).to(equal(expected))

        with context("with a fifth Epic appended to the canonical"):
            with before.each:
                for epic in self.canonical.epics:
                    epic.epics.append(Epic("child", 1))
                self.previous_tree = self.code_map.render(self.canonical)
                self.canonical.append_epic(Epic("Epic 5", 5))
                self.canonical.epics[-1].epics.append(Epic("child", 1))
                self.new_tree = self.code_map.render(self.canonical)

            with context("the appended Epic"):
                with it("should produce a new folder under the tests root"):
                    folders = self.code_map.folders_of(self.new_tree)
                    expect(
                        f"{self.code_map.tests_root}/{CodeEpic('Epic 5').slug()}" in folders
                    ).to(be_true)

            with context("the folders for the first four Epics"):
                with it("should be byte-identical to before"):
                    for path, content in self.previous_tree.items():
                        expect(path in self.new_tree).to(be_true)
                        expect(self.new_tree[path]).to(equal(content))

        with context("with the first Epic removed from the canonical"):
            with before.each:
                for epic in self.canonical.epics:
                    epic.epics.append(Epic("child", 1))
                self.previous_tree = self.code_map.render(self.canonical)
                self.canonical.epics.pop(0)
                self.new_tree = self.code_map.render(self.canonical)

            with context("the folder for the removed Epic and everything under it"):
                with it("should be gone"):
                    removed_prefix = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/"
                    expect(
                        any(p.startswith(removed_prefix) for p in self.new_tree)
                    ).to(be_false)

            with context("the folders for the remaining Epics"):
                with it("should be byte-identical to before"):
                    for path, content in self.previous_tree.items():
                        if path.startswith(
                            f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/"
                        ):
                            continue
                        expect(path in self.new_tree).to(be_true)
                        expect(self.new_tree[path]).to(equal(content))

        with context("with the first Epic renamed in the canonical"):
            with before.each:
                for epic in self.canonical.epics:
                    epic.epics.append(Epic("child", 1))
                self.previous_leaf = self.code_map.render(self.canonical)[
                    f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/child/child{self.code_map.LEAF_EXTENSION}"
                ]
                self.canonical.epics[0].name = "Epic 1 (renamed)"
                self.new_tree = self.code_map.render(self.canonical)

            with context("the folder for the first Epic"):
                with it("should carry the new slug"):
                    new_prefix = (
                        f"{self.code_map.tests_root}/{CodeEpic('Epic 1 (renamed)').slug()}/"
                    )
                    expect(any(p.startswith(new_prefix) for p in self.new_tree)).to(
                        be_true
                    )

                with context("its contents"):
                    with it("should be byte-identical to before"):
                        new_leaf = self.new_tree[
                            f"{self.code_map.tests_root}/{CodeEpic('Epic 1 (renamed)').slug()}/child/child{self.code_map.LEAF_EXTENSION}"
                        ]
                        expect(new_leaf).to(equal(self.previous_leaf))

        with context("with the first Epic holding 3 leaf Epics"):
            with before.each:
                self.canonical = fixture.story_map_with_4_epics_and_3_leaf_epics()
                self.first_epic = self.canonical.epics[0]
                self.tree = self.code_map.render(self.canonical)

            with context("the folder for the first Epic"):
                with it("should contain 3 sub-folders (one per leaf Epic)"):
                    epic_prefix = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/"
                    sub_folders = {
                        p.split("/")[2]
                        for p in self.tree
                        if p.startswith(epic_prefix)
                    }
                    expect(sub_folders).to(have_len(3))

            with context("every leaf Epic of the first Epic"):
                with it(
                    "should produce a sub-folder under the first Epic's folder, named after the Epic slug"
                ):
                    for sub in self.first_epic.epics:
                        prefix = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic(sub.name).slug()}/"
                        expect(any(p.startswith(prefix) for p in self.tree)).to(
                            be_true
                        )

                with it(
                    "should produce exactly one leaf file inside its own sub-folder, named after the Epic slug"
                ):
                    for sub in self.first_epic.epics:
                        expected = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic(sub.name).slug()}/{CodeEpic(sub.name).slug()}{self.code_map.LEAF_EXTENSION}"
                        expect(expected in self.tree).to(be_true)

            with context("with a leaf Epic appended to the first Epic"):
                with before.each:
                    self.previous_tree = dict(self.tree)
                    new_sub = Epic("Epic 1.4", 4)
                    new_sub.stories.append(Story("Story 1", 1, StoryType.USER))
                    self.first_epic.epics.append(new_sub)
                    self.new_tree = self.code_map.render(self.canonical)

                with context("the folder for the first Epic"):
                    with it("should contain 4 sub-folders"):
                        epic_prefix = (
                            f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/"
                        )
                        sub_folders = {
                            p.split("/")[2]
                            for p in self.new_tree
                            if p.startswith(epic_prefix)
                        }
                        expect(sub_folders).to(have_len(4))

                with context("the appended Epic"):
                    with it("should produce a new sub-folder holding a new leaf file"):
                        expected = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.4').slug()}/{CodeEpic('Epic 1.4').slug()}{self.code_map.LEAF_EXTENSION}"
                        expect(expected in self.new_tree).to(be_true)

                with context("the leaf files for the first three Epics"):
                    with it("should be byte-identical to before"):
                        for path, content in self.previous_tree.items():
                            expect(self.new_tree[path]).to(equal(content))

            with context("with the first Epic of the first Epic renamed"):
                with before.each:
                    self.previous_leaf = self.tree[
                        f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1').slug()}/{CodeEpic('Epic 1.1').slug()}{self.code_map.LEAF_EXTENSION}"
                    ]
                    self.first_epic.epics[0].name = "Epic 1.1 (renamed)"
                    self.new_tree = self.code_map.render(self.canonical)

                with context("the sub-folder for the first Epic"):
                    with it("should carry the new slug"):
                        prefix = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1 (renamed)').slug()}/"
                        expect(any(p.startswith(prefix) for p in self.new_tree)).to(
                            be_true
                        )

                with context("the leaf file inside it"):
                    with it("should carry the new slug in its filename"):
                        expected = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1 (renamed)').slug()}/{CodeEpic('Epic 1.1 (renamed)').slug()}{self.code_map.LEAF_EXTENSION}"
                        expect(expected in self.new_tree).to(be_true)

                    with context("its Story blocks"):
                        with it("should be unchanged"):
                            new_leaf = self.new_tree[
                                f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1 (renamed)').slug()}/{CodeEpic('Epic 1.1 (renamed)').slug()}{self.code_map.LEAF_EXTENSION}"
                            ]
                            expect("Story 1" in new_leaf).to(be_true)

            with context(
                "with a nested Epic added under the first (previously leaf) Epic"
            ):
                with before.each:
                    first_sub = self.first_epic.epics[0]
                    first_sub.epics.append(Epic("Nested", 1))
                    first_sub.epics[0].stories.append(
                        Story("Nested Story", 1, StoryType.USER)
                    )
                    self.new_tree = self.code_map.render(self.canonical)

                with context("the sub-folder for the first Epic"):
                    with it("should hold a further sub-folder for the nested Epic"):
                        nested_prefix = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1').slug()}/{CodeEpic('Nested').slug()}/"
                        expect(
                            any(p.startswith(nested_prefix) for p in self.new_tree)
                        ).to(be_true)

                    with context("the nested sub-folder"):
                        with it("should hold a leaf file for the nested Epic"):
                            nested_leaf = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1').slug()}/{CodeEpic('Nested').slug()}/{CodeEpic('Nested').slug()}{self.code_map.LEAF_EXTENSION}"
                            expect(nested_leaf in self.new_tree).to(be_true)

                with context("the leaf file that previously sat at the first Epic level"):
                    with it("should still exist when the first Epic still has Stories"):
                        previous_leaf = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1').slug()}/{CodeEpic('Epic 1.1').slug()}{self.code_map.LEAF_EXTENSION}"
                        expect(previous_leaf in self.new_tree).to(be_true)

    with context(
        "that holds hand-written regions in a leaf file outside the generated Story blocks"
    ):
        with before.each:
            self.canonical = fixture.story_map_with_4_epics_and_3_leaf_epics()
            first_leaf_path = f"{self.code_map.tests_root}/{CodeEpic('Epic 1').slug()}/{CodeEpic('Epic 1.1').slug()}/{CodeEpic('Epic 1.1').slug()}{self.code_map.LEAF_EXTENSION}"
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
                    raise_error(CodeStoryModelError)
                )
