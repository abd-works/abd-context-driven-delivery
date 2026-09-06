---
scanner: casing_transform_scanner.py
---

# Rule: Property Casing Transform

TypeScript uses **camelCase** for all property and argument names. JSON payloads (request bodies, response bodies, database documents) use **snake_case**. This is not optional or project-specific — it is the convention for this architecture. Every boundary crossing between TS code and serialized data applies this transform.

## The Contract

```
TypeScript (shared/client/server):   camelCase     boardMode, scopeLevel, ticketId
JSON (HTTP body, MongoDB doc):       snake_case    board_mode, scope_level, ticket_id
Route params/query:                  snake_case    ?board_mode=manual&scope_level=epic
```

## DO

- Name all TypeScript properties and arguments in camelCase.
- Serialize to snake_case when writing JSON (request body, response body, database document).
- Deserialize from snake_case to camelCase at the boundary (controller input, repository hydration).
- Use a consistent transform utility or do it explicitly at each boundary.
- Keep the **word** the same — only the casing changes: `boardMode` ↔ `board_mode`.

```typescript
// shared/ — camelCase properties
export interface BoardSnapshot {
  boardMode: BoardMode;
  scopeLevel: string;
  syncedAt: string;
}

// client API — sends snake_case in body
export async function toggleMode(boardId: string) {
  return post('/api/boards/toggle-mode', { board_id: boardId });
}

// controller — receives snake_case, passes camelCase to service
async toggleMode(req: Request, res: Response) {
  const boardId = req.body.board_id;
  const result = await this.service.toggleMode(boardId);
  res.json(toSnakeCase(result));
}

// repository — stores snake_case in MongoDB
async save(board: Board): Promise<void> {
  await this.collection.updateOne(
    { _id: board.id },
    { $set: { board_mode: board.boardMode, scope_level: board.scopeLevel } }
  );
}
```

## DON'T

- Use camelCase in JSON payloads: `{ "boardMode": "manual" }`.
- Use snake_case in TypeScript: `let board_mode = 'manual'`.
- Mix conventions: some properties camelCase in JSON, others snake_case.
- Change the word during casing transform: `boardMode` → `mode` (that's renaming, not casing).

```typescript
// WRONG — camelCase in JSON body
fetch('/api/boards/toggle-mode', {
  body: JSON.stringify({ boardId: id })  // should be board_id
});

// WRONG — snake_case in TypeScript
interface BoardSnapshot {
  board_mode: string;    // should be boardMode
  scope_level: string;   // should be scopeLevel
}

// WRONG — inconsistent mix
{
  "boardMode": "manual",     // camelCase
  "scope_level": "epic"      // snake_case — pick one (snake_case is correct)
}
```
