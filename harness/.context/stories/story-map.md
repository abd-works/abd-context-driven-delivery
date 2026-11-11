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

**Sources / context:** `harness/.context/module-context.md`; `harness/agent_tools/.context/module-context.md`; `harness/agent_tools/.context/agent-tools-model.md`; `harness/markdown/.context/module-context.md`; `installation/.context/installer-deployed-model.md`; `harness/hooks/.context/module-context.md`; `harness/guidance/guidance.py`; `harness/.context/context-tool-resource-model-om-bdd.md`; `harness/mcp/.context/module-context.md`; `actions/.context/module-context.md`; `practices/.context/module-context.md`; user spine: register agent toolsets → install markdown files (skill, slash command, rules) and MCP → invoke those → use context guidance (install skills and .mdc, invoke instructions, generate under rules) → use practice guidance (register guidance and fidelities, invoke practice and fidelity, shared and fidelity rules constrain output) → hook dispatch → extract markdown → lifecycle actions. CDD Kanban and Chat Bar: `space/kanban/.context/story-map.md` and `story-map.drawio`; `harness/chat-ui/.context/story-map.md` and `story-map.drawio`; the ticket enhancements on the session-board branch (`.sessions/session-board/ticket-enhancements.md`, removed with that session in commit 8483f7a40 and read from commit b08bfe47e; its `space/kanban/.context/story-map.md`); `harness/chat-ui/.context/cdr/0001-stage-strip-band.md`; `space/kanban/app/src/session-board/board-update.ts`; the ticket drawing `harness/.context/ux/ticket-ui.drawio` (2026-11-11), which supplements the design canvas for parent and child tickets; `harness/chat-ui/pane/hooks/register.ts`. The map also takes in the backlog items `.sessions/_backlog/maintain-tickets-on-board.md`, `.sessions/_backlog/guard-work-and-recover-fast.md` and `.sessions/_backlog/guard-work-and-recover-fast.md` as Intended stories.

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
### (S) Installer --> Store Install State

## (E) Install MCP And Hook Manifests

### (S) Mcp Installation --> Record Mcp Operation
### (S) Mcp Installation --> Publish Mcp Manifest
### (S) Author --> Register Hook Event
### (S) Hook Installation --> Publish Hooks Manifest

# (E) Deliver Work With Context Guidance

A practice is a lens on the work (Stories, DDD, UX, Clean Engineering, BDD), a fidelity is how deep that lens goes, and an action is what you do with it. A person composes the three into one command; the agent loads that practice's guidance at that fidelity and uses it to turn source material into context, shape the solution, produce the formal artifacts, and check them against the same rules. Sources: `catalog/workflow.md`, `cdd_guidance/actions/.context/module-context.md`, `.context/cdd-approach.md`.

## (E) Invoke Guidance Through Slash Commands

### (S) Person --> Compose Practice Action Fidelity Command

Observed: `/{practice} /{action} /{fidelity}`, such as `/stories /sketch /discovery`, or the fidelity's own skill such as `/practices-stories-stories-story-map` (`catalog/workflow.md` "How to use them").

### (S) Agent --> Load Practice Fidelity Instructions

Observed: the skill or MCP tool returns the practice's overview and guidance, its shared rules, the fidelity's rules, template and examples, all read from the markdown kept beside the practice's class, so a practice is one class plus the words the agent follows (`harness/.context/module-context.md`; `harness/markdown`).

### (S) Agent --> Call CDD Tool Through MCP

Observed: a skill or slash command that says "Use MCP tool" runs that operation on the cdd server, and a failed call stops the work and says what failed rather than falling back to a shell (`.claude/rules/mcp-fail-loud.md`).

### (S) Agent --> Guide Output With Matching Rules

Observed: installed rule files steer what the agent writes while it writes: always-apply rules such as `coding.md` on every turn, a practice's shared rules and a fidelity's rules whenever the agent touches a file their `paths` match, such as `stories-story-map.md` for `*story-map*` (`harness/installation/files.py`). Validate later checks the output against the same rules.

## (E) Turn Source Material Into Context

### (S) Agent --> Index Source Into Lens Segments

Observed: `/partition` splits handbooks, specs or code into an index plus verbatim segments for one practice's lens, and fails a chunk that drops a named entry the index requires (`actions/partition`).

### (S) Agent --> Add Lens To Existing Index

Observed: partitioning the same source through another practice adds that lens's columns and segments to the existing index; nothing already there is wiped (`catalog/workflow.md` Scenario 1).

### (S) Agent --> Describe Existing Artifacts

Observed: `/document` records what code, tests or docs already do for the listed guidance, flagging violations without correcting them, so context for an existing system is not an invented design (`actions/document`).

### (S) Agent --> Capture Documents Into Searchable Context

Observed: `context-setup.capture_from_documents` converts a folder of documents to markdown, partitions them through the chosen practices, and embeds the segments into one index that `context-index.ask` answers from with citations.

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

### (S) Agent --> Generate Fidelity Artifact

Observed: `/generate` writes each listed guidance's artifact at its fidelity, such as a story map, a class model or acceptance tests, into the session workpath's `.context/` or code folder, then validates what it wrote (`actions/generate`).

### (S) Agent --> Render Artifact Into Another Format

Observed: `/render` turns an artifact already generated into another format on the same guidance, such as a markdown story map into drawio (`actions/render`).

### (S) Agent --> Generate From Previous Fidelity

Observed: generating a fidelity reads the artifact of the fidelity before it, such as scenarios from the story map, and when the two use different formats the earlier one is rendered into the new format first (`Ticket.generate_commands`; `catalog/workflow.md` Scenario 1).

### (S) Agent --> Generate Several Practices In One Command

Observed: one action with several guidance names produces every practice's artifact at the same depth, such as Stories, Clean Engineering, UX and DDD at specification (`catalog/workflow.md` Scenario 3).

## (E) Check Artifacts Against Rules

### (S) Agent --> Validate Artifact Against Rules

Observed: `/validate` runs the practice's graph rules over the files and judges every rule Pass or Fail without editing, then saves the report, which the board and chat bar read (`actions/validate`).

### (S) Agent --> Satisfy Violations Until Clean

Observed: `/satisfy` validates, fixes every reported violation in the artifact, and validates again until it passes (`actions/satisfy`).

### (S) Agent --> Repair Guidance Behind Violation

Observed: `/repair` fixes why the practice produced the violation, in its context, example, template or scanner, rather than the artifact alone, and waits for approval (`actions/improvement`).

### (S) Agent --> Improve Guidance From Mistake

Observed: `/improve` logs the mistake and the correction, runs repair, and captures a regression example so the same failure does not come back (`catalog/workflow.md` Scenario 4).

### (S) Agent --> Add Rule From Failed Example

Observed: validate adds a named rule from an example that failed, so the next validation catches the same mistake (`actions/validate` purpose).

### (S) Person --> Review Fidelity Output

Observed: `/review` records that a person reviewed and approved each listed guidance at its fidelity, which completes that fidelity on the board and chat bar (`actions/review`).

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

### (S) Board App --> Display Board Server Health

Observed: a band across the page says the cdd server is not connected and how to reconnect. Requested (2026-11-06, as the Chat Bar does): a mark with ✓ connected, ⟳ reconnecting, ✕ disconnected or ! tools missing.

### (S) Person --> Open Board Server Health Panel

Requested (2026-11-06, as the Chat Bar does): a panel listing MCP host, Tools, Kanban app, Graph app and Hook server, or what is wrong.

### (S) Person --> Reconnect CDD Server From Board

Requested (2026-11-06, as the Chat Bar does): the board retries `cdd` and reads the board again. Built today (checked 2026-11-10): the board reads itself again every 2 s while cdd is down (`board-page-view.tsx:22`) and the board server opens a new session on the next call after a restart (`cdd-connection.ts:125`). Missing: a Reconnect button.

### (S) Person --> Reinstall CDD Tools From Board

Requested (2026-11-06, as the Chat Bar does): the board runs the installer and says installing, installed or failed.

### (S) Person --> Update Board And CDD

Observed: Update in the header (`board-update.ts` `BoardUpdate.update`, `/api/update`) gets the latest commit, rebuilds the board, installs with the cdd server pinned to that commit, then restarts the board and refreshes the page; a failed step says which step and why (`UpdateStepFailed`).

### (S) Person --> Reload Everything With One Button

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "restart refresh -> one button reloads plugins mcp everything"): Update also reloads the Claude Code plugins and the cdd server, so one press brings every part to the new code. Built today (checked 2026-11-10): Update pulls the code, pins and restarts the cdd server, reinstalls the cdd-board plugin, rebuilds the page and restarts the board server (`board-update.ts:59-62`). Missing: reloading the plugins in open chats, and reinstalling skills, rules and commands.

## (E) See Work On Session Board

### (S) Person --> [Open Board](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-open-board)

Observed: `board-page.ts` `start()` reads the board when the page opens.

### (S) Board App --> [Display Board](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-board)

Observed: Backlog, Discovery, Specification, Implementation and Complete, with In progress and Done inside each stage; the board refreshes after each cdd tool call, and a toast announces a ticket's move or review.

### (S) Person --> [Arrange Board And Details](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-arrange-board-and-details)

Observed: a drag on the split bar resizes the board and details; either can take the whole page.

### (S) Board App --> [Display Backlog Items As Tickets](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-backlog-items-as-tickets)

Observed: the Backlog column shows the title of each file in `.sessions/_backlog/`.

### (S) Board App --> [Display Ticket Card](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-ticket-card)

Observed: `ticket-card-view.tsx` draws the title, age and one block per enabled practice; the active ticket has a thick orange outline.

### (S) Board App --> [Display Ticket Details](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-display-ticket-details)

Observed: a press on a card shows its practices, fidelity progress and latest validation reports below the board; with none pressed, the details show the active ticket.

### (S) Person --> [Set Stage WIP Limit](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-set-stage-wip-limit)

Observed: `Board.set_wip_limit`, saved in `.sessions/_board.json`.

### (S) Person --> [Arrange Side Panel](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-arrange-side-panel)

Observed: the report, files and help panels resize, expand one at a time and close.

### (S) Person --> [Expand Ticket From Empty Area](move-work-forward-on-session-board/see-work-on-session-board/see_work_on_session_board_story.test.md#story-expand-ticket-from-empty-area)

Intended (`.sessions/_backlog/maintain-tickets-on-board.md` "click any empty area to expand ticket"): a press anywhere on a card that is not a control expands it. Built today (checked 2026-11-11): a press on a card chooses it and shows its details (`ticket-card-view.tsx:198`); only the expand mark opens the card's actions (`ticket-card-view.tsx:57`). Missing: expanding from an empty area.

## (E) Steer Ticket Sessions

### (S) Person --> [Open Ticket Session](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-open-ticket-session)

Observed: `Ticket.new` calls `Session.new`; a person can choose the folder the ticket's work goes in, for the whole ticket or one practice.

### (S) Person --> [Activate Ticket](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-activate-ticket)

Observed: Activate opens a dialog with what to do on leaving (commit, push, merge into main) and on opening (branch and worktree), then calls `board.activate`.

### (S) Person --> [Close Active Session](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-close-active-session)

Observed: Close asks what to do with the work, then `Ticket.close` moves the folder to `.sessions/_complete/`, so the ticket shows in Complete.

