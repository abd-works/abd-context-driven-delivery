---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Move Package Between Stops

### Scenario: Move only between stops on the same route

*Given* **Package** *P-100* on **Stop** *Dock-9* on the **Delivery Route**  
  *And* **Stop** *Dock-12* also on the **Delivery Route**  
*When* the **Dispatcher** moves *P-100* to *Dock-12*  
*Then* *P-100* hangs on *Dock-12*  
  *And* *Dock-9* no longer holds *P-100* for that **Delivery Route**  
