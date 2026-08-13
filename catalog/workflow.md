# CDD Workflow

Browse the [catalog](index.html) for the full map of tools, actions, fidelities, and utilities.

## What the pieces are

**Context tools** are lenses on the work. Each one owns a perspective.

- [/stories](context-tools/stories.html) — who does what, in what sequence.
- [/clean-engineering](context-tools/clean_engineering.html) — module boundaries and OO design.
- [/ux](context-tools/ux.html) — navigation, screens, front end.
- [/bdd](context-tools/bdd.html) — observable behavior and tests.
- [/ddd](context-tools/ddd.html) — bounded contexts and domain building blocks.
- [/cdd](context-tools/cdd.html) — orchestrates all child tools at one stage.

**Actions** are what you do with a context tool. Every tool shares the same lifecycle verbs.

- [/partition](actions/partition.html) — index source material and extract chunks.
- [/document](actions/document.html) — describe existing code, tests, or docs.
- [/generate](actions/generate.html) — produce the full formal artifact in one shot.
- [/grill](actions/grill.html) — context-grounded Q&A.
- [/sketch](actions/sketch.html) — grill plus create a rough draft.
- [/iterate](actions/iterate.html) — generate one small slice at a time.
- [/validate](actions/validate.html) — scan and report pass/fail.
- [/satisfy](actions/satisfy.html) — validate, fix, validate again until clean.
- [/repair](actions/repair.html) — root-cause and fix why the tool produced a violation.
- [/improve](actions/improve.html) — log mistake, repair, capture regression.

**Fidelities** control how deep you go. Each context tool maps three stages to its own concrete names.

- [/discovery](fidelities/cdd-discovery.html) — wide and shallow (Stories: `story_map`, CE: `modules`, UX: `ia`, DDD: `bounded_context`).
- [/specification](fidelities/cdd-spec.html) — narrower and deeper (Stories: `scenarios`, CE: `model`, UX: `mockup`, BDD: `behavior`, DDD: `building_blocks`).
- [/engineering](fidelities/cdd-engineer.html) — narrowest and deep (Stories: `acceptance_tests`, CE: `code`, UX: `front_end_code`, BDD: `development`, DDD: `tactics`).

**Utilities** are session helpers, not lenses.

- [/handoff](utilities/handoff.html) — compact the session for a fresh agent.
- [/diagnose](utilities/diagnose.html) — stuck RED / bug-fix loop.

## How to use them

Compose a command as **`/{context tool} /{action} /{fidelity}`**.

Example: [/stories /sketch /discovery](actions/sketch.html) — sketch the Stories tool at discovery (resolves to `story_map`).

You can also pass the tool's concrete fidelity directly: [/stories /sketch story_map](actions/sketch.html).

---

## Scenario 1 — Turn source documentation into context

Use when you have a handbook, spec, wiki, or any prose you want the system to reason from.

- **[Partition](actions/partition.html) the docs through your first lens.**
  Pick the lens that matters most right now and run [partition](actions/partition.html) to index the source and extract verbatim chunks.
  [/clean-engineering /partition modules](actions/partition.html) — indexes by module boundaries.
  [/stories /partition story_map](actions/partition.html) — indexes by epics and user interactions.
  [/ux /partition ia](actions/partition.html) — indexes by screens and navigation.

- **Add more lenses to the same index.**
  Each subsequent [partition](actions/partition.html) adds its own columns and chunks to the existing index. Nothing is wiped.
  Run [partition](actions/partition.html) again with a different tool for each perspective you need.

- **[Sketch](actions/sketch.html) the design from those chunks.**
  Once partitioned, draft a rough shape interactively before committing to formal output.
  [/clean-engineering /sketch modules](actions/sketch.html)
  [/stories /sketch story_map](actions/sketch.html)
  [/ux /sketch ia](actions/sketch.html)

- **[Generate](actions/generate.html) the formal artifact.**
  Produce the real deliverable at the chosen fidelity.
  [/clean-engineering /generate modules](actions/generate.html)

- **Close the gaps with [satisfy](actions/satisfy.html).**
  [Validate](actions/validate.html) the artifact, fix every reported violation, and validate again until it passes.
  [/clean-engineering /satisfy modules](actions/satisfy.html)

- **Deepen fidelity and repeat the loop.**
  When [discovery](fidelities/cdd-discovery.html) is solid, move to the next stage and [sketch](actions/sketch.html) → [generate](actions/generate.html) → [satisfy](actions/satisfy.html) again — same steps, tighter scope.
  [/stories /sketch scenarios](actions/sketch.html) → [/stories /generate scenarios](actions/generate.html)
  [/clean-engineering /sketch model](actions/sketch.html) → [/clean-engineering /generate model](actions/generate.html)
  Or set the stage with [/specification](fidelities/cdd-spec.html) or [/engineering](fidelities/cdd-engineer.html) on the tool already in scope.

---

## Scenario 2 — Document an existing codebase or test suite

Use when the system already exists and you want to add structured context files without inventing a new design.

- **Observe and describe what is there with [document](actions/document.html).**
  Document reads the code and produces a neutral description. Scanner violations are flagged but not fixed.
  [/clean-engineering /document code](actions/document.html)
  [/bdd /document development](actions/document.html)

- **Add context files based on what you observed.**
  Create or update `.context/module-context.md` files using the document output as your source of truth.

