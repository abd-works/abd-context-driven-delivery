---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Choose Place On First Visit

**Sources / context:** .context/babies-best-sketch.md (Choose Place On First Visit); grill-answers (remember last; first visit choose place)

### Scenario: No remembered place means pick borough before results

*Given* a **Parent** with no remembered **PlaceFilter**  
*When* the **Parent** opens Things to Do  
*Then* the catalog prompts for borough (then neighborhood)  
*And* no **Activity** rows are listed until place is chosen  
