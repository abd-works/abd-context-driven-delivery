# Session: smarter-caching-and-reuse-of-guidance-already-in-context-so-agents-stay-in-the-fidelity-tool-format-without-re-calling-manifest-17

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-17
- **goal:** Smarter caching and reuse of guidance already in context so agents stay in the fidelity-tool format without re-calling manifest
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Ticket intent
#17 asks that when governing-toolset guidance is **already in the agent chat**, later touches of the same governed asset stay in the fidelity-tool format **without re-calling `python -m tools manifest`** and without re-injecting the full manifest blob.

### Current behavior
`utilities/manifest_hook/manifest_gate.py` `_deliver_guidance` always calls `run_manifests(lines)` on every beforeReadFile / preToolUse / postToolUse for a stamped asset. Hook payloads already carry `conversation_id` (see `manifest_gate.debug`). There is no per-chat delivered cache.

### Sketch / related surface
- `primitives/tools/hooks/.context/manifest-gate-stories-sketch.md` — sub-epic **Deliver Guidance Once Per Chat, Then Reuse It**, scenario *touching the same asset again this chat just refers back to guidance already delivered* (nothing re-run, nothing re-injected).
- Story + agent helper: `…/deliver-guidance-once-per-chat/edit-a-governed-asset/`.
- Related: #16 (fewer CLI handoffs; options.md notes #17 as cache-so-hop-2-skips-remanifest), #8, #45 (manifest-alone invoke / do not remanifest).

### Intended delta
1. First touch in a chat: run manifests, deliver full guidance (unchanged).
2. Later touch of the same path in the same `conversation_id`: do **not** remanifest; do **not** re-inject the full blob; allow edit and optionally a short refer-back that guidance is already in context.
3. Missing `conversation_id`: keep current deliver-every-time behavior (safe default).

### Change surface
- Production: `utilities/manifest_hook/manifest_gate.py` (+ thin entry shim if hooks still point at `primitives/tools/hooks/manifest_gate.py`).
- Mechanical: `primitives/tools/hooks/manifest_gate_spec.py`.
- Agentic: strengthen repeat-touch helper assertions under deliver-guidance-once-per-chat.

## Approach

### Category
**CODE CHANGE** — production hook behavior in `manifest_gate`. Agent helpers/specs assert the new observable; no new prompt-only product path.

### Chosen approach
Per-chat delivered cache keyed by `(conversation_id, resolved path)` stored beside the gate (JSON, same family as the retired clearance store). On cache hit: skip `run_manifests`, return allow + short refer-back (or empty injection). On miss: existing `_deliver_guidance`, then mark delivered.

Why: smallest seam, matches the sketch wording, reuses existing hook payload field, safer rollback (delete store / feature flag by conversation_id empty).

### Rejected alternatives
1. **Prompt/AI only** ("agent, do not remanifest") — agents already get "Do not remanifest" from bodies; the gate still re-runs and re-injects. Does not close the ticket.
2. **In-process memory only** — hook runs are separate processes; memory does not span touches.
3. **Cache full manifest text and re-inject from disk** — still re-injects; sketch wants reuse of what is already in context, not a second dump.

## Model

### Altered
- `utilities/manifest_hook/manifest_gate.py` — deliver-once-per-chat cache + refer-back path.
- `primitives/tools/hooks/manifest_gate_spec.py` — mechanical examples for remanifest skip on repeat touch.
- `…/edit_a_governed_asset_test_helper.agent.py` — repeat-touch asserts no remanifest / refer-back.
- Entry shim `primitives/tools/hooks/manifest_gate.py` if missing (hooks.json / bat still point here).

### Left alone
- Deny-until-cleared (already retired).
- Retry / loud-failure / normal-verbose narration stories.
- Thin-first-expand / #16 courier experiments.
- Generate/Validate action kits (invocation composition), except as needed to run this change.
