# ce-comments-are-for-invariants-and-sequencing-notes-only

- **entry_id:** 095b28e7
- **artifact:** cdd-sketch.md # DDD > Plan BC
- **rule:** CE // comments are for invariants and sequencing notes only — do not use them for descriptive prose, implementation notes, or cross-references
- **wrong:** SelectedPlan // transient value object — carries chosen Plan into Create Account; no persistence // ⚠️ two atoms: onboarding 'selected-plan' vs selfcare root 'my-selected-plan' — same concept, split namespace
- **status:** fixed
