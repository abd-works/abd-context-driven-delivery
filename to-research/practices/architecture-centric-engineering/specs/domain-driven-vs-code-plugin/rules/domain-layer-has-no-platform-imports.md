---
scanner: domain_purity_scanner.py
---

# Rule: Domain Layer Has No Platform Imports

The domain entity files (`<domain>.ts`, the interface `I<Domain>`) are **pure TypeScript**. They must not import from `vscode`, the DOM, Node.js built-ins (`fs`, `path`, `os`), or any persistence library. Domain logic must run in a test with no VS Code context and no file system.

This is what makes the domain portable: the same `Counter` class runs in the extension host, in the webview bundle, and in plain Vitest tests without any mock of the VS Code API.

## DO

- Import only from TypeScript standard types and other domain files in this folder.
- Expose behaviour through methods and a matching interface (`ICounter`).
- Keep the interface in the same file as the implementation, or as a sibling — never pull in platform types for the interface.

```typescript
// src/counter/counter.ts — CORRECT: pure TS, no platform imports
export interface ICounter {
  count(amount: number | string): void;
  reset(): void;
  readonly total: number;
}

export class Counter implements ICounter {
  private _total = 0;

  count(amount: number | string): void {
    this._total += Number(amount);
  }

  reset(): void {
    this._total = 0;
  }

  get total(): number {
    return this._total;
  }
}
```

## DON'T

- Don't import `vscode` in `counter.ts` or `engine.ts`.
- Don't import `fs`, `path`, or any Node API in the domain entity.
- Don't import DOM types (`document`, `window`, `HTMLElement`) in the domain entity.

```typescript
// WRONG — vscode imported in domain entity
import * as vscode from 'vscode';

export class Counter {
  count(amount: number): void {
    vscode.window.showInformationMessage(`Counted: ${amount}`);  // WRONG
    this._total += amount;
  }
}
```

```typescript
// WRONG — fs imported in domain entity (belongs in CounterServer)
import * as fs from 'fs';

export class Counter {
  count(amount: number): void {
    fs.writeFileSync('counter.json', JSON.stringify({ total: amount }));  // WRONG
    this._total += amount;
  }
}
```
