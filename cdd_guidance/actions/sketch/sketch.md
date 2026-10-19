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
2. **Shell** — in that same turn, write the high-level shell and `save_sketch`. Follow each active fidelity's **Scaffold** section for the level of detail, and that practice's sketch template for the notation. When the active fidelity has no **Scaffold** section, use the **Scaffold** section of the earlier fidelity in that same practice. One section per active practice in the same file: `stories:`, `domain driven design:`, `user experience:`, `behavior driven development:`, and `clean engineering:` only when CE is active **without** DDD. No theme blocks.
3. **Themes** — list the themes in priority order and AskQuestion which theme to start with.
4. **Grill that theme** — ask three or four questions, then stop. See **When asking a question**. Do not sketch the theme during these questions.
5. **Sketch** — fold those answers into the existing practice sections, using each practice's sketch template. `save_sketch`, then `review_sketch`.
6. **Bottom of the theme** — after `review_sketch` confirms the sketch, ask whether to get deeper on this theme, explore another theme, or **render** the sketch at the fidelity just finished. Update that theme's status in the sketch file.

Carry forward every mistake named in review. Correct the sketch. Do not regenerate as if those mistakes never happened.

## Fidelity

Sketches start at **discovery**. Load the **Rules** for each active practice at the fidelity you are in. The level of detail stays at that fidelity. Each practice names discovery differently:

| Stage | Stories | Clean Engineering | Domain Driven Design | User Experience | Behavior Driven Development |
|---|---|---|---|---|---|
| Discovery | `story_map` | `modules` | `bounded_context` | `ia` | `behavior` |
| Specification | `scenarios` | `model` | `building_blocks` | `mockup` | `behavior` |
| Implementation | `acceptance_tests` | `code` | `tactics` | `front_end_code` | `development` |

You may dip into the next fidelity's **Sketch** section and **Rules** when a question needs it. Then return. The goal is to finish the fidelity you are on. Often that means exploring at the next level but that does not mean you're at the next fidelity — load the fidelity and its rules as needed, then go back to the previous.

Keep a theme list at the bottom of the sketch file. Every theme has a collection of check boxes beside each other ->`scaffold done`, `discovery done`, `specification done`, or `implementation done`. The shell sets each theme to `scaffold`. Update the status when that stage is finished. You may add new themes at the request of the user or as you discover new themes you should validate with the user whenever you want to add new themes.

At the bottom of a theme, AskQuestion:

- Get deeper on this theme — move that theme to the next stage in the table and keep working it.
- Explore another theme — return to the theme list.
- Render the sketch — turn the approved sketch into formal artifacts (see **Render from sketch** below).

## Render from sketch

When a theme passes through a fidelity (`scaffold done`, `discovery done`, `specification done`, or `implementation done`), ask whether to **render** the sketch into official artifacts. The sketch file is the source — render transforms it; do not re-author from chat.

**Default:** use **`/sketch_render`** or the `SketchRender` toolset (`actions/sketch_render/sketch_render.md`). Same grill-and-sketch loop as `/sketch`; after `review_sketch` confirms the sketch:

1. **AskQuestion** whether to render now (unless the user already asked to render). Do **not** ask which single format to pick — each stage has a **required pair** (below). Only deviate when the user explicitly names a different format set.

| Stage | Required formats (always both) |
|---|---|
| discovery | `drawio` **and** `markdown` |
| specification | `typescript` **and** `markdown` |

`build_render_calls` must receive **both** formats for the active stage when the listed practice supports them. Skip a format when that practice has no sketch transform for it (`SKETCH_RENDER_FORMATS` in `sketch_render.py`).

| Practice · fidelity | From sketch |
|---|---|
| Stories · `story_map` | `drawio`, `markdown` → `story-map.md` outline |
| DDD · `bounded_context` | `drawio`, `markdown` → bounded-context map |
| UX · `ia` | `drawio` only — markdown is optional `ux-context.md` notes, not IA |

Do not render UX as markdown from a multi-lens sketch file — that output is notes-only, not IA.

2. **`build_render_calls`** — pass the approved sketch path and the stage's required format list (e.g. `["drawio", "markdown"]` at discovery). Returns JSON: one `render.render` entry per practice × format. Each entry carries the **full sketch file** as `content` with `source: sketch` so each practice parses only its own `##` section.

3. **`render_approved_sketch`** — run that JSON in a background sub-agent (non-blocking). Each call is `render.render(guidance: {toolset, fidelity}, format, content, source=sketch)`. Then follow `render.place_rendered` on the written files.

Do not invent render parameters in the sub-agent — `build_render_calls` owns them.

**During an ongoing `/sketch` session** (without the full `sketch_render` wrapper), after the user asks to render:

