---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Reorder Route Zones

### Scenario: Reorder kept when it shortens driver path

*Given* a **Delivery Route** with **Zones** *North*, *East*, *West*  
  *And* a shorter path exists as *North*, *West*, *East*  
*When* the **Dispatcher** reorders zones to *North*, *West*, *East*  
*Then* **Zone order** is *North*, *West*, *East*  
  *And* **Route path** matches the shorter sequence  
