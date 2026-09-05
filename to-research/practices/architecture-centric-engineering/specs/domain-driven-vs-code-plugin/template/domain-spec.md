# Domain Spec — Counter / Engine (VS Code Plugin)

## Domain Roots

| Root | Folder | Role |
|------|--------|------|
| Engine | `src/engine/` | Composition root; assembles counters, owns webview panel lifecycle |
| Counter | `src/counter/` | Domain entity; counts and resets; extended by CounterServer for persistence |

## Concepts

| Concept | Type | Owner | Notes |
|---------|------|-------|-------|
| `ICounter` | Interface | Counter | Shared contract: `count(amount)`, `reset()`, `total` |
| `Counter` | Domain entity | Counter | Pure TS; implements ICounter; no persistence, no platform |
| `CounterServer` | Server domain | Counter | Extends Counter; adds `_load/_save` via Node `fs` |
| `IFoo` | Interface | Counter | Sub-concept on Counter; not a root |
| `Engine` | Domain root | Engine | Holds named counters; owns `add(name)`, `get(name)` |
| `BaseView` | Shared base | Engine | Template rendering and HTML escaping; no domain coupling |
| `EngineView` | Server view | Engine | Manages webview panel; dispatches commands via `_lookup` |
| `CounterView` | Server view | Counter | Wraps Counter; calls `postMessage` after every mutation |
| `engine_client.ts` | Client | Engine | Webview entry point; routes messages to counter client |
| `counter_client.ts` | Client | Counter | DOM adapter; implements ICounter; syncs to server |

## Interfaces

```typescript
// ICounter — shared by domain, server domain, server view, and client DOM adapter
export interface ICounter {
  count(amount: number | string): void;
  reset(): void;
  readonly total: number;
}
```

## Key Relationships

- `CounterServer extends Counter` — inherits domain behaviour, adds persistence
- `CounterView implements ICounter` — satisfies the interface for use in tests and by Engine
- `domCounter implements ICounter` — client-side implementation driven by the same test base
- `EngineView` holds `CounterView` references; routes postMessage commands via `_lookup`
- `Engine` holds a map of named `ICounter` instances; `engine.ts` is the composition root domain

## Layer Constraints

| File pattern | Allowed imports | Forbidden imports |
|---|---|---|
| `src/<domain>/<domain>.ts` | Other `src/<domain>` files | `vscode`, `fs`, DOM, Node APIs |
| `src/<domain>/<domain>_server.ts` | Domain entity, `fs`, `path` | `vscode`, DOM |
| `src/<domain>/view/<domain>_view.ts` | Domain entity, BaseView, `vscode` | `fs`, DOM |
| `src/<domain>/view/<domain>_client.ts` | Domain class (bundled), DOM | `vscode` (extension API), `fs` |
