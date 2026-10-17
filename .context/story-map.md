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

# (E) Install CDD Tools
##  (E) Install Agent Toolset
###     (S) Installer --> Generate Installer Skill
###     (S) Installer --> Generate skills and commands from Agent Toolset
###     (S) Installer --> Generate Skills and Commands With MCP Calls
###     (S) Installer --> Enroll Agent Toolset as MCP Tools
###     (S) Installer --> Configure and Start MCP Host Session
###     (S) Installer --> Register Agent Toolsets as Cursor hooks
###     (S) Installer --> Configure and Start MCP Host Session
###     (S) Installer --> Deploy Guidance Instructions
###     (S) Installer --> Deploy Guidance Rules
###     (S) Installer --> Clean previously installed skills
###     (S) Installer --> Install While preserving skills from prior installed Skills
###     (S) Installer --> Install While preserving skills from other sources
###     (S) Installer --> Cleanse previously installed MCP tools
###     (S) Installer --> Install MCP to User Project Specific Location
###     (S) Installer --> Raise Error on Install Failure
##  (E) Install Practice Guidance Class
###     (S) Installer --> Deploy Practice guidance instructions
###     (S) Installer --> Deploy Practice guidance rules
###     (S) Installer --> Deploy Practice guidance fidelities
###     (S) Installer --> Deploy Practice guidance fidelity instructions
###     (S) Installer --> Deploy Practice guidance fidelity rules
##  (E) Install Action Classes
###     (S) Installer --> Install Lifecycle actions
###     (S) Installer --> Install Lifecycle actions as several tools
# (E) Deliver Verified Context
##  (E) Open Practice Catalog
###     (S) User --> Open Practice Catalog
####        Tests
                # tools/catalog_generator/catalog_spec.py
                with context("that have been built from the guidance registry")
                    with it("should write each practice guidance markdown property as HTML to its own page")
                    with it("should write each fidelity guidance markdown property as HTML to its own page")
                    with it("should not scrape deployed markdown files or heading structure from disk")
##  (E) Isolate Running Application
###     (S) User --> Capture Live Application
####        Tests
                # tools/context_setup/context_setup_spec.py
                with context("whose capture_from_live_app action is expanded")
                    with it("should instruct the AI to classify external dependencies")
                    with it("should mention the complex-stub trigger threshold")
                    with it("should write the complex-stub pre-pass as stub-focus-map.md not Stories story-map.md")
                    with it("should instruct the AI to write external stubs")
                    with it("should tell the AI to write global stubs under tests/stubs/{system}/")
                    with it("should tell the AI domain-owned stubs go on the aggregate")
                    with it("should forbid a domain folder inside tests")
                    with it("should scout under sandbox/extracted-context")
                    with it("should accept capture_repo on capture_from_live_app")
                    with it("should tell the AI to set capture_repo then call smoke_test with repo_path and surface")
                    with it("should list smoke_test as a tool to call")
                    with it("should list scout_app as a tool to call")
                    with it("should list complete_capture as a tool to call")
                    with it("should mention PASS WARN FAIL review verdicts")
                    with it("should list embed as the final indexing step")

                # tools/context_setup/context_setup_spec.py
                with context("whose capture_from_live_app action tool_steps are resolved")
                    with it("should include smoke_test")
                    with it("should include scout_app")
                    with it("should include complete_capture")
                    with it("should include embed from ContextIndex")
###     (S) Context Setup --> Classify External Dependencies
####        Tests
                # tools/context_setup/context_setup_spec.py
                with context("whose capture_from_live_app action is expanded")
                    with it("should instruct the AI to classify external dependencies")
###     (S) Context Setup --> Write Boundary Stubs
####        Tests
                # tools/context_setup/context_setup_spec.py
                with context("whose capture_from_live_app action is expanded")
                    with it("should instruct the AI to write external stubs")

                # tools/context_setup/context_setup_spec.py
                with context("whose capture_from_live_app action is expanded")
                    with it("should tell the AI to write global stubs under tests/stubs/{system}/")

                # tools/context_setup/context_setup_spec.py
                with context("whose capture_from_live_app action is expanded")
                    with it("should tell the AI domain-owned stubs go on the aggregate")
###     (S) Context Setup --> Smoke Test Application
####        Tests
                # tools/context_setup/context_setup_spec.py
                with context("whose smoke_test tool is given a running web server")
                    with it("should return a SmokeTestResult")
                    with it("should report passed=True when the root is reachable")
                    with it("should contain one ScreenResult for the probed path")
                    with it("should record status 200 for the root")
                    with it("should write an inventory file")
                    with it("should write the inventory under tests/stubs/")

                # tools/context_setup/context_setup_spec.py
                with context("whose smoke_test tool is probing a non-existent server")
                    with it("should return passed=False when the server is not reachable")
                    with it("should record status 0 for the unreachable path")

                # tools/context_setup/context_setup_spec.py
                with context("whose smoke_test tool probes multiple paths")
                    with it("should produce one ScreenResult per path")
                    with it("should mark all reachable paths as passed")
