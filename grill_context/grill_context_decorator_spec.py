"""BDD spec for @grill_with_context decorator + manifest chain exposure."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
sys.modules.pop("grill_context", None)

from expects import be_true, contain, equal, expect, raise_error
from mamba import context, description, it

from action.action import ActionExpander, action, action_wrapper_names
from grill_context import grill_with_context
from grill_context.examples.demo import DemoGrill, DemoStack


with description("@grill_with_context decorator"):
    with context("applied to an @action method"):
        with it("marks the function with _grill_wrapped"):
            expect(getattr(DemoGrill.generate, "_grill_wrapped", False)).to(be_true)

        with it("registers the wrapper name in _action_wrappers"):
            names = action_wrapper_names(DemoGrill.generate)
            expect(list(names)).to(equal(["grill_with_context"]))

    with context("applied to a non-@action function"):
        with it("raises TypeError with a helpful message"):
            def _bare(): pass
            expect(lambda: grill_with_context(_bare)).to(
                raise_error(TypeError, contain("must decorate an @action method"))
            )


with description("ActionExpander integration for @grill_with_context"):
    with it("prepends grill_with_context's real instructions before the base action"):
        demo = DemoGrill()
        body = ActionExpander.instance().parse_body(DemoGrill.generate, demo)
        joined = "\n".join(body.prose_parts)
        expect(joined).to(contain("grilling"))
        grill_pos = joined.find("grilling")
        base_pos = joined.find("Demo grill base body")
        expect(grill_pos < base_pos).to(be_true)

    with it("preserves the original action docstring after the chained action instructions"):
        demo = DemoGrill()
        body = ActionExpander.instance().parse_body(DemoGrill.generate, demo)
        joined = "\n".join(body.prose_parts)
        expect(joined).to(contain("Demo grill base body"))


with description("stacked decorators"):
    with context("when two wrappers are declared in top-down order"):
        with it("lists wrapper names in declaration order (outermost first)"):
            names = action_wrapper_names(DemoStack.generate)
            expect(list(names)).to(equal(["stub_outer", "grill_with_context"]))

        with it("expands the outermost wrapper's instructions before the inner wrapper's"):
            demo = DemoStack()
            body = ActionExpander.instance().parse_body(DemoStack.generate, demo)
            joined = "\n".join(body.prose_parts)
            outer_pos = joined.find("Stub outer wrapper")
            grill_pos = joined.find("grilling")
            expect(outer_pos < grill_pos).to(be_true)


with description("manifest chain field"):
    with it("exposes wrapper names on a decorated action"):
        entry = DemoStack.manifest.signature["generate"]
        expect(entry["kind"]).to(equal("action"))
        expect(entry.get("chain")).to(equal(["stub_outer", "grill_with_context"]))

    with it("omits the chain field when no wrappers are declared"):
        entry = DemoGrill.manifest.signature["ping"]
        expect(entry["kind"]).to(equal("action"))
        expect(entry.get("chain")).to(equal(None))
