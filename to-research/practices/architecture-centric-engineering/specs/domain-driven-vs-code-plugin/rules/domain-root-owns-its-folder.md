---
scanner: domain_structure_scanner.py
---

# Rule: Domain Root Owns Its Folder

Each domain class that is the **root of a concept** gets its own named folder under `src/`. That folder contains the domain entity, its server extension, and a `view/` subfolder for server-view and client files. This layout is the structural contract — scanners and engineers read the folder to understand what a concept owns.

A **root** is any class that has its own identity, state, and behaviour that other parts of the system depend on. `Engine` and `Counter` are both roots. Sub-concepts that have no independent lifecycle live as methods or value objects on the root, not in their own folder.

## DO

- Give each domain root a folder named after it: `src/engine/`, `src/counter/`.
- Place the domain entity file at the root of the folder: `src/counter/counter.ts`.
- Place the server extension in the same folder: `src/counter/counter_server.ts`.
- Place all view files (server view, client, HTML, CSS) under `view/` inside the folder.
- Place shared base infrastructure (BaseView) in the engine folder: `src/engine/base_view.ts`.

```
src/
  engine/           ← Engine is a domain root
    engine.ts
    base_view.ts    ← shared base lives with the root that owns it
    view/
      engine_view.ts
      engine_client.ts
      Engine.html
      layout.css
  counter/          ← Counter is a domain root
    counter.ts
    counter_server.ts
    view/
      counter_view.ts
      counter_client.ts
      Counter.html
      counter.css
```

## DON'T

- Don't put domain roots in a flat `src/` namespace with no folder.
- Don't scatter server extensions away from the domain entity they extend.
- Don't put view files at the same level as the domain entity — they belong in `view/`.
- Don't create a folder for a concept that has no independent lifecycle (e.g. `IFoo` is not a root, it lives on `Counter`).

```
// WRONG — flat namespace, no domain root folders
src/
  counter.ts
  counter_server.ts
  counter_view.ts
  engine.ts
  engine_view.ts
```

```
// WRONG — server extension separated from domain entity
src/
  domain/
    counter.ts
  server/
    counter_server.ts
```