### (S) Person --> [Move Ticket](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-move-ticket)

Observed: the arrows or a drag move a ticket one column on (`Ticket.move_next`) or back (`Ticket.move_previous`); out of Implementation it closes into Complete, and back out of Discovery it goes to the Backlog with its work.

### (S) Person --> [Write Ticket Handoff](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-write-ticket-handoff)

Observed: Handoff fills the prompt with `/space-handoff-handoff-session`.

### (S) Board App --> [Display Latest Handoff](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-display-latest-handoff)

Observed: `Ticket.latest_handoff`.

### (S) Person --> [Restrict Actions To Active Session](move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md#story-restrict-actions-to-active-session)

Observed: with Active session only on, a ticket that is not the active session disables what sends commands to a chat; moving, activating and information stay open.

### (S) Board App --> Open Ticket Chat On Session Open

Observed (checked 2026-11-10): a press on a card points the board at the ticket's own chat (`ticket-client.tsx:184-188`), and the card's chat button opens the worktree, making it first if needed, then a new Claude chat on it through `/api/claude/open` and `ClaudeLink` (`ticket-client.tsx:196-205`, `chat-client.tsx:72-80`, `claude-link.ts`). It opens a new chat rather than the one the ticket ran in, and Activate opens none. Was: Intended (`.sessions/_backlog/suggest-the-next-step.md` "open associated chat on session open / manually"): opening a ticket's session opens the Claude Code chat it ran in. Observed today: a press on a ticket switches to its chat by hand (`/api/claude/open`, `ClaudeLink`).

### (S) Person --> Choose Where A Backlog Item Works

Observed (checked 2026-11-10): starting a backlog item opens Where <item> works, a folder browser that starts at the whole repository with Up and one button per folder; Use <folder> starts the item's session with that folder as its workpath (`root-choice-client.ts` `start`, `root-choice-view.tsx`).

## (E) Maintain Tickets

### (S) Person --> [Add Backlog Item](move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-add-backlog-item)

Observed: the + on the Backlog heading writes a title and text to one markdown file in `.sessions/_backlog/`; the → on a backlog card starts it as a ticket in Discovery (`BacklogItem.start`).

### (S) Person --> [Edit Ticket Text](move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-edit-ticket-text)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio` "edit text in markdown file"): a double click on a card's text edits it; a session ticket's text is a markdown file in its session folder that the session's instructions refer to, so the board and the agent read the same text; the agent's half, naming the file in the system prompt, is a scenario of Add Active Ticket To System Prompt. Built today (checked 2026-11-11): starting a backlog item moves its markdown file, text and all, into the ticket's session folder (`BacklogItem.start`, `backlog_item.py:121-128`), and a backlog card shows the file's text (`backlog-item-view.tsx:62`). Missing: a ticket's card does not show its file's text, no card edits text, and the agent's context (`Ticket.agent_context`, `ticket.py:217-226`) does not name the file.

### (S) Person --> [Reorder Tickets In Column](move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-reorder-tickets-in-column)

Intended (`.sessions/session-board/ticket-enhancements.md`): a ticket dragged up or down within its column keeps that place. Built today (checked 2026-11-11): a drag moves a ticket between columns only; the Backlog lists its items by file name (`board.py:328`) and no column keeps a place a person chose.

### (S) Person --> [Archive Ticket](move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-archive-ticket)

Observed as the `ticket.archive` tool (`Ticket.archive`). Intended (`.sessions/session-board/ticket-enhancements.md`): Archive on a card.

### (S) Person --> [Delete Ticket](move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-delete-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`): Delete on a card removes the ticket and its session folder. Built today (checked 2026-11-11): no delete operation on `Ticket` or `BacklogItem` (`ticket.py`, `backlog_item.py`); Archive is the nearest (`Ticket.archive`, `ticket.py:352`).

### (S) Person --> [Tag Ticket Session](move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md#story-tag-ticket-session)

Intended (`.sessions/_backlog/maintain-tickets-on-board.md` "tagging sessions"): a person adds tags to a ticket's session, and the card shows them. Built today (checked 2026-11-11): none; `session.json` holds no tags (`sessions.py:276`).

## (E) Organize Ticket Hierarchy

### (S) Person --> [Split Ticket Into Child Tickets](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-split-ticket-into-child-tickets)

Observed: `Ticket.new` records the parent; Split fills the prompt through `fillSplit`. Intended (`.sessions/session-board/ticket-enhancements.md`): the AI slices the ticket thinly into the child tickets it proposes.

### (S) Person --> [Add Child Ticket](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-add-child-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio` "add and remove a child"): a person adds a child ticket to a parent by hand. Built today (checked 2026-11-10): `ticket.create(parent=…)` records the parent (`ticket.py:94`, `sessions.py:268-275`) and Split asks the chat for one child per story. Missing: adding a single child by hand on the board.

### (S) Board App --> [Display Child Tickets In Parent](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-display-child-tickets-in-parent)

Intended (`.sessions/session-board/ticket-enhancements.md`): a parent's card holds its child tickets stacked inside it, with the parent's title small above them. The drawing (`harness/.context/ux/ticket-ui.drawio`) adds: the parent's card counts its children, and a child pulled out of it keeps a dashed row there. Built today (checked 2026-11-11): a child's card names its scope and parent, such as "story of epic" (`ticket-client.tsx:97-98`), and sits in its column like any other ticket.

### (S) Person --> [Expand Parent Ticket](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-expand-parent-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio`): a parent collapses to its own card and expands to show its children; collapsed it reads + N children, expanded - N children above the child rows.

### (S) Person --> [Detach Child Ticket](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-detach-child-ticket)

Intended (`.sessions/session-board/ticket-enhancements.md`; `harness/.context/ux/ticket-ui.drawio` "pull out of parent; and then drag and then move like regular ticket; remembers parent"): a child pulled out of its parent becomes a ticket of its own beside it, named parent.Child, that a person drags and moves like any ticket; it still has its parent. A person pulls a child out by dragging it out of its parent (the person, 2026-11-11).

### (S) Person --> [Reassign Ticket Parent](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-reassign-ticket-parent)

Intended (`.sessions/session-board/ticket-enhancements.md` "Add a ticket as a child of a different parent" and "Make a child independent of its parent"; `harness/.context/ux/ticket-ui.drawio` "add and remove a child"): a ticket made the child of a different parent leaves its old parent, and a child taken off its parent becomes a ticket with no parent. A person drags a ticket onto another to make it that ticket's child, and Alt-drags a child out of its parent to leave it with none (the person, 2026-11-11). Both change which parent the ticket has, so they are one story. Was: Move Child Ticket To Another Parent.

### (S) Board App --> [Place Parent At Leftmost Child Stage](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-place-parent-at-leftmost-child-stage)

Intended (`harness/.context/ux/ticket-ui.drawio` "parents cant be dragged; they change stage by taking on the stage of the leftmost ticket"): a parent sits in the stage of its child furthest back on the board and moves only as its children move; a person cannot drag a parent.

### (S) Claude Code --> [Nest Child Branch And Session](move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md#story-nest-child-branch-and-session)

Intended (`.sessions/session-board/ticket-enhancements.md`): a child ticket's branch and session nest under its parent's, so the hierarchy holds in git and in `.sessions/` as on the board. Set aside in the Maybe Later increment (the person, 2026-11-11: complicated, not now).

## (E) Guide Work Through Practices On Board

### (S) Board App --> [Display Fidelity Progress](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-display-fidelity-progress)

Observed: each fidelity on a tile shows Generate, Validate and Review as ○ to do, … in progress or ✓ done.

### (S) Person --> [Open Practice Tile](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-open-practice-tile)

Observed: a tile opens after a short hover, closes on leaving, and a press keeps it open.

### (S) Person --> [Choose Ticket Practices](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-choose-ticket-practices)

Observed: `Ticket.enable_practice` saves the choice to the ticket's `session.json`.

### (S) Person --> [Send Next Fidelity Action](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-send-next-fidelity-action)

Observed: Run next names the step that runs next and steps through generate, validate and review for each practice in order (`Ticket.next_fidelity`, `Ticket.next_action`), holding on fix violations until they are fixed.

### (S) Person --> [Send Action To Stage Practices](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-send-action-to-stage-practices)

Observed: the stage head sends one action for every enabled practice in a stage.

### (S) Person --> [Mark Ticket Done In Stage](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-mark-ticket-done-in-stage)

Observed: the arrow takes an In progress ticket to Done without crossing a column, written as a `done <stage>` session log line, and back as `in-progress <stage>`.

### (S) Person --> [Open Help](move-work-forward-on-session-board/guide-work-through-practices-on-board/guide_work_through_practices_on_board_story.test.md#story-open-help)

Observed: `Board.help`; the ? on a tile or practice name opens the overview, guidance and rules in a side panel, with a link to the Forge page.

### (S) Person --> Choose Session And Practice Roots

Observed (checked 2026-11-10): Roots of <ticket> lists the session's root and each practice's root, marked default until a person chooses another; Change browses the folders and Use sets the session's workpath (`chooseWorkpath`) or that practice's root (`root-choice-client.ts`, `root-choice-view.tsx`).

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

#### (S) Board App --> Run Work Type Flows

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

Intended (`.sessions/_backlog/show-board-quickly.md` cause 1): `TicketCheckout._found_branch` → `Branch.exists` → `Repo.has_ref` runs one `git show-ref` per check, about 70 ms each and about 7 per `board.show` (`space/kanban/ticket_checkout.py`, `space/repo/repo.py`); one board build checks each branch once.

### (S:technical) Board App --> Cache Practice Guidance By File And Change Time

Intended (`.sessions/_backlog/show-board-quickly.md` cause 2): practice guidance markdown is read and parsed again for every session (`harness/guidance/guidance.py`, `harness/markdown/markdown.py`); it is cached by file and modification time.

### (S:technical) Board App --> Read Session File Once Per Board Build

Intended (`.sessions/_backlog/show-board-quickly.md` cause 3): `session.json` is read thousands of times over a few `board.show` calls (`harness/installation/json_file.py`); one board build reads each session file once.

## (E) Work Fidelity Outputs On Board

### (E) Generate Fidelity Outputs On Board

#### (S) Person --> [Choose Action And Formats](move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-choose-action-and-formats)

Observed: the tile's action bar lists the actions and format chips, with the default format picked unless that output exists.

#### (S) Claude Code --> [Resolve Fidelity Output Paths](move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-resolve-fidelity-output-paths)

Observed: `Generate` and `Session.fidelity_outputs` take the outputs a fidelity declares, with the `session.json` overrides.

#### (S) Person --> [Generate Fidelity Output](move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-generate-fidelity-output)

Observed: Run sends `/actions-generate <fidelities> format=<formats>`, rendering the earlier fidelity into a new format first (`Ticket.generate_commands`); a generate line in the session log counts as Generate done.

#### (S) Person --> [Render Fidelity Format](move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-render-fidelity-format)

Observed: Render sends `/actions-render`.

#### (S) Person --> [Send Tile Action To Chat](move-work-forward-on-session-board/work-fidelity-outputs-on-board/generate-fidelity-outputs-on-board/generate_fidelity_outputs_on_board_story.test.md#story-send-tile-action-to-chat)

