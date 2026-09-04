---
name: car-trip_outline
description: "Provide guidance for in-character road stories at the current fidelity."
disable-model-invocation: true
---

# car-trip_outline

Use car guidance at `trip_outline` fidelity only.

Provide guidance for in-character road stories at the current fidelity.
At trip_outline fidelity: write bullet beats only — destination, conditions, tool order.
At road_story fidelity: write full prose with start, drive, speak, and stop woven in.
At full_journey fidelity: write prose and call wrap_story when a trip log is needed for inspection.
Every tool call uses this toolset with context make, model, year, and personality.
When the story needs a scripted trip, call travelTo on the CarStory companion and pass this Car as a tool argument.