# domain-surface-consistency

- **entry_id:** 938810d7
- **artifact:** tests/domain/paradise-mobile/paradise-mobile.ts
- **rule:** domain-surface-consistency — all domain concerns reached through properly named services or repositories; checkout is reached via cartRepository not as a top-level peer; authentication interaction reached via authentication() service not a naked credentials() accessor
- **wrong:** credentials() and checkout() exposed as top-level peers on ParadiseMobile interface alongside catalog() and cartRepository(); checkout() implies it is a parallel entry point independent of a cart; credentials() names the form object not the service
- **status:** open
