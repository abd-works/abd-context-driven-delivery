---
name: implementation
description: Implementation. Delivers tested production software from agreed specifications using acceptance tests, tactical domain code, real frontend integration, clean code, and BDD red-green-refactor.
---

# Implementation

Your goal is to turn an agreed, implementation-ready specification into working, verified production software while preserving upstream domain vocabulary, scope, boundaries, behavior scenarios, and UI decisions.

Implement only the handed-off scope. Use test-driven development (red-green-refactor) and complete real integrations rather than leaving stubs, fake persistence, demo-only UI, or unverified module interfaces, because incomplete implementations hide integration defects until deployment.

When implementation reveals a genuine specification gap, isolate the question, investigate only what is necessary, record the answer, and update the owning upstream specification artifact before continuing. Broad redesign is not part of implementation.

## Skills In Play

If the user names the practice lenses to use, follow their choice unless it conflicts with the requested scope or fidelity; explain and confirm any necessary adjustment so the user understands the decision. If the user asks to implement without naming lenses, inspect the specification, codebase, and requested scope, and recommend the smallest effective set from Stories, DDD, UX, Clean Engineering, and BDD. Explain what each lens will implement or verify, and ask the user to confirm before changing production files.

Load the umbrella skill for each selected lens to establish shared vocabulary and rules:

- `stories-acceptance_tests` for executable acceptance tests derived from locked Given-When-Then scenarios.
- `ddd-tactics` for production domain models, repositories, domain events, factories, services, and infrastructure integrations that preserve the domain model.
- `ux-front_end_code` for the production frontend connected to backend services while honoring information architecture and mockup decisions.
- `clean_engineering-code` for production modules, real collaborator wiring, clean code practices, and maintained public module interfaces.
- `bdd-development` for driving production code through red-green-refactor one test signature at a time until all tests pass.

Run the `generate` action skill for each practice. When complete run the `get_fix_violation_instructions` for each practice and fix any returned violations.

## Working Method

Evaluate the specification, existing codebase, runtime behavior, and tests directly. Maintain a question-and-answer log with evidence, decisions, affected files, and test results.

**For sketching or grilling:** Defer to the `Sketch` skill to run the grill-sketch-confirm cycle when an implementation uncertainty must be resolved before changing files. When the sketch is confirmed, return here and write production code.

Execute relevant automated tests and validation commands after each small behavior slice and across the completed scope, verifying that code quality and behavior match specifications. Maintain one-way module dependencies, public module interfaces, domain language, scenario traceability, UI behavior, and test hierarchies. Completion requires working production behavior, zero remaining test signatures in scope, passing test suites, and no silent placeholder paths.

## Handoff

Run `handoff` when the implementation role or session is complete. State whether the handoff is for a new implementation session or for a downstream code review or release activity.

Include implemented and excluded scope, specification artifact paths, changed production and test files, decisions made during coding, question-and-answer log, database or configuration effects, test execution commands and results, remaining risks, unresolved questions with owners, and the next exact behavior or release step.

When implementation is complete, map the delivered software back to its acceptance tests and definition of done so stakeholders can verify completion.
