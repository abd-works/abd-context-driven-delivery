---
scanner: interface_implementation_scanner.py
---

# Rule: Implement Full Interfaces

Every layer that claims to implement a domain interface must implement **all members**. Test adapters must correctly implement domain interfaces — no stub no-ops, no missing methods, no partial implementations. Both presentation (client) and persistence (server) layers implement the same domain interfaces independently, so domain logic is consistent across tiers. Verify completeness at compile time using TypeScript's type checker. Initialization order matters: all dependencies must be assigned before calling methods that use them.

## DO

- Implement every method and property defined in the domain interface.
- Use TypeScript `implements` keyword so the compiler catches missing members.
- Ensure test adapters (mocks, fakes) implement the full interface.
- Assign all dependencies in the constructor before any method calls.
- Verify at compile time: `tsc --noEmit` should report zero errors for interface compliance.

```typescript
// packages/recipients/shared/types.ts — domain interface
export interface RecipientRepository {
  findAll(): Promise<Recipient[]>;
  findByIds(ids: string[]): Promise<Recipient[]>;
  findByEnterprise(enterpriseId: string): Promise<Recipient[]>;
}

// packages/recipients/server/recipients.repository.ts — CORRECT: all methods implemented
export class MongoRecipientsRepository implements RecipientRepository {
  constructor(private db: Db) {}

  async findAll(): Promise<Recipient[]> { ... }
  async findByIds(ids: string[]): Promise<Recipient[]> { ... }
  async findByEnterprise(enterpriseId: string): Promise<Recipient[]> { ... }
}

// tests/.../helpers/fake-recipients.repository.ts — CORRECT: test adapter implements full interface
export class FakeRecipientsRepository implements RecipientRepository {
  private items: Recipient[] = [];

  async findAll() { return this.items; }
  async findByIds(ids: string[]) { return this.items.filter(r => ids.includes(r.id)); }
  async findByEnterprise(eid: string) { return this.items.filter(r => r.enterpriseId === eid); }

  seed(recipients: Recipient[]) { this.items = recipients; }
}
```

## DON'T

- Leave interface methods unimplemented or stubbed with `throw new Error('not implemented')`.
- Skip `implements` keyword — without it, TypeScript won't catch missing members.
- Create test adapters that only implement the methods used in one test (partial mocks).
- Call methods that depend on constructor-injected dependencies before those dependencies are assigned.
- Group unrelated methods into a single interface (Interface Segregation violation).

```typescript
// WRONG — partial implementation, missing findByEnterprise
export class RecipientsRepo implements RecipientRepository {
  async findAll() { ... }
  async findByIds(ids: string[]) { ... }
  // findByEnterprise is MISSING — compile error if `implements` is used
}

// WRONG — test adapter stubs with no-ops
export class MockRecipientsRepository implements RecipientRepository {
  async findAll() { return []; }
  async findByIds() { throw new Error('not implemented'); }  // WRONG: stub no-op
  async findByEnterprise() { return []; }
}

// WRONG — initialization order bug
export class RecipientsService {
  constructor(private repo: RecipientsRepository) {
    this.loadCache();  // WRONG: calls method before subclass fields are initialized
  }
}
```
