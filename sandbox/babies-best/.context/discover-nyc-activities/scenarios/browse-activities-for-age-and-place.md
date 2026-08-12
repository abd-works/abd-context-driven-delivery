---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Browse Activities For Age And Place

**Sources / context:** .context/babies-best-sketch.md (Browse Activities For Age And Place); grill-answers (profile age + remember last place)

### Scenario: Catalog opens with profile age and last remembered place

*Given* a **Parent** with **BabyProfile**.ageBand = `6-12 months`  
*And* last **PlaceFilter** = Brooklyn / Park Slope with citywide off  
*And* **Activities** for Park Slope playground + citywide museum  
*When* the **Parent** opens Things to Do  
*Then* **PlaceFilter** restores Brooklyn / Park Slope  
*And* **Activities** matching `6-12 months` in that place scope are listed  
*And* each row shows name, kind (`evergreen`|`event`), place label, age band  
