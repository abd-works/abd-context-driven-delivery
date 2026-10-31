# Session board: every session is a ticket on a kanban

## Goal

A kanban board beside the chat that shows where every piece of work is in the CDD flow, discovery → specification → implementation across Stories, DDD, UX, Clean Engineering, and BDD, with no agent keeping it up to date.

Each CDD session is a ticket. The board is computed from files the harness already writes. A Claude Code mod draws it; any other IDE or page can read the same data.

## Where this comes from

`abd-works/abd-skills` → `practices/kanban/`:

- `skills/abd-kanban-planning` picks a delivery strategy from a catalog (bug fix, new thin slice, spike, legacy migration, brownfield, regulatory-heavy, and others) and writes `kanban.json`, the system of work: stages, the scope level per stage, and each stage's ordered skills. Rules check the plan, for example "checkpoint density matches risk" and "plan is not the default six-stage".
- `apps/abd-delivery-agent-kanban` is the "War room Kanban" web app (MERN, Playwright e2e, full domain model and story map). Columns Backlog → Shaping → Discovery → Exploration → Specification → Engineering, each split into In Progress and Done. A ticket's position is derived from its skill progress; the app only reads `board.json`, `kanban.json`, and ticket files. A ticket scatters into child tickets when the next stage works at a finer scope.
- Also: `abd-kanban`, `abd-kanban-repo`, `abd-kanban-handoff`, `kanban-estimation`, and the role agents (kanban-lead, product-owner, business-expert, ux-designer, engineer).

In this repo, the same idea appeared as a `kanban` context tool (Kanban Lead routing items through practice agents, `cdd_guidance/agents/dont use yet/kanban-lead.md` is what remains), then as `tools/workflow` on GitHub Issues and Projects, with `tools/cli_agent` and `tools/swarm` spawning CLI agents. Those are retired in `.retired/` (commit `c1396af`).

### What made it too complex

Agents ran the bookkeeping. The Kanban Lead owned the board and ran `sync_kanban_board.py` after every event; an agent pool of executor/reviewer pairs with WIP limits, Cursor SDK sessions, heartbeats, output streams, and restart-from-slot checklists sat behind every move; the board app lived in a separate codebase. State drifted and failures were hard to see.

### What to keep

- A system of work chosen by strategy, with stages and the skills each requires.
- Board position derived from skill progress, never stored.
- A ticket waits in a stage's Done until it is pulled into the next stage.
- Scatter into child tickets with lineage when scope gets finer.
- A read-only board over files on disk; Executive and Engineering views.

## How it maps onto the harness

| abd-skills kanban | CDD harness |
|---|---|
| `kanban.json` system of work | The same, in CDD terms: stages are Discovery, Specification, Implementation; a stage's required work is a list of practice@fidelity (Discovery = `stories-story_map`, `ddd-bounded_context`, `ux-ia`, `ce-modules`) |
| Strategy catalog and planning rules | A thin `kanban` context tool: strategies and rules as practice guidance, so `/kanban /sketch` picks a strategy and `/kanban /validate` checks the plan |
| Ticket | A CDD session, `.sessions/<name>/` |
| Skill progress | Read from `session.log` and graph validation |
| Reviewer agents | Review is the practice rules: a skill is reviewed when `/validate` passes on it |
| Scatter | `/ticket split` creates child sessions from the story map's nodes |
| War room web app | A board pane mod beside the chat |
| Executive view | A shareable page generated from the same board data by the catalog generator |
| Agent pool, SDK sessions, heartbeats | Dropped. You, or Claude in your session, pull the next card. Optional later: a card starts a cloud session in the `abd-cdd` environment |

## Plan

### 1. System of work: a thin `kanban` context tool

Port `kanban.json`, the strategy catalog, and the planning rules from `abd-skills/practices/kanban/skills/abd-kanban-planning` as practice guidance. The output names stages and each stage's required practice@fidelity list.

### 2. Session as ticket, and `board()`

**Ticket fields.** `session.json` gains only what cannot be derived:

```json
{
  "name": "pet-visits",
  "workpath": "C:/dev/abd-pet-store-demo",
  "repo_path": "C:/dev/abd-context-driven-delivery",
  "title": "Pet visits",
  "scope": "feature",
  "parent": "pawplace"
}
```

Branch or worktree, handoffs, and decisions already belong to the session.

**Skill progress from `session.log`.** Action lines already name what was written and which practice and fidelity did it: paths first, then `practice fidelity [format]`:

