---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Open Dated Event Detail

**Sources / context:** .context/babies-best-sketch.md (Open Dated Event Detail)

### Scenario: Event shows when it happens

*Given* dated **Activity** "Library Story Time" with eventDate this Saturday  
*When* the **Parent** opens that **Activity**  
*Then* detail shows name, age band, place, eventDate, eventTime  
*And* kind = event  
