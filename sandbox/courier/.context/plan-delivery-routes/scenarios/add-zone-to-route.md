---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Add Zone To Route

### Scenario: Zone added recalculates path from order then shorter check

*Given* a **Delivery Route** with ordered **Zones** *North*, *East*  
  *And* **Zone** *West* adjacent to **Zone** *North*  
  *And* **Stops** in *West* from prior package intake  
*When* the **Dispatcher** adds **Zone** *West* to the **Delivery Route**  
*Then* **Delivery Route** zones include *West* in order  
  *And* **Stops** that fall in *West* appear on the **Delivery Route**  
  *And* the **Route path** is calculated from zone order then shorter-path check  
