---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Manage Turns

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md` ticks 8, 13; `utilities/workspace/.context/module-context.md`

### Domain terms

- *Plan* — associated with a **Workspace**; holds ordered **Turn**s
- *Turn* — existing `workspace.Turn`; one **action**; multiple tools via **tool_keys** and **toolCalls**; **TicketState** Backlog / In Progress / Done
- *ToolCall* — one toolset and name recorded on a **Turn**
- *CliAgent* — describes hanging **Turn** shape (`action`, `tool_keys`, `toolCalls`); does not open the **Turn**; holds no **Plan**
- *TicketState* — Backlog / In Progress / Done on **Turn** and **Ticket**

> In steps: bold domain concepts (`**<Concept>**`); italic concrete values (`*<value>*`).

## Behaviors

### Scenario: Turn holds multiple tools and one action

*Given* a **Plan** *compose-judged-plan* associated with a **Workspace**  
*When* the operator adds a **Turn**  
    with action *Sketch*  
    and **tool_keys** *Stories* and *CleanEngineering*  
    and a **ToolCall** toolset *Stories* name *Sketch*  
    and a **ToolCall** toolset *CleanEngineering* name *Sketch*  
*Then* that **Turn** action is *Sketch*  
  *And* that **Turn** holds both **ToolCall**s  
  *And* that **Turn** **TicketState** is *Backlog*

### Scenario: CliAgent describes the Turn shape without opening it

*Given* a hanging **Turn** with action *Sketch*  
  *And* **tool_keys** *Stories* and *CleanEngineering*  
  *And* **toolCalls** for *Stories* *Sketch* and *CleanEngineering* *Sketch*  
*When* **CliAgent** describes that **Turn**  
*Then* **CliAgent** shows action *Sketch*  
  *And* **CliAgent** shows those **tool_keys**  
  *And* **CliAgent** shows those **toolCalls**  
  *And* **CliAgent** does not open that **Turn**  
  *And* **CliAgent** holds no **Plan**

### Scenario: CLI opens and finishes the hanging Turn

*Given* that hanging **Turn** with action *Sketch*  
*When* the CLI opens that **Turn**  
  *And* runs *Sketch* with *Stories* and *CleanEngineering*  
  *And* finishes that **Turn**  
*Then* that **Turn** holds result  
  *And* that **Turn** still uses **TicketState**  
  *And* that **Turn** may still hold **HILCheck** and **JudgeCheckpoint**

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Turn holds multiple tools and one action | grill-answers.md | tick 13 |
| CliAgent describes the Turn shape without opening it | grill-answers.md | tick 13 |
| CLI opens and finishes the hanging Turn | grill-answers.md | tick 13 |
