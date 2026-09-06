# Architecture Specification: Domain-Driven VS Code Plugin

**Stack:** TypeScript / Node.js / VS Code Extension API  
**Template domain:** Counter / Engine  
**Template:** [`template/`](template/)  
**Scaffold:** [`templates/`](templates/)  
**Rules:** [`rules/`](rules/)  
**Scanners:** [`scanners/typescript/`](scanners/typescript/)

---

## Purpose

This specification describes a domain-driven approach to building VS Code (and Cursor) panel extensions. Business logic lives in pure TypeScript domain classes that run without VS Code, without a file system, and without a browser. The extension host and webview are thin adapters: the extension host extends domain classes for persistence; the webview bundles the same domain classes for client-side state.

The architecture scales to any number of domain concepts. Each concept follows the same structural contract: one folder, one entity, one server extension, one view pair.

---

## Instantiating the Domain

### Principles

1. **Domain roots own their folders.** A class is a root if it has independent identity and state. Give it `src/<name>/`. Sub-concepts live as methods or properties on the root.
2. **Domain entities are pure TypeScript.** No `vscode`, no `fs`, no DOM. The same class runs in tests, in the extension host, and in the webview bundle.
3. **Server extensions add persistence by inheriting, not wrapping.** `CounterServer extends Counter` — the interface stays intact, persistence is layered on.
4. **The webview bundles the domain class.** There is no separate DTO. Client and server share identity through the same class.
5. **Adapt to each VS Code surface with extend-or-wrap.** See decision below.

### Extend-or-Wrap Decision

Every VS Code surface needs an adapter. Choose the pattern based on what the adapter *is*:

**Extend** when the adapter IS the domain concept plus one new capability. The extension class calls `super(...)`, computes new properties, and satisfies the same or a compatible interface. No platform import required if TypeScript structural typing covers the surface contract.

```
CounterServer extends Counter        — IS-A counter that also persists
ModelPickItem extends Model          — IS-A model that also has Quick Pick shape (label/description/detail)
```

**Wrap** when the adapter HAS the domain as a dependency but also owns VS Code lifecycle objects (panel, `StatusBarItem`, provider registration). Wrapping is correct when the adapter's constructor takes VS Code objects the domain class cannot accept.

```
CounterView(panel, counter, uri)     — HAS-A counter + owns WebviewPanel
StatusBarAdapter(item, domain)       — HAS-A StatusBarItem + observes domain state
ChatProviderAdapter(catalog, client) — HAS-A catalog + satisfies vscode.lm provider callbacks
```

| Surface | Pattern | Class name convention |
|---|---|---|
| Persistence | **Extends** domain | `<Domain>Server` |
| Quick Pick presentation | **Extends** domain | `<Domain>PickItem` |
| Webview view | **Wraps** domain + implements interface | `<Domain>View` |
| Status bar | **Wraps** domain state | `<Domain>StatusBar` |
| LM chat provider | **Wraps** catalog + client | `<Domain>ChatProvider` |
| Command handlers | Standalone functions | `run<Action>Command(deps)` |

### Architecture Flow

```
User clicks button in webview
  → client DOM adapter (counter_client.ts) calls counter.count(amount)
  → vscode.postMessage({ command: 'count', args: [amount] }) sent to extension host
  → EngineView._lookup('count') resolves to CounterView.count
  → CounterView.count() calls CounterServer.count(amount)
  → CounterServer.count() calls super.count(amount) + _save()
  → CounterView posts { total: counter.total } back to webview
  → webview onmessage updates DOM
```

### Module Layout

