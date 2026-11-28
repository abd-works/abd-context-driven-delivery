# cog-02 session.toggle_guidance with a name that is no practice, stage or format answers success, raises the version and commits, and changes nothing

**Title** - Toggling practice `astrology`, practice `UX` (the short name the chat bar shows), stage `Specification` (the stage's title) or format `Markdown` is accepted silently: the version goes up, a commit is made on main, and nothing is turned on or off.

**Charter** - theme 7. **Tester** - Cog.

**Story** - Move Work Forward From Chat Bar / Choose Session Practices And Overlays In Chat Bar / Choose Session Practices, "Turn a fidelity's practice on or off from its square and name". The sibling story Choose Graph Overlays has "Refuse a name that is no pattern"; the practice, stage and format toggle have no such scenario, so no scenario covers this.

**Module and class** - `space/session/practices/guidance_selection.py` *GuidanceSelection.toggle* / `_toggled` / `select` (the unknown name is added to the list, then dropped by the loop over the session's practices or `STAGES.names`).

**Severity** - misleading message (an agent or page that sends the wrong spelling is told the toggle worked; the person's practice stays as it was).

## Steps

Sandbox and server as in cog-01 (`C:\dev\_et\after-1-2-1\cog`, port 8961, header `X-CDD-Project: C:\dev\_et\after-1-2-1\cog\work\repo`). Session `.sessions/checkout-flow/session.json` with Stories, DDD and UX on.

1. `session.toggle_guidance {"session": ".sessions/checkout-flow/session.json", "part": "practice", "name": "astrology"}`
2. Same with `"name": "UX"`, then `"name": ""`.
3. `{"part": "stage", "name": "Specification"}`, then `{"part": "format", "name": "Markdown"}`.
4. `git log --oneline` in `work/repo`.

## Expected

Each call refused, naming the part and the names it has (`stories, ddd, ux, clean_engineering, bdd`; `discovery, specification, ...`), with the selection, version and session.json unchanged, as `UnknownSelectionPart` already does for an unknown part and as the overlay toggle does for an unknown pattern.

## Actual

Every call answers OK with the selection unchanged and the version raised (5, 6, 7, 8, 9). Each makes a commit on main, for example:

```
5bf0667 sessions: checkout-flow guidance stages None, practices ['stories', 'ddd', 'ux', 'UX'], formats None sessions: checkout-flow guidance version raised
cba5990 sessions: checkout-flow guidance stages None, practices ['stories', 'ddd', 'ux', 'astrology'], formats None ...
```

Every waiting page (`guidance_selection_after`) is woken to redraw for a change that did not happen.

## Tier that should catch it

Unit: `space/session/session_spec.py` checks an unknown part (`colour`) but no unknown name within a known part.
