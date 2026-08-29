# Module build order — plan and swarm utilities (ticket 23)

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/git/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`; `utilities/workflow/.context/module-context.md`; `utilities/plan/.context/module-context.md`

**Fidelity:** modules  
**Session:** `plan-and-swarm-utilities-23`  
**Rule:** one-way deps only. Cycles are a hard fail. Git is the store; Plan/Swarm/Workflow are front-ends. Plan is based on Workflow.

## Order

| # | Module | Depends on (one-way) | Notes |
|---|--------|----------------------|-------|
| 1 | `git` | *(none among this work)* | Store: Ticket/Project columns, issues. |
| 2 | `workspace` | `git` | Working folder (not Repo). WorkSession + Turn. |
| 3 | `cli_agent` | `workspace` | Worker + doer-judge for Plan/Swarm Agents. |
| 4 | `workflow` | `git`, `workspace` | Front-end; named/reusable; small-work prebaked for Plan. |
| 5 | `plan` | `workspace`, `workflow`, `git` | Based on Workflow; `/plan /small-work` loads recipe. |
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
