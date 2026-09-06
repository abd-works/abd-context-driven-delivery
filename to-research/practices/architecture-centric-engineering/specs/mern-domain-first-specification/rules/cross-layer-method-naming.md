---
scanner: cross_layer_naming_scanner.py
---

# Rule: Cross-Layer Method Naming Contract

A single domain method name flows through all layers unchanged. The domain specification names the operation; every layer uses that same `{verbNoun}` stem. No layer invents a synonym, abbreviation, or CRUD-generic replacement.

## The Contract

```
domain specification:   {verbNoun}({domainArgs})
Shared:         {verbNoun}({domainArgs})              same name, TypeScript types
Client API:     async {verbNoun}({domainArgs})        same name, HTTP underneath
Controller:     async {verbNoun}(body)                same name, extracts args from body
Service:        async {verbNoun}({domainArgs})        same name, orchestrates domain + repo
Route:          POST /api/{resource}/{verb-noun}      kebab-case of the same name
```

## DO

- Derive every layer's method name from the domain specification verb: if the model says `toggleMode()`, the controller says `toggleMode(body)`, the service says `toggleMode(boardId)`, the API client says `toggleMode(boardId)`.
- Use the same verb-noun pair everywhere: `moveToStage`, `updatePairCount`, `scatterTickets`.
- Name routes as the kebab-case of the method: `toggleMode` → `POST /api/boards/toggle-mode`.
- When the domain model adds a new operation, add it with the same name in all layers simultaneously.

```typescript
// domain specification says: toggleMode()

// shared/KanbanBoard.ts
export class KanbanBoard {
  toggleMode(): BoardMode { ... }
}

// client/kanbanBoard.api.ts
export async function toggleMode(boardId: string): Promise<BoardSnapshot> {
  return post(`/api/boards/toggle-mode`, { board_id: boardId });
}

// server/kanbanBoard.controller.ts
export class KanbanBoardController {
  async toggleMode(req: Request, res: Response): Promise<void> {
    const result = await this.service.toggleMode(req.body.board_id);
    res.json(result);
  }
}

// server/kanbanBoard.service.ts
export class KanbanBoardService {
  async toggleMode(boardId: string): Promise<BoardSnapshot> {
    const board = await this.repo.findById(boardId);
    board.toggleMode();
    await this.repo.save(board);
    return board.toSnapshot();
  }
}

// server/kanbanBoard.routes.ts
router.post('/toggle-mode', (req, res) => controller.toggleMode(req, res));
```

## DON'T

- Use CRUD-generic names when the domain has a specific verb: `update()` instead of `toggleMode()`, `modify()` instead of `moveToStage()`.
- Rename across layers: `toggleMode` in shared but `switchBoardMode` in the controller.
- Use a different class as the host: domain says `Board.toggleMode()` but client puts it on `Heartbeat.toggleMode()`.
- Invent new verbs at the API client layer: `fetchToggleMode()`, `requestModeChange()`.

```typescript
// WRONG — different names at each layer for the same operation
// domain specification: incrementPairCount()
// Client:       Heartbeat.adjustTeam(root, role, +1)    ← verb changed to "adjust"
// Controller:   updateTeam(body)                        ← verb changed to "update"
// Service:      modifyTeamCount(role, delta)            ← verb changed to "modify"

// WRONG — CRUD generic hiding domain intent
// domain specification: moveToStage(ticket, stage)
// Controller:   update(body)                            ← lost the domain verb entirely
// Route:        PUT /api/tickets/:id                    ← generic REST, no domain verb
```
