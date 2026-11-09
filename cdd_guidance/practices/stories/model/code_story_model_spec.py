"""Mamba spec for `a code Story Map`: the folder and file layout every language shares, observed through Python
story tests. The code inside each file is covered by the TypeScript, Python, JavaScript, and Java specs."""

from expects import be_false, be_true, equal, expect, have_len, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModelError
from cdd_guidance.practices.stories.model.java.java_story_model import JavaStoryModel
from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Story, StoryModel, StoryType
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel


def story_named(name: str) -> Story:
    story = Story(name, 1, StoryType.USER)
    story.scenarios.append(Scenario(name=f"{name} works", sequential_order=1))
    return story


def epics_each_with_a_story(count: int) -> StoryModel:
    story_map = StoryModel()
    for order in range(1, count + 1):
        epic = Epic(f"Epic {order}", order)
        epic.stories.append(story_named(f"Story of epic {order}"))
        story_map.append_epic(epic)
    return story_map


def first_epic_with_three_sub_epics() -> StoryModel:
    story_map = epics_each_with_a_story(4)
    first = story_map.epics[0]
    for order in range(1, 4):
        sub_epic = Epic(f"Epic 1.{order}", order)
        sub_epic.stories.append(story_named(f"Story {order}"))
        first.epics.append(sub_epic)
    return story_map


def files_under(tree: dict, folder: str) -> list:
    return [path for path in tree if path.startswith(f"{folder}/")]


