---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Include Citywide Activities

**Sources / context:** .context/babies-best-sketch.md (Include Citywide Activities)

### Scenario: Citywide sits beside neighborhood results when toggled on

*Given* place filter = Brooklyn / Park Slope  
*And* a citywide **Activity** "Baby Music Festival" exists  
*When* the **Parent** turns citywide on  
*Then* Park Slope **Activities** and citywide **Activities** appear together  
