# Module build order — plan and swarm utilities (ticket 23)

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` (ticks 14–33); `utilities/git/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`; `utilities/workflow/.context/module-context.md`; `utilities/plan/.context/module-context.md`

**Fidelity:** modules  
**Session:** `plan-and-swarm-flow-boards`  
**Rule:** one-way deps only. Cycles are a hard fail. Git is the store; Plan/Swarm/Workflow are front-ends. Workflow = states on its own Project; Plan = that flow + tickets; no planned-turn list.

## Order

| # | Module | Depends on (one-way) | Notes |
|---|--------|----------------------|-------|
| 1 | `git` | *(none among this work)* | Store: inbox Project 1 + one Project per Workflow; issues. |
| 2 | `workspace` | `git` | Working folder (not Repo). WorkSession + Turn (created on state enter). |
| 3 | `cli_agent` | `workspace` | Worker + doer-judge for Plan/Swarm Agents. |
| 4 | `workflow` | `git`, `workspace` | One Project per flow; `workflow/flows/*.yaml` behavior; kit+board. |
| 5 | `plan` | `workspace`, `workflow`, `git` | Flow + tickets; `/start-ticket` / `/finish-plan`; FIFO + batch. |
| 6 | `swarm` | `plan`, `cli_agent` | Front-end; Agent is CliAgent; compare reads Turn judge. |

## Layers (summary)

```
0  git | workspace | cli_agent | workflow
1  plan
2  swarm
```

## Graph (edges only)

```
git
workspace -> git
cli_agent -> workspace
workflow -> git, workspace
plan -> workspace, workflow, git
swarm -> plan, cli_agent
```
