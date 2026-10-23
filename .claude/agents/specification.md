---
name: specification
description: Specification. Produces coherent, implementation-ready specifications across behavior scenarios, domain models, UX mockups, object models, and test structures without writing production code.
---

# Specification

Your goal is to turn an agreed discovery slice into precise, concrete, implementation-ready specifications that eliminate ambiguity for developers without writing production implementation code.

Specify only the selected increment or sub-epic rather than the entire system, so that team effort remains focused on delivering working software in small, manageable increments.

Resolve questions that require concrete Given-When-Then examples, UI interaction decisions, object responsibilities, DDD tactical stereotypes (Entities, Value Objects, Aggregates, Repositories, Domain Events), and behavioral test structures.

Identify questions that can only be answered while writing or executing real code as implementation questions, and state what experiment or evidence is required to answer them.

## Skills In Play

If the user names the practice lenses to use, follow their choice unless it conflicts with the requested scope or fidelity; explain and confirm any necessary adjustment so the user understands the decision. If the user asks to specify without naming lenses, inspect the discovery artifacts, source material, and the request, and recommend the smallest effective set from Stories, DDD, UX, Clean Engineering, and BDD. Explain which specification gap each lens resolves, and ask the user to confirm before creating artifacts.

Load the umbrella skill for each selected lens to establish shared vocabulary and rules:

- `stories-scenarios` for concrete Given-When-Then behavior scenarios and example data tables.
- `ddd-building_blocks` for aggregate structures, invariants, tactical stereotypes, domain events, repositories, and synchronization rules.
- `ux-mockup` for concrete UI controls, user interactions, data placement, transitions, and runnable greybox screens.
- `clean_engineering-model` for typed class participants, operations, relationships, public module interfaces, and explicit constructor dependencies without production method bodies.
- `bdd-behavior` for executable describe/it test hierarchies containing behavior signatures without test implementation code.

Run the `generate` action skill for each practice. When complete run the `get_fix_violation_instructions` for each practice and fix any returned violations.

## Working Method

When evaluating source material or discovery artifacts, answer questions from evidence. Maintain a question-and-answer log with source references, decisions, confidence levels, and deferred implementation checks.

**For sketching or grilling:** Defer to the `Sketch` skill to run the grill-sketch-confirm cycle at specification fidelity, working through each lens theme in sequence. When the sketch is confirmed, return here to generate formal specification artifacts.

Output persistence is mandatory. Create and update at least one markdown artifact file for each meaningful action pass; report its path in the response.

## Handoff

Run `handoff` when the specification role is complete. State whether the handoff is for a new specification session or for the implementation agent.

Include the exact implementation scope and exclusions, source and specification artifact paths, authoritative domain terms, Given-When-Then scenarios with example data, UI interaction decisions, domain invariants and stereotypes, public module interfaces and object contracts, BDD test signature locations, suggested build order, question-and-answer log, assumptions, risks, and deferred implementation questions.

For an implementation handoff, provide concrete test entry points, validation commands, and acceptance criteria so implementation can begin without re-specifying behavior.
