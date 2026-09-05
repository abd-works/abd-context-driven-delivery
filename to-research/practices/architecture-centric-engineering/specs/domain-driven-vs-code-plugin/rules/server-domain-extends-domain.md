---
scanner: server_domain_scanner.py
---

# Rule: Server Domain Extends the Domain Class

Persistence is added by **extending** the domain entity, not by wrapping it in a repository or service. `CounterServer extends Counter` — the domain behaviour stays intact, the server class overrides or intercepts to load/save state.

The result: `CounterServer` fully satisfies `ICounter`. Any code that accepts `ICounter` can receive a `CounterServer` without knowing about persistence.

## DO

- Name the server extension `<Domain>Server` and place it in `src/<domain>/<domain>_server.ts`.
- Extend (not wrap) the domain class: `class CounterServer extends Counter`.
- Load state in the constructor via a private `_load()` method.
- Persist on every mutation by calling `_save()` at the end of each overriding method.
- Keep `_load()` and `_save()` private — they are implementation details.
- Accept the file path in the constructor; don't hardcode paths.

```typescript
// src/counter/counter_server.ts — CORRECT
import * as fs from 'fs';
import { Counter } from './counter.js';

export class CounterServer extends Counter {
  private _filePath: string;

  constructor(filePath: string) {
    super();
    this._filePath = filePath;
    this._load();
  }

  override count(amount: number | string): void {
    super.count(amount);
    this._save();
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

## DON'T

- Don't create a `CounterRepository` that holds a `counter` field and delegates to it (wrapping) — the object graph becomes two objects where one is enough.
- Don't expose `_load()` or `_save()` publicly.
- Don't call persistence methods outside of the overridden mutation methods.
- Don't import `fs` in the base domain class.

```typescript
// WRONG — repository pattern wraps instead of extends
export class CounterRepository {
  private counter = new Counter();  // WRONG: wrapping, not extending

  count(amount: number): void {
    this.counter.count(amount);
    this._save();
  }

  get total(): number {
    return this.counter.total;    // WRONG: delegates, doesn't inherit
  }
}
```
