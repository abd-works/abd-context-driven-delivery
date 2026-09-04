# Handoff — harness (2026-09-03)

## Resume

- **Stage:** Experiment 1 implemented — composite ct-fidelity commands as an opt-in `extended` deploy mode
- **Last work:** `write_deploy(extended=True)` writes `{ct}-{fidelity}` commands baking the run-time `action: guidance` instructions per fidelity (`returned_guidance.py` + `ContextToolFidelityBody`); the default deploy keeps the slim `{ct}.{fidelity}` prompts and original confirm lines
- **Next action:** run an extended deploy on the real repo and measure it, then resume the isolated-plugin experiment (compiled guidance now exists to compile from)
- **Next focus:** plugin package emit; do not treat `com.cursor.ide/` as a documented Cursor loader

## Artifacts to read

- `.context/sessions/harness-experimantation/handoffs/handoff-2026-09-03-experiment-1-composite-ct-fidelity-commands-from-returned-guidance.md`
- `primitives/harness/.context/deployable-plugins-research.md` (current research)
- `primitives/harness/.context/harness-behavior-sketch.md`
- `primitives/harness/.context/harness-sketch.md`
- `.context/context-index.md`
