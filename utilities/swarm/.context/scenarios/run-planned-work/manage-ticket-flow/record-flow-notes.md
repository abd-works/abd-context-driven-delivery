---
fidelity: [specification]
artifact: [story-scenarios]
format: md
---

## Story: Record Flow Notes

**Story type:** user

**Actor:** Practitioner

**Sources / context:** `utilities/swarm/.context/plan-and-swarm-sketch.md`; `utilities/git/.context/module-context.md`

### Domain terms

- *Ticket* — keyed by GitHub issue number; notes via **Repo.note** / **Repo.readNotes**
- *Repo* — OO git + GitHub domain; notes are git-primary

## Behaviors

### Scenario: Flow notes live on the existing Ticket

*Given* a **Repo** with a **Ticket** number *23*  
*When* the operator records a flow note that *Start Plan opened a WorkSession*  
*Then* **Repo.readNotes** for that **Ticket** show that *Start Plan opened a WorkSession*  
  *And* that **Ticket** number is still *23*

### Scenario: A later flow note stays with the earlier note

*Given* that **Ticket** already has the *Start Plan* note  
*When* the operator records a flow note that *Execute Turn holds result*  
*Then* **Repo.readNotes** show both notes  
  *And* that **Ticket** number is still *23*

### Evidence

| Scenario | Source | Location |
| --- | --- | --- |
| Flow notes live on the existing Ticket | plan-and-swarm-sketch.md | Manage Ticket Flow / Record Flow Notes |
| A later flow note stays with the earlier note | plan-and-swarm-sketch.md | Manage Ticket Flow / Record Flow Notes |