```
src/
  engine/                   ← composition root
    engine.ts               ← root domain: holds named counters
    base_view.ts            ← shared: template rendering, HTML escaping
    view/
      engine_view.ts        ← server view: manages webview panel, routes commands
      engine_client.ts      ← client: webview entry, routes to domain clients
      Engine.html           ← webview shell template
      layout.css
  counter/                  ← domain root
    counter.ts              ← domain entity + ICounter interface
    counter_server.ts       ← server domain: CounterServer extends Counter + _load/_save
    view/
      counter_view.ts       ← server view: CounterView implements ICounter + postMessage
      counter_client.ts     ← client DOM adapter: domCounter implements ICounter
      Counter.html
      counter.css
  extension.ts              ← VS Code activation: registers command, mounts EngineView
test/
  counter/
    counter_test.ts         ← shared behaviour base (Template Method)
    counter.test.ts         ← domain + server domain tier tests
    counter_view.test.ts    ← server view tests (VS Code mock)
    counter_client.test.ts  ← client DOM adapter tests (jsdom)
  __mocks__/
    vscode.ts               ← minimal VS Code API mock for Vitest
```

### Participants

| Class | Layer | Implements | Extends |
|-------|-------|------------|---------|
| `Counter` | Domain | `ICounter` | — |
| `CounterServer` | Server domain | `ICounter` (via inheritance) | `Counter` |
| `CounterView` | Server view | `ICounter` | `BaseView` |
| `domCounter` | Client | `ICounter` (object literal) | — |
| `Engine` | Domain root | — | — |
| `EngineView` | Server view | — | `BaseView` |
| `BaseView` | Shared infra | — | — |

All four `ICounter` implementations run the same `CounterTest.registerTests()` suite, each adding tier-specific assertions on top.

### Layer Constraints

| File | May import | Must not import |
|------|-----------|-----------------|
| `<domain>.ts` | Other domain files | `vscode`, `fs`, `path`, `os`, DOM |
| `<domain>_server.ts` | Domain entity, `fs`, `path` | `vscode`, DOM |
| `<domain>_view.ts` | Domain entity, `BaseView`, `vscode` | `fs`, DOM APIs |
| `<domain>_client.ts` | Domain class (bundled) | `vscode` extension API, `fs` |

---

## Mechanism: Persistence

### Principles and Patterns

- **Extend, don't wrap.** `CounterServer extends Counter` keeps the full `ICounter` interface intact. No repository object is needed.
- **Load in constructor, save on mutation.** `_load()` in the constructor restores state from disk. Each override of a mutation method calls `_save()` after `super`.
- **File-based state.** State is serialized as JSON to a file whose path is injected at construction time. No database, no environment-specific config.
- **Inject the file path.** The path comes from the caller (typically `extension.ts` using `context.globalStorageUri`). The domain class has no opinion about where files live.

### File Structure

```
src/<domain>/
  <domain>_server.ts       ← CounterServer extends Counter; _load/_save
```

### Participants

| Class | Role |
|-------|------|
| `CounterServer` | Server domain: extends `Counter`; adds `_load()` in constructor; overrides `count()` and `reset()` to call `_save()` |
| `fs` (Node) | Persistence mechanism; imported only in `<domain>_server.ts` |

### Flow

```
EngineView.createOrShow(context.extensionUri)
  → new CounterServer(context.globalStorageUri.fsPath + '/counter.json')
  → CounterServer constructor calls this._load()
  → fs.readFileSync reads saved JSON → super.count(data.total) restores state

CounterView.count(amount)
  → super.count(amount)         [CounterServer inherits from Counter]
  → this._save()                [CounterServer writes JSON to disk]
  → postMessage({ total })      [CounterView notifies webview]
```

### Walkthrough Example

```typescript
// src/counter/counter_server.ts
import * as fs from 'fs';
import { Counter } from './counter.js';

export class CounterServer extends Counter {
  private _filePath: string;

  constructor(filePath: string) {
    super();
    this._filePath = filePath;
    this._load();            // restore persisted state immediately
  }

  override count(amount: number | string): void {
    super.count(amount);
    this._save();            // persist after every mutation
  }

  override reset(): void {
    super.reset();
    this._save();
  }

  private _load(): void {
    if (!fs.existsSync(this._filePath)) return;
    const data = JSON.parse(fs.readFileSync(this._filePath, 'utf-8'));
    if (typeof data.total === 'number') super.count(data.total);
  }

  private _save(): void {
    fs.writeFileSync(this._filePath, JSON.stringify({ total: this.total }));
  }
}
```

---

## Mechanism: Webview Bridge