with description("a code Story Map") as self:
    with before.each:
        self.code_map = PythonStoryModel("tests")

    with it("should write no files for an empty Story Map"):
        expect(self.code_map.render(StoryModel())).to(equal({}))

    with context("with 4 Epics that each hold their own Story"):
        with before.each:
            self.canonical = epics_each_with_a_story(4)
            self.tree = self.code_map.render(self.canonical)

        with it("should write each Epic's stories into a folder named after the Epic"):
            expect(sorted(self.tree)).to(equal([
                "tests/epic-1/epic_1_story.test.py",
                "tests/epic-2/epic_2_story.test.py",
                "tests/epic-3/epic_3_story.test.py",
                "tests/epic-4/epic_4_story.test.py",
            ]))

        with it("should read back every Epic"):
            expect([epic.name for epic in self.code_map.parse(self.tree).epics]).to(
                equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"])
            )

        with it("should read back each Epic's own Story"):
            parsed = self.code_map.parse(self.tree)
            expect([story.name for epic in parsed.epics for story in epic.stories]).to(
                equal([f"Story of epic {order}" for order in range(1, 5)])
            )

        with context("with a fifth Epic appended"):
            with before.each:
                fifth = Epic("Epic 5", 5)
                fifth.stories.append(story_named("Story of epic 5"))
                self.canonical.append_epic(fifth)
                self.new_tree = self.code_map.render(self.canonical)

            with it("should write a new folder for the appended Epic"):
                expect(files_under(self.new_tree, "tests/epic-5")).to(have_len(1))

            with it("should leave the files of the first four Epics byte-identical"):
                for path, content in self.tree.items():
                    expect(self.new_tree[path]).to(equal(content))

        with context("with the first Epic removed"):
            with before.each:
                self.canonical.epics.pop(0)
                self.new_tree = self.code_map.render(self.canonical)

            with it("should write nothing under the removed Epic's folder"):
                expect(files_under(self.new_tree, "tests/epic-1")).to(have_len(0))

            with it("should still write the files of the remaining Epics"):
                for path in files_under(self.tree, "tests/epic-2") + files_under(self.tree, "tests/epic-4"):
                    expect(path in self.new_tree).to(be_true)

        with context("with the first Epic renamed"):
            with before.each:
                self.canonical.epics[0].name = "Epic 1 renamed"
                self.new_tree = self.code_map.render(self.canonical)

            with it("should write the Epic's folder under the new slug"):
                expect(files_under(self.new_tree, "tests/epic-1-renamed")).to(have_len(1))

            with it("should keep the Epic's Story in the renamed folder"):
                content = self.new_tree["tests/epic-1-renamed/epic_1_renamed_story.test.py"]
                expect("Story of epic 1" in content).to(be_true)

    with context("with the first Epic holding 3 sub-Epics"):
        with before.each:
            self.canonical = first_epic_with_three_sub_epics()
            self.first_epic = self.canonical.epics[0]
            self.tree = self.code_map.render(self.canonical)

        with it("should write one file per sub-Epic inside the first Epic's folder"):
            for order in range(1, 4):
                expect(f"tests/epic-1/epic_1_{order}_story.test.py" in self.tree).to(be_true)

        with it("should keep the first Epic's own Story in its own file beside them"):
            expect("tests/epic-1/epic_1_story.test.py" in self.tree).to(be_true)

        with it("should read back the sub-Epics under the first Epic"):
            parsed = self.code_map.parse(self.tree)
            expect([sub.name for sub in parsed.epics[0].epics]).to(equal(["Epic 1.1", "Epic 1.2", "Epic 1.3"]))

        with context("with a sub-Epic appended to the first Epic"):
            with before.each:
                appended = Epic("Epic 1.4", 4)
                appended.stories.append(story_named("Story 4"))
                self.first_epic.epics.append(appended)
                self.new_tree = self.code_map.render(self.canonical)

            with it("should write a new file for the appended sub-Epic"):
                expect("tests/epic-1/epic_1_4_story.test.py" in self.new_tree).to(be_true)

            with it("should leave the files of the first three sub-Epics byte-identical"):
                for order in range(1, 4):
                    path = f"tests/epic-1/epic_1_{order}_story.test.py"
                    expect(self.new_tree[path]).to(equal(self.tree[path]))

        with context("with the first sub-Epic renamed"):
            with before.each:
                self.first_epic.epics[0].name = "Epic 1.1 renamed"
                self.new_tree = self.code_map.render(self.canonical)

            with it("should write the sub-Epic's file under the new name"):
                expect("tests/epic-1/epic_1_1_renamed_story.test.py" in self.new_tree).to(be_true)

            with it("should no longer write the file under the old name"):
                expect("tests/epic-1/epic_1_1_story.test.py" in self.new_tree).to(be_false)

            with it("should keep the sub-Epic's Story in the renamed file"):
                expect("Story 1" in self.new_tree["tests/epic-1/epic_1_1_renamed_story.test.py"]).to(be_true)

        with context("with a nested sub-Epic added under the first sub-Epic"):
            with before.each:
                first_sub_epic = self.first_epic.epics[0]
                nested = Epic("Nested", 1)
                nested.stories.append(story_named("Nested Story"))
                first_sub_epic.epics.append(nested)
                self.new_tree = self.code_map.render(self.canonical)

            with it("should make the first sub-Epic a folder holding the nested sub-Epic's file"):
                expect("tests/epic-1/epic-1-1/nested_story.test.py" in self.new_tree).to(be_true)

            with it("should keep the first sub-Epic's own Stories in a file inside its folder"):
                expect("tests/epic-1/epic-1-1/epic_1_1_story.test.py" in self.new_tree).to(be_true)

            with it("should read the nested sub-Epic back under the first sub-Epic"):
                parsed = self.code_map.parse(self.new_tree)
                expect([nested.name for nested in parsed.epics[0].epics[0].epics]).to(equal(["Nested"]))

    with context("that holds hand-written code in a story file outside the generated Story blocks"):
        with before.each:
            self.typescript_map = TypeScriptStoryModel("tests")
            self.canonical = first_epic_with_three_sub_epics()
            initial_tree = self.typescript_map.render(self.canonical)
            self.first_file_path = next(path for path in initial_tree if path.endswith("epic_1_1_story.test.ts"))
            self.previous_tree = dict(initial_tree)
            self.previous_tree[self.first_file_path] = (
                initial_tree[self.first_file_path] + "\nconst mySetupVariable = 42;\n"
            )

        with context("with the story file written again from the canonical Story Map and the previous tree"):
            with before.each:
                self.new_tree = self.typescript_map.render(self.canonical, previous=self.previous_tree)

            with it("should keep the hand-written code byte-for-byte"):
                expect("const mySetupVariable = 42;" in self.new_tree[self.first_file_path]).to(be_true)

            with it("should still write the Story blocks from the canonical Story Map"):
                expect("story('Story 1', () => {" in self.new_tree[self.first_file_path]).to(be_true)

    with context("that has been asked to parse a value that is not a mapping of paths to file content"):
        with it("should reject it"):
            expect(lambda: self.code_map.parse("not a mapping")).to(raise_error(CodeStoryModelError))


