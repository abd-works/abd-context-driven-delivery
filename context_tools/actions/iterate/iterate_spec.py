"""BDD spec for Iterate toolset + ActionExpander integration."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("iterate", None)

from expects import contain, equal, expect
from mamba import context, description, it

from primitives.actions.action import _ActionExpander
from iterate import Iterate
from tools.tool import _ToolsetLoader


with description("Iterate toolset"):
    with context("that records an iterate tick"):
        with it("should return the iterate-tick marker"):
            # Arrange / Act
            result = Iterate().mark_iterate_tick()
            # Assert
            expect(result).to(equal("iterate-tick"))

    with context("with iterate in its manifest"):
        with it("should expose iterate as an action with no decorator chain"):
            entry = Iterate.manifest.signature["iterate"]
            expect(entry["kind"]).to(equal("action"))
            expect(entry.get("chain")).to(equal(None))

    with context("with the iterate action body"):
        with it("should require one scan and one fix pass with no rescan"):
            iterator = Iterate()
            body = _ActionExpander.instance().parse_body(
                Iterate.iterate, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("one fix"))
            expect(joined).to(contain("Do NOT re-scan"))

        with it("should forbid dumping the whole artifact in one tick"):
            iterator = Iterate()
            body = _ActionExpander.instance().parse_body(
                Iterate.iterate, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("DEFECT"))
            expect(joined).to(contain("ONLY that unlocked slice"))
            expect(joined).to(contain("Do not chain ticks"))
            expect(joined).to(contain("Hard gate"))
            expect(joined).to(contain("Ask ONE question at a time"))

        with it("should include the iterate session body in iterate"):
            iterator = Iterate()
            body = _ActionExpander.instance().parse_body(
                Iterate.iterate, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("grill_with_context"))


with description("an iterate action"):
    with context("that expands"):
        with it("should include the iterate session body in iterate"):
            body = _ActionExpander.instance().parse_body(Iterate.iterate, Iterate())
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("mark_iterate_tick"))
            expect(joined).to(contain("grill_with_context"))


with description("BaseContextTool host face for iterate"):
    with it("should not expose iterate on the host composer"):
        from context_tools.base.base_context_tool import BaseContextTool

        cls = _ToolsetLoader.instance().load(
            "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
        )
        host = cls()
        expect("iterate" in host.actions).to(equal(False))
