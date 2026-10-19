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

**Sources / context:** `README.md` (install, practice plus action plus optional format, discovery / specification / implementation); `.context/principles/context-as-code-strategy.md` (sandbox, scaffold, document one slice, tests until green, human review, next increment); `practices/cdd/agents/context.md`, `discovery.md`, `specification.md`, `implementation.md`; `.context/module-context.md` (Installer, Context Setup, Stories, Ddd, Handoff, Eval); `tools/context_setup/.context/module-context.md`; `tools/context_setup/.context/cdr/0001-plain-toolset-not-context-domain.md`; `tools/context_setup/context_setup.py`; `tools/context_setup/context_index.py`; `tools/context_setup/context_setup_spec.py`; `tools/context_setup/context_index_spec.py`.

**Evidence:** Inferred from those sources. No live session was walked in this pass, so none of these nodes are marked observed. Context-setup nodes are inferred from the operations and action recipes in `context_setup.py` and `context_index.py`, and from the specs that assert those recipes and tool results. They are not observed, because this pass did not run a capture or an ask. Intended where a role prompt prescribes a confirm-or-handoff step the strategy does not show as a separate command.

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
###     (S) Installer --> Diagnose the finished install
##  (E) Install Practice Guidance Class
###     (S) Installer --> Deploy Practice guidance instructions
###     (S) Installer --> Deploy Practice guidance rules
###     (S) Installer --> Deploy Practice guidance fidelities
###     (S) Installer --> Deploy Practice guidance fidelity instructions
###     (S) Installer --> Deploy Practice guidance fidelity rules
##  (E) Install Action Classes
###     (S) Installer --> Install Lifecycle actions
###     (S) Installer --> Install Lifecycle actions as several tools
# (E) Open Work Session
##  (E) Open Named Work Session
###     (S) WorkSession --> Open Work Session Folder
###     (S) WorkSession --> Load Work Session Guidance
###     (S) WorkSession --> Hold Open Turn
###     (S) WorkSession --> Remember Completed Turns
##  (E) Announce Work Session Turn
###     (S) WorkSession --> Announce Work Session Turn
###     (S) Turn --> Commit Current Checkout
###     (S) Turn --> Record Turn Commit
###     (S) Turn --> Record Mistake
###     (S) Turn --> Record Correction
##  (E) Record Work Session Rules
###     (S) WorkSession --> Add Work Session Rule
###     (S) WorkSession --> Attach Mistake And Correction
###     (S) WorkSession --> Raise Work Session Rule Star
###     (S) WorkSession --> Inject Work Session Rules
###     (S) WorkSession --> Write Last Chat Injected Rules
##  (E) Hold Process Session
###     (S) Session --> Hold Knowledge Graph
###     (S) Session --> Hold Practice Guidance
###     (S) Session --> Reset Process Session
###     (S) Session --> Persist Session Across Hook Runs
###     (S) Session --> Hold Session On Mcp Server
# (E) Deliver Verified Context
##  (E) Open Practice Catalog
###     (S) User --> Open Practice Catalog
####        Tests
                # harness/catalog_generator/catalog_spec.py
                with context("that have been built from the guidance registry")
                    with it("should write each practice guidance markdown property as HTML to its own page")
                    with it("should write each fidelity guidance markdown property as HTML to its own page")
                    with it("should not scrape deployed markdown files or heading structure from disk")
##  (E) Prepare Context Index
###     (S) Context Setup --> Convert Documents To Markdown
###     (S) Context Setup --> Review Document Structure
###     (S) User --> Choose Indexer Practices
###     (S) Context Setup --> Partition Selected Context
###     (S) Context Index --> Embed Segment Files
###     (S) Context Index --> Search Ranked Chunks
###     (S) Context Index --> Answer Question With Citations
##  (E) Isolate Running Application
###     (S) User --> Capture Live Application
###     (S) Context Setup --> Classify External Dependencies
###     (S) Context Setup --> Write Stub Focus Documents
###     (S) Context Setup --> Write Boundary Stubs
###     (S) Context Setup --> Smoke Test Application
###     (S) Context Setup --> Smoke Test Desktop Process
###     (S) Context Setup --> Scout Application Pages
###     (S) Context Setup --> Review Capture Verdicts
###     (S) Context Setup --> Complete Capture Pages
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

**In scope:** The repeatable path a person uses to get verified context for an existing application. Install publishes skills, rules, commands, the MCP manifest, and hooks. A Work Session then opens under `.sessions`, announces turns, and records work-session rules; a process Session holds the knowledge graph and practice guidance. Then the catalog is opened. Context Setup converts a document folder to markdown, notes flat structure, partitions through the practices the person selects, and embeds a Context Index. It also isolates a running application: classify external dependencies, write stub-focus documents when the complex-stub trigger fires, write boundary stubs, smoke-test web and desktop surfaces, scout pages, review PASS, WARN, and FAIL verdicts, and complete capture for pages that did not pass. Context Index embeds segment files, searches ranked chunks, and answers a question with citations. Stories and Ddd scaffold the outline, document one slice, and prove that slice with story tests and domain wraps. The person reviews meaning, accepts the stage, and logs a mistake and its correction. The next increment covers another distinct behavior, and Handoff writes the session handoff.

**Out of scope:** The one-time repository clone. The toolset authoring spine in `harness/.context/story-map.md`. Scenario text, acceptance-test code, and domain class bodies. Clean Engineering, BDD, Diagnose, and workflow tickets, which the strategy names as available and leaves off this path.
