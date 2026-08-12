---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Assign Package To Stop

### Scenario: Package hangs only on a stop already on the route

*Given* a **Delivery Route** that enters **Zone** *North*  
  *And* **Stop** *Dock-9* falls in *North*  
  *And* **Package** *P-100* at *Dock-9* is unassigned  
*When* the **Dispatcher** assigns **Package** *P-100* to **Stop** *Dock-9*  
*Then* **Package** *P-100* is hung on *Dock-9* for that **Delivery Route**  
