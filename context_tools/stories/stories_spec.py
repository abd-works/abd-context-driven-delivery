"""BDD spec for Stories generator - fidelity defaults, transform, diagnostic, contexts."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from context_tools.stories.stories import Stories
from primitives.actions.action import _ActionExpander
from utilities.diagnose.diagnose import Diagnose

_SAMPLE_MARKDOWN = """\
(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
        (S) Customer --> Add Item To Cart
"""


def _expanded(stories, action_name):
    func = getattr(type(stories), action_name)
    body = _ActionExpander.instance().parse_body(func, stories)
    return "\n".join(body.prose_parts)


with description("Stories"):
    with context("that is constructed with fidelity story_map"):
        with before.each:
            self.stories = Stories(fidelity="story_map")

        with it("should default format to markdown"):
            expect(self.stories.format).to(equal("markdown"))

        with it("should retain fidelity story_map"):
            expect(self.stories.fidelity).to(equal("story_map"))

    with context("that is constructed with fidelity scenarios"):
        with before.each:
            self.stories = Stories(fidelity="scenarios")

        with it("should default format to markdown"):
            expect(self.stories.format).to(equal("markdown"))

        with it("should retain fidelity scenarios"):
            expect(self.stories.fidelity).to(equal("scenarios"))

    with context("that is constructed with fidelity acceptance_tests"):
        with it("should default format to python"):
            expect(Stories(fidelity="acceptance_tests").format).to(equal("python"))

    with context("that is constructed with an unsupported fidelity"):
        with it("should raise ValueError"):
            expect(lambda: Stories(fidelity="discovery")).to(raise_error(ValueError))

        with it("should raise ValueError for unknown names"):
            expect(lambda: Stories(fidelity="nope")).to(raise_error(ValueError))

    with context("that is constructed with an unsupported format"):
        with it("should raise ValueError"):
            expect(lambda: Stories(fidelity="story_map", format="yaml")).to(
                raise_error(ValueError)
            )

    with context("that provides a Diagnose companion"):
        with it("should return a Diagnose instance from diagnostic"):
            expect(Stories().diagnostic()).to(be_a(Diagnose))

    with context("that provides a CleanEngineering companion via ce()"):
        with it("should pass a code format through to the companion"):
            stories = Stories(fidelity="acceptance_tests", format="typescript")
            expect(stories.ce().format).to(equal("typescript"))

        with it("should pass python through unchanged"):
            stories = Stories(fidelity="acceptance_tests", format="python")
            expect(stories.ce().format).to(equal("python"))

        with it("should fall back to CE's own default for a non-code format"):
            stories = Stories(fidelity="story_map", format="markdown")
            expect(stories.ce().format).to(equal("python"))

    with context("whose satisfy action is expanded"):
        with it("should tell the agent to call diagnostic().diagnose() when a scenario keeps failing"):
            prose = _expanded(Stories(), "satisfy")
            expect("diagnostic().diagnose()" in prose).to(be_true)

        with it("should tell the agent to call ce().satisfy() to keep production GREEN"):
            prose = _expanded(Stories(), "satisfy")
            expect("ce().satisfy()" in prose).to(be_true)

        with it("should list diagnose as a tool step without inlining the six phases"):
            stories = Stories()
            body = _ActionExpander.instance().parse_body(type(stories).satisfy, stories)
            expect("diagnose" in body.tool_steps).to(be_true)
            prose = "\n".join(body.prose_parts)
            expect("Phase 1 - Build a feedback loop" in prose).to(equal(False))

    with context("whose iterate action is expanded"):
        with it("should tell the agent to call diagnostic().diagnose() when a scenario keeps failing"):
            prose = _expanded(Stories(), "iterate")
            expect("diagnostic().diagnose()" in prose).to(be_true)

    with context("whose transform tool converts markdown to python"):
        with before.each:
            self.stories = Stories(fidelity="story_map")
            self.result = self.stories.transform(
                source_format="markdown",
                target_format="python",
                content=_SAMPLE_MARKDOWN,
            )

        with it("should return a dict"):
            expect(isinstance(self.result, dict)).to(be_true)

        with it("should set format to python"):
            expect(self.result["format"]).to(equal("python"))

        with it("should set content to a dict of path->file text"):
            expect(isinstance(self.result["content"], dict)).to(be_true)
            expect(len(self.result["content"]) > 0).to(be_true)
            for path, text in self.result["content"].items():
                expect(isinstance(path, str)).to(be_true)
                expect(isinstance(text, str)).to(be_true)

    with context("whose contexts slot is expanded"):
        with before.each:
            self.stories = Stories(fidelity="story_map")
            self.contexts = self.stories.contexts().expand()

        with it("should return non-empty prose"):
            expect(len(self.contexts) > 0).to(be_true)

        with it("should include the verb-noun-format rule slug"):
            expect("verb-noun-format" in self.contexts).to(be_true)

        with it("should name the story_map fidelity"):
            expect("story_map" in self.contexts).to(be_true)
