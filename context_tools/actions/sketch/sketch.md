# Sketch

Rough, informal artifacts produced through an interactive grill loop, kept alongside a formal artifact until a higher-fidelity generation supersedes them.

## Purpose of sketching

- **Surface the shape before commitment** — force the design tree into view so unresolved branches are visible to both agent and user.
- **Reason in the open** — every recommendation is sketched with its "why", so the user can push back on the reasoning, not just the result.
- **Shared understanding** — the sketch is the working record of what has been agreed on so far; downstream fidelity levels inherit that agreement instead of re-negotiating it.
- **Cheap to change** — because it is rough and interactive, corrections happen while the cost of moving is low; the formal artifact never has to absorb a wrong shape.

## What sketching is

- A **sketch-and-explain loop with the user** — walk down each branch of the design tree, sketching your recommended shape and explaining the reasoning, one branch at a time. The user reacts; you refine. 
- A **scratch artifact** that survives across fidelity levels until absorbed by a formal one.

## What sketching is not

- Not a replacement for formal generation. A sketch always precedes or accompanies a formal artifact; it does not replace it.
- Not chat-only — always presented interactively **and** persisted via `save_sketch` on the first draft and every refinement.
- **Not a margin-annotation exercise.** Do not tag sketch lines with fidelity markers (`<-i`, `<-m`, `<-s`, or similar). If fidelity matters, declare it once at the top of the sketch. The body is the shape — not a legend of which line belongs to which fidelity.

## Loop

1. **Locate a template** — tiered discovery (see below).
2. **Draft** — rough shape inspired by the template.
3. **Present and persist** — show the sketch in chat with a short explanation, then **immediately** `save_sketch` to `{destination}/.context/{slug}-sketch.md`. A sketch that exists only in chat is a defect; the file is the working record.
4. **Extend the next branch** — pick the next unresolved branch of the design tree, sketch your recommended shape for it into the artifact, and explain why in one or two lines. One branch at a time. Wait for feedback.
5. **Refine and overwrite** — regenerate the sketch showing what changed, then **immediately** `save_sketch` again (same path). Do not batch saves; do not wait until the session ends.
6. **Repeat** 4–5 until either the user says done, or every branch of the design tree has been sketched and reasoned out. Ask a question only when a branch genuinely cannot be resolved by sketching a recommendation.

### Sketch cadence — question budget before first sketch

**Sketch early. A sketch with placeholders beats one more question.**

| Questions asked before first sketch | Status |
|---|---|
| 1–2 | Normal — expected range |
| 3 | Exceptional — only when all three genuinely block the first draft |
| 4+ | **Never** — sketch with `?` placeholders for unresolved branches instead |

If you reach 3 questions without having shown any shape: stop, draft what you know, mark gaps with `?`, then ask. Do not ask a fourth question before the first sketch exists.

## When asking a question (grill inside sketch)

Bare option lists are not allowed. The user must be able to decide from the concepts in play — not from intuition about unlabeled choices.

For every question:

1. **Frame** — name the sketch branch and ground the decision in the active practice concepts (e.g. for clean_engineering modules: high-cohesion, low-coupling, named-seam-and-constraint, deep-module, complexity-absorption; for OOAD: class vs property vs operation, composition/aggregation/association, single responsibility). Pull those concepts from the wrapped agent's material / fidelity docs, not from generic advice. Do not paste or restate prior grill-answer bodies into the AskQuestion text — cite `grill-answers.md` by path or heading if needed; the sketch file already holds what was agreed.
2. **Options with rationale** — 3–5 choices; recommended first; each option gets one short concept-tied rationale (what it does to the seam, ownership, or coupling). End with "Other / I'll specify."
3. **One question** — wait for the answer, then regenerate the sketch showing exactly what changed.

**Always use the AskQuestion tool** — never list options as plain chat text. One tool call = one question:

```
AskQuestion:
  title: "Grill — {theme name}"
  question: "{single focused question with framing}"
  options:
    - {option a — rationale}        # recommended first
    - {option b — rationale}
    - {option c — rationale}
    - Other / I'll specify
```

Question shape (frame + options) comes from `grill_with_context`, which `@sketch` pulls in explicitly. This section owns sketch show/persist cadence only.

## Template discovery (tiered)

