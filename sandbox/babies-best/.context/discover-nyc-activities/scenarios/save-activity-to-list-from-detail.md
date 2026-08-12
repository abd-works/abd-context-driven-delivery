---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

## Story: Save Activity To List From Detail

**Sources / context:** .context/babies-best-sketch.md (Save Activity To List From Detail); thin-slice (handoff to Lists)

### Scenario: Save hands off to list picker

*Given* **Activity Detail** open  
*And* at least one **PersonalList** exists  
*When* the **Parent** saves the **Activity** to a list  
*Then* that **Activity** appears on the chosen list  

### Variation: No list yet

*Given* **Activity Detail** open  
*And* the **Parent** has no **PersonalList**  
*When* the **Parent** chooses Save to list  
*Then* the app prompts to create a list (Curate Personal Lists) before saving  
