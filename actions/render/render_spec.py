"""BDD spec for the Render action — Guidance refs, fidelity, and source format."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import description, it

from actions.render.render import Render

_REF = "practices.clean_engineering.clean_engineering:CleanEngineering"
_STORIES = "practices.stories.stories:Stories"
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


with description("Render"):
    with it("should convert python on a Guidance ref string when source is python"):
        results = Render().render(
            _REF,
            format="markdown",
            content=_PYTHON,
            source="python",
        )
        expect(len(results)).to(equal(1))
        expect(str(results[0]["content"])).to(contain("Cart"))

    with it("should construct the Guidance at the given fidelity"):
        results = Render().render(
            {"toolset": _REF, "fidelity": "model"},
            format="markdown",
            content=_PYTHON,
        )
        expect(str(results[0]["content"])).to(contain("Cart"))

    with it("should convert a story map when source is md"):
        results = Render().render(
            _STORIES,
            format="drawio",
            content=_STORY_MAP,
            source="md",
        )
        expect(str(results[0]["content"])).to(contain("mxGraphModel"))
