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
    with context("that is constructed with fidelity scaffold"):
        with before.each:
            self.stories = Stories(fidelity="scaffold")

        with it("should default format to markdown"):
            expect(self.stories.format).to(equal("markdown"))

        with it("should retain fidelity scaffold"):
            expect(self.stories.fidelity).to(equal("scaffold"))

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

        with it("should default format to typescript"):
            expect(self.stories.format).to(equal("typescript"))

        with it("should retain fidelity scenarios"):
            expect(self.stories.fidelity).to(equal("scenarios"))

    with context("that is constructed with fidelity acceptance_tests"):
        with it("should default format to typescript"):
            expect(Stories(fidelity="acceptance_tests").format).to(equal("typescript"))

    with context("that is constructed with an unsupported fidelity"):
        with it("should raise ValueError"):
            expect(lambda: Stories(fidelity="not-a-fidelity")).to(raise_error(ValueError))

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

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, or iterate"):
            host = Stories()
            for name in (
                "generate",
                "validate",
                "satisfy",
                "repair",
                "grill",
                "sketch",
                "iterate",
            ):
                expect(name in host.actions).to(equal(False))

    with context("whose guidance action is expanded"):
        with it("should name `{story}.{tier}.ts` at acceptance_tests"):
            prose = _expanded(Stories(fidelity="acceptance_tests"), "guidance")
            expect("{story}.{tier}.ts" in prose).to(be_true)

        with it("should tell the agent to write epic/sub-epic/story names only at scaffold"):
            prose = _expanded(Stories(fidelity="scaffold"), "guidance")
            expect("names only" in prose).to(be_true)

        with it("should tell the agent to call diagnostic().diagnose() when a scenario keeps failing"):
            prose = _expanded(Stories(), "guidance")
            expect("diagnostic().diagnose()" in prose).to(be_true)

        with it("should tell the caller to call companion guidance and pass it to this action"):
            prose = _expanded(Stories(), "guidance")
            expect("call guidance" in prose).to(be_true)
            expect("pass that companion to this action" in prose).to(be_true)
            expect("already knows what to do" in prose).to(be_true)
            expect("Clean Engineering" in prose).to(be_true)

        with it("should NOT inline CleanEngineering generate instructions"):
            prose = _expanded(Stories(), "guidance")
            expect("Deepen OO design" in prose).to(equal(False))

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

    with context("whose contexts slot is expanded at story_map"):
        with before.each:
            self.stories = Stories(fidelity="story_map")
            self.contexts = self.stories.contexts().expand()

        with it("should return non-empty prose"):
            expect(len(self.contexts) > 0).to(be_true)

        with it("should include Shared rules and the story_map heading"):
            expect("## Shared rules" in self.contexts).to(be_true)
            expect("## story_map" in self.contexts).to(be_true)

        with it("should include the verb-noun-format rule slug"):
            expect("verb-noun-format" in self.contexts).to(be_true)

        with it("should omit other fidelity headings"):
            expect("## scenarios" in self.contexts).to(equal(False))
            expect("## acceptance_tests" in self.contexts).to(equal(False))

        with it("should omit scenario-only rule slugs"):
            expect("gwt-steps-trace-to-domain-operations" in self.contexts).to(equal(False))

    with context("whose contexts slot is expanded at scenarios"):
        with before.each:
            self.stories = Stories(fidelity="scenarios")
            self.contexts = self.stories.contexts().expand()

        with it("should include the gwt-steps-trace-to-domain-operations rule slug"):
            expect("gwt-steps-trace-to-domain-operations" in self.contexts).to(be_true)

        with it("should include the reconcile-live-immediately rule slug"):
            expect("reconcile-live-immediately" in self.contexts).to(be_true)

        with it("should include the explain-deep-link-arrival rule slug"):
            expect("explain-deep-link-arrival" in self.contexts).to(be_true)

        with it("should include the then-and-chaining rule slug"):
            expect("then-and-chaining" in self.contexts).to(be_true)

        with it("should include the when-holds-the-operation rule slug"):
            expect("when-holds-the-operation" in self.contexts).to(be_true)

        with it("should include the given-only-what-the-system-checks rule slug"):
            expect("given-only-what-the-system-checks" in self.contexts).to(be_true)

        with it("should include the load-with-identity-in-hand rule slug"):
            expect("load-with-identity-in-hand" in self.contexts).to(be_true)

        with it("should include the reuse-owning-aggregate-stubs rule slug"):
            expect("reuse-owning-aggregate-stubs" in self.contexts).to(be_true)

        with it("should include the infrastructure-in-lifecycle-hooks rule slug"):
            expect("infrastructure-in-lifecycle-hooks" in self.contexts).to(be_true)

        with it("should include the extract-assertion-helper rule slug"):
            expect("extract-assertion-helper" in self.contexts).to(be_true)

        with it("should include the seed-prior-story-as-given rule slug"):
            expect("seed-prior-story-as-given" in self.contexts).to(be_true)

        with it("should omit the story_map heading"):
            expect("## story_map" in self.contexts).to(equal(False))

    with context("whose examples slot is expanded at markdown"):
        with it("should omit python example files"):
            text = Stories(fidelity="story_map", format="markdown").examples().expand()
            expect("/py/" in text).to(equal(False))
            expect("/md/" in text).to(be_true)

        with it("should keep story-map and thin-slice and omit scenario examples"):
            text = Stories(fidelity="story_map", format="markdown").examples().expand()
            expect("story-map.md" in text).to(be_true)
            expect("thin-slice.md" in text).to(be_true)
            expect("scenario-main-flow.md" in text).to(equal(False))
            expect("scenario-outline.md" in text).to(equal(False))

    with context("whose templates slot is expanded at story_map markdown"):
        with before.each:
            self.templates = Stories(
                fidelity="story_map", format="markdown", session=None
            ).templates().expand()

        with it("should inline the markdown story-map and thin-slice templates"):
            expect("Story Map" in self.templates).to(be_true)
            expect("Thin slicing" in self.templates).to(be_true)
            expect("story-context.md" in self.templates).to(equal(False))

        with it("should omit scenario templates, sketch, and other-format story classes"):
            expect("scenario-outline" in self.templates).to(equal(False))
            expect("Stories sketch — match active fidelity" in self.templates).to(
                equal(False)
            )
            expect("StoryVerbNoun" in self.templates).to(equal(False))
            expect("_story.ts" in self.templates).to(equal(False))
            expect("_story.py" in self.templates).to(equal(False))

    with context("whose templates slot is expanded at scenarios python"):
        with before.each:
            self.templates = Stories(
                fidelity="scenarios", format="python", session=None
            ).templates().expand()

        with it("should inline the flat scenario-template without helpers"):
            expect("scenario-template.py" in self.templates).to(be_true)
            expect("story_test.py" in self.templates).to(be_true)
            expect('story("{Story Verb-Noun}"' in self.templates).to(be_true)
            expect("def story(" in self.templates).to(be_true)
            expect("from story_test import" in self.templates).to(be_true)
            expect("background(" in self.templates).to(be_true)
            expect("scenario(" in self.templates).to(be_true)
            expect("before_all(" in self.templates).to(be_true)
            expect("after_all(" in self.templates).to(be_true)
            expect("lambda when, then:" in self.templates).to(equal(False))
            expect("bdd-gwt" in self.templates).to(equal(False))
            expect("with description(" in self.templates).to(equal(False))
            expect("def story(" in self.templates).to(be_true)
            expect("lambda when, then:" in self.templates).to(equal(False))
            expect("@story" in self.templates).to(equal(False))
            expect("@background" in self.templates).to(equal(False))
            expect("@scenario" in self.templates).to(equal(False))
            expect("_primary_when" in self.templates).to(equal(False))
            expect("_invalid_input" in self.templates).to(equal(False))
            expect("from givens import" in self.templates).to(equal(False))
            expect("from whens import" in self.templates).to(equal(False))
            expect('from "./givens"' in self.templates).to(equal(False))
            expect('from "./whens"' in self.templates).to(equal(False))
            expect("artifacts-mirror-story-hierarchy" in self.templates).to(be_true)
            expect("_test_helper.py" in self.templates).to(equal(False))
            expect("_test_helper.ts" in self.templates).to(equal(False))
            expect("Protocol" in self.templates).to(equal(False))

    with context("whose templates slot is expanded at scenarios typescript"):
        with it("should inline sign-up-style scenario-template.ts"):
            text = Stories(
                fidelity="scenarios", format="typescript", session=None
            ).templates().expand()
            expect("scenario-template.ts" in text).to(be_true)
            expect("story-test.ts" in text).to(be_true)
            expect("export function story" in text).to(be_true)
            expect("export function background" in text).to(be_true)
            expect("Naming rules" in text).to(be_true)
            expect("background(({ given })" in text).to(be_true)
            expect("beforeAll" in text).to(be_true)
            expect("afterAll" in text).to(be_true)
            expect(".and(" in text).to(be_true)
            expect('from "vitest"' in text).to(be_true)
            expect('from "./givens"' in text).to(equal(False))
            expect('from "./whens"' in text).to(equal(False))
            expect("_test_helper.ts" in text).to(equal(False))
            expect("_test_helper.py" in text).to(equal(False))