###     (S) Context Setup --> Scout Application Pages
####        Tests
                # tools/context_setup/context_setup_spec.py
                with context("whose scout_app tool captures pages from a running web server")
                    with it("should return a ScoutResult")
                    with it("should capture one PageCapture per entry point")
                    with it("should write a screenshot for each captured page")
                    with it("should write an aria.yaml for each captured page")
                    with it("should write the extraction-overview.md")
                    with it("should write capture under sandbox/extracted-context/app-extraction")
                    with it("should report the correct page count via page_count property")
                    with it("should list both page slugs via page_slugs property")
###     (S) Context Setup --> Complete Capture Pages
####        Tests
                # tools/context_setup/context_setup_spec.py
                with context("whose complete_capture tool adds a missing page to an existing capture")
                    with it("should return a CaptureResult")
                    with it("should add one new PageCapture for the missing page")
                    with it("should write a screenshot for the added page")
                    with it("should write an aria.yaml for the added page")
                    with it("should report total_page_count as scout count plus added count")
                    with it("should update the extraction-overview.md with the new page section")
##  (E) Scaffold Solution Outline
###     (S) User --> Open Capture Session
####        Tests
                NA — tools/workspace
###     (S) User --> Request Discovery Scaffold
####        Tests
                NA — actions/sketch
###     (S) Discoverer --> Confirm Practice Lenses
####        Tests
                # practices/stories/stories_spec.py
                with context("that resolves discovery stage to story_map")
                    with it("should default format to markdown")
                    with it("should select story_map")

                # practices/stories/stories_spec.py
                with context("whose contexts slot is expanded at story_map")
                    with it("should return non-empty prose")
                    with it("should include Shared rules and the story_map heading")
                    with it("should include the verb-noun-format rule slug")
                    with it("should omit other fidelity headings")
                    with it("should omit scenario-only rule slugs")

                # practices/ddd/ddd_spec.py
                with context("whose contexts instruction is expanded")
                    with it("should include the experts-words-preferred rule slug")
                    with it("should include the bc-by-lifecycle-not-ui-themes rule slug")
                    with it("should include the repository-is-collection-lifecycle rule slug")
                    with it("should include the shared-identity-is-generalisation rule slug")
                    with it("should include the hang-deps-on-owning-bc rule slug")
                    with it("should include the user-facing-system-first rule slug")
                    with it("should include the context-tree-bc-aggregate-concept rule slug")
                    with it("should include the link-arrow-target rule slug")
                    with it("should name the bounded_context fidelity")
###     (S) Stories --> Name Journey Stories
####        Tests
                NA — practices/stories
###     (S) Ddd --> Name Context Aggregates
####        Tests
                NA — practices/ddd
##  (E) Document Behavior Slice
###     (S) User --> Document Specification Slice
####        Tests
                NA — practices/cdd
###     (S) Specification --> Confirm Practice Lenses
####        Tests
                # practices/stories/stories_spec.py
                with context("whose contexts slot is expanded at scenarios")
                    with it("should include the gwt-steps-trace-to-domain-operations rule slug")
                    with it("should not include the retired behavioral-observable-outcomes slug")
                    with it("should include the and-chaining rule slug")
                    with it("should include the when-holds-the-operation rule slug")
                    with it("should include the given-only-what-the-system-checks rule slug")
                    with it("should include the seed-prior-story-as-given rule slug")
                    with it("should not include extract-assertion-helper at scenarios fidelity")
                    with it("should not include shared-example-fixtures at scenarios fidelity")
                    with it("should not include infrastructure-in-lifecycle-hooks at scenarios fidelity")
                    with it("should omit the story_map heading")
###     (S) Stories --> Capture Story Scenarios
####        Tests
                NA — practices/stories
###     (S) Ddd --> Capture Aggregate Operations
####        Tests
                NA — practices/ddd
##  (E) Prove Behavior Slice
###     (S) User --> Document Engineering Slice
####        Tests
                NA — practices/cdd
###     (S) Stories --> Write Story Tests
####        Tests
                # practices/stories/stories_spec.py
                with context("whose transform tool writes typescript under tests")
                    with it("should emit files under tests/")

                # practices/stories/stories_spec.py
                with context("whose contexts slot is expanded at acceptance_tests")
                    with it("should reference scenarios rules via deployed skill notation")
                    with it("should include acceptance_tests-only rule slugs")
                    with it("should not duplicate scenarios rule slugs as same-rule bullets")
                    with it("should omit the scenarios heading")
