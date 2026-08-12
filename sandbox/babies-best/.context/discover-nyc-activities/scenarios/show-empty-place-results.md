---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Show Empty Place Results

**Sources / context:** .context/babies-best-sketch.md (empty place / no matches)

### Scenario: No matches message when place and filters yield nothing

*Given* **PlaceFilter** = Staten Island / Tottenville with citywide off  
*And* no **Activities** match the active age band in that place  
*When* the **Parent** views the **Activities Catalog**  
*Then* no **Activity** rows are listed  
*And* an empty-place message is shown  
