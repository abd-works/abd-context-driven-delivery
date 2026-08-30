# Session: sketch-and-grill-should-create-a-turn-after-every-tick-29

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-29
- **goal:** Sketch and grill should create a turn after every tick
- **fidelities:** development
- **contexts:** sketch, grill_context, workspace Turn

## Progress

- Added `LifecycleAction.complete_tick` — finishes the open Turn (commit when dirty) and opens the next hanging turn with the same action.
- Sketch: every `save_sketch` tick followed by `complete_tick` (prose + recipe + sketch.md).
- Grill: every `write_grill_answer` tick followed by `complete_tick` (prose + recipe).
- Vanilla BDD specs cover tool wiring, instructions, and mechanical finish/reopen + commit.
- Agent BDD: sketch/grill expand must require complete_tick after each persist (instructions + ai_judge).
