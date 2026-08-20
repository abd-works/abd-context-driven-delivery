# no-module-level-functions

- **entry_id:** b7d04e22
- **artifact:** tests/domain/paradise-mobile/paradise-mobile.e2e.ts
- **rule:** no-module-level-functions — factory and lifecycle operations must be static methods on the class, not module-level exported functions; module-level functions obscure which class owns the operation and prevent consistent call-site naming
- **wrong:** export async function open(cfg) delegated to ParadiseMobileE2e.open() as a module-level wrapper; story files called open(config) instead of ParadiseMobileE2e.initialize(config)
- **status:** open