- **[Generate](actions/generate.html) or [satisfy](actions/satisfy.html) against those context files.**
  Now that context exists, generate formal artifacts or run satisfy to close gaps.
  [/clean-engineering /generate modules](actions/generate.html)
  [/bdd /satisfy development](actions/satisfy.html)

---

## Scenario 3 — Design something new (greenfield)

Use when nothing exists yet and you need to shape the solution before building it.

- **[Sketch](actions/sketch.html) the shape.**
  [Grill](actions/grill.html) open decisions and create a rough draft. The sketch is saved to disk after each refinement — never left only in chat.
  [/stories /sketch story_map](actions/sketch.html)

- **[Generate](actions/generate.html) the formal artifact.**
  Produce the deliverable from the sketch and context.
  [/stories /generate story_map](actions/generate.html)

- **[Iterate](actions/iterate.html) one slice at a time.**
  For large artifacts, iterate generates one small validated slice per tick instead of dumping everything at once.
  [/stories /iterate scenarios](actions/iterate.html)

- **Run all child tools at one stage with [CDD](context-tools/cdd.html).**
  When you want every lens at the same depth, use the CDD orchestrator.
  [/cdd /sketch discovery](actions/sketch.html) — sketches Stories + Clean Engineering + UX + DDD at discovery.
  [/cdd /generate spec](actions/generate.html) — generates all child tools at spec fidelity.

---

## Scenario 4 — Fix and improve existing artifacts

Use when artifacts already exist but have violations or need refinement.

- **[Validate](actions/validate.html) without editing.**
  Scan and report pass/fail per rule. Nothing is changed.
  [/clean-engineering /validate modules](actions/validate.html)

- **[Satisfy](actions/satisfy.html) all violations.**
  Fix the **artifact** — validate, close every gap, validate again until it passes.
  [/clean-engineering /satisfy modules](actions/satisfy.html)

- **[Repair](actions/repair.html) the root cause.**
  Fix **why the context tool produced the violation** (context, example, template, or scanner) — not the asset in isolation. Requires a scan/validate signal; drafts a surgical change and waits for approval.
  [/clean-engineering /repair modules](actions/repair.html)

- **[Improve](actions/improve.html) when the mistake should stick.**
  Log the mistake, log the correction, then launch repair and capture a regression fixture so the same failure does not recur.
  [/clean-engineering /improve modules](actions/improve.html)

---

## Quick reference — context tools and fidelities

| Tool | Discovery | Spec | Engineer |
|---|---|---|---|
| [/cdd](context-tools/cdd.html) — orchestrate all child tools at one stage | [discovery](fidelities/cdd-discovery.html) | [spec](fidelities/cdd-spec.html) | [engineer](fidelities/cdd-engineer.html) |
| [/stories](context-tools/stories.html) — who does what, in what sequence | [story_map](fidelities/stories-story_map.html) | [scenarios](fidelities/stories-scenarios.html) | [acceptance_tests](fidelities/stories-acceptance_tests.html) |
| [/clean-engineering](context-tools/clean_engineering.html) — module boundaries and OO design | [modules](fidelities/clean_engineering-modules.html) | [model](fidelities/clean_engineering-model.html) | [code](fidelities/clean_engineering-code.html) |
| [/ux](context-tools/ux.html) — navigation, screens, front end | [ia](fidelities/ux-ia.html) | [mockup](fidelities/ux-mockup.html) | [front_end_code](fidelities/ux-front_end_code.html) |
| [/bdd](context-tools/bdd.html) — observable behavior and tests | — | [behavior](fidelities/bdd-behavior.html) | [development](fidelities/bdd-development.html) |
| [/ddd](context-tools/ddd.html) — bounded contexts and domain building blocks | [bounded_context](fidelities/ddd-bounded_context.html) | [building_blocks](fidelities/ddd-building_blocks.html) | [tactics](fidelities/ddd-tactics.html) |

## Quick reference — actions

| Action | What it does |
|---|---|
| [/partition](actions/partition.html) | Index source material and extract verbatim chunks. Re-run with another tool to add a lens. |
| [/document](actions/document.html) | Describe existing code, tests, or docs. Flags violations without correcting them. |
| [/generate](actions/generate.html) | Produce the full formal artifact in one shot. |
| [/grill](actions/grill.html) | Context-grounded Q&A. Writes `grill-answers.md`. Does not produce the artifact. |
| [/sketch](actions/sketch.html) | Grill plus create a rough draft. Shape only — not the formal artifact. |
| [/iterate](actions/iterate.html) | Grill, generate one small slice, validate, fix. Repeat per slice. |
| [/validate](actions/validate.html) | Judge only. Scan and report pass/fail. Do not edit. |
| [/satisfy](actions/satisfy.html) | Validate, fix every gap in the artifact, validate again until it passes. |
| [/repair](actions/repair.html) | Root-cause why the context tool produced the violation; fix the tool (context / example / template / scanner), not the asset alone. |
| [/improve](actions/improve.html) | Log mistake → log correction → launch repair → capture regression so it sticks. |

## Quick reference — session helpers

| Utility | What it does |
|---|---|
| [/handoff](utilities/handoff.html) | Compact the session for a fresh agent. |
| [/diagnose](utilities/diagnose.html) | Stuck RED / bug-fix loop. |