```
2026-10-22T21:31:22Z render C:\Users\jeffa, C:\dev\…\practices\stories stories story_map markdown …
2026-10-26T15:11:35Z render C:\dev\abd-context-driven-delivery clean_engineering model python …
2026-10-26T20:54:20Z tool ux-mockup
2026-10-20T21:54:14Z validate Stories story_map <violations…>
```

Generate and sketch always run with a practice, so every action line carries one. Paths can hold spaces and commas, so the reader looks for a known practice and fidelity pair in each line, using the names the harness defines, rather than splitting by position. No log format change.

| Skill state | Rule |
|---|---|
| not started | no line names it |
| in progress | it ran, but its latest `validate` has violations or has not happened |
| reviewed | its latest `validate` passed with no violations |

**Board position.** Against the system of work from step 1, or this default when there is none:

| Stage | Required (default) |
|---|---|
| Discovery | stories-story_map, ddd-bounded_context, ux-ia, ce-modules |
| Specification | stories-scenarios, ddd-model, ux-mockup, ce-model, bdd-behavior |
| Implementation | stories-acceptance_tests, ddd-tactics, ux-front_end_code, ce-code, bdd-development |

- **Backlog:** nothing logged yet.
- **In progress:** the first stage whose required skills are not all reviewed.
- **Stage Done:** every required skill in the stage is reviewed; the card waits until it is pulled.
- **Complete:** the session is in `.sessions/closed/`.

**What `board()` returns:**

```json
{
  "stages": ["Discovery", "Specification", "Implementation"],
  "active": "pet-visits",
  "tickets": [
    {
      "name": "pet-visits", "title": "Pet visits", "scope": "feature", "parent": "pawplace",
      "column": "Specification", "status": "in_progress",
      "branch": "session/pet-visits", "last_activity": "2026-10-26T21:51:13Z",
      "skills": {
        "stories-scenarios": "reviewed",
        "ux-mockup": "in_progress",
        "ddd-model": "not_started"
      },
      "next": "ddd-model",
      "handoff": ".sessions/pet-visits/handoff-20261026T2150.md"
    }
  ]
}
```

`next` is the first required skill in the card's stage that is not yet reviewed.

**Operations,** in `space/session`, annotated like the other operations so every IDE gets them as MCP tools and slash commands:

| Operation | Does |
|---|---|
| `board()` | Returns the JSON above. Reads files only. |
| `new(name, title, scope, parent)` | The existing `new`, with the ticket fields; opens the branch as today |
| `pull(name)` | Moves a card from a stage's Done into the next stage by logging `pull <stage>` |
| `switch`, `close` | Already exist: switch makes a card active; close makes it Complete |

### 3. The mod

A Claude Code mod that only draws and reacts; all logic stays in Python behind the `cdd` MCP server.

- **Board pane** beside the chat: stage columns with In Progress and Done, cards showing their practice × fidelity progress. Buttons: Pull, Split, Switch to, Handoff, Close.
- **Live updates:** a hook on every `cdd` tool call refreshes the active card, with a toast when a stage's required skills are all reviewed.
- **Status line:** ticket · stage · next required skill.
- **Context:** each prompt carries the active ticket, its stage, and its next required skill.
- **Handoff** on compaction and session end.
- **Commands:** `/board`, `/ticket new | split | pull`.

Panes are boxes, text, and buttons: no drag and drop. Cards move by button.

### 4. Later

- Scatter from the story map: `/ticket split` turns story map nodes into child sessions with lineage.
- The Executive view as a generated, shareable page.
- Optional: a card starts its next step as a cloud session in the `abd-cdd` environment.

## Rules this design keeps

1. Files are the source of truth. Status is computed, not stored.
2. No agent in the bookkeeping loop. Every state change comes from a real action: generate, validate, pull, close.
3. GitHub is optional, at most a one-way mirror.
4. One `board()` feeds every view: the pane, the status line, the executive page, other IDEs.

## Related mods

Ideas from the same review, each a thin mod over the harness:

- **Live rule guard:** on every Edit or Write to a file a practice's rules cover, validate that file and show violations above the prompt and to the model.
- **Command grammar:** autocomplete and run `/stories /sketch /discovery` as one command.
- **Session context:** the active session's practice, fidelity, context roots, and latest handoff added to the system prompt.
- **Grill and iterate band:** the current question, slices agreed, quick answers.
- **Transformation pane:** an artifact's markdown, draw.io, and Claude Design canvas forms side by side, with render and sync buttons.
