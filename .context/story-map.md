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

# Story Map — Context-Driven Delivery Framework

**Sources / context:** `harness/.context/module-context.md`; `harness/agent_tools/.context/module-context.md`; `harness/agent_tools/.context/agent-tools-model.md`; `harness/markdown/.context/module-context.md`; `installation/.context/installer-deployed-model.md`; `harness/hooks/.context/module-context.md`; `harness/guidance/guidance.py`; `harness/.context/context-tool-resource-model-om-bdd.md`; `harness/mcp/.context/module-context.md`; `actions/.context/module-context.md`; `practices/.context/module-context.md`; user spine: register agent toolsets → install markdown files (skill, slash command, rules) and MCP → invoke those → use context guidance (install skills and .mdc, invoke instructions, generate under rules) → use practice guidance (register guidance and fidelities, invoke practice and fidelity, shared and fidelity rules constrain output) → hook dispatch → extract markdown → lifecycle actions. CDD Kanban and Chat Bar: the CDD Kanban map, once `space/kanban/.context/story-map.md`, now kept here; `harness/chat-ui/.context/story-map.md` and `story-map.drawio`; the ticket enhancements on the session-board branch (`.sessions/session-board/ticket-enhancements.md`, removed with that session in commit 8483f7a40 and read from commit b08bfe47e; its `space/kanban/.context/story-map.md`); `harness/chat-ui/.context/cdr/0001-stage-strip-band.md`; `space/kanban/app/src/session-board/board-update.ts`; the ticket drawing `harness/.context/ux/ticket-ui.drawio` (2026-11-11), which supplements the design canvas for parent and child tickets; `harness/chat-ui/pane/hooks/register.ts`. The map also takes in the backlog items `.sessions/_backlog/maintain-tickets-on-board.md`, `.sessions/_backlog/guard-work-and-recover-fast.md` and `.sessions/_backlog/guard-work-and-recover-fast.md` as Intended stories. The prompt queue epic: the simple-queue chat of 2026-11-16 and the `prompt-queue` mod. The Review End-To-End Screens epic: the e2e-testing ticket (`.sessions/e2e-testing/e2e-testing.md`), `cdd_guidance/practices/tdd/tdd.md` (Flow A, Cadence), `harness/release/test_runs.py`, and pml-web's `test-utils/legacy-compare/` (`report.ts`, `story-legacy-compare.ts`, `release-baseline.ts`, `end-to-end-paths.ts`).

**Evidence:** Observed behaviour is cited from those files. Intended: practice guidance and fidelity guidance declare real `@hook` events from `CURSOR_EVENTS`, and lifecycle actions use the same mark-and-install path as practice guidance. For the CDD Kanban and Chat Bar epics: **Observed** means the code and its specs or tests do it today, **Inferred** means the code does it but nothing presses it, **Intended** means a source asks for it and the code does not do it yet, and **Requested** means the person asked on 2026-11-06 for each channel to do what the other does. In `story-map.drawio`, a story whose evidence is only Intended or Requested is filled a lighter yellow than one the code does today.

---

The map reads in the order the work happens: authors register and install toolsets, guidance and actions; people deliver work with context guidance through slash commands, skills and MCP; then people move work forward through two channels, the CDD Kanban and the Chat Bar. Each channel has its own epic and its own stories, because the two surfaces draw and behave differently even when they call the same `ticket.*`, `board.*`, `fidelity-progress.*` and `session.*` tools.

# (E) Register And Install Toolsets

## (E) Register Agent Toolsets

### (S) Author --> Register Agent Toolsets
### (S) Author --> Register Agent Operations
### (S) Author --> Register Agent Tools
### (S) Author --> Register Agent Instructions
### (S) Agent Toolset --> Validate Instruction Body

## (E) Register Guidance And Actions

### (S) Author --> Register Guidance
### (S) Author --> Register Fidelities
### (S) Author --> Register Action Tools
### (S) Author --> Register Action Prompt
### (S) Agent Instructions --> Build Instruction Expansion
### (S) Agent Instructions --> Collect Deferred Tools

## (E) Install Markdown Files

### (S) File Installation --> Publish Markdown Files
### (S) File Installation --> Publish Guidance Files
### (S) Installer --> Publish Action Command
### (S) Installer --> [Store Install State](../story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md#story-store-install-state)
### (S) Person --> [Choose Where To Install](../story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md#story-choose-where-to-install)

Observed (2026-11-19, `scripts/install.py`, `harness/installation/ide_layout.py`, `install_target.py`): the IDE is named in any case; a name that is no IDE is refused with the names it can be (`UnknownIde`), and a path that is a file, is empty, or is a chat's unknown folder is refused before anything is written (`NotAnInstallFolder`).

### (S) Person --> [Refresh The Installer's Own Commands](../story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md#story-refresh-the-installers-own-commands)

Observed (2026-11-19, `scripts/install.py --self`, `Installer.install`): the install and clean commands are written again over a finished install, and the record still lists every file that install wrote, so a clean removes them (`InstallRecord.adopt`).

### (S) Person --> [Install The Latest Release](../story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md#story-install-the-latest-release)

Observed (2026-11-19, `scripts/install.py` `_install_from_latest`, `_match_release_version`): installing from the latest release puts a locally edited, uncommitted version line back to the release's and keeps a committed version that is past the release.

### (S:system) Installer --> [Publish Mods For Every Chat](../story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md#story-publish-mods-for-every-chat)

Observed (2026-11-19, `harness/mcp/claude_marketplace.py` `ClaudeMarketplace.publish_mods`): one install at a time publishes the mods into the cdd home's marketplace, its `claude-plugins` folder, holding an `InstallLock`, so an install from the main checkout and one from a ticket's worktree at the same moment both finish.

Built (2026-11-24, commits b123d6925, fa6062c9b; `installer_heavy_spec.py` "installing a cdd plugin", `cdd_home_lanes_heavy_spec.py` "should have Claude Code load the mods of the code the dev lane serves"), not seen: Claude Code loads every cdd plugin from the cdd home's fixed folder, `~/.cdd/chat-plugins/{name}`, which `CLAUDE_CODE_PLUGIN_DIRS` names once; each install and repin points that folder at the folder the approved lane publishes the mod into (a junction on Windows), so the settings never change after the first time and a repin and a reload of the plugins reach every chat. Every cached copy Claude Code holds of a cdd plugin is uninstalled, as a cached copy keeps the version it was installed at (a chat kept a queue bar with no Flush after the mod gained one). An install that serves a feature on the dev lane loads that lane's mods. Scenarios: Load Each Cdd Plugin From The Cdd Home's Fixed Folder, Follow The Approved Lane On A Repin Without Changing The Settings, Take Away A Cached Copy Of A Cdd Plugin, Load The Mods Of The Code The Dev Lane Serves.

## (E) Install MCP And Hook Manifests

### (S) Mcp Installation --> Record Mcp Operation
### (S) Mcp Installation --> Publish Mcp Manifest
### (S) Author --> Register Hook Event
### (S) Hook Installation --> Publish Hooks Manifest

## (E) Serve CDD Code In Lanes

Intended (requested 2026-11-16; `harness/mcp/.context/cdr/0003-two-lanes-main-stable-features-dev.md`): the stable lane runs main for chats in a main checkout, and every other session is in the dev lane by default, which runs the one served feature pinned straight from its branch.

### (S:system) CDD Server --> [Choose The Lane For A Project](../story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/choose-the-lane-for-a-project/choose_the_lane_for_a_project_story.test.py)
### (S) Person --> [Install Into The Lane Of The Checkout](../story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/install-into-the-lane-of-the-checkout/install_into_the_lane_of_the_checkout_story.test.py)
### (S) Person --> [Serve A Feature Branch On The Dev Lane](../story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/serve-a-feature-branch-on-the-dev-lane/serve_a_feature_branch_on_the_dev_lane_story.test.py)
### (S:system) CDD Server --> [Send A Dev-Lane Chat's Calls To The Dev Lane](../story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/send-a-dev-lane-chats-calls-to-the-dev-lane/send_a_dev_lane_chats_calls_to_the_dev_lane_story.test.py)
### (S) Person --> Switch The Served Feature After Other Chats Agree
### (S:system) CDD Server --> [Serve Dev Lane Apps On Their Own Ports](../story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/serve-dev-lane-apps-on-their-own-ports/serve_dev_lane_apps_on_their_own_ports_story.test.py)
### (S:system) CDD Server --> [Keep A Lane's Server Running After Its Chat Ends](../story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/keep-a-lanes-server-running-after-its-chat-ends/keep_a_lanes_server_running_after_its_chat_ends_story.test.py)

# (E) Deliver Work With Context Guidance

A practice is a lens on the work (Stories, DDD, UX, Clean Engineering, BDD), a fidelity is how deep that lens goes, and an action is what you do with it. A person composes the three into one command; the agent loads that practice's guidance at that fidelity and uses it to turn source material into context, shape the solution, produce the formal artifacts, and check them against the same rules. Sources: `catalog/workflow.md`, `cdd_guidance/actions/.context/module-context.md`, `.context/cdd-approach.md`.

## (E) Invoke Guidance Through Slash Commands

### (S) Person --> Compose Practice Action Fidelity Command

Observed: `/{practice} /{action} /{fidelity}`, such as `/stories /sketch /discovery`, or the fidelity's own skill such as `/practices-stories-stories-story-map` (`catalog/workflow.md` "How to use them").

### (S) Agent --> Load Practice Fidelity Instructions

Observed: the skill or MCP tool returns the practice's overview and guidance, its shared rules, the fidelity's rules, template and examples, all read from the markdown kept beside the practice's class, so a practice is one class plus the words the agent follows (`harness/.context/module-context.md`; `harness/markdown`).

### (S) Agent --> [Call CDD Tool Through MCP](../story_tests/deliver-work-with-context-guidance/invoke-guidance-through-slash-commands/invoke_guidance_through_slash_commands_story.test.md#story-call-cdd-tool-through-mcp)

Observed: a skill or slash command that says "Use MCP tool" runs that operation on the cdd server, and a failed call stops the work and says what failed rather than falling back to a shell (`.claude/rules/mcp-fail-loud.md`). Observed (2026-11-23, commit b609c986e, `harness/mcp/tool_calls.py`): a call still running at its time limit keeps running and its caller is told so; the same call made again, however late, is answered with that run's result or its failure, never "still running" again (`harness/mcp/tool_calls_spec.py`).

### (S) Agent --> Guide Output With Matching Rules

Observed: installed rule files steer what the agent writes while it writes: always-apply rules such as `coding.md` on every turn, a practice's shared rules and a fidelity's rules whenever the agent touches a file their `paths` match, such as `stories-story-map.md` for `*story-map*` (`harness/installation/files.py`). Validate later checks the output against the same rules.

## (E) Turn Source Material Into Context

### (S) Agent --> Index Source Into Lens Segments

Observed: `/partition` splits handbooks, specs or code into an index plus verbatim segments for one practice's lens, and fails a chunk that drops a named entry the index requires (`actions/partition`).

### (S) Agent --> Add Lens To Existing Index

Observed: partitioning the same source through another practice adds that lens's columns and segments to the existing index; nothing already there is wiped (`catalog/workflow.md` Scenario 1).

### (S) Agent --> [Describe Existing Artifacts](../story_tests/deliver-work-with-context-guidance/turn-source-material-into-context/turn_source_material_into_context_story.test.md#story-describe-existing-artifacts)

Observed: `/document` records what code, tests or docs already do for the listed guidance, flagging violations without correcting them, so context for an existing system is not an invented design (`actions/document`).

### (S) Agent --> Capture Documents Into Searchable Context

Observed: `partition.partition` converts a folder of documents to markdown with `context-setup.convert`, partitions them through the practices it is given, and embeds the segments into one index that `context-index.ask` answers from with citations.

### (S) Agent --> Capture Live App Context

Observed: `context-setup.capture_from_live_app` scouts a running web, desktop or API application and saves each page's screenshot and accessibility tree as context.

## (E) Shape The Solution With Context

### (S) Agent --> Grill Plan Against Context

Observed: `/grill` asks one framed question at a time, grounded in files the agent has read, and writes each resolved answer to `grill-answers.md` (`actions/grill_context`).

### (S) Agent --> Sketch Rough Draft

Observed: `/sketch` grills the open decisions and saves a rough draft to a sketch file after each refinement, so the shape is agreed before the formal artifact exists (`actions/sketch`).

### (S) Agent --> Iterate One Slice At A Time

Observed: `/iterate` grills, generates one small slice, validates and fixes it, and asks for feedback before the next slice, instead of producing the whole artifact at once (`actions/iterate`).

### (S) Agent --> Record Context Decision

Observed: `record-decisions.write_cdr` writes a decision record under the session workpath's `.context/cdr/`, so why the solution took its shape stays with the context.

## (E) Produce Formal Artifacts

Grouped on 2026-11-24 into four sub-epics, as splitting its stories into stories of seven scenarios or fewer took it past nine: Generate Fidelity Artifacts, Render Artifacts Into Other Formats, Take Practice Artifacts To Other Formats And Back, and Take UX Artifacts To Other Formats And Back.

### (E) Generate Fidelity Artifacts

The agent writes each listed guidance's artifact at its fidelity, from the fidelity before it, and records the test tiers of the modules it writes tests for. Grouped on 2026-11-24 from Produce Formal Artifacts.

#### (S) Agent --> [Generate Fidelity Artifact](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/generate-fidelity-artifacts/generate_fidelity_artifacts_story.test.md#story-generate-fidelity-artifact)

Observed: `/generate` writes each listed guidance's artifact at its fidelity, such as a story map, a class model or acceptance tests, into the session workpath's `.context/` or code folder, then validates what it wrote (`actions/generate`).

#### (S) Agent --> Generate From Previous Fidelity

Observed: generating a fidelity reads the artifact of the fidelity before it, such as scenarios from the story map, and when the two use different formats the earlier one is rendered into the new format first (`Ticket.generate_commands`; `catalog/workflow.md` Scenario 1).

#### (S) Agent --> Generate Several Practices In One Command

Observed: one action with several guidance names produces every practice's artifact at the same depth, such as Stories, Clean Engineering, UX and DDD at specification (`catalog/workflow.md` Scenario 3).

#### (S) Agent --> [Record Test Tiers Of Module](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/generate-fidelity-artifacts/record_test_tiers_of_module_story.test.md#story-record-test-tiers-of-module)

Requested (2026-11-22, change 6 of the defect analysis: "the tiers in use are tracked in session.json, for each module", filled by "the appropriate generate or render command"); Built (2026-11-22): a generate or a render at Stories acceptance tests or BDD development records in the session's `session.json` the test tiers of the module it writes tests for, each with its test tool: unit by default, server and web once a test file of that tier is there. Where it cannot tell the module, the tool, or whether the module needs the server or web tier, its reply asks the agent to decide and record it with `session.record_test_tier` (`space/session/test_tiers.py`, `cdd_guidance/practices/tdd/module_tiers.py`).

#### (S) Agent --> [Record Decided Test Tier](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/generate-fidelity-artifacts/record_test_tiers_of_module_story.test.md#story-record-decided-test-tier)

Built (2026-11-22): the agent records the tier it decided with `session.record_test_tier`, which refuses a tier that is none of unit, server and web, a tier with no test tool and a record that is wrongly shaped, keeps the tool the agent recorded when a later render looks again, and reports a recorded module whose folder is gone (`space/session/test_tiers.py`). Split from Record Test Tiers Of Module on 2026-11-24.

### (E) Render Artifacts Into Other Formats

The agent turns an artifact already generated into another format on the same guidance and saves it where the fidelity declares it, without losing what a file already there holds. Grouped on 2026-11-24 from Produce Formal Artifacts.

#### (S) Agent --> [Render Artifact Into Another Format](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/render-artifacts-into-other-formats/render_artifacts_into_other_formats_story.test.md#story-render-artifact-into-another-format)

Observed: `/render` turns an artifact already generated into another format on the same guidance, such as a markdown story map into drawio, reading the source's format from its name, and refuses an empty file, a path outside the session's root, and a format the fidelity declares no file in (`actions/render`).

#### (S) Agent --> [Save Rendered Artifact Where Its Fidelity Declares It](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/render-artifacts-into-other-formats/render_artifacts_into_other_formats_story.test.md#story-save-rendered-artifact-where-its-fidelity-declares-it)

Observed (`cdd_guidance/actions/render/render.py`): a render is saved beside its source under the name the fidelity writes that format to, or the source's own name, and a render that saves nothing answers with its content and where the fidelity declares it. Split from Render Artifact Into Another Format on 2026-11-24.

#### (S) Agent --> [Render Story Tests For Each Story](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/render-artifacts-into-other-formats/render_artifacts_into_other_formats_story.test.md#story-render-story-tests-for-each-story)

Observed: a render of scenarios to code saves one story test for each story the named file holds, where the fidelity declares it, importing the step library by its path from the story test's folder, and a folder of story tests renders back to a scenarios file for each story. Split from Render Artifact Into Another Format on 2026-11-24.

#### (S) Agent --> [Render Onto File Already There](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/render-artifacts-into-other-formats/render_artifacts_into_other_formats_story.test.md#story-render-onto-file-already-there)

Observed: a render onto a story test or a document already there writes the changed scenarios and loses nothing, changes nothing when rendered again, leaves a step library a person changed as it is, and hands what the source no longer holds to the agent to decide. Split from Render Artifact Into Another Format on 2026-11-24.

### (E) Take Practice Artifacts To Other Formats And Back

An artifact of Stories, Clean Engineering, BDD or DDD rendered to another format and rendered back keeps what a person wrote. Grouped on 2026-11-24 from Produce Formal Artifacts.

#### (S) Agent --> [Take Artifact To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_artifact_to_another_format_and_back_story.test.md#story-take-artifact-to-another-format-and-back)

Observed (2026-11-19, the practices' format adapters under `cdd_guidance/practices/stories/model`, `clean_engineering/model` and `ddd/model`): an artifact rendered to another format and rendered back keeps what a person wrote: a story comes back under the sub-epic its cell names, and the prose a drawing cannot show is kept in the drawing. Split from Render Artifact Into Another Format, whose scenarios say where a render is saved. Intended: the scenarios in the story's file that name the evidence still missing.

#### (S) Agent --> [Take Class Model To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_artifact_to_another_format_and_back_story.test.md#story-take-class-model-to-another-format-and-back)

Observed (`cdd_guidance/practices/clean_engineering/model`): a class model taken through draw.io or code and back gains no relationship nobody wrote, keeps its classes' notes and calls, spells types in the language it is rendered to, and is saved in each module's own file. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take Module Cards To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_artifact_to_another_format_and_back_story.test.md#story-take-module-cards-to-another-format-and-back)

Observed: module cards come back from their drawing as the person wrote them, and a modules whiteboard is read back with only the modules a person wrote. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take BDD Specs To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_artifact_to_another_format_and_back_story.test.md#story-take-bdd-specs-to-another-format-and-back)

Observed (`cdd_guidance/practices/bdd`): a finished spec comes back from another language as it was written, keeping its observations' order, nested states and call graphs; a realization sketch is read and written in the sketch template's notation; and BDD offers only the formats it reads, renders and checks. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take Domain Documents To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_domain_documents_to_another_format_and_back_story.test.md#story-take-domain-documents-to-another-format-and-back)

Observed (`cdd_guidance/practices/ddd/model`; exploratory-testing defects widget-20, r3-bolt-03): a bounded-context map and a domain model keep every line a person wrote when read and written again, and when a drawing is written back over them or with no markdown beside it; a domain model rendered to code is saved in each aggregate's own file. Its scenarios were written before the story was on the map; it was put on the map on 2026-11-24, with the two scenarios about domain models from Take Artifact To Another Format And Back.

#### (S) Agent --> [Keep Aggregate Links Through Another Format](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_domain_documents_to_another_format_and_back_story.test.md#story-keep-aggregate-links-through-another-format)

Observed: the arrows between aggregates are read back from a domain model's drawing and drawn again from the markdown, an integration whose arrow a person removed is left out, and a bounded context's file names each aggregate as a link to the domain model, keeping what a person wrote. Split from Take Domain Documents To Another Format And Back on 2026-11-24.

### (E) Take UX Artifacts To Other Formats And Back

A UX map, a mockup and a view rendered to another format and rendered back keep what a person wrote. Grouped on 2026-11-24 from Produce Formal Artifacts; its scenarios were headed under Take Artifact To Another Format And Back.

#### (S) Agent --> [Take UX Map To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-ux-artifacts-to-other-formats-and-back/take_ux_map_to_another_format_and_back_story.test.md#story-take-ux-map-to-another-format-and-back)

Observed (`cdd_guidance/practices/ux/model`; exploratory-testing defects r3-gizmo-01, 02): the UX context and the UX map's drawing each keep what the other cannot hold, and a drawing is read back with its stories, domain terms, layouts, areas and kinds of navigation. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take Mockup Drawing To Another Format And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-ux-artifacts-to-other-formats-and-back/take_ux_map_to_another_format_and_back_story.test.md#story-take-mockup-drawing-to-another-format-and-back)

Observed: a mockup's drawing is saved beside its board, shows what each screen and control serves, and is read back with its controls in their own regions. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take Mockup To Claude Whiteboard And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-ux-artifacts-to-other-formats-and-back/take_ux_map_to_another_format_and_back_story.test.md#story-take-mockup-to-claude-whiteboard-and-back)

Observed: a mockup's board shows what each screen and control serves and is read back with it, reading a control where a person moved its card and keeping where a person put a screen. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take Mockup To Claude Design Canvas And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-ux-artifacts-to-other-formats-and-back/take_ux_map_to_another_format_and_back_story.test.md#story-take-mockup-to-claude-design-canvas-and-back)

Observed: a mockup goes to a Claude Design canvas and back, a canvas missing a screen's prototype page is refused, and a published canvas and a screen people ported are left as they are. Split from Take Artifact To Another Format And Back on 2026-11-24.

#### (S) Agent --> [Take View Code To Another Language And Back](../story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-ux-artifacts-to-other-formats-and-back/take_ux_map_to_another_format_and_back_story.test.md#story-take-view-code-to-another-language-and-back)

Observed: the front-end code fidelity starts in a format it writes, a view renders between TypeScript and JavaScript both ways onto the file a person wrote into, losing nothing, and a render that cannot hold the view, or between a view and a UX map, is refused. Split from Take Artifact To Another Format And Back on 2026-11-24.

## (E) Check Artifacts Against Rules

### (S) Agent --> [Validate Artifact Against Rules](../story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md#story-validate-artifact-against-rules)

Observed: `/validate` runs the practice's graph rules over the files and judges every rule Pass or Fail without editing, then saves the report, which the board and chat bar read (`actions/validate`).

### (S) Agent --> [Read Validated Files As Their Practice Writes Them](../story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md#story-read-validated-files-as-their-practice-writes-them)

Observed (exploratory-testing round 3, defects r3-rivet-10, r3-sparky-10, r3-sparky-04): validate reads each file as its practice writes it: a spec's describes however it quotes them, a story test validated alone at the place its story map gives it, and a markdown scenarios file's examples without asking for an examples file. Split from Validate Artifact Against Rules on 2026-11-24.

### (S) Agent --> Satisfy Violations Until Clean

Observed: `/satisfy` validates, fixes every reported violation in the artifact, and validates again until it passes (`actions/satisfy`).

### (S) Agent --> Repair Guidance Behind Violation

Intended (increment 5, Repair Guidance From Mistakes; the person, 2026-11-11: not built yet): `/repair` fixes why the practice produced the violation, in its context, example, template or scanner, rather than the artifact alone, and waits for approval (`actions/improvement`).

### (S) Agent --> Improve Guidance From Mistake

Intended (increment 5, Repair Guidance From Mistakes; the person, 2026-11-11: not built yet): `/improve` logs the mistake and the correction, runs repair, and captures a regression example so the same failure does not come back (`catalog/workflow.md` Scenario 4).

### (S) Agent --> Add Rule From Failed Example

Intended (increment 5, Repair Guidance From Mistakes; the person, 2026-11-11: not built yet): validate adds a named rule from an example that failed, so the next validation catches the same mistake (`actions/validate` purpose).

## (E) Deliver Work With Overlays

An overlay is guidance laid on top of the practices rather than a practice of its own. Today every overlay is a stack pattern under `cdd_guidance/patterns/`, such as lern_domain_driven, registered with `PatternOverlays` (`harness/graph/pattern_overlays.py`): it holds `practices/<practice>/` folders whose schema and rules the graph adds, and shared rules that Generate and Validate add on top of the practices' rules. The person asked on 2026-11-14 for overlays in general, such as a TDD overlay that adds one common test-first guideline to Clean Engineering `code`, Stories `acceptance_tests` and BDD `development`, at those fidelities only. Today that testing advice is spread over `cdd_guidance/practices/clean_engineering/rules/testing-approach.md` (the test shape ladder, not installed), `cdd_guidance/rules/test-timing.md`, `cdd_guidance/references/language-tools.md`, and red-green-refactor and boundary-stub rules restated in `bdd.md` and `stories.md` (session tdd-practice).

### (S) Person --> [Select Pattern Overlays For Session](../story_tests/deliver-work-with-context-guidance/deliver-work-with-overlays/deliver_work_with_overlays_story.test.md#story-select-pattern-overlays-for-session)

Observed: an action run with an `overlays=` word, such as `overlays=lern_domain_driven,mern_domain_driven`, chooses those overlays on the session first, and the session keeps them in its `session.json`; a word with nothing after it clears them (`guidance_actions.py` `GuidanceCommand.from_guidance`, `ticket.choose_overlays`). Requested (2026-11-14, "select pattern overlay(s) for session"): one or more overlays chosen for the session, whatever kind of overlay each is. The chat bar's + button is Choose Graph Overlays in Move Work Forward From Chat Bar.

### (S:system) CDD Server --> [Decorate Practice Fidelity With Overlay Guidance](../story_tests/deliver-work-with-context-guidance/deliver-work-with-overlays/deliver_work_with_overlays_story.test.md#story-decorate-practice-fidelity-with-overlay-guidance)

Requested (2026-11-14, "decorate guidelines with overlay guideline (eg TDD is added to CE, Stories, BDD at right fidelities)"): an overlay names the practices and fidelities its guidance decorates, such as a TDD overlay on Clean Engineering `code`, Stories `acceptance_tests` and BDD `development`, and adds its guidance and rules to those fidelities and no others. Observed today: a pattern decorates a practice only through its `practices/<practice>/model` schema and `rules` folders, which the graph reads (`GraphOverlay`, `pattern_overlays.py`); its shared rules are not tied to any fidelity.

### (S) Agent --> [Inject Overlay Guidance Into Fidelity Instructions](../story_tests/deliver-work-with-context-guidance/deliver-work-with-overlays/deliver_work_with_overlays_story.test.md#story-inject-overlay-guidance-into-fidelity-instructions)

Requested (2026-11-14, "inject overlay guidance"): loading a fidelity's instructions, through its skill or MCP tool, includes the guidance of each chosen overlay that decorates that fidelity, so the agent follows it while it writes, not only when Generate or Validate runs. Observed today: the fidelity instructions hold the practice's words only, and the hook that injects rules after an action (`GuidanceAction.inject_rules`) injects the listed guidance's rules, not an overlay's.

### (S) Agent --> [Generate With Overlay Rules](../story_tests/deliver-work-with-context-guidance/deliver-work-with-overlays/deliver_work_with_overlays_story.test.md#story-generate-with-overlay-rules)

Observed: Generate adds each chosen overlay's shared rules on top of the practices' rules, under `## Pattern overlay: {name}` (`cdd_guidance/actions/generate/generate.py`, `SessionBrief.overlay_rules`). Requested (2026-11-14, "generate with overlay rules"): only the overlays that decorate the fidelity being generated add their rules.

### (S) Agent --> [Validate With Overlay Rules](../story_tests/deliver-work-with-context-guidance/deliver-work-with-overlays/deliver_work_with_overlays_story.test.md#story-validate-with-overlay-rules)

Observed: Validate judges the work against the overlaid patterns' shared rules too, for content paths name the patterns the work was generated with, and the graph adds each overlay's rules to the node types it names (`cdd_guidance/actions/validate/validate.py`, `practice_rules_registry.py` `pattern_rules_for_practice`). Requested (2026-11-14, "validate with overlay rules"): only the overlays that decorate the fidelity being validated are judged.

## (E) Inject Guidance Into Chat Lifecycle

Hooks run Python at named Cursor events, so CDD can act at key moments of a chat without anyone calling a tool. Cursor starts `harness/hooks/hook_daemon.py` for each event, which runs every enabled hook for that event and returns one merged answer. The Claude install registers no hooks; in Claude Code, the cdd-board mod does this work (Move Work Forward From Chat Bar).

### (S) Cursor --> Start CDD Server On Session Start

Observed: `Installer.ensure_mcp_server_on_session_start` and `ensure_mcp_server_after_agent_response` (`harness/installation/installer.py`) start the one cdd server when none answers, because Cursor and VS Code can connect to it but cannot start it.

### (S) Cursor --> Inject Action Rules After Action Call

Observed: after a guidance action such as generate or validate returns, `GuidanceAction.inject_rules` on `postToolUse` (`harness/guidance_actions/guidance_actions.py`) adds the rules of the guidance it named to the chat.

### (S) Cursor --> Inject Practice Rules After File Edit

Observed, turned off: after the agent edits a file, `inject_rules` on `postToolUse` (`harness/guidance/rule.py`) adds the practice rules whose globs match that file; `@Hook(..., disabled=True)` keeps it from installing today.

### (S) Cursor --> Announce Running Action In Toast

Observed: `PromptNotify.on_pre_tool_use` on `preToolUse` (`tools/prompt_notify/prompt_notify.py`) shows an IDE toast naming the toolset or action about to run.

### (S) Cursor --> Log Prompts And Tool Calls

Observed, turned off: `PromptLog` hooks `beforeSubmitPrompt`, `beforeReadFile`, `preToolUse`, `subagentStart` and `afterAgentResponse` to record what Cursor sends the model; `@Hooks(disabled=True)` keeps it from installing today (`tools/prompt_log/prompt_log.py`).

# (E) Move Work Forward On Session Board

The CDD Kanban shows every ticket in the repository. Story files are under `move-work-forward-on-session-board/` beside this map, one per sub-epic; the specs that run them stay in `space/kanban/`.

## (E) Check CDD Server Health On Board

### (S) Board App --> [Display Board Server Health](../story_tests/move-work-forward-on-session-board/check-cdd-server-health-on-board/check_cdd_server_health_on_board_story.test.md#story-display-board-server-health)

Observed: a band across the page says the cdd server is not connected and how to reconnect; a failing tool shows in a toast without that band, a server failure shows its exception line with the whole traceback behind Details, and a call still running after eight seconds says the board is still waiting on it. Scenarios moved from Display Board on 2026-11-24. Requested (2026-11-06, as the Chat Bar does): a mark with ✓ connected, ⟳ reconnecting, ✕ disconnected or ! tools missing.

### (S) Person --> Open Board Server Health Panel

Requested (2026-11-06, as the Chat Bar does): a panel listing MCP host, Tools, Kanban app and Graph app, or what is wrong.

### (S) Person --> Reconnect CDD Server From Board

Requested (2026-11-06, as the Chat Bar does): the board retries `cdd` and reads the board again. Built today (checked 2026-11-10): the board reads itself again every 2 s while cdd is down (`board-page-view.tsx:22`) and the board server opens a new session on the next call after a restart (`cdd-connection.ts:125`). Missing: a Reconnect button.

### (S) Person --> Reinstall CDD Tools From Board

Requested (2026-11-06, as the Chat Bar does): the board runs the installer and says installing, installed or failed.

### (S) Person --> [Update Board And CDD](../story_tests/move-work-forward-on-session-board/check-cdd-server-health-on-board/check_cdd_server_health_on_board_story.test.md#story-update-board-and-cdd)

Observed (2026-11-12): Update in the header installs the Kanban app again through its generated client (`App.install`, `app.install`): npm install and build in the board's folder, then the page loads the new build; a failed install says why and how to fix it (`AppNotStarted`). It no longer gets the latest commit or re-pins cdd; `scripts/install.py --update` does that.

### (S) Person --> Reload Everything With One Button

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "restart refresh -> one button reloads plugins mcp everything"): Update also reloads the Claude Code plugins and the cdd server, so one press brings every part to the new code. Built today (checked 2026-11-10): Update pulls the code, pins and restarts the cdd server, reinstalls the cdd-board plugin, rebuilds the page and restarts the board server (`board-update.ts:59-62`). Missing: reloading the plugins in open chats, and reinstalling skills, rules and commands.

## (E) See Work On Session Board

The board shows the tickets and lets a person arrange what it shows. Its scenarios are in the files of its two sub-epics; its shared steps and tier specs stay in `see-work-on-session-board/`. Grouped into two sub-epics on 2026-11-24, as it had grown to ten stories.

