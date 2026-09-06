---
scanner: arg_naming_scanner.py
---

# Rule: Preserve Arg Names Across Layers

When a domain argument crosses a layer boundary, its **name stays the same** even if its type narrows. A `stage: Stage` object in the domain becomes `stage: StageId` (a string) at the API boundary — but it is still called `stage`, not `targetStage`, `stageId`, or `next`. The name is the thread that connects the domain concept through every layer.

## The Contract

```
domain specification:   {argName}: {DomainType}
Shared:         {argName}: {narrowedType}       name preserved, type may narrow
Client API:     {argName}: {narrowedType}       same name in function signature
Route body:     {arg_name}: value               snake_case of same name
Controller:     body.{arg_name}                 extracts by snake_case name
Service:        {argName}: {narrowedType}       camelCase again after extraction
```

## DO

- Keep the argument name identical across shared, client, service, and repository.
- Allow the **type** to narrow (object → string ID, rich type → primitive) without changing the name.
- Use snake_case of the same name in JSON bodies: `nextStage` → `next_stage`.
- Document narrowing in the domain specification or shared layer: "Stage narrows to StageId across the wire."

```typescript
// domain specification: moveToStage(ticket: Ticket, nextStage: Stage)

// shared/ — type narrows, name stays
export function moveToStage(ticketId: string, nextStage: StageId): void { ... }

// client API — same arg names
export async function moveToStage(ticketId: string, nextStage: StageId) {
  return post('/api/tickets/move-to-stage', { ticket_id: ticketId, next_stage: nextStage });
}

// controller — extracts by snake_case of same name
async moveToStage(req: Request, res: Response) {
  const { ticket_id, next_stage } = req.body;
  await this.service.moveToStage(ticket_id, next_stage);
}

// service — same arg names
async moveToStage(ticketId: string, nextStage: StageId) { ... }
```

## DON'T

- Rename args across layers: `ticket` in the model → `ticketId` in shared → `id` in the controller.
- Add redundant type prefixes: `stage` → `stageId`, `ticket` → `ticketObj`.
- Change the noun: `ticket` → `item`, `stage` → `column`, `role` → `agentType`.
- Use positional args with no name correspondence (relying on order instead of name).

```typescript
// WRONG — name changes at every layer
// domain specification: advanceToNextStage(ticket: Ticket)
// Shared:       advanceToNextStage(ticketId: string)     ← name changed from "ticket"
// Client:       advanceToNextStage(id: string)           ← name changed again to "id"
// Controller:   body.item_id                             ← completely different name

// CORRECT — name preserved, only type narrows
// domain specification: advanceToNextStage(ticket: Ticket)
// Shared:       advanceToNextStage(ticket: string)       ← same name, type narrowed
// Client:       advanceToNextStage(ticket: string)       ← same name
// Route body:   { ticket: "abc-123" }                    ← same name (no snake needed for single word)
```