###     (S) Ddd --> Write Domain Wraps
####        Tests
                # practices/ddd/ddd_spec.py
                with context("whose transform tool is called")
                    with it("should delegate to CleanEngineering and return a dict")

                # practices/ddd/model/transformation/ddd_transformer_spec.py
                with description("DddTransformer")
                    with description("a code-format build")
                        with it("should write bounded-context.md in each context folder")
###     (S) Stories --> Run Story Tests
####        Tests
                NA — practices/bdd
##  (E) Review Captured Behavior
###     (S) User --> Review Story Meaning
####        Tests
                # actions/grill_context/grill_context_spec.py
                with context("grill action body")
                    with it("should include the grill_with_context body in grill")
                    with it("should prefer thinking questions over syntax trivia")
                    with it("should require grilling to validate the sketch when one is in play")
                    with it("should batch similar questions so the loop does not run forever")

                # actions/grill_context/grill_context_agent_spec.py
                with context("when the agent explores context files")
                    with it("should return ok from explore_context_files")
                    with it("should identify explore_context_files as the invoked tool")
                    with it("should return a non-empty result listing context files")
                    with it("should judge that the result looks like a JSON array of context file objects")
###     (S) User --> Accept Stage View
####        Tests
                # actions/sketch/sketch_spec.py
                with context("that pauses for sketch review")
                    with it("should return the sketch-review marker from review_sketch")
                    with it("should expose review_sketch as a tool")

                # actions/sketch_render/sketch_render_spec.py
                with context("render_approved_sketch")
                    with it("should be a non-blocking sub_agent in the manifest")
###     (S) User --> Log Behavior Mistake
####        Tests
                # tools/workspace/legacy/workspace_spec.py
                with context("that records a mistake on its open turn")
                    with it("should own the mistake on its open turn")
                    with it("should note the artifact path on that commit")
                    with it("should note the rule name on that commit")
                    with it("should note what was wrong on that commit")
                    with it("should note the original excerpt on that commit")
                    with it("should note the tool name on that commit")
                    with it("should note the fidelity on that commit")
###     (S) Eval --> Record Mistake Entry
####        Tests
                # tools/workspace/legacy/workspace_spec.py
                with context("that records a mistake on its open turn")
                    with it("should own the mistake on its open turn")
###     (S) User --> Log Behavior Correction
####        Tests
                NA — tools/workspace
###     (S) Eval --> Nest Correction Repair
####        Tests
                # actions/improvement/improvement_spec.py
                with context("when repair is expanded")
                    with it("should inline the repair.md recipe")
                    with it("should require a proposed kit change before any test")
                    with it("should tell the agent not to list tactical diffs")
                    with it("should keep the turn open until after fail-first")
##  (E) Cover Remaining Behavior
###     (S) User --> Advance Coverage Increment
####        Tests
                # actions/iterate/iterate_spec.py
                with context("that records an iterate tick")
                    with it("should return the iterate-tick marker")

                # actions/iterate/iterate_spec.py
                with context("that expands")
                    with it("should include the iterate session body in iterate")
###     (S) Stories --> Cover Distinct Behaviors
####        Tests
                NA — practices/stories
###     (S) User --> Request Session Handoff
####        Tests
                NA — tools/handoff
###     (S) Handoff --> Write Handoff Document
####        Tests
                # tools/handoff/handoff_spec.py
                with it("should expose write_handoff tool and handoff_session action")

                # tools/handoff/handoff_spec.py
                with it("should call write_handoff when running the handoff_session action")

                # tools/handoff/handoff_spec.py
                with description("write_handoff")
                    with context("given a workspace with an active session folder")
                        with it("should write a file named handoff-{timestamp}.md in the session folder")
                        with it("should write the content verbatim")
                        with it("should return the absolute path of the written file")
                    with context("given a workspace with no active session")
                        with it("should create a fallback session folder and write the file there")
                        with it("should not write a handoff-latest.md")

---

## Scope boundary

**In scope:** The repeatable path a person uses to get verified context for an existing application. Install publishes skills, rules, commands, the MCP manifest, and hooks, then the catalog is opened. Context Setup isolates the running app. Stories and Ddd scaffold the outline, document one slice, and prove that slice with story tests and domain wraps. The person reviews meaning, accepts the stage, and logs a mistake and its correction. The next increment covers another distinct behavior, and Handoff writes the session handoff.

**Out of scope:** The one-time repository clone. The toolset authoring spine in `harness/.context/story-map.md`. Scenario text, acceptance-test code, and domain class bodies. Clean Engineering, BDD, Diagnose, and workflow tickets, which the strategy names as available and leaves off this path.
