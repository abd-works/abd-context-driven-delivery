---
description: "When work runs in several passes or merges, run the quick suite after each pass and the heavy specs once at the end."
alwaysApply: true
---

# Test Timing

When a piece of work runs in several passes, such as a series of merges, refactor rounds, or agents' branches landing one after another, run the **quick suite** after each pass and the **heavy specs** once, at the end of the whole approach.

- **Quick suite after each pass:** the non-heavy specs (`scripts/test.ps1`, or every `*_spec.py` that is not `*_heavy_spec.py`) and the story tests. They run in minutes and catch almost every break a pass makes, so the next pass starts from known-good code.
- **Heavy specs once, at the end:** every `*_heavy_spec.py` (`scripts/test.ps1 -Suite heavy`), the ones that start servers, browsers, or a real install. Run them together after the last pass, then fix what they find and run them again. Running them after every pass multiplies a ten-minute wait by the number of passes, and the breaks they catch are rarer and easier to trace once all the changes are in.
- **Push after the quick suite passes**, as each pass lands. Say in the report that the heavy specs are still to run, so nobody reads a pushed pass as fully verified.

A single change made in one pass runs both, quick first, then the heavy specs for the modules it touched.
