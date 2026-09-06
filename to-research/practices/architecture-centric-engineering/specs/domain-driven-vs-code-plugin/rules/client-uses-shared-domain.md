---
scanner: domain_purity_scanner.py
---

# Rule: Client Bundles and Uses the Shared Domain Class

The webview client (`<domain>_client.ts`) imports the **same domain class** that runs on the server. The bundler (esbuild/webpack) includes `Counter` in the webview bundle — there is no separate DTO, no manual schema replication. This is the "share domain logic" principle applied to VS Code webviews.

The client DOM adapter implements `ICounter` so domain tests can drive it via the same shared test base. DOM binding (`syncToServer`) translates every mutation to a `postMessage` back to the extension host.

## DO

- Import the domain class from its source path: `import { Counter } from '../counter.js'`.
- Have the DOM adapter implement `ICounter` so it can be substituted in tests.
- Wrap DOM state sync in a `syncToServer()` call that posts to the VS Code API after each mutation.
- Use `acquireVsCodeApi()` once and cache the result; never call it more than once per frame.
- Update DOM elements from `onmessage` using the message payload (do not re-request state).

```typescript
// src/counter/view/counter_client.ts — CORRECT
import { Counter } from '../counter.js';
import type { ICounter } from '../counter.js';

export function initCounterClient(vscode: { postMessage(msg: unknown): void }): ICounter {
  const counter = new Counter();   // same class as server side

  function syncToServer(): void {
    vscode.postMessage({ command: 'count', args: [counter.total] });
  }

  const domCounter: ICounter = {
    count(amount) {
      counter.count(amount);
      document.getElementById('total')!.textContent = String(counter.total);
      syncToServer();
    },
    reset() {
      counter.reset();
      document.getElementById('total')!.textContent = '0';
      syncToServer();
    },
    get total() { return counter.total; },
  };

  window.addEventListener('message', (event) => {
    const { total } = event.data as { total: number };
    counter.count(total - counter.total);   // reconcile to server total
    document.getElementById('total')!.textContent = String(total);
  });

  return domCounter;
}
```

## DON'T

- Don't define a separate client-side data class that mirrors the server domain (no DTO duplication).
- Don't mutate DOM state without also updating the in-memory domain object.
- Don't call `acquireVsCodeApi()` more than once.
- Don't import `vscode` (the extension API) from client code — use the `vscode` object injected by `acquireVsCodeApi()`.

```typescript
// WRONG — client-side DTO duplicates server schema
interface CounterDto {          // WRONG: duplication of ICounter
  total: number;
}

// WRONG — acquireVsCodeApi called multiple times
function count() {
  const vs = acquireVsCodeApi();   // WRONG: must be called once
  vs.postMessage({ command: 'count' });
}
```
