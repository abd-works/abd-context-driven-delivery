---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Filter Activities By Kind

**Sources / context:** .context/babies-best-sketch.md (Filter Activities By Kind)

### Scenario: Evergreen vs dated event can be narrowed

*Given* mixed evergreen and dated **Activities** in the catalog  
*When* the **Parent** filters kind = Events  
*Then* only dated-event **Activities** remain listed  
