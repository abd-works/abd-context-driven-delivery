---
scanner: entity_behavior_scanner.py
---

# Rule: Implement Domain Entities Correctly

Business rules belong **on domain classes**, not in services. Domain entities own their state and behavior — they are not anemic data bags passed to services that do all the work. Zod schemas validate at the **repository boundary** (raw data → typed entity) and at the **API boundary** (request body → validated input). Value Objects encapsulate domain constraints (e.g., SWIFT format, status transitions). Collection classes provide domain-oriented query methods.

## DO

- Place business logic as methods on the entity or value object that owns the data.
- Use Value Objects for constrained values: `RecipientStatus`, `BeneficiaryBank`, `RecipientEmail`.
- Create collection classes (e.g., `Recipients`) that wrap arrays with domain-oriented filter/search methods.
- Validate with `Schema.parse()` at the repository boundary (converting raw docs to entities).
- Validate with `Schema.safeParse()` at the API/form boundary (user input → request).
- Keep domain classes portable: no framework imports, no side effects, no async.

```typescript
// packages/recipients/shared/RecipientStatus.ts — CORRECT: logic on the value object
export class RecipientStatus {
  constructor(
    public readonly status: RecipientStatusType,
    public readonly createdAt: Date,
    private readonly countryCode: 'US' | 'MX' = 'US'
  ) {}

  isEligibleForPayment(): boolean {
    return this.status === 'Active';
  }

  get remainingPendingMinutes(): number | null {
    if (this.countryCode !== 'MX' || this.status !== 'Pending') return null;
    const elapsed = Date.now() - this.createdAt.getTime();
    return Math.ceil(Math.max(0, 30 * 60 * 1000 - elapsed) / 60000);
  }
}
```

```typescript
// packages/recipients/shared/Recipients.ts — CORRECT: collection with domain methods
export class Recipients {
  constructor(private readonly items: Recipient[]) {}

  filterByStatus(status: RecipientStatusType): Recipients {
    return new Recipients(this.items.filter(r => r.status.status === status));
  }

  search(query: string): Recipients {
    const lower = query.toLowerCase();
    return new Recipients(this.items.filter(r =>
      r.name.toLowerCase().includes(lower)
    ));
  }

  toArray(): Recipient[] { return [...this.items]; }
  get length(): number { return this.items.length; }
}
```

## DON'T

- Place business rules in services while leaving entities as plain data objects (Anemic Domain Model).
- Scatter validation logic outside the schema/entity boundary.
- Use raw `Recipient[]` arrays everywhere instead of typed collection classes.
- Put async operations or framework calls inside domain entities.

```typescript
// WRONG — Anemic Domain Model: service does all the work, entity is a data bag
export interface Recipient {
  id: string;
  name: string;
  status: string;
}

export class RecipientService {
  isEligible(recipient: Recipient): boolean {   // WRONG: logic belongs on the entity
    return recipient.status === 'Active';
  }

  filterActive(recipients: Recipient[]): Recipient[] {  // WRONG: use a collection class
    return recipients.filter(r => r.status === 'Active');
  }
}
```

```typescript
// WRONG — domain entity with framework dependency
export class Recipient {
  async save() {                          // WRONG: persistence in domain entity
    await mongoose.model('Recipient').save(this);
  }
}
```
