---
fidelity: [shaping]
artifact: [story-map]
---

# Generate — Story Map Outline (Shaping)

## Output shape

At **shaping** fidelity the story map is an **outline**, not a fully decomposed map.

Use `templates/md/story-map-outline.md` exactly. Do **not** use the discovery template (`story-map.md`) or add thin-slice sections.

### Outline notation

Plain text only — **never** wrap epic, sub-epic, story, or actor names in backticks.

```
(E) Move money
    * approx 22-27 total stories
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        * approx 2-3 more stories (various transfer detail entry and validation)
    (E) Approve transfer
        * approx 4-6 more stories (review, approve, reject, etc)
```

**Estimate lines** (`* approx …`) are required on every epic and every sub-epic:

- **Epic estimate** — rough total story count for the whole epic (`* approx 22–27 total stories`).
- **Sub-epic estimate** — additional stories not yet named (`* approx 2–3 more stories (various transfer detail entry and validation)`).

A sub-epic may have **only** confirming stories plus an estimate, **only** an estimate, or both. Do not fully decompose every branch — that is discovery fidelity.

Each epic needs **at least two confirming stories** somewhere under it — but those stories can all sit in one or two sub-epics. Not every sub-epic needs confirming stories; an estimate-only sub-epic is perfectly valid at shaping (see `concepts/story-map.md` outline mode). Name actors on confirming stories via `(S) Actor --> Story`.

## Fidelity branching

Respect the depth level the user asks for (see `concepts/story-map.md`).

- **Shaping** — outline with estimates and confirming stories only; do not apply the full discovery rule set.
- **Discovery and below** — use `generate-instructions/discovery.md` (or the fidelity-specific file) and the full `story-map.md` template.

Follow every file in `rules/` that applies at shaping; fill `templates/md/story-map-outline.md` to match its headings and fields exactly.

## story-graph.json schema (shaping)

Write `story-graph.json` as a flat object following this schema exactly.  Use camelCase keys.  The `users` field on every confirming story is **required** — the scanners enforce it.

```json
{
  "epics": [
    {
      "name": "Move money",
      "estimate": "approx 22-27 total stories",
      "subEpics": [
        {
          "name": "Compose transfer",
          "estimate": "approx 2-3 more stories (enter destination, validate amount)",
          "stories": [
            {
              "name": "Draft transfer details",
              "users": ["Treasurer"],
              "sequentialOrder": 1,
              "storyType": "user",
              "scenarios": []
            }
          ]
        }
      ]
    }
  ]
}
```

Rules:
- `users` is a list with one element — the actor name exactly as written in `(S) Actor --> Story`.
- `estimate` on epics and sub-epics mirrors the `* approx …` line from the markdown.
- Sub-epics with only estimates and no named stories have `"stories": []`.
- Do not add `scenarios`, `evidence`, or `domain_concepts` at shaping fidelity.

## Sub-epic scope rule

**At shaping, sub-epics represent major behavioral tracks — not every capability in the brief.**

Group related capabilities under one sub-epic rather than creating a sub-epic per capability.  Sub-epics that would contain only 1–2 stories should be absorbed into a related sub-epic and counted in its estimate.

Examples of consolidation:
- "Cancel pending transfer" has 1–2 stories → absorb into **Route transfer** or **Compose transfer**, not its own sub-epic.
- "Handle fraud-flag outcomes" has 2–3 stories → absorb into **Route transfer** (it is part of the routing decision), not its own sub-epic.
- "Submit transfer" is part of the compose→approve flow → absorb into **Approve transfer** or **Compose transfer**, not its own sub-epic.

Create a new sub-epic only when the capability is large enough to need its own track (roughly 4+ stories) **and** the brief describes it as a distinct user-facing behavior, not just an implementation step.

## Input traps

Assumptions, ambiguities, and missing context that commonly produce bad story maps. Check each trap against available input before generating — flag gaps honestly; do not invent structure to fill them.

- **Full decomposition at shaping** — if every sub-epic has a complete story list, you are at discovery depth, not shaping. Stop and produce an outline with estimates instead.
- **Inferred sub-epics** — every sub-epic must trace directly to the brief. If you cannot point to a sentence in the brief that names or clearly implies this behavior, remove the sub-epic and add a context gap instead.
- **Backticks on names** — do not wrap epic, sub-epic, story, or actor names in backticks; plain text only.
- **Missing estimates** — every epic and sub-epic needs an `* approx …` line sizing unmapped work. Estimates are not optional at shaping.
- **Hidden actors** — who actually uses this — is "the user" hiding three different people with different goals, or is there a system actor nobody mentioned?
- **Actor reality** — for every actor, confirm they exist in this iteration. Ask: is this a real human role, or an automated system? If automated, does the automation exist yet? Do not assume an actor is real because it sounds plausible — verify it. If everything is manual in this iteration, automated actors do not belong on the map.
- **Behaviors vs. tasks** — are these outcomes people care about, or build tasks disguised as stories? "Implement payment gateway" is a task; "Process customer payment" is a behavior. Which are we looking at?
- **Vague story names** — when a story uses a vague verb or noun ("provision", "manage", "handle", "set up", "improve"), ask what the actual concrete steps are. A story name must describe one observable behavior, not a category of work.
- **Tool specificity** — when a story describes a generic behavior ("extract content", "send notification"), ask which specific tool or mechanism is actually used. Generic behavior names produce generic output; name the tool.
- **Missing triggers** — are there background processes, scheduled jobs, or external systems that kick off behaviors nobody has surfaced yet? They always show up later as gaps.
- **Sequencing** — read the sub-epics in order. Can each story actually be done before the next one starts? Are there prerequisites that haven't appeared yet? Repo-before-extraction, setup-before-use. Common sense must pass.
- **Scope bleeding** — where does this product's responsibility end and another system's begin? If that boundary isn't drawn, stories will leak across it.
- **Duplication across sub-epics** — before finalising, scan all sub-epics for overlap. Do any two sub-epics describe the same behaviour under different names? If yes, collapse or kill the duplicate — do not carry redundant sub-epics forward.
- **Depth agreement** — does everyone expect the same level of detail from this map — an outline to frame conversations, or a full breakdown to plan work? Mismatched expectations waste everyone's time.
