"""BDD spec for Stories generator — fidelity defaults, transform, contexts."""

import sys
from pathlib import Path

from expects import be_true, equal, expect, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import contexts  # noqa: F401 — generator package on path
from contexts.stories.stories import Stories

_SAMPLE_MARKDOWN = """\
(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
        (S) Customer --> Add Item To Cart
"""


with description("Stories fidelity and format defaults"):
    with context("Stories constructed with fidelity discovery"):
        with before.each:
            self.stories = Stories(fidelity="discovery")

        with it("should default format to markdown"):
            expect(self.stories.format).to(equal("markdown"))

        with it("should retain fidelity discovery"):
            expect(self.stories.fidelity).to(equal("discovery"))

    with context("Stories constructed with fidelity exploration"):
        with before.each:
            self.stories = Stories(fidelity="exploration")

        with it("should default format to python"):
            expect(self.stories.format).to(equal("python"))

        with it("should retain fidelity exploration"):
            expect(self.stories.fidelity).to(equal("exploration"))

    with context("Stories constructed with fidelity specification"):
        with it("should default format to python"):
            expect(Stories(fidelity="specification").format).to(equal("python"))

    with context("Stories constructed with fidelity engineering"):
        with it("should default format to python"):
            expect(Stories(fidelity="engineering").format).to(equal("python"))

    with context("Stories constructed with an unsupported fidelity"):
        with it("should raise ValueError"):
            expect(lambda: Stories(fidelity="nope")).to(raise_error(ValueError))

    with context("Stories constructed with an unsupported format"):
        with it("should raise ValueError"):
            expect(lambda: Stories(fidelity="discovery", format="yaml")).to(
                raise_error(ValueError)
            )


with description("Stories transform tool"):
    with context("transform from markdown to python"):
        with before.each:
            self.stories = Stories(fidelity="discovery")
            self.result = self.stories.transform(
                source_format="markdown",
                target_format="python",
                content=_SAMPLE_MARKDOWN,
            )

        with it("should return a dict"):
            expect(isinstance(self.result, dict)).to(be_true)

        with it("should set format to python"):
            expect(self.result["format"]).to(equal("python"))

        with it("should set content to a dict of path→file text"):
            expect(isinstance(self.result["content"], dict)).to(be_true)
            expect(len(self.result["content"]) > 0).to(be_true)
            for path, text in self.result["content"].items():
                expect(isinstance(path, str)).to(be_true)
                expect(isinstance(text, str)).to(be_true)


with description("Stories contexts instruction"):
    with context("the contexts slot is expanded"):
        with before.each:
            self.stories = Stories(fidelity="discovery")
            self.contexts = self.stories.contexts().expand()

        with it("should return non-empty prose"):
            expect(len(self.contexts) > 0).to(be_true)

        with it("should include the verb-noun-format rule slug"):
            expect("verb-noun-format" in self.contexts).to(be_true)

        with it("should name the discovery fidelity"):
            expect("discovery" in self.contexts).to(be_true)
