---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Recalculate Route Path

### Scenario: Adjacent zones trigger shorter-path improvement

*Given* a **Delivery Route** with zone order *East*, *North*, *West*  
  *And* *North* is adjacent to *West* such that *North*, *West*, *East* is shorter  
*When* the **Dispatcher** recalculates the **Route path**  
*Then* **Route path** uses the shorter zone sequence  
  *And* **Zone order** reflects that sequence  