Observed: Run sends `/actions-sketch`, `/actions-iterate` or `/actions-document` to the chosen chat.

#### (S) Person --> Add Comment To Sent Command

Intended (`.sessions/_backlog/enter-commands-faster.md` "add comment to command sent to chat"): a person adds their own words to the command the board sends to the chat. Built today (checked 2026-11-10): Split, Handoff, + Ticket and Run next put the command into the prompt for the person to edit before sending (`chat-client.tsx:144-148`). Missing: tile Run, Validate and Fix send at once, and there is no comment field.

#### (S) Person --> Choose Testing Strategy

Intended (`.sessions/_backlog/customize-board-workflow.md` "support for multi language / bespoke testing layers eg a testing strategy; generate; validate"): a person chooses the test layers and languages a ticket's tests use, and generate and validate follow that choice.

#### (S) Person --> Toggle Sub Agents

Intended (`.sessions/_backlog/customize-board-workflow.md` "use sub agents toggle"): a person turns on running a board action in sub-agents.

### (E) Validate Fidelity Outputs On Board

#### (S) Person --> [Validate Fidelity](move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-validate-fidelity)

Observed: Validate sends `/actions-validate`; a validate line counts as done only when it names no graph-rule violations.

#### (S) Claude Code --> [Save Validation Report](move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-save-validation-report)

Observed: `Validate` saves `.sessions/<session>/validation-reports/<practice>-<fidelity>-<date>.md` and the graph it checked beside it in `.json`.

#### (S) Person --> [Open Validation Report](move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-open-validation-report)

Observed: `fidelity-progress.report` opens the latest report in a side panel.

#### (S) Person --> [Fix Report Violations](move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-fix-report-violations)

Observed: Fix sends the chat the rule, the error at its file and line, and the content that failed; Fix all sends every violation of the rule in one message.

#### (S) Board App --> [Display Violations Band](move-work-forward-on-session-board/work-fidelity-outputs-on-board/validate-fidelity-outputs-on-board/validate_fidelity_outputs_on_board_story.test.md#story-display-violations-band)

Observed: the band shows the active ticket's violations, only when it has some, and sends them to satisfy.

#### (S) Board App --> Display Report Without Header Noise

Observed (checked 2026-11-10; commits 93eb442e7, e502c9963): the raw report text shows only when the report has no saved graph and no rules could be read from it; otherwise the panel opens on the rules (`report-panel-view.tsx:48-61`). Was: Intended (`.sessions/_backlog/review-work-in-board-files.md` "kill weird MD area at top of violation report"): the report panel opens on the findings, without the markdown block that sits above them today.

#### (S) Board App --> Display Report Errors In Code Fences

Observed (checked 2026-11-10): each violation that names a file and line shows a block of source lines headed by its location, with the failing line marked (`report-rule-view.tsx:10-43`, `harness/graph/violation.py:128-164`); a violation with no file and line shows only its message. Was: Intended (`.sessions/_backlog/review-work-in-board-files.md` "violation report not showing code fences for errors"): each error's content shows in a code fence.

### (E) Review Fidelity Outputs On Board

#### (S) Person --> [List Ticket Files](move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-list-ticket-files)

Observed: `fidelity-progress.files` lists the tile's or ticket's fidelities' files; on a ticket working in the whole repository, only what its branch changed.

#### (S) Person --> [Browse Ticket Folder](move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-browse-ticket-folder)

Observed: the folder mode of the files panel groups the files under their folders.

#### (S) Person --> [View Fidelity Files](move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-view-fidelity-files)

Observed: one tab per format the fidelity offers, generated or not; × closes one.

#### (S) Person --> [Review Fidelity](move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md#story-review-fidelity)

Observed: Reviewed is off until a clean validate; when every fidelity of a stage is reviewed, the ticket shows in that stage's Done.

#### (S) Person --> List Ticket Context Files

Intended (`.sessions/_backlog/review-work-in-board-files.md` "include ticket context file and folders with list - folder-files; separate section"): the files panel lists the ticket's own context file and folders in a section of their own.

#### (S) Person --> Open Session Files From Details

Intended (`.sessions/_backlog/review-work-in-board-files.md` "session information -> link to file or folders"): each file or folder the session information names opens from where it is named. Built today (checked 2026-11-10): the details open the session folder, the stage's files and the latest handoff (`details-view.tsx:37-55`). Missing: the workpath link opens the root chooser rather than the folder.

#### (S) Person --> View Files In Rich Viewer

Intended (`.sessions/_backlog/review-work-in-board-files.md` "integrate with monaco viewer OR native file rendering"): files open in an editor-grade viewer, or rendered as the file type.

#### (S) Person --> Comment On File Selection

Intended (`.sessions/_backlog/review-work-in-board-files.md` "select some text in file view and add comment that gets sent to chat like in design view"): a person selects text in a file and sends a comment on it to the chat.

#### (S) Board App --> Show AI Changes As Diff

Intended (`.sessions/_backlog/review-work-in-board-files.md` "change viewer from ai change like vscode / cursor"): the viewer marks what the agent changed in a file, as VS Code and Cursor do.

### (E) Integrate Practice Content Editor Apps On Board

#### (S) Person --> Open Story UI On Ticket Scope

Requested (2026-11-06, "board --> story ui for ticket's scope"): the board opens the Story UI editor on the part of the story map the ticket covers, from its session folder. Also Intended (`.sessions/_backlog/integrate-practice-content-editor-apps.md` "view story map / ux design canvas for a session").

#### (S) Person --> Filter Knowledge Graph To Ticket Scope

Requested (2026-11-06, "filter to scope of ticket"): opening the Graph app from the board or the chat bar loads only the ticket's session folders. Also Intended (`.sessions/_backlog/integrate-practice-content-editor-apps.md` "view knowledge graph from here").

#### (S) Person --> Filter Knowledge Graph To Ticket Practices

Requested (2026-11-06, "practices loaded for ticket / board"): the Graph app opens with its practice filter set to the practices the ticket has turned on, or every practice on the board when opened from the board header.

#### (S) Agent --> Deploy Knowledge Graph App With Board State

Requested (2026-11-06, non-functional): the Graph app runs on the same app server and instance as the board's state, so the graph and the board share one state for the active ticket.

#### (S) Agent --> Refactor Knowledge Graph App To Web Domain Access

Observed (checked 2026-11-10; commit 23e3d037e): `GraphClient extends GraphClientGenerated` (`harness/graph/app/graph/GraphClient.ts:1-6`), with `GraphApi implements CddApi` as transport and the server mounting the generated `graphRoutes` (`server.ts:8,50`). Was: Requested (2026-11-06, non-functional): the Graph app reaches the CDD domain through the TypeScript language adapter generated by the cdd_web_domain_access pattern, instead of its own calls.

#### (S) Person --> Invoke Story Explorer In Session Context

Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "view story map / ux design canvas for a session", requested on 2026-11-06): the board opens the browser story explorer on the ticket's story map, framed by its design canvas screens.

# (E) Move Work Forward From Chat Bar

The Chat Bar is the line above the chat prompt for the one session the chat works in, so where the board says ticket it says session (CDR `harness/chat-ui/.context/cdr/0001-stage-strip-band.md`). Acceptance tests are under `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/`.

## (E) Check CDD Server Health In Chat Bar

### (S) Chat Bar --> [Display Server Health Mark](../../chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/display-server-health-mark/display_server_health_mark_story.test.ts)

Observed: `ServerHealthBandView` draws ✓ connected, ⟳ reconnecting, ✕ disconnected or ! tools missing, left of the session name.

### (S) Person --> [Open Server Health Panel](../../chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/open-server-health-panel/open_server_health_panel_story.test.ts)

Observed: the panel shows MCP host, Tools with the loaded count, Kanban app, Graph app and Hook server, or a headline saying what is wrong; pressing the mark pins it open.

### (S) Person --> [Reconnect CDD Server](../../chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reconnect-cdd-server/reconnect_cdd_server_story.test.ts)

Observed: Reconnect retries `cdd` up to three times (`RECONNECT_TRIES`), then reads the active session again.

### (S) Person --> [Reinstall CDD Tools](../../chat-ui/pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reinstall-cdd-tools/reinstall_cdd_tools_story.test.ts)

Observed: Run install runs the installer and says installing, installed (open a new session) or failed; Details shows the tool, error, server and fix.

### (S) Person --> Update CDD From Chat Bar

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "checkout latest and build"), and Requested on 2026-11-06 as the CDD Kanban does: get the latest commit, rebuild the board, pin the cdd server to that commit, and restart the board.

### (S) Person --> Open App From Health Panel

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "click on app in health bar"): pressing the Kanban app or Graph app in the server health panel opens that app. Requested (2026-11-10, "clicking on app in chat ui starts it if down, opens it if up"): pressing an app that is not running starts it and then opens it; pressing one that is running opens it.

### (S) Person --> Restart Parts From Chat Bar

Intended (`.sessions/_backlog/guard-work-and-recover-fast.md` "restart buttons not on panel"): the restart controls sit on the chat bar itself, not only inside the server health panel.

## (E) See Work In Chat Bar

### (S) Person --> Open Board From Chat

Observed: the `/board` command in `harness/chat-ui/pane/hooks/register.ts` opens the board, starting it when it is not running.

### (S) Chat Bar --> [Display Stage Strip](../../chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-stage-strip/display_stage_strip_story.test.ts)

Observed: one line with the health mark, the session name, fidelity dots, action button, stage icons, then handoff, files and close (`chat-bar-view.tsx` `LineView`).

### (S) Chat Bar --> [Display Session Fidelity Dots](../../chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-fidelity-progress/display_fidelity_progress_story.test.ts)

Observed: one square per fidelity of the shown stage in its practice's colour, fainter the less is done, with the violation count in red beside it and the fidelity's name above it on hover (`FidelityView`).

### (S) Person --> [Display Stage Fidelities](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/display-stage-fidelities/display_stage_fidelities_story.test.ts)

Observed: pressing a stage icon shows that stage's fidelities on the dots, tinted while it is not the stage in progress, and drops an action picked from the menu (`stage-client.ts` `selectStage`).

### (S) Person --> [Display Session Card](../../chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-session-card/display_session_card_story.test.ts)

Observed: the pointer on the session name shows the card, with each fidelity's name and state over its dot and its folder as a chip that opens its files; pressing the name pins the card open and ✕ closes it (`session-card-view.tsx`). The folder chip covers `.sessions/_backlog/bring-chat-bar-level-with-board.md` "Click a practice to get its file list".

### (S) Chat Bar --> Show Active Session On Status Line

Observed (`register.ts` `showStatus`, `chat-bar-client.ts` `statusLine`): the status line below the chat, where the host draws a plugin's status, names the repository, the active session, the folder it works in, and the action the button runs with the fidelities it runs on; a press on the chat bar shows the action it now runs. Requested on 2026-11-11 ("repo . session . root path of session . action selected", "below the actual chat edit like before"). Left aligned was also asked; the host places a plugin's status line itself, so a plugin cannot align it, and drawing the row in the chat bar or in the prompt hint line (tried in ce6b9157e and 066b2d3fc) lost it below the chat.