### Principles and Patterns

- **Template rendering via BaseView.** `renderTemplate(templatePath, substitutions)` reads the HTML file, replaces `{{key}}` tokens, escapes user data. All server views extend `BaseView`; no raw string concatenation.
- **postMessage is the only channel.** Server → client: `panel.webview.postMessage(payload)`. Client → server: `vscode.postMessage({ command, args })`. No shared memory, no event emitters.
- **Command dispatch via `_lookup`.** The server view maps command strings to `[target, method]` pairs. `EngineView` delegates commands to sub-views by calling `_lookup` on the correct view.
- **The client bundles the domain class.** The esbuild/webpack bundle for the webview includes `Counter`. The DOM adapter implements `ICounter` using this local instance, then syncs to the server via postMessage after every mutation.
- **`acquireVsCodeApi()` is called once.** The result is passed into initialisation functions so it can be stubbed in tests.

### File Structure

```
src/engine/
  base_view.ts               ← renderTemplate, escapeHtml
  view/
    engine_view.ts           ← manages panel; routes commands via _lookup
    engine_client.ts         ← webview entry; routes to domain clients
    Engine.html

src/<domain>/
  view/
    <domain>_view.ts         ← CounterView: wraps counter; postMessage after mutations
    <domain>_client.ts       ← DOM adapter: implements ICounter; syncs to server
    <Domain>.html
```

### Participants

| Class / function | Side | Role |
|-----------------|------|------|
| `BaseView` | Server | Template rendering; HTML escaping |
| `EngineView` | Server | Manages VS Code `WebviewPanel`; receives postMessage from client; dispatches to sub-view via `_lookup` |
| `CounterView` | Server | Wraps `CounterServer`; implements `ICounter`; sends `{ total }` to client after mutations |
| `engine_client.ts` | Client | Webview entry point; calls `acquireVsCodeApi()` once; routes to `initCounterClient` |
| `domCounter` | Client | DOM adapter; implements `ICounter`; updates DOM; posts mutations back to server |

### Flow

```
Client (webview)                              Server (extension host)
────────────────                              ──────────────────────
User clicks "Count"
→ domCounter.count(1)
  → updates local Counter + DOM
  → vscode.postMessage({ command: 'count', args: [1] })
                                              → EngineView receives message
                                              → EngineView._lookup('count')
                                                  → returns [counterView, 'count']
                                              → counterView.count(1)
                                                  → CounterServer.count(1)
                                                  → _save()
                                                  → postMessage({ total: 1 })
← window.onmessage({ total: 1 })
  → reconcile domCounter + update DOM span
```

### Walkthrough Example

```typescript
// src/counter/view/counter_view.ts
export class CounterView extends BaseView implements ICounter {
  constructor(
    readonly panel: WebviewPanel,
    private _counter: ICounter,
    extensionUri: Uri
  ) { super(extensionUri); }

  count(amount: number | string): void {
    this._counter.count(amount);
    this.panel.webview.postMessage({ total: this._counter.total });
  }

  reset(): void {
    this._counter.reset();
    this.panel.webview.postMessage({ total: this._counter.total });
  }

  get total(): number { return this._counter.total; }

  _lookup(pathStr: string): [object, string] {
    return { count: [this, 'count'], reset: [this, 'reset'] }[pathStr]
      ?? [this, pathStr];
  }

  getHtml(): string {
    return this.renderTemplate('counter/view/Counter.html', {
      total: String(this.total),
    });
  }
}
```

```typescript
// src/counter/view/counter_client.ts (runs in webview bundle)
import { Counter } from '../counter.js';

export function initCounterClient(vscode: { postMessage(m: unknown): void }) {
  const counter = new Counter();   // local copy — same class as server

  const domCounter = {
    count(amount: number | string) {
      counter.count(amount);
      document.getElementById('total')!.textContent = String(counter.total);
      vscode.postMessage({ command: 'count', args: [amount] });
    },
    reset() {
      counter.reset();
      document.getElementById('total')!.textContent = '0';
      vscode.postMessage({ command: 'reset', args: [] });
    },
    get total() { return counter.total; },
  };

  window.addEventListener('message', ({ data }: { data: { total: number } }) => {
    counter.count(data.total - counter.total);   // reconcile to authoritative server total
    document.getElementById('total')!.textContent = String(data.total);
  });

  return domCounter;
}
```

