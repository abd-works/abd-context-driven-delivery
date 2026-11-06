"""BDD spec for the Render action — Guidance refs, fidelity, and source format."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import description, it

from cdd_guidance.actions.render.render import Render

_REF = "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering"
_STORIES = "cdd_guidance.practices.stories.stories:Stories"
_PYTHON = '''\
class Cart:
    """Cart holds line items and places orders."""

    def __init__(self, owner: str) -> None:
        self.owner = owner
'''
_STORY_MAP = """\
(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Browse Product Catalog
"""
_MARKDOWN_STORY_MAP = """\
# (E) Manage Customer Orders

## (E) Place New Order

### (S) Customer --> Browse Product Catalog
"""
_STORY_TEST = '''\
from story_test import given, scenario, story, then, when

with story("Browse Product Catalog"):
    with scenario("Show the products in stock"):
        with given("the catalog holds a kettle in stock"):
            pass
        with when("the Customer opens the catalog"):
            pass
        with then("the kettle is listed"):
            pass
'''


with description("Render"):
    with it("should convert python on a Guidance ref string when source is python"):
        results = Render().render(
            _REF,
            format="markdown",
            paths=[],
            content=_PYTHON,
            source="python",
        )
        expect(len(results)).to(equal(1))
        expect(str(results[0]["content"])).to(contain("Cart"))

    with it("should construct the Guidance at the given fidelity"):
        results = Render().render(
            {"toolset": _REF, "fidelity": "model"},
            format="markdown",
            paths=[],
            content=_PYTHON,
        )
        expect(str(results[0]["content"])).to(contain("Cart"))

    with it("should convert each guidance slug you type"):
        results = Render().render(
            ["clean-engineering-model", "bdd-behavior"],
            format="python",
            paths=[],
            content="### **Cart**\n+ owner: str\n",
            source="sketch",
        )
        expect(len(results)).to(equal(2))
        expect(results[0]["format"]).to(equal("python"))
        expect(results[1]["format"]).to(equal("python"))

    with it("should convert a story map when source is md"):
        results = Render().render(
            _STORIES,
            format="drawio",
            paths=[],
            content=_STORY_MAP,
            source="md",
        )
        expect(str(results[0]["content"])).to(contain("mxGraphModel"))

    with it("should read a sketch from a file path and leave the document body off the call"):
        folder = Path(tempfile.mkdtemp(prefix="render-paths-"))
        sketch = folder / "cart-sketch.md"
        sketch.write_text("Cart\n  owner\n", encoding="utf-8")
        results = Render().render(
            ["clean-engineering-model"],
            format="python",
            paths=[str(sketch)],
            source="sketch",
        )
        expect(len(results)).to(equal(1))
        expect(str(results[0]["content"])).to(contain("Cart"))

    with it("should read the sketches in a folder"):
        folder = Path(tempfile.mkdtemp(prefix="render-folder-"))
        (folder / "cart-sketch.md").write_text("Cart\n  owner\n", encoding="utf-8")
        results = Render().render(
            ["clean-engineering-model"],
            format="python",
            paths=str(folder),
            source="sketch",
        )
        expect(str(results[0]["content"])).to(contain("Cart"))

    with it("should read the story tests in a folder under their story map"):
        folder = Path(tempfile.mkdtemp(prefix="render-story-tests-"))
        (folder / "story-map.md").write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        story_test = folder / "manage-customer-orders" / "place-new-order" / "browse-product-catalog"
        story_test.mkdir(parents=True)
        (story_test / "browse_product_catalog_story.test.py").write_text(_STORY_TEST, encoding="utf-8")
        results = Render().render(
            ["stories-scenarios"],
            format="markdown",
            paths=str(folder),
            source="python",
        )
        expect(str(results[0]["content"])).to(contain("Scenario: Show the products in stock"))

    with it("should link a rendered story map to the story files beside the map it reads"):
        folder = Path(tempfile.mkdtemp(prefix="render-links-"))
        story_map = folder / "story-map.md"
        story_map.write_text(_MARKDOWN_STORY_MAP, encoding="utf-8")
        story_file = folder / "orders" / "browse_product_catalog_story.test.md"
        story_file.parent.mkdir(parents=True)
        story_file.write_text("## Story: Browse Product Catalog\n", encoding="utf-8")
        results = Render().render(
            _STORIES,
            format="drawio",
            paths=[str(story_map)],
            source="markdown",
        )
        expect(str(results[0]["content"])).to(contain('link="orders/browse_product_catalog_story.test.md"'))
