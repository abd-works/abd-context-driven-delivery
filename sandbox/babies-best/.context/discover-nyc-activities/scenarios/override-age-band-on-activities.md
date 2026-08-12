---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Override Age Band On Activities

**Sources / context:** .context/babies-best-sketch.md (Override Age Band On Activities)

### Scenario: Manual age filter overrides profile default for this browse

*Given* **BabyProfile**.ageBand = `0-3 months`  
*And* filter currently following profile  
*When* the **Parent** sets age filter to `12-18 months`  
*Then* listed **Activities** match `12-18 months`  
*And* **BabyProfile**.ageBand is unchanged  