---

## Mechanism: Commands

### Principles and Patterns

- **Commands are a user surface AND the shared invocation protocol.** The Command Palette, keyboard shortcuts, right-click menus, status bar clicks, and notification action buttons all funnel through registered commands. Every other surface invokes actions by firing a command id.
- **Define in `package.json`, register in `extension.ts`.** `contributes.commands` declares the command (id, title, category) so VS Code can show it in the palette. `registerCommand(id, handler)` wires the id to code. The id must match exactly.
- **Handler functions are standalone and injectable.** Each command is handled by a `run<Action>Command(deps)` function in `src/<domain>/` or `src/engine/`. Handlers receive dependencies as a typed `deps` object — no globals, no singletons. This makes them testable without VS Code.
- **`registerCommands()` in `extension.ts` is a flat dispatch table.** One array of `[id, handler]` pairs, looped once. No logic lives there — logic lives in the handler functions.

### File Structure

```
src/extension.ts           ← registerCommands() — flat [id, handler] table
src/<domain>/
  <domain>_commands.ts     ← run<Action>Command(deps) handler functions
src/engine/
  engine_commands.ts       ← engine-level commands (open panel, reset all, etc.)
package.json               ← contributes.commands: id + title + category
```

### Participants

| | Role |
|---|---|
| `package.json` | Declares command ids, titles, and categories to VS Code |
| `registerCommands()` | Wires each id to its handler; pushes disposables to `context.subscriptions` |
| `run<Action>Command(deps)` | Standalone async function; calls `vscode.window.*` or domain methods via `deps` |
| `deps` object | Injected: domain instance, output channel, client factory, etc. |

### Flow

```
User types "Counter: Reset" in Command Palette
  → VS Code fires 'extension.resetCounter'
  → registerCommands() table → runResetCounterCommand(deps)
  → deps.counterServer.reset()
  → deps.output.appendLine('[counter] reset')
  → vscode.window.showInformationMessage('Counter reset.')
```

### Walkthrough Example

Scenario: user activates "Counter: Reset" from the Command Palette.

1. **`package.json`** declares `{ "command": "extension.resetCounter", "title": "Reset Counter", "category": "Counter" }` so VS Code lists it in the palette.
2. **`extension.ts` / `registerCommands()`** receives the activation event; loops the `[id, handler]` table and calls `vscode.commands.registerCommand('extension.resetCounter', handler)`.
3. **VS Code** fires the command id when the user selects it; calls the registered handler closure.
4. **`runResetCounterCommand(deps)`** in `counter_commands.ts` calls `deps.counterServer.reset()`, appends a log line to `deps.output`, then calls `vscode.window.showInformationMessage`.
5. **`CounterServer`** resets its state and calls `_save()` to persist; returns control to the handler.
6. **VS Code** displays the information message toast to the user.

```typescript
// src/counter/counter_commands.ts
export async function runResetCounterCommand(
  deps: { counterServer: ICounter; output: vscode.OutputChannel }
): Promise<void> {
  deps.counterServer.reset();
  deps.output.appendLine('[counter] reset');
  await vscode.window.showInformationMessage('Counter reset.');
}
```

### Testing the Mechanism

**Domain tier** — test `runResetCounterCommand` by passing a mock `ICounter` and a mock `OutputChannel`; assert `reset()` was called and a log line was appended. No `vscode` import needed in the test.

**Integration tier** — test `registerCommands()` by verifying the `[id, handler]` table is wired correctly; spy on `vscode.commands.registerCommand` with `test/__mocks__/vscode.ts`.

See **Testing Architecture** for the `vscode` mock setup shared by all tiers.

---

## Mechanism: Native VS Code Interaction

### Principles and Patterns

