## Overview

How anything outside Python reaches the **CDD domain**. The domain, its rules, and its state stay in Python. Skills, actions, and commands reach it through MCP tools. Code in any other language reaches those same tools through a **language adapter** for that language, which the installer deploys beside the skills and MCP operations. Every language follows the same pattern, and TypeScript is the first implementation, so the examples below are TypeScript.

**Every MCP call is made on the server.** The cdd server is a local program the application's server starts and talks to over its standard input and output. A browser cannot start it or reach it, and exposing it to the page would bypass the application server's guard on who may act. So the browser asks the application's server, and the server calls MCP.

**The language adapter is a straight conversion of the Python, and the installer writes all of it.** Everything it needs is already in the Python: the tool names, their arguments and types, what each returns, the shape `to_json()` returns, and which field names the object. Because the browser's path to the server follows one fixed rule, the installer writes both ends of it, so they match by construction:

| Generated | Where it runs | What it is |
|---|---|---|
| `{Object}` | Browser and server | The shared base: the object's state, its `camelCase` getters, and `changed(data)`, which takes on new state. It makes no call. **Nothing uses it directly**; code always works with one of its subtypes. |
| `{Object}NodeAdapter extends {Object}` | Server | Each operation calls its MCP tool and takes on the state Python returns. |
| `{Object}ClientGenerated extends {Object}` | Browser | Each operation posts to its route and takes on the state the server returns. |
| `{object}Routes` | Server | One route for each tool. Each reads the request against the tool's published schema and calls `{Object}NodeAdapter`. |
| `CddConnection` | Server | One per install. Starts one cdd server and carries calls to it. It knows no tool by name. |

**What the application's pattern adds.** LERN mounts `{object}Routes` on its server, and subclasses `{Object}ClientGenerated` for what only the page knows, such as selecting a card or showing a toast. That subclass is LERN's `{Domain}Client`. A Claude Code mod reaches the tools through `$.mcp.call`, as `patterns-cdd-claude-mod` describes. Nothing in the application calls a tool, parses a request for one, or writes a path to one.

**No god connector.** Each domain object has its own classes that know its own tools. `TicketNodeAdapter` calls `ticket.move_next`, and `BoardNodeAdapter` calls `board.show`. One connection underneath carries the calls and knows no tool by name.

**Reach the end-user API, not the framework.** Practices, patterns, actions, and `space` are the CDD domain an application reaches. `harness/` is the framework that installs and serves them, so an application does not call into it. The graph is reached through the practices that read it, such as validate with `graph`; expose a graph tool directly only when an application's generation needs it and no practice gives it.

**No fidelity progression of its own.** Every run works one domain object through the layers below, Python first.

| Layer | File | Role |
|---|---|---|
| Domain | `cdd_guidance/practices/<practice>/*.py`, `cdd_guidance/patterns/<pattern>/*.py`, `cdd_guidance/actions/<action>/*.py`, `space/<domain>/*.py` | The Python classes. Every rule, decision, and piece of state lives here. |
| Tool | The same file, marked `@mcp @agent_tool` | One operation for each thing a person or agent does. The tool reads `{object}.{operation}`. |
| Contract | `{Object}Data`, a `TypedDict` that `to_json()` is annotated with | The only agreement between the languages. The language adapter is written from it. |
| Mark | `@language_adapter(language="typescript", identity="name")` on the class | Opts the toolset in to the language adapter for that language. `identity` names the field of `{Object}Data` that holds the object's name, so a browser object knows which object its routes act on. |
| Language adapter | `<install path>/language-adapters/<language>/<source folders>/<object>.<ext>` | Generated: `{Object}Data`, `{Object}`, `{Object}NodeAdapter`, `{Object}ClientGenerated`, and `{object}Routes`. |
| Connection | `<install path>/language-adapters/<language>/cdd-connection.<ext>` | Generated: `CddConnection`, once per install. |

```mermaid
classDiagram
  class TicketPython {
    <<Python>>
    +move_next()
    +to_json() TicketData
  }
  class Ticket {
    <<generated>>
    +column
    +isDone
    #changed(data)
  }
  class TicketNodeAdapter {
    <<generated>>
    +fromRequest(cdd, request)
    +moveNext()
  }
  class TicketClientGenerated {
    <<generated>>
    +moveNext()
  }
  class ticketRoutes {
    <<generated>>
  }
  class CddConnection {
    <<generated>>
    +call(tool, args)
  }
  class TicketClient {
    <<LERN>>
    +select()
  }

  Ticket <|-- TicketNodeAdapter
  Ticket <|-- TicketClientGenerated
  TicketClientGenerated <|-- TicketClient
  TicketClientGenerated ..> ticketRoutes : POST
  ticketRoutes --> TicketNodeAdapter : asks
  TicketNodeAdapter --> CddConnection : its own tools
  CddConnection --> TicketPython : MCP
```

