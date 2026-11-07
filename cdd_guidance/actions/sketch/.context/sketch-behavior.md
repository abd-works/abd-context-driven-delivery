# Sketch — Maintainer Behavior

Narrative for maintainers of the sketch module itself. AI reading this file: this describes how the module is structured and where design authority lives.

## What lives here

- `sketch.py` — the `Sketch` action, a `GuidanceAction` made for one session. Its tools are `find_template`, `save_sketch`, `list_sketches`, and `review_sketch`; its instructions are `sketch(guidance)`, published as the `actions-sketch` skill and the `sketch.sketch` MCP operation.
- `sketch_outline.py` — `SketchOutline` and `SketchLens`: a sketch holds one section per practice, opened by the headings that practice declares, and `SketchOutline.body_for(lens)` hands one practice its section, flattened to indentation, so the practice's sketch format can read it.
- `sketch.md` — the behavior contract and rules an agent reads at runtime.
- `templates/sketch-template.md` — the default heading-and-indent notation used when the practice has no sketch template of its own.
- `agents/sketcher.md` — the Sketcher sub-agent that runs sketch-grill-confirm cycles.
- `__init__.py` — public exports.

## Design authority

`sketch.md` is the source of truth for how a sketch runs:

- Sketch is an action, not a fidelity: each fidelity's **Scaffold** section sets how much detail the first shell holds, and each practice's sketch template sets its notation.
- One sketch file per session, `{session root}/.context/{session name}-sketch.md`, with one section per practice, so every practice in play is sketched side by side.
- Sketch runs the grill (`GrillContext`) made for the same session, and `review_sketch` is a hard gate after every save, so each grill question is asked against a sketch the person has confirmed.

## How it runs

1. `sketch(guidance)` begins the action on the listed guidance, adds each listed fidelity's rules and sketch template to the instructions, and runs `GrillContext.grill_with_context`.
2. The agent writes the shell and calls `save_sketch` in the same turn; `review_sketch` asks the person whether it is correct before the next question.
3. After three or four grill answers, the agent sketches that theme into the same file, saves it, and reviews it again.
4. `GrillContext.generate_each` follows, so the agreed sketch can become the formal artifact.

Template discovery is tiered: a template the caller passes in the session, then `{agent_dir}/templates/*-sketch.*`, then `templates/sketch-template.md`.

## When to change the default template

Change `templates/sketch-template.md` only when the heading-and-indent notation itself is being revised. A practice keeps its own notation in its `templates/{practice}-sketch.md`, so do not change the default to suit one practice.