1. Confirm the sketch with `review_sketch` if that gate has not passed yet.
2. Use the required format pair for the active stage (discovery → `drawio` + `markdown`; specification → `typescript` + `markdown`).
3. Call `SketchRender.build_render_calls(formats, sketch_path)` then `SketchRender.render_approved_sketch(render_calls)`.

**When render is not enough** — use `generate.generate` only when the user explicitly wants a fresh AI-authored pass that does not transform the sketch file (rare). Normal sketch completion is **render**, not generate.

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

When more than one practice is active (Stories, Clean Engineering, Domain Driven Design, User Experience, Behavior Driven Development), they share one sketch file. Each practice has one section. A theme is worked inside those sections. It does not get its own block.

When **Domain Driven Design** is active, follow `practices/ddd/ddd.md` under **Sketch** at the active fidelity for how module seams and aggregate-root operations fold into `domain driven design:`.

```
## stories:
## clean engineering:
## domain driven design:
## user experience:
## behavior driven development:
```

Omit a section when that practice is not active. Use that practice's sketch template inside its section. Do not invent a notation.

### Headings carry the hierarchy

Each practice section is a `##` heading. Inside it, the practice's tree nests through deeper headings — `###` for the top of that practice's shape, `####` for its children, and so on — so every epic, module, context, journey, and subject folds on its own. Detail that has not earned a heading sits in a fenced block under the heading that owns it. Each practice's sketch template names which heading depth holds what.

Prose that is not part of a practice's tree — open questions, what is settled, false cognates, the theme list — is its own `##` section beside the practice sections, never a heading inside one.

### Rules

- **`views-already-named`** — When the user names the practices or fidelities, do not ask which views. Proceed to the shell.
- **`shell-before-questions`** — The first save is the shell. Its level of detail is that fidelity's **Scaffold** section. Its notation is the practice sketch template. Do not read practice Rules to produce the shell.
- **`themes-after-shell`** — After the shell is saved, give a prioritized theme list and ask which theme to start.
- **`grill-then-sketch`** — On the chosen theme, ask three or four questions from that fidelity's **Sketch** section, using that fidelity's **Rules**. Then sketch. Sketching edits the existing `stories:`, `clean engineering:`, `domain driven design:`, `user experience:`, and `behavior driven development:` sections. Stay at discovery until the user asks to go deeper.
- **`theme-status`** — The sketch file lists every theme and its status: `scaffold`, `scaffold done`, `discovery done`, `specification done`, or `implementation done`.
- **`deeper-or-another-or-render`** — After review, ask whether to get deeper on this theme, explore another theme, or render the sketch at the fidelity just finished.
- **`render-from-sketch`** — When a theme finishes a fidelity, offer render. Use `SketchRender.build_render_calls` and `render_approved_sketch` (or `/sketch_render` end-to-end). Pass the sketch file as `content` with `source: sketch` — straight render from sketch, not `generate.generate`. Discovery always renders **drawio and markdown**; specification always renders **typescript and markdown**.
- **`one-sketch-per-engagement`** — One sketch file. Deepen it in place. Do not add a second file per fidelity or practice.
- **`lens-from-child-template`** — Section bodies use that practice's sketch template. No free prose inside `stories:` / `clean engineering:` / `domain driven design:` / `user experience:` / `behavior driven development:`.
- **`headings-carry-the-hierarchy`** — Nest each practice's tree through markdown headings below its `##` section, at the depths that practice's template names. Keep leaf detail in a fenced block under the heading that owns it. Open questions, settled decisions, and the theme list are their own `##` sections, not headings inside a practice section.

### Common mistakes

❌ Asking which views when the user already named them
❌ Designing stories, classes, or rules before the shell file exists
❌ A `=========` block per theme — themes are a queue, not sections
❌ Asking the user to pick a story split, a class, or a property
❌ Sketching after one question — wait for three or four
❌ A second sketch file for another practice
❌ Rendering only one format at discovery (markdown without drawio) or specification (typescript without markdown)

---
## Composition — how sketch chains with other actions

`@sketch` **explicitly calls** `grill_with_context`, then chains `sketch_session`. Expansion order:

```
grill_with_context  ← pure Q-loop (no sketch advice)
sketch_session      ← template + save_sketch cadence
base action body    ← e.g. Context.sketch (persist only; render is separate)
```

`@sketch_render` chains the same sketch loop, then **`build_render_calls` → `render_approved_sketch`** on approval. See `actions/sketch_render/sketch_render.md`.

Base `Context` exposes peer entry points: `generate` (plain), `grill`, `sketch`, `sketch_render`, `iterate`. Domains inherit them; do not re-decorate domain `generate` with `@sketch` / `@grill_with_context`. After sketch approval, prefer **`sketch_render`** over `generate` for formal artifacts.
