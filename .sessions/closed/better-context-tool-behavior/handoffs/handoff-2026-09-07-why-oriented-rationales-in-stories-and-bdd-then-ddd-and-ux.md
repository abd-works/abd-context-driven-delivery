# Handoff — better-context-tool-behavior (2026-09-07)

## Resume

- **Stage:** clean_engineering why pass complete; stories/bdd/ddd/ux pending
- **Last work:** `dff2ebad` — why rationales in `clean_engineering.md` goals, guidance, rules; split `limit-operation-parameters` / `avoid-vague-parameter-names`; refined OO guidance from user feedback
- **Next action:** Same why-oriented review on **stories** and **bdd** kits; then a similar pass on **ddd** and **ux**
- **Next focus:** Why-oriented rationales in stories and bdd, then ddd and ux

Stay on branch `session/better-context-tool-behavior`.

---

## What we did (clean_engineering) — the pattern to repeat

Modern reasoning models need the **why behind every rule and guidance point** — framed from a **coding perspective** (what breaks in the code if you skip it), not abstract principles.

### Document layers (do not blur them)

| Layer | Job | Why treatment |
|---|---|---|
| **Goal** | Why this fidelity exists | Meta-why: what you get from doing this stage (e.g. model = reviewable design surface; code = real system + clean code keeps boundaries) |
| **Guidance** | How to think — workflow, examples | Embed consequences like modules Guidance — each paragraph should say what goes wrong in practice |
| **Rules** | Scannable slugs for scanners | Append one consequence clause after the rule text; do not duplicate full Guidance prose |

### Quality bar for a good why

- Name the **concrete failure** — scattered logic, two reasons to change, missing class in the model, stub ships as silent no-op
- Not: "harder to maintain", "best practice", "cognitive load" without tying to code
- User corrections that set the tone:
  - Synonyms → same logic written twice
  - Logic off owning type → concept scattered across types, hard to find/refactor
  - 3+ parameters → missing class that should own the behavior
  - `@property` → stored and computed access indistinguishable; `get_`/`set_` splits behavior from state at the seam
  - Two jobs on one operation/class → two conflicting change vectors, brittle

### What changed in `context_tools/clean_engineering/clean_engineering.md`

- Opener + all three fidelity **Goals** (modules deferral, model as review surface, code as real system + clean code preserves design)
- **Shared rules** vocabulary whys
- **modules** Guidance already had whys; **Module rules** block got consequences
- **model** Guidance got parity with modules Guidance (consequence per paragraph)
- **model** + **code** Rules — selective whys on rules that read as style preferences
- **code** Guidance — whys only where Rules do not already cover the point
- Rule splits: `use-clear-operation-parameters` → `limit-operation-parameters` + `avoid-vague-parameter-names` (scanner still `use-clear-function-parameters` — align separately if needed)

---

## Phase 1 — stories + bdd (do these first)

### Files

- `context_tools/stories/stories.md`
- `context_tools/bdd/bdd.md`

### stories.md — audit

**Already has some structure** from prior session (Guidance rename, merged rules, acceptance_tests cross-ref, telco-website golden example). **Goals largely lack why.**

| Section | Gap |
|---|---|
| Top **Guidance** (hierarchical, action-oriented) | Procedural + examples; thin on consequences (why 7–9 children, why verb–noun, why same pattern at every level) |
| **story_map** Goal | Says what to produce; no why story mapping before scenarios |
| **story_map** Guidance | Decomposition/spine/scope — needs coding/test consequences (untestable tasks, missed actors, spine too fat) |
| **story_map** Rules | Mostly what-only (`four-to-nine-children`, `branch-on-mechanical-uniqueness`, …) — high priority for whys |
| **scenarios** Goal | Thin |
| **scenarios** Guidance | Better than rules but missing consequence clauses on happy-path-only, concrete examples, domain language |
| **scenarios** Rules | Partial whys on `gwt-steps-trace-to-domain-operations`; others (`given-only-what-the-system-checks`, `when-holds-the-operation`, `and-chaining`, …) need coding consequences |
| **acceptance_tests** | Cross-ref to scenarios; fixture rules need whys (inline literals drift, lifecycle hooks vs domain givens) |

**Do not** re-add duplicate rules between scenarios and acceptance_tests.

### bdd.md — audit