### (S) Claude Code --> [Add Active Ticket To System Prompt](move-work-forward-from-chat-bar/see-work-in-chat-bar/see_work_in_chat_bar_story.test.md#story-add-active-ticket-to-system-prompt)

Inferred: the `prompt.compose` hook in `register.ts` adds the active session and its next guidance, and leaves the prompt unchanged with no active session. Intended (`.sessions/session-board/ticket-enhancements.md`): the prompt also names the file that holds the ticket's text (increment Maintain Tickets On Board).

## (E) Steer Sessions

### (S) Person --> [Create New Session](../../chat-ui/pane/test/move-work-forward-from-chat-bar/steer-sessions/create-new-session/create_new_session_story.test.ts)

Observed: the ▾ beside the session name opens the session list, whose field names a new session that `ticket.create` creates (`session-client.ts` `createSession`). Requested (2026-11-06, as the CDD Kanban does): choose the session root.

### (S) Person --> [Open Session](../../chat-ui/pane/test/move-work-forward-from-chat-bar/steer-sessions/open-session/open_session_story.test.ts)

Observed: picking a session from the list opens a dialog saying the active session is committed and pushed, with merge off, and that the new one opens on its own branch and worktree, then calls `board.activate` (`session-dialogs-view.tsx` `ActivateView`).

### (S) Person --> [Write Session Handoff](../../chat-ui/pane/test/move-work-forward-from-chat-bar/steer-sessions/write-session-handoff/write_session_handoff_story.test.ts)

Observed: the ⇥ handoff icon adds "Write a handoff for ticket <session> with /space-handoff-handoff-session." to the prompt (`chat-bar-client.ts` `runHandoff`).

### (S) Chat Bar --> Display Latest Session Handoff

Requested (2026-11-06, as the CDD Kanban does): the chat bar shows the active session's latest handoff.

### (S) Person --> [Close Session From Chat Bar](../../chat-ui/pane/test/move-work-forward-from-chat-bar/steer-sessions/close-active-session/close_active_session_story.test.ts)

Observed: the ✕ icon opens a dialog saying the session's work is committed and pushed first when it has a branch, then Close session calls `ticket.close` (`session-dialogs-view.tsx` `CloseView`).

### (S) Person --> Add Backlog Item From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"), from `.sessions/_backlog/bring-chat-bar-level-with-board.md`: an Add to backlog button on the chat bar adds a feature to the backlog, as the board's Add Backlog Item does.

### (S) Person --> Commit Work From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Commit button commits the active session's changes (`Repo.commit` in `space/repo/repo.py`).

### (S) Person --> Push Work From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Push button pushes the active session's branch (`repo.push_commit`).

### (S) Person --> Pull Latest From Chat Bar

Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Pull button pulls the latest commits into the active session's checkout (`Repo.pull` in `space/repo/repo.py`).

## (E) Guide Work Through Practices In Chat Bar

### (S) Person --> [Move Session To Next Stage](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/move-session-to-next-stage/move_session_to_next_stage_story.test.ts)

Observed: once every fidelity of the stage is reviewed, the action button shows ➜ and pressing it calls `ticket.move_next` (`action-button-view.tsx` `actionOf`).

### (S) Person --> Move Session To Previous Stage

Requested (2026-11-06, as the CDD Kanban does): the chat bar moves the session back a stage through `ticket.move_previous`.

### (S) Person --> Mark Session Done In Stage

Requested (2026-11-06, as the CDD Kanban does): the chat bar marks the active session Done in its stage and back to In progress.

### (S) Person --> Choose Session Practices

Requested (2026-11-06, as the CDD Kanban does): the chat bar turns the active session's practices on and off through `ticket.enable_practice`. Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "Toggle practices on and off from the card"): the practices turn on and off from the expanded session card.

### (S) Person --> Open Fidelity Help

Requested (2026-11-06, as the CDD Kanban does): the chat bar opens the same help for a fidelity or practice through `board.help`.

### (S) Person --> Choose Session Folders From Chat Bar

Requested (2026-11-10, "new session or session where folders aren't set on switch --> probably one dialog box, eg expand above chat bar"): when the chat bar creates a session that does not come from a backlog item, or switches to a session whose workpath and practice roots are not set, one dialog opens above the chat bar to choose the workpath and each practice's root, as the board's Choose Where A Backlog Item Works and Choose Session And Practice Roots do.

### (S:system) Ticket --> List Available Patterns

Requested (2026-11-11, "opens a list box for LERN, MERN eg all patterns we have ... set this list dynamically based on contents of folder"): a ticket's `overlay_choices` answers one choice per pattern, each with its icon and whether the session chose it. The patterns are every one registered from `cdd_guidance/patterns/`, where each subfolder whose module of the same name defines a pattern class registers itself (`PatternOverlays.names`), so a pattern folder added there is offered with no change to the chat bar.

### (S) Person --> Choose Graph Overlays

Requested (2026-11-11, "right after practices we need + overlay button where we can add one or more graph overlays ... can select more than one"): a + right after the fidelity dots opens a list box of the patterns the board lists, the session's chosen ones marked; a press on one adds it to or takes it out of the session's overlays through `ticket.choose_overlays`, which keeps them in the session's `session.json` and applies them to the session's graph (`Graph.overlays`).

### (S) Chat Bar --> Display Overlay Icons

Requested (2026-11-11, "adds a new icon to bar, pushing action and format", "icon is first and last letter of pattern"): each overlay the session has chosen shows as an icon after the + and before the format chips and the action button, its pattern's first and last letter in capitals (`lern_domain_driven` is LN), the pattern's name on hover.

## (E) Work Fidelity Outputs In Chat Bar

### (E) Generate Fidelity Outputs In Chat Bar

#### (S) Person --> [Select Fidelity](../../chat-ui/pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/select-fidelity/select_fidelity_story.test.ts)

Observed: pressing a dot selects that fidelity, and the action button then shows its next action, such as ▶ generate for a fidelity still to do; selecting another drops an action picked for the one before, and nothing is sent to the chat (`fidelity-client.ts` `selectFidelity`).

#### (S) Chat Bar --> Display Action Before Fidelity Dots

Requested (2026-11-06, "reorder buttons; action then practices"): the action button and its picker come first on the line, then the practices' fidelity dots, so the person chooses what to do before choosing where.

#### (S) Person --> Select Several Fidelities

Observed (commit a585473e3; `fidelity-progress-client.ts` `selectFidelity`): a press on a fidelity, on the line or on the session card, adds it to or takes it out of the selection, and the action button runs one command on every selected fidelity. Requested on 2026-11-06 ("multi select").

#### (S) Person --> [Choose Action](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/choose-fidelity-action/choose_fidelity_action_story.test.ts)

Observed: the ▾ on the action button opens a list of generate, validate, review, iterate, sketch, render and document, with the fidelity's next one marked next; picking one puts it on the button in place of the next action (`action-button-view.tsx` `PickerView`).

#### (S) Person --> Choose Format

Observed (commits a6ddef81c, 21a87f4a7; `chat-bar-view.tsx`, `format-choices-client.ts`): one chip per format group the fidelities offer sits just before the action button, as on a board ticket; a press turns it on or off, and the picked formats go into generate and render. Requested on 2026-11-06 ("add format multi select"). Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "Toggle formats on the card, as the format chips do on the bar"): the session card carries the same chips.

#### (S) Person --> [Generate Session Fidelity Output](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/invoke-next-fidelity-action/invoke_next_fidelity_action_story.test.ts)

Observed: pressing the button on generate puts the commands of `ticket.generate_commands` for the fidelity's default format in the prompt box, a render first when the fidelity before it uses another format; the person presses Enter to send them (`fidelity-client.ts` `runAction`).

#### (S) Claude Code --> Resolve Session Fidelity Output Paths

Observed: `Generate` and `Session.fidelity_outputs` take the outputs the fidelity declares, with the session's `session.json` overrides, as on the CDD Kanban.

#### (S) Person --> Fill Prompt With Fidelity Action

Observed: pressing the button on validate, render, iterate, sketch or document puts `/actions-<action> <guidance>` in the prompt box for the person to send (`fidelity-client.ts` `runAction`).


#### (S) Person --> [Run Fidelity Action With Overlays](move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar/generate_fidelity_outputs_in_chat_bar_story.test.md)

Requested (2026-11-11, "doesnt result in LERN being passed in as a param? shouldnt it?"): the command the action button puts in the prompt names the session's chosen overlays in an `overlays=` word beside `format=` (`overlay-choices-client.ts` `overlayArgumentOf`); an action run with that word chooses those overlays on the session first (`WorkList.take`), and Generate adds each overlay's shared rules on top of the practices' rules (`Generate._overlay_rules`).
### (E) Review Fidelity Outputs In Chat Bar

#### (S) Person --> [List Session Files](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/list-session-files/list_session_files_story.test.ts)

Observed: the ▤ files icon, or a folder chip on the session card, opens a tab per file `fidelity-progress.files` declares for the selected fidelity (`fidelity-files-client.ts` `openFiles`).

#### (S) Person --> [View Session Files](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/view-fidelity-files/view_fidelity_files_story.test.ts)

Observed: each tab's text comes from `session.read_file`, which refuses a file outside the session's roots. This covers `.sessions/_backlog/bring-chat-bar-level-with-board.md` "Show the file list, with each file clickable to open it": the files view has one tab per file.

#### (S) Person --> Open Validation Report From Violation Count

Observed (chat-ui story map, View Fidelity Files): pressing a fidelity's red violation count opens its latest report, from `fidelity-progress.report`, in its own tab drawn as markdown. Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "open its validation report"): the session card opens a practice's report too.

#### (S) Person --> Fix Violations From Chat Bar

Requested (2026-11-06, as the CDD Kanban does): the chat bar sends Fix and Fix all for the report it opens.

#### (S) Person --> [Review Session Fidelity](../../chat-ui/pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/review-fidelity/review_fidelity_story.test.ts)

Observed: pressing the button on review records the person's approval through `fidelity-progress.finish_review`, which refuses it until the fidelity's latest Validate passed (`chat-bar-client.ts` `reviewFidelity`).

### (E) Integrate Practice Content Editor Apps In Chat Bar

#### (S) Person --> Open Story UI Side Panel From Chat Bar

Requested (2026-11-06, "chat band -> story UI side panel"): the chat bar opens the Story UI editor in a side panel on the active session's story map. Also Intended (the chat bar, as the CDD Kanban).

#### (S) Person --> Invoke Claude Design Story Explorer From Chat Bar

Intended (requested on 2026-11-06, as the CDD Kanban): the chat bar opens the Claude Design story explorer the design canvas draws today (`explorer.dc.html`) on the active session's story map and screens.

#### (S) Agent --> Deploy Story UI App With Board State

Requested (2026-11-06, non-functional): the Story UI app runs on the same app server and instance as the board's state, so the story map, the explorer and the board share one state for the active ticket.

#### (S) Agent --> Refactor Story UI App To Web Domain Access

Requested (2026-11-06, non-functional): the Story UI app reaches the CDD domain through the TypeScript language adapter generated by the cdd_web_domain_access pattern, instead of its own calls.

#### (S) Person --> Open UX Design In Claude Design

Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "claude design integration with ux tool"): the UX practice's design opens in Claude Design from the chat.

#### (S) Person --> Trace Story Through Artifacts