1. **Session context** — templates or examples the caller passed in at invocation time. Owned by the current session. Highest priority: a user pasting an example in chat immediately shapes the sketch.
2. **Convention (wrapped agent's own template)** — `{agent_dir}/templates/*-sketch.*` inside the wrapped agent's `templates/` folder (e.g. `bdd/templates/bdd-sketch.md`). Owned by whoever wrote that agent; lets each agent shape its own sketches without touching the sketch toolset.
3. **Default (built-in fallback)** — `sketch/templates/sketch-template.md` shipped inside the sketch toolset itself. Owned by this toolset; used only when nobody upstream supplied a template.

If none of the above yield a template, the sketcher invents a shape for the domain at hand — explicitly a fallback, not a design target.

## Persistence lifecycle

- **Session-rooted paths:** when chained from a Context generator, read the host **`active`** resource.
  - Engagement docs/diagrams → `destination = session` → `{session}/.context/{slug}-sketch.md`
  - Module sketch → `destination = {session}/{module}` → `{session}/{module}/.context/{slug}-sketch.md`
  - Generated code for that module → `{session}/{module}/` (not under `.context/`)
- Sketches live at `{destination}/.context/{slug}-sketch.md`.
- `.context/` is created inside the destination if it does not already exist.
- **Hard rule:** call `save_sketch` as soon as the first interim draft exists; overwrite on every regeneration. Never defer persistence to the end of the grill.
- They persist until a formal artifact absorbs their content.
- Retirement is manual for now — remove the sketch when the formal artifact fully captures its intent.

## Multi-lens sketching (CDD and similar orchestrators)

When sketching across multiple lenses (Stories / DDD / UX / Modules / BDD):

### Rules

- **`confirm-lenses-before-sketch`** — **Hard gate.** Before any scaffold or sketch, use AskQuestion (allow_multiple: true) to confirm which lenses are active. Present them by sketch label. Do not proceed until confirmed. All active lenses are recommended by default; user removes out-of-scope ones.
- **`scaffold-before-content`** — **Hard gate.** Read the engagement sketch template (`templates/cdd-sketch.md` for CDD) and each active child's `sketch_template` **before** writing the sketch file. Do not invent a free-prose `sketch.md`.
- **`grill-before-theme-detail`** — **Hard gate.** Before writing any non-scaffold content for a theme, run at least one grill round on that theme's open questions. The session-level lens confirmation does NOT substitute for this per-theme grill.
- **`one-sketch-per-engagement`** — One sketch file per engagement. Deepening fidelity updates `fidelity:` at the top and deepens blocks in place. Never create a new file for a new fidelity level.
- **`scaffold-before-detail`** — A scaffold pass is required when the ask is greenfield, spans multiple themes/epics/modules, or no whole-design scaffold exists. Not required for a single narrow theme in an already-scaffolded design. Mark every scaffold line `< scaffold`. Never scaffold and detail in the same pass.
- **`scaffold-per-epic-not-mega-block`** — One `=========` theme block per epic (or sub-epic for large systems). Do not group all epics into a single mega-theme block.
- **`detail-updates-scaffold-in-place`** — When detailing a theme, update scaffold lines within the existing `=========` block. Remove `< scaffold` from filled lines. Never create a second parallel block for the same epic — one epic = one theme block for its lifetime.
- **`lens-from-child-template`** — Every lens block body must use that lens's own sketch notation (from child `sketch_template`). No free prose inside `stories:` / `ddd:` / `ux:` / `ce:` / `bdd:`. Use `* approx …` or omit the block if the content is not yet known.

### Scaffold level by lens

| Lens | Scaffold contains | NOT scaffold |
|---|---|---|
| **Stories** | Epics, Sub-Epics, minimal story spine | Scenarios, Given/When/Then |
| **DDD** | Bounded context names, top-level aggregate roots | Building blocks, value objects, domain events |
| **UX** | Site map / navigation only | Screen boxes, controls, layouts |
| **Modules** | Module folder names only | Classes, operations, properties |
| **BDD** | Top-level `describe` lines only | `it …` / `with …` behaviours |

### Common mistakes (multi-lens)

❌ Skipping the lens confirmation gate before scaffold or sketch
❌ Writing the sketch file before reading the sketch template and child `sketch_template`s
❌ Skipping the per-theme grill — lens confirmation does not substitute for it
❌ Creating a new sketch file when moving to a deeper fidelity — deepen in place
❌ Creating a new theme block when detailing — update scaffold lines in the existing block
❌ Grouping all epics into one mega-theme block — one block per epic
❌ Scaffolding and detailing in the same pass
❌ Scaffolding one lens only when other active lenses also need a whole-system map
❌ Leaving scaffold lines without the `< scaffold` marker
❌ Writing free prose inside lens blocks — child notation only
❌ Working multiple themes at once — finish one, then move to the next

---
## Composition — how sketch chains with other actions

`@sketch` **explicitly calls** `grill_with_context`, then chains `sketch_session`. Expansion order:

```
grill_with_context  ← pure Q-loop (no sketch advice)
sketch_session      ← template + save_sketch cadence
base action body    ← e.g. Context.sketch → self.generate()
```

Base `Context` exposes peer entry points: `generate` (plain), `grill`, `sketch`, `iterate`. Domains inherit them; do not re-decorate domain `generate` with `@sketch` / `@grill_with_context`.
