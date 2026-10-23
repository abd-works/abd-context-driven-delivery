---
name: patterns-lern-domain-driven
description: >-
  ## Overview
  
  Implementation fidelity for a **domain-module-organized LERN stack** ([lowdb](https://github.com/typicode/lowdb)
  JSON files / Express / React / Node, TypeScript everywhere) on an already-designed
  vertical slice — story map, module boundaries, and screens all exist before this
  tool runs. `generate` calls `self._stories()` at `acceptance_tests` /
  `typescript` — specs first, then Stories' own `ce()` wires matching
  production TypeScript. The rules below are additive on top of what Stories
  and CleanEngineering already enforce, not a restatement of them.
  
  **No fidelity progression of its own.** Every run pins `stories` at
  `acceptance_tests` with `format="typescript"`; production code arrives via
  Stories' `ce()` companion at `code` / `typescript`.
  
  One aggregate. `{Domain}Client` and `{Domain}Node` extend `{Domain}`. The view paints the client. The route asks the node. `{Domain}Repository` is in-memory. `{Domain}RepositoryNode` extends it, runs Zod `.parse()`, and writes `<aggregate>.json`.
  
  | Layer | File | Role |
  |---|---|---|
  | Boot | `packages/<epicSlug>/app.ts`, `serve.ts`, `main.tsx` | Start Express and Vite. Mount the first view. |
  | View | `src/…/<aggregate>/<screen-slug>.tsx` | Hold the client in React state. Paint fields and actions. |
  | Client | `<aggregate>-client.tsx` | `{Domain}Client`. Field changes return a new instance. Call the route. |
  | Routes | `<aggregate>-routes.ts` | Parse the request. Call the node. Return `destination`. |
  | Node | `<aggregate>-node.ts` | `{Domain}Node` maps the step to a path. `{Domain}RepositoryNode` runs Zod `.parse()` and writes `<aggregate>.json`. |
  | Domain | `<aggregate>.ts` | `{Domain}`, `{SubDomain}`, in-memory `{Domain}Repository`. Framework-free. |
  | Store | `<aggregate>.json` | One lowdb file. `{Domain}RepositoryNode` is the only writer. |
  
  1. Boot mounts the view for the current path.
  2. The view constructs `{Domain}Client` and paints its fields.
  3. A field edit replaces React state with a new client.
  4. Submit calls the aggregate route.
  5. The route builds `{Domain}Node` and runs the domain operation.
  6. The node calls `{Domain}RepositoryNode` (`load`, `create`, `search`, or `update`).
  7. `{Domain}RepositoryNode` runs Zod `.parse()` and writes `<aggregate>.json`. `{Domain}Repository` stays in memory.
  8. The route asks `{Domain}Node.destination` and returns that path.
  9. The next view in the aggregate folder mounts.
  
  ```mermaid
  classDiagram
    class Domain {
      <<aggregate root>>
      +operation()
    }
    class ValueObject {
      <<value object>>
    }
    class Repository {
      <<in memory>>
      +load(id)
      +create(input)
      +search(query)
      +update(root)
    }
    class RepositoryNode {
      +parse()
      +write()
    }
    class DomainNode {
      +destination()
    }
    class DomainClient {
      +withField()
    }
    class View {
      <<React>>
    }
    class Routes
    class JsonStore {
      <<lowdb>>
    }
  
    Domain <|-- DomainNode
    Domain <|-- DomainClient
    Domain o-- ValueObject
    Repository ..> Domain : root
    Repository <|-- RepositoryNode
    DomainNode --> RepositoryNode
    RepositoryNode --> JsonStore
    View --> DomainClient : renders
    DomainClient --> Routes : HTTP
    Routes --> DomainNode : asks
  ```
  
  ```mermaid
  sequenceDiagram
    actor User
    participant Boot
    participant View
    participant Client as DomainClient
    participant Routes
    participant Node as DomainNode
    participant Repository as RepositoryNode
    participant Store as JsonStore
  
    Boot->>View: mount screen
    View->>Client: new client
    User->>View: edit field
    View->>Client: withField
    Client-->>View: new client
    User->>View: submit
    View->>Client: host operation
    Client->>Routes: HTTP
    Routes->>Node: domain operation
    Node->>Repository: create or update
    Repository->>Store: Zod parse, write JSON
    Store-->>Repository: root
    Repository-->>Node: root
    Routes->>Node: destination
    Node-->>Routes: next path
    Routes-->>View: next path
    View->>View: mount next view
  ```
  
  ---
---

overview

Use MCP tool: `lern-domain-driven.instructions()`
