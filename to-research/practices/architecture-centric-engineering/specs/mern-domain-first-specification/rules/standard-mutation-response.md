---
scanner: mutation_response_scanner.py
---

# Rule: Standard Mutation Response Shape

All mutating endpoints (POST, PUT, DELETE) return the **same snapshot type** for a given aggregate. When a client calls any mutation on a domain aggregate, it gets back the full current state — no guessing which fields changed, no partial responses, no inconsistency between "create returns X but update returns Y."

## The Contract

```
POST   /api/{resource}/{verb-noun}  →  {AggregateSnapshot}
PUT    /api/{resource}/:id          →  {AggregateSnapshot}
DELETE /api/{resource}/:id          →  {AggregateSnapshot}  (or 204 if aggregate is gone)
```

Every mutation on the same aggregate returns the same shape. The client replaces its local state atomically.

## DO

- Define one `{Aggregate}Snapshot` type in `shared/` that represents the full read model.
- Return that snapshot from every mutation controller method.
- Let the client replace its local state wholesale after any mutation — no merging, no field-level diffing.
- For aggregates with sub-entities (e.g., a Board with Tickets), the snapshot includes the full tree.

```typescript
// shared/boardSnapshot.ts — the one shape
export interface BoardSnapshot {
  board_id: string;
  board_mode: string;
  tickets: TicketSnapshot[];
  team: Record<string, number>;
  synced_at: string;
}

// controller — every mutation returns the same shape
async toggleMode(req: Request, res: Response) {
  const snapshot = await this.service.toggleMode(req.body.board_id);
  res.json(snapshot);
}

async moveToStage(req: Request, res: Response) {
  const snapshot = await this.service.moveToStage(req.body.ticket_id, req.body.next_stage);
  res.json(snapshot);
}

async updatePairCount(req: Request, res: Response) {
  const snapshot = await this.service.updatePairCount(req.body.role, req.body.delta);
  res.json(snapshot);
}

// client — knows every mutation returns BoardSnapshot
export async function toggleMode(boardId: string): Promise<BoardSnapshot> { ... }
export async function moveToStage(ticket: string, stage: string): Promise<BoardSnapshot> { ... }
export async function updatePairCount(role: string, delta: number): Promise<BoardSnapshot> { ... }
```

## DON'T

- Return different shapes from different mutations on the same aggregate.
- Return only the modified entity from a mutation that affects the aggregate.
- Return `{ success: true }` or `{ message: "updated" }` — return the state.
- Make the client fetch separately after mutating to get the new state.

```typescript
// WRONG — different shapes per endpoint
async create(req, res) {
  res.status(201).json(created);              // returns just the entity
}
async toggleMode(req, res) {
  res.json({ success: true });                // returns a status message
}
async moveToStage(req, res) {
  res.json({ ticket: updated, stage: next }); // returns a partial projection
}

// CORRECT — all three return the full BoardSnapshot
```