Intended (`.sessions/_backlog/integrate-practice-content-editor-apps.md` "Trace pane"): picking a story shows its scenarios, tests and code from `harness/graph`, with the domain, class and bounded-context diagrams. Built today (checked 2026-11-10): the Graph app folds story, scenario and step and shows a step's invokes, observes and demonstrates with its source (`harness/graph/app/app.test.tsx:429,746`). Missing: one trace view of a picked story's scenarios, tests and code, and the diagrams.

### (E) Capture Session Knowledge

#### (S) Claude Code --> Write Handoff When Session Ends

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Automatic handoff"): the handoff is written when a session ends, so the next session never starts cold. Built today (checked 2026-11-10): closing or leaving a session from the chat bar offers Create handoff, on by default (`session-dialogs-view.tsx:34`). Missing: writing one when a Claude Code session ends.

#### (S) Claude Code --> Offer Correction Log Entry

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Correction capture"): `$.model.classify` spots when the person corrects generated work and offers, in the chat panel, to add it to `corrections.log` beside that work.

#### (S) Claude Code --> Offer Decision Record

Intended (`.sessions/_backlog/suggest-the-next-step.md` "Correction capture"): the same check spots a decision and offers to write a CDR for it.

## (E) Enter CDD Commands Faster

### (S) Claude Code --> Autocomplete CDD Commands

Intended (`.sessions/_backlog/enter-commands-faster.md` "Command entry and autocomplete"; `.sessions/_backlog/enter-commands-faster.md` "constrained lists params on commands"): `prompt.autocomplete` offers an action, then a practice-fidelity, then content or a file, taken from the installed CDD catalog so the lists cannot drift.

### (S) Claude Code --> Show Command Argument Hints

Intended (`.sessions/_backlog/enter-commands-faster.md` "argumentHint"): after a command's name, the prompt shows the parameters it expects.

### (S) Claude Code --> Suggest Next Command

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

# (E) Author Story Maps

This epic is the app's own story map, `C:/dev/story-ui/.context/story-map.md`; its evidence lines name the app's files.
## (E) View Story Map
### (S) Story Designer --> Open Story Map By Address

Observed: The workspace loads the map named in the `?mapId=` query (or `default`) and, when no map with that id exists yet, the server creates and saves an empty one so the designer always lands on a map (main.tsx; stories-server.ts `createStoryMapRouter` GET `/`).

### (S) Story Designer --> Pick Story Map From Dashboard

Intended (story_map.information_architecture.md, Story Map Dashboard scaffold): a dashboard lists maps and "open map" takes the designer into the workspace; no dashboard screen exists.

### (S) Story Designer --> Browse Story Hierarchy

Observed: The map renders Epic, SubEpic, and Story lanes on one shared grid, with each Story under its parent SubEpic column, lanes sized to their bottommost children, and collapsed titles kept on one line (stories-client.tsx `StoryHierarchyView`, `computeColumnLayout`; workspace.css).

### (S) Story Designer --> Browse Nested SubEpic Lanes

Intended (mern-story-map-ai-sketch.md, Browse Story Hierarchy): nested SubEpics render as two stacked SubEpic lanes under their parent SubEpic; the model in stories.ts holds only one SubEpic level.

### (S) Story Designer --> Inspect Selected Node Fields

Intended (mern-story-map-ai-sketch.md, BDD "when the Story Designer selects a node"): selecting a Story shows story_type and users, a SubEpic shows test_file and domain_concepts; the cards show only names and controls.

### (S) Story Designer --> Pan Workspace Canvas With Right-Click Drag

Observed: Holding the right mouse button and dragging scrolls the canvas on both axes, suppresses the browser context menu, shows a grabbing cursor, and stops on release even outside the canvas (stories-client.tsx `StoryMapWorkspaceView` `handleCanvasMouseDown` and window mouse listeners).

### (S) Story Designer --> Switch Between Map View And Increment View

Observed: The toolbar's Map View and Increment View buttons switch between the plain map and the map with increment lanes and an Unassigned drop zone (stories-client.tsx `useStoryMapViewState.toggleViewMode`, `StoryHierarchyView` `showIncrements`).

### (S) Story Designer --> Show And Hide Scenarios And Examples

Intended (story_map.information_architecture.md toolbar; story_map.modules.md session toggles): Show Scenarios and Show Examples buttons toggle their active state in stories-client.tsx, but the story card and scenario panel ignore them, so nothing is shown or hidden.

### (S) Story Designer --> Switch Color Mode

Observed: The Executive / Engineering switch changes the page theme and logo and remembers the choice in browser storage (stories-client.tsx `StoryMapWorkspaceView` `THEME_STORAGE_KEY`; workspace.css `data-theme`).

## (E) Expand Story Details
### (S) Story Designer --> Expand One Story Card

Observed: Clicking a Story card or its expand button opens that card inline to show its Scenarios, Steps, and Example tables while neighbouring cards stay collapsed in their columns; clicking again collapses it (stories-client.tsx `StoryCard`, `handleExpand`).

### (S) Story Designer --> Expand Descendant Story Cards

Observed: The expand button on an Epic or SubEpic opens every Story card beneath it side by side in their own columns (stories-client.tsx `getAllDescendantStoryIds`, `useStoryMapViewState.expandDescendants`).

### (S) Story Designer --> Expand And Collapse Whole Map

Observed: The toolbar's Expand All opens every Epic, SubEpic, and Story, and Collapse All closes them all (stories-client.tsx `StoryMapWorkspaceView` toolbar, `collapseAll`).

### (S) Story UI --> Widen Columns Around Expanded Story Cards

Observed: An expanded card grows to fit its content and its column, the SubEpic and Epic lanes above it, and everything to its right shift to make room, then narrow again on collapse (workspace.css `.story-card.expanded`; stories-client.tsx shared grid in `StoryHierarchyView`).

## (E) Build Map Structure
### (S) Story Designer --> Add First Epic To Empty Map

Observed: A map with no Epics shows a single "+ Epic" starter button that opens the title popover (stories-client.tsx `StoryHierarchyView` Epic lane, `AddNodePopoverButton`).

### (S) Story Designer --> Add Epic, SubEpic, Or Story At Chosen Position

Observed: The + on a card, or the leading + on the first card in a group, opens a title popover; Add uses the typed title or a default name, Cancel or Escape creates nothing, and the new node lands after that sibling or at the start (stories-client.tsx `AddNodePopoverButton`, `insertEpicAfter`, `prependSubEpic`, `insertSubEpicAfter`, `prependStory`, `insertStoryAfter`; stories-server.ts POST `/epics`, `/epics/:epicId/sub-epics`, `/sub-epics/:subEpicId/stories`).

### (S) Story Designer --> Remove Epic, SubEpic, Or Story

Observed: The − on a card deletes that node and everything under it and renumbers the remaining siblings to close the gap (stories.ts `removeEpic`, `removeSubEpic`, `removeStory`; stories-server.ts DELETE routes).

### (S) Story Designer --> Rename Node Inline

Observed: Double-clicking a card focuses its name; Enter, Tab, or leaving the field saves the new name and Escape restores the old one (stories-client.tsx `NodeNameInput`, `focusNameFieldOnDoubleClick`; stories-server.ts PATCH `/nodes/:nodeId` via `translateFrom`).

## (E) Rearrange Map By Dragging
### (S) Story Designer --> Reorder Sibling Epics, SubEpics, And Stories

Observed: Dragging a card within its own lane or parent saves the new sibling order with whole-number positions (stories-client.tsx `makeEpicDragHandlers`; stories.ts `reorderEpics`, `reorderSubEpics`, `reorderStories`).

### (S) Story Designer --> Move Story To A Different SubEpic

Observed: Dropping a Story card on another SubEpic, even under a different Epic, moves it there with its Scenarios at the dropped position (stories-client.tsx `makeStoryDragHandlers`; stories.ts `StoryMapModel.moveStory`).

### (S) Story Designer --> Move SubEpic To A Different Epic

Observed: Dropping a SubEpic lane on another Epic moves it and all its Stories there at the dropped position (stories-client.tsx `makeSubEpicDragHandlers`; stories.ts `StoryMapModel.moveSubEpic`).

### (S) Story Designer --> Drop Node Into Empty Parent

Observed: An Epic with no SubEpics or a SubEpic with no Stories accepts a dragged SubEpic or Story into its empty placeholder (stories-client.tsx `makeEmptyParentDropZone`).

### (S) Story Designer --> See Full-Size Drop Preview While Dragging

Observed: While dragging, the card itself shows full-size, greyed and dashed, at the spot it would land and its siblings shift around it, with no floating browser drag image (stories-client.tsx `useDragVisuals`, `computeDisplayIds`, `suppressNativeDragImage`).

## (E) Plan Increments
### (S) Story Designer --> Add Increment

Observed: In Increment View the "+ Increment" button appends a new increment lane at the bottom (stories-client.tsx `StoryHierarchyView`; stories.ts `appendIncrement`).

### (S) Story Designer --> Rename Increment

Observed: The increment label is an inline name field saved on Enter, Tab, or leaving it, with Escape restoring the old name (stories-client.tsx `IncrementLabel`).

### (S) Story Designer --> Reorder Increments

Observed: Dragging an increment label up or down saves the new increment order (stories-client.tsx `IncrementLabel` drag handlers; stories.ts `reorderIncrements`).

### (S) Story Designer --> Remove Increment

Observed: The − on an increment label deletes that increment and its Stories return to the unassigned spine (stories.ts `removeIncrement`; stories-server.ts DELETE `/increments/:incrementId`).

### (S) Story Designer --> Assign Story To Increment By Dragging

Observed: Dropping a Story card on an increment lane moves it into that increment, out of any other, while it stays under its SubEpic column (stories-client.tsx increment lane `onDrop`; stories.ts `assignStoryToIncrement`).

### (S) Story Designer --> Unassign Story From Increment

Observed: Dropping a Story card on the "Unassigned" zone, shown only in Increment View, removes it from its increment and puts it back in the spine (stories-client.tsx Unassigned drop zone; stories.ts `unassignStoryFromIncrement`).

## (E) Author Scenarios And Steps
### (S) Story Designer --> Add Scenario Under Story

Observed: The + beside Scenarios in an expanded Story card adds "New Scenario" at the end of that Story's Scenarios (stories-client.tsx `handleAppendScenario`; stories.ts `StoryModel.appendScenario`).

### (S) Story Designer --> Rename Scenario

Observed: The Scenario name is an inline field saved on Enter, Tab, or leaving it, with Escape restoring the old name (stories-client.tsx `ScenarioPanel` `saveScenarioName`).

### (S) Story Designer --> Remove Scenario

Observed: The − on a Scenario deletes it and renumbers the remaining Scenarios (stories.ts `StoryModel.removeScenario`).

### (S) Story Designer --> Reorder Scenarios

Observed: Dragging a Scenario by its handle within the expanded card saves the new Scenario order (stories-client.tsx `StoryCard` `makeDragHandlers`; stories.ts `reorderScenarios`).

### (S) Story Designer --> Add Step

Observed: The + beside Steps adds a "Given New step" at the end of that Scenario (stories-client.tsx `handleAddStep`; stories.ts `ScenarioModel.addStep`).

