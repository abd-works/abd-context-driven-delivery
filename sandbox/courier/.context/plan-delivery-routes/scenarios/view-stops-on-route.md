---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: View Stops On Route

### Scenario: Stops listed are only those in entered zones

*Given* a **Delivery Route** that enters **Zone** *North*  
  *And* **Stop** *A* falls in *North*  
  *And* **Stop** *B* falls in *East*  
*When* the **Dispatcher** views stops on the **Delivery Route**  
*Then* **Stop** *A* is listed  
  *But* **Stop** *B* is not listed  
