---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Manage Turns

**Story type:** user

**Actor:** Practitioner (operator composing the **Plan**)

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` ticks 8 and 13; `utilities/workspace/.context/module-context.md` (`Turn`, `tool_keys`, `toolCalls`); `utilities/plan/.context/module-context.md`

### Domain terms

- *Plan* — associated with a **Workspace**; holds ordered **Turn**s
- *Turn* — existing `workspace.Turn`; one **action**; multiple tools via **tool_keys** and **toolCalls**; **TicketState** Backlog / In Progress / Done
- *ToolCall* — one toolset invoke on a **Turn**
- *CliAgent* — binds a hanging **Turn** (`action`, `tool_keys`, `toolCalls`); no **Plan** on **CliAgent**

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario: Turn holds multiple tools and one action

*Given* a **Plan** *compose judged plan* associated with a **Workspace**  
*When* the operator adds a **Turn**  
    with action *Sketch*  
    tool_keys *stories* and *clean_engineering*  
    and a **ToolCall** toolset *Stories* name *Sketch*  
    and a **ToolCall** toolset *CleanEngineering* name *Sketch*  
*Then* that **Turn** action is *Sketch*  
  *And* that **Turn** holds both **ToolCall**s  
  *And* that **Turn** **TicketState** is *Backlog*

### Scenario: CliAgent binds the hanging Turn

*Given* a hanging **Turn** with action *Sketch*  
  *And* that **Turn** tool_keys are *stories* and *clean_engineering*  
  *And* that **Turn** holds **ToolCall**s for *Stories* and *CleanEngineering*  
*When* a **CliAgent** binds that **Turn**  
*Then* that **CliAgent** runs that **Turn** action with those tool_keys and **ToolCall**s  
  *And* that **CliAgent** does not hold a **Plan**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Turn holds multiple tools and one action | grill-answers.md | tick 13 |
| CliAgent binds the hanging Turn | grill-answers.md | tick 13; workspace.Turn tool_keys |
