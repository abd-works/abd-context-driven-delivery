# Module build order — plan and swarm utilities (ticket 23)

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/git/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/cli_agent/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

**Fidelity:** modules  
**Session:** `plan-and-swarm-utilities-23`  
**Rule:** one-way deps only. Cycles are a hard fail. **Workflow** consumes **git**; it is not a dependency of **plan** or **swarm**. Git is the store; Plan/Swarm/Workflow are front-ends.

## Order

| # | Module | Depends on (one-way) | Notes |
|---|--------|----------------------|-------|
| 1 | `git` | *(none among this work)* | Store: Ticket/Project columns, issues. |
| 2 | `workspace` | `git` | Working folder (not Repo). WorkSession + Turn. |
| 3 | `cli_agent` | `workspace` | Worker + doer-judge for Plan/Swarm Agents. |
| 4 | `plan` | `workspace`, `git` | Front-end; Turn.state → Project columns; JudgeCheckpoint on Turn. |
| 5 | `swarm` | `plan`, `cli_agent` | Front-end; Agent is CliAgent; compare reads Turn judge results. |
| 6 | `workflow` | `git`, `workspace` | Front-end; backlog/start/finish columns. |

## Layers (summary)

```
0  git | workspace | cli_agent
1  plan | workflow
2  swarm
```

## Graph (edges only)

```
git
workspace -> git
cli_agent -> workspace
plan -> workspace, git
workflow -> git, workspace
swarm -> plan, cli_agent
```