- **Quick Pick items extend the domain class.** A selectable concept owns its own presentation shape (`label`, `description`, `detail`). `ModelPickItem extends Model` — IS-A model that also satisfies `vscode.QuickPickItem` by structural typing (no `vscode` import needed in the extension class). The surface adapter constructs items and passes them to `showQuickPick`.
- **Notifications carry action buttons that fire commands.** `showInformationMessage(text, ...buttons)` returns the clicked button string. Buttons invoke `vscode.commands.executeCommand` — they do not contain inline logic.
- **Output channel is a log sink, not a surface.** Create once in `activate()`, pass as `deps.output`. All handlers and providers receive it; none create their own.
- **Input box for single-value text input.** `showInputBox({ prompt, password })` returns the entered string or `undefined` if cancelled.

### File Structure

```
src/<domain>/
  <domain>_pick_item.ts    ← <Domain>PickItem extends <Domain>; no vscode import
  <domain>_commands.ts     ← run<Action>Command(deps) — calls showQuickPick / showInputBox / showInformationMessage
src/engine/
  engine_commands.ts       ← engine-level commands
src/extension.ts           ← createOutputChannel once; pass as deps
```

### Participants

| Class / function | Role |
|---|---|
| `<Domain>PickItem extends <Domain>` | Domain extension with `label`, `description`, `detail`; no vscode import; satisfied by structural typing |
| `run<Action>Command(deps)` | Calls `vscode.window.showQuickPick` / `showInputBox` / `showInformationMessage`; receives domain data and output channel via `deps` |
| `vscode.OutputChannel` | Logging sink; created once in `activate()`; injected everywhere |

### Flow

```
User runs "Counter: Browse History" from Command Palette
  → runBrowseHistoryCommand(deps)
  → deps.counterServer.history()        — pure domain call, returns Entry[]
  → entries.map(e => new EntryPickItem(e))  — extend domain; no vscode
  → vscode.window.showQuickPick(items)  — VS Code renders the list
  → picked.entry.id                     — back to domain types
```

### Walkthrough Example

Scenario: user activates "Counter: Browse History" from the Command Palette.

1. **`runBrowseHistoryCommand(deps)`** in `counter_commands.ts` calls `deps.counterServer.history()` to retrieve a list of `Counter` snapshots — a pure domain call with no VS Code dependency.
2. **`runBrowseHistoryCommand`** maps each snapshot to a `CounterPickItem` (a pure extension of `Counter` with `label`, `description`, `detail`; no `vscode` import in `counter_pick_item.ts`).
3. **`vscode.window.showQuickPick(items)`** receives the item array; renders the list; returns the item the user selected or `undefined` if they dismissed.
4. **`runBrowseHistoryCommand`** checks `picked`; if defined, appends a log line to `deps.output` and calls `vscode.window.showInformationMessage` to confirm the selection to the user.

```typescript
// src/counter/counter_pick_item.ts — no vscode import
export class CounterPickItem extends Counter {
  readonly label: string;
  readonly description: string;
  readonly detail: string;
  constructor(source: Counter, readonly snapshotLabel: string) {
    super();
    if (source.total > 0) this.count(source.total);
    this.label       = snapshotLabel;
    this.description = `total: ${this.total}`;
    this.detail      = this.total > 100 ? '⚠ high count' : 'normal range';
  }
}
```

### Testing the Mechanism

**Domain tier** — test `CounterPickItem` independently: construct from a known `Counter`, assert `label`, `description`, and `detail` produce the correct strings. No `vscode` import; no mock needed.

**Integration tier** — test `runBrowseHistoryCommand` by passing mock snapshots and a stub `vscode.window.showQuickPick` (via `test/__mocks__/vscode.ts`); assert `output.appendLine` and `showInformationMessage` are called with the expected values when a pick is made, and not called when dismissed.

See **Testing Architecture** for the `vscode` mock setup shared by all tiers.

---

## Mechanism: Status Bar

### Principles and Patterns

