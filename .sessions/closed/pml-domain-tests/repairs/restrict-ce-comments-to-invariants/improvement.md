# ce-comments-are-for-invariants-and-sequencing-notes-only

- **tool:** CleanEngineering
- **error:** SelectedPlan // transient value object — carries chosen Plan into Create Account; no persistence // two atoms: onboarding 'selected-plan' vs selfcare root 'my-selected-plan' — same concept, split namespace
- **rule:** ce-comments-are-for-invariants-and-sequencing-notes-only
- **what changed:**
  - **Prose — yes.** Named rule in `clean_engineering.md` (model `//` notes) and the sketch legend in `templates/clean_engineering-sketch.md`. `//` is must/never/before/after only — not descriptive prose.
  - **Scanner — yes.** `ce_comments_are_for_invariants_scanner.py`.
