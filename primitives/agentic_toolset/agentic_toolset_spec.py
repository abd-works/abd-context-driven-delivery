"""BDD spec — agentic toolset compound instructions."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import context, description, it

from context_tools.context_guidance.fixtures.agentic_ops.agentic_ops import SampleAgenticOps


with description("a toolset module with several agent-instructions operations"):
    with context("with the instructions property read on a loaded instance"):
        with it("should assemble one compound instructions string from each registered operation"):
            host = SampleAgenticOps()
            text = host.instructions
            keys = set(host.instructions_registry)
            expect(text).to(contain("compound generate instructions"))
            expect(text).to(contain("compound sketch instructions"))
            expect("generate" in keys).to(equal(True))
            expect("sketch" in keys).to(equal(True))
