# Increments summary

What each increment delivers and why it matters, in build priority order. Drawn from [thin-slice.md](stories/thin-slice.md) (order set on 2026-11-10); story counts are the stories listed under each increment there.

| # | Increment | Stories |
|---|---|---|
| 0 | Built Today (baseline) | 248 |
| 1 | Maintain Tickets On Board | 11 |
| 2 | Integrate Practice Content Editor Apps | 9 |
| 3 | Sync Design Canvas With Production | 21 |
| 4 | Integrate Stories With The Canvas Explorer | 14 |
| 5 | Enter Commands Faster | 5 |
| 6 | Measure Code On The Model | 2 |
| 7 | Check Clean Engineering Across Files | 5 |
| 8 | Fully Integrated App Flow | 39 |
| 9 | Review Work In Board Files | 5 |
| 10 | Customize Board Workflow | 12 |
| 11 | Author Story Maps | 14 |
| 12 | Guard Work And Recover Fast | 11 |
| 13 | Show Board Quickly | 3 |
| 14 | Bring Chat Bar Level With Board | 10 |
| 15 | Draw Linked Models On The Canvas | 8 |
| 16 | Suggest The Next Step | 5 |
| 17 | Maybe Later | 1 |
| | **Planned (1–17)** | **175** |

---

## 0. Built Today — 248 stories