```mermaid
sequenceDiagram
  actor Person
  participant Client as TicketClient (LERN, browser)
  participant Others as Other page clients
  participant Generated as TicketClientGenerated (browser)
  participant Route as ticketRoutes (server)
  participant Node as TicketNodeAdapter (server)
  participant Connection as CddConnection (server)
  participant Python as Ticket (Python)

  Person->>Client: moveNext()
  Client->>Generated: super.moveNext()
  Generated->>Route: POST /ticket/session-board/move-next
  Route->>Node: fromRequest(cdd, request).moveNext()
  Node->>Connection: call('ticket.move_next', { ticket })
  Connection->>Python: MCP
  Python-->>Connection: to_json()
  Connection-->>Node: TicketData
  Node-->>Route: itself, with that state
  Route-->>Generated: TicketData
  Generated-->>Client: itself, with that state
  Client->>Others: refresh the board, follow the moved card
  Client-->>Person: the board shows the move
```

---

## Guidance

Enforceable rules live in **§ Shared rules** below. This section explains how they apply; do not treat guidance bullets as a second rule list.

### Every door reaches the same tool

A person typing a slash command, an agent calling a tool, and a person pressing a button in a web app all reach one MCP tool, and the tool calls one domain operation. Because they share that tool, what the board shows and what the agent does cannot disagree.

| Door | Reaches the tool through |
|---|---|
| Skill, action, or command | The agent calls the MCP tool |
| Claude Code mod | `$.mcp.call`, typed by the language adapter, as `patterns-cdd-claude-mod` describes |
| Web page | `{Object}ClientGenerated`, then `{object}Routes`, then `{Object}NodeAdapter` |
| Server code | `{Object}NodeAdapter` |

### One straight line

An operation reads the same from the page to the domain, so anyone can follow it by searching one word.

| Browser | Route | Server | Tool | Domain |
|---|---|---|---|---|
| `TicketClientGenerated.moveNext()` | `POST /ticket/:ticket/move-next` | `TicketNodeAdapter.moveNext()` | `ticket.move_next` | `Ticket.move_next()` |
| `TicketClientGenerated.enablePractice(practice, isEnabled)` | `POST /ticket/:ticket/enable-practice` | `TicketNodeAdapter.enablePractice(practice, isEnabled)` | `ticket.enable_practice` | `Ticket.enable_practice(practice, is_enabled)` |

The route is the tool's object, then the object's identity when the tool loads one, then the operation in kebab case. Every route is a `POST` with the operation's own arguments in the body, so both ends follow from the tool's name alone.

### The language adapter is a deployment target

The installer treats a language adapter as one more channel, beside skills, commands, rules, MCP, and hooks. It walks the same toolsets, reads the same marks, tracks what it writes so `clean` removes it, and reports it in `diagnostics.json`. Like the rest of the install it is generated, never edited, and not committed, so run the installer on a fresh clone before building. Each language gets its own folder under `language-adapters/`; a new language adds a writer for that folder and changes nothing in the Python domain or its tools. The TypeScript adapter below is the first.

```python
@language_adapter(language="typescript", identity="name")
@agent_toolset
class Ticket(Card):
    def to_json(self) -> TicketData: ...
```

```
.claude/language-adapters/typescript/
├── cdd-connection.ts            CddConnection, using only Node's own modules
├── cdd-shared.ts                what every object shares and a browser can load: reading a request, the page's API, the errors
├── harness/kanban/
│   ├── ticket.ts                TicketData, Ticket, TicketClientGenerated
│   ├── ticket-node-adapter.ts   TicketNodeAdapter, ticketRoutes
│   ├── board.ts
│   └── board-node-adapter.ts
└── space/session/...
```

The folders mirror the toolset's source. Only marked toolsets are written, so catalog pages, rules, and guidance prose never appear here. **Mark a toolset when an application needs its results as data.** A toolset that returns prompt text for an agent to follow, as the practices and actions do, gains little from a typed adapter, so it stays unmarked.

