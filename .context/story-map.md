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

**Sources / context:** `README.md` (install, practice plus action plus optional format, discovery / specification / implementation); `.context/principles/context-as-code-strategy.md` (sandbox, scaffold, document one slice, tests until green, human review, next increment); `cdd_guidance/agents/context.md`, `discovery.md`, `specification.md`, `implementation.md`; `.context/module-context.md` (Installer, Context Setup, Stories, Ddd, Handoff, Eval); `cdd_guidance/context_setup/.context/module-context.md`; `cdd_guidance/context_setup/.context/cdr/0001-plain-toolset-not-context-domain.md`; `cdd_guidance/context_setup/context_setup.py`; `cdd_guidance/context_setup/context_index.py`; `cdd_guidance/context_setup/context_setup_heavy_spec.py`; `cdd_guidance/context_setup/context_index_spec.py`; `space/session/session.py`; `space/session/session_spec.py`; `space/session/session-sketch.md`; `space/session/.context/session-context.md`; `space/repo/repo.py`; `space/repo/repo_heavy_spec.py`, `space/repo/worktree_spec.py`; `space/repo/.context/module-context.md`; `harness/guidance/guidance.py` (`PracticeGuidance` does not load a graph).

**Evidence:** Install and context-setup nodes are inferred from those sources. No live capture was walked for them. Open Work Session nodes are observed from the examples in `space/session/session_spec.py` and the operations in `space/session/session.py`. `Session.practice(name)` returns the session's one instance of the practice, which the session's graph holds. Work With Repo Branch and Work With Repo Worktree are observed from `space/repo/repo_heavy_spec.py`, `space/repo/worktree_spec.py` and the branch, worktree, and push operations on `space.repo.repo:Repo`.

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
##  (E) Open Named Session
###     (S) Session --> Open New Session
###     (S) Session --> Select Existing Session
###     (S) Session --> Open Session Loop
###     (S) Session --> Remember Practice Folders
##  (E) Record Session Log
###     (S) Session --> Record Session Action
###     (S) Session --> Record Validation Run
###     (S) Session --> Attach Action Chat
###     (S) Session --> Record Session Error
##  (E) Hold Process Session
###     (S) Session --> Load Practice Guideline
###     (S) Session --> Reset Process Session
###     (S) Session --> Persist Hook Session
###     (S) Session --> Hold Mcp Session
##  (E) Work With Repo Branch
###     (S) Repo --> Switch Branch
###     (S) Repo --> Create Branch
###     (S) Repo --> Close Branch
###     (S) Repo --> Merge Branch
###     (S) Repo --> Commit Branch
###     (S) Repo --> Push Branch
##  (E) Work With Repo Worktree
###     (S) Repo --> List Worktree
###     (S) Repo --> Open Worktree
###     (S) Repo --> Reuse Worktree
###     (S) Repo --> Remove Worktree
###     (S) Repo --> Fetch Worktree
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

                NA — no spec writes `.context/bounded-context.md` today; DDD reads it (`practices/ddd/model/graph_reading.py`)
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

                # actions/grill_context/grill_context_spec.py
                with context("explore_context_files tool")
                    with context("that names no folder")
                        with it("should scan the session's root")
                    with context("that scans a root containing a context-named file")
                        with it("should return that file with kind context-named")
###     (S) User --> Accept Stage View
####        Tests
                # actions/sketch/sketch_spec.py
                with context("that pauses for sketch review")
                    with it("should return the sketch-review marker from review_sketch")
                    with it("should expose review_sketch as a tool")

                # actions/render/render_spec.py
                with description("Render")
                    with it("should read a sketch from a file path and leave the document body off the call")
###     (S) User --> Log Behavior Mistake
####        Tests
                NA — no spec; the retired workspace toolset recorded mistakes, and nothing records them today
###     (S) Eval --> Record Mistake Entry
####        Tests
                NA — no spec; the retired workspace toolset recorded mistakes, and nothing records them today
###     (S) User --> Log Behavior Correction
####        Tests
                NA — tools/workspace
###     (S) Eval --> Nest Correction Repair
####        Tests
                # actions/improvement/improvement_spec.py
                with context("that is expanded for repair")
                    with it("should inline the repair.md recipe")
                    with it("should require a proposed toolset change before any test")
                    with it("should tell the agent not to list tactical diffs")
                    with it("should keep the turn open until after fail-first")
##  (E) Cover Remaining Behavior
###     (S) User --> Advance Coverage Increment
####        Tests
                # actions/iterate/iterate_spec.py
                with context("that marks an iterate cycle due")
                    with it("should return the iterate-round marker")

                # actions/iterate/iterate_spec.py
                with context("that expands")
                    with it("should include the iterate session body in iterate")
###     (S) Stories --> Cover Distinct Behaviors
####        Tests
                NA — practices/stories
###     (S) User --> Request Session Handoff
####        Tests
                NA — space/session
###     (S) Handoff --> Write Handoff Document
####        Tests
                # space/session/handoff_spec.py
                with description("a session's handoff tools")
                    with it("should offer write_handoff as a tool")
                    with it("should offer handoff_session as instructions")
                    with it("should call write_handoff when running the handoff_session instructions")

                # space/session/handoff_spec.py
                with description("a session writing a handoff")
                    with context("with a project whose current session is named")
                        with it("should write a file named handoff-{timestamp}.md in that session's folder")
                        with it("should write the content verbatim")
                        with it("should return the absolute path of the written file")
                        with it("should not write a handoff-latest.md")
                    with context("with a project that has no named current session")
                        with it("should write into the main session folder")

---

## Scope boundary

**In scope:** The repeatable path a person uses to get verified context for an existing application. Install publishes skills, rules, commands, the MCP manifest, and hooks. A Work Session then opens under `.sessions`, announces turns, and records work-session rules; a process Session holds the knowledge graph and practice guidance. That same session works the repository: switch, create, close, merge, commit, and push a branch, and list, open, reuse, remove, and fetch a worktree. Then the catalog is opened. Context Setup converts a document folder to markdown, notes flat structure, partitions through the practices the person selects, and embeds a Context Index. It also isolates a running application: classify external dependencies, write stub-focus documents when the complex-stub trigger fires, write boundary stubs, smoke-test web and desktop surfaces, scout pages, review PASS, WARN, and FAIL verdicts, and complete capture for pages that did not pass. Context Index embeds segment files, searches ranked chunks, and answers a question with citations. Stories and Ddd scaffold the outline, document one slice, and prove that slice with story tests and domain wraps. The person reviews meaning, accepts the stage, and logs a mistake and its correction. The next increment covers another distinct behavior, and Handoff writes the session handoff.

**Out of scope:** The one-time repository clone. The toolset authoring spine in `harness/.context/story-map.md`. Scenario text, acceptance-test code, and domain class bodies. Clean Engineering, BDD, Diagnose, and workflow tickets, which the strategy names as available and leaves off this path.
