---
scanner: share_domain_logic_scanner.py
---

# Rule: Share Domain Logic

Define domain entities, value objects, Zod validation schemas, and business rule methods **once** in the `shared/` package. Both `client/` and `server/` import from `shared/` — never duplicate validation, type definitions, or business logic across tiers. This eliminates drift between frontend and backend validation, ensures consistent behavior, and creates a single source of truth for domain rules.

## DO

- Place all Zod schemas in `shared/` so both tiers validate identically.
- Define domain entity classes with business methods in `shared/`.
- Export collection/aggregate classes (e.g., `Recipients`) from `shared/` for reuse in both tiers.
- Use the shared schema in the repository layer to validate raw DB documents into typed entities.
- Use the same shared schema in the client for form validation before HTTP calls.
- **Hydrate API responses** into domain class instances in the API client layer. `fetch()` returns plain JSON objects — calling domain methods like `completedCount()` on them throws `TypeError: not a function`. The API client (`*.api.ts`) must reconstruct domain entities using static factory methods (e.g., `TodoList.create()`, `Task.create()`).

```typescript
// packages/todo-lists/client/todoLists.api.ts — CORRECT: hydrates JSON → domain classes
import { TodoList, Task } from '@taskflow/todo-lists-shared';

function hydrateTodoList(raw: any): TodoList {
  const tasks = (raw.tasks || []).map((t: any) =>
    Task.create({ id: t.id, title: t.title, completed: t.completed, createdAt: new Date(t.createdAt) })
  );
  return TodoList.create({
    id: raw.id, userId: raw.userId, name: raw.name, tasks,
    createdAt: new Date(raw.createdAt), updatedAt: new Date(raw.updatedAt),
  });
}

export async function fetchTodoLists(): Promise<TodoList[]> {
  const response = await fetch(API_BASE);
  const data = await response.json();
  return (data.items || []).map(hydrateTodoList);  // hydrate each item
}
```

```typescript
// WRONG — returns raw JSON, domain methods will crash at runtime
export async function fetchTodoLists(): Promise<TodoList[]> {
  const response = await fetch(API_BASE);
  const data = await response.json();
  return data.items;  // BUG: these are plain objects, not class instances
}
```

```typescript
// packages/recipients/shared/recipient.schema.ts — CORRECT: single source of truth
import { z } from 'zod';

export const RecipientSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(140),
  status: z.enum(['Active', 'Pending', 'Inactive']),
  beneficiaryBank: BeneficiaryBankSchema,
});

export type RecipientDTO = z.infer<typeof RecipientSchema>;
```

```typescript
// packages/recipients/server/recipients.repository.ts — CORRECT: validates with shared schema
import { RecipientSchema } from '@project/recipients/shared';

async findAll(): Promise<Recipient[]> {
  const docs = await this.collection.find().toArray();
  return docs.map(doc => RecipientSchema.parse(doc));  // shared validation
}
```

```typescript
// packages/recipients/client/RecipientForm.tsx — CORRECT: same schema for client validation
import { RecipientSchema } from '@project/recipients/shared';

const result = RecipientSchema.safeParse(formData);
if (!result.success) { setErrors(result.error.issues); }
```

## DON'T

- Duplicate Zod schemas or validation logic between `client/` and `server/`.
- Redefine TypeScript interfaces that already exist in `shared/`.
- Place business rule methods (e.g., eligibility checks) in only one tier.
- Create separate "client types" and "server types" for the same domain concept.

```typescript
// packages/recipients/server/validation.ts — WRONG: duplicated schema
import { z } from 'zod';
export const ServerRecipientSchema = z.object({  // DUPLICATE of shared schema
  id: z.string().uuid(),
  name: z.string().min(1).max(140),
  status: z.enum(['Active', 'Pending', 'Inactive']),
});
```

```typescript
// packages/recipients/client/types.ts — WRONG: separate type definition
export interface ClientRecipient {  // DUPLICATE: already defined in shared
  id: string;
  name: string;
  status: 'Active' | 'Pending' | 'Inactive';
}
```