Import it through the `@cdd` path alias, which points at the install. The install sits outside every application's packages, so the adapter imports no package: the connection speaks MCP with Node's own modules, the routes are plain data any server framework can mount, and the client posts through whatever `CddApi` the page hands it. The browser imports `<object>.ts`, which loads nothing from Node; only the server imports `<object>-node-adapter.ts`.

```ts
export class Ticket {
  #state: TicketData | null

  constructor(state: TicketData | null) {
    this.#state = state
  }

  toJSON(): TicketData {
    return this.#read()
  }

  get isDone(): boolean {
    return this.#read().is_done
  }

  protected changed(state: TicketData): this {
    this.#state = state
    return this
  }

  // A server adapter is built from the name a request carries, before Python has sent its state.
  #read(): TicketData {
    if (!this.#state) throw new CddNotReadError('ticket')
    return this.#state
  }
}

export class TicketNodeAdapter extends Ticket {
  constructor(protected readonly cdd: CddConnection, protected readonly ticket: string, state: TicketData | null = null) {
    super(state)
  }

  static fromRequest(cdd: CddConnection, request: CddRequest): TicketNodeAdapter { ... }

  async moveTo(stage: string, done?: boolean): Promise<this> {
    return this.changed(await this.cdd.call<TicketData>('ticket.move_to', { ticket: this.ticket, stage, done }))
  }
}

export class TicketClientGenerated extends Ticket {
  constructor(protected readonly api: CddApi, state: TicketData | null = null, protected readonly ticket: string = state?.name ?? '') {
    super(state)
  }

  static named(api: CddApi, ticket: string): TicketClientGenerated {
    return new TicketClientGenerated(api, null, ticket)
  }

  async moveTo(stage: string, done?: boolean): Promise<this | null> {
    const state = await this.api.post<TicketData>(`/ticket/${encodeURIComponent(this.ticket)}/move-to`, { stage, done })
    return state ? this.changed(state) : null
  }
}

export const ticketRoutes: CddRoute[] = [
  { path: '/ticket/:ticket/move-to', run: (cdd, request) => { ... TicketNodeAdapter.fromRequest(cdd, request).moveTo(sent.stage, sent.done) } },
]
```

- An operation whose tool returns the object's own data takes on that state and returns the object. Any other result, such as another object's data or a choice of objects, is returned as Python sent it.
- A Python `@classmethod` operation becomes a `static` operation that takes the connection or the API and returns the new object's data. The application builds the subtype it needs from that data.
- A route reads the operation's arguments from the body, checked against the tool's published schema, and raises `CddRequestError` when one is missing or the wrong type. The schema already says what each argument is, so the application writes no parsing.
- `CddApi.post` answers `null` once the page has shown the person a failure, so a browser operation then keeps its state and returns `null`, and the page stops there.
- Page code that knows only a name builds `{Object}ClientGenerated.named(api, name)` and acts on that object before it has read it.
- An object without `identity`, such as the one board, has routes with no name in them.

### Python states the contract

`{Object}Data` is a `TypedDict` the domain class annotates `to_json()` with, so the shape is written once, in Python, and every other language follows. A plain `dict[str, Any]` generates `Record<string, unknown>`, which the compiler cannot check. `NotRequired` becomes an optional field, and `str | None` a nullable one. Fields keep Python's `snake_case` in `{Object}Data`, because it states exactly what `to_json()` returns and some keys are data, such as a fidelity named `story_map`. The getters, operation names, and arguments are `camelCase`, and the adapters send arguments under their Python names.

### State stays behind the tool

An application keeps no copy of what the domain owns. There is no repository, no store, and no cache for a CDD object, because a second copy drifts from the first and the agent changes state without telling the application. An adapter holds only the state its last call returned; to stay current, call again.

**lowdb is for state CDD does not own.** A web app built in LERN still uses lowdb for what belongs to that app alone, such as a person's saved layout. For an aggregate backed by CDD, `{Object}NodeAdapter` takes the repository's place on the server.

### When a call fails

The MCP server answers a failed operation with plain text, such as `TicketNotFoundError: no ticket x`, and it does not always set `isError`. Every successful operation returns JSON, so `CddConnection` treats text that is not JSON as a failure and raises `CddToolError` with that text. When the server cannot start or stops, it raises `CddNotConnectedError`. The application's pattern decides how each shows to the person.

### Testing