### (E) [Show Tickets On Board](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/show_tickets_on_board_story.test.md)

The board opens on a project and shows every ticket and backlog item in the column its work puts it in. Grouped on 2026-11-24 from See Work On Session Board.

#### (S) Person --> [Open Board](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/show_tickets_on_board_story.test.md#story-open-board)

Observed: `board-page.ts` `start()` reads the board when the page opens.

#### (S) Board App --> [Display Board](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/show_tickets_on_board_story.test.md#story-display-board)

Observed: Backlog, Discovery, Specification, Implementation, Hardening and Complete, with In progress and Done inside each stage; a ticket moved into Hardening was walked by hand on 2026-11-24 (Move a ticket into Hardening, its screens in `walks/hardening/`), not yet in a browser story test; the board refreshes after each cdd tool call, and a toast announces a ticket's move or review. The scenarios about the cdd server's health and the board's own install moved to Display Board Server Health and Update Board And CDD on 2026-11-24.

#### (S) Board App --> [Display Backlog Items As Tickets](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/show_tickets_on_board_story.test.md#story-display-backlog-items-as-tickets)

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`.

#### (S) Board App --> [Display Ticket Card](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/show_tickets_on_board_story.test.md#story-display-ticket-card)

Observed: `ticket-card-view.tsx` draws the title, age and one block per enabled practice; the active ticket has a thick orange outline.

#### (S) Board App --> [Place Ticket In Column](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/show-tickets-on-board/show_tickets_on_board_story.test.md#story-place-ticket-in-column)

Observed: a ticket shows in the stage of its latest move or, before any move, in the earliest stage its session shows work in; work in a later or an earlier stage moves it there, and a person's move holds until the next work (`see-work-on-session-board.story.shared.py`). Split from Display Ticket Card on 2026-11-24.

### (E) [Arrange Board And Ticket Details](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md)

The person sizes the board, its details and its side panels, sets each stage's limit, and opens a ticket's card and details. Grouped on 2026-11-24 from See Work On Session Board.

#### (S) Person --> [Arrange Board And Details](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md#story-arrange-board-and-details)

Observed: a drag on the split bar resizes the board and details; either can take the whole page.

#### (S) Board App --> [Display Ticket Details](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md#story-display-ticket-details)

Observed: a press on a card shows its practices, fidelity progress and latest validation reports below the board; with none pressed, the details show the active ticket.

#### (S) Person --> [Set Stage WIP Limit](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md#story-set-stage-wip-limit)

Observed: `BoardFile.set_wip_limit`, saved in `.sessions/_board.json`.

#### (S) Person --> [Arrange Side Panel](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md#story-arrange-side-panel)

Observed: the report, files and help panels resize, expand one at a time and close.

#### (S) Person --> [Expand Ticket From Empty Area](../story_tests/move-work-forward-on-session-board/see-work-on-session-board/arrange-board-and-ticket-details/arrange_board_and_ticket_details_story.test.md#story-expand-ticket-from-empty-area)

Observed: one ticket's card is expanded at a time, and a press on a card's fidelity segment opens the card on that fidelity (scenarios moved from Display Ticket Details on 2026-11-24). Intended (`.sessions/_backlog/maintain-tickets-on-board.md` "click any empty area to expand ticket"): a press anywhere on a card that is not a control expands it. Built today (checked 2026-11-11): a press on a card chooses it and shows its details (`ticket-card-view.tsx:198`); only the expand mark opens the card's actions (`ticket-card-view.tsx:57`). Missing: expanding from an empty area.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/see-work-on-session-board/see-work-on-session-board.story.ui.spec.ts`, and by the domain and server tiers.

## (E) Steer Ticket Sessions

A ticket's session is opened, made active, moved and closed from the board. Its scenarios are in the files of its three sub-epics; its shared steps and tier specs stay in `steer-ticket-sessions/`. Grouped into three sub-epics on 2026-11-24, as it had grown to fifteen stories with Delete Ticket Branch.

### (E) [Open Ticket Sessions](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-sessions/open_ticket_sessions_story.test.md)

A person opens a ticket's session, chooses where its work goes, and reaches the ticket's chat. Grouped on 2026-11-24 from Steer Ticket Sessions.

#### (S) Person --> [Open Ticket Session](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-sessions/open_ticket_sessions_story.test.md#story-open-ticket-session)

Observed: `Ticket.new` calls `Session.new`; a person can open the ticket on a folder of the repository.

#### (S) Person --> [Choose Ticket Workpath And Roots](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-sessions/open_ticket_sessions_story.test.md#story-choose-ticket-workpath-and-roots)

Observed: a person browses to the folder a ticket's work goes in, for the whole ticket or one practice, and can put a practice back on its default root (the roots dialog; `steer-ticket-sessions.story.shared.py`). Split from Open Ticket Session on 2026-11-24.

#### (S) Person --> Choose Where A Backlog Item Works

Observed (checked 2026-11-10): starting a backlog item opens Where <item> works, a folder browser that starts at the whole repository with Up and one button per folder; Use <folder> starts the item's session with that folder as its workpath (`root-choice-client.ts` `start`, `root-choice-view.tsx`).

#### (S) Board App --> [Refuse Unusable Ticket Title](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-sessions/open_ticket_sessions_story.test.md#story-refuse-unusable-ticket-title)

Observed (exploratory-testing defects gizmo-04, 05, 06): a new ticket's title that gives no name, whose name a ticket already has, or whose name is longer than 64 characters is refused, naming the title or the limit, and nothing is written for it. Split from Open Ticket Session on 2026-11-24.

#### (S) Board App --> [Open Ticket Chat On Session Open](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-sessions/open_ticket_sessions_story.test.md#story-open-ticket-chat-on-session-open)

Observed (checked 2026-11-10): a press on a card points the board at the ticket's own chat (`ticket-client.tsx:184-188`), and the card's chat button opens the worktree, making it first if needed, then a new Claude chat on it through Python's `chats.open` (`Chats.open`, `harness/chat/chat.py`) (`ticket-client.tsx:196-205`, `chat-client.tsx:72-80`, `claude-link.ts`). It opens a new chat rather than the one the ticket ran in, and Activate opens none. Was: Intended (`.sessions/_backlog/suggest-the-next-step.md` "open associated chat on session open / manually"): opening a ticket's session opens the Claude Code chat it ran in. Observed today: a press on a ticket switches to its chat by hand (`chats.open`).

### (E) [Activate And Move Ticket Sessions](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md)

A person makes a ticket's session the active one, in its own branch and worktree, and moves the ticket from stage to stage. Grouped on 2026-11-24 from Steer Ticket Sessions.

#### (S) Person --> [Activate Ticket](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md#story-activate-ticket)

Observed: Activate opens a dialog with what to do on leaving (commit, push, merge into main) and on opening (branch and worktree), then calls `board.activate`.

#### (S) Board App --> [Find Ticket Branch And Worktree](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md#story-find-ticket-branch-and-worktree)

Observed: activating a ticket finds the branch and worktree its work is on when its session records none or a wrong one, says which branches could be its own rather than guess, leaves a branch named as another ticket to that ticket, and refuses to open onto a folder that is not its checkout (`Ticket.activate`; `space/repo/worktree.py`). Split from Activate Ticket on 2026-11-24.

#### (S) Person --> [Switch Session](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md#story-switch-session)

Observed: a chat switches to the session it names (`sessions.switch`, `OpenSessions.switch` in `space/session/open_sessions.py`); a chat in a ticket's own worktree always works on that ticket's session, and a new chat started for a ticket first switches to it. A name no session has is refused, naming the sessions there are, unless the switch asks for a new session (`create=true`), which makes its folder and so its card on the board (exploratory-testing question gizmo-10, answered 2026-11-23). Scenarios moved from Activate Ticket on 2026-11-24.

#### (S) Person --> [Restrict Actions To Active Session](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md#story-restrict-actions-to-active-session)

Observed: with Active session only on, a ticket that is not the active session disables what sends commands to a chat; moving, activating and information stay open.

#### (S) Person --> [Move Ticket](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/activate-and-move-ticket-sessions/activate_and_move_ticket_sessions_story.test.md#story-move-ticket)

Observed: the arrows or a drag move a ticket one column on (`Ticket.move_next`) or back (`Ticket.move_previous`); out of Implementation it closes into Complete, and back out of Discovery it goes to the Backlog with its work.

### (E) [Close And Hand Off Ticket Sessions](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md)

A person closes a ticket's session without losing its work, deletes its branch, and hands the work on. Grouped on 2026-11-24 from Steer Ticket Sessions.

#### (S) Person --> [Close Active Session](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md#story-close-active-session)

Observed: Close asks what to do with the work, then `Ticket.close` moves the folder to `.sessions/_complete/`, so the ticket shows in Complete.

#### (S) Board App --> [Protect Work When Closing Session](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md#story-protect-work-when-closing-session)

Observed (exploratory-testing defects gizmo-14, 15, 17 and questions gizmo-11, 12): closing offers to commit a branch open in its worktree, warns that deleting a worktree without a commit loses its work, leaves what the repository's own folder holds uncommitted out of the close, keeps the ticket open when its branch does not merge into main or a program holds its worktree open, and refuses to close main. Split from Close Active Session on 2026-11-24.

#### (S) Person --> [Delete Ticket Branch](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md#story-delete-ticket-branch)

Observed (requested 2026-11-09: deleting a branch only deletes the branch, and merging is its own choice): closing a ticket can delete its branch, here and on origin, without merging it into main; the worktree that has the branch goes with it, and a branch checked out nowhere is offered for deletion with no commit or push of main (`steer-ticket-sessions.story.shared.py`; `delete_ticket_branch_story.test.py`). Put on the story map on 2026-11-24, where its scenarios already were.

#### (S) Person --> [Clear Done Worktrees](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md#story-clear-done-worktrees)

Built (2026-11-24, the person: clear away what was cleared by hand that day): `/clear-worktrees` calls `repo.clear_worktrees` (`Repo.clear_worktrees`, *WorktreeClearing* in `space/repo/worktree_clearing.py`), which removes each worktree whose work is all on main and holds nothing uncommitted, its branch kept; deletes each folder beside the main clone named as its worktrees are that git no longer lists, keeping a repository of its own; and deletes git's record of each worktree whose folder is gone, clearing read-only flags and taking the folder over when Windows refuses (*FolderDeletion*). It keeps the main clone, the worktree the call works in, every worktree whose branch has commits not on main, even when its session is closed, and every worktree holding work not committed, and answers each folder removed and kept with why. Test: `space/repo/worktree_clearing_heavy_spec.py`.

#### (S) Person --> [Write Ticket Handoff](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md#story-write-ticket-handoff)

Observed: Handoff fills the prompt with `/space-handoff-handoff-session`.

#### (S) Board App --> [Display Latest Handoff](../story_tests/move-work-forward-on-session-board/steer-ticket-sessions/close-and-hand-off-ticket-sessions/close_and_hand_off_ticket_sessions_story.test.md#story-display-latest-handoff)

Observed: `Ticket.latest_handoff`.

## (E) Maintain Tickets

### (S) Person --> [Add Backlog Item](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-add-backlog-item)

Observed: the + on the Backlog heading writes a title and text to one markdown file in `.sessions/_backlog/`, and refuses a title another idea's file has or one that gives its file no name.

### (S) Person --> [Start Backlog Item](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-start-backlog-item)

Observed: the → on a backlog card starts it as a ticket in Discovery, in the folder the Person chooses, with its idea file kept with the new ticket (`BacklogItem.start`); a ticket moved back to the Backlog comes back with its work, and an idea whose name a ticket already has is refused. Split from Add Backlog Item on 2026-11-24.

### (S) Person --> [Edit Ticket Text](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-edit-ticket-text)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio` "edit text in markdown file"): a double click on a card's text edits it; a session ticket's text is a markdown file in its session folder that the session's instructions refer to, so the board and the agent read the same text; the agent's half, naming the file in the system prompt, is a scenario of Add Active Ticket To System Prompt. Built today (checked 2026-11-11): starting a backlog item moves its markdown file, text and all, into the ticket's session folder (`BacklogItem.start`, `backlog_item.py:121-128`), and a backlog card shows the file's text (`backlog-item-view.tsx:62`). Missing: a ticket's card does not show its file's text, no card edits text, and the agent's context (`Ticket.agent_context`, `ticket.py:217-226`) does not name the file.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/maintain-tickets/maintain-tickets.story.ui.spec.ts`, and by the domain and server tiers.

Requested (2026-11-23); Built (2026-11-23): the link under a backlog item's text opens its file in the Files app, as a ticket's text file opens there, through main's session, since an item has no session until it starts (`BacklogItemClient.openInFiles`); it no longer opens the file in the app the computer opens markdown with, and `backlog-item.open_file` is gone.

### (S) Person --> [Reorder Tickets In Column](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-reorder-tickets-in-column)

Intended (`.sessions/session-board/ticket-enhancements.md`): a ticket dragged up or down within its column keeps that place. Built today (checked 2026-11-11): a drag moves a ticket between columns only; the Backlog lists its items by file name (`board.py:328`) and no column keeps a place a person chose.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/maintain-tickets/maintain-tickets.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Person --> [Archive Ticket](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-archive-ticket)

Observed as the `ticket.archive` tool (`Ticket.archive`). Intended (`.sessions/session-board/ticket-enhancements.md`): Archive on a card.

### (S) Person --> [Delete Ticket](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-delete-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`): Delete on a card removes the ticket and its session folder. Built today (checked 2026-11-11): no delete operation on `Ticket` or `BacklogItem` (`ticket.py`, `backlog_item.py`); Archive is the nearest (`Ticket.archive`, `ticket.py:352`).

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/maintain-tickets/maintain-tickets.story.ui.spec.ts`, and by the domain and server tiers.

Requested (2026-11-23, after the person deleted share-read-only-projects-in-the-board-tools-spec from `.sessions/_backlog/` by hand); Built (2026-11-23): a selected Backlog card, or a selected child row inside its parent's card, offers Delete, which after one confirmation removes the item's markdown file, or its whole folder for a parent with its children or a ticket moved back, and redraws the Backlog without it; a child's file goes alone and its parent stays (`BacklogItem.delete`, `IdeaPlace.remove`, `backlog-item-view.tsx` `DeleteItemView`). Driven by the same three tiers.

### (S) Person --> [Tag Ticket Session](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-tag-ticket-session)

Intended (`.sessions/_backlog/maintain-tickets-on-board.md` "tagging sessions"): a person adds tags to a ticket's session, and the card shows them. Built today (checked 2026-11-11): none; `session.json` holds no tags (`sessions.py:276`).

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/maintain-tickets/maintain-tickets.story.ui.spec.ts`, and by the domain and server tiers.

### (S:system) Session --> [Keep Every Change To Session Record](../story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-keep-every-change-to-session-record)

Requested (2026-11-22, "one lock for every session.json update, so two chats or processes changing one session's record at once each keep their change"); Built (2026-11-22): every change to a ticket's `session.json` holds the file from its read to its write (`SessionRecord.update`, `JsonFile.held`), so a tag, a root, a format or a test tier two chats save at the same moment are both kept. A holder that is killed blocks nobody, and a `session.json` left half written is refused by name and left for a person to repair (`space/session/session_record_processes_heavy_spec.py`).

## (E) Organize Ticket Hierarchy

### (S) Person --> [Split Ticket Into Child Tickets](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-split-ticket-into-child-tickets)

Observed: `Ticket.new` records the parent; Split fills the prompt through `fillSplit`. Intended (`.sessions/session-board/ticket-enhancements.md`): the AI slices the ticket thinly into the child tickets it proposes.

### (S) Person --> [Add Child Ticket](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-add-child-ticket)

Built (2026-11-11): a person adds a child ticket to a parent by hand: the plus on its card opens a title field, and Enter calls `ticket.add_child` (`add-child-view.tsx`). Split still asks the chat for one child per story.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize-ticket-hierarchy.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Board App --> [Display Child Tickets In Parent](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-display-child-tickets-in-parent)

Intended (`.sessions/session-board/ticket-enhancements.md`): a parent's card holds its child tickets stacked inside it, with the parent's title small above them. The drawing (`harness/.context/ux/ticket-ui.drawio`) adds: the parent's card counts its children, and a child pulled out of it keeps a dashed row there. Built today (checked 2026-11-11): a child's card names its scope and parent, such as "story of epic" (`ticket-client.tsx:97-98`), and sits in its column like any other ticket.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize-ticket-hierarchy.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Person --> [Expand Parent Ticket](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-expand-parent-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio`): a parent collapses to its own card and expands to show its children; collapsed it reads + N children, expanded - N children above the child rows.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize-ticket-hierarchy.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Person --> [Detach Child Ticket](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-detach-child-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio` "pull out of parent; and then drag and then move like regular ticket; remembers parent"): a child pulled out of its parent becomes a ticket of its own beside it, named parent.Child, that a person drags and moves like any ticket; it still has its parent. A person pulls a child out by dragging it out of its parent (the person, 2026-11-11).

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize-ticket-hierarchy.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Person --> [Reassign Ticket Parent](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-reassign-ticket-parent)

Intended (`.sessions/session-board/ticket-enhancements.md` "Add a ticket as a child of a different parent" and "Make a child independent of its parent"; `harness/.context/ux/ticket-ui.drawio` "add and remove a child"): a ticket made the child of a different parent leaves its old parent, and a child taken off its parent becomes a ticket with no parent. A person drags a ticket onto another to make it that ticket's child, and Alt-drags a child out of its parent to leave it with none (the person, 2026-11-11). Both change which parent the ticket has, so they are one story. Was: Move Child Ticket To Another Parent.

Built (2026-11-11): dragging a ticket onto another card makes it that ticket's child (`TicketClient.takeAsChild` calls `ticket.reassign_parent`), and dropping a Backlog item on a ticket starts it as that ticket's child (`backlog-item.start_under`); the Alt-drag out of a parent is not built yet.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize-ticket-hierarchy.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Board App --> [Place Parent At Leftmost Child Stage](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-place-parent-at-leftmost-child-stage)

Intended (`harness/.context/ux/ticket-ui.drawio` "parents cant be dragged; they change stage by taking on the stage of the leftmost ticket"): a parent sits in the stage of its child furthest back on the board and moves only as its children move; a person cannot drag a parent.

Built (2026-11-12): on the board, driven by its screen story in `story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize-ticket-hierarchy.story.ui.spec.ts`, and by the domain and server tiers.

### (S) Claude Code --> [Nest Child Branch And Session](../story_tests/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-nest-child-branch-and-session)

Intended (`.sessions/session-board/ticket-enhancements.md`): a child ticket's branch and session nest under its parent's, so the hierarchy holds in git and in `.sessions/` as on the board. Set aside in the Maybe Later increment (the person, 2026-11-11: complicated, not now).

## (E) Guide Work Through Practices On Board

### (S) Board App --> [Display Fidelity Progress](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-display-fidelity-progress)

Observed: each fidelity on a tile shows Generate and Validate as ○ to do, … in progress or ✓ done; a fidelity whose latest validate passes is done.

### (S) Person --> [Open Practice Tile](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-open-practice-tile)

Observed: a tile opens after a short hover, closes on leaving, and a press keeps it open.

### (S) Person --> [Choose Ticket Practices](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-choose-ticket-practices)

Observed: `Ticket.enable_practice` saves the choice to the ticket's `session.json`.

### (S) Person --> [Send Next Fidelity Action](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-send-next-fidelity-action)

Observed: Run next names the step that runs next and steps through generate and validate for each practice in order (`Ticket.next_fidelity`, `Ticket.next_action`), holding on fix violations until they are fixed.

### (S) Person --> [Send Action To Stage Practices](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-send-action-to-stage-practices)

Observed: the stage head sends one action for every enabled practice in a stage.

### (S) Person --> [Mark Ticket Done In Stage](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-mark-ticket-done-in-stage)

Observed: the arrow takes an In progress ticket to Done without crossing a column, written as a `done <stage>` session log line, and back as `in-progress <stage>`.

### (S) Person --> [Open Help](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-open-help)

Observed: `Board.help`; the ? on a tile or practice name opens the overview, guidance and rules in a side panel, with a link to the Forge page.

### (S) Person --> [Choose Session And Practice Roots](../story_tests/move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-choose-session-and-practice-roots)

Observed (checked 2026-11-10): Roots of <ticket> lists the session's root and each practice's root, marked default until a person chooses another; Change browses the folders and Use sets the session's workpath (`chooseWorkpath`) or that practice's root (`root-choice-client.ts`, `root-choice-view.tsx`).

Requested (2026-11-16, "we need better instructions on session setup to scan for all relevant folders to set up roots correctly across product, tests, domain etc."): setting up or switching to a session, the agent proposes each practice's and fidelity's roots from what the ticket names and what its branch changed, digging down to the narrowest folder that holds each piece (an aggregate's folder, a package, a sub-epic's folder in story_tests), confirms them with the person, then sets them; a folder found later is added beside the roots a fidelity has (`session.set_up_roots`, `fidelity-session-output.propose_roots`).

## (E) Customize Board Workflow

A team defines its own workflow, then the board draws, moves and tracks tickets by that workflow instead of the fixed Discovery, Specification and Implementation stages (`harness/guidance/stages.py` `ApproachStages`).

### (E) Define Board Workflow

#### (S) Person --> Customize Workflow Stages

Intended (`.sessions/_backlog/customize-board-workflow.md` "customize workflow, add process, assign practices fidelity, HIL column"): a person adds a stage, chooses the practices and fidelities it holds, and adds a column where a person must act before work moves on.

#### (S) Person --> Write Column Policies

Intended (`.sessions/_backlog/customize-board-workflow.md` "write policies"): a person writes the policy a column holds work to, such as what must be true before a ticket leaves it.

#### (S) Person --> Collapse Column Policies

Intended (`.sessions/_backlog/customize-board-workflow.md` "collapse / expand policies for columns"): a column's policies collapse to its heading and expand again.

#### (S) Person --> Configure Todo List

Intended (`.sessions/_backlog/customize-board-workflow.md` "configurable todo list"): a person sets the list of steps a ticket works through.

### (E) Run Tickets Through Customized Workflow

#### (S) Board App --> Display Board From Customized Workflow

Requested (2026-11-10): the board draws one column per stage of the ticket's workflow, in the workflow's order, with its human review columns and each column's policies, in place of the fixed stages.

#### (S) Board App --> Display Work Type Flows On Board

Intended (`.sessions/_backlog/customize-board-workflow.md` "work type based flows; multi flow shows up on board"): each work type has its own flow, and the board shows several flows at once.

#### (S) Person --> Move Ticket Along Customized Workflow

Requested (2026-11-10): moving a ticket to the next or previous stage follows the workflow's own stage order, and a ticket cannot be moved to a stage its workflow does not have.

#### (S) Person --> Approve Ticket Out Of Human Review Column

Requested (2026-11-10), from the human review column in Customize Workflow Stages: a ticket in a human review column waits there until a person approves it, and only then moves to the next stage.

#### (S) Board App --> Track Ticket Status Through Workflow

Requested (2026-11-10): the board records the stage each ticket is in, when it entered and left each stage, which todo list steps are done and which column policies it meets, and shows that status on the ticket card and in its details. Built today (checked 2026-11-10): the session log records timestamped move, done and in-progress lines per stage (`StageMarks`, `ticket.py:447-479`), and the card shows its column, done or in progress, and its age. Missing: when it left each stage, todo steps, and policies met.

#### (S) Board App --> Show Stage Practices From Customized Workflow

Requested (2026-11-10): the practice tiles and next fidelity action for a ticket come from the practices and fidelities its workflow assigns to the ticket's current stage.

## (E) Show Board Quickly

Intended (`.sessions/_backlog/show-board-quickly.md`): `board.show` takes about 1.6 s per call (profiled), which makes `space/kanban/kanban_tools_spec.py` take about 200 s for 198 examples and slows the chat bar and the board. Goal: `kanban_tools_spec` under 60 s and a faster chat bar. The change is in shared modules, so reinstall after it.

### (S:technical) Board App --> Check Ticket Branches Once Per Board Build

Intended (`.sessions/_backlog/show-board-quickly.md` cause 1): `TicketCheckout._found_branch` → `Branch.exists` → `Refs.has` runs one `git show-ref` per check, about 70 ms each and about 7 per `board.show` (`space/kanban/ticket_checkout.py`, `space/repo/repo.py`); one board build checks each branch once.

### (S:technical) Board App --> Cache Practice Guidance By File And Change Time

Intended (`.sessions/_backlog/show-board-quickly.md` cause 2): practice guidance markdown is read and parsed again for every session (`harness/guidance/guidance.py`, `harness/markdown/markdown.py`); it is cached by file and modification time.

### (S:technical) Board App --> Read Session File Once Per Board Build

Intended (`.sessions/_backlog/show-board-quickly.md` cause 3): `session.json` is read thousands of times over a few `board.show` calls (`harness/installation/json_file.py`); one board build reads each session file once.

## (E) Work Fidelity Outputs On Board

### (E) Generate Fidelity Outputs On Board

#### (S) Person --> [Choose Action And Formats](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-choose-action-and-formats)

Observed: the tile's action bar lists the actions and format chips, with the default format picked unless that output exists.

#### (S) Person --> [Run Chosen Formats](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-run-chosen-formats)

Observed: a tile's Run stays off on a render with nothing to render, with no chat, and on a locked ticket, and a stage's Run sends the formats picked so each fidelity writes the first it takes (`tile-client.spec.ts`; `choose_action_and_formats_story.test.py`, `run_chosen_formats_story.test.py`). Split from Choose Action And Formats on 2026-11-24.

#### (S) Claude Code --> [Resolve Fidelity Output Paths](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-resolve-fidelity-output-paths)

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides.

#### (S) Person --> [Generate Fidelity Output](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-generate-fidelity-output)

Observed: Run sends `/actions-generate <fidelities> format=<formats>`, rendering the earlier fidelity into a new format first (`Ticket.generate_commands`); a generate line in the session log counts as Generate done.

#### (S) Person --> [Render Fidelity Format](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-render-fidelity-format)

Observed: Render sends `/actions-render`.

#### (S) Person --> [Send Tile Action To Chat](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-send-tile-action-to-chat)

Observed: Run sends `/actions-sketch`, `/actions-iterate` or `/actions-document` to the chosen chat.

#### (S) Person --> Add Comment To Sent Command

Intended (`.sessions/_backlog/enter-commands-faster.md` "add comment to command sent to chat"): a person adds their own words to the command the board sends to the chat. Built today (checked 2026-11-10): Split, Handoff, + Ticket and Run next put the command into the prompt for the person to edit before sending (`chat-client.tsx:144-148`). Missing: tile Run, Validate and Fix send at once, and there is no comment field.

#### (S) Person --> Choose Testing Strategy

Intended (`.sessions/_backlog/customize-board-workflow.md` "support for multi language / bespoke testing layers eg a testing strategy; generate; validate"): a person chooses the test layers and languages a ticket's tests use, and generate and validate follow that choice.

#### (S) Person --> Toggle Sub Agents

Intended (`.sessions/_backlog/customize-board-workflow.md` "use sub agents toggle"): a person turns on running a board action in sub-agents.

### (E) Validate Fidelity Outputs On Board

#### (S) Person --> [Validate Fidelity](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-validate-fidelity)

Observed: Validate sends `/actions-validate`; a validate line counts as done only when it names no graph-rule violations.