- **Status bar is a persistent output adapter — wrap only.** It owns a `vscode.StatusBarItem` and observes domain state. It never receives domain mutations — extend does not apply. Use `<Domain>StatusBar` as the class name.
- **`setState(data)` is the only public mutation.** Domain state flows in through one typed method; the adapter translates it to VS Code text and tooltip format. Domain classes have no `vscode` import — tooltip markdown is built by a pure method on the domain class (`toStatusBarMarkdown()`), then wrapped in `new vscode.MarkdownString(...)` in the adapter.
- **Click fires a command.** `item.command = 'extension.someCommand'` — the status bar never handles logic inline.
- **Create once in `activate()`, push to `context.subscriptions`.** The adapter implements `vscode.Disposable`.

### File Structure

```
src/<domain>/
  <domain>_status_bar.ts   ← <Domain>StatusBar: owns StatusBarItem; setState(data); refresh()
src/<domain>/
  <domain>.ts              ← toStatusBarMarkdown(): string — pure, no vscode import
```

### Participants

| Class | Role |
|---|---|
| `<Domain>StatusBar` | Wraps `StatusBarItem`; owns lifecycle; exposes `setState(data)` and `dispose()` |
| `<domain>.toStatusBarMarkdown()` | Pure method on domain class; returns markdown string; no vscode import |

### Flow

```
Domain mutation occurs
  → caller calls statusBar.setState({ total: counter.total, label: 'counter' })
  → <Domain>StatusBar.refresh()
      → item.text = `$(circuit-board) counter: ${data.total}`
      → item.tooltip = new vscode.MarkdownString(domain.toStatusBarMarkdown())
      → item.show()
```

### Walkthrough Example

Scenario: `CounterServer.reset()` is called; the status bar must reflect the new total.

1. **`extension.ts`** (or a command handler) calls `counterStatusBar.setState({ counter: counterServer, label: 'counter' })` after the mutation.
2. **`CounterStatusBar.setState()`** stores the state and calls `_refresh()`.
3. **`CounterStatusBar._refresh()`** reads `counter.total` and sets `item.text` to the formatted string (e.g. `$(circuit-board) counter: 0`).
4. **`Counter.toStatusBarMarkdown()`** — a pure method on the domain class with no `vscode` import — returns the markdown string for the tooltip.
5. **`CounterStatusBar._refresh()`** wraps the string in `new vscode.MarkdownString(...)` and assigns it to `item.tooltip`; calls `item.show()`.
6. **VS Code** renders the updated text and tooltip in the status bar.

```typescript
// src/counter/counter_status_bar.ts
export class CounterStatusBar implements vscode.Disposable {
  private _item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  private _state?: CounterStatusBarState;
  constructor() { this._item.command = 'extension.resetCounter'; }
  setState(state: CounterStatusBarState): void { this._state = state; this._refresh(); }
  private _refresh(): void {
    if (!this._state) { this._item.hide(); return; }
    const { counter, label } = this._state;
    this._item.text    = `$(circuit-board) ${label}: ${counter.total}`;
    this._item.tooltip = new vscode.MarkdownString(counter.toStatusBarMarkdown());
    this._item.show();
  }
  dispose(): void { this._item.dispose(); }
}
```

### Testing the Mechanism

**Domain tier** — test `Counter.toStatusBarMarkdown()` directly: assert the returned string contains the expected total and conditional warning text. Pure function; no mock.

**Integration tier** — test `CounterStatusBar.setState()` with a stub `StatusBarItem` (via `test/__mocks__/vscode.ts`); assert `item.text`, `item.tooltip`, and `item.show()` are called with the expected values. Assert `item.hide()` is called when state is cleared.

See **Testing Architecture** for the `vscode` mock setup shared by all tiers.

---

## Mechanism: Language Model Chat Provider

### Principles and Patterns