### (S) Story Designer --> Edit Step Keyword And Text

Observed: Each Step has a Given/When/Then/And/But selector and a text field, saved on Enter or Tab and restored on Escape (stories-client.tsx `StepEditor`; stories.ts `updateStep`).

### (S) Story Designer --> Remove Step

Observed: The − on a Step deletes it and renumbers the remaining Steps (stories.ts `ScenarioModel.removeStep`).

### (S) Story Designer --> Reorder Steps

Observed: Dragging a Step by its handle saves the new Step order within that Scenario (stories-client.tsx `ScenarioPanel` step drag handlers; stories.ts `reorderSteps`).

## (E) Author Examples
### (S) Story Designer --> Add Example To Scenario

Observed: The + beside Examples adds an empty "New Example" table to the Scenario (stories-client.tsx `handleAddExample`; stories.ts `ScenarioModel.addExample`).

### (S) Story Designer --> Remove Example From Scenario

Observed: The − on an Example deletes that table and renumbers the remaining Examples (stories.ts `ScenarioModel.removeExample`).

### (S) Story Designer --> Add Example Field

Observed: Typing a field name in the header and pressing + adds a column, and a name already in the table is refused (stories-client.tsx `ExampleBlock`; stories.ts `addExampleField`, `DUPLICATE_FIELD_NAME`).

### (S) Story Designer --> Remove Example Field

Observed: The − on a column header removes that field from the Example (stories.ts `ScenarioModel.removeExampleField`).

### (S) Story Designer --> Add Example Line

Observed: The add button under the table adds an empty line at the bottom of the Example table (stories-client.tsx `handleAddExampleRow`; stories.ts `addExampleRow`).

### (S) Story Designer --> Edit Example Cell

Observed: Each cell is an inline field saved on Enter or leaving it (stories-client.tsx `ExampleCellEditor`; stories.ts `updateExampleRow`).

### (S) Story Designer --> Remove Example Line

Observed: The − on a line deletes it and renumbers the remaining lines (stories.ts `ScenarioModel.removeExampleRow`).

### (S) Story Designer --> Reorder Example Lines

Observed: Dragging a line by its handle saves the new line order in that Example (stories-client.tsx `ExampleBlock` line drag handlers; stories.ts `reorderExampleRows`).

## (E) Save And Share Changes
### (S) Story UI --> Save Each Edit To The Server

Observed: Every edit is sent to the server as one request, saved to MongoDB, and the map is reloaded from the saved copy (stories-client.tsx `useStoryModel`; stories-server.ts `StoryMapRepositoryServer`, `StoryMapServer.persist`).

### (S) Story UI --> Show Save Status

Observed: The status rail shows synced, pending changes, or save error, and notes when an update report is available (stories-client.tsx `StoryMapWorkspaceView` status rail, `storyModelReducer`).

### (S) Story UI --> Refuse Edits That Break Map Rules

Observed: The server refuses a Scenario under a non-Story, an increment on a non-Story, an unknown increment, a node outside its claimed parent, or a duplicate field name, answers 422 with the rule code, and the status rail shows save error (stories.ts `MutationGuardError`; stories-server.ts error handler).

### (S) Story UI --> Record One Save Event Per Save

Intended (mern-story-map-ai-sketch.md Resolved Implementation Decisions; story_map.modules.md audit): stories-server.ts only comments that the collaboration layer emits the event, and no audit module exists.

### (S) Story Designer --> Browse Save History

Intended (story_map.information_architecture.md, Version History Timeline scaffold): no history screen or save record exists.

### (S) Story Designer --> Recover Workspace View State

Intended (story_map.stories.md, Recover Persisted Story Map State; story_map.modules.md session): session.ts and session-server.ts can store view mode, expanded nodes, and toggles, but app.ts never mounts `createSessionRouter` and the workspace never calls `useStoryMapSession`, so a reload resets the view.

### (S) Story Designer --> Join Real-Time Story Map Session

Intended (story_map.stories.md, Synchronize Story Map State; story_map.modules.md collaboration): no collaboration module or broadcast exists.

### (S) Story UI --> Reconcile Concurrent View State Changes

Intended (story_map.stories.md, Resolve Concurrent View State Changes; mern-story-map-ai-sketch.md realtime-collaboration): no collaboration module exists.

### (S) Agent --> Test Story UI Editor On Session Story Map

Requested on 2026-11-06: the Story UI editor opens a CDD session's `story-map.md`, edits it and saves it back, and its tests run against that map. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

## (E) Author Story Changes With AI
### (S) Story Designer --> Open AI Chat Panel

Intended (story_map.information_architecture.md, open chat to AI Chat Panel scaffold): no chat panel exists.

### (S) Story Designer --> Request AI Story Change

Intended (story_map.stories.md, Request AI Story Mutation; story_map.modules.md ai-mutation): no ai-mutation module exists.

### (S) Story Designer --> Review Proposed Map Changes

Intended (story_map.stories.md, Review Proposed Graph Changes): no proposal view exists.

### (S) Agent --> Apply AI Change To Story Map

Intended (story_map.stories.md, Apply AI Mutation to Story Map; mern-story-map-ai-sketch.md "Direct auto-apply changes"): no ai-mutation module exists.

### (S) Story Designer --> Place Notes On The Story Map

Requested (2026-11-10, "native claude markup panel": "annotate on the story editor app with notes and have a canvas like experience, eg comments sent directly to claude for processing; then potentially reuse that for a bespoke class editor and realization editor"), from `.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md`: a person places notes anywhere on the Story UI editor's map, as on a canvas, beside the nodes they are about. The same markup may later serve a bespoke class editor and a realization editor; those editors are not on this map yet.

# (E) Explore Stories In Story UI

The story explorer is a new part of the Story UI app: the Story UI editor's screen frames view opens it, and its core frame is the selected step's design canvas screen. It replaces the story map artboard and the explorer (`explorer.dc.html`) the design canvas draws today, so every story here is new.

## (E) Show Screen Frames In Story UI

### (S) Person --> Switch Story Map To Screen Frames View

Requested (2026-11-06): the Story UI editor has a screen frames view beside its base view; in it, each story's card has its screen as a frame beneath it. The base view stays the plain story map.

### (S) Story UI --> Show Screen Frame Under Each Story

Requested (2026-11-06): each frame is the story's main design canvas screen, drawn small under its card. It replaces the design canvas, where today the story map artboard draws a thumbnail under each story (`thumbnail` in `canvas.py`, `claude_design_story_model_spec.py`).

### (S) Story UI --> Mark Story Without A Screen

Requested (2026-11-06): a story with no screen gets an empty frame saying so. It replaces the design canvas, where today the artboard shows "No screenshot" in place of the picture (`thumbnail` in `canvas.py`).

### (S) Person --> Open Story Explorer From Screen Frame

Requested (2026-11-06): pressing a frame opens the browser story explorer at that story, scenario and step. It replaces the design canvas, where today only the artboard's thumbnails link, each opening `explorer.dc.html` at its story (`claude_design_story_model_spec.py`).

## (E) Navigate The Story Tree

### (S) Person --> Open The Explorer At A Story, Scenario And Step

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `explorer.dc.html` reads the story, scenario and step from the link, or from the place the map kept, and selects it in the tree.

### (S) Person --> Collapse And Reset The Story Tree

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer's *Collapse all* and *Reset* buttons close the epic → sub-epic → story → scenario → step tree or return it to the first story (`explorer.dc.html`).

### (S) Story UI --> Keep The Selected Story In View

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer scrolls the selected entry into view when the selection changes (`explorer.dc.html`).

### (S) Person --> Copy A Request To Open A Story In Its File

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, the explorer carries each story's and scenario's `path:line` and offers to copy an open-in-file-viewer request for it (`claude_design_story_model_spec.py`, `copyOpenRequest` in `explorer.dc.html`).

### (S) Person --> Pick An Outline Scenario's Example

Built in the design canvas explorer (checked 2026-11-10): `explorer.dc.html` lists an outline scenario's examples from the fixtures bundle and picking one calls `go(..., ex.name)` (`outlineRows`). Intended: the Story UI explorer does the same. Was: Intended (`claude_design.md` outline-rows): an outline scenario lists its examples from the fixtures bundle and picking one loads it on the screen; the explorer does not list them yet.

## (E) Play Stories In The Explorer

### (S) Person --> Play The Next Story

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the explorer's *Play next* button moves the selection to the next step or story (`explorer.dc.html`).

### (S) Person --> Hide And Show The Story Panel

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the » and « buttons hide the story panel so the screen fills the frame, and bring it back (`explorer.dc.html`).

### (S) Person --> Return To Story UI Map

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, the panel's **← Story map** link opens `Main.dc.html` again (`explorer.dc.html`).

### (S) Agent --> Test Story Explorer On Session Story Map

Requested on 2026-11-06: the browser story explorer plays a CDD session's story map on its design canvas screens, and its specs run against that map. Each gap a test finds becomes an Intended story in this app's map, fixed before the board or chat bar invokes the app.

## (E) Frame Design Canvas Screens In Explorer
### (S) Story UI --> Show Design Canvas Screen As Explorer Frame

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, `_imports` in `nodes.py` imports each prototype screen into the explorer with the story, scenario and a `go` call, so the selected scenario runs on the real screen (`claude_design_story_model_spec.py`).

### (S) Story UI --> Choose The Screen For A Step

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where observed, a step shows the screen it is shown on, else its scenario's screen, else its story's screen (`_story_entry` and `_screen_of` in `nodes.py`, `claude_design_story_model_spec.py`).

### (S) Story UI --> Join A Step Without A Screen To The Next Step

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `_story_entry` in `nodes.py` groups a step with no screen of its own with the next step that has one, so every entry the person picks shows a screen.

### (S) Story UI --> Show A Screenshot When No Screen Runs

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, when no prototype applies, the explorer shows the step's screenshot, skipping blank captures (`_blank` in `nodes.py`).

### (S) Story UI --> Keep Each Screen's Own Stylesheets

Requested (2026-11-06): new in the Story UI app; replaces what the design canvas does today, where inferred, `_stylesheets` in `nodes.py` links every stylesheet the prototype screens use, so a screen drawn inside the explorer keeps its own look.

# (E) Build Design Canvas Screens

This epic is the app's own story map, [design_canvas/.context/story-map.md](../../design_canvas/.context/story-map.md); its evidence lines name the app's files.
## (E) Lay Out The Canvas Files
### (S) Design Canvas --> Place Pages On The Canvas

Observed: `DesignCanvas.add_page` lists each page in `canvas.json` in the order added, and the canvas launches on the first page (`design_canvas_spec.py`).

### (S) Design Canvas --> Place Artboards On Their Pages

Observed: `DesignCanvas.add_board` puts each artboard on its page and keeps the order they were added in `canvas.json` (`design_canvas_spec.py`).

### (S) Design Canvas --> Write The Canvas Into A Project Folder

Observed: `DesignCanvas.write` puts `canvas.json` and every artboard it was given text for under `project/` in the chosen folder, so the folder can be published as it is (`design_canvas_spec.py`).

### (S) Design Canvas --> Name An Imported Screen After Its File

Observed: `stem` and `camel` in `canvas.py` give a screen file's import name and its live flag in camel case, so the explorer can import the screen by name (`design_canvas_spec.py`).