#### (S) Claude Code --> [Save Validation Report](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-save-validation-report)

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md` and the graph it checked beside it in `.json`.

#### (S) Person --> [Open Validation Report](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-open-validation-report)

Observed: `fidelity-progress.report` opens the latest report in a side panel.

#### (S) Person --> [Fix Report Violations](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-fix-report-violations)

Observed: Fix sends the chat the rule, the error at its file and line, and the content that failed; Fix all sends every violation of the rule in one message.

#### (S) Person --> [Accept Report Violation](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-accept-report-violation)

Requested (2026-11-21, "we need a way to accept violations so we dont see them again if we click accept; a simple violations accepted json which match acceptances to node id; ignore these exact same on subsequent passes"). Built (2026-11-21): Accept beside Fix and False on the board's report keeps the acceptance in the project's `.context/violations-accepted.json` by the violation's rule, the id of its node and its message (`space/session/validation/accepted_violations.py` *AcceptedViolations*); that violation is left out of every later report, count and validation while it stays the same, and Take back shows it again. The Files app and the Graph app still mark an accepted violation.

#### (S) Board App --> [Display Violations Band](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-display-violations-band)

Observed: the band shows the active ticket's violations, only when it has some, and sends them to satisfy.

#### (S) Board App --> Display Report Without Header Noise

Observed (checked 2026-11-10; commits 93eb442e7, e502c9963): the raw report text shows only when the report has no saved graph and no rules could be read from it; otherwise the panel opens on the rules (`report-panel-view.tsx:48-61`). Was: Intended (`.sessions/_backlog/review-work-in-board-files.md` "kill weird MD area at top of violation report"): the report panel opens on the findings, without the markdown block that sits above them today.

#### (S) Board App --> Display Report Errors In Code Fences

Observed (checked 2026-11-10): each violation that names a file and line shows a block of source lines headed by its location, with the failing line marked (`report-rule-view.tsx:10-43`, `harness/graph/violation.py:128-164`); a violation with no file and line shows only its message. Was: Intended (`.sessions/_backlog/review-work-in-board-files.md` "violation report not showing code fences for errors"): each error's content shows in a code fence.

### (E) Review Fidelity Outputs On Board

Changed (2026-11-21, design proposal 24, approved): the board's own files panel is gone, and every board press that opened it opens the Files app on the same ticket's files, folder, or file at a line. The tabs and filters these stories describe are the Files app's (Review Files In Files App).

#### (S) Person --> [List Ticket Files](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-list-ticket-files)

Observed: `fidelity-progress.files` lists the tile's or ticket's fidelities' files; on a ticket working in the whole repository, only what its branch changed. Intended (the person, 2026-11-12, "this is a filter eg a checkbox on the file viewer at the top where tabs are; you click only changed files listed"): the list shows every file of the fidelity, and a changed-files-only check box at the top beside the tabs filters it to what the ticket's branch changed.

#### (S) Person --> [Browse Ticket Files By Practice](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-browse-ticket-files-by-practice)

Observed: the folder mode of the files panel groups the files under their folders. Requested (2026-11-12, "list a shortened form/image of each practice top to bottom on left side, filters preset when clicking files button in chat ui, user can toggle them; top has file tabs like now but colored to practice"): the practice filters sit along the top of the files panel, each by its short form (2026-11-12: "put the filter toggles on the top, it will waste less space"). Every file is a tab along the top, grouped by practice and colored in its practice's color. Opening the files from the chat bar presets the filters, which the person can toggle ("these are just filters on left; all files are shown in tabs above grouped by practice colored by practice color"). This replaces grouping by folder, and builds on the person's 2026-11-11 notes (groupings by knowledge-graph root such as practice, click to select, check box to select several).

#### (S) Person --> [View Fidelity Files](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-view-fidelity-files)

Observed: one tab per format the fidelity offers, generated or not; × closes one.

#### (S) Person --> List Ticket Context Files

Intended (`.sessions/_backlog/review-work-in-board-files.md` "include ticket context file and folders with list - folder-files; separate section"): the files panel lists the ticket's own context file and folders in a section of their own.

#### (S) Person --> [Open Session Files From Details](../story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-open-session-files-from-details)

Intended (`.sessions/_backlog/review-work-in-board-files.md` "session information -> link to file or folders"): each file or folder the session information names opens from where it is named. Built today (checked 2026-11-10): the details open the session folder, the stage's files and the latest handoff (`details-view.tsx:37-55`). Missing: the workpath link opens the root chooser rather than the folder. Requested (2026-11-12, "clicking on a session button when the button is in session mode eg no expand no main; opens the file view on .session/session"): pressing a ticket's session button, not main and not expanded, opens the file view on its .sessions/<session> folder.

### (E) Integrate Practice Content Editor Apps On Board

#### (S) Person --> [Open Story UI On Ticket Scope](../story_tests/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/integrate_practice_content_editor_apps_on_board_story.test.md#story-open-story-ui-on-ticket-scope)

Requested (2026-11-06, "board --> story ui for ticket's scope"): the board opens the Story UI editor on the part of the story map the ticket covers, from its session folder. Also Intended (`.sessions/_backlog/integrate-practice-content-editor-apps.md` "view story map / ux design canvas for a session"). Requested (2026-11-12): a small editor widget on the ticket's Stories story-map row opens it.

#### (S) Person --> Filter Graph To Ticket Scope

Requested (2026-11-06, "filter to scope of ticket"): opening the Graph app from the board or the chat bar loads only the ticket's session folders. Also Intended (`.sessions/_backlog/integrate-practice-content-editor-apps.md` "view knowledge graph from here"). Requested (2026-11-12): a graph widget on the ticket, beside its folder and file icons, opens the graph on the ticket's scope.

#### (S) Person --> Filter Graph To Ticket Practices

Requested (2026-11-06, "practices loaded for ticket / board"): the Graph app opens with its practice filter set to the practices the ticket has turned on, or every practice on the board when opened from the board header.

#### (S) Graph App --> Show Board's Active Ticket In Graph

Requested (2026-11-06, non-functional): the Graph app runs on the same app server and instance as the board's state, so the graph and the board share one state for the active ticket. The repeatable behaviour: the Graph app shows the ticket the board has active, from the board's own state.

#### (S) Board App --> Show Agent's Ticket Changes On Board

Requested (2026-11-12, non-functional, "like above but for kanban board"): the CDD Kanban, like the Story UI app, follows the cdd_web_domain_access and lern_domain_driven patterns: its backend is the MCP-generated domain objects through the TypeScript adapter, not calls of its own. The repeatable behaviour: a change the agent makes through the tools shows on the board with no copy kept in the page, and a board whose cdd server is down says so.

#### (S) Agent --> [Refactor Knowledge Graph App To Web Domain Access](../story_tests/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/integrate_practice_content_editor_apps_on_board_story.test.md#story-refactor-knowledge-graph-app-to-web-domain-access)

Observed (checked 2026-11-10; commit 23e3d037e): `GraphClient extends GraphClientGenerated` (`harness/graph/app/graph/GraphClient.ts:1-6`), with `GraphApi implements CddApi` as transport and the server mounting the generated `graphRoutes` (`server.ts:8,50`). Was: Requested (2026-11-06, non-functional): the Graph app reaches the CDD domain through the TypeScript language adapter generated by the cdd_web_domain_access pattern, instead of its own calls.

#### (S) Person --> [Invoke Story Explorer In Session Context](../story_tests/move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board/integrate_practice_content_editor_apps_on_board_story.test.md#story-invoke-story-explorer-in-session-context)

Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "view story map / ux design canvas for a session", requested on 2026-11-06): the board opens the browser story explorer on the ticket's story map, framed by its design canvas screens.

# (E) Move Work Forward From Chat Bar

The Chat Bar is the line above the chat prompt for the one session the chat works in, so where the board says ticket it says session (CDR `harness/chat-ui/.context/cdr/0001-stage-strip-band.md`). Its scenarios are under `story_tests/move-work-forward-from-chat-bar/`; the mod's plugin tests (`claude plugin test`) sit beside the code they test in `harness/chat-ui/pane/hooks/`. The stubbed story tests that played the scenarios were removed in 8c56ab052.

## (E) Check CDD Server Health In Chat Bar

The chat bar's health mark, the server health panel and the apps it opens, and the version of CDD the chat runs. Grouped on 2026-11-24 into two sub-epics, as it had grown to twelve stories.

### (E) [Check CDD Server And Apps In Chat Bar](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md)

The health mark, the server health panel, and the repairs and apps a person reaches from it. Grouped on 2026-11-24 from Check CDD Server Health In Chat Bar.

#### (S) Chat Bar --> [Display Server Health Mark](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-display-server-health-mark)

Observed: `ServerHealthBandView` draws ✓ connected, ⟳ reconnecting, ✕ disconnected or ! tools missing, right of the session's name and its buttons, before the version (`chat-bar-view.tsx` `LineView`).

#### (S) Person --> [Open Server Health Panel](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-open-server-health-panel)

Observed: the session card shows one line of icons, the MCP host and each app the health report names (Graph, Files, Kanban, Story UI), each icon's tip giving its name and state, the tool count in the MCP host's; above them the panel gives a headline saying what is wrong, only while something is; pressing the mark pins the card open.

#### (S) Person --> [Reconnect CDD Server](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-reconnect-cdd-server)

Observed: Reconnect retries `cdd` up to three times (`RECONNECT_TRIES`), then reads the active session again.

#### (S) Person --> [Create Git Repository First](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-create-git-repository-first)

Built (2026-11-18), not seen (the coordinator, relaying the person: "A git repository is required: remove every way to choose or work in a plain folder, and in a plain folder the chat bar asks to create the git repository first"): CDD works in a git repository. In a session whose project is no git repository, the chat bar's line holds only the folder's path, "is no git repository, and CDD works in one", a Create the git repository button, the health mark and the version badge: no stages, fidelities, actions, session card or lists. The press calls `repo.make_repository` (`Repo.make_repository`, `NewRepository.make_from_folder`): the folder's `.gitignore` takes what the CDD checkout ignores, then `git init -b main` and a first commit of the folder's own files with a README, leaving `.claude` and `.sessions` out; the bar is read again and draws the session. The repository list's Folder Only (No Repo) section and the `repos.open_folder` tool and `/open-folder` command, which opened a folder as it was, are gone. Tests: `harness/chat-ui/pane/hooks/chat-bar/make-repository.test.ts` (`claude plugin test`), `space/repo/new_repository_heavy_spec.py`.

#### (S) Person --> [Reinstall CDD Tools](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-reinstall-cdd-tools)

Observed: Run install runs the installer and says installing, installed (open a new session) or failed; Details shows the tool, error, server and fix.

Built (2026-11-18), not seen (the person: "When the plugin starts in a chat, run the installer into that chat's folder if its .claude, skills and commands are missing"): when the board mod starts in a chat whose folder has no `.claude/skills` or no `.claude/commands`, it runs the same install Run install runs (`installWhenMissing`, `health/server-health-client.ts`), beside the board's first read, and the health panel says installing, installed or failed. `scripts/install.py --from-chat FOLDER` for a folder that is no CDD checkout now installs into `FOLDER/.claude`, where it had installed into the served checkout's own `.claude`. It refuses the home folder, a folder in the temporary folder and the desktop app's spare folders (exit 3, `NOT_A_PROJECT_EXIT`), so a chat started there never writes CDD's skills into `~/.claude` or a folder that is thrown away; at chat start the refusal shows nothing, and a pressed Run install shows why on the failure line. Observed (2026-11-18, a headless chat loading the worktree's mod): a chat in an empty folder that is no git repository got `.claude` with skills and commands; the same chat without the mod got none; a chat in a temporary folder got none. Tests: `harness/chat-ui/pane/hooks/health/install-on-start.test.ts` (`claude plugin test`), `scripts/install_spec.py`.

#### (S) Person --> [Open App From Health Panel](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-open-app-from-health-panel)

Observed: pressing the Kanban app or the Graph app on the server health panel opens it in the browser, and starts it first when it reads not running (requested 2026-11-10, "clicking on app in chat ui starts it if down, opens it if up"). The Kanban app starts as `/board` starts it (`startedBoard` in `board-server.ts`) and opens on this repository's board page; the Graph app starts with the repository's own `scripts/start_graph_web.py` and `scripts/start_graph_app.py` and opens where the second says it answers. A start that fails says why in a toast (`health/open-app-client.ts`). Its scenarios about the chat's session and lane, and about an app that did not open, became stories of their own on 2026-11-24.

#### (S) Person --> [Open App On The Chat's Session And Lane](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-open-app-on-the-chats-session-and-lane)

Observed: an app opened from the chat bar names the checkout the chat works in, so a ticket's worktree is answered by the dev lane and the main checkout by the stable lane; the Kanban app opens with the chat's ticket selected and the Graph app on the chat's session path (`health/open-app-client.ts`). Split from Open App From Health Panel on 2026-11-24.

#### (S) Chat Bar --> [Say Why App Did Not Open](../story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check-cdd-server-and-apps-in-chat-bar/check_cdd_server_and_apps_in_chat_bar_story.test.md#story-say-why-app-did-not-open)

Observed: when the Graph app's start script fails, the chat has no browser pane, or the app's page does not load in the pane, nothing opens elsewhere and the Person is told why, naming the failing script and its log or in the pane's own words (`health/open-app-client.ts`). Split from Open App From Health Panel on 2026-11-24.

#### (S) Person --> Restart Parts From Chat Bar

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "restart buttons not on panel"): the restart controls sit on the chat bar itself, not only inside the server health panel.

### (E) Keep CDD Version Current In Chat Bar

The version badge, the next version a person sets, and the update the badge runs. Grouped on 2026-11-24 from Check CDD Server Health In Chat Bar; these stories have no scenarios yet.

#### (S) Chat Bar --> Display CDD Version Badge

Observed (requested 2026-11-14, "a small button with v.<major.minor> ... green current version; yellow behind minor; red behind major"): as the chat opens, `cdd-version.check` (`CddVersion.check`, `harness/release/cdd_version.py`) fetches origin main and answers the version the cdd server runs, read as major and minor from `pyproject.toml`, the version on origin main, and how the two stand; the badge at the end of the line shows `v0.1` green when current, yellow a minor version behind, red a major version behind, grey when origin main was never fetched, with the summary on hover (`health/cdd-version-view.tsx`). Specs: `harness/release/cdd_version_spec.py`.

#### (S) Person --> Set Next CDD Version

Observed (requested 2026-11-14, "/version --> enters the next version to repo config e.g. push", "dont version automatically"): `/version` (`cdd-version.set_next`, `CddVersion.set_next`) writes the next version into the `version` of the repository's `pyproject.toml`: the version given, such as `0.2` or `1.0.1`, or with none given the next minor version; text that is not a version is refused (*VersionNotValid*). Nothing raises the version by itself, so a person runs it when a change is a release, before pushing to main; the version badge in other chats turns yellow or red once that push reaches origin main. Specs: `harness/release/cdd_version_spec.py`.

#### (S) Person --> Update CDD From Chat Bar

Observed (requested 2026-11-14, "click opens dialog update and reinstall? use above script if yes"): pressing the version badge asks to update and reinstall; Update and reinstall runs `/harness:installation:install-latest` in the chat (`updateToLatest`, `health/cdd-version-client.ts`), so the chat lists its seven steps and ticks each off as it finishes: pull origin main, stop every app, restart the cdd server, install every toolset, ping the server; once the command's turn ends the badge reads the version again; hovering the badge says updating…, up to date, or update failed, and a failure shows why on the failure line. The agent does the same with `/install-latest` (`Installer.install_latest`), which ticks off each step as `scripts/install.py` reports it.

## (E) See Work In Chat Bar

### (S) Person --> Open Board From Chat

Observed: the `/board` command in `harness/chat-ui/pane/hooks/register.ts` opens the board, starting it when it is not running.

### (S) Chat Bar --> [Display Stage Strip](../story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-display-stage-strip)

Observed (read in `chat-bar-view.tsx` `LineView`, 2026-11-23): one line with the stage icons, a separator, the practice dots, the overlay and format chips, the action button, the files, handoff and debug buttons, then at the right the session name, the session buttons, the health mark and the version badge. A draw that throws shows "chat bar failed to draw" and why, in red, in place of the line (`register.ts`; plugin test `chat-bar-draw.test.ts`).

### (S) Chat Bar --> [Display Session Fidelity Dots](../story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-display-session-fidelity-dots)

Observed (read in `PracticeDotView` and `PracticeDotClient`, 2026-11-23): one square per practice with a fidelity in the shown stages, in its practice's colour shaded by its least advanced fidelity, faint while the practice is turned off for the session, with the practice's violation count in red beside it while it is on; the practice's fidelities show above it on hover, each opening its help. Pressing the square turns the practice on or off for the session.

### (S) Person --> Display Stage Fidelities

Observed: pressing a stage icon shows that stage's fidelities on the dots, tinted while it is not the stage in progress, and drops an action picked from the menu (`stage-client.ts` `selectStage`).

### (S) Person --> [Display Session Card](../story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-display-session-card)

Observed: the pointer on the session name shows the card, with each fidelity's name and state over its dot and its folder as a chip that opens its files; pressing the name pins the card open and ✕ closes it (`session-card-view.tsx`). The folder chip covers `.sessions/_backlog/bring-chat-bar-level-with-board.md` "Click a practice to get its file list".

### (S) Chat Bar --> [Show Active Session On Status Line](../story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-show-active-session-on-status-line)

Observed (`register.ts` `showStatus` and its `PromptHint` hook, `chat-bar-client.ts` `statusLine`): the hint line under the prompt, after what the engine writes there, and the status line below the chat, where the host draws a plugin's status, name the repository, the branch the session's chat works on, and the whole path of the folder the session works in. Requested on 2026-11-11 ("repo . session . root path of session . action selected", "below the actual chat edit like before"). Left aligned was also asked; the host places a plugin's status line itself, so a plugin cannot align it, and drawing the row in the chat bar or in the prompt hint line (tried in ce6b9157e and 066b2d3fc) lost it below the chat; the bar's own left-aligned row (c8abaf8d0) put it under the bar's menus, and it came back below the chat on 2026-11-13.

### (S) Claude Code --> [Add Active Ticket To System Prompt](../story_tests/move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-add-active-ticket-to-system-prompt)

Inferred: the `prompt.compose` hook in `register.ts` adds the active session and its next guidance, and leaves the prompt unchanged with no active session. Intended (`.sessions/session-board/ticket-enhancements.md`): the prompt also names the file that holds the ticket's text (increment Maintain Tickets On Board).

## (E) Steer Sessions

### (S) Person --> Create New Session

Observed: the ▾ beside the session name opens the session list, whose field names a new session that `ticket.create` creates (`session-client.ts` `createSession`). Requested (2026-11-06, as the CDD Kanban does): choose the session root.

### (S) Person --> [Open Session](../story_tests/move-work-forward-from-chat-bar/steer-sessions/steer_sessions_story.test.md#story-open-session)

Observed: picking a session from the list opens a dialog saying the active session is committed and pushed, with merge off, and that the new one opens on its own branch and worktree, then calls `board.activate` (`session-dialogs-view.tsx` `ActivateView`).

### (S) Person --> Write Session Handoff

Observed: the ⇥ handoff icon adds "Write a handoff for ticket <session> with /space-handoff-handoff-session." to the prompt (`chat-bar-client.ts` `runHandoff`).

### (S) Chat Bar --> [Display Latest Session Handoff](../story_tests/move-work-forward-from-chat-bar/steer-sessions/steer_sessions_story.test.md#story-display-latest-session-handoff)

Requested (2026-11-06, as the CDD Kanban does): the chat bar shows the active session's latest handoff.

### (S) Person --> Close Session From Chat Bar

Observed: the ✕ icon opens a dialog saying the session's work is committed and pushed first when it has a branch, then Close session calls `ticket.close` (`session-dialogs-view.tsx` `CloseView`).

### (S) Person --> Add Backlog Item From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"), from `.sessions/_backlog/bring-chat-bar-level-with-board.md`: an Add to backlog button on the chat bar adds a feature to the backlog, as the board's Add Backlog Item does.

### (S) Person --> [Debug A Failure From Chat Bar](../story_tests/move-work-forward-from-chat-bar/steer-sessions/steer_sessions_story.test.md#story-debug-a-failure-from-chat-bar)

Requested (the person, 2026-11-15): a debug button right after handoff sends the agent to capture what went wrong as fully as it can, stack traces included, then asks for more detail and whether to fix the bug or request help; help emails jeff.anderson@abdworks.com, and a fix is made in a sub-agent and pushed to main, or sent as a pull request to the CDD repository where the person cannot push there. The chat bar's Fix buttons take the same fix. Built (2026-11-15): the 🐞 icon after ⇥ puts `/space-session-debug-session` in the prompt box (`Session.debug_session`); it writes `debug/debug-{time}.md` in the session's folder, asks with AskUserQuestion, opens the help email as a draft in the person's mail program for them to send, and checks `gh api repos/<owner>/<repo> --jq .permissions.push` before pushing or opening the pull request. Fix on a failure line starts it with `choice=fix` and the failure as its details; Fix on a board that did not answer adds it as a last step.

## (E) Sync Session Work With Git From Chat Bar

The chat bar's buttons that commit the session's work, push its branch, merge it to main and pull the latest commits. Grouped on 2026-11-24 from Steer Sessions, which had grown to eleven stories.

### (S) Person --> Commit Work From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Commit button commits the active session's changes (`WorkingTree.commit`, `repo.working_tree`, in `space/repo/repo.py`).

### (S) Person --> [Push Work From Chat Bar](../space/repo/session_to_main_spec.py)

Observed (2026-11-14): the ⤴ icon, first of the session buttons, calls `repo.push_work` (`Repo.push_work`) for the folder the chat works in: the checkout commits its work on its branch and pushes the branch; nothing is merged. Was Requested (2026-11-10): a Push button pushes the active session's branch.

### (S) Person --> [Push Session To Main From Chat Bar](../space/repo/session_to_main_heavy_spec.py)

Observed (2026-11-14): the ⇪ icon after ⤴, "push & merge to origin/main", asks "Push <session> and merge it to origin/main?", and yes calls `repo.push_to_main` (`Repo.push_to_main`) for the folder the chat works in, whichever repository holds it: the checkout commits its work on its branch and pushes the branch, the main clone merges that branch into the repository's default branch (`Branch.merge_into_default`; `Repo.default_branch` is the branch origin's HEAD names, else main or master), pushes it, and goes back to the branch it had. On main itself it commits and pushes main. The version is not raised; `/version` does that when the person chooses. `repo.merge_to_main` does the same without pushing, for an agent; the chat bar has no button for it (2026-11-14: "we only need the other button").

### (S) Person --> Pull Latest From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Pull button pulls the latest commits into the active session's checkout (`Repo.pull` in `space/repo/repo.py`).

## (E) Guide Work Through Practices In Chat Bar

### (S) Person --> Move Session To Next Stage

Observed: once every fidelity of the stage has passed validate, the action button shows ➜ and pressing it calls `ticket.move_next` (`action-button-view.tsx` `actionOf`).

### (S) Person --> [Invoke Next Fidelity Action](../story_tests/move-work-forward-from-chat-bar/guide-work-through-practices-in-chat-bar/guide_work_through_practices_in_chat_bar_story.test.md#story-invoke-next-fidelity-action)

From the chat bar's own map (harness/chat-ui/.context/story-map.md, folded in 2026-11-16). Mirrors Send Next Fidelity Action, for one fidelity: the action button runs generate, validate or review on the selected fidelity (CDR "Action button and ▾ picker"; "Actions run on one fidelity at a time"). Its story test was removed with the chat bar's stubbed tests (8c56ab052).

### (S) Person --> Choose Fidelity Action

From the chat bar's own map, folded in 2026-11-16. Mirrors Choose Action And Formats, without formats: the ▾ picker offers generate, validate, review, iterate, sketch, render and document (CDR "Action button and ▾ picker"); selecting another fidelity drops the picked action. Its story test was removed with the chat bar's stubbed tests (8c56ab052).

### (S) Person --> Move Session To Previous Stage

Requested (2026-11-06, as the CDD Kanban does): the chat bar moves the session back a stage through `ticket.move_previous`.

### (S) Person --> Mark Session Done In Stage

Requested (2026-11-06, as the CDD Kanban does): the chat bar marks the active session Done in its stage and back to In progress.

### (S) Person --> Open Fidelity Help

Requested (2026-11-06, as the CDD Kanban does): the chat bar opens the same help for a fidelity or practice through `board.help`.

## (E) [Choose Session Practices And Overlays In Chat Bar](../story_tests/move-work-forward-from-chat-bar/choose-session-practices-and-overlays-in-chat-bar/choose_session_practices_and_overlays_in_chat_bar_story.test.md)

What a session works with, chosen from the chat bar: its practices, its folders, and the pattern overlays its graph applies. Grouped on 2026-11-24 from Guide Work Through Practices In Chat Bar, which had grown to eleven stories.

### (S) Person --> [Choose Session Practices](../story_tests/move-work-forward-from-chat-bar/choose-session-practices-and-overlays-in-chat-bar/choose_session_practices_and_overlays_in_chat_bar_story.test.md#story-choose-session-practices)

Requested (2026-11-06, as the CDD Kanban does): the chat bar turns the active session's practices on and off through `ticket.enable_practice`. Observed (`session-card-view.tsx` `FidelityCellView`): on the session card, one button holds a fidelity's coloured square and its name, and its press turns that fidelity's practice off for the session, or on again, through `session.toggle_guidance`; picking a fidelity from the dots on the line is Select Fidelity. Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "Toggle practices on and off from the card"): the practices turn on and off from the expanded session card.

### (S) Person --> Choose Session Folders From Chat Bar

Requested (2026-11-10, "new session or session where folders aren't set on switch --> probably one dialog box, eg expand above chat bar"): when the chat bar creates a session that does not come from a backlog item, or switches to a session whose workpath and practice roots are not set, one dialog opens above the chat bar to choose the workpath and each practice's root, as the board's Choose Where A Backlog Item Works and Choose Session And Practice Roots do.

### (S:system) Ticket --> [List Available Patterns](../story_tests/move-work-forward-from-chat-bar/choose-session-practices-and-overlays-in-chat-bar/choose_session_practices_and_overlays_in_chat_bar_story.test.md#story-list-available-patterns)

Requested (2026-11-11, "opens a list box for LERN, MERN eg all patterns we have ... set this list dynamically based on contents of folder"): a ticket's `overlay_choices` answers one choice per pattern, each with its icon and whether the session chose it. The patterns are every one registered from `cdd_guidance/patterns/`, where each subfolder whose module of the same name defines a pattern class registers itself (`PatternOverlays.names`), so a pattern folder added there is offered with no change to the chat bar.

### (S) Person --> [Choose Graph Overlays](../story_tests/move-work-forward-from-chat-bar/choose-session-practices-and-overlays-in-chat-bar/choose_session_practices_and_overlays_in_chat_bar_story.test.md#story-choose-graph-overlays)

Requested (2026-11-11, "right after practices we need + overlay button where we can add one or more graph overlays ... can select more than one"): a + right after the fidelity dots opens a list box of the patterns the board lists, the session's chosen ones marked; a press on one adds it to or takes it out of the session's overlays through `ticket.choose_overlays`, which keeps them in the session's `session.json` and applies them to the session's graph (`Graph.overlays`).

### (S) Chat Bar --> [Display Overlay Icons](../story_tests/move-work-forward-from-chat-bar/choose-session-practices-and-overlays-in-chat-bar/choose_session_practices_and_overlays_in_chat_bar_story.test.md#story-display-overlay-icons)

Requested (2026-11-11, "adds a new icon to bar, pushing action and format", "icon is first and last letter of pattern"): each overlay the session has chosen shows as an icon after the + and before the format chips and the action button, its pattern's first and last letter in capitals (`lern_domain_driven` is LN), the pattern's name on hover.

## (E) Work Fidelity Outputs In Chat Bar

### (E) Generate Fidelity Outputs In Chat Bar

#### (S) Person --> Select Fidelity

Observed: pressing a dot selects that fidelity, and the action button then shows its next action, such as ▶ generate for a fidelity still to do; selecting another drops an action picked for the one before, and nothing is sent to the chat (`fidelity-client.ts` `selectFidelity`).

#### (S) Chat Bar --> Display Action Before Fidelity Dots

Requested (2026-11-06, "reorder buttons; action then practices"): the action button and its picker come first on the line, then the practices' fidelity dots, so the person chooses what to do before choosing where.

#### (S) Person --> Select Several Fidelities

Observed (commit a585473e3; `fidelity-progress-client.ts` `selectFidelity`): a press on a fidelity, on the line or on the session card, adds it to or takes it out of the selection, and the action button runs one command on every selected fidelity. Requested on 2026-11-06 ("multi select").

#### (S) Person --> Choose Action

Observed: the ▾ on the action button opens a list of generate, validate, review, iterate, sketch, render and document, with the fidelity's next one marked next; picking one puts it on the button in place of the next action (`action-button-view.tsx` `PickerView`).

#### (S) Person --> Choose Format

Observed (commits a6ddef81c, 21a87f4a7; `chat-bar-view.tsx`, `format-choices-client.ts`): one chip per format group the fidelities offer sits just before the action button, as on a board ticket; a press turns it on or off, and the picked formats go into generate and render. Requested on 2026-11-06 ("add format multi select"). Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "Toggle formats on the card, as the format chips do on the bar"): the session card carries the same chips.

#### (S) Person --> Generate Session Fidelity Output

Observed: pressing the button on generate puts the commands of `ticket.generate_commands` for the fidelity's default format in the prompt box, a render first when the fidelity before it uses another format; the person presses Enter to send them (`fidelity-client.ts` `runAction`).

#### (S) Claude Code --> Resolve Session Fidelity Output Paths

Observed: `Generate` and `Session.fidelity_outputs` take the outputs the fidelity declares, with the session's `session.json` overrides, as on the CDD Kanban.

#### (S) Person --> Fill Prompt With Fidelity Action

Observed: pressing the button on validate, render, iterate, sketch or document puts `/actions-<action> <guidance>` in the prompt box for the person to send (`fidelity-client.ts` `runAction`).


#### (S) Person --> [Apply Chosen Overlays To Fidelity Action](../story_tests/move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar/generate_fidelity_outputs_in_chat_bar_story.test.md#story-apply-chosen-overlays-to-fidelity-action)

Requested (2026-11-11, "doesnt result in LERN being passed in as a param? shouldnt it?"): the command the action button puts in the prompt names the session's chosen overlays in an `overlays=` word beside `format=` (`overlay-choices-client.ts` `overlayArgumentOf`); an action run with that word chooses those overlays on the session first (`WorkList.take`), and Generate adds each overlay's shared rules on top of the practices' rules (`Generate._overlay_rules`).
### (E) Review Fidelity Outputs In Chat Bar

#### (S) Person --> List Session Files, View Session Files

Moved (2026-11-15) to [Review Generated Work In File Viewer](#e-review-generated-work-in-file-viewer) as Open Stage Files From Chat Bar, Open Session Folder From Chat Bar and List Files The Link Names: the chat bar's files button and session name open the Files app beside the chat, no longer a tab per file in the chat bar.

#### (S) Person --> Open Validation Report From Violation Count

Observed (chat-ui story map, View Fidelity Files): pressing a fidelity's red violation count opens its latest report, from `fidelity-progress.report`, in its own tab drawn as markdown. Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "open its validation report"): the session card opens a practice's report too.

#### (S) Person --> Fix Violations From Chat Bar

Requested (2026-11-06, as the CDD Kanban does): the chat bar sends Fix and Fix all for the report it opens.

### (E) Integrate Practice Content Editor Apps In Chat Bar

#### (S) Person --> Open Editor App From App Status Row

Requested (2026-11-06, "chat band -> story UI side panel"; 2026-11-12, "same but for KG"; 2026-11-12, the CDD Kanban): the chat bar's app status row lists each editor app with its status; clicking one installs it when it is not installed, launches it when it is down, and opens it in the side panel. Examples: the Story UI editor, the Graph app, the CDD Kanban.

#### (S) Person --> Open Stories File In Story UI Editor

Requested (2026-11-12): the file viewer shows a story-map editor tile for every Stories file, which opens that file in the Story UI editor on the active session's story map.

#### (S) Graph App --> Load Session Folders In Graph

Requested (2026-11-12, "same but for KG"): the Graph app opened from the chat bar loads the folders the session's practice roots name.

#### (S) Graph App --> Follow Last Activated Session

Requested (2026-11-12, "same but for KG"): the open Graph app follows the session activated last.

#### (S) Person --> [Invoke Claude Design Story Explorer From Chat Bar](../story_tests/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/integrate_practice_content_editor_apps_in_chat_bar_story.test.md#story-invoke-claude-design-story-explorer-from-chat-bar)

Intended (requested on 2026-11-06, as the CDD Kanban): the chat bar opens the Claude Design story explorer the design canvas draws today (`explorer.dc.html`) on the active session's story map and screens. Requested (2026-11-12, for now): the file viewer has a link that opens the design view attached to the session.

#### (S) Story UI App --> Show Board's Active Ticket In Story UI

Requested (2026-11-06, non-functional): the Story UI app runs on the same app server and instance as the board's state, so the story map, the explorer and the board share one state for the active ticket. Requested (2026-11-12): built with the cdd_web_domain_access and lern_domain_driven patterns. The repeatable behaviour: the board's server serves the Story UI editor, which shows the ticket activated on the board.

#### (S) Person --> [Open UX Design In Claude Design](../story_tests/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/integrate_practice_content_editor_apps_in_chat_bar_story.test.md#story-open-ux-design-in-claude-design)

Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "claude design integration with ux tool"): the UX practice's design opens in Claude Design from the chat.

#### (S) Person --> [Trace Story Through Artifacts](../story_tests/move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar/integrate_practice_content_editor_apps_in_chat_bar_story.test.md#story-trace-story-through-artifacts)

Intended (`.sessions/_backlog/integrate-practice-content-editor-apps.md` "Trace pane"): picking a story shows its scenarios, tests and code from `harness/graph`, with the domain, class and bounded-context diagrams. Built today (checked 2026-11-10): the Graph app folds story, scenario and step and shows a step's invokes, observes and demonstrates with its source (`harness/graph/app/app.test.tsx:429,746`). Missing: one trace view of a picked story's scenarios, tests and code, and the diagrams.

### (E) [Edit Story Map Files In Story UI](../story_tests/move-work-forward-from-chat-bar/edit-story-map-files-in-story-ui/edit_story_map_files_in_story_ui_story.test.md)

The Story UI editor edits a story map, its descriptions and increments, and its scenario files through the CDD domain, and links each story to its acceptance tests. Grouped on 2026-11-24 from Integrate Practice Content Editor Apps In Chat Bar, with the scenarios of Refactor Story UI App To Web Domain Access, a story of the scenario file that was on no story of the map.

#### (S) Story UI App --> [Save Story Map Edit Through Domain](../story_tests/move-work-forward-from-chat-bar/edit-story-map-files-in-story-ui/edit_story_map_files_in_story_ui_story.test.md#story-save-story-map-edit-through-domain)

Requested (2026-11-06, non-functional): the Story UI app reaches the CDD domain through the TypeScript language adapter generated by the cdd_web_domain_access pattern, instead of its own calls. Requested (2026-11-12): the story map's backend moves out of TypeScript into the MCP-generated domain objects, not a JSON story map; each edit is saved and rendered to the formats chosen in the chat bar, which the Story UI app can toggle. Its scenarios were the scenario file's story Refactor Story UI App To Web Domain Access, split on 2026-11-24.

#### (S) Person --> [Edit Descriptions And Increments On Story Map](../story_tests/move-work-forward-from-chat-bar/edit-story-map-files-in-story-ui/edit_story_map_files_in_story_ui_story.test.md#story-edit-descriptions-and-increments-on-story-map)

Requested (2026-11-12, `harness/.context/grill-answers.md`): a story's, an epic's and a sub-epic's description is the paragraph under its heading and is edited there, and increments are edited through the story map and kept in its thin slice, every other line staying as written. Split from Refactor Story UI App To Web Domain Access on 2026-11-24.

#### (S) Person --> [Edit Scenario Files Through Story Model](../story_tests/move-work-forward-from-chat-bar/edit-story-map-files-in-story-ui/edit_story_map_files_in_story_ui_story.test.md#story-edit-scenario-files-through-story-model)

Requested (2026-11-12, `harness/.context/grill-answers.md`): a scenario file is edited in the Story UI editor through the story model, and an example's cell is written back in its row, an example keeping the place its table gives it. Split from Refactor Story UI App To Web Domain Access on 2026-11-24.

#### (S) Story UI App --> [Link Story To Its Acceptance Tests](../story_tests/move-work-forward-from-chat-bar/edit-story-map-files-in-story-ui/edit_story_map_files_in_story_ui_story.test.md#story-link-story-to-its-acceptance-tests)

Decided (2026-11-12, `harness/.context/grill-answers.md`): a story's acceptance tests are links that open in the file viewer of the chat that opened the editor, never edited; an editor no chat opened names the file and says where to read it. Split from Refactor Story UI App To Web Domain Access on 2026-11-24.

### (E) Capture Session Knowledge

#### (S) Claude Code --> [Write Handoff When Session Ends](../story_tests/move-work-forward-from-chat-bar/capture-session-knowledge/capture_session_knowledge_story.test.md#story-write-handoff-when-session-ends)

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Automatic handoff"): the handoff is written when a session ends, so the next session never starts cold. Built today (checked 2026-11-10): closing or leaving a session from the chat bar offers Create handoff, on by default (`session-dialogs-view.tsx:34`). Missing: writing one when a Claude Code session ends.

#### (S) Claude Code --> [Offer Correction Log Entry](../story_tests/move-work-forward-from-chat-bar/capture-session-knowledge/capture_session_knowledge_story.test.md#story-offer-correction-log-entry)

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Correction capture"): `$.model.classify` spots when the person corrects generated work and offers, in the chat panel, to add it to `corrections.log` beside that work.

#### (S) Claude Code --> [Offer Decision Record](../story_tests/move-work-forward-from-chat-bar/capture-session-knowledge/capture_session_knowledge_story.test.md#story-offer-decision-record)

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Correction capture"): the same check spots a decision and offers to write a CDR for it.

## (E) Enter CDD Commands Faster

### (S) Claude Code --> Autocomplete CDD Commands

Intended (`.sessions/_backlog/enter-commands-faster.md` "Command entry and autocomplete"; `.sessions/_backlog/enter-commands-faster.md` "constrained lists params on commands"): `prompt.autocomplete` offers an action, then a practice-fidelity, then content or a file, taken from the installed CDD catalog so the lists cannot drift.

### (S) Claude Code --> Show Command Argument Hints

Intended (`.sessions/_backlog/enter-commands-faster.md` "argumentHint"): after a command's name, the prompt shows the parameters it expects.

### (S) Claude Code --> [Suggest Next Command](../story_tests/move-work-forward-from-chat-bar/enter-cdd-commands-faster/enter_cdd_commands_faster_story.test.md#story-suggest-next-command)

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Next-step suggestion"): after each turn, `$.prompt.suggest` fills in the next command from `ticket.generate_commands`. Requested (2026-11-06, "the list box of actions should be on the next action recommended"): the recommendation shows on the chat band's action list box, marked recommended and set on ▶, not in the chat panel. Built today (checked 2026-11-10): the action button shows the fidelity's next action and the action list marks it next (`action-button-view.tsx:20-25,77-83`), which covers the 2026-11-06 request. Missing: `prompt.suggest` after a turn.

### (S) Claude Code --> Announce CDD Tool Calls

Intended (`.sessions/_backlog/enter-commands-faster.md` "Hooks and notifications"): every CDD tool call shows a toast naming the action or practice that ran, with an optional sound, as `tools/prompt_notify` does for Cursor.

## (E) Guard Work Against Rules

### (S) Claude Code --> Refuse Forbidden Edits

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Rule guards"): `tool.call` refuses edits to `.claude/` or `.mcp.json`, writes to `AGENTS.md`, and a bare `git stash`, and says which rule forbids it.

### (S) Claude Code --> Warn When Work Outruns Fidelity

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Stage guard"): a warning shows when work runs ahead of the active ticket's fidelity, such as production code while the ticket is in Discovery.

### (S) Claude Code --> Catch Banned Words In Markdown

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Banned word check"): a markdown write that uses a writing-guidelines banned word is caught before it reaches the file.

### (S) Claude Code --> Warn On Branch Mismatch

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "Branch guard"): a warning shows before a commit when the branch does not match the active ticket's session.

# (E) Queue Prompts For Later

The prompt queue is its own Claude Code mod, `prompt-queue`, not part of the CDD chat bar: it sits above the chat bar, at rest only a stack image with the count drawn on it (the person, 2026-11-16: "this shouldnt be part of the cdd chat bar / it should be above it with some separation / a separate mod from chat ui"). Sources: the brief that started the simple-queue chat on 2026-11-16 (stack above the prompt, a `+` button, Ctrl+Enter, reordering, a sub-agent mode, sending on `turn.complete` ahead of Claude's own queue, a `/queue` command) and the person's directions in that chat. The mod is `tools/prompt_queue/hooks/`, published by the installer, with its `claude plugin test` specs in `register.test.tsx`. Evidence words as on the chat bar epics: **Observed** seen working in the desktop chat, **Built** in code and plugin tests but not seen, **Intended** asked for and not done.

Grouped on 2026-11-17 into four sub-epics, as the epic had grown to sixteen children: Build Prompt Queue (the person puts work on the queue and shapes it), Work Through Prompt Queue (play, pause and the agent take the work in order), Nest Prompt Steps In Queue (each card's steps), and Share Queue Among Robots (sub-agent mode). The story names stay as they were. On 2026-11-24 a fifth, Keep Queue Files Safe, took the two stories exploratory testing added to Build Prompt Queue about the queue's file. Later on 2026-11-24 a sixth, Track Working Prompt From Chat, took the stories of Nest Prompt Steps In Queue about the prompt being worked following the chat, as that sub-epic had grown to eleven stories.

## (E) [Build Prompt Queue](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md)

The person puts work on the chat's queue and shapes it before it runs: queues a draft as it is, has the model place a draft or the conversation into the plan, keeps a draft's images with it, and opens, edits, reorders and removes the cards. Every change goes through the cdd server's `prompt-queue.*` tools (`tools/prompt_queue/prompt_queue.py`), and the mod draws the queue the server answers (`tools/prompt_queue/hooks/queue/prompt-queue.ts`).

### (S) Person --> [Queue Draft Prompt](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-queue-draft-prompt)

Observed (2026-11-16): the `+` beside the stack moves the prompt box's draft to the bottom of the queue and empties the box (`queueDraft`); the `+` shows when the pointer is on the stack. Ctrl+Enter did not work on the desktop, so the key is Alt+Enter. Built: Alt+Enter queues the draft (`queueByKey`), and a submission that follows it is dropped, "Queued for later" (`isQueuedByKey`). Changed (2026-11-17, commit 54e73186a): the `+` no longer moves the draft as it is; it places the draft into the plan (Place Draft Into Plan), and Alt+Enter is the plain add.

### (S) Person --> [Place Draft Into Plan](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-place-draft-into-plan)

Built (2026-11-17), not seen (commits f803207ae, 54e73186a; `register.test.tsx` "+ files the draft as a task of the goal the model picks", "/queue with a draft places it into the plan the way + does"): the `+` on the band runs /queue on the prompt box's draft (`queueDraft`). /queue given a draft has the model read this conversation and the goals on the queue, each with its id, and place each piece of the draft (`placeDraft`): a piece about a goal on the queue becomes a task of that goal, marked [interruption] (`prompt-queue.add_interruption`); a piece no goal covers becomes a card of its own (`prompt-queue.add`). Neither gives a card a robot: the agents button groups the work into robots. The prompt box empties once the draft is placed and keeps it when the model could not place it; an edited prompt goes back in its place instead. Observed (2026-11-17, a pasted list answered "Queued 0 prompt(s)"), then built: /queue given a pasted list queues each item in order without asking the model (`listedItems`).

### (S) Person --> [Plan Queue From Conversation](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-plan-queue-from-conversation)

Built, not seen: `/queue [what to focus on]` has the model read the conversation and adds the next prompts it lists to the queue, in order (`planFromConversation`). Built: when the model proposes none, /queue says so with what the model answered.

### (S) Person --> [Attach Images To Queued Prompt](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-attach-images-to-queued-prompt)

Built (2026-11-17), not seen (the person's /queue: "add images / attachments in chat along with text"): a plugin cannot send images with a prompt (`$.prompt.submit`: pasted images are not expanded for a plugin's prompt), so when Alt+Enter queues a draft, the images and documents pasted in it, which the dropped submission carries, are read (`$.prompt.media`) and kept as files beside the queued prompt (`prompt-queue.attach`, the chat's `attachments` folder). The queue beside a prompt lists each file for the agent to open, and the card shows 📎 with how many. The `+` button reads only the draft's text, so it queues no images. Story test: [attach_images_to_queued_prompt_story.test.py](../story_tests/queue-prompts-for-later/build-prompt-queue/attach-images-to-queued-prompt/attach_images_to_queued_prompt_story.test.py).

### (S) Person --> [Open Prompt Queue](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-open-prompt-queue)

Observed (2026-11-16): pressing the stack image opens the queue upward: one rounded card per prompt, in the order they will be sent, with the controls staying where they were at the bottom; an empty queue shows "Add" beside Alt and ↵ key caps. Pressing it again closes it. Built (2026-11-17), not seen (the person's /queue): the open queue and each card fill the chat box's width, a card's hover buttons sit on solid grey so they read over its text, the card being worked is bright. Observed (2026-11-17, the person: "looks great"): the card being worked has an orange rounded border around its button and its text bold and underlined; a button's text takes no colour of its own, so the orange is in the border. Observed (2026-11-17, the person: "Dim, good"), asked as "dont remove done items, dim them": prompt-queue.done marks a prompt done and keeps it in its place, drawn dim with its steps; play, the stack's count and the queue the agent reads pass over done prompts, and clear takes the done prompts off first, everything only when none is done. Built (2026-11-17), not seen (the person's /queue: "use the same exception handling / fix defect button that the rest of cdd uses"): the queue draws no failure line of its own; it keeps its latest failure, numbered, and the CDD chat bar's one failure line shows it with the same Fix (`/space-session-debug-session choice=fix`) and ✕, which hide it there by its number. Only a plugin writes its own stored values, so the board reads the queue's.

### (S) Person --> [Edit Queued Prompt](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-edit-queued-prompt)

Built (2026-11-16, the person: "right side of every queue item so we can edit before the arrows"; then "we should not lose positioning when we edit an item, keep it in list but shaded; adding to queue adds to the edited option"): the pencil on a card puts its prompt in the prompt box; the card keeps its place, shaded and marked editing, and is not sent while it waits; the next add, Alt+Enter or `+`, puts the changed text back in that place (`editPrompt`).

### (S) Person --> [Reorder Queued Prompts](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-reorder-queued-prompts)

Built: the ↑ and ↓ on a card move its prompt one place (`movePrompt`). Intended (the brief): drag a card to its new place; a drag list was built and taken out on 2026-11-16, as the desktop never drew it.

### (S) Person --> [Remove Queued Prompts](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-remove-queued-prompts)

Built: the ✕ on a card takes its prompt off the queue (`removePrompt`); the bin clears the whole queue (`clearQueue`). Built (2026-11-17), not seen (the person: "when deleting a queue (eg clear all) make sure we save a copy of the json so we have an archive of the work"): every prompt clear or remove takes off is kept as JSON in the chat's `queue-archive` folder, one file for each time, named for when they were taken off, with the prompts' steps and attachments. Built (2026-11-17): in a session the copy goes to the session's work folder, `.sessions/<session>/queue-archive`, in the ticket's worktree (`PromptQueue.load`).

### (S) Person --> [Flush Prompt Queue](../story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md#story-flush-prompt-queue)

Built (2026-11-23), not seen (the person: "add a flush button that does what I just asked when I click it, eg time stamped copy of queue file then delete finished bots"): the flush button on the queue's toolbar, beside the bin, calls `prompt-queue.flush` (`flushQueue`), which keeps a copy of the whole queue file as it stood in the queue archive, named for when, such as `prompt-queue-20261124T044511Z.json`, then takes the done cards off as clear does, leaving the work still to do in order (`PromptQueue.flush`). With no card done it still keeps the copy and takes nothing off. Story test: [flush_prompt_queue_story.test.py](../story_tests/queue-prompts-for-later/build-prompt-queue/flush-prompt-queue/flush_prompt_queue_story.test.py).

## (E) [Keep Queue Files Safe](../story_tests/queue-prompts-for-later/keep-queue-files-safe/keep_queue_files_safe_story.test.md)

The cdd server keeps each chat's prompt queue in one file in that chat's own folder, and every caller, the mod, the agent and both lanes' cdd servers, changes that one file (`tools/prompt_queue/prompt_queue.py`). The queue stays whole however it is reached: every caller's change is kept, a file nobody can read is refused and left for a person to repair, and no queue file is written outside the chats folder. Moved out of Build Prompt Queue on 2026-11-24 (closing choice 13 of the release-1-2-fixes exploratory testing), with the scenarios of Queue Draft Prompt about callers changing the queue at once.

### (S:system) Cdd Server --> [Keep Every Caller's Queue Change](../story_tests/queue-prompts-for-later/keep-queue-files-safe/keep_queue_files_safe_story.test.md#story-keep-every-callers-queue-change)

Observed (2026-11-19, exploratory-testing defects sparky-01, 02; `PromptQueue` holds the queue's file from its read to its write; `prompt_queue_spec.py`, `prompt_queue_processes_heavy_spec.py`): callers that change one queue at the same moment, on one cdd server or on both lanes' servers, each keep their change; a reader is shown the whole queue while another caller changes it; a caller killed while it held the file blocks nobody; and a change that waits for the file in vain is told the file is held, with its path. Split from Queue Draft Prompt on 2026-11-24.

### (S) Agent --> [Refuse Queue File That Holds No Queue](../story_tests/queue-prompts-for-later/keep-queue-files-safe/keep_queue_files_safe_story.test.md#story-refuse-queue-file-that-holds-no-queue)

Observed (2026-11-19, `tools/prompt_queue/prompt_queue.py` `QueueFileUnreadable`; `prompt_queue_spec.py`, `harness/installation/json_file_spec.py`): a queue file that is cut off, is empty, holds a list, or holds cards with no id or a shared id is refused with the file's path, and nothing is written over it, so a person can repair it; a file saved with a byte-order mark is read.

### (S) Agent --> [Name Queue By Chat Id](../story_tests/queue-prompts-for-later/keep-queue-files-safe/keep_queue_files_safe_story.test.md#story-name-queue-by-chat-id)

Observed (2026-11-19, `PromptQueue.of_chat`, `ChatIdNotAnId`; `prompt_queue_spec.py`, `prompt_queue_heavy_spec.py`): a chat's queue is kept in that chat's own folder under the chats folder, and a chat id that is a path, holds a separator or a drive, or is empty is refused, so no queue file is written outside the chats folder.

## (E) [Work Through Prompt Queue](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md)

The queue is kept by the cdd server, so the mod, the agent in the chat and a session starting in it change one queue (`tools/prompt_queue/prompt_queue.py`, MCP tools `prompt-queue.*`). The agent works through it: it reads the queue, does each prompt in order, and marks each one done. The person sets the pace: plays and pauses the queue, sends a card now, and moves the queue's pointer back to rerun a card or forward to pass one.

### (S) Agent --> [Queue Prompts Through The Cdd Server](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-queue-prompts-through-the-cdd-server)

Observed (2026-11-17): this chat queued its unfinished items with `prompt-queue.add_all` and took each off with `prompt-queue.done` as it finished it; `prompt_queue_heavy_spec.py` runs them on a real cdd server.

### (S:system) Cdd Server --> [Queue Handoff Steps On Session Start](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-queue-handoff-steps-on-session-start)

Built (2026-11-17): switching a chat to a session queues the numbered steps of its latest handoff's Approach for Next Agent on that chat's queue, once per handoff, and the switch says so (`OpenSessions._handoff_queued_note`, `PromptQueue.queue_handoff`); `session_spec.py` checks it.

### (S) Prompt Queue --> [Show Prompt Queue To Agent](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-show-prompt-queue-to-agent)

Observed (2026-11-17): while play is on, every prompt carries the queue, in order with each prompt's id, and how to work through it (`queueContext`); a paused queue carries nothing, and a prompt the person is editing is left out.

### (S) Person --> [Play Prompt Queue](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-play-prompt-queue)

Observed (2026-11-17, the person: "an agentic instruction with prompts to ai that they are responsible for taking the next item rather than it being forced on them ... don't remove it from the queue, have that be an operation the ai does"): while play is on, a finished turn asks the agent to take the next prompt ("Take the next prompt on the queue."), and the queue stays as it is until the agent marks a prompt done (`sendNextPrompt`). Play pauses when the agent left the prompt it was asked to take. A queued slash command runs as that command (`$.command.run`), which the agent cannot type, and the mod marks it done. Until 2026-11-17 play sent the next prompt itself and took it off the queue.

### (S) Person --> [Pause Prompt Queue](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-pause-prompt-queue)

Built (2026-11-16): pause stops finished turns from sending the next prompt; the queue keeps its prompts until play is pressed again.

### (S) Prompt Queue --> [Wait For Answer Before Moving On](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-wait-for-answer-before-moving-on)

Observed (2026-11-17): the agent ended a turn asking the person to check the robots' queues; with no answer in a minute, play sent the agent "No answer came within a minute. Put prompt [0b21ea030467] back on the queue as unfinished...", and the agent marked the card [decision required]. Built (2026-11-17), not seen (the person: "never go idle - always proceed to next item -- if blocked on task by decision put item onto queue with a flag required decision and move onto next item, maybe have a timer"; then "if i dont answer after a minute time out, back in queue as unfinished and move on to next"): while play is on, a turn the agent ends asking the person something (its wrap-up names a question or says it is blocked) does not send the next prompt at once; play waits a minute (`waitForDecision`). A turn starting in that minute, the person's answer, ends the wait. With no answer, the agent is told to put the prompt back on the queue with a text starting "[decision required]", the question and its recommendation, and take the next prompt (`decisionTimedOut`); play and the queue the agent reads pass over prompts marked that way.

### (S) Person --> [Send Queued Prompt Now](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-send-queued-prompt-now)

Built (2026-11-17), not seen (the person's /queue: "send now button"): the ↵ on a card moves its prompt to the top of the queue and sends it to the chat at once, playing or not, as "Take prompt [id] on the queue now: …", so the agent knows the id to mark it done; it becomes the prompt being worked.

### (S) Person --> [Move Queue Pointer](../story_tests/queue-prompts-for-later/work-through-prompt-queue/work_through_prompt_queue_story.test.md#story-move-queue-pointer)

Observed (2026-11-17, commits 89c85aa52, c0e3a1875, 1ca7fc939): the run2 demo's cards were rerun through the queue's pointer, which reopened each with `prompt-queue.reopen`. Built (2026-11-17, commits c2cff7454, 0173f75bf; `register.test.tsx` "▲ on the pointer opens the done card above it again, so it runs again"): the queue's pointer stands at the left of the next card to do, the first card neither done nor marked [decision required], and under the last card when every card is done (`pointerOf`). ▲, "Set previous to current", opens the nearest done card above it again, its steps not started (`movePointerUp`, `prompt-queue.reopen`), so play runs it again; ▼, "Set next to current", marks the card it points at done (`movePointerDown`, `prompt-queue.done`), so play moves past it. The orange working mark stands on the pointer's card, whichever card the agent last touched, so it moves with the pointer. In sub-agent mode each robot's queue has its own pointer.

## (E) [Nest Prompt Steps In Queue](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md)

Intended (2026-11-17, the person: "for each action you'll come up with a task list ... I want these to be synchronized ... you nest six or seven tasks in them and check those off in a nested way"; the plan they agreed in the simple-queue-enhancements chat): the queue holds both levels, the prompts the person queued and, under each, the steps the agent planned for it, so the queue box and the agent's task list show one plan. Decided with it: the cdd server stays the one owner of the queue and its steps. The queue does not move to Claude Code's own task store, `~/.claude/tasks` (TaskCreate, TaskUpdate): those tools are undocumented, hold flat lists linked only by blockedBy, their tool-call hooks were reported not to fire, and in the desktop app the agent's task list is the app's own `update_plan`, not TaskCreate.

### (S) Agent --> [Set Steps Of Queued Prompt](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md#story-set-steps-of-queued-prompt)

Built (2026-11-17), not seen: the agent gives a queued prompt its steps, each pending, being worked, or done, through a new prompt-queue tool on the cdd server, and the queue answers the prompt with them.

### (S) Agent --> [Tick Off Prompt Step](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md#story-tick-off-prompt-step)

Built (2026-11-17), not seen: the agent marks one step of a prompt done (`prompt-queue.step_done`); once every step is done the prompt is ready for `prompt-queue.done`, which still takes it off the queue.

### (S) Person --> [Show Prompt Steps In Queue](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md#story-show-prompt-steps-in-queue)

Built (2026-11-17), not seen: each card shows how many of its steps are done (3/7) as a button that opens its steps under it, done ones ticked and dim and the one being worked marked; the card being worked is bright and a card whose steps are all done dim. Built (2026-11-24), not seen (main's chat-ui-defects, a goal with 77 interruption steps: "its finished steps folded away"; `register.test.tsx` "a card's finished steps fold into one line under it once there are three, the steps still to do shown"): once a card holds three or more finished steps, every step above its step pointer folds into one line, "▸ ✓ 3 done", which shows them again when pressed ("▾ ✓ 3 done") (`toggleDoneSteps`, `shownDoneSteps`).

### (S) Person --> [Edit Prompt Steps](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md#story-edit-prompt-steps)

Built (2026-11-17), not seen (the person: "i want to add steps sometimes ... 2/5 click opens + - up down just like queue"): with the pointer on a card, + adds the prompt box's draft as the card's last step, not started, empties the box and opens the steps (`addStep`); with the pointer on an open step, ↑ and ↓ move it one place (`moveStep`) and ✕ takes it off (`removeStep`). Each change gives the prompt its whole list through `prompt-queue.set_steps`; for the prompt being worked the agent's task list then carries on from the changed steps. Built (2026-11-17, commit 3d19477a7): ✎ on a step with the prompt box empty puts the step's text in the box to change; with a draft in the box, the draft becomes the step's text and the box empties (`editStep`).

### (S) Person --> [Send Prompt Step Now](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md#story-send-prompt-step-now)

Built (2026-11-17), not seen (commit 3d19477a7, the person: a step has all of a card's buttons): ↵ on a step sends that step of its prompt to the chat at once, as "Take step 2 of prompt [a] on the queue now: …", and its prompt becomes the one being worked (`sendStepNow`).

### (S) Person --> [Move Step Pointer](../story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md#story-move-step-pointer)

Built (2026-11-17, commit c2cff7454): a card's open steps have a pointer of their own at the left of the first step not done (`QueuedPrompt.step_pointer`, which the server answers). ▲ works the done step above it again and puts every step after it back to not started (`prompt-queue.step_back`); ▼ marks its step done and starts the next (`prompt-queue.step_on`). A step's ↑, ↓ and ✕ each call one tool too (`prompt-queue.move_step`, `prompt-queue.remove_step`), so the mod and the agent follow the server's one rule.

## (E) [Track Working Prompt From Chat](../story_tests/queue-prompts-for-later/track-working-prompt-from-chat/track_working_prompt_from_chat_story.test.md)

The prompt being worked follows the chat: it takes the agent's task list, a prompt the person sends straight to the chat goes on the queue as the one being worked, and a message the person sends while a goal is worked is filed under that goal, titled by what it asks, or split off again. Grouped on 2026-11-24 from Nest Prompt Steps In Queue, which had grown to eleven stories.

### (S:system) Prompt Queue --> [Copy Task List Onto Working Prompt](../story_tests/queue-prompts-for-later/track-working-prompt-from-chat/track_working_prompt_from_chat_story.test.md#story-copy-task-list-onto-working-prompt)

Observed (2026-11-17): after /reload-plugins, the person's prompt "?" went first on the queue as the one being worked, and the agent's task list was copied onto it as five steps (prompt-queue.show). Built (2026-11-17): the queue mod's `tool.call` hook replays each `update_plan` call (a whole list, advance, done, start) and copies the list onto the prompt being worked with `prompt-queue.set_steps`; a `wrap_up` finishes every step. Not yet seen: whether the desktop app hands the mod's hook its own `update_plan` calls; until the mod has seen one, the queue beside a prompt tells the agent to set the steps and mark each one done itself.

Built (2026-11-17), not seen (the person: the queue and task list "doesnt make sense"; the steps had landed on the person's last message, not the queue item worked): the queue tells the agent to call `prompt-queue.set_steps` with a prompt's id when it takes it, and the mod's `tool.call` hook makes that prompt the one being worked (`followTakenPrompt`), so the task list's next changes follow onto it. A wrap-up still marks every step done, as the desktop app's own wrap-up checks off the task list.

### (S:system) Prompt Queue --> [Queue Sent Prompt As Running](../story_tests/queue-prompts-for-later/track-working-prompt-from-chat/track_working_prompt_from_chat_story.test.md#story-queue-sent-prompt-as-running)

Observed (2026-11-17): after /reload-plugins, the person's prompt "?" went first on the queue as the one being worked, and the agent's task list was copied onto it as five steps (prompt-queue.show). Built (2026-11-17): a prompt the person sends straight to the chat, not from the queue, goes on the queue first as the prompt being worked, and the agent is told its id to mark it done, so its steps have a prompt to sit under. Built (2026-11-17, `register.test.tsx` "a prompt sent straight to the chat goes above the next prompt to do, below the done ones, marked as an interruption"): the prompt goes just above the next prompt to do, below the done ones, its text starting "[interruption]"; a background task's notice arriving in the chat is not queued.

Replaced (2026-11-24, commit b3d0c6d56): a prompt the person sends straight to the chat is no longer put on the queue by the mod; the agent queues it when it is work, as Title Goal From Sent Message says. The scenarios that held the mod's queueing are gone; a background task's notice and play's own request are still left off the queue.

### (S:system) Prompt Queue --> [Add Interruption To Working Prompt](../story_tests/queue-prompts-for-later/track-working-prompt-from-chat/track_working_prompt_from_chat_story.test.md#story-add-interruption-to-working-prompt)

Observed (2026-11-17): after /reload-plugins, the person's message "heavy test are written and run in a sub task tho", sent between turns, was filed by the cdd server under the goal last worked as an "[interruption]" step, and the agent was told so. Built (2026-11-17), not seen (the person: "YES and update backend for this", to filing a message sent between turns under the goal last worked): the cdd server files a message under a goal (`prompt-queue.add_interruption`): it becomes the goal's last step, not started, marked "[interruption]", and a done goal opens again; the mod calls it for every message the person sends while a goal last worked is on the queue, mid-turn or between turns, and a card of its own is made only when there is none. Built (2026-11-17), not seen (the person: "you should be putting these interruptions into one goal and adding tasks to them, add smarter organizing instructions"): the queue tells the agent to keep one card for each goal: a message that belongs to a goal already on the queue becomes a task of that goal and its own card comes off, related [interruption] cards gather under one goal card, and the order stays done, being worked, not started. Observed (2026-11-17): a message the person sent while the agent worked the sub-agent columns prompt joined it as an "[interruption]" step, and the agent was told so. Built (2026-11-17), not seen (the person: "a new chat message from the edit box doesnt go to top of queue it goes above the active or next item in queue as an interruption OR inside current queue item as a task"): a message sent when no turn runs goes on the queue just above the next prompt to do, below the done ones, its text starting "[interruption]". Built (2026-11-17), not seen (the person: "if its a simple correction or comment in flight pertaining to a current queue then add it to the queues list as a task in process, put a special annotation in front and save that it was a user interruption"): a message the person sends while a turn runs on a queued prompt becomes a step of that prompt, its text starting "[interruption]", instead of a new card (`addInterruption`); the agent is told which prompt it joined and may move it to a card of its own with `prompt-queue.add` when it is separate work. A new task list from the agent keeps interruption steps it does not list (`keptInterruptions`). Observed (2026-11-23, the person: "wth"): the main chat's queue band read "70/77 1. [interruption] <pasted_content id="7250"> ## Notes from the backlog…": the chat's first message, a paste, became the goal with the raw paste and its tags as its title, and every later message was filed under it as an [interruption] step until it held 77. Built (2026-11-23, `register.test.tsx` "a message about new work sent between turns starts a goal of its own, not another step of the goal last worked", "a goal sent as pasted text is titled by the paste's first line, without its tags"): a message is filed under the goal last worked only while a turn works it or when its turn ended asking the person something; any other message sent between turns is new work, a goal of its own.

Replaced (2026-11-24, commit b3d0c6d56): the mod no longer files a message under the goal last worked; the agent files work for a goal with `prompt-queue.add_interruption` itself, as Title Goal From Sent Message says. The scenarios that held the mod's filing are gone; the cdd server's filing, and the robots' queues shown beside a message in sub-agent mode, stay. Built (2026-11-24, commit 140dba085; `register.test.tsx` "in sub-agent mode the note on a new message shows the robots' queues and lets the agent decide where it goes"), not seen: in sub-agent mode the agent is told to give a robot a card with `prompt-queue.assign`.

### (S:system) Prompt Queue --> [Title Goal From Sent Message](../story_tests/queue-prompts-for-later/track-working-prompt-from-chat/track_working_prompt_from_chat_story.test.md#story-title-goal-from-sent-message)

Built (2026-11-24), not seen (the person: "fix so messages dont create cards - the chat is notified to create the card; messages get sent to chat"; `register.test.tsx` "a message sent between turns puts nothing on the queue", "a message sent while a prompt is worked adds no step to it", "a pasted message puts nothing on the queue", "the agent is told the message is on no card and to queue it only when it is work, titled cleanly"): a message the person sends goes to the chat as sent and puts no card or step on the queue. The agent is told the message is on no card, with the goals still to do and the goal being worked, and decides: talk (a question, an answer, a complaint or a comment) is only answered; work for a goal is filed under it with `prompt-queue.add_interruption`; new work becomes a card of its own with `prompt-queue.add`, titled as a short statement of the goal with the typing mistakes and venting left out; then it reads the queue back with `prompt-queue.show` to check what it placed. A message that is only talk (`prompt-queue.is_only_talk`, `SentMessage` in `tools/prompt_queue/prompt_queue.py`) carries no note at all. This replaces the title the mod made from the message itself (`goalTitleOf`, removed), which kept the person's typing as the card's title. Split from Add Interruption To Working Prompt on 2026-11-24.

Built (2026-11-24, commits 3c5dbc74b, b123d6925), not seen (the person, on a question sent while a board viewer was open, which became a card titled by the viewer's state): talk, a question, an answer or a comment that asks for no work, is answered in the chat and never queued, mid-work or between turns (`register.test.tsx` "a message that is only talk, such as …, sent mid-work is not filed on the queue" and "… sent between turns is not queued"). The board viewer's state the Claude app puts before a message (`<artifact-view-context>`) is never read as the person's words: a "?" sent from a board viewer is talk, and the cdd server queues and files only the person's words, never the viewer's state, as a card's title or a step (`prompt_queue_spec.py` "queues only the person's words of a card sent from a board viewer", "files only the person's words of a message sent from a board viewer, leaving out the viewer's state", "files nothing under a goal for a message that holds only a board viewer's state"). Scenarios: Answer Talk Without Queueing It, Read Talk Sent From A Board Viewer By The Person's Words Alone, Keep A Board Viewer's State Out Of A Card's Title And Steps, File Nothing For A Message That Holds Only A Board Viewer's State.

### (S) Person --> [Split Goal Of Interruptions](../story_tests/queue-prompts-for-later/track-working-prompt-from-chat/track_working_prompt_from_chat_story.test.md#story-split-goal-of-interruptions)

Built (2026-11-24), not seen (main's chat-ui-defects: "a goal holding many unrelated interruptions is split"; `prompt_queue_spec.py` "that the goal is split", `register.test.tsx` "split on a card puts each interruption still to do on a card of its own, right after it"): the cdd server splits a goal (`prompt-queue.split`, `PromptQueue.split`): each [interruption] step not done becomes a card of its own, in order, right after the goal and given the goal's robot, and comes off the goal's steps; the goal keeps its own steps and the interruptions already done, and a goal with no interruption still to do changes nothing. A card whose goal holds an interruption still to do shows split, ⑂, among its buttons (`splitGoal`); the note beside a filed message tells the agent to split a goal's interruptions about other work with `prompt-queue.split`.

## (E) [Share Queue Among Robots](../story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md)

In sub-agent mode the queue's work is shared among robots: sub-agents that run side by side, each drawn as a Claude-orange robot with a fun name on top of its own queue of the queue's cards (the person: "visualize the use of sub agents: place tasks in columns, independent queues by sub agent name (allow naming, its fun!) with a robot on the top of each queue"). Each card keeps its robot on the cdd server's queue.

### (S) Person --> [Group Queue Into Robots](../story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md#story-group-queue-into-robots)

Observed (2026-11-17, the person: "its good"): with eight demo prompts in four independent two-step strands, switching sub-agent mode on had the model group them into four robots (Bolt, Gizmo, Rivet, Pixel) of two prompts each, side by side as the queue's own cards. Built (2026-11-17, commits bab265447, 81ae9ada6, 12e7c3a94, 52592da57): switching sub-agent mode on has the model group the work not done and given to no robot into tasks that can run side by side (`groupIntoTasks`); each task becomes a robot named apart from the robots already on the queue (Sparky, Bolt, Gizmo…), each of its cards is given that robot (`prompt-queue.assign`), and every robot's queue opens, so the work just handed out shows. The open queue draws one queue for each robot in the list's place, each with its own robot drawing (a different shade, eyes and antenna for each place), its name and what it does, the queues sharing the width evenly. A card whose text starts "[for Bolt]" shows in Bolt's queue.

Built (2026-11-24, commit 3c5dbc74b; `register.test.tsx` "switching sub-agent mode off takes every robot off the queue", "switching sub-agent mode off forgets the robots and their sub-agents"), not seen: switching sub-agent mode off gives every card to no robot and forgets the robots, their sub-agents and their open queues, as the work is the chat's own again. Scenario: Take Every Robot Off The Queue When Sub-Agent Mode Is Switched Off.

### (S:system) Cdd Server --> [Assign Queued Prompt To Robot](../story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md#story-assign-queued-prompt-to-robot)

Built (2026-11-17, commit 81ae9ada6; `prompt_queue_spec.py` "keeps the robot a prompt is assigned to on the queue, so its robot's queue comes back after a reload"): the cdd server keeps the robot each card is given (`prompt-queue.assign`), so each robot's queue comes back after a reload, when the mod no longer holds the grouping; an empty robot takes the card off its robot.

### (S) Person --> [Send Queued Prompts To Sub-Agents](../story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md#story-send-queued-prompts-to-sub-agents)

Observed (2026-11-17, run2 demo): pressing play sent the four robots off side by side; each wrote only into its own .sessions/simple-queue-enhancements/demo/run2/ folder and marked its own two cards done through prompt-queue.done, which stayed on the queue dimmed in its robot's queue; Pixel's timed lines show the robots ran at the same time. Built: with sub-agent mode on, sending starts one sub-agent for each robot with work not done, on its cards, described by the robot's name and what it does (`sendTasksToSubAgents`); the cards stay on the queue, so each sub-agent marks its own done. Built (2026-11-17, commit 5dcc4cf5f): a robot's card has the single queue's buttons, shown on hover; the card that opened in place under a robot is gone.

Built (2026-11-24, commit b123d6925; `register.test.tsx` "a sub-agent started for a card goes by the name of the card's robot on the queue, whatever name this chat wrote", "a sub-agent started for a card is remembered as the card's robot", "a robot whose sub-agent is known is handed its next card by that sub-agent's id"), not seen: a robot goes by its sub-agent's name. The hand-out asks that each robot's sub-agent be started with its card's id; the mod renames the sub-agent's description to the card's robot, whatever name this chat wrote, remembers the sub-agent as that robot's, and hands the robot its next card through that sub-agent with SendMessage. Scenarios: Start A Robot's Sub-Agent Under The Name Of The Card's Robot, Hand A Robot Its Next Card Through The Sub-Agent It Goes By.

### (S) Person --> [Rename Robot](../story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md#story-rename-robot)

Removed for now (2026-11-17, the person: "remove the edit bot name button for now, its distracting"); the robot shows its name only. Was built, not seen (the person: "allow naming, its fun!"): ✎ beside a robot's name renames it from the prompt box's draft, gives each of its cards the new name (`renameAgent`, `prompt-queue.assign`) and empties the box; the sub-agent starts with that name in its description.

### (S) Person --> [Collapse Robot Queue](../story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md#story-collapse-robot-queue)

Built (2026-11-17, commits 3320efd56, 8594772f9): pressing a robot collapses its queue to the robot alone, showing under it how many of its items are done, such as 3/5, and the other robots' queues widen to take the room; pressing it again expands it (`toggleCollapsedAgent`).

Built (2026-11-24, commit b123d6925; `register.test.tsx` "pressing a closed robot whose sub-agent is running shows that sub-agent's task in the main view", "pressing the open robot goes back to the main conversation"), not seen: pressing a robot whose sub-agent is running opens that sub-agent's view, the one the background tasks panel opens, as well as its queue; pressing the open robot goes back to the main conversation and closes its queue. Scenarios: Show A Robot's Running Sub-Agent When The Robot Is Pressed, Go Back To The Main Conversation When The Open Robot Is Pressed.

# (E) Review Generated Work In File Viewer

The file viewer is the Files app (`harness/files_app/`): a page of its own, opened beside the chat, where a person reads, filters and comments on the files a session generated, and, once its graph view is built, works the session's graph on those same files. Moved back (2026-11-15) from the Files app's own map, where release-2 had gathered every story about viewing a session's files on 2026-11-14 (commit 5aa8569f3); the person: "move the file viewer stories back to the main map under its own epic". Scenarios: [review_files_in_files_app_story.test.md](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md). Evidence words as there: **Observed** walked in the browser pane on 2026-11-14, **Built** in code and specs but not walked, **Intended** asked for and not done yet. The board's Review Files In Viewer sub-epic moved here on 2026-11-15; on 2026-11-21 (design proposal 24) the board's own files panel and its UI spec were removed, and the board opens the Files app instead.

Requested (2026-11-15): the file viewer becomes where the graph is worked too. A toggle at its top switches between its files and the graph; the graph view does what the Graph app does, but on the files the Files app lists, opening every file a person selects and folding them to the nodes selected. The person: "the actual file viewer is going to have a toggle that can switch from folder files and graph ... we basically ingest all of the stories and functionality that the Graph application can do except for you're now selecting file(s), eg more than one file opens; expand and collapse in file viewer based on the nodes in the graph; graph filtered like file filter is". Once these stories work, the Graph app's own epics (Explore Graph In Graph App, Filter Graph In Graph App, Review Violations In Graph App) retire into them.

## (E) Open Files In Files App

### (S) Person --> [Open Stage Files From Chat Bar](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-stage-files-from-chat-bar)

Built (2026-11-14): the chat bar's ▤ files button opens the Files app beside the chat on every fidelity of the shown stage, every practice's, so the app's practice toggles filter them (`fidelity-files-client.ts` `openStageFiles`). A folder chip on the session card opens one fidelity's files (`openFiles`). Was the chat bar's List Session Files, which opened a tab per file in the chat bar.

### (S) Person --> [Open Session Folder From Chat Bar](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-session-folder-from-chat-bar)

Observed (2026-11-14): pressing the session's name opens the Files app on `.sessions/<session>`, listing its log, handoffs, notes and reports (`openSessionFolder`, `session.folder_files`).

### (S) Story UI --> [Open File From Another Page](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-file-from-another-page)

Built: a page the chat opened, such as the Story UI editor, sends the chat an `open_file`, and the chat opens that file in the Files app on its session folder (`harness/chat-ui/pane/hooks/chat-bar/check-in-client.ts` `shown`, `openFileInViewer`).

### (S) Files App --> [List Files The Link Names](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-list-files-the-link-names)

Observed (2026-11-14): the page reads only the files its link names, each once, and never the board (`files-page.ts` `list`); a file not generated yet is listed but cannot be opened. Was View Fidelity Files on the board and the chat bar.

### (S) Person --> [Open Diagram In Files App](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-diagram-in-files-app)

Built (2026-11-15): a press on a `.drawio` file shows the draw.io editor in the file view, beside the file list, with a ↗ link to a tab of its own (`files-page-view.tsx` `DrawioFileView`); the app's browser pane opens no tab of its own, so a new tab took the Files app's place there. Was the chat bar's Open a diagram in the draw.io editor and the graph's Display Drawio File As Diagram; that story's Source tab and shape marking stay Intended.

### (S) Person --> [Open File In File Browser](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-file-in-file-browser)

Built (2026-11-15): a right-click on a file or folder shows a menu whose one choice opens it in the system's file browser, named for the system (`files-page.ts` `reveal`, `file-explorer.ts`).

### (S) Person --> [Switch File Bar Between Folders And List](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-switch-file-bar-between-folders-and-list)

Built (2026-11-14): the file bar collapses to its buttons and expands again, and shows its files as a list or in their folders, the open file's folders open (`file-bar.ts` *FileBar*, `files-page-view.tsx` `FileBarView`). Requested (the person, 2026-11-14): "expand collapse file bar with buttons to swap a folder view and file list".

## (E) Filter Files In Files App

What the file list shows follows the session's guidance selection and the chat bar's dots, so the same filter holds wherever the session is worked.


### (S) Person --> [Resize File Bar](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-resize-file-bar)

Built (2026-11-15): a line between the file bar and the open file drags the bar between 160 and 900 pixels wide, and this browser remembers the width (`file-bar.ts` `resize`).
### (S) Person --> [List Only The Files The Branch Changed](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-list-only-the-files-the-branch-changed)

Built (2026-11-15): the file bar's Changed button, with its count, lists only the files the session's branch changed, a published design canvas kept (`file-bar.ts` `toggleChangedOnly`, `entries`). Requested (the person, 2026-11-15): "Yes, add it", to a changed-only filter for a session on the whole repository, where UX's mockup pattern lists about 150 files.

### (S) Person --> Follow Chat Bar Selection In Files App

Built (2026-11-15): the chat bar sends its selected fidelity dots at check-in (`Chat.check_in` `selected_fidelities`, `Chat.show`); the Files app reads them every second and, while any it lists are selected, shows only their files, its practice toggles following the dots (`files-page.ts` `filesShown`, `isShown`). Requested (the person, 2026-11-15): "make sure that the filter in the Files window is inherited from the filter in the chatbar", pointing at the chat bar's fidelity dots.

### (S) Person --> Select Guidance On The Session

Built (2026-11-15): the stages, practices and format groups selected are one guidance selection the session holds (`Session.guidance_selection`, `toggle_guidance`, and the waiting read `guidance_selection_after`), with a version every change raises. Changed (2026-11-21, design proposal 14): a press names one stage, practice, or format group (`session.toggle_guidance`) and the session works out the selection, applying the ticket's stage first while nobody chose stages; the selection writes each action's command (`commands`), with the formats chosen. The chat bar and the Files app each follow it with one waiting read and draw a press at once; a practice's dot is the practice on or off for the session, all its fidelities of the stages selected. The chat's own selection, stage list, chip cache and refresh messages are gone. Requested (the person, 2026-11-15): "the CDD session object should already have this; it needs to follow the domain model: session.updateGuidanceSelection({stage, practice, format}) ... subscriber.notify()".

### (S) Person --> Show Stages In Files App And Chat Bar

Built (2026-11-15): the chat bar's single stage chip and its list become a button per stage, toggled on together; the dots show, and the action runs on, the fidelities of every stage shown. The Files app has the same buttons first in its header. The stages shown are the chat's, one choice held by cdd (`Chat.show_stages`), with each stage's fidelities listed by the chat bar from the board (`Chat.list_stages`). Requested (the person, 2026-11-15): "we don't have a sync for stages", "toggles to select one or more stage, default stage from chat bar", "a collection of buttons so you can toggle and generate across multiple stages; the action would then submit fidelities of all toggled-on stages", "and we have exact same thing on top of file viewer".

### (S) Person --> [Filter Files By Format In Files App](../story_tests/review-generated-work-in-file-viewer/filter-files-in-files-app/filter_files_in_files_app_story.test.md#story-filter-files-by-format-in-files-app)

Built (2026-11-15): format chips after the practice toggles, with the chat bar's glyphs (M↓, ◇, </>, ▦) and colours; a press chooses the format in the session (`ticket.choose_formats`), the same choice as the chat bar's chips, which read again on the refresh the page sends; while any is chosen the list shows only those formats' files (`format-chips.ts`, `filesShown`). Requested (the person, 2026-11-15): "we want formats to be a filter as well ... same exact functionality as practice filter; place buttons after practices; use same images as chat bar".

### (S) Person --> [Toggle Practice In Files App](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-toggle-practice-in-files-app)

Built (2026-11-14): the session's practices sit along the top as toggles, each in its practice colour, filled while on and an outline while off; a press turns the practice on or off for the session and the list shows only the files of the practices turned on (`files-page.ts` `togglePractice`, `practice_session_output.enable`). Requested (the person, 2026-11-14): "the patterns should be toggles at the top; be the practice color; and allow us to toggle the practice filter here". Builds on the board's Browse Ticket Files By Practice (2026-11-12): "put the filter toggles on the top".

### (S) Files App --> [Keep Chat Bar Practices In Sync](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-keep-chat-bar-practices-in-sync)

Built (2026-11-14): a practice turned on or off in the Files app sends the chat that opened it a `refresh`, and its chat bar reads the board again, so its fidelity dots show the same practices (`chat.send` kind `refresh`, `harness/chat-ui/pane/hooks/chat-bar/check-in-client.ts` `refreshed`); the page reads the practices again every three seconds while it shows (and when the person comes back to it), so a practice turned off on the chat bar or the board hides its files there with no press: a page in a side pane is never focused again (fixed 2026-11-14, the person: "the file filter needs to respect the practice that is toggled"). Requested (the person, 2026-11-14): "also toggles the command bar so they stay in sync".

## (E) View Files In Source View

The open file shows in the Files app's view, rendered or as source, and its code folds and carries the marks of the rules it breaks. Grouped on 2026-11-24 into two sub-epics, as it had grown to ten stories.

### (E) Read Files In Source View

The file opens rendered or as source, its links and callouts open in place, and its lines lay out for reading. Grouped on 2026-11-24 from View Files In Source View.

#### (S) Person --> [View File In Source View](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-view-file-in-source-view)

Observed (2026-11-14): the open file shows in the graph explorer's Monaco source view, read-only, its lines numbered and coloured by language (`file-source-view.tsx`, `@source-view/SourceView`). Was the board's View Files In Rich Viewer and the graph's Open Node Source.

Built (2026-11-19, requested: scenarios, story maps and domain models read as pages, their text a press away): a markdown, HTML, SVG or JSON file opens rendered, with Rendered and Source toggles leading the file's bar (`files/file-view.tsx`, `files/file-rendering.ts`); a file opened at lines asked for, such as a node selected in the graph view, opens in the source view. Markdown and SVG are cleaned with DOMPurify, markdown rendered with marked, both the versions Monaco already loads; an HTML page shows in a sandboxed frame that runs no script.

#### (S) Person --> [Render File As A Page](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-render-file-as-a-page)

Built (2026-11-19): a markdown, HTML, SVG or JSON file opens rendered as the page it describes, each format the page can draw, a generated UX mockup walked in its frame, front matter shown as the file's facts, a scenario's domain terms and examples underlined and an indented tree keeping its levels (`files/file-view.tsx`, `files/file-rendering.ts`). Split from View File In Source View on 2026-11-24.

#### (S) Person --> [Follow Links And Callouts In A File](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-follow-links-and-callouts-in-a-file)

Built: a link or a callout on a rendered page or in the source view opens what it names in place, or the file it names, and says what is not there for a heading or a file that is missing; the file view's filters choose which callouts show. Split from View File In Source View on 2026-11-24.

#### (S) Person --> [Lay Out Lines In Source View](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-lay-out-lines-in-source-view)

Built: the source view scrolls a long line sideways or wraps it, in Cursor's default colours with an orange cursor. Split from View File In Source View on 2026-11-24.

#### (S) Person --> Browse Files Without Reading Rules

Built (2026-11-15): Rules and Cross-file toggles at the top of the Files app, both off by default. With Rules on, `Session.file(rules=True)` reads the open file into the session's live graph when it changed (about 1.5 s) and answers its folds and broken rules, with the last validate's saved findings beside them, as the Graph app's source view shows them; Cross-file has the graph hold the whole working copy first (`Graph.hold_whole`). Fixed (2026-11-15): the two toggles are independent; Rules reads the file alone (`SessionGraph.alone`, a *DocumentGraph*, about 0.8 s), Cross-file adds only what the whole working copy finds. The person: "when loading files don't use cross file unless cross file is toggled, and vice versa". Requested (the person, 2026-11-15): "I don't see code folding in here I don't see any of the violations", then "toggle at top and have it off by default; for rules; same with cross file that way we don't incur a performance penalty when we just want to browse files".

#### (S) Person --> [Save Edited File](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-save-edited-file)

Intended: Edit turns the file editable and Save writes it through the file manager (`session.write_file`). The board's panel does it; the Files app is read-only today.

### (E) Fold And Mark Code In Source View

The source view folds a file's classes, operations and headings, opens the calls and classes the code reaches in place, and marks the lines a broken rule names. Grouped on 2026-11-24 from View Files In Source View.

#### (S) Person --> [Fold Classes And Operations](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-fold-classes-and-operations)

Built: the session's graph places each class and operation, and the source view folds each one as a block (`session.file` folds). Was the graph's Unfold Calls And Classes In Source.

Changed (2026-11-16, "native expand collapse for class functions, heading levels in markdown etc like a real IDE"): the source view folds with Monaco's own folding, classes, functions and blocks as Monaco reads the language, and markdown by its headings (`source/source-folding.ts` `foldMarkdownHeadings`), with or without Rules; the session's folds stay for the board's files panel.

#### (S) Person --> [Fold With Keyboard Shortcuts](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-fold-with-keyboard-shortcuts)

Requested (2026-11-16, "Cursor-equivalent keyboard shortcuts (or VS Code, configurable in a context config json), e.g. Ctrl+K Ctrl+0, Ctrl+M etc."). Built: VS Code's fold chords, which `.context/files-app-keybindings.json`, written as VS Code's keybindings.json, overrides command by command; a wrong file keeps VS Code's and a toast says why (`FoldKeys`, `FilesFoldKeys`).

#### (S) Person --> [Open Calls And Classes In Place](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-calls-and-classes-in-place)

Requested (2026-11-16, "too aggressive on the shading and double shading ... on expand, hide the callout label and show the content; on collapse, bring it back; only shade once"). Built: a call or class the code reaches is a callout like a markdown link's: a label after its line while closed; open, its lines alone in a view zone under the line, shaded once, a call inside it one shade deeper; never from a comment, a docstring or a string, and without the graph's `/* call: */` marks (`source/call-expansion.ts` *CallCatalog*, `source/source-callouts.ts`).

#### (S) Person --> [Mark Lines A Broken Rule Names](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-mark-lines-a-broken-rule-names)

Built: the rules the session's saved graph found broken in the file mark their lines with a rule chip (`session.file` violations). Was the graph's Open Violation In Source.

## (E) Review Files With Comments

### (S) Person --> [Add Comment To File Selection](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-add-comment-to-file-selection)

Observed (2026-11-14): select lines, right-click, Add comment; Enter adds the comment and sends it, Add keeps it unsent; a marker shows beside the selection's first line (`comment-box-view.tsx`, `file-comments.add`). The menu opened from the keyboard (Shift+F10); a right-click from the browser tool closed it at once, not yet checked by hand.

### (S) Person --> [Open Edit And Delete File Comment](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-open-edit-and-delete-file-comment)

Observed (2026-11-14): a press on the marker opens the comment under its lines with its state; Save keeps an edited comment, not sent again; Delete removes it.

### (S) Person --> [Send File Comments To Chat](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-send-file-comments-to-chat)

Observed (2026-11-14): a sent comment lands in the prompt box of the chat that opened the page, with its file, lines and session (`file-comments.send`, a fill); Send all open comments sends every comment not yet sent in one message.

### (S) Chat --> [Mark File Comment Processed](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-mark-file-comment-processed)

Built: a sent comment is processed once the chat's turn that worked on it has ended; the page reads the open file again every two seconds while a comment on it is sent (`SENT_REFRESH_MILLISECONDS`).

### (S) Files App --> [Show Changed File After Comment](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-show-changed-file-after-comment)

Built: when a comment on the open file is processed, the page shows the file as the chat changed it.

### (S) Person --> [Clear Processed File Comments](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-clear-processed-file-comments)

Built: Clear processed removes the processed comments and keeps the ones not sent or still sent. Not walked: no comment was processed on 2026-11-14.

### (S) Files App --> [Show AI Changes As Diff](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-show-ai-changes-as-diff)

Intended: the page marks what the chat changed in the file, as VS Code and Cursor do (`SessionFile.changes`); the board's panel draws it, the Files app does not yet.

### (S) Person --> [Add File Or Selection To Chat Context](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md#story-add-file-or-selection-to-chat-context)

Requested (2026-11-15, "on right click of file we also need an add to context option; same with selected text in file viewer; adds to chat context like Claude functionality does in file viewer"). Intended: Add to context, in the right-click menu of a file in the file bar and, beside Add comment, of lines selected in the source view, attaches the file by its path from the session's root, or the path, line range and selected text, to the chat that opened the Files app. As Claude's own file viewer does, it goes with the chat's next prompt rather than being sent on its own. One mechanic, so a file and a selection are two scenarios of this story.

Built (2026-11-15): Add to context on a file's or folder's right-click menu in the file bar, and beside Add comment on the source view's right-click menu for selected lines, calls `session.add_to_chat_context` (`Session.add_to_chat_context`), which queues a fill for the chat that opened the Files app: `@path ` for a whole file, the path, the range and each line quoted (`Range.context`) for a selection. A chat not connected refuses it, and the page says so in a toast.

### (S) Person --> [Send Failure To Be Fixed](../story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/send_failure_to_be_fixed_story.test.md#story-send-failure-to-be-fixed)

Requested (2026-11-20, "error in display or rendering / generation action or session roots --> fix button with most common causes listed to send to ai to fix"). Built (2026-11-20): a failure the Files app shows stays in its failure band with a Fix button; Fix lists the most common causes of that kind of failure, which Python holds (`tools/error_display/failure.py` *FailureKinds*), and sends the failure with those causes to the chat that opened the page (`FailureFixes`). The board's fidelity outputs do not raise these failures yet.

## (E) Switch Files App Between Files And Graph

[Scenarios](../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md).

### (S) Person --> [Switch Files App To Graph View](../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md#story-switch-files-app-to-graph-view)

Requested (2026-11-15, "the actual file viewer is going to have a toggle that can switch from folder files and graph"): a toggle at the top of the Files app switches its file bar between the files it lists, as a list or in folders (`file-bar.ts` *FileBar*), and the practice trees of the session's graph, as the Graph app's tree shows them. Switching back shows the files again.

Built (2026-11-15), not walked: the file bar's Graph button beside List and Folders (`files-graph-view.tsx` *FilesGraphView*), reading `session.graph_trees` for the files the bar lists; each practice tree starts collapsed and the open file stays open. Fixed (2026-11-15, "why is story graph empty"; 2026-11-16, "the graph needs to have the same file filtering that vanilla session files does"): the graph view's graph is read from exactly the files the page lists, each named from the project, its story tests in markdown and code alike, and keeps only what they hold, so the page's file filters are the one filter (`Session.graph_trees`, `Graph.load_files`). Tests: `harness/files_app/app/files/files-graph.spec.ts`, `space/session/session_graph_spec.py`.

### (S) Files App --> [Read Story Map Into Stories Tree](../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md#story-read-story-map-into-stories-tree)

Built (2026-11-15, "why is story graph empty"): the graph view's Stories tree holds the project's story map, a story listed only by its story test in code or by its scenarios in markdown, and every epic of a map listed beside a code story test; a map listed in markdown and drawio is read once, from its markdown, and a story listed only by its map holds its scenarios (`Session.graph_trees`). Split from Switch Files App To Graph View on 2026-11-24.

### (S) Files App --> [Filter Graph Like The File List](../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md#story-filter-graph-like-the-file-list)

Requested (2026-11-15, "graph filtered like file filter is"): the graph view holds only the nodes of the files the file list would show: the stages, practices and format groups of the session's guidance selection, the chat bar's selected fidelity dots while any are selected, and the Changed button's branch changes while it is on (`files-page.ts` `filesShown`, `file-bar.ts` `entries`). A filter changed in either view shows in both.

Built (2026-11-15), not walked: the graph is read again whenever the bar lists other files (`FilesGraph.follow`), so a practice turned off here or on the chat bar, and the Changed button, narrow it as they narrow the list; the session keeps only the nodes read from those files (`Session.graph_trees`, the graph filter's `paths`).

### (S) Files App --> [Filter Callouts Like The Graph](../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md#story-filter-callouts-like-the-graph)

Requested (2026-11-20, "callout filtering should be done exactly the same way knowledge graph filtering is done"). Built (2026-11-20): the session answers only the callouts the file view's filters show: the files listed for the stages, practices and formats chosen, and the graph view's node filter, decided in Python by the graph's own filter (`space/session/files/file_view_filter.py` *FileViewFilter*); the page sends its filters with `session.file` and draws what comes back.

### (S) Files App --> [Filter Step Callouts By Node Filter](../story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/switch_files_app_between_files_and_graph_story.test.md#story-filter-step-callouts-by-node-filter)

Built (2026-11-20): a connector or a node type left out of the graph view's node filter leaves out what a step reaches by it, while a step keeps what it reaches in the files listed with it (*FileViewFilter*). Split from Filter Callouts Like The Graph on 2026-11-24.

## (E) Open Graph Nodes In Files App

[Scenarios](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md). A node selected in the graph view opens the files and lines it covers in the file view, a story's scenarios and the code its steps reach included. Grouped on 2026-11-24 from Switch Files App Between Files And Graph, as it had grown to twelve stories; the steps stay in `switch-files-app-between-files-and-graph.story.shared.py`.

### (S) Person --> [Open Several Files From Graph Nodes](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-open-several-files-from-graph-nodes)

Requested (2026-11-15, "except for you're now selecting file(s), eg more than one file opens"): selecting a node in the graph view opens its file in the source view; selecting nodes in more than one file opens each of those files, where the Files app opens one file today and the Graph app shows one node's source.

Built (2026-11-15), not walked: selecting a node opens its file at its lines (`Session.graph_node_ranges`); a node no file's lines hold, such as a package that is a folder or a practice's root, opens each listed file below it, spanning the lines its nodes cover there ("module would show multiple files"); Ctrl, Cmd or Shift with the press selects it beside the others, and each other file opens below the first (`FilesPage.showNodes`).

Changed (2026-11-16): each open file collapses to its name and expands on its own, with Collapse all and Expand all above several (`OpenFiles`).

### (S) Person --> [Open Story Test Lines From Graph Nodes](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-open-story-test-lines-from-graph-nodes)

Built (2026-11-15): selecting a step opens its scenarios file at the step's line, and a scenario, a step or a story of a Python story test opens the lines of its whole function or its scenarios, never the examples module an example comes from (`Session.graph_node_ranges`). Split from Open Several Files From Graph Nodes on 2026-11-24.

### (S) Files App --> [Fold Open Files To Selected Nodes](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-fold-open-files-to-selected-nodes)

Requested (2026-11-15, "expand and collapse in file viewer based on the nodes in the graph"): each open file unfolds the blocks of the nodes selected in the graph and folds its other classes and operations, from the folds the session's graph places (`session.file` folds); selecting another node unfolds it and leaves the rest folded. Builds on the Files app's Fold Classes And Operations and the Graph app's Unfold Calls And Classes In Source.

Built (2026-11-15), not walked: an open file opens only the folds holding a selected node, its class too, and closes the rest (`SourceView` `openAround`, Monaco's Fold All then Unfold up from the node since 2026-11-16), and the page scrolls the first a third of the way down the window: the editor is as tall as its file, so the page scrolls, not the editor ("we should scroll to line of member if it's below the fold"). Changed (2026-11-16, "make that line be near the top of the screen so it's obvious we are there; select the lines of the clicked node in a file if it's not the whole file"): the first selected line scrolls near the top and the selected lines are marked.

### (S) Person --> [Open Story Scenarios Across Files](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-open-story-scenarios-across-files)

Requested (2026-11-16, "story map md story has scenario file"): selecting a story the markdown story map holds opens its scenarios, which live in another file, beside the story map's line; a markdown scenario spans its heading through its last step.

### (S) Files App --> [Show Rules Story Tests Break](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-show-rules-story-tests-break)

Built (2026-11-16): the file view shows the rules a story test breaks: a When in a story test that calls none of the code it tests is flagged, a markdown When is not asked to invoke code before a realization names it, and a story test outside the session's folder shows its rules too. Split from Open Story Scenarios Across Files on 2026-11-24.

### (S) Person --> [Open Linked Sections In Place](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-open-linked-sections-in-place)

Requested (2026-11-16, "should have callout to expand and see story scenarios; scenario has domain references in its terms, callout to markdown class model if it exists"): a markdown line that links to a heading in another file carries a callout that opens that heading's section in place, as a call opens in place in code: a story map story opens its scenarios, and a scenario's domain term opens its class in the markdown model (`SessionFile.callouts`).

### (S) Person --> [Follow Story Steps To Code](../story_tests/review-generated-work-in-file-viewer/open-graph-nodes-in-files-app/open_graph_nodes_in_files_app_story.test.md#story-follow-story-steps-to-code)

Requested (2026-11-16, "observes and invokes do not reach the Python code; tested for TypeScript but not Python"; "class callouts in tests should be placed next to steps if they are step relationships"): a Python story test's step invokes the functions it calls by name as well as the operations it calls on an object (`StoryLinks._functions_called`), and in the source view a story test's callouts sit on the step whose invokes and observes they are, never on a line that only names a class in prose.

## (E) Explore Graph In Files App

[Scenarios](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md). Requested (2026-11-15, "we basically ingest all of the stories and functionality that the Graph application can do"): each story brings one of the Graph app's into the Files app's graph view, working on the files it lists rather than on a folder chosen in the app.

### (S) Person --> [Expand Practice Tree In Files App](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md#story-expand-practice-tree-in-files-app)

Brings in the Graph app's Expand Practice Tree: each practice starts collapsed, and the person opens nodes one level at a time (`GraphView.tsx` `TreeNode`).

Built (2026-11-15), not walked ("the viewer graph needs to borrow much more from original graph tree"): the graph view draws each row as the Graph app does, a twist, then the Graph app's mark for the node's kind (`labels/kind-mark.tsx` *KindMark*) and its name.

### (S) Person --> [Follow Relationships Under Node In Files App](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md#story-follow-relationships-under-node-in-files-app)

Brings in the Graph app's Follow Relationships Under Node: a node shows its relationship groups as children, such as the invokes under an operation, and selecting a related node opens its file beside the files already open.

### (S) Person --> [Filter Graph By Node Type And Connector In Files App](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md#story-filter-graph-by-node-type-and-connector-in-files-app)

Brings in the Graph app's Filter By Node Type, Filter By Connector and Select All Or No Filter Choices, on top of the file list's filters: choosing node types keeps only those nodes and narrows the connectors and rules offered (`Graph.filter_choices`). The Graph app's Filter By Practice is the Files app's practice toggles already.

### (S) Person --> [Apply Pattern Overlays In Files App](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md#story-apply-pattern-overlays-in-files-app)

Brings in the graph's Apply Pattern Overlays: the graph view shows the overlays the session has chosen, the same choice as the chat bar's overlay chips (`ticket.choose_overlays`), with each overlay's nodes and rules in the tree.

### (S) Files App --> [Show Graph Load Steps In Files App](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md#story-show-graph-load-steps-in-files-app)

Brings in the Graph app's Show Load Steps While Loading and Copy Load Failure For Agent: while the session's graph loads, the graph view shows the step it is on and how long it has run (`graph/query-progress.ts`); a failed load shows the server's reason, with a copy for the chat, instead of loading forever.

Built (2026-11-15), not walked, the load steps only: while `session.graph_trees` runs, the page reads the cdd server's progress reports (`/cdd/progress`) into the graph state and shows them with the Graph app's own view, moved out of `GraphView` (`graph/LoadProgressView.tsx`). A failed load shows its reason but not yet the copy for the chat.

### (S) Person --> [Open Calls Across Files In Files App](../story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md#story-open-calls-across-files-in-files-app)

Requested (2026-11-15, "inner cross file code folding doesn't seem to be working; in original graph explorer folding expansion across files"): brings in the Graph app's Unfold Calls And Classes In Source across files: a call in the open file to an operation in another file opens that operation's lines in place.

Built (2026-11-15), not walked: once the graph view read the trees, the page reads every member the graph holds (`Session.graph_members`, the explorer's `source_members`) and hands them to the source view with each open file (`sourceOf`), which the Graph app's call layout opens calls from.

## (E) Review Graph Violations In Files App

[Scenarios](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md). These take in the board's and the chat bar's Read Graph Violations sub-epics (2026-11-06): a violation is read from the session's live graph wherever it shows, and fixed from where it is read.

### (S) Person --> [Show Only Violating Nodes In Files App](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-show-only-violating-nodes-in-files-app)

Brings in the Graph app's Show Only Violations and Filter Violations By Rule: the Violations switch keeps only the nodes that break a rule, and with rules chosen, only those that break a chosen one (`Filter._fails_selected_rule`).

### (S) Person --> [See Rules Under Node In Files App](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-see-rules-under-node-in-files-app)

Brings in the Graph app's See Rules Under Node and Hover Violating Rule For Message: each node lists its passing, broken and prompt rules, a node that breaks one is marked in the tree, and hovering a broken rule shows its messages.

### (S) Person --> [Open Violation In Files App Source](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-open-violation-in-files-app-source)

Brings in the Graph app's Open Violation In Source: selecting a broken rule opens its node's file with the rule and its message above the lines it names, unfolded, as the Files app's Mark Lines A Broken Rule Names marks them.

### (S) Person --> [Fix Graph Violations From Files App](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-fix-graph-violations-from-files-app)

Requested (2026-11-06, "board and chat ... fix"; "/fix is a first class action; fix rule; file; default across all rules / files"): Fix this one on a violation, Fix rule on a rule and Fix all on the view send the Fix action to the chat that opened the page, for that violation, rule, or every violation the graph view shows. Takes in the board's Fix Graph Violations From Board and the Graph app's Copy Correct Prompt, whose prompt names the node, file and lines, rule, excerpt and message (`source/violation-prompt.ts`).

Built (2026-11-23): in the graph view, a broken rule under a node offers Fix this one, for the rule on that node, and Fix rule, for every node the view shows breaking it, and the view offers Fix all; each fills the prompt of the chat that opened the page with the fix Python writes for what the view shows (`session.graph_fix_prompt`, `Graph.fix_prompt`, `ViolationCorrections`). In the file view, the broken rule's banner lists every place the rule is broken, each with Fix this one, and offers Fix rule, and the file's bar offers Fix all; each puts the fix comment on the lines of each broken place and sends them to the chat in one prompt (`file_comments.fix`). The Graph app's banner says Fix this one in place of Correct.

### (S) Person --> [Fix Graph Violations From Chat Bar](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-fix-graph-violations-from-chat-bar)

Requested (2026-11-06, "board and chat ... fix"): Fix in the action picker sends the Fix action for the selected fidelities, every violation the live graph holds for them by default.

### (S) Chat Bar --> [Count Session Violations From Live Graph](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-count-session-violations-from-live-graph)

Requested (2026-11-06, "default is to have a graph and just read the violations"; "board and chat generate"): each fidelity dot's red count comes from the session's live graph, not from the last validation report, so a generate, or a file read again in the Files app, updates the dots. Takes in Read Session Violations From Latest Graph and Generate And Judge Fidelity From Chat Bar.

### (S) Board App --> [Count Fidelity Violations From Live Graph](../story_tests/review-generated-work-in-file-viewer/review-graph-violations-in-files-app/review_graph_violations_in_files_app_story.test.md#story-count-fidelity-violations-from-live-graph)

Requested (2026-11-06, "default is to have a graph and just read the violations"; "board and chat generate"): a tile's violation count comes from the session's live graph, not from the last validation report. Also Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "better graph integration - load up front on session open, show all violations as a result of graph, no need for explicit run"). Takes in Read Fidelity Violations From Latest Graph and Generate And Judge Fidelity From Board.

## (E) Align Formats In Files App

[Scenarios](../story_tests/review-generated-work-in-file-viewer/align-formats-in-files-app/align_formats_in_files_app_story.test.md).

### (S) Person --> [Diagnose And Align Session Formats](../story_tests/review-generated-work-in-file-viewer/align-formats-in-files-app/align_formats_in_files_app_story.test.md#story-diagnose-and-align-session-formats)

Requested (2026-11-20, "we need a diagnose and align button that goes on context viewer through graph and selected stages, fidelities, formats and determines gaps and then syncs, failures can be fixed; check graphs for alignment; check callouts match"). Built (2026-11-20): Diagnose goes through the session's selected stages, practices and chosen formats and its graph and lists each gap in plain words: a chosen format with no file, formats of one document whose graph readings differ, callouts that match no edge (`format-alignment.diagnose_alignment`). Align renders the format that lacks from the one that holds more through the Render action; formats that conflict wait for the person; each failure can be sent to be fixed (`format-alignment.align_formats`).

### (S) Person --> [Render Formats Into Their Files](../story_tests/review-generated-work-in-file-viewer/align-formats-in-files-app/align_formats_in_files_app_story.test.md#story-render-formats-into-their-files)

Built (2026-11-20, the person: "all renders should result in the final output -> file"; 2026-11-21, "existing code, comments, whatever exists only in one shape must be preserved"): a render saves the chosen code format that has no file, reshapes a code file that already has code keeping its bodies, keeps a member the model no longer holds for migration, fails a render that would lose a line, and answers a render that fails as a failure. Split from Diagnose And Align Session Formats on 2026-11-24.

### (S) Person --> [Diagnose Drawings And Callouts](../story_tests/review-generated-work-in-file-viewer/align-formats-in-files-app/align_formats_in_files_app_story.test.md#story-diagnose-drawings-and-callouts)

Built (2026-11-20): the diagnosis reports a drawing that cannot be read, a callout whose target is missing, and callouts and edges that do not match. Split from Diagnose And Align Session Formats on 2026-11-24.

# (E) Author Story Maps

This epic is the app's own story map, `C:/dev/story-ui/.context/story-map.md`; its evidence lines name the app's files. Condensed on 2026-11-16 at the person's request on the story map whiteboard: stories that were one interaction each became one story with acceptance criteria, which stay here in the source until they become scenarios.

## (E) View Story Map
### (S) Story Designer --> Browse Story Hierarchy

**Acceptance criteria:**
- Observed: Epic, SubEpic and Story lanes render on one shared grid, each Story under its parent SubEpic column, lanes sized to their bottommost children and collapsed titles on one line (stories-client.tsx `StoryHierarchyView`, `computeColumnLayout`; workspace.css).
- Intended: nested SubEpics render as two stacked SubEpic lanes under their parent SubEpic; the model in stories.ts holds only one SubEpic level (mern-story-map-ai-sketch.md, Browse Story Hierarchy).
- Intended: selecting a Story shows its story_type and users, and a SubEpic its test_file and domain_concepts; the cards show only names and controls (mern-story-map-ai-sketch.md, "when the Story Designer selects a node").

### (S) Story Designer --> Adjust Workspace View

**Acceptance criteria:**
- Observed: holding the right mouse button and dragging pans the canvas on both axes, without the browser menu, with a grabbing cursor, stopping on release even outside the canvas (stories-client.tsx `StoryMapWorkspaceView` `handleCanvasMouseDown`).
- Observed: Map View and Increment View switch between the plain map and the map with increment lanes and an Unassigned drop zone (`useStoryMapViewState.toggleViewMode`, `StoryHierarchyView` `showIncrements`).
- Intended: Show Scenarios and Show Examples show and hide them; today the buttons toggle but the card and scenario panel ignore them (story_map.information_architecture.md toolbar; story_map.modules.md session toggles).
- Observed: the Executive / Engineering switch changes the theme and logo and remembers the choice in browser storage (`THEME_STORAGE_KEY`; workspace.css `data-theme`).

## (E) Build, Expand, Rearrange And Plan Story Map
### (S) Story Designer --> Expand And Collapse Story Cards

**Acceptance criteria:**
- Observed: clicking a Story card or its expand button opens it inline with its Scenarios, Steps and Example tables while neighbours stay collapsed, and clicking again collapses it (stories-client.tsx `StoryCard`, `handleExpand`).
- Observed: the expand button on an Epic or SubEpic opens every Story card beneath it (`getAllDescendantStoryIds`, `useStoryMapViewState.expandDescendants`).
- Observed: the toolbar's Expand All and Collapse All open or close the whole map (`StoryMapWorkspaceView` toolbar, `collapseAll`).
- Observed: an expanded card's column, the lanes above it and everything to its right widen to fit it, and narrow again on collapse (workspace.css `.story-card.expanded`; shared grid in `StoryHierarchyView`).

### (S) Story Designer --> Add, Remove And Rename Map Nodes

**Acceptance criteria:**
- Observed: a map with no Epics shows one "+ Epic" starter button that opens the title popover (`StoryHierarchyView` Epic lane, `AddNodePopoverButton`).
- Observed: the + on a card, or the leading + on a group's first card, adds an Epic, SubEpic or Story with the typed or a default title after that sibling or at the start; Cancel or Escape adds nothing (`AddNodePopoverButton`, `insertEpicAfter`, `insertSubEpicAfter`, `insertStoryAfter`; stories-server.ts POST routes).
- Observed: the − on a card deletes that node and everything under it and renumbers its siblings (stories.ts `removeEpic`, `removeSubEpic`, `removeStory`).
- Observed: double-clicking a card edits its name inline; Enter, Tab or leaving saves and Escape restores (`NodeNameInput`; stories-server.ts PATCH `/nodes/:nodeId`).

### (S) Story Designer --> Rearrange Map Nodes By Dragging

**Acceptance criteria:**
- Observed: dragging a card within its lane or parent saves the new sibling order (`makeEpicDragHandlers`; stories.ts `reorderEpics`, `reorderSubEpics`, `reorderStories`).
- Observed: dropping a Story on another SubEpic, or a SubEpic on another Epic, moves it there with everything under it (`StoryMapModel.moveStory`, `moveSubEpic`).
- Observed: an empty Epic or SubEpic accepts a dropped node (`makeEmptyParentDropZone`).
- Observed: the dragged card shows full-size at the spot it would land, with no browser drag image (`useDragVisuals`, `computeDisplayIds`, `suppressNativeDragImage`).

### (S) Story Designer --> Add, Rename, Reorder And Remove Increments

**Acceptance criteria:**
- Observed: in Increment View "+ Increment" appends a new increment lane at the bottom (stories.ts `appendIncrement`).
- Observed: the increment label is an inline name field saved on Enter, Tab or leaving it, Escape restoring the old name (`IncrementLabel`).
- Observed: dragging an increment label up or down saves the new increment order (stories.ts `reorderIncrements`).
- Observed: the − on an increment label deletes it and its Stories return to the unassigned spine (stories.ts `removeIncrement`; DELETE `/increments/:incrementId`).

### (S) Story Designer --> Assign Stories To Increments

**Acceptance criteria:**
- Observed: dropping a Story card on an increment lane moves it into that increment, out of any other, while it stays under its SubEpic column (stories.ts `assignStoryToIncrement`).
- Observed: dropping a Story card on the Unassigned zone, shown only in Increment View, removes it from its increment (stories.ts `unassignStoryFromIncrement`).

### (S) Story Designer --> [Change Story Map With AI](../story_tests/author-story-maps/build-expand-rearrange-and-plan-story-map/change_story_map_with_ai_story.test.md)

**Acceptance criteria:**
- Intended: the designer asks for a change in an AI chat panel; no chat panel or ai-mutation module exists (story_map.stories.md, Request AI Story Mutation; story_map.information_architecture.md, AI Chat Panel).
- Intended: the agent applies the change to the story map directly (story_map.stories.md, Apply AI Mutation to Story Map; mern-story-map-ai-sketch.md "Direct auto-apply changes").
- Moved on 2026-11-24 from the sub-epic Author Story Changes With AI, which held only this story, into this sub-epic, whose outcome it serves.

## (E) Author Scenarios And Steps
### (S) Story Designer --> Add Scenario To Story

**Acceptance criteria:**
- Observed: the + beside Scenarios in an expanded card adds "New Scenario" at the end (`handleAppendScenario`; stories.ts `StoryMap.appendScenario`).

### (S) Story Designer --> Rename Scenario Inline

**Acceptance criteria:**
- Observed: the Scenario name is an inline field saved on Enter, Tab or leaving it, Escape restoring the old name (`ScenarioPanel` `saveScenarioName`).

### (S) Story Designer --> Remove Scenario From Story

**Acceptance criteria:**
- Observed: the − on a Scenario deletes it and renumbers the rest (stories.ts `StoryMap.removeScenario`).

### (S) Story Designer --> Reorder Scenarios By Dragging

**Acceptance criteria:**
- Observed: dragging a Scenario by its handle saves the new order (`StoryCard` `makeDragHandlers`; stories.ts `reorderScenarios`).

### (S) Story Designer --> Add Step To Scenario

**Acceptance criteria:**
- Observed: the + beside Steps adds "Given New step" at the end of the Scenario (`handleAddStep`; stories.ts `ScenarioModel.addStep`).

### (S) Story Designer --> Edit Step Keyword And Text

**Acceptance criteria:**
- Observed: each Step has a Given/When/Then/And/But selector and a text field, saved on Enter or Tab and restored on Escape (`StepEditor`; stories.ts `updateStep`).

### (S) Story Designer --> Remove Step From Scenario

**Acceptance criteria:**
- Observed: the − on a Step deletes it and renumbers the rest (stories.ts `ScenarioModel.removeStep`).

### (S) Story Designer --> Reorder Steps By Dragging

**Acceptance criteria:**
- Observed: dragging a Step by its handle saves the new order (stories.ts `reorderSteps`).

## (E) Author Examples
### (S) Story Designer --> Add And Remove Examples On Scenario

**Acceptance criteria:**
- Observed: the + beside Examples adds an empty "New Example" table (`handleAddExample`; stories.ts `ScenarioModel.addExample`).
- Observed: the − on an Example deletes that table and renumbers the rest (stories.ts `ScenarioModel.removeExample`).

### (S) Story Designer --> Add And Remove Example Fields

**Acceptance criteria:**
- Observed: typing a field name in the header and pressing + adds a column, and a name already in the table is refused (`ExampleBlock`; stories.ts `addExampleField`, `DUPLICATE_FIELD_NAME`).
- Observed: the − on a column header removes that field (stories.ts `ScenarioModel.removeExampleField`).

### (S) Story Designer --> Add, Edit, Remove And Reorder Example Lines

**Acceptance criteria:**
- Observed: the add button under the table adds an empty line at the bottom (`handleAddExampleRow`; stories.ts `addExampleRow`).
- Observed: each cell is an inline field saved on Enter or leaving it (`ExampleCellEditor`; stories.ts `updateExampleRow`).
- Observed: the − on a line deletes it and renumbers the rest (stories.ts `ScenarioModel.removeExampleRow`).
- Observed: dragging a line by its handle saves the new order (stories.ts `reorderExampleRows`).

## (E) Save And Share Changes
### (S) Story UI --> Save Valid Edits And Keep Their History

**Acceptance criteria:**
- Observed: every edit is sent to the server as one request, saved to MongoDB, and the map reloaded from the saved copy (`useStoryMap`; stories-server.ts `StoryMapRepositoryServer`, `StoryMapServer.persist`).
- Observed: an edit that breaks a map rule (a Scenario under a non-Story, an increment on a non-Story, an unknown increment, a node outside its claimed parent, a duplicate field name) is refused with 422 and the rule code (stories.ts `MutationGuardError`).
- Observed: the status rail shows synced, pending changes, or save error (`StoryMapWorkspaceView`, `storyModelReducer`).
- Intended: each save records one save event; today stories-server.ts only comments that the collaboration layer emits it (mern-story-map-ai-sketch.md; story_map.modules.md audit).
- Intended: the designer browses the saved versions on a history timeline; no history screen exists (story_map.information_architecture.md, Version History Timeline).

### (S) Story Designer --> [Recover Workspace View State](../story_tests/author-story-maps/save-and-share-changes/save_and_share_changes_story.test.md#story-recover-workspace-view-state)

**Acceptance criteria:**
- Intended: reloading keeps the view mode, expanded nodes and toggles; session.ts and session-server.ts can store them, but app.ts never mounts `createSessionRouter` and the workspace never calls `useStoryMapSession` (story_map.stories.md, Recover Persisted Story Map State).

### (S) Story Designer --> Share Real-Time Story Map Session

**Acceptance criteria:**
- Intended: designers on the same map see each other's changes as they happen; no collaboration module or broadcast exists (story_map.stories.md, Synchronize Story Map State).
- Intended: concurrent view-state changes are reconciled; no collaboration module exists (story_map.stories.md, Resolve Concurrent View State Changes).

### (S) Agent --> [Test Story UI Editor On Session Story Map](../story_tests/author-story-maps/save-and-share-changes/save_and_share_changes_story.test.md#story-test-story-ui-editor-on-session-story-map)

**Acceptance criteria:**
- Requested on 2026-11-06: the Story UI editor opens a CDD session's `story-map.md`, edits it and saves it back, and its tests run against that map; each gap a test finds becomes an Intended story here, fixed before the board or chat bar invokes the app.

# (E) Explore Stories In Story UI

The story explorer is a new part of the Story UI app: the Story UI editor's screen frames view opens it, and its core frame is the selected step's design canvas screen. It replaces the story map artboard and the explorer (`explorer.dc.html`) the design canvas draws today, so every story here is new.

## (E) Show Screen Frames In Story UI

### (S) Person --> [Switch Story Map To Screen Frames View](../story_tests/explore-stories-in-story-ui/show-screen-frames-in-story-ui/show_screen_frames_in_story_ui_story.test.md#story-switch-story-map-to-screen-frames-view)

Requested (2026-11-06): the Story UI editor has a screen frames view beside its base view; in it, each story's card has its screen as a frame beneath it. The base view stays the plain story map.

### (S) Story UI --> [Show Screen Frame Under Each Story](../story_tests/explore-stories-in-story-ui/show-screen-frames-in-story-ui/show_screen_frames_in_story_ui_story.test.md#story-show-screen-frame-under-each-story)

Requested (2026-11-06): each frame is the story's main design canvas screen, drawn small under its card. It replaces the design canvas, where today the story map artboard draws a thumbnail under each story (`thumbnail` in `canvas.py`, `claude_design_story_map_spec.py`).

### (S) Story UI --> [Mark Story Without A Screen](../story_tests/explore-stories-in-story-ui/show-screen-frames-in-story-ui/show_screen_frames_in_story_ui_story.test.md#story-mark-story-without-a-screen)

Requested (2026-11-06): a story with no screen gets an empty frame saying so. It replaces the design canvas, where today the artboard shows "No screenshot" in place of the picture (`thumbnail` in `canvas.py`).

### (S) Person --> [Open Story Explorer From Screen Frame](../story_tests/explore-stories-in-story-ui/show-screen-frames-in-story-ui/show_screen_frames_in_story_ui_story.test.md#story-open-story-explorer-from-screen-frame)

Requested (2026-11-06): pressing a frame opens the browser story explorer at that story, scenario and step. It replaces the design canvas, where today only the artboard's thumbnails link, each opening `explorer.dc.html` at its story (`claude_design_story_map_spec.py`).

## (E) Navigate The Story Tree

### (S) Person --> [Open The Explorer At A Story, Scenario And Step](../story_tests/explore-stories-in-story-ui/navigate-the-story-tree/navigate_the_story_tree_story.test.md#story-open-the-explorer-at-a-story-scenario-and-step)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `explorer.dc.html` reads the story, scenario and step from the link, or from the place the map kept, and selects it in the tree.

### (S) Person --> [Collapse And Reset The Story Tree](../story_tests/explore-stories-in-story-ui/navigate-the-story-tree/navigate_the_story_tree_story.test.md#story-collapse-and-reset-the-story-tree)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer's *Collapse all* and *Reset* buttons close the epic → sub-epic → story → scenario → step tree or return it to the first story (`explorer.dc.html`).

### (S) Story UI --> [Keep The Selected Story In View](../story_tests/explore-stories-in-story-ui/navigate-the-story-tree/navigate_the_story_tree_story.test.md#story-keep-the-selected-story-in-view)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer scrolls the selected entry into view when the selection changes (`explorer.dc.html`).

### (S) Person --> [Copy A Request To Open A Story In Its File](../story_tests/explore-stories-in-story-ui/navigate-the-story-tree/navigate_the_story_tree_story.test.md#story-copy-a-request-to-open-a-story-in-its-file)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, the explorer carries each story's and scenario's `path:line` and offers to copy an open-in-file-viewer request for it (`claude_design_story_map_spec.py`, `copyOpenRequest` in `explorer.dc.html`).

### (S) Person --> [Pick An Outline Scenario's Example](../story_tests/explore-stories-in-story-ui/navigate-the-story-tree/navigate_the_story_tree_story.test.md#story-pick-an-outline-scenarios-example)

Built in the design canvas explorer (checked 2026-11-10): `explorer.dc.html` lists an outline scenario's examples from the fixtures bundle and picking one calls `go(..., ex.name)` (`outlineRows`). Intended: the Story UI explorer does the same. Was: Intended (`claude_design.md` outline-rows): an outline scenario lists its examples from the fixtures bundle and picking one loads it on the screen; the explorer does not list them yet.

## (E) Play Stories In The Explorer

### (S) Person --> [Play The Next Story](../story_tests/explore-stories-in-story-ui/play-stories-in-the-explorer/play_stories_in_the_explorer_story.test.md#story-play-the-next-story)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer's *Play next* button moves the selection to the next step or story (`explorer.dc.html`).

### (S) Person --> [Hide And Show The Story Panel](../story_tests/explore-stories-in-story-ui/play-stories-in-the-explorer/play_stories_in_the_explorer_story.test.md#story-hide-and-show-the-story-panel)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the » and « buttons hide the story panel so the screen fills the frame, and bring it back (`explorer.dc.html`).

### (S) Person --> [Return To Story UI Map](../story_tests/explore-stories-in-story-ui/play-stories-in-the-explorer/play_stories_in_the_explorer_story.test.md#story-return-to-story-ui-map)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the panel's **← Story map** link opens `Main.dc.html` again (`explorer.dc.html`).

### (S) Agent --> [Test Story Explorer On Session Story Map](../story_tests/explore-stories-in-story-ui/play-stories-in-the-explorer/play_stories_in_the_explorer_story.test.md#story-test-story-explorer-on-session-story-map)

Requested on 2026-11-06: the browser story explorer plays a CDD session's story map on its design canvas screens, and its specs run against that map. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

## (E) Frame Design Canvas Screens In Explorer
### (S) Story UI --> [Show Design Canvas Screen As Explorer Frame](../story_tests/explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer/frame_design_canvas_screens_in_explorer_story.test.md#story-show-design-canvas-screen-as-explorer-frame)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, `_imports` in `nodes.py` imports each prototype screen into the explorer with the story, scenario and a `go` call, so the selected scenario runs on the real screen (`claude_design_story_map_spec.py`).

### (S) Story UI --> [Choose The Screen For A Step](../story_tests/explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer/frame_design_canvas_screens_in_explorer_story.test.md#story-choose-the-screen-for-a-step)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, a step shows the screen it is shown on, else its scenario's screen, else its story's screen (`_story_entry` and `_screen_of` in `nodes.py`, `claude_design_story_map_spec.py`).

### (S) Story UI --> [Join A Step Without A Screen To The Next Step](../story_tests/explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer/frame_design_canvas_screens_in_explorer_story.test.md#story-join-a-step-without-a-screen-to-the-next-step)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `_story_entry` in `nodes.py` groups a step with no screen of its own with the next step that has one, so every entry the person picks shows a screen.

### (S) Story UI --> [Show A Screenshot When No Screen Runs](../story_tests/explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer/frame_design_canvas_screens_in_explorer_story.test.md#story-show-a-screenshot-when-no-screen-runs)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, when no prototype applies, the explorer shows the step's screenshot, skipping blank captures (`_blank` in `nodes.py`).

### (S) Story UI --> [Keep Each Screen's Own Stylesheets](../story_tests/explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer/frame_design_canvas_screens_in_explorer_story.test.md#story-keep-each-screens-own-stylesheets)

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `_stylesheets` in `nodes.py` links every stylesheet the prototype screens use, so a screen drawn inside the explorer keeps its own look.

# (E) Build Design Canvas Screens

This epic holds the design canvas app's stories; its own map, harness/design_canvas/.context/story-map.md, was folded in here on 2026-11-16. Its evidence lines name the app's files.
## (E) Lay Out The Canvas Files
### (S) Design Canvas --> Place Pages On The Canvas

Observed: `DesignCanvas.add_page` lists each page in `canvas.json` in the order added, and the canvas launches on the first page (`design_canvas_spec.py`).

### (S) Design Canvas --> Place Artboards On Their Pages

Observed: `DesignCanvas.add` and `place` put each artboard on its page and keeps the order they were added in `canvas.json` (`design_canvas_spec.py`).

### (S) Design Canvas --> Write The Canvas Into A Project Folder

Observed: `DesignCanvas.write` puts `canvas.json` and every artboard it was given text for under `project/` in the chosen folder, so the folder can be published as it is (`design_canvas_spec.py`).

### (S) Design Canvas --> Name An Imported Screen After Its File

Observed: `stem` and `camel` in `canvas.py` give a screen file's import name and its live flag in camel case, so the explorer can import the screen by name (`design_canvas_spec.py`).

### (S) Design Canvas --> Give Each Prototype Screen Its Own Page

Observed: `ClaudeDesignStoryMap.canvas` puts the story map, the story explorer, and each prototype screen on its own page (`claude_design_story_map_spec.py`).

### (S) Design Canvas --> Place A Read-Only Story Panel Beside A Screen

Observed: `_context_panel` in `nodes.py` draws a Stories board to the right of a screen, with the screen's own stories opened to their scenarios and steps and every other story greyed out (`claude_design_story_map_spec.py`).

## (E) Load Scenario Fixtures With The Fixture Bar
### (S) Person --> Load A Scenario Into A Standalone Screen

Inferred: opened on its own, a screen's fixture bar starts on *Load a scenario…* and loads nothing until the person picks a scenario, which loads its fixture and types the values it enters (`fixture_screen.py` `loadFromFixture`).

### (S) Design Canvas --> Load The Explorer's Scenario Into The Screen

Inferred: inside the explorer the screen loads the explorer's scenario as soon as the fixtures bundle is there, and again whenever the explorer moves (`fixture_screen.py` `followExplorer`).

### (S) Person --> Pick Another Scenario From Inside The Explorer

Inferred: picking a scenario on the bar inside the explorer loads it and moves the explorer's tree to it (`fixture_screen.py` `pickScenario`).

### (S) Person --> Paste Dev Seed Data Into A Screen

Inferred: the bar lists dev mode's seed paste for the screen's path, and picking it types each pasted field into the screen (`fixture_screen.py` `pasteSeedData`).

### (S) Person --> Follow A Screen Link To The Next Story

Inferred: a link to the next screen moves the explorer to that story, or opens the next screen when the screen stands alone (`fixture_screen.py` `follow`).

### (S) Person --> Edit A Screen On Its Own Artboard

Inferred: inside the explorer the bar ends with **Edit**, a link to the screen's own artboard, because an edit inside the explorer would change the explorer (`fixture_screen.py` `bar`).

### (S) Design Canvas --> Report Where The Screen's Data Came From

Inferred: the bar's values carry the loaded story and scenario, the pasted seed, or the loading problem (`fixture_screen.py` `barVals`).

## (E) Browse The Story Map Artboard

From the design canvas's own map (harness/design_canvas/.context/story-map.md, folded in 2026-11-16): the artboard stories Explore Stories In Story UI does not hold. Its thumbnail stories are Show Screen Frames In Story UI there.

### (S) Design Canvas --> Draw The Whole Story Map On One Artboard

Observed: `_story_map` in `nodes.py` draws every epic, sub-epic, actor and story card on the single `Main.dc.html` artboard, one column per story (`claude_design_story_map_spec.py`).

### (S) Design Canvas --> Draw Each Epic Bar Across Its Sub-Epics

Observed: the story map draws each epic bar once, spanning all of its sub-epics (`claude_design_story_map_spec.py`).

### (S) Design Canvas --> Draw The Map In The abd Engineering Look

Observed: `LOOK` in `look.py` gives epics, sub-epics, actors and stories their dark cards and orange accent, and `box` in `canvas.py` draws them; the map has no white background (`claude_design_story_map_spec.py`).

### (S) Person --> Zoom The Story Map

Inferred: a zoomable `artboard` in `canvas.py` lets the person zoom the map with a trackpad pinch or ctrl + wheel and its − / % / + buttons, without shrinking the frame.

### (S) Design Canvas --> Keep A Clicked Link's Place For The Linked Artboard

Inferred: the zoomable artboard in `canvas.py` stores a clicked link's `#` part in local storage under `design-canvas.link:`, because the canvas opens a linked artboard without it, and the explorer reads it back (`explorer.dc.html`).

