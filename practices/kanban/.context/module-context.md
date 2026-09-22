# Kanban

**Purpose:** Orchestrate other practice agents through a simple backlog. The *Kanban Lead* does not write stories, designs, models, tests, or code — it carves the ask into items and passes each item to the agents that must act on it, in order.

**Primary use case:** Given a prompt, set up a backlog, route each item through the right agents as separate sessions, and move items from next to in progress to done.

**Rationale:** Discovery, specification, and implementation stay on the practice that owns them. One orchestrator keeps that order honest; if the lead also produces artifacts, the other agents never own the work.

## Seam

`Kanban Lead` is the seam: understand the ask, carve the backlog the way the prompt says, launch one agent role per session, and track progress.

Constraint: never combine multiple roles in one agent session. Constraint: follow the prompt for how to carve and which flow to use — do not impose a fixed process when the prompt already names one.

## Public API

- Agent instructions: `practices/kanban/agents/kanban-lead.md`
- Typical route: Stories (`story-writer`) → UX (`ux-designer`) → DDD (`domain-designer`) → Clean Engineering (`engineer`) → BDD (`behavior-developer`)

## Dependencies

Stories, UX, DDD, Clean Engineering, and BDD agents. One-way: Kanban launches those agents; they do not import Kanban.
