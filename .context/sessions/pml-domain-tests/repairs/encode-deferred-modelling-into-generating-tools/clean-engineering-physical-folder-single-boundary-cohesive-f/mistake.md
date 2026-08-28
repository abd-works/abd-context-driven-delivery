# clean-engineering-physical-folder-single-boundary-cohesive-f

- **entry_id:** 3127a00c
- **artifact:** acceptance-test-strategy.md
- **rule:** clean-engineering physical-folder / single-boundary / cohesive-file / nest-when-shared-else-flat module rules; stories artifacts-mirror-story-hierarchy rule
- **wrong:** First two drafts of the Playwright acceptance-test folder structure organized files by ARTIFACT KIND instead of by domain module: all domain-model interfaces dumped flat into one domain-model/ folder, and all e2e implementations dumped flat into a separate tiers/e2e/ folder. This was invented without re-reading clean_engineering.md or stories.md first, and without checking cdd-sketch.md's own documented cross-BC dependency notes (the '-> Subscription' / '-> Order' / '-> Plan' / '-> Customer' blocks) to decide real module boundaries.
- **status:** fixed