The Python domain keeps its own Mamba specs, and `{object}.{operation}` keeps its tool spec. An application's tests that call `{Object}NodeAdapter` run it against the real cdd server on a throwaway project, because a stubbed tool would still pass after the Python changed. A behavior both languages state keeps the same `should` sentence, so a sentence on one side only shows what is untested on the other. The generated routes and `{Object}ClientGenerated` are tested once, in the installer's specs, so an application tests its own subclass and not the paths between them.

---

## Generate

1. Follow **session_guidance**. Start from the Python: name the classes this slice exposes, read their `.context/`, and list their `@mcp @agent_tool` operations.
2. Add any missing domain operation and its Mamba spec first. Annotate `to_json()` and each operation's result with a `TypedDict`, and mark the class with `@language_adapter(language=..., identity=...)`: the application's language, such as `"typescript"`, and the field of `{Object}Data` that names the object.
3. Run `python scripts/install.py --ide Claude`. The language adapter follows, with the skills, commands, and MCP entry.
4. Point the `@cdd/*` path alias at `<install path>/language-adapters/typescript/`.
5. Construct one `CddConnection` on the application's server and mount every `{object}Routes` on it. Subclass `{Object}ClientGenerated` for what only the page knows. The application's pattern says where each lives.
6. Run the type-check, the tests, and validate. If validate fails, fix and validate again until it passes.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-routes.ts,**/*-node.ts,**/*-client.tsx,**/*-tools.ts,**/*-adapter.ts,**/cdd-connection*.ts"
```

Whenever you create, alter, or delete code outside Python that reaches the CDD domain, or the MCP tools it calls. Follow these rules.

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-code.mdc`. The `practices/ddd/ddd-tactics.mdc` rules apply to the Python domain classes.

### Domain and state

- **`domain-lives-in-python`** — Put every rule and decision in the Python domain class: what a state means, whether an action is allowed, what comes next. A rule written in another language is lost to the agent's tools and to every other door.
- **`state-lives-behind-the-tool`** — Get every fact about a CDD object from its adapter, and keep no repository, store, or cache of it beside the state the adapter's last call returned. The agent changes that state without telling the application, so a copy goes stale.

### One object, one set of generated classes

- **`one-class-per-object`** — Each domain object has its own generated `{Object}NodeAdapter` and `{Object}ClientGenerated` that call only that object's tools. Code that calls a tool by name, or posts to a tool's route by hand, has skipped the object's typed operation and hides which object owns it.
- **`adapter-is-generated`** — The installer writes `CddConnection`, `{Object}`, `{Object}NodeAdapter`, `{Object}ClientGenerated`, and `{object}Routes`, and nobody edits them or writes one by hand. Subclass `{Object}ClientGenerated` only for what the page alone knows, never to add a call, a route, or parsing. A hand-kept class drifts from Python, and the compiler then checks the wrong thing.
- **`mark-toolsets-that-return-data`** — Mark a toolset with `@language_adapter` when an application needs its results as data, and name its `identity` when a tool loads one object. Marking one that returns prompt text adds an adapter nobody can type.

### One line from adapter to domain

- **`one-line-to-the-domain`** — One adapter operation reaches one MCP tool, which calls one domain operation. Work spanning several calls belongs in a domain operation, so an agent and a person get the same result.
- **`tool-matches-the-object`** — Name the toolset after the Python object it acts on, so the tool reads `ticket.move_next`. A tool named after the component gathers every object's operations into one class.
- **`same-verb-across-layers`** — Use the same verb and noun from page to domain: `moveNext`, `/ticket/:ticket/move-next`, `ticket.move_next`, `Ticket.move_next`. A reader can then follow an action by searching one word.
- **`tool-stays-thin`** — A tool finds the domain object, calls one operation, and returns `to_json()`. Logic in a tool cannot be reached by anything that calls the domain directly.

### Contract and failure

- **`annotate-what-typescript-reads`** — Annotate `to_json()` and each MCP operation on a marked toolset with a `TypedDict`. A plain `dict[str, Any]` generates an open record, which the compiler cannot check.
- **`fail-loud-on-mcp`** — When a call fails or the server is missing, show the person what failed and how to fix it. Drawing old state as if it were current misleads them into acting on it.

### Testing

- **`test-the-adapter-against-real-cdd`** — Tests that call `{Object}NodeAdapter` run against a real cdd server on a throwaway project. A stubbed tool would pass after the Python changed.
- **`act-on-a-throwaway-project`** — Any test that moves, closes, or commits runs on a throwaway project with no real remote, because these tools really commit and push.
