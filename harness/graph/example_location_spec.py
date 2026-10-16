"""An example declaration lives in an examples folder, not in the story that uses it."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from practices.stories.model.graph_story_model import GraphStoryModel
from practices.stories.model.story_model import StoryModel
from practices.stories.rules.acceptance_tests import ExampleRoleNames


class _Source:
    def __init__(self, file: str) -> None:
        self.file = file


class _Example:
    type = "Example"
    name = "resentValidationCode"

    def __init__(self, file: str) -> None:
        self.source = _Source(file)


class _Context:
    def __init__(self, text: str) -> None:
        self._text = text

    def text(self, node) -> str:
        return self._text


with description("example location"):
    with it("should read the declaration from the examples folder beside the story"):
        root = _REPO / "harness" / "graph" / "examples" / "input"
        story = "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts"
        found, _line, _end = GraphStoryModel(StoryModel())._example_span(
            str(root),
            "resentValidationCode",
            story,
            215,
            276,
        )
        expect(found).to(equal(
            "tests/onboard-a-customer/authenticate-user/examples/validation-code.examples.ts"
        ))

    with it("should ignore a const of the same name in the story file"):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            story_rel = "tests/authenticate-user/authenticate_user.story.shared.ts"
            story = root / story_rel
            story.parent.mkdir(parents=True)
            story.write_text("const resentValidationCode = { code: 'from the story' };\n", encoding="utf-8")
            fixture = root / "tests/authenticate-user/examples/validation-code.examples.ts"
            fixture.parent.mkdir()
            fixture.write_text("export const resentValidationCode = { code: '654321' };\n", encoding="utf-8")
            found, line, _end = GraphStoryModel(StoryModel())._example_span(
                str(root),
                "resentValidationCode",
                story_rel,
                215,
                276,
            )
        expect(found).to(equal("tests/authenticate-user/examples/validation-code.examples.ts"))
        expect(line).to(equal(1))

    with it("should not treat a story file as an example export"):
        hits = ExampleRoleNames().check(
            _Example("tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts"),
            _Context("export const resentValidationCode = { code: '654321' };"),
        )
        expect(hits).to(equal([]))