The starting line, not a slice to build: what the framework, the CDD Kanban, the Chat Bar and the apps do now, grouped as the 27 lessons of the [Learning plan](#learning-plan) below, each topic leaning only on the ones before it.

| Topic | Lessons |
|---|---|
| Generate and check | Install · Practices, fidelities, actions and stages · Generate · Document and render · Validate · Satisfy · Injected rules and toasts |
| Sketch and iterate | Grill, sketch and iterate |
| Sessions | Sessions, worktrees and branches · Handoffs and decision records · Server health |
| Real context and deeper stages | Partition · Document capture · Live-app sandbox · Meeting notes · Specification and implementation · Background diagnosis |
| The CDD Kanban and the visual apps | CDD Kanban · Kanban fidelity work · Story UI editor · Design canvas and story demo · Knowledge graph · Catalog and project approach |
| Improve and extend CDD | Guidance repair · Pattern overlays · Builders and annotations · Agent BDD and prompt log |

## 1. Maintain Tickets On Board — 11 stories - IN PROGRESS

A person can edit a ticket's text, reorder tickets in a column, tag and delete them, and arrange them as parents and children: add a child, see children inside the parent, detach a child or give it a new parent, with the parent sitting at its leftmost child's stage.

The benefit is a board people can actually keep tidy by hand. Backlog grooming and breaking big work into smaller pieces happen on the board itself instead of through file edits or commands, which finishes the Kanban as a working tool.

## 2. Integrate Practice Content Editor Apps — 9 stories

The board and chat bar open the Story UI editor, the Claude Design story explorer and the Knowledge Graph app already scoped to the ticket's own stories and practices, with each app deployed carrying the board's state.

The benefit is no more hunting for the right map or filtering the graph by hand: one click takes a person from a ticket to its content in the right tool, using what each app already does, and lets them trace a story through its artifacts.

## 3. Sync Design Canvas With Production — 21 stories

The design canvas shows production as it really is. Every packaged file is proven against the product repo by hash, styles and assets come from one pinned Design System package, each screen mounts the real production view with fixture data, hosted edits are pulled back before the next version, and a screen under redesign is detached and marked diverged until its change ships.

The benefit is that designers and reviewers stop working from stale copies: drift fails a check, traceability is reported as a percentage, and redesigns are visibly separated from what is live. Every later canvas increment builds on this.

## 4. Integrate Stories With The Canvas Explorer — 14 stories

A person tests a screen against its scenarios from the explorer — each scenario marked passed, failed or stale, with Thens run and UI steps played on the screen — and changes stories by commenting on the canvas or in Story UI, with the map refreshing and the change landing in the story code.

The benefit is one loop between design and specification: screens are checked against the behaviour they promise, and story feedback given where people look at the design flows straight into the same source of truth.

## 5. Enter Commands Faster — 5 stories

A person types a CDD command with actions, practices, fidelities and formats offered as they type, sees argument hints, can add a comment to a sent command, and sees CDD tool calls announced.

The benefit is fewer mistyped or half-remembered commands and less trips to the help: the framework's vocabulary is discoverable right at the prompt.

## 6. Measure Code On The Model — 2 stories

Validating at the Clean Engineering model or code fidelity measures each function, class and module, stores each measure as a fact on its graph node, and reports anything past a limit in the same validation report.

The benefit is that code-size and complexity limits are checked as part of the practice, where the violation can be fixed, replacing the removed always-on metrics gate.

## 7. Check Clean Engineering Across Files — 5 stories

Clean Engineering validation finds problems that only show across files — unused classes, runtime dependencies that should be owned, disconnected classes, one-class packages — as graph rules, plus one AI-judged pass over the codebase where the graph cannot answer.

The benefit is that structural decay is caught automatically instead of by agents running cross-file passes by hand.

## 8. Fully Integrated App Flow — 39 stories

The chat bar, board, Story UI editor with its story explorer, and the Knowledge Graph app work on one ticket together. Generate refreshes the graph and judges rules as it goes, violations are read and fixed from the latest graph on both board and chat bar, the two stay in sync, and the story explorer runs inside Story UI framed by design canvas screens — one screen per story and step, with playback, navigation and fallbacks to screenshots.

The benefit is a single connected workspace: a person moves from ticket to story to screen to graph without context switches, and every view agrees on what is wrong right now.

## 9. Review Work In Board Files — 5 stories

A person reads a ticket's context and changed files in a rich viewer, opens session files from the details, comments on a file selection straight to the chat, and sees the AI's changes as a diff.

The benefit is reviewing agent work on the board where the ticket lives, with feedback going directly back to the agent.

## 10. Customize Board Workflow — 12 stories

A team shapes the board's stages, column policies, todo list, work-type flows and testing strategy, and the board displays, moves, approves and tracks tickets along that customized workflow, including a human-review column and a sub-agent toggle.

The benefit is that the board fits the team's way of working rather than one fixed process.

## 11. Author Story Maps — 14 stories

The Story UI editor gets its remaining stories: a dashboard to pick maps, nested sub-epic lanes, a node inspector, show/hide scenarios and examples, save history and view-state recovery, real-time shared sessions, and an AI chat panel that proposes map changes for review before applying them.

The benefit is a complete story-map authoring tool for collaborative and AI-assisted work, with every save traceable.

## 12. Guard Work And Recover Fast — 11 stories

A person sees at once when CDD is down and fixes it from where they are — reconnect, reinstall, reload everything, update or restart parts from the board or chat bar — and the agent is stopped before it breaks a rule: forbidden edits refused, work outrunning its fidelity warned, banned words caught, branch mismatches flagged.

The benefit is less lost time to a dead server and fewer rule violations that must be cleaned up afterwards.

## 13. Show Board Quickly — 3 stories

`board.show` stops repeating git checks, guidance parsing and session file reads within one board build, so the board and chat bar answer faster and the kanban tool spec runs in under 60 seconds.

The benefit is a snappier board and faster tests; small and technical, it can go in at any point.

## 14. Bring Chat Bar Level With Board — 10 stories

Everything a person can do to one session on the board they can do from the chat bar: move back a stage, mark done, choose practices and folders, open fidelity help, fix violations, add backlog items, and commit, push and pull.

The benefit is that people who live in the chat never have to switch to the board for routine session work.

## 15. Draw Linked Models On The Canvas — 8 stories

The bounded context map, domain model and module class models are drawn as canvas artboards matching their drawio layouts, linked so a person clicks from a story to its screen, classes and context and back, sees which classes a scenario touches and which stories exercise a class, and sees model nodes that fail rules.

The benefit is navigable traceability across practices in one visual place. It depends on nothing and can run alongside increments 3 and 4.

## 16. Suggest The Next Step — 5 stories

The chat proposes the next command, writes a handoff when a session ends, shows the latest handoff, and offers to capture correction-log entries and decision records.

The benefit is less "what now?" between steps, and knowledge that would otherwise be lost in a chat is captured as it happens.

## 17. Maybe Later — 1 story

Work set aside because it is complicated and not needed yet: nesting a child ticket's own branch and session under its parent. Picked up only when asked.

---

## Learning plan

How to teach what is built today (Increment 0): what the framework, the CDD Kanban, the Chat Bar and the apps do now. The 27 lessons below are drawn from the README, `catalog/workflow.md`, `.context/cdd-approach.md`, every module's `.context/module-context.md`, the installed skills, and the Built Today stories in the story map. Each lesson is one feature a person can be taught on its own, told from their point of view. They are grouped by topic, and each lesson leans only on the ones before it.

Each lesson has the same parts: **What you do**, **What you get** (the benefit), **Try it** (a command or place to start), **Or from the chat bar** (where the chat bar can do it), **Under the hood** (where it lives in the code) and, for the ones the chat bar or board drive, **What happens underneath** (the steps the system takes). The CDD Kanban does everything the chat bar does for every ticket at once, so it is taught later, in its own topic.

### Generate and check: get CDD running, make your first artifact, and hold it to written rules

**Lesson 1. Install CDD into your IDE**
- *What you do:* run `python scripts/install.py --ide Claude` (or Cursor, "VS Code", Kilo), or `/install` in chat. To get the CDD Kanban pane in Claude Code, also install the `cdd-board` plugin.
- *What you get:* every practice, action and rule appears as a slash command, skill and always-on rule. One `cdd` MCP server answers every chat, and a hook server starts it when a chat opens. Nothing has to be wired by hand, and reinstalling picks up any change to the guidance.
- *Try it:* reinstall, open a new chat, type `/` and look for the `stories-`, `ddd-` and `actions-` entries.
- *Under the hood:* `harness/installation` writes the `.claude/` / `.cursor/` files, `harness/mcp` is the one `cdd` server, and `harness/hooks` runs `sessionStart`.

**Lesson 2. Learn the map: practices, fidelities, actions, stages**
- *What you do:* open the catalog (`cdd_guidance/catalog/index.html`) or run `/guidance`.
- *What you get:* one way of thinking about all the work.
  - **Practices** are views: Stories (who does what), DDD (business concepts and their boundaries), UX (screens and navigation), Clean Engineering (modules and code), and BDD (behaviour tests).
  - **Stages** are Discovery (wide, cheap to change), Specification (one increment, executable specs) and Implementation (tests and code on the target stack).
  - **Fidelities** are one practice in one stage, for example `stories-story-map`, `ddd-model` or `ux-front-end-code`.
  - **Actions** are the verbs every practice shares.
- *Try it:* in the catalog, follow Stories from story_map to scenarios to acceptance_tests.
- *Under the hood:* `harness/catalog_generator` builds the catalog from the same guidance classes the agent reads, so the pages always show what the agent is actually given.

**Lesson 3. Generate your first artifact**
- *What you do:* run `/generate stories-story-map` and describe the product.
- *What you get:* a story map that follows the practice's template and rules, written to the practice's folder and checked as soon as it is written.
- *Try it:* `/generate stories-story-map`, then `/generate ddd-bounded-context` on the same idea.
- *Meet the chat bar:* the bar above the prompt is how you drive CDD without typing commands. From the left, it shows the server health mark, the session name, an action button, one dot per fidelity of the stage (in its practice's colour, fainter the less is done, with a red violation count beside it), the stage icons, and then handoff, files and close. Hover over or press the session name to see the session card with each fidelity's state and folder. The status line names the active session, its stage, its next guidance and its violations, and every prompt you send tells the agent which session it is working on.
- *Or from the chat bar:* press the fidelity's dot on the chat bar (the action button shows ▶ generate when generate is next) and turn on the format chips you want. Press the button, then press Enter to send the commands it puts in the prompt.
- *Under the hood:* `cdd_guidance/actions/generate`, built on `harness/guidance_actions`. Each practice is one `{practice}.md` with a section per fidelity.
- *What happens underneath:*
  1. The `cdd-board` plugin draws the bar and reads the active session from the `cdd` server through the TypeScript language adapter; its `prompt.compose` hook adds that session and its next guidance to every prompt.
  2. The chat bar asks `ticket.generate_commands` for the fidelity's commands and puts them in the prompt. If the fidelity before it uses another format, a render comes first.
  3. The agent calls `generate.generate` on the `cdd` MCP server.
  4. The server opens the session, loads that fidelity's section of `{practice}.md` with its template and rules, and returns them to the agent as instructions.
  5. The agent writes the artifact where the fidelity declares it, or where the session's `session.json` says instead.
  6. The agent then validates what it wrote.
  7. The session log records a generate line, and the dot fills in.

**Lesson 4. Document or render: describe what exists, or convert what you made**
- *What you do:*
  - `/document <practice-fidelity>` on code, specs or docs that already exist, for example `/document clean-engineering-modules` on a legacy folder.
  - `/render <format>` on an artifact CDD already generated, for example the story map to drawio, or a Clean Engineering model to python.
- *What you get:* two actions that are easy to confuse but do opposite jobs.

  | | Document | Render |
  |---|---|---|
  | **Starts from** | what already exists (code, tests, docs, a running app) | an artifact CDD already generated |
  | **Produces** | the practice's artifact, filled in with what was observed | the same content in another format (markdown, drawio, miro, python, typescript, json) |
  | **Applies the rules?** | no: it flags violations in the document but never fixes them | no: it only converts, and adds or removes nothing |
  | **Opens a session and logs?** | yes: it writes under the session's root | no: it opens no session and commits nothing |
  | **Use it to** | get an honest "as-is" baseline before changing anything | see or share the same model as a diagram, a board or code |

  Use document first on legacy work so the gap between "as is" and "should be" is visible, then generate the "should be". Use render whenever a person needs a different view of the same thing. Generate renders an earlier fidelity into a new format on its own before it builds on it.
- *Try it:* `/document stories-story-map` on an existing app's tests, then `/render drawio` on the story map and open it with `python tools/drawio_viewer/drawio_viewer.py`.
- *Or from the chat bar:* select the fidelity's dot, open ▾ on the action button and pick document or render (for render, turn on the format chip you want). Press the button, then send the prompt it fills in.
- *Under the hood:* `cdd_guidance/actions/document` and `cdd_guidance/actions/render`, with each practice's `model/{format}/` adapters. `tools/drawio_viewer` opens `.drawio` files in the real draw.io editor and saves them back.
- *What happens underneath:*
  1. **Document** takes a neutral observer's view. It reads the session's root and the practice's contexts, then fills the practice's template with only what it observes.
  2. It runs the scan, appends every violation to the document as-is, and saves the result where the session says the practice writes.
  3. **Render** reads the files you name (never pasted into the chat) and the format they are already in.
  4. The practice's `model/{format}/` adapter parses that format and writes the target one.
  5. Render then folds the result into the module it belongs to, keeping behaviour that is already there and never replacing an existing file. It refreshes the session's graph with exactly the files it wrote.

**Lesson 5. Validate: check an artifact against its rules**
- *What you do:* `/validate stories-story-map`, optionally with `rule=` to check just one rule, or `paths=` to check exactly the files you're editing.
- *What you get:* a pass/fail report against the practice's written, named rules, saved in the session so you can come back to it. For graph-backed practices it also reports problems that only show across files.
- *Try it:* validate the story map, then open the report under the session's `validation-reports/`.
- *Or from the chat bar:* select the dot, pick validate from ▾ and send the prompt. A red violation count appears beside the dot; press it to open the report in its own tab.
- *Under the hood:* `cdd_guidance/actions` (Validate, *CheckedGraph*, *ValidationReport*), plus the graph rules in `harness/graph`.
- *What happens underneath:*
  1. The agent calls `validate.validate`.
  2. A path that does not exist, or is outside the session's root, is refused, so a validate never checks nothing and reports it as clean.
  3. The server checks the files against every rule the fidelity holds, judging the prose rules with AI.
  4. For graph-backed practices, it refreshes the session's knowledge graph with just those files and runs the graph rules on the nodes they hold.
  5. *ValidationReport* saves the report, with the checked graph beside it, under `validation-reports/`, and the log records a validate line.
  6. The chat bar and board read the violation count through `fidelity-progress.report`.

**Lesson 6. Satisfy: fix until clean**
- *What you do:* `/satisfy stories-story-map`, or press Fix on a report.
- *What you get:* the agent validates, fixes every violation, and validates again until the artifact is clean, so you don't run the fix-and-recheck loop by hand.
- *Try it:* satisfy the fidelity you just validated, then compare the two reports.
- *Under the hood:* `cdd_guidance/actions/satisfy` and `Generate.generate_fixes_from_validate`.
- *What happens underneath:*
  1. Satisfy hands the agent the fidelity's rules and lists `validate` as the tool to call before and after its fixes.
  2. The agent validates, then follows the fixes step of Generate to correct each violation in place.
  3. It validates again, and repeats until the report is clean.
  4. Satisfy itself checks nothing and saves no report: each validate it calls saves its own report and log line.

**Lesson 7. Rules and notices that come to you**
- *What you do:* nothing. Just work.
- *What you get:*
  - After an action call or a file edit, the matching practice rules are added to the chat for that path.
  - A toast names the action, practice or rule being used.
  - Always-on rules (in `cdd_guidance/rules/`) apply everywhere.
- *Under the hood:* `harness/hooks` (`preToolUse`, `afterAgentResponse`), `tools/prompt_notify` (toasts), `cdd_guidance/rules/`.

### Sketch and iterate: shape the plan with a person in the loop

**Lesson 8. Shape the plan with a person in the loop**
- *What you do:*
  - `/grill` asks questions grounded in files it has read.
  - `/sketch stories ddd` drafts several practices together in short passes.
  - `/iterate` delivers the formal artifact one agreed slice at a time.
  - Use the Discoverer agent to run a whole discovery stage this way.
- *What you get:* each pass is small enough for a person to absorb, so systemic mistakes are caught while they're still cheap. Answers are kept in `grill-answers.md`.
- *Or from the chat bar:* select one or more fidelity dots, pick sketch or iterate from ▾ and send the prompt. `/grill` is typed in the chat.
- *Under the hood:* `cdd_guidance/actions/grill_context`, `sketch`, `iterate`, and `cdd_guidance/agents/discovery.md`.
- *What happens underneath:*
  1. Grill reads the context files first, then asks one framed question at a time and writes each answer to `grill-answers.md`.
  2. Sketch writes one shell file with a section per practice, at that fidelity's Scaffold level, then asks three or four questions and sketches the answers in.
  3. Iterate generates only the slice the latest answers unlocked, validates it, makes one fix pass, and asks for feedback before the next batch.
  4. Each round is marked as a Loop in the session log.

### Sessions: run your work as sessions from the chat

**Lesson 9. Sessions: each piece of work gets its own folder, worktree and branch**
- *What you do:* create a session (`ticket.create`, or `/switch-session <name>`) and activate it (`ticket.activate`). `/current-session` says which one is open.
- *Or from the chat bar:* press ▾ beside the session name, type a new name to create a session, or pick one from the list. A dialog says the current session will be committed and pushed and the new one opens on its own branch and worktree. Confirm it.
- *What you get:* one piece of work, kept in three places that always match:
  - **Folder:** `.sessions/{name}/` holds the session's record (`session.json`, the idea file, `session.log`, handoffs, decision records and validation reports). It always lives on main, so the board sees every session.
  - **Branch:** the work's own branch. Every commit carries a `Ticket:` trailer.
  - **Worktree:** a checkout of that branch beside the main folder, which stays on main.

  Any chat can pick up the work from the folder, and actions only touch the active session. Leaving or closing a session offers to hand off, commit, push and merge.
- *Under the hood:* `space/session` (*Session*, *Sessions*, *SessionLog*) and `space/repo` (*Repo*, *Branch*, *Worktree*), with the leave/open/close choices in `space/kanban` and `/push`.
- *What happens underneath:*
  1. Creating a session calls `ticket.create`, which makes `.sessions/{name}/` with its `session.json`, idea file and `session.log`.
  2. Activating it calls `ticket.activate`, which first acts on the leave choices for the session you are leaving: a handoff, a commit and push of its work branch, and a merge if you asked for one.
  3. Session folders that are not committed yet are committed on main and pushed.
  4. `branch.open_in_worktree` opens the session's own worktree on its branch.
  5. A chat working in that worktree works on the session, which it finds from the worktree's branch. A chat in the main folder keeps its open session in *WorkState* under `~/.cdd`, never in the checkout.
  6. Every later `session.*` call and log line goes to the session's folder, stamped with the chat that made it.
  7. A push first merges in origin's copy of the branch (`catch_up_with_origin`). A merge that conflicts is aborted, never left half done.

**Lesson 10. Hand off and record decisions**
- *What you do:* run the `space-session-handoff-session` skill when you stop, and `space-session-record-decisions-session` while you decide.
- *What you get:* a short handoff (what was done, what was learned, where to start next) so a fresh agent continues without rereading the chat, and numbered Context Decision Records for choices that are hard to reverse.
- *Or from the chat bar:* press the ⇥ handoff icon on the chat bar and send the prompt it fills in. Closing or leaving a session also offers Create handoff, which is on by default.
- *Under the hood:* *Handoffs* and *DecisionRecords* in `space/session`, with `HANDOFF-FORMAT.md` and `CDR-FORMAT.md` as templates.
- *What happens underneath:*
  1. The icon puts "Write a handoff for ticket <session> with /space-handoff-handoff-session" in the prompt.
  2. The agent reads `HANDOFF-FORMAT.md` through `session.read_handoff_format`, drafts the handoff to a file, and calls `session.write_handoff`.
  3. A new `handoff-{timestamp}.md` lands in the session folder, and the board shows the latest one.
  4. Decision records work the same way through `session.read_cdr_format` and `session.write_cdr`. Each is numbered one past the highest in `.context/cdr/`.

**Lesson 11. Keep CDD healthy**
- *What you do:* watch the server health mark and open its panel. From there you can reconnect the server, reinstall the tools, or update the board and CDD.
- *What you get:* when tools stop answering you see it straight away and fix it in seconds, and install probes catch a broken setup before a chat trips over it.
- *Under the hood:* `harness/diagnostics` (health report and probes), and the `server-health`, `cdd_ping` and `cdd_restart` tools.
- *What happens underneath:*
  1. The health mark reads the server health report, which checks the MCP host, the tools loaded, the Kanban app, the Graph app and the hook server.
  2. Reconnect retries `cdd` up to three times, then reads the active session again.
  3. Run install runs the installer and reports installing, installed (open a new session) or failed. Details shows the tool, the error, the server and the fix.
  4. Install probes call each published tool through the live host and write the results to `diagnostics.json`.

### Real context and deeper stages: bring in real context and take the work to code

**Lesson 12. Partition: index a source, then cut it into verbatim segments**
- *What you do:* `/partition stories-story-map paths=<handbook folder>`, then partition the same source through another practice, such as `/partition ux-ia` or `/partition clean-engineering-modules`.
- *What you get:*
  - **Index** (`.context/{subject}-index.md`): a list of what matters to that practice (epics, screens, modules), each with the entries its segment must hold. It follows the practice's view, not the source's own table of contents.
  - **Segments** (`{artifact}/.context/{artifact}-segment.md`): verbatim chunks of the source, one per indexed item, so later work cites the exact words instead of a summary.
  - **Completeness check:** a segment fails if it drops an entry the index named. It is judged by its named entries, never by its length.
  - **Several views on one source:** each practice adds its own columns and segments, and never wipes or re-chunks what an earlier one wrote.
- *Try it:* partition a long spec with `mode=index_only`, read the index, then run it again in `one_go` to write the segments.
- *Under the hood:* `cdd_guidance/actions/partition` (*Partition*, *PartitionIndex*, *Segment*) and its tools `partition.index`, `partition.segment`, `partition.segment_files` and `partition.verify_segment_completeness`.
- *What happens underneath:*
  1. You pass the source by path. The action reads it locally, and the source is never put on an MCP call.
  2. **Index:** it reads `partition_guidance.md`, filled in from the practice's Overview and the fidelity's Scaffold section, and builds the index. An existing index is added to, never replaced.
  3. **Segment:** it writes each indexed item's passages, word for word, into that item's segment file.
  4. **Verify:** `partition.verify_segment_completeness` fails any segment missing a named entry. Project-specific limits go in the index's `<!-- partition-config -->` block.
  5. `partition.segment_files` lists every segment written, so a later step, such as embedding, reads exactly those files.
  6. `mode` is `one_go` (all three steps), `pause` (stop after the index for you to check it), or `index_only`.

**Lesson 13. Capture documents into a searchable index**
- *What you do:* run the Context Setup skill `context-setup-capture-from-documents` on a folder of Word, PDF, slide, HTML or text files, naming the practices that should index it. Then ask questions with `context-setup-ask`. You can also use the Context agent to run the whole thing.
- *What you get:* one searchable index over all the documents, which answers in plain language and cites the segment each answer came from.
- *Try it:* capture a product handbook with Stories and DDD, then ask "what happens when a customer ports a number?"
- *Under the hood:* `cdd_guidance/context_setup` (`convert`, `capture_from_documents`, `embed`, `search`, `ask`) and `cdd_guidance/agents/context.md`.
- *What happens underneath:*
  1. **Convert:** each supported document is converted to `markdown/<name>.md`, with notes on its heading depth and size.
  2. **Partition:** the markdown is partitioned through each practice you chose, with the first practice going first.
  3. **Embed:** the segment files that `partition.segment_files` lists are embedded into one FAISS index (`index.faiss`), with a `meta.json` file that records where each segment came from.
  4. **Search and ask:** `search` returns the closest segments to a question, and `ask` answers from them with citations.
  5. Each step reads what the step before wrote, so no step restates where another writes.

**Lesson 14. Sandbox a live app and capture it as context**
- *What you do:* point Context Setup's `context-setup-capture-from-live-app` at the application's repository on disk, as a web, desktop or API app, and name a separate **capture repo** where the stubs and captures go. Then open your session in the capture repo and scaffold the story map and bounded contexts from what the running app shows.
- *What you get:*
  - The running app becomes the source of truth instead of memory, a vendor PDF or a guessed happy path.
  - The app runs in isolation, with only its outermost neighbours stubbed, so the seam you are proving stays real.
  - Every page is captured as a screenshot plus an accessibility tree, with one overview the practices can read.
- *Try it:* smoke-test the app first with `context-setup-smoke-test`, then run the full live-app capture.
- *Under the hood:* `cdd_guidance/context_setup` (`smoke_test`, `scout_app`, `complete_capture`, `capture_from_live_app`) and `.context/principles/context-as-code-strategy.md`, step 1 "Set up the sandbox".
- *What happens underneath:*
  1. **Isolate:** classify the app's external systems and write the minimum stubs (canned responses from its neighbours) at the outermost boundary only, never on the seam being proven. Global stubs go in `tests/stubs/{system}/`. A domain's own stubs go in `domain/{aggregate}/stubs/{system}/`, taken from that aggregate's source rather than invented in a test.
  2. **Smoke test:** probe the app's primary screens and pass only when each returns HTTP 2xx or 3xx. The results go to `tests/stubs/stub-inventory.md`.
  3. **Scout:** capture 10 to 20 representative pages, each with a `screenshot.png` and an `aria.yaml`, under `sandbox/extracted-context/app-extraction/pages/<slug>/`, and write `extraction-overview.md`.
  4. **Complete capture:** run only when the scout has failed or warning pages. It re-captures just those pages and updates the overview.
  5. The overview can then be embedded like any other context and used to scaffold the first story map and bounded contexts, still at Discovery.

**Lesson 15. Bring meeting notes in as context**
- *What you do:* run `granola.organize` to file loose Granola notes into folders, and `granola.context` to bring chosen notes into `.context/granola/`.
- *What you get:* decisions and facts from meetings become citable context files, one file per note. Nothing is moved until you confirm.
- *Under the hood:* `tools/granola`.

**Lesson 16. Go deeper: from story map to tests to code**
- *What you do:* move the ticket through Specification and Implementation.
  - Generate `stories-scenarios`, `ddd-model`, `ux-mockup` and `clean-engineering-model`.
  - Then generate `stories-acceptance-tests`, `bdd-development` and `clean-engineering-code`.
  - Use the Specification and Implementation agents to run each stage.
- *What you get:* scenarios become executable specs, then passing tests that drive real code. The same domain words run from the outcome all the way down to the code.
- *Or from the chat bar:* when every fidelity of the stage has passed validate, the action button shows ➜. Press it to move the session to the next stage, then work the new stage's dots the same way.
- *Under the hood:* the practices in `cdd_guidance/practices/`, with `cdd_guidance/agents/specification.md` and `implementation.md`.
- *What happens underneath:*
  1. ➜ calls `ticket.move_next`, which records the new stage in `session.json` and the log.
  2. The chat bar shows the new stage's fidelities on its dots.
  3. Generate builds each fidelity from the one before it, rendering into the new format first when the formats differ.
  4. Acceptance tests come before the code they drive, and the graph links steps and observations to the operations they call.

**Lesson 17. Hand hard problems to a background agent**
- *What you do:* `/diagnose` (optionally with a practice) for a stubborn bug, or `sub-agent` for any recipe.
- *What you get:* a disciplined hunt runs in the background (reproduce, minimise, form hypotheses, fix, add a regression test) while you keep working.
- *Under the hood:* `cdd_guidance/actions/diagnose` and `tools/sub_agent`.

### The CDD Kanban and the visual apps

**Lesson 18. See and move work on the CDD Kanban**
- *What you do:* open the board and find every session as a ticket in Backlog, Discovery, Specification, Implementation or Complete.
  - Add a backlog item and start it as a ticket.
  - Move tickets forward or back.
  - Set a WIP limit per stage, split a ticket into children, and archive it when it's finished.
- *What you get:* AI work is visible and limited like any agile team's work. A ticket's place comes from its log (Generate and Validate per fidelity), so a move made by the agent and one made by a person give the same answer.
- *Under the hood:* `space/kanban` (*Board*, *Ticket*, *Stage*, *BacklogItem*, *FidelityProgress*) and the CDD Kanban app in `app/src/kanban`.
- *What happens underneath:*
  1. Typing `/board` in the chat starts the board app if it isn't running, then opens it.
  2. The app calls `board.show`.
  3. The server reads every ticket, backlog item and worktree from `.sessions/` and git, once per board build.
  4. Each ticket's column and progress are worked out from its session log. They are never stored.
  5. A move calls `ticket.move_next`, `move_previous` or `move_to`, which writes `stage` and `stage_mark` into `session.json` and adds a line to the log.
  6. WIP limits and the order of cards are kept in `.sessions/_board.json`.

**Lesson 19. Work a ticket's fidelities from the board**
- *What you do:* choose the ticket's practices and read each fidelity tile's progress dots.
  - Send the next action, or one action to every practice in the stage, with format chips.
  - Open the violations band and its report, and fix the violations.
  - Browse the ticket's files.
- *What you get:* the next step is always one click away. The board sends the exact command to the chat working on the ticket.
- *Under the hood:* `fidelity-progress.*`, `ticket.violations`, `file-manager.*`, and `harness/chat`, which reaches a live chat and follows the command until it finishes.
- *What happens underneath:*
  1. Each tile reads its *FidelityProgress* (whether Generate and Validate are done, from the session log) and its `commands`.
  2. Pressing an action sends that command through `harness/chat` to the connected chat working on the ticket, whose cdd-board plugin checks in every second.
  3. The board follows the command until the chat has shown it and finished.
  4. The violations band reads `ticket.violations`, and the files list reads `fidelity-progress.files` and `file-manager.*`.

**Lesson 20. Author story maps in the Story UI editor**
- *What you do:* open a map by its address and switch between map view and increment view.
  - Add, rename, drag and reorder epics, sub-epics and stories.
  - Plan increments by dragging stories into them.
  - Write scenarios, steps and example tables.
- *What you get:* product people shape scope visually. Each edit is saved as you go, edits that break map rules are refused, and the result is the same story files the agents read.
- *Under the hood:* the Story UI app and the story model in `cdd_guidance/practices/stories/model`.

**Lesson 21. Prototype on the design canvas and play stories through it**
- *What you do:*
  - Lay out pages and artboards and write the canvas into a project folder.
  - Load a scenario's fixture data into a screen and follow screen links to the next story.
  - Play or drive a mockup through its story in the story demo.
  - Start, publish and release canvas versions.
- *What you get:* stakeholders click through screens driven by real scenarios, and every published version is kept with its link. Regenerating the canvas never overwrites what people edited.
- *Under the hood:* `harness/design_canvas` (*DesignCanvas*, *FixtureScreen*) and `cdd_guidance/practices/ux/story-demo`.

**Lesson 22. See everything in the knowledge graph**
- *What you do:*
  - Load the working copy into one graph of every practice's nodes and the links between them.
  - Apply pattern overlays.
  - In the Graph app, expand practice trees, follow relationships, open a node's source, and filter by practice, node type, connector or violations only.
  - Hover over a broken rule, jump to the line, and copy a correction prompt.
- *What you get:* you can click through from outcome to story to class to code, and cross-practice problems show on the exact node and line. Graph rules also report inside `/validate`, and the graph is refreshed after each action that writes files.
- *Under the hood:* `harness/graph` (`graph.load_working_copy`, `return_nodes`, `explorer_trees`, `save_json`), with each practice's `PracticeReading`.

**Lesson 23. Publish the catalog and your project's approach**
- *What you do:* run `catalog.generate_catalog`, `catalog.generate_project_approach` and `catalog.apply_brand`.
- *What you get:* a self-contained, brandable website of every practice, fidelity, rule and action, plus a one-page approach built from your own project's example artifacts, to share with a team or a client.
- *Under the hood:* `harness/catalog_generator`.

### Improve and extend CDD

**Lesson 24. Make the guidance learn from mistakes**
- *What you do:*
  - `/repair` traces a violation back to the guidance that let it happen and fixes that guidance.
  - Improve guidance from a mistake, and add a rule from a failed example.
  - `/verify_fix` re-runs the regression check.
- *What you get:* each error makes every later run better. You compound learning instead of fixing the same thing again.
- *Under the hood:* `cdd_guidance/actions/improvement`, `Validate.create_rule`, and each practice's `rules/rule_examples.py`.

**Lesson 25. Add your stack: pattern overlays**
- *What you do:* apply a pattern such as LERN or MERN domain-driven, CDD web domain access, or a Claude Code mod on top of the practices.
- *What you get:* stack-specific guidance and graph rules (acceptance tests first, then the code they drive) without changing a practice.
- *Under the hood:* `cdd_guidance/patterns` (*DomainDrivenStack*, *LernDomainDriven*, *MernDomainDriven*, *CddWebDomainAccess*, *CddClaudeMod*).

**Lesson 26. Build your own toolsets and practices**
- *What you do:*
  - Use the builders `builders-create-agent-toolset` and `builders-create-practice-guidance`.
  - Annotate a plain class with `@agent_toolset`, `@agent_tool`, `@agent_instructions`, `@skill`, `@mcp`, `@hook` or `@Toast`.
  - Reinstall.
- *What you get:* a team turns its own practices, tools and quality bar into commands, skills, MCP tools and hooks that work with every existing action on the first try.
- *Under the hood:* `cdd_guidance/builders`, `harness/annotations`, `harness/agent_tools`, and `harness/guidance` (*PracticeGuidance*, *PracticeCatalogue*).

**Lesson 27. Test agents and audit what they see**
- *What you do:*
  - Write agent BDD specs that drive a real agent and judge its output with an AI rubric.
  - Turn on the prompt log to record every prompt, file read and tool call.
  - Use `echo` to read exactly what an action would instruct.
- *What you get:* agent behaviour is tested like code, and you can see afterwards exactly what the model was given.
- *Under the hood:* `cdd_guidance/practices/agent_bdd`, `tools/prompt_log` (off by default), `tools/echo`.
