---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories.
     Do not wrap epic, sub-epic, story, or actor names in backticks.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story-kebab-slug}.py
     — epic/sub-epic folders kebab-case; one story file per story (no {story}/ folder).
     Exception: Python epic helper only — {epic_slug}_helper.py at epic root. -->

# Story Map — Context-Driven Delivery

**Sources / context:** `README.md` (install, practice plus action plus optional format, discovery / specification / implementation); `.context/principles/context-as-code-strategy.md` (sandbox, scaffold, document one slice, tests until green, human review, next increment); `practices/cdd/agents/context.md`, `discovery.md`, `specification.md`, `implementation.md`; `.context/module-context.md` (Installer, Context Setup, Stories, Ddd, Handoff, Eval).

**Evidence:** Inferred from those sources. No live session was walked in this pass, so none of these nodes are marked observed. Intended where a role prompt prescribes a confirm-or-handoff step the strategy does not show as a separate command.

---

(E) Deliver Verified Context
    (E) Install Delivery Harness
        (S) User --> Run Install Command
        (S) Installer --> Publish Markdown Installation
        (S) Mcp Installation --> Publish Mcp Manifest
        (S) Hook Installation --> Publish Hooks Manifest
        (S) User --> Open Practice Catalog
    (E) Isolate Running Application
        (S) User --> Capture Live Application
        (S) Context Setup --> Classify External Dependencies
        (S) Context Setup --> Write Boundary Stubs
        (S) Context Setup --> Smoke Test Application
        (S) Context Setup --> Scout Application Pages
        (S) Context Setup --> Complete Capture Pages
    (E) Scaffold Solution Outline
        (S) User --> Open Capture Session
        (S) User --> Request Discovery Scaffold
        (S) Discoverer --> Confirm Practice Lenses
        (S) Stories --> Name Journey Stories
        (S) Ddd --> Name Context Aggregates
    (E) Document Behavior Slice
        (S) User --> Document Specification Slice
        (S) Specification --> Confirm Practice Lenses
        (S) Stories --> Capture Story Scenarios
        (S) Ddd --> Capture Aggregate Operations
    (E) Prove Behavior Slice
        (S) User --> Document Engineering Slice
        (S) Stories --> Write Story Tests
        (S) Ddd --> Write Domain Wraps
        (S) Stories --> Run Story Tests
    (E) Review Captured Behavior
        (S) User --> Review Story Meaning
        (S) User --> Accept Stage View
        (S) User --> Log Behavior Mistake
        (S) Eval --> Record Mistake Entry
        (S) User --> Log Behavior Correction
        (S) Eval --> Nest Correction Repair
    (E) Cover Remaining Behavior
        (S) User --> Advance Coverage Increment
        (S) Stories --> Cover Distinct Behaviors
        (S) User --> Request Session Handoff
        (S) Handoff --> Write Handoff Document

---

## Scope boundary

**In scope:** The repeatable path a person uses to get verified context for an existing application. Install publishes skills, rules, commands, the MCP manifest, and hooks, then the catalog is opened. Context Setup isolates the running app. Stories and Ddd scaffold the outline, document one slice, and prove that slice with story tests and domain wraps. The person reviews meaning, accepts the stage, and logs a mistake and its correction. The next increment covers another distinct behavior, and Handoff writes the session handoff.

**Out of scope:** The one-time repository clone. The toolset authoring spine in `harness/.context/story-map.md`. Scenario text, acceptance-test code, and domain class bodies. Clean Engineering, BDD, Diagnose, and workflow tickets, which the strategy names as available and leaves off this path.
