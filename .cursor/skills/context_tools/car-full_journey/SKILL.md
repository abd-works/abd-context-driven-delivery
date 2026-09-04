---
name: car-full_journey
description: "Provide guidance for in-character road stories at the current fidelity."
disable-model-invocation: true
---

# car-full_journey

Use car guidance at `full_journey` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@car-road_story
@car-trip_outline

Provide guidance for in-character road stories at the current fidelity.
At trip_outline fidelity: write bullet beats only — destination, conditions, tool order.
At road_story fidelity: write full prose with start, drive, speak, and stop woven in.
At full_journey fidelity: write prose and call wrap_story when a trip log is needed for inspection.
Every tool call uses this toolset with context make, model, year, and personality.
When the story needs a scripted trip, call travelTo on the CarStory companion and pass this Car as a tool argument.