---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Filter By Borough Then Neighborhood

**Sources / context:** .context/babies-best-sketch.md (Filter By Borough Then Neighborhood); CDR 0001

### Scenario: Place narrows from borough to neighborhood

*Given* **Activities Catalog** showing Brooklyn results  
*And* **Neighborhood** Park Slope has **Activities**  
*When* the **Parent** selects **Borough** Brooklyn then **Neighborhood** Park Slope  
*Then* only Park Slope **Activities** (plus citywide if included) are listed  
*And* the place filter shows Brooklyn / Park Slope  
