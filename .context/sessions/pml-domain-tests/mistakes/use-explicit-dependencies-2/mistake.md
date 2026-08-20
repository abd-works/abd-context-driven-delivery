# use-explicit-dependencies-2

- **entry_id:** d4a91c73
- **artifact:** tests/domain/prospect/cart/cart.ts, tests/domain/paradise-mobile/paradise-mobile.ts, tests/onboard-a-customer/*.e2e.ts
- **rule:** use-explicit-dependencies — a cart has no identity outside its prospect; never load a cart from a standalone repository that defaults to ambient session state
- **wrong:** paradise.cartRepository().current() / selectPlan() / save() — an orphaned cart loaded without the prospect that owns it
- **status:** open