### (S) Design Canvas --> Give Each Prototype Screen Its Own Page

Observed: `ClaudeDesignStoryModel.canvas` puts the story map, the story explorer, and each prototype screen on its own page (`claude_design_story_model_spec.py`).

### (S) Design Canvas --> Place A Read-Only Story Panel Beside A Screen

Observed: `_context_panel` in `nodes.py` draws a Stories board to the right of a screen, with the screen's own stories opened to their scenarios and steps and every other story greyed out (`claude_design_story_model_spec.py`).

## (E) Load Scenario Fixtures With The Fixture Bar
### (S) Person --> Load A Scenario Into A Standalone Screen

Inferred: opened on its own, a screen's fixture bar starts on *Load a scenario…* and loads nothing until the person picks a scenario, which loads its fixture and types the values it enters (`fixture_bar.py` `loadFromFixture`).

### (S) Design Canvas --> Load The Explorer's Scenario Into The Screen

Inferred: inside the explorer the screen loads the explorer's scenario as soon as the fixtures bundle is there, and again whenever the explorer moves (`fixture_bar.py` `followExplorer`).

### (S) Person --> Pick Another Scenario From Inside The Explorer

Inferred: picking a scenario on the bar inside the explorer loads it and moves the explorer's tree to it (`fixture_bar.py` `pickScenario`).

### (S) Person --> Paste Dev Seed Data Into A Screen

Inferred: the bar lists dev mode's seed paste for the screen's path, and picking it types each pasted field into the screen (`fixture_bar.py` `pasteSeedData`).

### (S) Person --> Follow A Screen Link To The Next Story

Inferred: a link to the next screen moves the explorer to that story, or opens the next screen when the screen stands alone (`fixture_bar.py` `follow`).

### (S) Person --> Edit A Screen On Its Own Artboard

Inferred: inside the explorer the bar ends with **Edit**, a link to the screen's own artboard, because an edit inside the explorer would change the explorer (`fixture_bar.py` `bar`).

### (S) Design Canvas --> Report Where The Screen's Data Came From

Inferred: the bar's values carry the loaded story and scenario, the pasted seed, or the loading problem (`fixture_bar.py` `barVals`).

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

Observed: `record_link` keeps each version's canvas link in `versions.json`, in the order published (`versions_spec.py`).

### (S) Agent --> Keep A Published Version As A Release

Observed: `release` renames the version's folder and its link to the release's name (`versions_spec.py`).

### (S) Agent --> Remove Older Versions When Keeping A Release

Intended (`claude_design.md` release-a-version): when a version is kept as a release the older versions are removed; `release` in `versions.py` only renames.

### (S) Agent --> Start Numbering Again From A Release

Observed: once no numbered version is left, `start_next` starts `version-1` as a copy of the latest release (`versions_spec.py`).

### (S) Agent --> Find A Release's Canvas Folder

Observed: `CanvasVersions.in_practice_root` opens `<ux root>/design-canvas`, in the root session.json names for the UX practice, beside its other outputs (`versions_spec.py`).

## (E) Reuse Production Assets On The Canvas

Intended ([sync-design-canvas-with-production.md](../../../.sessions/_backlog/sync-design-canvas-with-production.md)): the product repo builds one package of its real CSS, images, fonts and React views, published as a pinned Design System artifact; each screen becomes a thin shell that mounts the real view, and a manifest proves every packaged file by hash. A published canvas only sees its own `project/` files, so links and symlinks cannot do this. The four feature groups below are the asset reuse plan's phases 1 to 4 and come before every other new design canvas story.

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

Intended (asset reuse plan, `one-scenario-list` under "Thin screens"; [integrate-stories-with-the-canvas-explorer.md](../../../.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md) slice C): a mounted view owns its state, so a DOM driver types the scenario's entered values; the same driver plays UI steps in Play A Story's UI Steps On A Screen.

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

Intended ([integrate-stories-with-the-canvas-explorer.md](../../../.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md)): a person presses Test and sees, for each scenario, whether the screen behaves as its specs say. Built after Phase 0 of the asset reuse plan.

### (S) Agent --> Package End-To-End Results With The Canvas

Intended (integrate-stories-with-the-canvas-explorer.md slice A): at package time the end-to-end JSON under `.sessions/<release>/e2e-test-results` becomes a `results.json` tied to the bundle hash.

### (S:system) Design Canvas --> Mark Each Explorer Scenario Passed Or Failed

Intended (integrate-stories-with-the-canvas-explorer.md slice A): each explorer scenario shows passed, failed or no result.

### (S:system) Design Canvas --> Label Stale Test Results

Intended (integrate-stories-with-the-canvas-explorer.md slice A and "Done means"): a result whose bundle hash differs from the canvas's bundle is labelled stale.

### (S) Person --> Run A Scenario's Thens On The Canvas

Intended (integrate-stories-with-the-canvas-explorer.md slice B): a Test button per scenario and per story runs the `beforeEach` and `it` bodies through a second story host with a real `expect` in a test build, and shows passed or failed for each step with the failing assertion's message.

### (S) Person --> Play A Story's UI Steps On A Screen

Intended (integrate-stories-with-the-canvas-explorer.md slice C): the story's Playwright steps run against the screen through a small `page` facade over the DOM, so a detached screen is tested against the same story as production.

### (S) Agent --> Check Screen Logic Against Scenarios From A Command

Intended (integrate-stories-with-the-canvas-explorer.md slice D, only if slice C proves too limited): `check_screen.cjs` becomes a generic command in `harness/design_canvas/` that runs a screen's logic on each scenario.

## (E) Draw Linked Models On The Canvas

Intended ([draw-linked-models-on-the-canvas.md](../../../.sessions/_backlog/draw-linked-models-on-the-canvas.md)): the bounded context map, the domain model and the module class models sit beside the story map as artboards that mirror their drawio layout and link to one another, so from any story a person reaches its screen, its classes and its bounded context and back.

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

This epic is the app's own story map, [graph/.context/story-map.md](../../graph/.context/story-map.md); its evidence lines name the app's files.
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
### (S) Knowledge Graph --> Read Modules Classes And Operations

Observed: Clean Engineering reads modules (folders with a module card), packages, classes, operations, properties and parameters, keeps each file's top-level functions in a `_module` class, and orders their groups under each node (`working_copy.py` `_record_clean`, `graph_spec.py` "with clean engineering", `working_copy_scan_spec.py` "over module cards").

### (S) Knowledge Graph --> Read Clean Engineering Model Documents

Inferred: the load reads each scoped folder's `.context/*-model.md` beside the code so members and interactions the model document names join the graph (`working_copy.py` `_record_clean_models`, described in `cdd_guidance/practices/bdd/bdd.md`).

### (S) Knowledge Graph --> Place DDD Building Blocks Under Aggregates

Observed: DDD reads bounded contexts from folders holding `.context/bounded-context.md` and places aggregates, entity roots, value objects and repositories under them by stereotype (`working_copy.py` `_record_ddd`, `graph_spec.py` "with domain-driven design").

### (S) Knowledge Graph --> Read Story Maps And Story Tests

Observed: Stories reads epics, sub-epics and stories from story map markdown and draw.io files, and scenarios, steps and examples from story tests, keeping each node's path and line (`working_copy.py` `_record_stories`, `graph_spec.py` "with stories", `working_copy_scan_spec.py` "limited to an edited story map markdown file", "limited to an edited Python story test").

### (S) Knowledge Graph --> Read BDD Spec Trees

Observed: BDD reads each spec file's describe tree into spec, description, context and observation nodes (`working_copy.py` `_record_bdd`, `graph_spec.py` "with behavior-driven development").

### (S) Knowledge Graph --> Link Steps And Observations To Operations

Observed: a story step and a BDD observation each get an `invokes` edge to the operations their code calls, with `invokedBy` back on the operation and setup calls of the enclosing context first (`working_copy.py` `_record_story_edges`, `_record_bdd_edges`, `graph_spec.py` "with a step that invokes an operation", `bdd_invokes_spec.py`).

### (S) Knowledge Graph --> Link Examples To Classes And Steps

Observed: an example that demonstrates a class, a then step that observes an example, and an example retrieved using a property each get their relationship edge in both directions (`schema_edges.py` `SchemaEdges.sync`, `graph_spec.py` "with an example that demonstrates a class", "with a then step that observes an example").

### (S) Knowledge Graph --> Place Story Nodes On Their Source Lines

Observed: scenarios and steps sit in source-line order, a step opens on the call holding its label, a scenario runs through its closing brace, and an imported example sits in its examples file (`graph.py` `Node._edges_in_source_order`, `Source.align_to_label`, `align_to_example_export`, `graph_spec.py` "a scenario", "a step", "an example a story test imports"); `defects.md` still lists scenario and step order under Not fixed.

### (S) Knowledge Graph --> Give Each Node Its Fidelity

Observed: each node knows the fidelity its practice's schema creates it at and every higher fidelity it belongs to (`graph.py` `Node.fidelities`, `graph_spec.py` "a node's fidelity").

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

#### (S:system) Knowledge Graph --> Record Code Metrics As Node Facts

Requested (2026-11-10, "when we run validation at clean model or clean code we integrate the metrics ... and add those findings onto the model itself, it's just another fact on the model: what is its cyclomatic complexity"); Intended (`.sessions/_backlog/measure-code-on-the-model.md`): each function, class and module node carries its measures as facts, such as the paths through a function (cyclomatic complexity), its readability score (cognitive complexity), its lines and parameters, a class's total complexity, method count and dependencies, and methods sharing no data with the rest of their class, measured with the tools `.context/repo-review/metrics_gate.py` already uses (radon, lizard, complexipy, cohesion, grimp).

#### (S:system) Validate --> Check Code Metrics Against Clean Engineering Limits

Requested (2026-11-10, "when we run validation at clean model or clean code we integrate the metrics ... and add those findings onto the model itself, it's just another fact on the model: what is its cyclomatic complexity"); Intended (`.sessions/_backlog/measure-code-on-the-model.md`): at the Clean Engineering model and code fidelities the limits are named rules checked on those facts, such as a function over 10 paths, a readability score over 15, over 50 lines or over 5 parameters, and a class over 100 total complexity or 30 methods. Each function, class or module past a limit shows in the same validation report as the other rules, its metric named in plain English and its trend coloured as getting better or worse.

#### (S:system) Knowledge Graph --> Report Unused Class For Deletion

Intended (`.sessions/_backlog/check-clean-engineering-across-files.md` "Every class is used or uses something"): a production class with no relationship, not using another class, not used, and not built, read or installed at build time (an annotation kind, a published toolset, a registration at import, a generated adapter), is reported as no use, delete. A class others use that uses nothing is in use.

#### (S:system) Knowledge Graph --> Report Runtime Dependency That Should Be Owned

Intended (`.sessions/_backlog/check-clean-engineering-across-files.md` "A runtime dependency must earn its place"): a caller that builds the other object per call from strings or dicts, re-reads a file another object holds, or passes the owner's data into a helper is reported with the owner and the relationship it should be, a part or a held collaborator.

#### (S:system) Knowledge Graph --> Report Disconnected Class

Intended (`.sessions/_backlog/check-clean-engineering-across-files.md` "Disconnected classes"): a class connected only by inheritance, or not at all, is reported as a relationship the model missed or as code that is not resource-oriented, with the owner and the redesign.

