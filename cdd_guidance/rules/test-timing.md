---
description: "Run the unit tier after each pass, the heavy tier once at the end, and the e2e tier when the work touches a browser or an agent."
alwaysApply: true
---

# Test Timing

The suite has three tiers, `scripts/test.ps1 -Suite unit | heavy | e2e`. What belongs in each is the BDD practice's `tier-by-speed` rule (`@bdd` development).

When a piece of work runs in several passes, such as a series of merges, refactor rounds, or agents' branches landing one after another, run the **unit tier** after each pass and the **heavy tier** once, at the end of the whole approach.

- **Unit after each pass:** it runs in seconds to a minute and catches almost every break a pass makes, so the next pass starts from known-good code. It fails any example over its budget; make that example fast or move it to a heavy spec.
- **Heavy once, at the end:** run it after the last pass, then fix what it finds and run it again. Running it after every pass multiplies a ten-minute wait by the number of passes, and the breaks it catches are rarer and easier to trace once all the changes are in.
- **E2E when the work touches a browser capture or an agent**, also once at the end.
- **Push after the unit tier passes**, as each pass lands. Say in the report which tiers are still to run, so nobody reads a pushed pass as fully verified.

A single change made in one pass runs unit first, then the heavy specs for the modules it touched.
