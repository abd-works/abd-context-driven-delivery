"""BDD rules on python widget_spec fixtures."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mamba import context, description, it

from harness.graph.bdd_example_harness import assert_bdd_source_pair

_LAYER_FAULT = Path(
    "/workspace/practices/bdd/model/python/.examples/layer-isolation/widget_spec.py"
).read_text(encoding="utf-8")
_LAYER_CLEAN = "def test_apply():\n    assert True\n"


with description("BDD example specs"):
    with context("layer-isolation"):
        with it("should flag import-time patch decorators"):
            assert_bdd_source_pair("layer-isolation", _LAYER_FAULT, _LAYER_CLEAN)