- **VS Code calls you — you don't initiate.** Register once with `vscode.lm.registerLanguageModelChatProvider(vendor, provider)`. VS Code calls `provideLanguageModelChatInformation` for the model list and `provideLanguageModelChatResponse` when a user sends a message using one of your models.
- **Message mapping is pure domain logic.** The function that converts `LanguageModelChatMessage[]` to the backing API format has no `vscode` import — it takes typed inputs and returns typed outputs. The adapter calls it before making any network request.
- **Stream response tokens via `progress.report()`.** For each text chunk, call `progress.report(new vscode.LanguageModelTextPart(chunk))`. Wire `token.onCancellationRequested` to abort the stream.
- **Wrap the catalog and client — do not extend.** The provider adapter holds `catalog: ModelDef[]` and `client: ApiClient` as dependencies. It satisfies VS Code's provider callbacks but is not itself a domain concept.
- **Feature-detect at registration time.** `vscode.lm.registerLanguageModelChatProvider` is not available in older VS Code builds. Check for its existence before registering; log gracefully if unavailable.

### File Structure

```
src/engine/
  engine_chat_provider.ts  ← EngineChatProvider: registers with vscode.lm; wraps catalog + client
src/<domain>/
  <domain>_message_mapper.ts  ← pure: maps LanguageModelChatMessage[] → ApiRequest; no vscode import
```

### Participants

| Class / function | Side | Role |
|---|---|---|
| `EngineChatProvider` | Extension host | Registers with `vscode.lm`; calls `provideLanguageModelChatInformation` and `provideLanguageModelChatResponse` |
| `<Domain>MessageMapper` | Extension host | Pure: maps VS Code message types to backing API format; no vscode import; unit-testable |
| `progress` | VS Code runtime | Receives streamed text parts via `progress.report()` |

### Flow

```
User selects your model in Copilot chat
  → VS Code calls provideLanguageModelChatInformation()
  → EngineChatProvider returns buildProviderModels(catalog)   — pure domain fn

User sends a message
  → VS Code calls provideLanguageModelChatResponse(model, messages, options, progress, token)
  → MessageMapper.map(messages)                                — pure, no vscode
  → client.createChatCompletionStream(request)
  → for await chunk: progress.report(new LanguageModelTextPart(text))
  → token.onCancellationRequested → handle.abort()
```

### Walkthrough Example

Scenario: user selects the extension's model in Copilot chat and sends a message.

1. **VS Code** calls `provideLanguageModelChatInformation()` on **`EngineChatProvider`** to build the model list; the method delegates to `buildProviderModels(this._catalog)` — a pure function with no `vscode` import.
2. **VS Code** calls `provideLanguageModelChatResponse(model, messages, options, progress, token)` on **`EngineChatProvider`** when the user sends a chat message.
3. **`EngineChatProvider._handleRequest()`** calls `MessageMapper.map(messages, model.id)` — a pure static method in `message_mapper.ts` with no `vscode` import — to translate the VS Code message array to the backing API request shape.
4. **`EngineChatProvider._handleRequest()`** calls `this._client.stream(request)` to open a streaming connection; registers `token.onCancellationRequested` to abort the stream if the user cancels.
5. **`EngineChatProvider._handleRequest()`** iterates the async stream; for each chunk calls `progress.report(new LanguageModelTextPart(chunk.text))` to stream text back to the chat panel.
6. **VS Code** renders each streamed token in the Copilot chat response pane as it arrives.

```typescript
// src/engine/message_mapper.ts — no vscode import
export class MessageMapper {
  static map(messages: readonly { role: number; content: unknown[] }[], modelId: string): ApiRequest {
    return { model: modelId, messages: messages.map(mapMessage), stream: true };
  }
}
```

### Testing the Mechanism

**Domain tier** — test `MessageMapper.map()` directly: pass a fixed array of message shapes, assert the returned `ApiRequest` has the correct model id and translated messages. No `vscode` import; no mock.

**Integration tier** — test `EngineChatProvider._handleRequest()` with a stub `ApiClient` that yields known chunks; a stub `progress` object; and a stub `CancellationToken`. Assert `progress.report` is called once per chunk with the expected text. Assert `handle.abort()` is called on cancellation.

**Feature-detect path** — test `EngineChatProvider.register()` when `vscode.lm` is undefined or missing the method; assert `_output.appendLine` logs the unavailability message and no registration is attempted.

See **Testing Architecture** for the `vscode` mock setup shared by all tiers.

---

## Grill Me — Map a Story to a Surface

When implementing a new story, answer these questions to choose the right surface and adapter pattern:

