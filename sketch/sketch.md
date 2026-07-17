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
- Not a file dumped into chat — always presented and refined interactively before persisting.
- **Not a margin-annotation exercise.** Do not tag sketch lines with fidelity markers (`<-i`, `<-m`, `<-s`, or similar). If fidelity matters, declare it once at the top of the sketch. The body is the shape — not a legend of which line belongs to which fidelity.

## Loop

1. **Locate a template** — tiered discovery (see below).
2. **Draft** — rough shape inspired by the template. In chat only.
3. **Present** — show the sketch to the user with a short explanation of the reasoning behind the shape. No files yet.
4. **Extend the next branch** — pick the next unresolved branch of the design tree, sketch your recommended shape for it into the artifact, and explain why in one or two lines. One branch at a time. Wait for feedback.
5. **Refine** — regenerate the sketch showing what changed, integrating the branch just extended (or the correction the user gave).
6. **Repeat** 4–5 until either the user says done, or every branch of the design tree has been sketched and reasoned out. Ask a question only when a branch genuinely cannot be resolved by sketching a recommendation.
7. **Persist** — save to `{destination}/.context/{slug}-sketch.md` where destination is the folder of the thing being sketched.

## When asking a question (grill inside sketch)

Bare option lists are not allowed. The user must be able to decide from the concepts in play — not from intuition about unlabeled choices.

For every question:

1. **Frame** — name the sketch branch, restate what is already agreed in the sketch, and ground the decision in the active practice concepts (e.g. for clean_engineering modules: high-cohesion, low-coupling, named-seam-and-constraint, deep-module, complexity-absorption; for OOAD: class vs property vs operation, composition/aggregation/association, single responsibility). Pull those concepts from the wrapped agent's material / fidelity docs, not from generic advice.
2. **Options with rationale** — 3–5 choices; recommended first; each option gets one short concept-tied rationale (what it does to the seam, ownership, or coupling). End with "Other / I'll specify."
3. **One question** — wait for the answer, then regenerate the sketch showing exactly what changed.

When `@grill_with_context` is also in the chain, follow that action's Step 3a–3b for the question shape; this section is the sketch-side contract for the same standard.

## Template discovery (tiered)

1. **Session context** — templates or examples the caller passed in at invocation time. Owned by the current session. Highest priority: a user pasting an example in chat immediately shapes the sketch.
2. **Convention (wrapped agent's own template)** — `{agent_dir}/sketch-template.*` sitting next to the wrapped agent's module. Owned by whoever wrote that agent; lets each agent shape its own sketches without touching the sketch toolset.
3. **Default (built-in fallback)** — `sketch/sketch-template.md` shipped inside the sketch toolset itself. Owned by this toolset; used only when nobody upstream supplied a template.

If none of the above yield a template, the sketcher invents a shape for the domain at hand — explicitly a fallback, not a design target.

## Persistence lifecycle

- Sketches live at `{destination}/.context/{slug}-sketch.md` where destination is the folder of the thing being sketched (e.g. `ooad/.context/ooad-sketch.md`).
- `.context/` is created inside the destination if it does not already exist.
- They persist until a formal artifact absorbs their content.
- Retirement is manual for now — remove the sketch when the formal artifact fully captures its intent.

## Composition — how sketch chains with other actions

The `@sketch` decorator marks an `@action` method so the sketch loop fires before the base action's body is expanded. Decorators fire in **declaration order** (top-down):

```
@sketch          ← fires 1st
@grill_context   ← fires 2nd
@action
def generate(self, ...): ...   ← base action runs last
```

See `ooad/.context/rethinking-fidelity-and-process.md` for the full design record and the deferred implementation slice that wires this decorator marker into the ActionExpander.