#### (S:system) Knowledge Graph --> Report One-Class Package

Intended (`.sessions/_backlog/check-clean-engineering-across-files.md` "One-class packages"): a package holding one class is reported as unused (delete), part of a bigger package (merge), or not fully modelled.

#### (S:system) Validate --> Judge Clean Engineering Rules Across Files

Intended (`.sessions/_backlog/check-clean-engineering-across-files.md` "Other cross-file checks"): where the graph cannot answer, Clean Engineering's validation judges the whole codebase in one pass, not one folder at a time, for second object models, the same behaviour in several files, second registries of practices, actions or stages, global or ambient state, state passed as parameters the object already holds, legacy names and dead code, and swallowed failures.

## (E) Review Violations In Graph App
### (S) Person --> See Rules Under Node

Observed: each node has a rules entry listing its passing, violating and prompt rules, and a violating node is marked in the tree (`graph.py` `Node.rule_category`, `GraphView.tsx`, `app.test.tsx` "should show a passing rule and a violating rule under the operation").

### (S) Person --> Hover Violating Rule For Message

Observed: hovering a violating rule shows its violation messages (`GraphView.tsx` `violationHint`, `app.test.tsx` "should expose the violation message when hovering a violating rule").

### (S) Person --> Open Violation In Source

Observed: selecting a violating rule opens the node's source with a banner naming the rule and message and highlights the lines the hit names (`SourceView.tsx`, `graph/graph-selection.ts` `selectionForRule`, `app.test.tsx` "should show the violation banner, highlight the source").

### (S) Person --> Display Drawio File As Diagram

Requested on 2026-11-06: a `.drawio` file opens as its diagram, with a Source tab for the XML. A violation marks the shape it names in red, and pressing a shape opens its lines in the source. Built today (checked 2026-11-10): the chat bar's files view offers Open in draw.io, which opens the file in the draw.io editor through `tools/drawio_viewer` (`drawio-viewer-client.ts:44`). Missing: a Source tab, marking the shape a violation names, and opening a pressed shape's lines.

### (S) Person --> Copy Correct Prompt

Observed: the Correct button copies a prompt holding the node, file and lines, rule, code excerpt and violation, asking for a test-driven fix (`source/violation-prompt.ts`, `app.test.tsx` "should build a Correct prompt with the rule, excerpt, and violation message").

### (S) Agent --> Test Knowledge Graph Explorer On Session Files

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

# (E) Connect Sessions Across Channels And Apps

The chat bar, the CDD Kanban, the Story UI editor and the knowledge graph work on one ticket's session at a time, so each one opens the others on that ticket and shows what the others are doing. Validation moves into generate: the graph is rebuilt from what changed, its violations are read straight from it, and Fix is an action of its own. Every story here was requested on 2026-11-06 and none is built yet.

## (E) Connect Chat Bar Board And Story UI

### (S) Person --> Open Board Side Panel From Chat Bar

Requested (2026-11-06, "chat band -> board side panel"): the chat bar opens the active ticket's board card and tiles in a side panel beside the chat.

### (S) Chat Bar --> Sync Chat Bar With Board Selection

Requested (2026-11-06, "update chat band, eg selected stage, next action"; "and on the chat panel"; "and practices enabled for that session"): a ticket, stage or fidelity selected on the board becomes the chat bar's session, shown stage and selected fidelity, so the action button shows that fidelity's next action; the chat panel switches to that ticket's chat and the band shows the practices enabled for its session.

### (S) Chat Bar --> Keep Chosen Formats Across Actions In A Fidelity

Requested (2026-11-06, "have format saved across actions in fidelity"): the formats picked for a fidelity stay picked when the person switches between generate, render, sketch, iterate, document and fix, so each action writes the same formats without picking them again. Built today (checked 2026-11-10): format chips are kept per set of fidelities (`format-choices-client.ts:23,30`, commit 07c9026ee). Missing: the picks go back to the defaults after an action runs, and only generate and render take formats.

### (S) Person --> Start Ticket Session From Increment

Requested (2026-11-06, "increment could be a separate ticket/session in board"; "create a ticket on board on demand in backlog with proper naming reference to story map increment"): the Story UI editor's increments view offers Create ticket on each increment; pressing it adds a ticket to the board's backlog named after the story map and the increment, with its own session holding that increment's stories.

### (S) Board App --> Show Increment Ticket In Story UI

Requested (2026-11-06, "story UI -> board/chat integration"): an increment that has a ticket shows that ticket's stage and active state in the Story UI editor.

## (E) Check Work In Generate

### (S) Generate --> Refresh Graph After Generate

Requested (2026-11-06, "generate --> load refreshed graph based on changes immediately"): when generate writes a fidelity's files, the knowledge graph rebuilds those files at once, without a separate load or Validate run. Built today (checked 2026-11-10): generate tells the agent to call validate afterwards, and validate refreshes the graph (`generate.py:32-33`, `graph.py:1397`). Missing: generate refreshing the graph itself.

### (S) Knowledge Graph --> Attach Violations To Latest Graph

Observed (checked 2026-11-10): a refresh drops and re-reads the files, then `practices.check()` records each hit on its node (`harness/graph/graph_build.py:368-394`, `graph.py:1105,1131`), and violations are saved per node in graph.json (`saved_graph.py:134,153`); a refresh saves only the checked files' nodes, not the whole graph.json. Was: Requested (2026-11-06, "violations now attached to latest graph automatically"): each rebuilt node carries its graph-rule violations, so the latest graph is where every violation is read from.

### (S) Generate --> Judge Rules During Generate

Requested (2026-11-06, "judge validation must be part of generate, merge the two actions"): generate ends with the agent's rule-by-rule judgment of what it wrote, saved with the graph's hits, so a generate counts as generated and validated. Built today (checked 2026-11-10): generate ends by calling validate, which runs the AI judgment and saves it with the graph hits (`generate.py:32-36`, `validate.py:80`). Missing: one action; validate is still a separate call, log line, and board and chat bar action.

### (S) Agent --> Fix Graph Violations

Requested (2026-11-06, "/fix is a first class action; fix rule; file; default across all rules / files"): Fix is an action of its own: on one rule, on one file, or by default on every violation of every rule in every file, reading the violations from the latest graph.

### (S) Agent --> Validate Fidelity On Demand

Requested (2026-11-06, "validate still exists as independent action"; "validate is a slash command story only now"): Validate runs on its own on any files only as the `/actions-validate` slash command, and its report is saved as today; the board and the chat bar have no Validate, since generate judges the rules. Built today (checked 2026-11-10): `/actions-validate` runs and saves its report. Missing: validate is still on the board tiles (`action-bar-view.tsx:64-70`) and in the chat bar's stage actions.

### (S:system) Claude Code --> Check Graph Rules When An Artifact Changes

Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "Validate on save"): when an artifact in a session changes, the graph rules run on it and the band's violation count updates, with no explicit validate.

## (E) Read Graph Violations On Board

### (S) Board App --> Read Fidelity Violations From Latest Graph

Requested (2026-11-06, "default is to have a graph and just read the violations"): a tile's violation count and list come from the latest graph, not from the last validation report. Also Intended (`.sessions/_backlog/fully-integrated-app-flow.md` "better graph integration - load up front on session open, show all violations as a result of graph, no need for explicit run").

### (S) Person --> Generate And Judge Fidelity From Board

Requested (2026-11-06, "board and chat generate"): an expanded tile offers ▶ generate, which runs generate with its judgment on the ticket's enabled practices, and the tile shows the violations the refreshed graph holds. Built today (checked 2026-11-10): a tile's generate sends `/actions-generate`, which chains to validate. Missing: the tile's violations come from the report, not the refreshed graph.

### (S) Person --> Fix Graph Violations From Board

Requested (2026-11-06, "board and chat ... fix"): an expanded tile offers fix, and the Inspector offers Fix rule and Fix this one; each sends the Fix action for that scope, and with nothing picked it fixes every violation. Built today (checked 2026-11-10): the report panel has Fix per violation, Fix all per rule and Fix all violations (`report-rule-view.tsx:56,79`, `report-panel-view.tsx:71`), as prompts built from the report. Missing: Fix on the expanded tile, fed from the graph.

## (E) Read Graph Violations In Chat Bar

### (S) Chat Bar --> Read Session Violations From Latest Graph

Requested (2026-11-06, "default is to have a graph and just read the violations"): each fidelity dot's red count comes from the latest graph, not from the last validation report.

### (S) Person --> Generate And Judge Fidelity From Chat Bar

Requested (2026-11-06, "board and chat generate"): generate from the action button runs generate with its judgment, and the dots update from the refreshed graph. Built today (checked 2026-11-10): generate from the action button chains to validate. Missing: the dots update from the report, not the graph.

### (S) Person --> Fix Graph Violations From Chat Bar

Requested (2026-11-06, "board and chat ... fix"): Fix in the action picker sends the Fix action for the selected fidelity, a rule or a file, every violation by default.

## (E) Change Stories From Canvas And Story UI

Intended ([integrate-stories-with-the-canvas-explorer.md](../../../.sessions/_backlog/integrate-stories-with-the-canvas-explorer.md)): a person adds or changes a story from the canvas or from story-ui, or comments on one, and the map updates. Both paths send commands ("add story X under Y"), never a diff of the picture, and end in the same story code.

### (S:system) Design Canvas --> Give Each Map Card A Stable Node Id

Intended (integrate-stories-with-the-canvas-explorer.md slice 2): each card drawn by `box()` and each explorer entry carries a `data-node` derived from the story path, which every comment and command below names.

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

---

## Scope boundary

**In scope:** Authoring an Agent Toolset with `@agent_tool` and `@agent_instructions`. Installing that toolset as two writes — File Installation publishes skill, slash command, and rules as one story (same channel, same write) and Mcp Installation publishes `mcp.json` — then invoking the skill, slash command, and MCP tool and prompt. Installed rules are not invoked as a file check — they constrain valid output. Context Guidance is installed the same way (skill and `.mdc` rules), invoked so `instructions` come back, then used to generate content those rules constrain. Practice Guidance is that same Guidance plus registered fidelities — invoke at practice scope and at fidelity scope; shared rules and fidelity-specific rules each constrain the matching AI output. Hook dispatch; extracting co-located markdown via `@markdown`; the CDD Kanban and the Chat Bar as two channels that move a ticket's session through its practices, each with its own stories; the practice content editor apps those channels invoke (Story UI, design canvas, Graph app), with each app's own story map; connecting sessions across the channels and apps, which joins the channels and apps on one ticket, and validation read from the latest graph; every host-action kit from `actions/.context/module-context.md` (`partition`, `grill`, `sketch`, `iterate`, `generate`, `document`, `render`, `satisfy`, `validate`, `scan`, `repair`, `createRule`).

**Out of scope:** Catalog HTML pages; on the Chat Bar, the board's whole-board views (columns, Backlog items, WIP limits, side panels, ticket hierarchy) and sending one action to a whole stage (CDR 0001); one-time renames and repository moves; YAML manifest CLI / `tools.ps1` invoke; inventing extra practices or product domains beyond this framework spine; scenario and acceptance-test text (later fidelities).
