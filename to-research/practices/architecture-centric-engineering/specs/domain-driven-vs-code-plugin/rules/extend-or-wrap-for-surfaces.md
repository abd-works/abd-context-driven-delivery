# Rule: Surface adapters follow extend-or-wrap

**DO** choose extend when the adapter IS-A domain concept that also satisfies a VS Code interface.  
**DO** choose wrap when the adapter HAS-A domain dependency and owns VS Code lifecycle objects.

## DO — extend

Use extend when the VS Code interface is a presentation contract the domain concept naturally satisfies.
The extending class adds `label`, `description`, `detail`, or other surface-specific fields.
It does NOT import `vscode`.

```typescript
// GOOD — CounterPickItem IS-A Counter with presentation shape; no vscode import
export class CounterPickItem extends Counter {
  readonly label: string;
  readonly description: string;
  constructor(source: Counter, snapshotLabel: string) {
    super();
    if (source.total > 0) this.count(source.total);
    this.label       = snapshotLabel;
    this.description = `total: ${this.total}`;
  }
}
```

## DO — wrap

Use wrap when the adapter owns VS Code lifecycle objects (StatusBarItem, WebviewPanel, OutputChannel)
or when it manages callbacks/subscriptions that have no place on the domain class.

```typescript
// GOOD — CounterStatusBar WRAPS Counter; it owns a StatusBarItem
export class CounterStatusBar implements vscode.Disposable {
  private _item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  setState(state: { counter: ICounter }): void { /* ... */ }
  dispose(): void { this._item.dispose(); }
}
```

## DO NOT — conflate

Do not make a domain class implement VS Code interfaces directly, and do not put lifecycle management
inside a domain class.

```typescript
// BAD — domain class owns a StatusBarItem; mixes lifecycle into domain
export class Counter implements vscode.Disposable {
  private _item = vscode.window.createStatusBarItem(...); // ❌ vscode in domain
}
```

## DO NOT — skip the extending class

Do not pass plain domain objects directly to VS Code surfaces when a presentation shape is needed.
Build the presentation extension explicitly.

```typescript
// BAD — Counter has no label; showQuickPick will display undefined
const items: vscode.QuickPickItem[] = snapshots as any; // ❌ no label
await vscode.window.showQuickPick(items);
```

Source: `architecture-specification.md` — Instantiating the Domain / Extend-or-Wrap Decision
