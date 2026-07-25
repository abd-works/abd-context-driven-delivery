# Handoff - Stories discovery iterate - thin-slice

## 1. Next session focus

**Thin-slice.** Discovery story-map is done; chunk repairs finished. Next: Stories iterate thin-slice from sandbox/modules/.context/module-build-order.md (checks then character spine first). Do not re-open whole-map inventory unless to-fix forces a local map fix.

## 2. Resume in three lines

(a) Stage: **iterate** Stories - fidelity **discovery** - format **markdown** - path=sandbox - bout discovery.
(b) Last accepted: full map named; extras/flaws **59/59**, Senses options **27/27**, HQ features **28/28** completeness PASS; modifiers re-proved (eleven mechanic sub-epics); map declared done; thin-slice unlocked.
(c) Next: /stories iterate - grill **first thin-slice** (build-order #1-2). One unlocked slice per tick; never dump the whole thin-slice tree.

## 3. Generator state

- Toolset: context_tools.stories.stories:Stories (via Context)
- Fidelity / format: discovery / markdown
- Durable map: sandbox/.context/story-map.md (**map done**; thin-slice next)
- Bout: sandbox/.context/sessions/discovery/
- Iterate hard gate (utilities/iterate): each tick writes ONLY the unlocked slice

## 4. Grilling / skills state

- Grill answers: sandbox/.context/sessions/discovery/grill-answers.md (through **Chunk repairs finished**)
- Process locks:
  - Prefer **Use / Activate XXXX** for powers
  - Sources scoped to epic/sub-epic; common parents (Resolve Checks under Build Character; Purchase under Use Skills / Use Advantages; conflict peers under Resolve Conflict)
  - 	o-fix -> fix immediately + write_to_fix / action log_fix on Context (bout 	o-fix.log)
  - After segmenting catalog chunks: call **erify_segment_completeness** (length-only is false PASS); FAIL blocks story inventory
  - branch-on-mechanical-uniqueness (not one-story-per-effect-title)
- Suggested skills: /stories (iterate thin-slice), /grill-context, /handoff

## 5. CDD progress

None (no cdd-sketch in this bout).

## 6. Artifacts to read

- sandbox/.context/sessions/discovery/grill-answers.md
- sandbox/.context/sessions/discovery/to-fix.log
- sandbox/.context/story-map.md (Scope: map done; chunk repairs done)
- sandbox/modules/.context/module-build-order.md
- Segment verifies: segment-verify-extras-flaws.md, segment-verify-sensory.md, segment-verify-gear.md
- Module segments for the unlocked thin-slice only (start checks/character)
- utilities/iterate/iterate.py - hard-gate instructions
- Index mid-epic columns in HeroesHandbook-index.md are stubs, not story inventory

## 7. Open questions / risks

- **First thin-slice shape undecided** - grill which stories enter slice 1 (build-order suggests checks + character)
- Four-to-nine / estimate-line scan noise still deferred
- X-Ray Vision has no separate Senses-option header in Deluxe PDF (primer-only) - scenario under Use Senses if needed
- Do not invent Operate Vehicle under Use Vehicles; no separate Impose Concealment; Feint/Demoralize stay under Use Skills