## (E) Start A Canvas Version
### (S) Agent --> Start The First Version

Observed: `CanvasVersions.start_next` begins at `version-1` when there are no versions yet (`versions_spec.py`).

### (S) Agent --> Start The Next Version As A Copy

Observed: `start_next` copies the latest version into the next one and leaves the version people edited as it was (`versions_spec.py`).

### (S) Agent --> Write Into The Version Not Yet Published

Observed: `working` keeps returning the latest version while it has no published link, and starts the next one once it does (`versions_spec.py`).

### (S) Agent --> Refuse To Add To A Published Version

Observed: `unpublished` raises `PublishedVersion` when the latest version is already published, so a screen generator never writes over people's edits (`versions_spec.py`).

## (E) Publish And Release A Canvas Version
### (S) Agent --> Title A Published Canvas By Its Version

Observed: `CanvasVersions.title` names the canvas `<name> — version-N` (`versions_spec.py`).

### (S) Agent --> Record Each Version's Published Link

Observed: `CanvasVersion.publish_at` keeps each version's canvas link in `versions.json`, in the order published (`versions_spec.py`).

### (S) Agent --> Keep A Published Version As A Release

Observed: `release` renames the version's folder and its link to the release's name (`versions_spec.py`).

### (S) Agent --> [Remove Older Versions When Keeping A Release](../story_tests/build-design-canvas-screens/publish-and-release-a-canvas-version/publish_and_release_a_canvas_version_story.test.md#story-remove-older-versions-when-keeping-a-release)