**Strong hierarchy / mental model prose**; rules list is long with mixed coverage.

| Section | Gap |
|---|---|
| Opener + **Hierarchy shape** | Good examples; fail cases are implicit |
| **Mental model** (Branch/Nest/Share/Promote) | Teaches pattern; light on why (unreadable trees, duplicate coverage, repeated conditions) |
| **Shared rules** | Mostly prohibition without consequence (`describe-is-subject-not-internal`, `state-not-when`, `full-surface-coverage`, …) |
| **modules / behavior / development** Goals | Thin or missing |
| **behavior** Rules | `hierarchy-preservation`, `signature-markers`, `no-implementation` — procedural |
| **development** Rules | Many RED/GREEN rules; some overlap; add whys where agents override (batch all markers, mock the subject, layer-isolation) |

Rename **Mental model** → **Guidance** if not already done (stories pattern).

### stories + bdd approach

1. Read each **Goal** — add why this fidelity exists (what cheap here, expensive later)
2. Read **Guidance** paragraphs — one consequence clause per paragraph where missing (match `clean_engineering` model Guidance density)
3. Read **Rules** — add coding consequence to rules that are style-only; skip rules that already state the failure (`never-swallow-exceptions` pattern)
4. Split rules doing two jobs (like parameter count + vague names)
5. Fix typos while there (`statementys`, `apporach`, `sucessful`, `hiererachy`, bdd `shgould`, `tighly`, `artifactif`)
6. Run `stories_spec.py` / `bdd` specs if rule slugs change

---

## Phase 2 — ddd + ux (after stories/bdd)

### Files

- `context_tools/ddd/ddd.md`
- `context_tools/ux/ux.md`

### ddd.md — audit

**Rich domain content** — failure modes paragraph in bounded_context is a good model for whys elsewhere.

| Section | Gap |
|---|---|
| **bounded_context** Goal | Has failure modes list — extend Goal with why map before building blocks |
| **bounded_context** Rules | Long; many are what-only (`bc-by-lifecycle-not-ui-themes`, `one-meaning-per-context`, `hang-deps-on-owning-bc`, …) — consequences are in prose above but not on slugs |
| **building_blocks** stereotype table | Definitions only; rules need why (VO vs Entity habit, `*Service` verb bag, repository without lifecycle) |
| **tactics** Goal | Bullet list; thin why on `load-with-identity-in-hand` |

### ux.md — audit

**Very procedural** (mockup steps, shell layout, Story Demo wiring). Less rule-heavy than CE/stories.

| Section | Gap |
|---|---|
| **ia** Goal | One line — why IA before mockup |
| **mockup** Goal + numbered steps | What to do; stand-in/stub consequences only at end (`stub-catalogue-honest`) |
| **front_end_code** Goal | Says not greybox; needs why (same as CE code goal — real system, decisions carry forward) |
| **Shared rules** + fidelity **Rules** | Mostly mirrors without consequences (`tab-states-are-separate-screens`, `screen-story-budget`, `brand-is-opt-in`, `real-backend-wired`) |
| Top **Guidance** | Missing entirely — consider short Guidance block per fidelity (like CE) before rules |

### ddd + ux approach

Same three-layer pass. DDD: lean on existing **failure modes** and **input traps** — translate those into rule-level consequences. UX: prioritize **Goals** and **mockup/front_end_code** Guidance whys (why greybox, why Story Demo is not shipping UI, why stubs must be catalogued).

---

## Artifacts to read

- `context_tools/clean_engineering/clean_engineering.md` — reference implementation for why density
- `context_tools/stories/stories.md`
- `context_tools/stories/examples/telco-website/` — golden fixture example (do not break)
- `context_tools/bdd/bdd.md`
- `context_tools/ddd/ddd.md`
- `context_tools/ux/ux.md`
- Recent commits: `dff2ebad`, `21a9b186`, `ef871f3a`

---

## Corrections (do not repeat)

- Do not append "because best practice" — name the code that breaks
- Guidance ≠ Rules — do not duplicate every rule why into Guidance; Guidance teaches thinking, Rules enforce
- User will reject new sentences added to merge paragraphs — edit in place
- Do not invent `md/` subfolders in examples; hierarchy matches story map
- `/turn` via `workspace.workspace:Turn` tool `turn`; TurnCommit YAML serialization may error even when commit succeeds — verify with `git log -1`
