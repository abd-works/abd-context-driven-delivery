---
name: stories
description: >-
  ## Overview
  
  Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.
  
  ---
---

## Overview

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

---

story_map — Define a story map as Epic → nestable Sub-Epic → Story. Change the map while nodes are still titles; after scenarios, screens, and tests exist, the same move is much more expensive.

Use MCP tool: `stories-story-map()`

scenarios — `{epic}/{sub-epic}/{story}/{story_snake}_story.test.md` — same stem as the TypeScript or Python acceptance test; only the extension is `md`. One file per story. Refine Stories into concrete examples with preconditions, triggering operations, and observable outcomes. A Scenario defines both the required behaviour and the evidence that will show whether it works.

Use MCP tool: `stories-scenarios()`

acceptance_tests

Use MCP tool: `stories-acceptance-tests()`