def epic_names_read_back(model) -> list:
    """The epic names model reads back from the files it writes for four epics."""
    return [epic.name for epic in model.parse(model.render(epics_each_with_a_story(4))).epics]


with description("a code Story Map under a tests root two folders deep") as self:
    with context("in Python"):
        with it("should read each epic from the folder below the tests root"):
            expect(epic_names_read_back(PythonStoryModel("stories/tests"))).to(equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"]))

    with context("in JavaScript"):
        with it("should read each epic from the folder below the tests root"):
            expect(epic_names_read_back(JavaScriptStoryModel("stories/tests"))).to(equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"]))

    with context("in Java"):
        with it("should read each epic from the folder below the tests root"):
            expect(epic_names_read_back(JavaStoryModel("stories/tests"))).to(equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"]))

    with context("in TypeScript"):
        with it("should read each epic from the folder below the tests root"):
            expect(epic_names_read_back(TypeScriptStoryModel("stories/tests"))).to(equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"]))


with description("a code Story Map asked which files are its story files") as self:
    with context("in Java"):
        with it("should leave out a helper beside a story file"):
            expect(JavaStoryModel.is_story_file("tests/checkout/PaymentHelper.java")).to(be_false)

    with context("in TypeScript"):
        with it("should leave out a story file under an examples folder"):
            expect(TypeScriptStoryModel.is_story_file("tests/checkout/examples/card_story.test.ts")).to(be_false)

        with it("should take a shared story file"):
            expect(TypeScriptStoryModel.is_story_file("tests/checkout/pay.story.shared.ts")).to(be_true)


with description("a story read from a TypeScript story file") as self:
    with before.each:
        from cdd_guidance.practices.stories.model.brace_story_file import BraceStoryFile
        from cdd_guidance.practices.clean_engineering.model.code_body import TYPESCRIPT

        text = (
            "story('Pay by card', () => {\n"
            "  const card = new Card();\n"
            "  scenario('the card is charged', ({ given }) => {\n"
            "    given('a basket', () => {\n"
            "      basket.add(item);\n"
            "    });\n"
            "  });\n"
            "});\n"
        )
        self.story = BraceStoryFile(TYPESCRIPT, text).stories(TypeScriptStoryModel.story_type, "pay.ts")[0][0]

    with it("should keep the line that opens its block"):
        expect(self.story.written.heading).to(equal(["story('Pay by card', () => {"]))

    with it("should keep the code it shares between its scenarios as its setup"):
        expect(self.story.setup.text.strip()).to(equal("const card = new Card();"))

    with it("should give its scenario's step the body its block holds"):
        expect(self.story.scenarios[0].steps[0].body.text.strip()).to(equal("basket.add(item);"))


# A story file is read once: each story is made from its own block, so a story whose comment names it differently from
# its call still keeps the code it was written with, and sits on the lines of its block.
with description("a TypeScript story file whose story comment names the story differently from its call") as self:
    with before.each:
        text = (
            'import { scenario, story } from "story-test";\n'
            "\n"
            "/**\n"
            " * Story: Pay\n"
            " */\n"
            "story('Pay by card', () => {\n"
            "  scenario('the card is charged', ({ given }) => {\n"
            "    given('a basket', () => {\n"
            "      basket.add(item);\n"
            "    });\n"
            "  });\n"
            "});\n"
        )
        self.path = "tests/shop/pay_story.test.ts"
        self.story = TypeScriptStoryModel().parse({self.path: text}).every_story()[0]

    with it("should take the name its comment gives"):
        expect(self.story.name).to(equal("Pay"))

    with it("should keep the code it was written with"):
        expect(self.story.written is not None).to(be_true)

    with it("should sit on the lines of its story call"):
        expect((self.story.source.file, self.story.source.start_line, self.story.source.end_line)).to(equal((self.path, 6, 12)))
