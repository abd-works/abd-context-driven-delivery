# model-navigational-outcomes

- **entry_id:** 3909515c
- **artifact:** tests/domain/catalog/catalog.ts
- **rule:** model-navigational-outcomes — when a domain operation navigates to the next step, the return value must be the domain object that enables that next step, not a data bag or void; this keeps the test chain readable as a sequence of real domain interactions and avoids needing a separate repository load just to confirm where you ended up
- **wrong:** catalog.select(plan): Promise<SelectedPlan> returned { plan } — a data bag that carried no actionable domain object and forced the test to call prospectRepository.load() to confirm navigation
- **status:** rejected
