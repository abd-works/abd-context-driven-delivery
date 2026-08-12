---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: View Route Path

### Scenario: Dispatcher sees calculated path for the route

*Given* a **Delivery Route** that enters ordered **Zones** *North*, *West*, *East*  
  *And* the **Route path** has been calculated  
*When* the **Dispatcher** views the **Route path**  
*Then* the **Route path** shows the zone sequence used for the driver  
