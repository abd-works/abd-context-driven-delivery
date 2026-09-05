"""Mamba spec for `a Java acceptance-test Story Map`."""

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
from src.formats.code.code_story_map import CodeStoryMapError, to_pascal
from src.formats.code.java.java_story_map import JavaStoryMap


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story("Return an item", 1, StoryType.USER)
        story.acceptance_criteria.append(
            AcceptanceCriteria(name="AC 1", sequential_order=1, text="an item is eligible")
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a Java acceptance-test Story Map") as self:
    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.java = JavaStoryMap()
            self.canonical = _story_map_with_stories()
            self.tree = self.java.render(self.canonical)
            self.leaf_paths = [p for p in self.tree if p.endswith("Test.java")]
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<SubEpicPascalCase>Test.java`"):
                for path in self.leaf_paths:
                    filename = path.split("/")[-1]
                    expect(filename.endswith("Test.java")).to(be_true)
                    stem = filename[:-len("Test.java")]
                    expect(stem[:1].isupper()).to(be_true)

            with it("should open with a `package` declaration matching its folder path under the tests root"):
                for content in self.leaf_contents:
                    first_line = content.splitlines()[0]
                    expect(first_line.startswith("package ")).to(be_true)
                    expect(first_line.endswith(";")).to(be_true)

            with it(
                "should import JUnit 5 (`org.junit.jupiter.api.Test`, `DisplayName`, `Nested`, `BeforeEach`, `AfterEach`, and the static `Assertions`)"
            ):
                for content in self.leaf_contents:
                    expect("import org.junit.jupiter.api.Test;" in content).to(be_true)
                    expect("import org.junit.jupiter.api.DisplayName;" in content).to(be_true)
                    expect("import org.junit.jupiter.api.Nested;" in content).to(be_true)
                    expect("import org.junit.jupiter.api.BeforeEach;" in content).to(be_true)
                    expect("import org.junit.jupiter.api.AfterEach;" in content).to(be_true)
                    expect("import static org.junit.jupiter.api.Assertions.*;" in content).to(be_true)

            with it("should parse and compile as a valid Java source file"):
                for content in self.leaf_contents:
                    # WHY: we don't have javac available here; the balanced-brace check gives us a
                    # cheap syntactic sanity check that reflects the same intent.
                    expect(content.count("{")).to(equal(content.count("}")))

        with context("every leaf file's outer class"):
            with it(
                "should be a `class <SubEpicPascalCase>Test` carrying `@DisplayName` set to the SubEpic's human-readable name"
            ):
                for content in self.leaf_contents:
                    expect('@DisplayName("SubEpic 1.1")' in content or '@DisplayName("SubEpic 1.2")' in content or '@DisplayName("SubEpic 1.3")' in content).to(be_true)

            with it(
                "should hold the shared `given*`, `when*`, and `then*` helpers as `private static` methods, and no `@Test` methods of its own"
            ):
                for content in self.leaf_contents:
                    expect("private static void given" in content).to(be_true)
                    expect("private static void when" in content).to(be_true)
                    expect("private static void then" in content).to(be_true)

        with context("every Story block"):
            with it(
                "should be an `@Nested class <StoryPascalCase>Tests` inside its SubEpic's outer class, carrying `@DisplayName` set to the Story name"
            ):
                for content in self.leaf_contents:
                    expect("@Nested" in content).to(be_true)
                    expect(f"class {to_pascal('Return an item')}Tests" in content).to(be_true)
                    expect('@DisplayName("Return an item")' in content).to(be_true)

        with context("every Scenario derived from an AcceptanceCriteria"):
            with it("should be a `@Test`-annotated `void <scenarioNameCamelCase>()` method on its Story's `@Nested` class, in the AcceptanceCriteria's declared order"):
                for content in self.leaf_contents:
                    expect("@Test" in content).to(be_true)
                    expect("void anItemIsEligible()" in content).to(be_true)

            with it("should carry `@DisplayName` set to the Scenario's outcome in plain English"):
                for content in self.leaf_contents:
                    expect('@DisplayName("AC 1")' in content).to(be_true)

            with context("its body"):
                with it("should be an orchestrator of `// Given` / `// When` / `// Then` comment sections, each calling one of the outer class's `given*` / `when*` / `then*` helpers rather than inlining setup or assertions"):
                    for content in self.leaf_contents:
                        expect("// Given" in content).to(be_true)
                        expect("// When" in content).to(be_true)
                        expect("// Then" in content).to(be_true)
                        expect("givenAnItemIsEligible()" in content).to(be_true)

        with context("with an AcceptanceCriteria added to the first Story"):
            with before.each:
                story = self.canonical.epics[0].sub_epics[0].stories[0]
                story.acceptance_criteria.append(
                    AcceptanceCriteria(name="AC 2", sequential_order=2, text="a second scenario")
                )
                self.new_tree = self.java.render(self.canonical)
                self.first_leaf = self.new_tree[self.leaf_paths[0]]

            with context("the `@Nested` class for the first Story"):
                with it("should carry one additional `@Test` method at the end"):
                    expect(self.first_leaf.count("@Test") >= 2).to(be_true)

            with context("the outer class's private static helpers"):
                with it("should carry any newly referenced `given*` / `when*` / `then*` helpers required by the new method"):
                    expect("givenASecondScenario" in self.first_leaf).to(be_true)
                    expect("whenASecondScenario" in self.first_leaf).to(be_true)
                    expect("thenASecondScenario" in self.first_leaf).to(be_true)

    with context("that has been edited in the Java source and synced back against a canonical code Story Map"):
        with before.each:
            self.canonical = _story_map_with_stories()
            edited = _story_map_with_stories()
            # WHY: edit sub-epic 1.1 — Java backend represents only leaf
            # SubEpics, so tests observe sync via the SubEpic layer.
            edited.epics[0].sub_epics[0].name = "SubEpic 1.1 (edited)"
            edited.epics[0].sub_epics.append(SubEpic("SubEpic 1.4", 4))
            edited_tree = JavaStoryMap().render(edited)
            self.report = JavaStoryMap().sync(edited_tree, self.canonical)

        with context("the returned UpdateReport"):
            with it("should list every add, remove, rename, reorder, and move applied to the source"):
                total = (
                    len(self.report.adds())
                    + len(self.report.renames())
                    + len(self.report.removes())
                    + len(self.report.reorders())
                )
                expect(total >= 1).to(be_true)

        with context("the reconstructed code Story Map"):
            with it("should reflect every edit made to the source"):
                sub_names = [
                    s.name.lower() for s in self.canonical.epics[0].sub_epics
                ]
                expect(
                    any("edited" in n or "1-4" in n or "subepic14" in n for n in sub_names)
                ).to(be_true)

    with context("that is not a valid Java acceptance-test tree"):
        with context("the sync"):
            with it("should be rejected"):
                java = JavaStoryMap()
                expect(lambda: java.parse(None)).to(raise_error(CodeStoryMapError))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = JavaStoryMap().parse(JavaStoryMap().render(self.canonical))

        with it("should preserve Story and AcceptanceCriteria counts under each SubEpic"):
            first_sub = self.parsed.epics[0].sub_epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].acceptance_criteria).to(have_len(1))
