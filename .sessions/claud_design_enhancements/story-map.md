---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Design Canvas Experience

**Sources / context:** `.context/story-map.drawio` (starting hierarchy and order); `.context/story-map.md` (actors and sources for the carried stories); `.context/cdd-flow-of-work.drawio` (domain model before the prototype: bounded context and domain model, domain model API covers all scenarios, scenario tests call the domain API, domain code implements them, then the behavioral prototype); `cdd_guidance/practices/stories/model/claude_design/claude_design.md` and `nodes.py`, `explorer.dc.html`; `cdd_guidance/practices/ux/model/claude_design/claude_design.md` and `nodes.py`; `cdd_guidance/patterns/lern_domain_driven/practices/stories/model/claude_design/claude_design.md` and `fixtures.py`; `harness/design_canvas/canvas.py`, `fixture_bar.py`, `versions.py`, `design_canvas_spec.py`, `versions_spec.py`; `.sessions/claud_design_enhancements/backlog.md` (no canvas diagram for the domain model yet).

**Evidence:**

| Part of the map | Label | Why |
|---|---|---|
| Build Canvas Prototype, Publish Canvas Version, Play Canvas Story | observed in code and guidance | Read from the canvas code, its specs, and the `claude_design.md` rules. No published canvas was walked for this map. |
| Isolate Running Application, Scaffold Solution Outline, Document Behavior Slice, Prove Behavior Slice, Review Captured Behavior, Cover Remaining Behavior | inferred | Carried from `.context/story-map.drawio`. That map says no live run was walked for them. |
| Model Core Domain | intended | The user asked for the domain model as a core part of the flow. Order comes from `.context/cdd-flow-of-work.drawio`. |
| Trace Steps To Domain Operations, Implement Domain Code | intended | Named by the rule `gwt-steps-trace-to-domain-operations` and by `.context/cdd-flow-of-work.drawio`. They are not stories on the starting map. |

---

# (E) Prepare Canvas Model
## (E) Isolate Running Application
### (S) User --> Capture Live Application
### (S) Context Setup --> Classify External Dependencies
### (S) Context Setup --> Write Boundary Stubs
### (S) Context Setup --> Smoke Test Application
### (S) Context Setup --> Scout Application Pages
### (S) Context Setup --> Complete Capture Pages
## (E) Scaffold Solution Outline
### (S) User --> Open Capture Session
### (S) User --> Request Discovery Scaffold
### (S) Discoverer --> Confirm Practice Lenses
### (S) Stories --> Name Journey Stories
## (E) Model Core Domain
### (S) Ddd --> Map Bounded Contexts
### (S) Ddd --> Name Context Aggregates
### (S) Ddd --> Capture Aggregate Operations
### (S) Ddd --> Draw Domain Model Diagrams
### (S) User --> Review Domain Model
## (E) Document Behavior Slice
### (S) User --> Document Specification Slice
### (S) Specification --> Confirm Practice Lenses
### (S) Stories --> Capture Story Scenarios
### (S) Stories --> Trace Steps To Domain Operations
### (S) Ux --> Link Stories To Screens
## (E) Prove Behavior Slice
### (S) User --> Document Engineering Slice
### (S) Stories --> Write Story Tests
### (S) Ddd --> Write Domain Wraps
### (S) Ddd --> Implement Domain Code
### (S) Stories --> Run Story Tests
# (E) Play Design Canvas
## (E) Build Canvas Prototype
### (S) Canvas Fixtures --> Bundle Story Fixtures
### (S) Ux --> Port Product Screen
### (S) Ux --> Attach Fixture Bar
### (S) Ux --> Read Screen State From Fixture
### (S) Ux --> Bind Buttons To Domain Operations
## (E) Publish Canvas Version
### (S) Canvas Versions --> Start Working Version
### (S) Claude Design --> Render Story Map Artboard
### (S) Claude Design --> Render Story Explorer
### (S) Claude Design --> Lay Out Screen Pages
### (S) User --> Publish Canvas Version
### (S) Canvas Versions --> Record Version Link
### (S) Canvas Versions --> Release Canvas Version
## (E) Play Canvas Story
### (S) User --> Zoom Story Map
### (S) User --> Open Story Thumbnail
### (S) User --> Select Scenario Step
### (S) User --> Select Outline Row
### (S) Canvas Fixtures --> Replay Scenario Givens
### (S) Screen --> Show Domain Refusal
### (S) User --> Paste Dev Seed
### (S) User --> Follow Next Story
### (S) User --> Copy Open Request
## (E) Review Captured Behavior
### (S) User --> Review Story Meaning
### (S) User --> Edit Screen Artboard
### (S) User --> Accept Stage View
### (S) User --> Log Behavior Mistake
### (S) Eval --> Record Mistake Entry
### (S) User --> Log Behavior Correction
### (S) Eval --> Nest Correction Repair
## (E) Cover Remaining Behavior
### (S) User --> Advance Coverage Increment
### (S) Stories --> Cover Distinct Behaviors
### (S) User --> Request Session Handoff
### (S) Handoff --> Write Handoff Document

---

## Scope boundary

**In scope:** The repeatable path from a running application to a design canvas a person can play. The domain model is worked before the behavior slice, so scenario steps trace to aggregate operations, story tests call those operations, and canvas screens run the same domain code through the fixtures bundle. A version is rendered, published, played, reviewed, and followed by the next increment.

**Out of scope:** Installation, Open Work Session, Open Practice Catalog, and Prepare Context Index. The canvas enhancements in `.sessions/claud_design_enhancements/backlog.md` (asset reuse, a test button, story-ui, and domain diagrams on the canvas) are not current behavior. Draw Domain Model Diagrams means the existing diagram render, not a canvas page.
