# Skill Errors Log — abd-story-acceptance-criteria

---

### Domain terms used in AC without backing in domain model artifacts

- **Context:** `acceptance-criteria.md` generation for Increment 1 (Hero Virtual Tabletop)
- **DO / DO NOT:** DO look up every candidate term in the project's domain model artifacts (Domain Language, domain model, domain specification) before listing it in a story's Domain terms section. If a term is absent from all artifacts, add it to `domain-terms.md` in the deliverables folder first. DO NOT invent or define terms inline that have no backing outside the AC file.
- **Example (wrong):** 28 terms listed in story Domain terms sections (e.g. *COH Game Directory*, *Prism Shell*, *Clipboard*, *Crowd Tree*, *Settings*) had no entry in `domain-language.md`, domain model, or domain specification. They were defined only inside the AC file itself.
- **Example (correct):** `domain-terms.md` created in `docs/` containing all 28 missing terms with definitions before the AC references them. Rule added to SKILL.md and `rules/domain-terms-must-come-from-domain-model.md` to enforce this going forward.
- **Likely source:** prompt gap — skill template and rules did not previously require tracing domain terms to a domain artifact before use
- **Status:** confirmed
