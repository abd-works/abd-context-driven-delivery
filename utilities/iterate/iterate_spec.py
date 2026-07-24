"""BDD spec for iterate — @iterate decorator + Iterator toolset + ActionExpander integration."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("iterate", None)

from expects import be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from primitives.actions.action import _ActionExpander, _action_wrapper_names, action
from iterate import Iterator, iterate
from iterate.examples.demo import Demo


with description("@iterate decorator"):
    with context("applied to an @action method"):
        with it("marks the function with _iterate_wrapped"):
            expect(getattr(Demo.generate, "_iterate_wrapped", False)).to(be_true)

        with it("registers iterate in the wrapper chain (grill lives on iterate_session)"):
            names = _action_wrapper_names(Demo.generate)
            expect(list(names)).to(equal(["iterate"]))

    with context("applied to a non-@action function"):
        with it("raises TypeError with a helpful message"):
            def _bare(): pass
            expect(lambda: iterate(_bare)).to(
                raise_error(TypeError, contain("must decorate an @action method"))
            )


with description("_ActionExpander integration"):
    with context("when expanding an @iterate-wrapped @action"):
        with it("expands iterate_session (with in-method grill) before the base action"):
            demo = Demo()
            body = _ActionExpander.instance().parse_body(Demo.generate, demo)
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("(Recommended)"))
            expect(joined).to(contain("validate"))
            iterate_pos = joined.find("validate")
            base_pos = joined.find("Base generate action body")
            expect(iterate_pos < base_pos).to(be_true)

        with it("preserves original tool steps on the base action"):
            demo = Demo()
            body = _ActionExpander.instance().parse_body(Demo.generate, demo)
            expect("do_thing" in body.tool_steps).to(be_true)


with description("Iterator toolset"):
    with context("manifest signature"):
        with it("exposes iterate_session as an action with no decorator chain"):
            entry = Iterator.manifest.signature["iterate_session"]
            expect(entry["kind"]).to(equal("action"))
            expect(entry.get("chain")).to(equal(None))

    with context("iterate_session action body"):
        with it("requires one scan and one fix pass with no rescan"):
            iterator = Iterator()
            body = _ActionExpander.instance().parse_body(
                Iterator.iterate_session, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("one fix"))
            expect(joined).to(contain("Do NOT re-scan"))

        with it("forbids dumping the whole artifact in one tick"):
            iterator = Iterator()
            body = _ActionExpander.instance().parse_body(
                Iterator.iterate_session, iterator
            )
            joined = "\n".join(body.prose_parts)
            expect(joined).to(contain("DEFECT"))
            expect(joined).to(contain("ONLY that unlocked slice"))
            expect(joined).to(contain("Do not chain ticks"))
            expect(joined).to(contain("Hard gate"))
            expect(joined).to(contain("Ask ONE question at a time"))
