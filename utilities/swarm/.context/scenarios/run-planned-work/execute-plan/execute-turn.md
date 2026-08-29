---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Execute Turn

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/story-map.md`; `utilities/swarm/.context/grill-answers.md` ticks 15–16, 22; `utilities/workspace/.context/module-context.md`

### Domain terms

- *Turn* — one ticket going through one flow state; created when the ticket enters that state; work + commit
- *State behavior* — tools / one action / utilities / prose from `workflow/flows/{name}.yaml` for that state

## Behaviors

### Scenario: Entering a state runs that state’s behavior on the Turn

*Given* **Ticket** *#14* just entered state *Fix* on **Project** *small-work-board*  
  *And* that state yaml lists action *generate* and tool *Bdd*  
*When* the CLI opens the hanging **Turn** and runs that action  
*Then* that **Turn** runs *Bdd* with action *generate*  
  *And* finishing the **Turn** commits the work for **Ticket** *#14* in state *Fix*

### Scenario: CliAgent does not open the Turn

*Given* a hanging **Turn** for **Ticket** *#14* in state *Fix*  
*When* **CliAgent** describes that **Turn**  
*Then* **CliAgent** shows the action and tool_keys from the state yaml  
  *And* **CliAgent** does not open that **Turn**  
  *And* the CLI opens and finishes it

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Entering a state runs that state’s behavior on the Turn | grill-answers.md | ticks 15–16, 22 |
| CliAgent does not open the Turn | grill-answers.md | tick 13 |
