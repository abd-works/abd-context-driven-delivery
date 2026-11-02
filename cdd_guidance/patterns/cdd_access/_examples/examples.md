# CDD access examples

## `one-class-per-object`

**Faulty.** One connector knows every tool, and routes pass tool names to it.

```ts
routes.post('/tickets/:ticket/move-next', async (request, response) => {
  response.json(await cdd.call('ticket.move_next', { ticket: request.params.ticket }))
})
```

**Repaired.** The route asks the object, whose adapter class knows its own tool.

```ts
routes.post('/tickets/:ticket/move-next', async (request, response, next) => {
  await TicketNode.fromRequest(cdd, request).moveNext().then(result => response.json(result), next)
})
```

## `text-that-is-not-json-is-a-failure`

**Faulty.** A failed operation's plain text becomes a syntax error, and the real reason is lost.

```ts
return JSON.parse(text) as T
```

**Repaired.** Text that is not JSON is the failure, and it carries the real reason.

```ts
try {
  return JSON.parse(text) as T
} catch {
  throw new CddToolError(tool, text)
}
```

## `lowdb-only-for-what-cdd-does-not-own`

**Faulty.** The app keeps its own copy of tickets, which goes stale when the agent moves one.

```ts
export class TicketRepositoryNode extends TicketRepository {}
```

**Repaired.** Tickets are read through their tool. lowdb holds only what this app alone owns.

```ts
export class BoardLayoutRepositoryNode extends BoardLayoutRepository {}
```