Intended (`claude_design.md` release-a-version): when a version is kept as a release the older versions are removed; `release` in `versions.py` only renames.

### (S) Agent --> Start Numbering Again From A Release

Observed: once no numbered version is left, `start_next` starts `version-1` as a copy of the latest release (`versions_spec.py`).

### (S) Agent --> Find A Release's Canvas Folder

Observed: `CanvasVersions.in_practice_root` opens `<ux root>/design-canvas`, in the root session.json names for the UX practice, beside its other outputs (`versions_spec.py`).

## (E) Reuse Production Assets On The Canvas

Intended ([sync-design-canvas-with-production.md](../.sessions/_backlog/sync-design-canvas-with-production/sync-design-canvas-with-production.md)): the product repo builds one package of its real CSS, images, fonts and React views, published as a pinned Design System artifact; each screen becomes a thin shell that mounts the real view, and a manifest proves every packaged file by hash. A published canvas only sees its own `project/` files, so links and symlinks cannot do this. The four feature groups below are the asset reuse plan's phases 1 to 4 and come before every other new design canvas story.

### (E) Trace Canvas Files To Production

#### (S:system) Design Canvas --> Record Packaged Files In Sources Manifest

Intended (asset reuse plan, Phase 1): `sources.json` beside `CanvasVersions` records each packaged file's repo path, sha256 and git commit.

