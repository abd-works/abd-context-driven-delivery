# Handoff — harness-experimantation (2026-09-03)

## Resume

- **Stage:** Experiment 1 implemented — composite ct-fidelity commands as an opt-in `extended` deploy mode
- **Last work:** baseline deploy unchanged by default; `write_deploy(extended=True)` writes the composite commands
- **Next action:** try `write_deploy(extended=True)` on the real deploy (or `/deploy-harness` with the parameter) and measure whether the composite commands reduce CLI hops vs the catalog skills
- **Next focus:** keep `primitives/harness/*` as the bdd root; the slim `{ct}.{fidelity}` prompt recipe stays the default — do not remove it

## What Experiment 1 is

An **enhancement**, not a replacement. The default deploy is the original harness:

- `{context_tool}.{fidelity}` fidelity prompts (dot notation), slim ActionBody, original confirm lines
- all baseline spec examples green again

`write_deploy(extended=True)` switches one deploy to the composite mode:

- one command per context tool fidelity, named `{context_tool}-{fidelity}`
- each command contains the run-time guidance: the harness iterates the context
  tool's `action: guidance` at each fidelity exactly like the run-time fence
  (load the class from its file, construct with `context.fidelity`, expand via
  `_ActionExpander`) and bakes the returned `response.instructions` into the body;
  on failure it falls back to the guidance docstring, then the overview
- the fence pins `context.fidelity` and `action: generate`; never a fidelity AskQuestion
- confirm lines swap to consider **straight prompt passed vs ct** (action bodies choose
  the context tool; guidance/composite bodies choose the action)
- `.deploy-state.json` records `extended` so `generateAgain` reproduces the mode

Also fixed while restoring the baseline (spec examples that pinned intended behavior):
the `generate` recipe now tells the agent to set `context.type` before running;
`source={context_tool_slug}` now also deploys that tool's fidelity prompts; and a
utility with an `@agent_instructions` op and no write vehicles deploys a prompt
named from its module stem with required ctor params in the context block.

## Files

- `primitives/harness/returned_guidance.py` — new: run-time guidance expansion at one fidelity
- `primitives/harness/bodies.py` — `ContextToolFidelityBody : ContextToolBody` (extended), `ct_fidelity` resolve kind, `extended` flag on resolve/Action/ContextTool bodies; slim fidelity body and default wording restored
- `primitives/harness/prompt.py` — fidelity branch: slim body by default, composite when `extended`
- `primitives/harness/skill.py`, `instruction.py` — thread `extended` into body builders
- `primitives/harness/harness.py` — `write_deploy(extended=False)` parameter, mode-dependent fidelity naming/payload, `_wanted` mode split, utility default branch, generate `Set context.type` line, `extended` in deploy state
- `primitives/harness/harness_spec.py` — baseline assertions restored; extended-mode examples added
- `primitives/harness/.context/harness-sketch.md`, `harness-behavior-sketch.md` — both modes documented

## Verify

- `.\.venv\Scripts\python.exe -m mamba.cli primitives/harness/harness_spec.py --no-color`
  → 73 examples, 0 failures (also `primitives/harness/harness_invoke_fixtures_spec.py` +
  `context_tools/agent_bdd/spec_helpers_spec.py` → 20 examples, 0 failures)
- Run via `python -m mamba.cli`; the `mamba.exe` shim points at a stale venv in the
  OneDrive checkout and resolves `primitives` against the wrong repo

## Artifacts to read

- `C:\dev\abd-cdd-harness-experimantation\.context\context-index.md`
- `primitives/harness/.context/harness-sketch.md`
- `primitives/harness/.context/deployable-plugins-research.md` (compiled-guidance background)
