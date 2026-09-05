---
scanner: layer_purity_scanner.py
---

# Rule: Maintain Layer Purity

Dependencies point inward toward the domain core. The `shared/` package contains **plain TypeScript only** — no framework imports. The `server/` package never imports from `client/`, and vice versa. Both `client/` and `server/` depend on `shared/`, but `shared/` depends on neither.

## DO

- Keep `shared/` free of Express, React, MongoDB, Mongoose, and any infrastructure framework.
- Use only plain TypeScript, Zod (validation), and standard library in `shared/`.
- Import domain logic from `shared/` into both `client/` and `server/`.
- Place HTTP/Express concerns exclusively in `server/`.
- Place React/UI concerns exclusively in `client/`.

```typescript
// packages/recipients/shared/RecipientStatus.ts — CORRECT: plain TypeScript only
export type RecipientStatusType = 'Active' | 'Pending' | 'Inactive';

export class RecipientStatus {
  constructor(
    public readonly status: RecipientStatusType,
    public readonly createdAt: Date
  ) {}

  isEligibleForPayment(): boolean {
    return this.status === 'Active';
  }
}
```

```typescript
// packages/recipients/server/Recipients.ts — CORRECT: server-side domain uses repo
import { Recipients as DomainRecipients } from '@app/recipients-shared';
import { RecipientsRepository } from './recipients.repository';

export class Recipients extends DomainRecipients {
  static async loadByEnterprise(
    enterpriseId: string,
    repo: RecipientsRepository,
  ): Promise<Recipient[]> {
    const all = await repo.findByEnterprise(enterpriseId);
    return new DomainRecipients(all).filterByStatus('Active').toArray();
  }
}
```

```typescript
// packages/recipients/server/recipients.routes.ts — CORRECT: delegates to domain-server
import { Recipients } from './Recipients';

router.get('/', async (req, res) => {
  const recipients = await Recipients.loadByEnterprise(enterpriseId, repo);
  res.json({ recipients });
});
```

## DON'T

- Import Express, React, MongoDB, or any framework/infrastructure library in `shared/`.
- Import `client/` code from `server/` or `server/` code from `client/`.
- Place React components or hooks in `shared/`.
- Place Express middleware or route handlers in `shared/`.
- Depend on the concrete repository class in the service layer — services must accept the repository **interface** so they can work with any implementation (MongoDB, in-memory, test fake).

```typescript
// packages/recipients/shared/Recipient.ts — WRONG: framework import in shared
import { Schema, model } from 'mongoose';  // VIOLATION: infrastructure in domain core
import express from 'express';              // VIOLATION: server framework in shared

export const RecipientSchema = new Schema({ ... });
```

```typescript
// packages/recipients/server/recipients.routes.ts — WRONG: importing from client
import { useRecipients } from '@app/recipients-client';  // VIOLATION: server imports client
```

```typescript
// packages/recipients/server/recipients.routes.ts — WRONG: route calls repo directly
router.get('/', async (req, res) => {
  const all = await repo.findByEnterprise(enterpriseId);  // VIOLATION: delegate to domain-server
});
```
