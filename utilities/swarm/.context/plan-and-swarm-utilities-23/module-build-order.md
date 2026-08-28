# Module build order — plan and swarm utilities (ticket 23)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md`; `utilities/git/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/sub_agent/.context/module-context.md`; `utilities/workflow/.context/module-context.md`

**Fidelity:** modules  
**Session:** `plan-and-swarm-utilities-23` at `utilities/swarm/.context/plan-and-swarm-utilities-23/`  
**Rule:** one-way deps only. Cycles are a hard fail. **Workflow** consumes **git**; it is not a dependency of **plan** or **swarm**.

## Order

| # | Module | Depends on (one-way) | Notes |
|---|--------|----------------------|-------|
| 1 | `git` | *(none among this work)* | Existing. Research tags, notes, flow on Ticket/Project. |
| 2 | `workspace` | *(existing)* | WorkSession + actual Turn. Plan starts a WorkSession. |
| 3 | `sub_agent` | *(none among this work)* | Existing launch seam reused by swarm. |
| 4 | `plan` | `workspace` | Plan holds Turns; Turn.state is TicketState; optional JudgeCheckpoint / HILCheck on a Turn. |
| 5 | `swarm` | `plan`, `sub_agent` | Supervisor Outcome + Agent Hypothesis; slice is Turns. |

## Layers (summary)

```
0  git | workspace | sub_agent
1  plan
2  swarm
```

## Graph (edges only)

```
git
workspace
sub_agent
plan -> workspace
swarm -> plan, sub_agent
```
