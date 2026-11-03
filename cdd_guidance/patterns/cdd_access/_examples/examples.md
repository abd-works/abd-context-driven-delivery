# CDD access examples

## `one-class-per-object`

**Faulty.** One connector knows every tool, and routes pass tool names to it.

```ts
routes.post('/tickets/:ticket/move-next', async (request, response) => {
  response.json(await cdd.call('ticket.move_next', { ticket: request.params.ticket }))
})
```

**Repaired.** The application mounts the routes the installer generates, and each runs its object's own adapter.

```ts
app.use('/api', cddRoutes(cdd, [...boardRoutes, ...ticketRoutes, ...backlogItemRoutes]))
```

## `adapter-is-generated`

**Faulty.** A hand-written class wraps the generated adapter to parse requests the installer already reads.

```ts
export class TicketNode extends TicketNodeAdapter {
  moveToRequested(request: Request): Promise<TicketNodeAdapter> {
    const { stage, done } = Destination.parse(request.body)
    return this.moveTo(stage, done)
  }
}
```

**Repaired.** The generated route reads the arguments against the tool's schema, and the page's subclass adds only what the page knows.

```ts
export class TicketClient extends TicketClientGenerated {
  override async moveTo(stage: string, done?: boolean): Promise<this | null> {
    const moved = await super.moveTo(stage, done)
    await this.page.reader.refresh()
    return moved
  }
}
```

## `state-lives-behind-the-tool`

**Faulty.** The app keeps its own copy of tickets, which goes stale when the agent moves one.

```ts
export class TicketRepositoryNode extends TicketRepository {}
```

**Repaired.** Tickets are read through their adapter. lowdb holds only what this app alone owns.

```ts
export class BoardLayoutRepositoryNode extends BoardLayoutRepository {}
```
