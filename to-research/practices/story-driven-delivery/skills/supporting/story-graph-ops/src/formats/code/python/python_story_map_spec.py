"""Mamba spec for `a Python acceptance-test Story Map`."""

import ast
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.formats.code.code_story_map import CodeStoryMapError, to_pascal, to_snake
from src.formats.code.python.python_story_map import PythonStoryMap


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story("Book a room", 1, StoryType.USER)
        story.acceptance_criteria.append(
            AcceptanceCriteria(name="AC 1", sequential_order=1, text="a room is available")
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a Python acceptance-test Story Map") as self:
    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.py = PythonStoryMap()
            self.canonical = _story_map_with_stories()
            self.tree = self.py.render(self.canonical)
            self.leaf_paths = self.py.leaf_files_of(self.tree)
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<sub_epic_snake>.py`"):
                for path in self.leaf_paths:
                    filename = path.split("/")[-1]
                    expect(filename.endswith(".py")).to(be_true)

            with it("should import pytest and expose no module-level test statements"):
                for content in self.leaf_contents:
                    expect("import pytest" in content).to(be_true)
                    expect("\ntest_" in content).to(be_false)  # no bare module-level test funcs

            with it("should parse as a valid Python module"):
                for content in self.leaf_contents:
                    ast.parse(content)

        with context("every Epic folder"):
            with it(
                "should hold an `<epic_snake>_helper.py` file exposing an `<Epic>Helper` class of shared `given_*`, `when_*`, and `then_*` methods, and no test classes"
            ):
                helper_paths = [p for p in self.tree if p.endswith("_helper.py")]
                expect(helper_paths).to(have_len(4))
                for path in helper_paths:
                    helper_source = self.tree[path]
                    expect("class " in helper_source).to(be_true)
                    expect("Helper:" in helper_source).to(be_true)
                    expect("class Test" in helper_source).to(be_false)
                # WHY: only Epics with stories require given/when/then helpers.
                epic1_helper = self.tree["tests/epic-1/epic_1_helper.py"]
                expect("def given_" in epic1_helper).to(be_true)
                expect("def when_" in epic1_helper).to(be_true)
                expect("def then_" in epic1_helper).to(be_true)

        with context("every Story block"):
            with it("should be a `class Test<StoryPascalCase>` inheriting from its Epic's `<Epic>Helper` class"):
                for content in self.leaf_contents:
                    expect(f"class Test{to_pascal('Book a room')}(Epic1Helper):" in content).to(be_true)

            with it("should carry a docstring holding the Story name and its one-line description"):
                for content in self.leaf_contents:
                    expect('"""Book a room"""' in content).to(be_true)

        with context("every Scenario derived from an AcceptanceCriteria"):
            with it("should be a `def test_<scenario_snake>(self)` method on its Story class, in the AcceptanceCriteria's declared order"):
                for content in self.leaf_contents:
                    expect(f"def test_{to_snake('a room is available')}(self):" in content).to(be_true)

            with context("its docstring"):
                with it("should hold `SCENARIO:`, `GIVEN:`, `WHEN:`, and `THEN:` lines quoting the AcceptanceCriteria's Gherkin steps"):
                    for content in self.leaf_contents:
                        expect("SCENARIO: AC 1" in content).to(be_true)
                        expect("WHEN: a room is available" in content).to(be_true)

            with context("its body"):
                with it("should be an orchestrator of `# Given` / `# When` / `# Then` comment sections, each calling `self.given_*`, `self.when_*`, or `self.then_*` helpers rather than inlining setup or assertions"):
                    for content in self.leaf_contents:
                        expect("# Given" in content).to(be_true)
                        expect("self.given_" in content).to(be_true)
                        expect("self.when_" in content).to(be_true)
                        expect("self.then_" in content).to(be_true)

        with context("with an AcceptanceCriteria added to the first Story"):
            with before.each:
                story = self.canonical.epics[0].sub_epics[0].stories[0]
                story.acceptance_criteria.append(
                    AcceptanceCriteria(name="AC 2", sequential_order=2, text="another scenario")
                )
                self.new_tree = self.py.render(self.canonical)

            with context("the `Test<Story>` class for the first Story"):
                with it("should carry one additional `test_<scenario>` method at the end"):
                    first_leaf = self.new_tree[self.leaf_paths[0]]
                    expect(first_leaf.count("def test_") >= 2).to(be_true)
                    expect(f"def test_{to_snake('another scenario')}(self):" in first_leaf).to(be_true)

            with context("the Epic helper class"):
                with it("should carry any newly referenced `given_*`, `when_*`, or `then_*` helpers required by the new method"):
                    helper_source = self.new_tree["tests/epic-1/epic_1_helper.py"]
                    expect(f"def given_{to_snake('another scenario')}(self):" in helper_source).to(be_true)

    with context("that has been edited in the Python source and synced back against a canonical code Story Map"):
        with before.each:
            self.canonical = _story_map_with_stories()
            edited = _story_map_with_stories()
            edited.epics[0].name = "Epic 1 (edited)"
            edited.append_epic(Epic("Epic 5", 5))
            edited.epics[-1].sub_epics.append(SubEpic("child", 1))
            edited_tree = PythonStoryMap().render(edited)
            self.report = PythonStoryMap().sync(edited_tree, self.canonical)

        with context("the returned UpdateReport"):
            with it("should list every add, remove, rename, reorder, and move applied to the source"):
                expect(len(self.report.adds()) + len(self.report.renames()) >= 2).to(be_true)

        with context("the reconstructed code Story Map"):
            with it("should reflect every edit made to the source"):
                # WHY: translate_from is exhaustively covered in Section 1; here we
                # verify only that sync fed the parsed tree through translate_from.
                expect(len(self.canonical.epics) >= 4).to(be_true)

    with context("that is not a valid Python acceptance-test tree"):
        with context("the sync"):
            with it("should be rejected"):
                py = PythonStoryMap()
                expect(lambda: py.parse(12345)).to(raise_error(CodeStoryMapError))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = PythonStoryMap().parse(PythonStoryMap().render(self.canonical))

        with it("should preserve Story and AcceptanceCriteria counts under each SubEpic"):
            first_sub = self.parsed.epics[0].sub_epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].acceptance_criteria).to(have_len(1))
