---
scanner: webview_bridge_scanner.py
---

# Rule: Server View Extends BaseView and Uses postMessage

Server views live in `src/<domain>/view/<domain>_view.ts`. Each extends `BaseView`, which provides `renderTemplate()` for HTML generation and `escapeHtml()` for safe interpolation. Server views hold a reference to the domain object and a webview panel; they dispatch state to the client after every mutation via `panel.webview.postMessage()`.

Command routing (`_lookup`) maps the command string received from the client to the view method that handles it, keeping the dispatch table centralised in the server view.

## DO

- Extend `BaseView` for every server view class.
- Name the view class `<Domain>View` and the file `<domain>_view.ts` inside `view/`.
- Call `this.panel.webview.postMessage({ total: this._counter.total })` after every mutation.
- Implement `_lookup(path: string): [object, string]` to resolve command strings to bound method references.
- Implement `getHtml(): string` by calling `this.renderTemplate(...)` with the HTML template path and substitutions.

```typescript
// src/counter/view/counter_view.ts — CORRECT
import type { WebviewPanel, Uri } from 'vscode';
import { BaseView } from '../../engine/base_view.js';
import type { ICounter } from '../counter.js';
import { Counter } from '../counter.js';

export class CounterView extends BaseView implements ICounter {
  private _counter: ICounter;
  readonly panel: WebviewPanel;

  constructor(panel: WebviewPanel, counter: ICounter, extensionUri: Uri) {
    super(extensionUri);
    this.panel = panel;
    this._counter = counter;
  }

  count(amount: number | string): void {
    this._counter.count(amount);
    this.panel.webview.postMessage({ total: this._counter.total });
  }

  reset(): void {
    this._counter.reset();
    this.panel.webview.postMessage({ total: this._counter.total });
  }

  get total(): number {
    return this._counter.total;
  }

  _lookup(pathStr: string): [object, string] {
    const routes: Record<string, [object, string]> = {
      'count': [this, 'count'],
      'reset': [this, 'reset'],
    };
    return routes[pathStr] ?? [this, pathStr];
  }

  getHtml(): string {
    return this.renderTemplate('counter/view/Counter.html', {
      total: String(this.total),
    });
  }
}
```

## DON'T

- Don't implement a server view without extending `BaseView`.
- Don't skip `postMessage` after mutations — the client will be out of sync.
- Don't write raw HTML string concatenation in the view — use `renderTemplate()`.
- Don't put the command dispatch table outside the view class.

```typescript
// WRONG — raw HTML, no postMessage, no BaseView
export class CounterView {
  getHtml(): string {
    return `<div>${this._counter.total}</div>`;   // WRONG: raw string, no escaping
  }

  count(amount: number): void {
    this._counter.count(amount);
    // WRONG: forgot postMessage — client won't update
  }
}
```
