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

1. **Views** — if the user already named the practices or fidelities, those are the views. Proceed. Otherwise AskQuestion which views to sketch, then proceed.
2. **Shell** — in that same turn, write the high-level shell and `save_sketch`. Follow each active fidelity's **Scaffold** section for the level of detail, and that practice's sketch template for the notation. When the active fidelity has no **Scaffold** section, use the **Scaffold** section of the earlier fidelity in that same practice. One section per practice in the same file (`stories:`, `ce:`, `ddd:`, `ux:`, `bdd:`). No theme blocks.
3. **Themes** — list the themes in priority order and AskQuestion which theme to start with.
4. **Grill that theme** — ask three or four questions, then stop. See **When asking a question**. Do not sketch the theme during these questions.
5. **Sketch** — fold those answers into the existing practice sections, using each practice's sketch template. `save_sketch`, then `review_sketch`.
6. **Bottom of the theme** — after `review_sketch` confirms the sketch, ask whether to get deeper on this theme or explore another theme. Update that theme's status in the sketch file.

Carry forward every mistake named in review. Correct the sketch. Do not regenerate as if those mistakes never happened.

## Fidelity

Sketches start at **discovery**. Load the **Rules** for each active practice at the fidelity you are in. The level of detail stays at that fidelity. Each practice names discovery differently:

| Stage | Stories | Clean engineering | DDD | UX | BDD |
|---|---|---|---|---|---|
| Discovery | `story_map` | `modules` | `bounded_context` | `ia` | `behavior` |
| Specification | `scenarios` | `model` | `building_blocks` | `mockup` | `behavior` |
| Implementation | `acceptance_tests` | `code` | `tactics` | `front_end_code` | `development` |

You may dip into the next fidelity's **Sketch** section and **Rules** when one question needs it. Then return. The goal is to finish the fidelity you are on.

Keep a theme list at the top of the sketch file. Every theme has one status: `scaffold`, `scaffold done`, `discovery done`, `specification done`, or `implementation done`. The shell sets each theme to `scaffold`. Update the status when that stage is finished.

At the bottom of a theme, AskQuestion:

- Get deeper on this theme — move that theme to the next stage in the table and keep working it.
- Explore another theme — return to the theme list.

When a theme passes through a fidelity (`scaffold done`, `discovery done`, `specification done`, or `implementation done`), ask whether to generate an official document. If yes, AskQuestion which formats, `allow_multiple: true`: markdown, diagram, and code. Then run `generate` for that practice at that fidelity, in each chosen format, following `actions/generate/generate.md`.

### Shell before questions

The shell is the first file. Zero questions before it when the user has already named the subject and the views. Mark anything still unknown with `?` or `* approx`.

Practice Rules for the fidelity you are in apply when sketching after the three or four answers. They do not apply to the shell. At the start, that fidelity is discovery: `story_map`, `modules`, `bounded_context`, `ia`, or `behavior`, for whichever practices are active.

## When asking a question (grill inside sketch)

Ask questions that the active guidance is designed to answer. See the **Sketch** section of that fidelity. Ask three or four of those questions, then sketch. Do not start by asking mechanical questions "EG how would you like to break up the stories" Unless it's germane to answering a specific business outcome. Focus first on questions that speak to outcomes, activities, steps, state, structure, and experience; Then drill into the more mechanical asects afterwards.

Each question is one of these:

- A recommended choice, with options, asked with AskQuestion.
- Or the same kind of question after you have read context. Still ask. Link to the recommendation source and location at the file you read.

Do not skip the question because you found an answer. Do not sketch between these questions.

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

Question shape is the AskQuestion block above. What to ask is the **Sketch** section of the active fidelity.

## Template discovery (tiered)

1. **Pasted example** — an example the user pasted in the chat. Use that shape.
2. **Practice template** — `practices/{practice}/templates/*-sketch.md` for each active practice (stories, clean engineering, DDD, UX).
3. **Built-in** — `actions/sketch/templates/sketch-template.md`, only when that practice has no sketch template.

If no template is found, say so and stop. Do not invent a notation.

