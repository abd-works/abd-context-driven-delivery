"""Specs for a story file in code, read once by the kind its language's model picks: block by block, or from its text
alone when its blocks cannot be read."""
from expects import be_a, be_none, equal, expect
from mamba import description, it

from cdd_guidance.practices.stories.model.brace_story_file import BraceStoryFile
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.python.shared_story_file import SharedStoryFile
from cdd_guidance.practices.stories.model.python.story_file import PythonStoryFile
from cdd_guidance.practices.stories.model.screen_spec_file import ScreenSpecFile
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

_PYTHON = 'with story("Pay by card"):\n    with scenario("the card is charged"):\n        with given("a basket"):\n            pass\n'
_BROKEN_PYTHON = 'with story("Pay by card"):\n    with scenario("the card is charged"):\n        with given("a basket"):\n            basket.add(\n'
_SHARED = '@stories.scenario("Pay by card", "the card is charged")\ndef charged(s):\n    pass\n'
_SCREEN = "test.describe('Pay by card', () => {\n  test('the card is charged', async ({ page }) => {\n    await page.goto('/');\n  });\n});\n"


with description("a story file in code"):
    with it("should be read block by block in Python"):
        expect(PythonStoryModel().story_file("pay_story.test.py", _PYTHON)).to(be_a(PythonStoryFile))

    with it("should be a shared story file when Python writes its scenarios as functions"):
        expect(PythonStoryModel().story_file("pay.story.shared.py", _SHARED)).to(be_a(SharedStoryFile))

    with it("should be a screen spec when TypeScript describes tests"):
        expect(TypeScriptStoryModel().story_file("pay.story.ui.spec.ts", _SCREEN)).to(be_a(ScreenSpecFile))

    with it("should be read block by block in TypeScript otherwise"):
        expect(TypeScriptStoryModel().story_file("pay_story.test.ts", "story('Pay by card', () => {});\n")).to(be_a(BraceStoryFile))

    with description("whose blocks it reads"):
        with it("should hold each story with its scenarios"):
            story = PythonStoryModel().story_file("pay_story.test.py", _PYTHON).stories[0]
            expect([story.name, [scenario.name for scenario in story.scenarios]]).to(equal(["Pay by card", ["the card is charged"]]))

        with it("should keep the file's own code around its stories"):
            expect(PythonStoryModel().story_file("pay_story.test.py", _PYTHON).own_code.path).to(equal("pay_story.test.py"))

    with description("that Python cannot parse"):
        with it("should still hold its stories, read from its text"):
            story = PythonStoryModel().story_file("pay_story.test.py", _BROKEN_PYTHON).stories[0]
            expect([story.name, [scenario.name for scenario in story.scenarios]]).to(equal(["Pay by card", ["the card is charged"]]))

        with it("should keep none of its own code"):
            expect(PythonStoryModel().story_file("pay_story.test.py", _BROKEN_PYTHON).own_code).to(be_none)

    with description("with no story block"):
        with it("should be one story read from its text"):
            expect(len(PythonStoryModel().story_file("pay_story.test.py", "x = 1\n").stories)).to(equal(1))
