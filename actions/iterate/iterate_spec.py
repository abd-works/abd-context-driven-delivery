"""BDD spec for Iterate toolset + ActionExpander integration."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("iterate", None)

from expects import contain, equal, expect
from mamba import context, description, it

from grill_context.grill_context import GrillContext
from iterate import Iterate
from harness.agent_tools.agent_tools import AgentToolSet


with description("Iterate toolset"):
    with context("that records an iterate tick"):
        with it("should return the iterate-tick marker"):
            # Arrange / Act
            result = Iterate().mark_iterate_tick()
            # Assert
            expect(result).to(equal("iterate-tick"))

    with context("with iterate in its manifest"):
        with it("should expose iterate as an action with no decorator chain"):
            entry = Iterate().tools["iterate"]
            expect(entry.kind).to(equal("instructions"))

    with context("with the iterate action body"):
        with it("should require one scan and one fix pass with no rescan"):
            prose = Iterate.iterate.__doc__ or ""
            expect(prose).to(contain("grill"))
            expect(prose).to(contain("validate"))

        with it("should forbid dumping the whole artifact in one tick"):
            prose = Iterate.iterate.__doc__ or ""
            expect(prose).to(contain("Do not dump the whole product"))
            expect(prose).to(contain("do not sketch"))

        with it("should include the iterate session body in iterate"):
            iterator = Iterate()
            expect("mark_iterate_tick" in iterator.tools).to(equal(True))
            expect("grill_with_context" in GrillContext().tools).to(equal(True))


with description("an iterate action"):
    with context("that expands"):
        with it("should include the iterate session body in iterate"):
            iterator = Iterate()
            expect("mark_iterate_tick" in iterator.tools).to(equal(True))
            expect("grill_with_context" in GrillContext().tools).to(equal(True))


with description("PracticeGuidance operations for iterate"):
    with it("should not expose iterate on practice Guidance"):
        cls = type(
            AgentToolSet.instantiate(
                "builders.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
            )
        )
        practice = cls()
        expect("iterate" in practice.agent_tools).to(equal(False))