#### (S:system) Design Canvas --> Fail Check When A Packaged File Drifts

Intended (asset reuse plan, Phase 1): the drift check fails when a file no longer matches its manifest entry, for example an edited CSS file.

#### (S:system) Design Canvas --> Report Version Traceability Percentage

Intended (asset reuse plan, Phase 1): each version reports the share of its files proven identical to source by hash; pml-web proves 342,654 bytes (2.2%) today.

#### (S:system) Design Canvas --> Store Each Screenshot Once By Content Hash

Intended (asset reuse plan, Phase 1): shots are named by content hash, so the 68 duplicate shots in pml-web become none.

#### (S:system) Design Canvas --> Find Screen Files Through The Manifest

Intended (asset reuse plan, Phase 1 and "Thin screens"): `_fixture_scripts`, `_blank` and `_stylesheets` in `nodes.py` read the manifest instead of the version folder, so a manifest entry is not dropped and a blank capture is not shown.

### (E) Install Production Design System On The Canvas

#### (S) Agent --> Package Product Styles And Assets In Their Production Layout

Intended (asset reuse plan, Phase 2): `ds/<product>/` mirrors the product package layout (`packages/my-paradise`), so the CSS is byte-identical with no URL rewrites and `copy_styles` goes.

#### (S) Agent --> Publish Product Package As Design System Artifact

Intended (asset reuse plan, Phase 2): one Design System artifact per product, published once.

#### (S:system) Design Canvas --> Record Installed Design Systems In Canvas File

Intended (asset reuse plan, Phase 2 and option G): `canvas.json` lists its `designSystems` with their versions instead of the hard-coded empty list (`canvas.py:67`), and each version takes the package by server-side copy into `project/ds/<product>/`.

#### (S) Agent --> Derive Publish List From Sources Manifest

Intended (asset reuse plan, Phase 2): the publish list comes from the manifest in place of the `pub_*.json` files.

#### (S) Agent --> Pull Hosted Edits Back Before Next Version

Intended (asset reuse plan, Phase 2): before `start_next` copies the local folder (`versions.py:63`), the edits people made on the published canvas come back, so they are not missing from the next version.

### (E) Mount Production Views As Screens

#### (S) Agent --> Bundle Product Views For The Canvas

Intended (asset reuse plan, Phase 3 and option I2): a `canvas-components` bundle exports the wanted views by name and a `CanvasRoot` for scenario, remount and `go`; it builds with classic `React.createElement` against `window.React` (React 18.3.1), and esbuild `define` stands in for `fetch` and `window.location` with no production code change.

#### (S:system) Design Canvas --> Mount Production View In A Thin Screen

Intended (asset reuse plan, Phase 3): a generic `thin_screen()` driven by `ux.json` writes a shell of about 30 lines that mounts the view with `<x-import component-from-global-scope="Ns.Export">`, in place of the hard-coded `prototype()` map.

#### (S:system) Design Canvas --> Answer Screen Requests From Fixture Routes

Intended (asset reuse plan, Phase 0 gate 3): the screen's requests reach the product's real routes over in-memory repositories holding the scenario's fixture, or a thin fetch table over those repositories when the routes cannot run in the browser. Built today (checked 2026-11-10): in-memory repositories are loaded with the scenario's Givens (`lern_domain_driven/.../claude_design/fixtures.py`, `canvas-fixtures.ts`). Missing: routing the screen's requests to product routes, or a fetch table.

#### (S:system) Design Canvas --> Keep Explorer Navigation Inside The Artboard

Intended (asset reuse plan, Phase 0 gate 4): a mounted view's navigation moves the explorer through `go` and the artboard stays put.

#### (S:system) Design Canvas --> Keep Product Styles Inside The Screen

Intended (asset reuse plan, Phase 0 gate 5): the product's CSS stays inside the screen, so the explorer's own panel is unaffected.