## Persistence lifecycle

- **Session-rooted paths:** when chained from a Context generator, read the host **`active`** resource.
  - Engagement docs/diagrams → `destination = session` → `{session}/.context/{slug}-sketch.md`
  - Module sketch → `destination = {session}/{module}` → `{session}/{module}/.context/{slug}-sketch.md`
  - Generated code for that module → `{session}/{module}/` (not under `.context/`)
- Sketches live at `{destination}/.context/{slug}-sketch.md`. The slug names the subject, not the practice. When the session sketches more than one practice or guidance together (clean-engineering-model and bdd-behavior, object model and BDD), put every lens in that one file so the pairing stays visible; do not add `{slug}-bdd-sketch.md` beside it.
- `.context/` is created inside the destination if it does not already exist.
- **Hard rule:** `save_sketch` the shell in the same turn it is written. After three or four grill answers, sketch the theme into that same file, `save_sketch` again, then `review_sketch`. Do not ask the next theme until that review confirms the sketch. The three or four grill questions happen before that sketch, not after a review.
- **Carry-forward mistakes:** mistakes named in review — bad assumptions, poor performance, poor hygiene, or anything else — must shape the next sketch. Correct the model; do not regenerate as if those mistakes never happened.
- They persist until a formal artifact absorbs their content.
- Retirement is manual for now — remove the sketch when the formal artifact fully captures its intent.

## Multi-lens sketching

When more than one practice is active (Stories, DDD, UX, Clean Engineering, BDD), they share one sketch file. Each practice has one section. A theme is worked inside those sections. It does not get its own block.

```
stories:
ce:
ddd:
ux:
bdd:
```

Omit a section when that practice is not active. Use that practice's sketch template inside its section. Do not invent a notation.

### Rules

- **`views-already-named`** — When the user names the practices or fidelities, do not ask which views. Proceed to the shell.
- **`shell-before-questions`** — The first save is the shell. Its level of detail is that fidelity's **Scaffold** section. Its notation is the practice sketch template. Do not read practice Rules to produce the shell.
- **`themes-after-shell`** — After the shell is saved, give a prioritized theme list and ask which theme to start.
- **`grill-then-sketch`** — On the chosen theme, ask three or four questions from that fidelity's **Sketch** section, using that fidelity's **Rules**. Then sketch. Sketching edits the existing `stories:`, `ce:`, `ddd:`, `ux:`, and `bdd:` sections. Stay at discovery until the user asks to go deeper.
- **`theme-status`** — The sketch file lists every theme and its status: `scaffold`, `scaffold done`, `discovery done`, `specification done`, or `implementation done`.
- **`deeper-or-another`** — After review, ask whether to get deeper on this theme or explore another theme.
- **`generate-on-the-way-through`** — When a theme finishes a fidelity, ask whether to generate the official document. Formats are markdown, diagram, and code. Multiple formats are allowed. Run `generate` at that fidelity in the chosen formats.
- **`one-sketch-per-engagement`** — One sketch file. Deepen it in place. Do not add a second file per fidelity or practice.
- **`lens-from-child-template`** — Section bodies use that practice's sketch template. No free prose inside `stories:` / `ddd:` / `ux:` / `ce:` / `bdd:`.

### Common mistakes

❌ Asking which views when the user already named them
❌ Designing stories, classes, or rules before the shell file exists
❌ A `=========` block per theme — themes are a queue, not sections
❌ Asking the user to pick a story split, a class, or a property
❌ Sketching after one question — wait for three or four
❌ A second sketch file for another practice

---
## Composition — how sketch chains with other actions

`@sketch` **explicitly calls** `grill_with_context`, then chains `sketch_session`. Expansion order:

```
grill_with_context  ← pure Q-loop (no sketch advice)
sketch_session      ← template + save_sketch cadence
base action body    ← e.g. Context.sketch → self.generate()
```

Base `Context` exposes peer entry points: `generate` (plain), `grill`, `sketch`, `iterate`. Domains inherit them; do not re-decorate domain `generate` with `@sketch` / `@grill_with_context`.
