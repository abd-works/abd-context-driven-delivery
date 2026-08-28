# Ticket 23 — Plan and Swarm utility packages

**Issue:** [#23](https://github.com/abd-works/abd-context-driven-delivery/issues/23)

GitHub CLI was not on PATH and GitKraken was unsigned-in when this session opened. The body below is the operator ask captured in chat — treat it as the source requirements. Do not invent extra product behavior.

## Two utility packages

### 1. plan

Define a sequence of **context tool**, **action**, **fidelity**, and **context** as **ordered steps**.

Steps may include:

- **AI judge** checkpoints
- **HIP** (human-in-process) checkpoints

### 2. Enhance current git / GitHub issue API

Enhance the current API on **git repo issues / project states** (and related surfaces) so it can manage **all state and flow**: research tags, notes, and similar ticket/session flow metadata.

Existing seam: `utilities/git` — `Repo`, `Branch`, `Commit`, `Project`, `Ticket`, `TicketState`. Today tickets carry number/title/body/url/state plus an open `data` map; notes exist for eval-mistakes; project states are Backlog / In Progress / Done. The ask is to manage **research tags, notes, and flow state** on that API — not a second parallel store.

### 3. swarm

Run a **plan** (or selected **steps** of a plan) with **multiple sub-agents**.

Each sub-agent must have something unique called out as a **first-order concept / hypothesis**, then run. Results are **compared** to the other agents using a **Supervisor / Swarm** pattern:

- **Swarm** is a collection of agents
- Each agent gets the **plan** and its **unique context** (the first-order concept / hypothesis)
- **Supervisor** can have its **own rubric**, or evaluate **one or more judge rubrics from the plan**

Existing related seams: `utilities/sub_agent` (`@sub_agent`, non-blocking launch); `agent_bdd` `ai_judge`; workflow/git ticket + project status.

## Out of scope unless the source later says so

- New slash-command product UX beyond what existing kits already do
- Invented kanban columns or status badges
- A second ticket identity besides GitHub issue `#`
- Implementing production code in this generate turn (modules + story_map only)
