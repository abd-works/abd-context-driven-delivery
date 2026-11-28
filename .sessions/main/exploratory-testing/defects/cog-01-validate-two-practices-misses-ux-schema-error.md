# cog-01 Validating UX IA beside DDD bounded context passes a ux.json that fails conforms-to-schema alone

**Title** - `validate.validate` naming `ux-ia ddd-bounded-context` reports "No graph rule violations" for both, and the board marks ux-ia done, while the same `ux/ux.json` validated with `ux-ia` alone has a checked `conforms-to-schema` ERROR.

**Charter** - theme 7, a practice switched off while work on it is under way. **Tester** - Cog.

**Story** - Deliver Work With Context Guidance / Produce Formal Artifacts / validate artifacts. No scenario covers validating two practices' fidelities in one call.

**Module and class** - `cdd_guidance/actions/validate/validate.py` *Validate* (graph report per guidance), with `harness/guidance_actions/guidance_actions.py` *GuidanceAction* listing the guidance.

**Severity** - wrong result (a broken checked rule is hidden, and the board shows the fidelity done with 0 violations).

## Steps

Sandbox: `C:\dev\_et\after-1-2-1\cog\work\repo` (Bookshop story fixture, plus `ux/ux.json` copied from `cdd_guidance/practices/ux/model/_examples/trip/ordering-ux-map.json` and a small `.context/bounded-context-map.md`). cdd server: `python -m harness.mcp --port 8961` from the build checkout with `CDD_HOME=C:\dev\_et\after-1-2-1\cog\cdd_home`. Calls over MCP HTTP with header `X-CDD-Project: C:\dev\_et\after-1-2-1\cog\work\repo` (script `C:\dev\_et\after-1-2-1\cog\scripts\cdd.py`).

1. `ticket.create {"title":"Checkout flow"}`; Stories, DDD and UX on.
2. `validate.validate {"guidance":"ux-ia session=.sessions/checkout-flow/session.json","paths":["ux/ux.json"]}`
3. `validate.validate {"guidance":"ux-ia ddd-bounded-context session=.sessions/checkout-flow/session.json","paths":["ux/ux.json",".context/bounded-context-map.md"]}`
4. `board.show`, look at checkout-flow's ux-ia progress.

## Expected

Step 3's ux-ia report holds the same checked hit as step 2 (validate.md step 3: "A checked rule's hit is a violation"), and each fidelity's report holds its own practice's rules.

## Actual

- Step 2 report `ux-ia-20261128T165528.md`: "Total graph violations: 1", `[X] ERROR [graph rule] ux/ux.json#L67: StoryDemoControl 'Products' has no storySteps relationship to Step, which the ux practice schema requires.` 8 AI rules in scope.
- Step 3 reports `ux-ia-20261128T165536.md` and `ddd-bounded-context-20261128T165536.md`: both "No graph rule violations. All scanned graph rules passed.", both "AI rules in scope: 30", both list the same 30 headings (the 8 UX rules followed by the 22 DDD bounded-context rules), and both name the same graph source `checked-graphs/ux-ia-20261128T165536/graph.json` (the DDD report points at the ux-ia graph).
- Step 4: `ux-ia state=done actions={'generate': 'done', 'validate': 'done'} viol=0`.
- Seen twice (16:54:09 and 16:55:36), with UX on both times; switching UX off and on is not the cause.

## Tier that should catch it

Heavy (real graph build through the validate action with two practices). The unit specs of Validate run one guidance at a time, so nothing checks that a list of guidance keeps each practice's own graph rules and hits.
