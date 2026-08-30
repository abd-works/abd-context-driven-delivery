# Session: smarter-caching-and-reuse-of-guidance-already-in-context-so-agents-stay-in-the-fidelity-tool-format-without-re-calling-manifest-17

## Start

- **date:** 2026-08-30
- **path:** C:\dev\abd-cdd-17
- **goal:** Smarter caching and reuse of guidance already in context so agents stay in the fidelity-tool format without re-calling manifest
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

### Intended change (from ticket)

Reuse guidance that is **already in the agent context** so agents stay in the fidelity-tool / manifest format zone without re-calling `python -m tools manifest …` (or equivalent) over and over for the same information.

Related: [#8](https://github.com/abd-works/abd-context-driven-delivery/issues/8), [#16](https://github.com/abd-works/abd-context-driven-delivery/issues/16) (Done), [#45](https://github.com/abd-works/abd-context-driven-delivery/issues/45) (Done).

### Current behavior — three seams

#### 1. Manifest gate (governed-asset touch) — primary leftover for #17

**Spec (desired):** `primitives/tools/hooks/.context/manifest-gate-stories-sketch.md` story *Deliver Guidance Once Per Chat, Then Reuse It*:

- First touch: run each `@toolset-manifest` command and deliver full guidance into context.
- Edit proceeds on the same touch (no deny-until-cleared).
- **Repeat touch:** gate checks whether that guidance already appears in context; does **not** require remanifest; nothing re-run; nothing re-injected; agent keeps using what it has.

**Code (actual):** `utilities/manifest_hook/manifest_gate.py`

- Module docstring: deliver guidance **on every touch**.
- `_deliver_guidance` always calls `run_manifests(lines)` then builds `agent_message` / `user_message`.
- `handle_before_read_file` / `handle_pre_tool_use` / `handle_post_tool_use` all go through that path with **no** “already in context?” check and **no** per-chat delivered cache.

**Tests today:**

- Mechanical: `primitives/tools/hooks/manifest_gate_spec.py` — asserts delivery + allow; **no** repeat-touch / no-remanifest example.
- Agentic: `edit_a_governed_asset_test_helper.agent.py` scenario 3 (“repeat touch”) only asserts both edits succeed (`RESULT: EDIT SUCCEEDED`); it does **not** assert that the second touch skipped `run_manifests` or skipped re-injection.

So the sketch already names the #17 behavior; the gate implementation and coverage never closed the reuse half.

#### 2. Tools CLI / harness slash-skill path — largely settled by #16 + #45

- Skills/bodies say: skill **is** the catalog; pipe the YAML fence to `.\tools.ps1 run -`; **Do not remanifest**; follow `response.instructions` only (`primitives/harness/bodies.py`, toolset header comments).
- #16 single-command + walker: one stdin `run -` per generate; agents stopped inventing a domain `action: guidance` hop.
- #45 Done: agents run tool/fidelity/action/utility from the deployed slash/skill alone (manifest-alone invoke).

On the courier generate pair, #16 explicitly recorded: *“Issue 17 as ‘cache so hop 2 can skip remanifest’ does not apply: there is no hop 2 on this pair.”* Thin-first-expand (fidelity/format-filtered load) was the #17 restatement for **payload size**, and that landed under #16.

#### 3. Session-level “4a cache for later hops” — parked under #16

`options.md` / `backlog.md` for session 16: id **4a** *Session cache for later hops* deferred because the measured generate pair has no hop 2. That is a different clock than governed-asset remanifest-on-every-touch.

### Context read

| Artifact | Relevance |
|---|---|
| `.context/context-index.md` | Workspace roots (bdd / clean_engineering / stories) — no #17-specific map |
| Issue #17 body | Backlog request: smarter caching/reuse if guidance already in context; stay in fidelity-tool format; stop re-calling manifest |
| `primitives/tools/hooks/.context/manifest-gate-stories-sketch.md` | Canonical desired reuse semantics |
| `primitives/tools/hooks/.context/sessions/manifest-gate/session.md` | Gate rewrite delivered-on-touch + allow; reuse half left as sketch intent |
| `utilities/manifest_hook/manifest_gate.py` | Live hook: remanifest every touch |
| `primitives/tools/.context/module-context.md` | Tools seam: AI follows manifest/`run`, not authoring from `.py` |
| Session 16 `options.md` / `backlog.md` / `experiments.md` | #17 vs thin-expand vs 4a; remanifest hop already gone on generate |
| Session 45 | Manifest-alone invoke without remanifest for slash/skills |

### History (area of the change)

- Manifest-gate session (2026-08-04/05): deny-until-cleared → deliver-and-allow; first/repeat/recursive agent specs; sketch still requires reuse-without-re-run.
- #16 finish (`4d6c41cd` line): single-command, thin-first-expand, channel-write miss; #17 hop-2-cache reframed away for generate.
- `e8d6bda3` / `2611586e`: thin-first-expand filters (fidelity/format load).
- `d50e0fa9` (#45): tools.ps1 manifest-alone invoke + agent BDD harness.
- Ongoing header rule: “Agent reading this file: do not remanifest — slash/skill is the catalog.”

### Similar / related past changes

| Item | Relation to #17 |
|---|---|
| #16 optimize CLI handoffs | Settled remanifest/file hops for generate; thin-expand = size; **not** gate reuse |
| #8 fewer files / tool calls | Parent theme; overlapping invoke taxes |
| #45 manifest-alone invoke | Agents must not remanifest to rediscover how to run tools — complementary prompt/harness seam |
| Manifest-gate “once per chat then reuse” | Same requirement as #17 on the **hook** seam; implementation incomplete |

### Map: current → intended delta

| Surface | Current | Intended delta for this ticket |
|---|---|---|
| Manifest gate on repeat touch | Always `run_manifests` + re-inject full guidance | Detect guidance already in context (or remember delivered-this-chat); skip remanifest and skip re-injection; agent stays on existing fidelity-tool guidance |
| Gate mechanical / agentic tests | Delivery + allow; repeat only checks edit success | Assert second touch does not remanifest / does not re-inject |
| Slash/skill / `tools.ps1 run -` | Already “do not remanifest”; skill is catalog (#16/#45) | Out of primary delta unless a thin prompt nudge is needed to “reuse guidance already delivered” |
| Generate expand payload | Thin-first-expand already landed under #16 | Do **not** re-open as the #17 change surface |
| Session hop cache (4a) | Parked | Only if later multi-hop kits need it; not the backlog’s “already in context” wording |

### Change-surface shortlist (for later approach job)

1. **`utilities/manifest_hook/manifest_gate.py`** — `_deliver_guidance` / handlers: reuse / skip path.
2. **Optional small store** — per-chat “delivered for this toolset/header” (hook-visible state), if “appears in context” cannot be read from the IDE payload.
3. **`manifest_gate_spec.py` + repeat-touch agent helper** — make reuse observable (no second `run_manifests`, no second full inject).
4. **Sketch already exists** — alter in place only if wording must match the chosen detection mechanism; do not remodel the whole gate.
5. **Possibly thin agent/skill line** — reinforce “if MANIFEST GATE / fidelity guidance is already in context, use it; do not remanifest” (prompt complement, not a substitute for the hook skip).

### What this analysis is not

Not a defect hunt beyond mapping the intended small change. Not a proposal to redo #16 thin-expand or #45 manifest-alone. Those stay settled; #17’s remaining delta is **smarter reuse when guidance is already present**, centered on the gate’s repeat-touch path (and any thin instruction that keeps agents in that format zone).