**1. What triggers the story?**
- User types in Command Palette or uses keyboard shortcut → **Commands**
- User interacts with a rich HTML panel → **Webview Bridge**
- A model is selected in Copilot chat → **Language Model Chat Provider**
- User needs a quick selection or text input (modal) → **Native Interaction**
- Story needs always-visible ambient state in the bottom bar → **Status Bar**

**2. What does the story output?**
- Rich UI with HTML/CSS → **Webview Bridge**
- A list to pick from → **Native Interaction (Quick Pick)**
- A text prompt → **Native Interaction (Input Box)**
- A short message with optional action buttons → **Native Interaction (Notification)**
- A log line → `deps.output.appendLine(...)` — no separate mechanism
- AI chat completion tokens → **Language Model Chat Provider**
- Ambient status indicator → **Status Bar**

**3. Does the domain concept present itself on this surface?**
- It IS the concept plus a selectable shape → **extend** (`<Domain>PickItem extends <Domain>`)
- It IS the concept plus persistence → **extend** (`<Domain>Server extends <Domain>`)
- It HAS the concept as a dependency + owns VS Code lifecycle objects → **wrap**

**4. Does state need to persist between sessions?**
- Yes → `<Domain>Server extends <Domain>` with `_load/_save`
- No → plain domain class

**5. Does the story involve streaming AI completions?**
- Yes → **Language Model Chat Provider**
- No → other surfaces

---

## Rules

| Rule | File | Scanner |
|------|------|---------|
| Domain root owns its folder | [`rules/domain-root-owns-its-folder.md`](rules/domain-root-owns-its-folder.md) | `domain_structure_scanner.py` |
| Domain layer has no platform imports | [`rules/domain-layer-has-no-platform-imports.md`](rules/domain-layer-has-no-platform-imports.md) | `domain_purity_scanner.py` |
| Server domain extends the domain class | [`rules/server-domain-extends-domain.md`](rules/server-domain-extends-domain.md) | `server_domain_scanner.py` |
| Server view extends BaseView and uses postMessage | [`rules/server-view-extends-base-view.md`](rules/server-view-extends-base-view.md) | `webview_bridge_scanner.py` |
| Client bundles and uses the shared domain class | [`rules/client-uses-shared-domain.md`](rules/client-uses-shared-domain.md) | `webview_bridge_scanner.py` |
| Test each tier independently with a shared base | [`rules/test-each-tier-independently.md`](rules/test-each-tier-independently.md) | `domain_structure_scanner.py` |
| Surface adapters follow extend-or-wrap | [`rules/extend-or-wrap-for-surfaces.md`](rules/extend-or-wrap-for-surfaces.md) | `domain_purity_scanner.py` |
| Domain class owns its presentation shape | [`rules/domain-owns-presentation-shape.md`](rules/domain-owns-presentation-shape.md) | `domain_purity_scanner.py` |

---

## Running Scanners

```bash
# From the project root being checked:
python path/to/domain_structure_scanner.py .
python path/to/domain_purity_scanner.py .
python path/to/server_domain_scanner.py .
python path/to/webview_bridge_scanner.py .
```

Or via the common runner (if configured):

```bash
python skill-helpers/skills/common/scripts/run_scanners.py \
  --spec-root practices/architecture-centric-engineering/specs/domain-driven-vs-code-plugin \
  --project-root <path-to-your-plugin>
```

---

## Applying to a New Domain

1. Copy `templates/src/{domain}/` → `src/<newdomain>/`; replace `{domain}` and `{{Domain}}` with your concept name.
2. Copy `templates/test/{domain}/` → `test/<newdomain>/`.
3. Implement the domain entity interface and behaviour (fill in the TODOs).
4. Implement `<Domain>Server`: override mutation methods to call `_save()`.
5. Implement `<Domain>View`: `_lookup`, `getHtml`, `postMessage` after mutations.
6. Implement `<domain>_client.ts`: DOM bindings, `syncToServer()`.
7. Register the command in `extension.ts` and `package.json`.
8. Run scanners to verify structure and layer purity.