#### (S) Person --> Type Scenario Values Into A Mounted Screen

Intended (asset reuse plan, `one-scenario-list` under "Thin screens"; [integrate-stories-with-the-canvas-explorer.md](../.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md) slice C): a mounted view owns its state, so a DOM driver types the scenario's entered values; the same driver plays UI steps in Play A Story's UI Steps On A Screen.

#### (S) Agent --> Generate Attached Screens Without Markup

Intended (asset reuse plan, Phase 5): an agent following the rewritten guidance writes no screen markup for a screen that exists in production.

### (E) Redesign A Screen By Detaching It

#### (S) Person --> Detach A Screen To Editable Markup

Intended (asset reuse plan, Phase 4 and option I3): the production view is rendered once to markup with `renderToStaticMarkup`, so people can edit its text on the canvas.

#### (S:system) Design Canvas --> Keep Leaf Components Mounted In A Detached Screen

Intended (asset reuse plan, "The trade-off to accept"): leaf components that take props, such as `PlanCardView` and `ParadiseShell`, stay mounted inside a detached layout.

#### (S:system) Design Canvas --> Mark Detached Screen As Diverged

Intended (asset reuse plan, Phase 4): the manifest, the map and the explorer mark a detached screen as diverged from production.

#### (S) Person --> Reattach A Screen Once Its Change Reaches Production

Intended (asset reuse plan, Phase 4): once the change lands in the TSX the screen mounts the production view again and the diverged mark clears.

## (E) Check Screens Against Their Scenarios

Intended ([integrate-stories-with-the-canvas-explorer.md](../.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md)): a person presses Test and sees, for each scenario, whether the screen behaves as its specs say. Built after Phase 0 of the asset reuse plan.

### (S) Agent --> Package End-To-End Results With The Canvas

Intended (integrate-stories-with-the-canvas-explorer.md slice A): at package time the end-to-end JSON under `.sessions/<release>/e2e-test-results` becomes a `results.json` tied to the bundle hash.

### (S:system) Design Canvas --> Mark Each Explorer Scenario Passed Or Failed

Intended (integrate-stories-with-the-canvas-explorer.md slice A): each explorer scenario shows passed, failed or no result.

### (S:system) Design Canvas --> Label Stale Test Results

Intended (integrate-stories-with-the-canvas-explorer.md slice A and "Done means"): a result whose bundle hash differs from the canvas's bundle is labelled stale.

### (S) Person --> Test A Scenario's Thens On The Canvas

Intended (integrate-stories-with-the-canvas-explorer.md slice B): a Test button per scenario and per story runs the `beforeEach` and `it` bodies through a second story host with a real `expect` in a test build, and shows passed or failed for each step with the failing assertion's message.

### (S) Person --> Play A Story's UI Steps On A Screen

Intended (integrate-stories-with-the-canvas-explorer.md slice C): the story's Playwright steps run against the screen through a small `page` facade over the DOM, so a detached screen is tested against the same story as production.

### (S) Agent --> Check Screen Logic Against Scenarios From A Command

Intended (integrate-stories-with-the-canvas-explorer.md slice D, only if slice C proves too limited): `check_screen.cjs` becomes a generic command in `harness/design_canvas/` that runs a screen's logic on each scenario.

## (E) Draw Linked Models On The Canvas

Intended ([draw-linked-models-on-the-canvas.md](../.sessions/_backlog/draw-linked-models-on-the-canvas.md)): the bounded context map, the domain model and the module class models sit beside the story map as artboards that mirror their drawio layout and link to one another, so from any story a person reaches its screen, its classes and its bounded context and back.

### (S:system) Design Canvas --> Draw Arrows From Drawio Waypoints

Intended (draw-linked-models-on-the-canvas.md slice 1): `arrow()` in `canvas.py` splits drawio waypoints into straight segments, one small `<svg>` each, using the `diagrams.md` formulas.

### (S) Agent --> Draw Bounded Context Map As An Artboard

Intended (draw-linked-models-on-the-canvas.md slice 2): a `claude_design` format for the ddd practice draws the bounded context map with each box a separate element.

### (S) Agent --> Draw Domain Model As An Artboard

Intended (draw-linked-models-on-the-canvas.md slice 3): the domain model gets its own artboard on a Models page.

### (S) Agent --> Draw Module Class Models As Artboards

Intended (draw-linked-models-on-the-canvas.md slice 3): a `claude_design` format for clean engineering draws one artboard per module class model, sharing the layout code with the ddd format.

### (S) Person --> Follow Links From A Context To Its Models

Intended (draw-linked-models-on-the-canvas.md slice 4): context → domain model → module class model through `<a href>` kept by `LINK_KEY`; arriving selects the target node.

### (S) Person --> See The Classes A Scenario Touches

Intended (draw-linked-models-on-the-canvas.md slice 5): from a scenario in the explorer, the classes it reaches through `specifiedBy` and `invokes`, exported from the graph without the whole 19.7 MB.

### (S) Person --> See The Stories That Exercise A Class

Intended (draw-linked-models-on-the-canvas.md slice 5): from a class, the stories whose scenarios reach it.

### (S:system) Design Canvas --> Mark Model Nodes That Fail Rules

Intended (draw-linked-models-on-the-canvas.md slice 6, optional): nodes the graph's `violations: true` filter returns carry a rule mark.

# (E) Map Work Into Knowledge Graph

This epic holds the Graph app's stories; its own map, harness/graph/.context/story-map.md, was folded in here on 2026-11-16. Its evidence lines name the app's files.
## (E) Load And Save Graph
### (S) Agent --> Load Working Copy Into Graph

Observed: `graph.load_working_copy` opens each practice on its source root in a repo folder and builds the explorer tree for every practice asked for (`graph.py` `Graph.load_working_copy`, `graph_spec.py` "loaded from the account credentials working copy").

### (S) Knowledge Graph --> Reuse Saved Graph

Observed: a load reads `.context/graph.json` instead of scanning when the saved graph already holds the requested practices on the same roots and nothing is newer than it, and it can load a subset of the saved practices (`graph_json_spec.py` "should load the saved json", "should load a subset of the saved practices").

### (S) Knowledge Graph --> Rebuild Graph After Source Or Rule Changes

Observed: a source file or a rule file (`rules.py`, `schema.yaml`, `rules.yaml`) newer than the saved graph makes the load scan the folder again (`graph.py` `_saved_graph_is_current`, `graph_json_spec.py` "should reload the folder", "should reload").

### (S) Person --> Force Graph Reload

Observed: the Force reload button at the top right of the Graph app rebuilds the graph from source even when the saved graph is current (`App.tsx`, `app.test.tsx` "should force a reload from the top right of the page", `graph_json_spec.py` "that is forced to reload").

### (S) Agent --> Load Only Edited Files

Observed: `graph.load_files` builds each practice from only the named files or folders as they are now, runs the rules on them, keeps edges to classes declared in other files, and leaves the saved graph alone (`graph.py` `Graph.load_files`, `working_copy_scan_spec.py` "limited to the edited files", `graph_spec.py` "loaded from only the edited files").

### (S) Knowledge Graph --> Skip Build And Cache Folders

Observed: a scan leaves out `node_modules`, `dist`, test-run output, caches, dot-folders, and the `_examples` and `fixtures` folders, but still reads `.examples` folders (`skipped_folders.py`, `working_copy_scan_spec.py` "over build and test-run output").

### (S) Knowledge Graph --> Report Load Progress

Observed: a load names the saved-graph check, each source file it reads, and each rule as it runs, so whoever called it can watch (`graph.py` `report_progress`, `rules.py` `attach_rules`, `load_progress_spec.py`).

### (S) Agent --> Save Graph To Context Folder

Observed: `graph.save_json` writes the serialized graph to the loaded folder's `.context/graph.json`, and every rebuild saves itself there (`graph.py` `Graph.save_json`, `graph_json_spec.py` "should save serialized json in the folder context").

### (S) Knowledge Graph --> Keep Other Practices When Saving

Observed: saving merges into the existing `graph.json`, so practices already saved that this load did not include stay in the file (`graph.py` `_merged_graph_document`, `graph_json_spec.py` "should keep other practices when saving a different load").

## (E) Build Practice Trees From Source

The knowledge graph reads each practice's files into a tree of its own, then links the trees: a step to the operations it invokes, an example to the classes it shows.

### (E) Read Practice Trees From Source
#### (S) Knowledge Graph --> [Read Modules Classes And Operations](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_practice_trees_from_source_story.test.md#story-read-modules-classes-and-operations)

Observed: Clean Engineering reads modules (folders with a module card), packages, classes, operations, properties and parameters, keeps each file's top-level functions in a `_module` class, and orders their groups under each node (`working_copy.py` `_record_clean`, `graph_spec.py` "with clean engineering", `working_copy_scan_spec.py` "over module cards").

#### (S) Knowledge Graph --> Read Clean Engineering Model Documents

Inferred: the load reads each scoped folder's `.context/*-model.md` beside the code so members and interactions the model document names join the graph (`working_copy.py` `_record_clean_models`, described in `cdd_guidance/practices/bdd/bdd.md`).

#### (S) Knowledge Graph --> Place DDD Building Blocks Under Aggregates

Observed: DDD reads bounded contexts from folders holding `.context/bounded-context.md` and places aggregates, entity roots, value objects and repositories under them by stereotype (`working_copy.py` `_record_ddd`, `graph_spec.py` "with domain-driven design").

#### (S) Knowledge Graph --> [Read Domain Documents And Code](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_domain_documents_and_code_story.test.md#story-read-domain-documents-and-code)

Observed: DDD reads the bounded contexts, aggregates, context mappings and events the bounded-context map and each domain model document write, and holds a class a document describes and the code declares, and an aggregate a document describes and a folder holds, as one node that keeps the document's place, matched by the folder the code is in and never on a name alone (`cdd_guidance/practices/ddd/reading/graph_reading.py`, `graph_reading_spec.py`; scenarios in `story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_domain_documents_and_code_story.test.md`).

#### (S) Knowledge Graph --> [Join Domain Blocks Across Documents And Code](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_domain_documents_and_code_story.test.md#story-join-domain-blocks-across-documents-and-code)

Observed: a building block is joined to the block written in its own language and to the Clean Engineering class it is, a block the domain model draws and the code declares is one node, and a bounded context is given the aggregates its file links, heads under another name, or names in plain words (`cdd_guidance/practices/ddd/reading/graph_reading.py`, `graph_reading_spec.py`). Split from Read Domain Documents And Code on 2026-11-24.

#### (S) Knowledge Graph --> [Read UX Maps](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_ux_maps_story.test.md#story-read-ux-maps)

Observed: UX reads each UX map file into screens, regions, controls, interactions and transitions, with edges to the stories a screen shows and the domain terms it names (`cdd_guidance/practices/ux/model/graph_reading.py`, `graph_reading_spec.py`; scenarios in `story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_ux_maps_story.test.md`).

#### (S) Knowledge Graph --> [Join UX Controls To The Steps They Serve](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_ux_maps_story.test.md#story-join-ux-controls-to-the-steps-they-serve)

Observed: a control, whether in a UX map or drawn on a mockup's board, is joined to the story, scenario and step its served link names, a link written from the project's folder or saved in an epic's `.context` is followed, a link that names no story file or heading joins nothing, what a control serves is kept when the scenarios are not read, and a Story Demo control is joined to the step it runs and the property it shows (`cdd_guidance/practices/ux/model/graph_reading.py`, `graph_reading_spec.py`). Split from Read UX Maps on 2026-11-24.

#### (S) Knowledge Graph --> Give Each Node Its Fidelity

Observed: each node knows the fidelity its practice's schema creates it at and every higher fidelity it belongs to (`graph.py` `Node.fidelities`, `graph_spec.py` "a node's fidelity").

### (E) [Read Story And Spec Trees From Source](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-story-and-spec-trees-from-source/read_story_and_spec_trees_from_source_story.test.md)

The knowledge graph reads the Stories practice's story maps and story tests, in whichever language they are written, and the BDD practice's specs, into trees that keep each node on its source lines. Grouped on 2026-11-24 from Read Practice Trees From Source, which had grown past nine stories.

#### (S) Knowledge Graph --> [Read Story Maps And Story Tests](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-story-and-spec-trees-from-source/read_story_and_spec_trees_from_source_story.test.md#story-read-story-maps-and-story-tests)

Observed: Stories reads epics, sub-epics and stories from story map markdown and draw.io files, and scenarios, steps and examples from story tests, keeping each node's path and line (`working_copy.py` `_record_stories`, `graph_spec.py` "with stories", `working_copy_scan_spec.py` "limited to an edited story map markdown file", "limited to an edited Python story test").

#### (S) Knowledge Graph --> [Report Story Files The Map Does Not Hold](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-story-and-spec-trees-from-source/read_story_and_spec_trees_from_source_story.test.md#story-report-story-files-the-map-does-not-hold)

Observed (exploratory-testing defect widget-21): the stories a scenarios file or a story test in code names that the map does not hold are kept in the graph and reported by `scenarios-name-a-story-on-the-map`, and a scenarios file whose stories the map holds is reported for nothing. Split from Read Story Maps And Story Tests on 2026-11-24.

#### (S) Knowledge Graph --> [Read Story Files In Any Language](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-story-and-spec-trees-from-source/read_story_and_spec_trees_from_source_story.test.md#story-read-story-files-in-any-language)

Observed: story files written in markdown, Python, TypeScript or JavaScript give the same graph, a JavaScript shared story file and screen spec are read as the TypeScript ones are, and JavaScript story tests are read as the map where no story map names their epics. Split from Read Story Maps And Story Tests on 2026-11-24.

#### (S) Knowledge Graph --> Read BDD Spec Trees

Observed: BDD reads each spec file's describe tree into spec, description, context and observation nodes (`working_copy.py` `_record_bdd`, `graph_spec.py` "with behavior-driven development").

#### (S) Knowledge Graph --> Place Story Nodes On Their Source Lines

Observed: scenarios and steps sit in source-line order, a step opens on the call holding its label, a scenario runs through its closing brace, and an imported example sits in its examples file (`graph.py` `Node._edges_in_source_order`, `Source.align_to_label`, `align_to_example_export`, `graph_spec.py` "a scenario", "a step", "an example a story test imports"); `defects.md` still lists scenario and step order under Not fixed.

### (E) Link Practice Trees Across Practices
#### (S) Knowledge Graph --> [Link Steps And Observations To Operations](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link-practice-trees-across-practices/link_steps_and_observations_to_operations_story.test.md#story-link-steps-and-observations-to-operations)

Observed: a story step and a BDD observation each get an `invokes` edge to the operations their code calls, with `invokedBy` back on the operation and setup calls of the enclosing context first (`working_copy.py` `_record_story_edges`, `_record_bdd_edges`, `graph_spec.py` "with a step that invokes an operation", `bdd_invokes_spec.py`).

#### (S) Knowledge Graph --> [Find The Class A Step Calls](../story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link-practice-trees-across-practices/link_steps_and_observations_to_operations_story.test.md#story-find-the-class-a-step-calls)

Observed: a step's `invokes` edge goes to the class its linked domain term names, the one class its seed's package holds that declares the operation, or the class the story file built the receiver as; it links nothing when two classes in reach declare the operation and the receiver's class is not written, and a link to a heading the domain model does not hold gives no edge. Split from Link Steps And Observations To Operations on 2026-11-24.

#### (S) Knowledge Graph --> Link Markdown Steps To Model Operations

Observed: a When in a markdown scenarios file with a realization gets an `invokes` edge to each operation its realization's call graph names, matched in the domain model (DDD) or class model (Clean Engineering) its domain-term links lead to, with `invokedBy` back on the operation; a renamed operation or a step with no realization stays unlinked, and `code-steps-invoke-code` reports a When whose realization names no operation of that model (`realization_links.py` `RealizationLinks`, `realization_links_spec.py`).

#### (S) Knowledge Graph --> Link Examples To Classes And Steps

Observed: an example that demonstrates a class, a then step that observes an example, and an example retrieved using a property each get their relationship edge in both directions (`schema_edges.py` `SchemaEdges.sync`, `graph_spec.py` "with an example that demonstrates a class", "with a then step that observes an example").

## (E) Apply Pattern Overlays
### (S) Person --> Add Named Overlay From Catalog

Observed: the Graph app lists the pattern overlays under `cdd_guidance/patterns` that hold practices, such as Lern domain driven, and applying one rebuilds the graph (`FilterView.tsx`, `graph.py` `available_pattern_overlays`, `app.test.tsx` "should offer built-in overlay names from the catalog").

### (S) Person --> Add Overlay Folder

Observed: Add folder opens a folder dialog, `graph.overlay_of` resolves the chosen folder to the overlay root that holds `practices/`, and the app applies it (`GraphClient.ts` `chooseOverlayFolder`, `app.test.tsx` "should apply overlays through the api when a folder is chosen", `pattern_overlay_spec.py`).

### (S) Person --> Remove Overlay

Observed: the remove control on an applied overlay takes it off and the graph rebuilds without it (`App.tsx` `removeOverlay`, `app.test.tsx` "should remove an overlay when its remove control is clicked").

### (S) Agent --> Rebuild Graph With Overlay Nodes

Observed: `graph.set_overlays` applies the overlays, reloads the open folder, and adds the overlay's node types, such as LERN node roots, client roots, routes and views parented on their aggregate (`graph.py` `Graph.set_overlays`, `working_copy.py` `_record_lern`, `pattern_overlay_spec.py` "should add the lern nodes when that overlay is applied").

### (S) Graph App --> Remember Applied Overlays

Inferred: the app stores the applied overlays in browser storage and sends them with the next load (`App.tsx` `LAST_OVERLAYS`, `readSavedOverlays`).

## (E) Explore Graph In Graph App

