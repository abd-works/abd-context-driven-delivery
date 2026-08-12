---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Unassign Package From Stop

### Scenario: Package removed from stop on the route

*Given* **Package** *P-100* hung on **Stop** *Dock-9* on a **Delivery Route**  
*When* the **Dispatcher** unassigns **Package** *P-100* from **Stop** *Dock-9*  
*Then* **Package** *P-100* is not hung on *Dock-9* for that **Delivery Route**  
