---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Open Evergreen Activity Detail

**Sources / context:** .context/babies-best-sketch.md (Open Evergreen Activity Detail)

### Scenario: Standing place shows hours and notes, not a single date

*Given* evergreen **Activity** "Carroll Park Playground" in Park Slope  
*When* the **Parent** opens that **Activity**  
*Then* detail shows name, age band, neighborhood (and its borough), hours, notes  
*And* kind = evergreen  
