---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Remove Zone From Route

### Scenario: Removing zone drops its stops from the route

*Given* a **Delivery Route** that enters **Zones** *North*, *West*  
  *And* **Stop** *Dock-9* falls in *West*  
*When* the **Dispatcher** removes **Zone** *West*  
*Then* *West* is not on the **Delivery Route**  
  *And* *Dock-9* is not on the **Delivery Route**  
  *And* the **Route path** is recalculated  
