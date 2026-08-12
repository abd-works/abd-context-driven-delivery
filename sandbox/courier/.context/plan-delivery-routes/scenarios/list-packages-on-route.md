---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: List Packages On Route

### Scenario: Packages listed for stops on the route

*Given* a **Delivery Route** that enters **Zone** *North*  
  *And* **Package** *P-100* hung on **Stop** *Dock-9* on the route  
*When* the **Dispatcher** lists packages on the **Delivery Route**  
*Then* **Package** *P-100* is shown for **Stop** *Dock-9*  