Retires (2026-11-15) into [Explore Graph In Files App](#e-explore-graph-in-files-app) once the Files app's graph view works.

### (S) Person --> Choose Repo Folder

Observed: the Repo folder button opens a folder dialog on the server's machine, or the person types a path, and the app loads every practice on that folder and shows its classes (`App.tsx` `browse`, `choose_folder.py`, `app.test.tsx` "should put the chosen folder on the page and show its classes").

### (S) Graph App --> Reopen Last Folder

Observed: the app reloads the last loaded folder when it opens (`App.tsx` `cdd-graph-folder`, `app.test.tsx` "should reload the last folder when the app opens", `defects.md`).

### (S) Person --> Expand Practice Tree

Observed: each practice starts collapsed and the person opens nodes one level at a time, such as a customer aggregate with its entity, repository and value objects (`GraphView.tsx` `TreeNode`, `app.test.tsx` "should leave every practice collapsed until it is opened", `defects.md`).

### (S) Person --> Follow Relationships Under Node

Observed: a node shows its relationship groups as children, such as every invoke under an operation and invokes, observes and demonstrates on a step, and a module copy shown under a class appears without its own children (`graph.py` `Node.serialize`, `app.test.tsx` "should list every invoke under an operation", "should show invokes, observes, and demonstrates on a step", "should show a module without its children and a class with its module").

### (S) Person --> Open Node Source

Observed: selecting a node shows its file, lines and text in a read-only editor, numbered from the file's own lines (`graph.py` `Graph.source`, `SourceView.tsx`, `app.test.tsx` "should number a step from its line in the file", `app_smoke_spec.py` "with an operation opened").

### (S) Person --> Unfold Calls And Classes In Source

Observed: calls, classes and blocks in the source fold and unfold in place, opening the called operation or the class of a typed variable under the line, and stories, scenarios and steps fold the same way (`source/call-expansion.ts` `inlineCallLayout`, `app.test.tsx` "should fold calls, classes, and blocks in the source", "should fold a story, a scenario, and a step the way a class folds", `defects.md`).

### (S) Graph App --> Show Load Steps While Loading

Observed: while a load runs the app polls `/cdd/progress` and shows the current step, elapsed time, a meter and a log of steps (`App.tsx`, `GraphView.tsx`, `graph/query-progress.ts`, `app.test.tsx` "should show each load step while the graph is loading").

### (S) Person --> Copy Load Failure For Agent

Observed: a failed call shows the server's diagnosis and traceback instead of loading forever, with a Copy for AI button (`server.ts` `diagnosis`, `GraphView.tsx`, `app.test.tsx` "should show the backend traceback instead of loading forever").

### (S) Person --> Switch Display Theme

Inferred: the Executive and Engineering buttons switch the page and editor between light and dark themes and remember the choice (`App.tsx` `applyTheme`, `main.tsx`).

## (E) Filter Graph In Graph App

Retires (2026-11-15) into [Filter Graph Like The File List](#s-files-app----filter-graph-like-the-file-list) and [Filter Graph By Node Type And Connector In Files App](#s-person----filter-graph-by-node-type-and-connector-in-files-app) once the Files app's graph view works.

### (S) Person --> Filter By Practice

Observed: choosing practices selects every node type, connector and rule those practices hold, and adding another practice keeps the first practice's choices (`Graph.filter_choices`, which `App.tsx` `offerChoices` asks, `app.test.tsx` "should select every node, connector, and rule for the practice", "should keep the first practice filters when another practice is added").

### (S) Person --> Filter By Node Type

Observed: choosing node types keeps only those nodes in the tree and narrows the connectors and rules offered to the ones those types carry (`App.tsx` `applyFilter`, `graph.py` `Graph.filter_choices`, `app.test.tsx` "should keep the selected node type and drop the other class", `graph_spec.py` "with operations selected").

### (S) Person --> Filter By Connector

Observed: choosing a connector keeps the nodes that sit on that kind of edge (`graph.py` `Filter._on_relationship`, `graph_view_spec.py` "should return the nodes on the selected edge").

### (S) Person --> Show Only Violations

Observed: the Violations switch sends `violations: true`, and the tree keeps only failing nodes with their violations attached (`FilterView.tsx`, `filter/filter-selection.ts`, `app.test.tsx` "should send violations when the switch is turned on", "should keep the violation attached when violations are filtered", `defects.md`).

### (S) Person --> Filter Violations By Rule

Observed: with violations on, the chosen rules decide which failures count, so a node that passes the chosen rule is left out (`graph.py` `Filter._fails_selected_rule`, `graph_spec.py` "with violations of the parameter rule").

### (S) Person --> Select All Or No Filter Choices

Inferred: each filter list has All and None buttons that choose every option or clear the list (`FilterView.tsx` `FilterSelect`).

## (E) Find Nodes For Agent
### (S) Agent --> Return Matching Nodes With Relationships

Observed: `graph.return_nodes` (the read-graph skill) returns each node matching practice, type, name, relationship and source path with its practice, ancestors, children and rules (`graph.py` `Graph.return_nodes`, `explorer.py` `FilteredNode`, `app_smoke_spec.py` "with operations selected", `working_copy_scan_spec.py` "should keep only nodes under the given path").

### (S) Agent --> Return Only Failing Nodes And Rules

Observed: `violations: true` returns only nodes that fail a rule, each with only its failing rule entries and their hits (`graph.py` `Node.rule_rows`, `working_copy_scan_spec.py` "returning violations", `rule_category_spec.py`).

### (S) Agent --> List Practice Inventory

Observed: `graph.inventory` returns each loaded practice's node counts, edge count, node types, edge kinds, rules and explorer tree, with the overlays applied and available, and the app shows the same counts (`graph.py` `Graph.inventory`, `app_smoke_spec.py` "should count the same nodes as the graph").

### (S) Agent --> List Filter Choices

Observed: `graph.filter_choices` returns the node types, relationships and rules a filter offers once practices and node types are chosen, and clears the graph's own filter (`graph.py` `Graph.filter_choices`, `app_smoke_spec.py` "with clean engineering chosen in the filter").

### (S) Agent --> Read Node Source With Members

Observed: `graph.source` returns a node's file, lines and text with every class, operation and property the graph holds so calls in it can be opened, and nothing for an id with no node such as a rule entry (`graph.py` `Graph.source`, `explorer.py` `NodeSource`, `app_smoke_spec.py` "with an id the graph holds no node for").

## (E) Check Nodes Against Graph Rules
### (S) Knowledge Graph --> Attach Schema Rules To Nodes

Observed: each node gets the rules its practice's `schema.yaml` lists for its type, with the rule's prose and whether it has an executable check (`node_rules.py`, `schema_rules.py` `slugs_for_type`, `schema_rules_spec.py` "schema rules on a node", `rule_category_spec.py`).

### (S) Knowledge Graph --> Check Nodes Against Practice Rules

Observed: each practice's rule checks run on its loaded nodes and record violations, for example Clean Engineering operation size and module depth, DDD stereotypes and repositories, Stories verb-noun names and child counts, BDD spec shape, and draw.io class titles (`rules.py` `attach_rules`, `practice_rules_registry.py`, `ce_rules_spec.py`, `ddd_rules_spec.py`, `stories_examples_spec.py`, `story_scenario_count_spec.py`, `bdd_examples_spec.py`, `drawio_rules_spec.py`).

### (S) Knowledge Graph --> Inherit Clean Engineering Rules On DDD Types

Observed: DDD types that extend a Clean Engineering type, such as an entity on a class or a bounded context on a module, carry that type's rules too (`schema_rules.py` `ce_anchor_type`, `schema_rules_spec.py` "DDD schema extends clean engineering").

### (S) Knowledge Graph --> Add Overlay Rules

Observed: an applied pattern overlay adds its own rules to the node types it names, such as LERN tier rules on a node root (`practice_rules_registry.py` `pattern_rules_for_practice`, `schema_rules_spec.py` "LERN overlay rules").

### (S) Knowledge Graph --> Mark Prose Rules As Prompts

Observed: a rule with no executable check shows as a prompt rather than passing or violating (`graph.py` `Node.rule_rows`, `graph_spec.py` "should leave do-not-invent-requirements prompt", `stories_examples_spec.py` "vocabulary-traces-to-domain-source").

### (S) Knowledge Graph --> Place Violation At Node Lines

Observed: each recorded violation keeps the file and lines of the node it was found on (`graph_rules_collection.py` `GraphRule.record`, `schema_rules_spec.py` "should place a recorded violation at the node's source", `graph_spec.py` "should store the epic child-count hit on the line that names the epic").

### (S) Knowledge Graph --> Name Rules By Practice Node And Rule

Observed: every rule is labelled `practice.node.rule`, with the owning pattern in front for an overlay rule (`schema_rules.py` `qualified_rule_label`, `schema_rules_spec.py` "a rule label", `app.test.tsx` "should list rules as practice, node, then rule").

### (E) Check Clean Engineering Code Through The Graph

Validate at Clean Engineering's modules, model and code fidelities checks what one file at a time cannot see: the size and complexity of each function, class and module, and the relationships between classes across files.

#### (S:system) Knowledge Graph --> [Record Code Metrics As Node Facts](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/record_code_metrics_as_node_facts_story.test.md#story-record-code-metrics-as-node-facts)

Requested (2026-11-10, "when we run validation at clean model or clean code we integrate the metrics ... and add those findings onto the model itself, it's just another fact on the model: what is its cyclomatic complexity"); Built (2026-11-22, the person's decisions of that day in `.sessions/_backlog/measure-code-on-the-model.md`; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/record_code_metrics_as_node_facts_story.test.md)): the Clean Engineering reader takes the measures of the files a validate is given and keeps each as a fact on its function or class node: the paths through a function (cyclomatic complexity), its readability score (cognitive complexity), and a class's total complexity, classes depended on, and groups of methods sharing no data. A measure a fact on the node already gives is read from that fact with no tool: a function's lines and parameters, a class's methods. Each other measure is supplied by the tool the project's `.context/config.json` chooses for it in the code's language (`code_measures`: lizard or the practice's own reader, for Python, TypeScript and JavaScript); code in a language with no tool chosen, or a chosen tool that is not installed, is reported by name by the measure's rule (`measures/checked_measures.py`, `code_measures_spec.py`, `code_measures_heavy_spec.py`).

#### (S:system) Knowledge Graph --> [Measure Code With The Project's Chosen Tools](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/record_code_metrics_as_node_facts_story.test.md#story-measure-code-with-the-projects-chosen-tools)

Built (2026-11-22, `.sessions/_backlog/measure-code-on-the-model.md`): each measure is taken with the tool the project's `.context/config.json` chooses for it in the code's language (`code_measures`); code in a language with no tool chosen and a chosen tool that is not installed are reported by name, a measure the project says is not measured is left out, and a project that chose no tools takes no measure (`measures/checked_measures.py`, `code_measures_spec.py`, `code_measures_heavy_spec.py`). Split from Record Code Metrics As Node Facts on 2026-11-24.

#### (S:system) Knowledge Graph --> [Record Module Measures As Node Facts](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/record_module_measures_as_node_facts_story.test.md#story-record-module-measures-as-node-facts)

Requested (2026-11-22, "the item names functions, classes and modules, and listed no measure for a module"); Built (2026-11-22, the person's decisions of that day in `.sessions/_backlog/measure-code-on-the-model.md`; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/record_module_measures_as_node_facts_story.test.md)): the same read keeps on each module node the modules that import it, and its abstractness and instability, the last two for information only. Its import loops and the modules it imports are facts every read already keeps, and copied function bodies are the facts `eliminate-duplication` reports, so no tool repeats them. Blocks of code copied across files are written as not measured until a tool is chosen, and defects for each thousand lines of a branch are not part of this build (`measures/measuring_tools.py` `ReaderTool`).

#### (S:system) Validate --> [Check Code Metrics Against Clean Engineering Limits](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/check_code_metrics_against_clean_engineering_limits_story.test.md#story-check-code-metrics-against-clean-engineering-limits)

Requested (2026-11-10, "when we run validation at clean model or clean code we integrate the metrics ... and add those findings onto the model itself, it's just another fact on the model: what is its cyclomatic complexity"); Built (2026-11-22, the person's decisions of that day in `.sessions/_backlog/measure-code-on-the-model.md`; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/check_code_metrics_against_clean_engineering_limits_story.test.md)): seven named graph rules read the measures off the nodes and report a node past its limit in the same validation report as the other rules, each naming its measure in plain English: a function over 10 paths, a readability score over 15, over 50 lines of code or over 5 parameters, a class over 100 total complexity or 30 methods, and a class whose methods fall into more than one group sharing no data. The limits are kept beside the chosen tools in the project's config. An import loop is already reported by `one-way-deps`, and a class that depends on more classes than before is kept as a fact with no rule, since it needs a base commit to compare with (`rules/code_measure_limits.py`).

#### (S:system) Validate --> [Judge Clean Engineering Rules Across Files](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/judge_clean_engineering_rules_across_files_story.test.md#story-judge-clean-engineering-rules-across-files)

Built (2026-11-22, step 2 of `.sessions/_backlog/check-clean-engineering-across-files.md`; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/judge_clean_engineering_rules_across_files_story.test.md)): rules of scope all compare the files of the whole codebase, each listing its candidates in the paths a validate is given and over the rest of the working copy when validate is asked for the judged pass (`judge_all`): `eliminate-duplication` lists, as one candidate, operations in different files whose bodies match once their own names are set aside; `hold-state-on-the-object-not-in-parameters` a parameter handed down unchanged to two other classes, and a class every operation of which takes one parameter; `do-not-invent-parallel-object-models` a second registry, a collection naming the classes another file's collection names; `use-consistent-naming` two verbs used for one target across classes; and `seam-names-current-code`, checked, a module card whose seam terms or dependencies no longer match the code. Global or ambient state, legacy names and dead code, and swallowed failures are left to the rules that already check them.

#### (S:system) Validate --> [Judge Passed Parameters And Second Registries](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/check-clean-engineering-code-through-the-graph/judge_clean_engineering_rules_across_files_story.test.md#story-judge-passed-parameters-and-second-registries)

Built (2026-11-22, step 2 of `.sessions/_backlog/check-clean-engineering-across-files.md`): `hold-state-on-the-object-not-in-parameters` lists a parameter handed down unchanged to two other classes and a class every operation of which takes the same parameter, passing one handed between a class's own operations or to a constructor; `do-not-invent-parallel-object-models` lists a second registry of the same classes, passing a list of exported names and one that spells the classes' names as labels (`cross_file_rules.py`). Split from Judge Clean Engineering Rules Across Files on 2026-11-24.

### (E) Report Unused And Poorly Connected Code

Validate at Clean Engineering's model and code fidelities reports code nothing uses for deletion, an operation only its own module calls, and classes and packages joined to the rest of the code too loosely or built where they should be owned. Grouped on 2026-11-24 from Check Clean Engineering Code Through The Graph, which had grown past nine stories.

#### (S:system) Knowledge Graph --> [Report Unused Class For Deletion](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md#story-report-unused-class-for-deletion)

Requested (`.sessions/_backlog/check-clean-engineering-across-files.md` "Every class is used or uses something"); Built (2026-11-22; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md)): a production class no other class uses and which uses none, which nothing calls into, and which none of the ways the project's `.context/config.json` names under `code_reach` reaches, is reported as no use, delete (`delete-unused-classes`), and so is a public operation of a used class nothing calls (`delete-unused-operations`). One a call the read could not join may reach, in a file that could reach it, is listed for a reading instead (`check-use-the-graph-cannot-see`). A class others use that uses nothing is in use (`rules/code_use.py`, `code_use_rules.py`).

#### (S:system) Knowledge Graph --> [Count Indirect Uses Before Reporting Deletion](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md#story-count-indirect-uses-before-reporting-deletion)

Built (2026-11-22, `.sessions/_backlog/check-clean-engineering-across-files.md`): before a class or member is reported for deletion, a use from example code counts only when production imports it, spec support the project's config names as test code gives no use, a call through a protocol is a use of each class that satisfies it, and a class or member a library outside the code read or a call the read could not join may use is listed as a candidate for a reading, not reported as a violation (`check-use-the-graph-cannot-see`; `rules/code_use.py`, `code_use_rules.py`). Split from Report Unused Class For Deletion on 2026-11-24.

#### (S:system) Knowledge Graph --> [Report Operation Used Only Inside Its Module](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md#story-report-operation-used-only-inside-its-module)

Requested (`.sessions/_backlog/check-clean-engineering-across-files.md` "internal operations left public"); Built (2026-11-22; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md)): a public operation of a class its module shows other modules, which only code inside the module calls, is listed for a reading as an operation to make private (`make-module-only-operations-private`).

#### (S:system) Knowledge Graph --> [Report Runtime Dependency That Should Be Owned](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_runtime_dependency_that_should_be_owned_story.test.md#story-report-runtime-dependency-that-should-be-owned)

Built (2026-11-22, step 2 of `.sessions/_backlog/check-clean-engineering-across-files.md`; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_runtime_dependency_that_should_be_owned_story.test.md)): `put-logic-on-the-owning-resource`, judged and of scope all, lists each class that builds another on each call from strings or dicts, or looks it up by name, naming the class as the owner to consider and the relationship it could hold instead, a part it builds once and keeps (composition) or one handed to it (association); a class it is handed, holds, or builds in its constructor, a value, a failure, a record with no behaviour, and one built from a formatted message are not listed (`cross_file_rules.py`, `reading/owned_dependencies.py`). Re-reading a file another object holds and passing the owner's data into a helper are not listed yet.

#### (S:system) Knowledge Graph --> [Report Disconnected Class](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md#story-report-disconnected-class)

Requested (`.sessions/_backlog/check-clean-engineering-across-files.md` "Disconnected classes"); Built (2026-11-22; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md)): a used class whose family is connected to other classes only by inheritance, or not at all, is listed for a reading as a relationship the model missed or as code that is not resource-oriented, naming the composition or association it may be missing (`connect-disconnected-classes`).

#### (S:system) Knowledge Graph --> [Report One-Class Package](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md#story-report-one-class-package)

Requested (`.sessions/_backlog/check-clean-engineering-across-files.md` "One-class packages"); Built (2026-11-22; [scenarios](../story_tests/map-work-into-knowledge-graph/check-nodes-against-graph-rules/report-unused-and-poorly-connected-code/report_unused_and_disconnected_code_story.test.md)): a package, a folder with no module card, holding one class and no folder is listed for a reading as unused (delete), part of a bigger package (merge), or not fully modelled (`merge-one-class-packages`).

## (E) Review Violations In Graph App

Retires (2026-11-15) into [Review Graph Violations In Files App](#e-review-graph-violations-in-files-app) once the Files app's graph view works.

### (S) Person --> See Rules Under Node

Observed: each node has a rules entry listing its passing, violating and prompt rules, and a violating node is marked in the tree (`graph.py` `Node.rule_category`, `GraphView.tsx`, `app.test.tsx` "should show a passing rule and a violating rule under the operation").

### (S) Person --> Hover Violating Rule For Message

Observed: hovering a violating rule shows its violation messages (`GraphView.tsx` `violationHint`, `app.test.tsx` "should expose the violation message when hovering a violating rule").

### (S) Person --> Open Violation In Source

Observed: selecting a violating rule opens the node's source with a banner naming the rule and message and highlights the lines the hit names (`SourceView.tsx`, `graph/graph-selection.ts` `selectionForRule`, `app.test.tsx` "should show the violation banner, highlight the source").

### (S) Person --> [Display Drawio File As Diagram](../story_tests/map-work-into-knowledge-graph/review-violations-in-graph-app/review_violations_in_graph_app_story.test.md#story-display-drawio-file-as-diagram)

Requested on 2026-11-06: a `.drawio` file opens as its diagram, with a Source tab for the XML. A violation marks the shape it names in red, and pressing a shape opens its lines in the source. Built today (checked 2026-11-10): the chat bar's files view offers Open in draw.io, which opens the file in the draw.io editor through `tools/drawio_viewer` (`drawio-viewer-client.ts:44`). Missing: a Source tab, marking the shape a violation names, and opening a pressed shape's lines.

### (S) Person --> Copy Correct Prompt

Observed: the Correct button copies a prompt holding the node, file and lines, rule, code excerpt and violation, asking for a test-driven fix (`source/violation-prompt.ts`, `app.test.tsx` "should build a Correct prompt with the rule, excerpt, and violation message").

### (S) Agent --> [Test Knowledge Graph Explorer On Session Files](../story_tests/map-work-into-knowledge-graph/review-violations-in-graph-app/review_violations_in_graph_app_story.test.md#story-test-knowledge-graph-explorer-on-session-files)

Requested on 2026-11-06: the Graph app loads a CDD session's files and shows their nodes and violations, and its specs run against those files. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

## (E) Report Graph Rules In Validate
### (S) Validate --> Build Graph From Edited Files

Observed: Validate given edited paths loads every graph practice from just those files and writes `edited-graph.json` beside the session, without touching the workspace graph (`validate.py` `_edited_graph_json`, `validate_spec.py` "should write the edited graph beside the session", "should not write the workspace graph").

### (S) Validate --> Report Own Practice Violations

Observed: the graph-rule report lists only the violations of the guidance's own practice, at each node's path and line, alongside the AI-judged rules (`validate.py` `_graph_and_ai_rule_report`, `validate_spec.py` "should report only the violations of the guidance's own practice", "should append a graph-rule report from summary JSON and still include AI rules").

### (S) Validate --> Report Saved Graph Hits

Observed: with `graph: true` or a graph path, Validate reads the hits from the saved `graph.json` or `graph_return_nodes` JSON (`validate.py` `_resolve_graph_json_paths`, `validate_spec.py` "with the saved graph", `checked_graph_spec.py` "that was named a saved graph document").

### (S) Validate --> Leave Unedited Files Out

Observed: hits in files outside the named paths stay out of the report (`validate_spec.py` "should leave files outside the edited paths out of the report").

### (S) Validate --> Refuse Missing Path

Observed: a named path that is not there, or not under the session's root, is refused with the path and the root it was read from, so no graph is built from nothing (`validate.py`, `validate_spec.py` "should refuse, naming the path and the root it was read from").

### (S) Validate --> Save Checked Graph Beside Report

Observed: the graph a validation checked is saved beside its report under the same name, keeping the rule hits on their nodes and leaving earlier reports' graphs as they were (`validate.py` `_save_reports`, `validate_spec.py` "should save the graph it checked beside the report, under the same name").

### (S) Session Board --> Count Graph Hits From Report

Observed: the session board reads the graph saved beside a validation report and counts its rule hits, so a fidelity with graph-rule violations still needs Validate (`space/kanban/report.py` `ReportFile.report`, `validate_fidelity_story.test.py` "Count Validate done only with no graph-rule violations").

# (E) Draw Practice Models On Claude Whiteboard

Requested (2026-11-15, ticket claude-whiteboard): Claude Whiteboard becomes one more channel a practice renders to and loads from, with the same architecture and object model as drawio and miro. The channel-agnostic diagram types (`DiagramNode`, `DiagramClass`, `DiagramModule` in `clean_engineering/model/diagram/diagram_node.py`; `DiagramStoryNode`, `DiagramStoryMap` in `stories/model/diagram_story_map.py`) are extended by whiteboard types exactly as `DrawIOClass`, `DrawIOModule` (`clean_engineering/model/drawio/diagram_node.py`) and `MiroStory`, `MiroEpic`, `MiroStoryMap` (`stories/model/miro/nodes.py`) extend them. The code every practice shares (the whiteboard element, the board and its writes) goes in `harness/whiteboard`; each practice's whiteboard types go in `cdd_guidance/practices/{practice}/model/whiteboard`; and the format is registered with the practice's adapters (`PracticeFormats`, `harness/guidance/practice_formats.py`) as `drawio` and `miro` are. A board is a Claude Artifact made from the Whiteboard type: `board/meta` holds its title and back-to-front order, and each `elements/<id>` is one shape, section, text or arrow, written and read through the artifact's store. The difference from drawio and miro is only that: the artifacts are whiteboards in Claude, loaded into the graph from what was rendered.

## (E) Lay Out Shared Whiteboard Elements

Requested (2026-11-15, "common code should go into harness/whiteboard (eg whiteboard node, whiteboard, etc)"): the board and its elements, which every practice's whiteboard types draw with, as `DrawioVertex` and the drawio page are for drawio.

### (S:technical) Whiteboard Node --> Place Element From Diagram Geometry

Requested: a whiteboard node takes the `Geometry` a diagram node was placed at (`clean_engineering/model/diagram/geometry.py`) and writes it as the element's `x`, `y`, `w` and `h`, so a whiteboard is laid out by the same placement as its drawio.

### (S:technical) Whiteboard Node --> Write Node As Board Element

Requested: each node writes itself as one `elements/<id>` record — a `shape` with its kind, colour and text, a `container` for a section, or a `text` for a title — as `DrawioVertex.append_to` writes one `mxCell`.

### (S:technical) Whiteboard --> Order Board Elements Back To Front

Requested: the board writes `board/meta` with its title and every element id in back-to-front order, sections before what they hold.

### (S:technical) Whiteboard --> Join Elements With Arrows

Requested: a dependency or relationship between two nodes is written as an `arrow` element from one element id to the other, with its sides and, where its meaning is not plain, its label.

### (S:technical) Whiteboard --> Keep Element Ids Across Renders

Requested (as drawio's `keep_positioning` and `previous` keep a diagram's layout): a node drawn before keeps its element id and the position a person moved it to, and only new nodes are placed.

## (E) Render Practice Models To Whiteboard

Requested (2026-11-15, "practice specific rendering goes in practices/{practice}/model/whiteboard"; "whiteboard should extend diagram just like drawio and hopefully miro"): each practice that draws a diagram today draws the same model on a whiteboard.

### (S) Agent --> Lay Out Story Map On Whiteboard

Requested: `WhiteboardStoryMap`, `WhiteboardEpic`, `WhiteboardStory` and `WhiteboardIncrement` extend the `Diagram*` story types as the miro types do, drawing epics and sub-epics as bars, stories as cards with their actor above, and increments as lanes.

### (S) Agent --> Draw Module Dependencies On Whiteboard

Requested: a whiteboard module extends `DiagramModule` as `DrawIOModule` does, drawing each module with its purpose and seam terms, and its dependencies as arrows.

### (S) Agent --> Show Class Members And Relationships On Whiteboard

Requested: a whiteboard class extends `DiagramClass` as `DrawIOClass` does, drawing each class with its stereotypes, properties and operations, an imported class dashed, and its relationships as arrows.

### (S) Agent --> Group Aggregates In Bounded Context Sections

Requested (DDD draws its bounded context map in drawio today, `ddd/model/drawio/drawio_bounded_context_map.py`): the same map drawn on a whiteboard, each context a section holding its aggregates.

### (S) Agent --> Connect Screens By Navigation Moves

Requested (UX draws its information architecture in drawio today, `ux/model/drawio/nodes.py` `DrawioUxMap`): the same screens and the moves between them drawn on a whiteboard.

## (E) Publish Board To Claude

Requested (2026-11-15, "the only difference you are creating whiteboard artifacts in claude"): what a render wrote reaches a Whiteboard artifact in Claude.

### (S) Agent --> [Create Whiteboard Artifact For Fidelity File](../story_tests/draw-practice-models-on-claude-whiteboard/publish-board-to-claude/publish_board_to_claude_story.test.md#story-create-whiteboard-artifact-for-fidelity-file)

Requested: the first render of a fidelity's file creates a Whiteboard artifact titled after it, and the board's address is kept beside the file, so the next render updates the same board.

### (S) Agent --> Write Board Elements To Artifact Store

Requested: the agent writes `board/meta` and the elements, back to front, to the board's store in batches the store accepts.

### (S) Agent --> Update Changed Elements On Existing Board

Requested: a render to a board that exists writes only the elements whose content changed, adds the new ones and removes the gone ones with their arrows, and never rebuilds the board, so what people moved or added stays.

### (S) Agent --> Link Board From Fidelity Outputs

Requested: the fidelity's files list the board's address with its drawio and markdown, so a person opens the board from where they open the other formats.

## (E) Load Whiteboard Into Practice Model

Requested (2026-11-15, "loading graph from that"): a board read back becomes the practice's model, as a drawio or miro file is parsed today (`MiroStoryMap.load`, `DrawIOModule.from_cell`).

### (S) Agent --> Read Board Into Whiteboard File

Requested: the agent reads the board's `board/meta` and every element from its store into a file in the session, which the practice reads as it reads a `.drawio` file.

### (S:system) Whiteboard Story Model --> Parse Story Map From Board

Requested: epics, sub-epics, stories with their actors, and increments come back from the board's elements, keeping each story's kind.

### (S:system) Whiteboard Class Model --> Parse Classes And Modules From Board

Requested: classes with their members and stereotypes, modules with their seam terms, and the arrows between them come back from the board's elements.

### (S:system) Knowledge Graph --> Load Whiteboard File Into Graph

Requested: a whiteboard file in a fidelity's outputs is read into the knowledge graph through its practice's adapter, as its drawio is, so graph rules run on what the board shows.

## (E) Choose Whiteboard Format In Channels

Requested (2026-11-15, "add claude whiteboard as a channel"): the whiteboard format is picked and run like any other format.

### (S) Person --> Pick Whiteboard Format Chip

Requested: the whiteboard is offered in the diagram format group (`Format.GROUPS`, `harness/markdown/format.py`), so its chip shows on the board ticket and in the chat bar for each fidelity that offers it.

### (S) Agent --> Generate Fidelity Into Whiteboard

Requested: `/actions-generate` with `format=whiteboard` writes the fidelity's whiteboard and publishes it, and `/actions-render` turns an artifact already written into one.

### (S:system) Story Channel --> Round Trip Story Map Through Whiteboard

Requested: the story channel spec (`stories/model/story_channel.feature.py`) saves a map to the whiteboard and reads it back from every other format, keeping each epic, sub-epic, story and actor, with scenarios left out as for drawio and miro.

### (S) Agent --> Scan Whiteboard Layout Rules

Requested (as `Drawio.scan` runs drawio's layout scanners): the whiteboard's own layout rules, such as no overlapping elements and no arrow crossing a shape, are scanned on its file, and a definitive failure sends the generator to repair.

# (E) Connect Sessions Across Channels And Apps

The chat bar, the CDD Kanban, the Story UI editor and the knowledge graph work on one ticket's session at a time, so each one opens the others on that ticket and shows what the others are doing. Validation moves into generate: the graph is rebuilt from what changed, its violations are read straight from it, and Fix is an action of its own. The stories were requested on 2026-11-06.

## (E) Connect Chat Bar Board And Story UI

### (S) Person --> [Open Board Side Panel From Chat Bar](../story_tests/connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui/connect_chat_bar_board_and_story_ui_story.test.md#story-open-board-side-panel-from-chat-bar)

Requested (2026-11-06, "chat band -> board side panel"): the chat bar opens the active ticket's board card and tiles in a side panel beside the chat.

### (S) Chat Bar --> [Keep Chosen Formats Across Actions In A Fidelity](../story_tests/connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui/connect_chat_bar_board_and_story_ui_story.test.md#story-keep-chosen-formats-across-actions-in-a-fidelity)

Requested (2026-11-06, "have format saved across actions in fidelity"): the formats picked for a fidelity stay picked when the person switches between generate, render, sketch, iterate, document and fix, so each action writes the same formats without picking them again. Built (2026-11-23): the formats picked for a fidelity are saved on its session (`guidance_selection.py` `select`), and the chat bar and the board show those same chips for every action (`format-choices-client.ts`). Generate, iterate, sketch, render and document each take them (`@on_stage(..., TAKES_FORMATS)`), so every one of their commands names the same `format=` (`GuidanceSelection.commands_on`; `session_spec.py` "should name the same chosen formats for sketch, iterate and document as for generate", `action_catalogue_spec.py`). Fix is not an action on a fidelity's stage, so it has no command of its own to name formats in; validate reads the files in the formats they already have.

### (S) Person --> [Start Ticket Session From Increment](../story_tests/connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui/connect_chat_bar_board_and_story_ui_story.test.md#story-start-ticket-session-from-increment)

Requested (2026-11-06, "increment could be a separate ticket/session in board"; "create a ticket on board on demand in backlog with proper naming reference to story map increment"): the Story UI editor's increments view offers Create ticket on each increment; pressing it adds a ticket to the board's backlog named after the story map and the increment, with its own session holding that increment's stories.

### (S) Board App --> [Show Increment Ticket In Story UI](../story_tests/connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui/connect_chat_bar_board_and_story_ui_story.test.md#story-show-increment-ticket-in-story-ui)

Requested (2026-11-06, "story UI -> board/chat integration"): an increment that has a ticket shows that ticket's stage and active state in the Story UI editor.

## (E) Check Work In Generate

### (S) Generate --> [Refresh Graph After Generate](../story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md#story-refresh-graph-after-generate)

Requested (2026-11-06, "generate --> load refreshed graph based on changes immediately"): when generate writes a fidelity's files, the knowledge graph rebuilds those files at once, without a separate load or Validate run. Built today (checked 2026-11-10): generate tells the agent to call validate afterwards, and validate refreshes the graph (`generate.py:32-33`, `graph.py:1397`). Missing: generate refreshing the graph itself.

### (S) Knowledge Graph --> [Attach Violations To Latest Graph](../story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md#story-attach-violations-to-latest-graph)

Observed (checked 2026-11-10): a refresh drops and re-reads the files, then `practices.check()` records each hit on its node (`harness/graph/graph_build.py:368-394`, `graph.py:1105,1131`), and violations are saved per node in graph.json (`saved_graph.py:134,153`); a refresh saves only the checked files' nodes, not the whole graph.json. Was: Requested (2026-11-06, "violations now attached to latest graph automatically"): each rebuilt node carries its graph-rule violations, so the latest graph is where every violation is read from.

### (S) Generate --> [Judge Rules During Generate](../story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md#story-judge-rules-during-generate)

Requested (2026-11-06, "judge validation must be part of generate, merge the two actions"): generate ends with the agent's rule-by-rule judgment of what it wrote, saved with the graph's hits, so a generate counts as generated and validated. Built today (checked 2026-11-10): generate ends by calling validate, which runs the AI judgment and saves it with the graph hits (`generate.py:32-36`, `validate.py:80`). Missing: one action; validate is still a separate call, log line, and board and chat bar action.

### (S) Agent --> [Fix Graph Violations](../story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md#story-fix-graph-violations)

Requested (2026-11-06, "/fix is a first class action; fix rule; file; default across all rules / files"): Fix is an action of its own: on one rule, on one file, or by default on every violation of every rule in every file, reading the violations from the latest graph.

### (S) Agent --> [Validate Fidelity On Demand](../story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md#story-validate-fidelity-on-demand)

Requested (2026-11-06, "validate still exists as independent action"; "validate is a slash command story only now"): Validate runs on its own on any files only as the `/actions-validate` slash command, and its report is saved as today; the board and the chat bar have no Validate, since generate judges the rules. Built today (checked 2026-11-10): `/actions-validate` runs and saves its report. Missing: validate is still on the board tiles (`action-bar-view.tsx:64-70`) and in the chat bar's stage actions.

### (S:system) Claude Code --> [Check Graph Rules When An Artifact Changes](../story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md#story-check-graph-rules-when-an-artifact-changes)

Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "Validate on save"): when an artifact in a session changes, the graph rules run on it and the band's violation count updates, with no explicit validate. Built on release-2 (2026-11-15) for one file: with the Files app's Rules toggle on, `SessionGraph.alone`, a *DocumentGraph* reads the open file into the session's live graph when it changed, in under a second, and answers its broken rules. Built (2026-11-24): after each Edit or Write the agent makes that goes through, the chat bar calls `session.check_changed_artifact` without holding the agent up; the session runs Validate on that file alone for each fidelity the chat bar shows that declares it (`ChangedArtifact`, `space/session/validation/changed_artifact.py`), saving a report and logging its validate line, and the bar reads the board again, so its violation count follows the edit (`harness/chat-ui/pane/hooks/chat-bar/changed-artifact-client.ts`).

## (E) Change Stories From Canvas And Story UI

Intended ([integrate-stories-with-the-canvas-explorer.md](../.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md)): a person adds or changes a story from the canvas or from story-ui, or comments on one, and the map updates. Both paths send commands ("add story X under Y"), never a diff of the picture, and end in the same story code.

### (S:system) Design Canvas --> Give Each Map Card A Stable Node Id

Intended (integrate-stories-with-the-canvas-explorer.md slice 2): each card drawn by `Place.card()` and each explorer entry carries a `data-node` derived from the story path, which every comment and command below names.

### (S) Person --> Comment On A Story Card

Intended (integrate-stories-with-the-canvas-explorer.md slice 3): the canvas declares `comments` with `composer_only: true, customAnchors: true` and opens a composer anchored to the card's node id.

### (S) Agent --> Change Story Code From A Canvas Comment

Intended (integrate-stories-with-the-canvas-explorer.md slice 3): the agent reads the comment through `ArtifactComments`, changes the story code, replies on the thread and regenerates the map.

### (S) Agent --> Refresh Map Artboard From A Data File

Intended (integrate-stories-with-the-canvas-explorer.md slice 4): `Main.dc.html` draws from `project/data/story-map.json`, so an update publishes one data file instead of a whole new version.

### (S:system) Story UI --> Save Story Map To Story Files

Intended (integrate-stories-with-the-canvas-explorer.md slice 5): a `StoryMapRepository` adapter over the CDD story graph takes the place of MongoDB, so a story added in story-ui appears on the next map refresh.

### (S) Person --> Comment On A Story In Story UI

Intended (integrate-stories-with-the-canvas-explorer.md slice 5): story-ui gains comments, keyed by the same node ids as the canvas. Requested (2026-11-10, "native claude markup panel": "annotate on the story editor app with notes and have a canvas like experience"): a comment goes straight to Claude for processing, as a canvas comment does.

### (S) Person --> Rearrange Stories Inside The Canvas

Intended (integrate-stories-with-the-canvas-explorer.md slice 6, after Phase 0 of the asset reuse plan): story-ui's `StoryHierarchyView` mounts in the canvas, with its drag and drop sent through a transport standing in for REST.

# (E) Review End-To-End Screens

Intended ([e2e-testing ticket](../.sessions/e2e-testing/e2e-testing.md)): every end-to-end step records a screenshot keyed story › scenario › step, and the agent checks each screen against the phase before it: a walk by hand against the scenario text (TDD Flow A steps 1–2), the e2e test against the accepted walk (Flow A step 3), and every later e2e run against the last accepted run (regression). The run folders and pixel check come from pml-web's `test-utils/legacy-compare/` (`report.ts`, `story-legacy-compare.ts`, `release-baseline.ts`). The daily e2e run is `harness/release/test_runs.py` today; packaging results for the canvas stays under Check Screens Against Their Scenarios.

## (E) Walk Scenarios By Hand

Intended (ticket, "Flow A: a new boundary", steps 1–2, and "Walk report"): the first run of a new boundary is the agent driving the real app through each scenario, as a person would.

### (S) Agent --> Screenshot Each Step Of A Walk

Intended (ticket, Flow A step 1): while walking a scenario in the running app, the agent takes a screenshot after each Given, When and Then and records it, with the step text, as one row of the walk's `results.json` under its story › scenario › step key, marked walked by hand.

### (S) Agent --> Judge A Step's Screen Against Its Step Text

Intended (ticket, Flow A step 2): the agent records **meets the intent** or **misses the intent** for each step, with its reason: the Given's state is visible, the When took effect, the Then shows the right values, labels and messages. A step that misses is fixed and walked again.

### (S) Agent --> Write The Walk Report

Intended (ticket, "Walk report"): `report.ts` reduced to one run writes one self-contained page per sub-epic and a story map page: for each step its Given/When/Then text, its one screenshot embedded at half size, and its verdict and reason; scenarios with a missed step open by themselves.

### (S) Person --> Accept A Walk As The Reference

Intended (ticket, Flow A step 2, `person-accepts-the-baseline`): the person reviews the walk report, and accepting it makes the walk the reference the sub-epic's e2e tests are compared with. A walk with a step that misses its intent is not accepted.

## (E) Capture End-To-End Steps

Intended (ticket, Flow A step 3 and "Compare reports"): the e2e test that captures a walked path records the same steps, and is compared with the accepted walk.

### (S:system) Story Test --> Screenshot Each Step Of An E2E Run

Intended (ticket, "Step capture hook", `every-step-captured`): after each Given, When and Then of a `*.story.ui.spec.ts` test, the step helper waits until the page settles (as `story-legacy-compare.ts` does), takes the screenshot, and writes the step's row to the run's `results.json`, marked run by a test, with its pass or fail.

### (S) Agent --> Compare An E2E Run With The Accepted Walk

Intended (ticket, Flow A step 3): each step's screen is paired with the same step of the accepted walk; where they differ the agent fixes the test or the code and reruns.

### (S) Agent --> Walk A Disputed Step Again

Intended (ticket, Flow A step 3): when it is unclear whether the walk or the test is right, the agent walks that step by hand again and compares once more.

### (S) Person --> Accept An E2E Run As The First Baseline

Intended (ticket, Flow A step 3): when every pair matches, or the person accepts the explained differences, the run becomes the sub-epic's first regression baseline.

## (E) Review E2E Runs For Regressions

Intended (ticket, "Reviewing e2e screens: every e2e run", `every-run-reviewed`): every later e2e run, by ticket, by hand or scheduled, is compared with the last accepted run before its result counts.

### (S:system) E2E Review --> Choose The Baseline Run

Intended (ticket, "Run folders"): the run to compare with is the last accepted run of the same sub-epic, as `release-baseline.ts` and `end-to-end-paths.ts` choose it in pml-web; accepted baselines are kept on a branch, as pml-web keeps `e2e-latest`.

### (S:system) E2E Review --> List Changed Step Pairs By Pixels

Intended (ticket, "Pixel prefilter"): each step is paired with the same step of the baseline, and only pairs whose 8px blocks differ (`lookDifference` in `story-legacy-compare.ts`) go to the agent; a step with no earlier screen is listed as new.

### (S) Agent --> Judge A Changed Step Pair

Intended (ticket, step 3 of the review, `ai-judges-every-changed-pair`): the agent reads both screens, the step text, and the stories and code changed since the baseline, and records one verdict with its reason through `record_verdict`: **intended**, citing the change behind it; **regression caught**, naming the failing test; **missed by the tests**; or **noise**.

### (S) Agent --> Add A Failing Test For A Missed Change

Intended (ticket, step 4 of the review, `missed-change-adds-a-test-first`): for each pair missed by the tests, the agent writes the test at the layer that owns the behaviour, sees it fail, fixes the code and reruns. Noise is fixed in the harness and rerun, never accepted (`noise-is-fixed-in-the-harness`).

### (S) Person --> Accept A Reviewed Run As The Baseline

Intended (ticket, step 5 of the review): once every changed pair is intended, the person reviews the report, and accepting it makes the run the new baseline. Nothing else moves the baseline.

### (S:system) CDD Server --> Review The Daily E2E Run

Intended (ticket, "Daily run"): when the daily e2e run ends, the cdd server starts the regression review in a background agent session and raises a toast for each step judged missed by the tests; the fix happens in a ticket.

## (E) [Run Test Tiers One At A Time](../story_tests/review-end-to-end-screens/run-test-tiers-one-at-a-time/run_test_tiers_one_at_a_time_story.test.md)

Observed (`harness/release/test_runs.py`; `test_runs_spec.py`, `test_runs_heavy_spec.py`): the test runner, the cadence and `scripts/test.ps1` run one tier at a time on a checkout, and the record of test runs keeps the runs the release reads. Closing choice 12 of the release-1-2-fixes exploratory testing asked whether the test runner gets a story on the map; the person decided on 2026-11-23 that it does.

### (S) Person --> [Run Test Tier](../story_tests/review-end-to-end-screens/run-test-tiers-one-at-a-time/run_test_tiers_one_at_a_time_story.test.md#story-run-test-tier)

Observed (`harness/release/test_runs.py`, tested by `harness/release/test_runs_spec.py` and `test_runs_heavy_spec.py`): `python -m harness.release.test_runs <tier>` and `scripts/test.ps1` each wait for a tier already running on the same checkout, saying which process they wait for, and the cadence starts nothing while one runs. Its scenarios are tested by those specs; no story test file runs them.

### (S:system) Test Runner --> [Record Test Run](../story_tests/review-end-to-end-screens/run-test-tiers-one-at-a-time/run_test_tiers_one_at_a_time_story.test.md#story-record-test-run)

Observed (`harness/release/test_runs.py`, tested by `harness/release/test_runs_spec.py` and `test_runs_heavy_spec.py`): the record of test runs keeps the run the release reads as a tier's latest: a run again after a killed run is the latest, the killed one abandoned; the process the cadence started finishes the run the cadence recorded rather than recording a second; and a run by `scripts/test.ps1` on uncommitted edits is never the tier's latest result. Its scenarios are tested by those specs; no story test file runs them. Split from Run Test Tier on 2026-11-24, as a sub-epic holds at least two stories and keeping the record is a mechanic of its own.

## (E) Read E2E Reports

Intended (ticket, "Report"): one report shape for all three comparisons, from `report.ts`.

### (S) Person --> Open A Sub-Epic's Step Report

Intended (ticket, "Compare reports"): one page per sub-epic shows story › scenario › each step with its screen, or its two screens side by side, the test result, and the verdict with its reason.

### (S) Person --> Filter A Report To Changed Or Missed Steps

Intended (ticket, "Compare reports"): a filter on the page shows only the steps that changed or that missed.

### (S) Person --> Open The E2E Story Map Report

Intended (ticket, "Report"): a story map page over every sub-epic shows the pass, changed and missed counts per story and sub-epic, each linked to its sub-epic's page, as `writeStoryMapReport` does in pml-web.

### (S) Person --> Read Earlier E2E Runs

Intended (ticket, "Report"): each run also writes a page without images and a `summary.md` section into the run history, which is never cleared, as `writeHistoryReport` does in pml-web.

### (S) Chat Bar --> Show The Latest E2E Review In Server Health

Intended (ticket, "Health line"): the server health report shows the latest run, its changed and missed counts, and a link to the story map page.

---

## Scope boundary

**In scope:** Authoring an Agent Toolset with `@agent_tool` and `@agent_instructions`. Installing that toolset as two writes — File Installation publishes skill, slash command, and rules as one story (same channel, same write) and Mcp Installation publishes `mcp.json` — then invoking the skill, slash command, and MCP tool and prompt. Installed rules are not invoked as a file check — they constrain valid output. Context Guidance is installed the same way (skill and `.mdc` rules), invoked so `instructions` come back, then used to generate content those rules constrain. Practice Guidance is that same Guidance plus registered fidelities — invoke at practice scope and at fidelity scope; shared rules and fidelity-specific rules each constrain the matching AI output. Hook dispatch; extracting co-located markdown via `@markdown`; the CDD Kanban and the Chat Bar as two channels that move a ticket's session through its practices, each with its own stories; the practice content editor apps those channels invoke (Story UI, design canvas, Graph app), with each app's own story map; Claude Whiteboard as a format that practices render to and load from, extending the shared diagram types as drawio and miro do; connecting sessions across the channels and apps, which joins the channels and apps on one ticket, and validation read from the latest graph; reviewing end-to-end screens step by step against a walk by hand and the last accepted run; every host-action kit from `actions/.context/module-context.md` (`partition`, `grill`, `sketch`, `iterate`, `generate`, `document`, `render`, `satisfy`, `validate`, `scan`, `repair`, `createRule`).

**Out of scope:** Catalog HTML pages; on the Chat Bar, the board's whole-board views (columns, Backlog items, WIP limits, side panels, ticket hierarchy) and sending one action to a whole stage (CDR 0001); one-time renames and repository moves; YAML manifest CLI / `tools.ps1` invoke; inventing extra practices or product domains beyond this framework spine; scenario and acceptance-test text (later fidelities).
