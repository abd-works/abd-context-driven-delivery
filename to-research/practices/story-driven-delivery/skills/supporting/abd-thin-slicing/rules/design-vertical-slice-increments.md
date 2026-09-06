# Rule: Design vertical-slice increments

Each increment is a **vertical slice**: a **working** path from **input → processing → persistence → visible outcome**, pulling **partial** depth from **multiple** epics or features as needed. Avoid **horizontal** plans that finish one epic before the next—those delay end-to-end validation.

## DO

- Include the **smallest** set of behaviors that still **demonstrates** the journey, across whatever parts of the map touch that journey.
- Show **integration points** early—even if crudely (manual handoff, file store, simple UI).
- Make **partial completion** visible per epic when helpful (e.g. “Invoice epic2/5 in this increment”) so progress is honest.

```text
Increment 1: Place order → manual payment recording → save to file → confirmation email (stub).
Increment 2: Same flow → real gateway → database → richer confirmation.
```

## DON'T

- Plan “Increment 1 = all of character creation, Increment 2 = all of storage” with **no** playable journey until late.
- Ship an increment that stops mid-air (**no** persistence, **no** visible result) and call it “done.”
- Optimize for **component completeness** over **journey demonstrability**.
