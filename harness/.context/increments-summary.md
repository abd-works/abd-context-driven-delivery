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

The starting line, not a slice to build: everything the framework, the Session Board and the Chat Bar do now. It covers registering and installing toolsets, guidance and hooks; the practice actions (partition, grill, sketch, generate, render, validate, satisfy, repair, review); the board's tickets, stages, fidelity tiles, files and server health; the chat bar's session strip and fidelity actions; the Story UI editor; the design canvas and its versions; and the knowledge graph with its filters, overlays and rule checks.

## 1. Maintain Tickets On Board — 11 stories

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
