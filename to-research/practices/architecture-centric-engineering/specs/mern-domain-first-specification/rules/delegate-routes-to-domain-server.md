---
scanner: route_delegation_scanner.py
---

# Rule: Delegate Routes to Domain Server

Route handlers in `<<domain>>.routes.ts` are thin HTTP adapters. They parse the request and delegate to a **server-side domain class** in `<<domain>>-server` (`server/<<Entity>>s.ts` or aggregate class). They never call the repository or instantiate domain logic from `shared/` directly.

## DO

- Delegate every handler to a method on the server-side domain class: `Recipients.loadByEnterprise(...)`, `KanbanBoard.moveToStageAndPersist(...)`.
- Inject the repository into the router factory; pass it to server-side domain static methods or constructors.
- Keep request parsing (query params, body validation) in the route handler only.

```typescript
// packages/recipients/server/recipients.routes.ts — CORRECT
router.get('/', async (req, res) => {
  const enterpriseId = (req as any).user.enterpriseId;
  const activeOnly = req.query.activeOnly === 'true';
  const recipients = await Recipients.loadByEnterprise(enterpriseId, repo, { activeOnly });
  res.json({ recipients, total: recipients.length });
});
```

```typescript
// packages/recipients/server/Recipients.ts — CORRECT: server-side domain owns repo
export class Recipients extends DomainRecipients {
  static async loadByEnterprise(
    enterpriseId: string,
    repo: RecipientsRepository,
    opts?: { activeOnly?: boolean },
  ): Promise<Recipient[]> {
    const all = await repo.findByEnterprise(enterpriseId);
    // ... shared domain logic ...
  }
}
```

## DON'T

- Call `repo.findByEnterprise()` or `repo.findByIds()` directly inside a route handler.
- Apply `new Recipients(all).filterByStatus(...)` in the route — that belongs in `<<domain>>-server`.
- Add a default `service.ts` application layer; use server-side domain classes that extend `shared/`.
- Skip server-side domain and wire routes straight to repository.

```typescript
// WRONG — route calls repository directly
router.get('/', async (req, res) => {
  const all = await repo.findByEnterprise(enterpriseId);
  const recipients = new Recipients(all).filterByStatus('Active').toArray();
  res.json({ recipients });
});
```
