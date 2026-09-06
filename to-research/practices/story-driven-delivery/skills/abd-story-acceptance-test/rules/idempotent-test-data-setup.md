---
scanner: idempotent_setup_scanner.py
---

# Rule: Idempotent Test Data Setup

Test setup (seed scripts, `global-setup`, `beforeAll` hooks) must be **idempotent** — running setup twice against the same database produces the same starting state, never duplicates or conflicts. Every entity the tests create must be explicitly cleaned before it is re-created.

## DO

- **Delete before create.** Clean up transient entities (redemptions, API keys, sessions, tokens) at the top of setup before re-seeding.
- **Delete children first.** Respect referential integrity: delete dependent rows before parent rows (e.g. redemptions before vouchers, vouchers before campaigns).
- **Upsert with full field set.** When using upsert (or `INSERT … ON CONFLICT UPDATE`), the `update` block must set every field that matters — not just the `create` block. If a field is missing from `update`, stale values persist on re-run.
- **Use far-future dates for long-lived fixtures.** Entities that must never expire during test runs (e.g. campaigns used by redemption tests) should use `endAt: 2099-12-31` or `null`, never a date in the near future.
- **Scope cleanup to test-owned data.** Use a naming convention (e.g. `E2E-` prefix, a dedicated `organizationId`) so cleanup never deletes non-test rows.

```typescript
// global-setup.ts — idempotent seed
await prisma.$transaction(async (tx) => {
  // 1. Clean children first
  await tx.redemption.deleteMany({ where: { voucher: { campaignId: E2E_CAMPAIGN_ID } } })
  await tx.apiKey.deleteMany({ where: { organizationId: E2E_ORG_ID, name: { startsWith: 'E2E-' } } })
  await tx.voucher.deleteMany({ where: { campaignId: E2E_CAMPAIGN_ID } })

  // 2. Upsert parents with FULL field set in update
  await tx.campaign.upsert({
    where: { id: E2E_CAMPAIGN_ID },
    create: { id: E2E_CAMPAIGN_ID, name: 'E2E Campaign', endAt: new Date('2099-12-31'), ... },
    update: { name: 'E2E Campaign', endAt: new Date('2099-12-31'), ... },  // ALL fields
  })

  // 3. Upsert children
  for (const voucher of SEEDED_VOUCHERS) {
    await tx.voucher.upsert({
      where: { code: voucher.code },
      create: { ...voucher, campaignId: voucher.campaignId ?? E2E_CAMPAIGN_ID },
      update: { ...voucher, campaignId: voucher.campaignId ?? E2E_CAMPAIGN_ID },  // ALL fields
    })
  }
})
```

## DON'T

- **Don't rely on a fresh database.** Tests run against persistent dev DBs. Rows from previous runs will exist.
- **Don't omit fields from the upsert `update` block.** If `create` sets `campaignId` but `update` does not, re-runs leave stale values:

```typescript
// WRONG — update block missing campaignId; re-runs keep stale assignment
await tx.voucher.upsert({
  where: { code: 'REDEEM-OK' },
  create: { code: 'REDEEM-OK', campaignId: LONG_LIVED_CAMPAIGN_ID, ... },
  update: { redemptionCount: 0 },  // campaignId NOT updated — bug on re-run
})
```

- **Don't use near-future dates for fixtures that must survive across test sessions.** A campaign with `endAt: '2026-04-30'` will start failing in May:

```typescript
// WRONG — date will expire; redemption tests start returning 409
create: { endAt: new Date('2026-04-30') }

// CORRECT — far-future or null for evergreen fixtures
create: { endAt: new Date('2099-12-31') }
```

- **Don't skip cleanup of transient entities.** Without cleanup, redemptions from a previous run cause duplicate-key or conflict errors:

```typescript
// WRONG — no cleanup; second run gets 409 "already redeemed"
await tx.voucher.upsert({ ... })
// Missing: await tx.redemption.deleteMany(...)
```

## Checklist for global-setup / seed scripts

- [ ] All transient children deleted before parent upserts
- [ ] Upsert `update` blocks mirror `create` (no missing fields)
- [ ] Long-lived fixtures use `2099-12-31` or `null` for expiry
- [ ] Test data uses a naming convention (`E2E-` prefix or dedicated org/tenant ID)
- [ ] Running setup twice against the same DB produces identical state
