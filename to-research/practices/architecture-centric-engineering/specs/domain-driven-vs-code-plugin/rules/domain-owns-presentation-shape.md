# Rule: Domain class owns its presentation shape

**DO** put pure presentation helpers (markdown strings, display labels, tooltip text) on the domain class or a domain-tier extension.  
**DO NOT** import `vscode` in those methods or classes — use plain `string` return types; the surface adapter wraps them in VS Code types.

## DO — pure method on domain class

Domain classes may expose `toStatusBarMarkdown(): string`, `toLabel(): string`, or similar.
These return plain strings. The adapter wraps the string in `new vscode.MarkdownString(...)`.

```typescript
// GOOD — pure method; no vscode import
export class Counter implements ICounter {
  toStatusBarMarkdown(): string {
    return [
      `**Counter**`,
      `Total: ${this.total}`,
      this.total > 100 ? '⚠ High count' : 'Normal range',
    ].join('\n');
  }
}

// GOOD — adapter wraps it
this._item.tooltip = new vscode.MarkdownString(counter.toStatusBarMarkdown());
```

## DO — extend for selectable presentation shape

When a domain object must appear in a `QuickPick`, extend it with `label`, `description`, `detail`.
The extension class has no `vscode` import; structural typing satisfies `QuickPickItem`.

```typescript
// GOOD — CounterPickItem satisfies vscode.QuickPickItem without importing it
export class CounterPickItem extends Counter {
  readonly label: string;
  readonly description: string;
  readonly detail: string;
}
```

## DO NOT — build presentation in the adapter

Do not let the wrapping adapter assemble display strings from raw domain data.
That logic belongs on the domain class or its extension.

```typescript
// BAD — adapter builds the tooltip inline; should delegate to domain
this._item.tooltip = new vscode.MarkdownString(
  `**Counter**\nTotal: ${counter.total}\n${counter.total > 100 ? '⚠' : ''}` // ❌
);
```

## DO NOT — import vscode in the domain tier

Domain classes and their extensions must not import `vscode` at any level.

```typescript
// BAD — domain class imports vscode
import * as vscode from 'vscode';
export class Counter {
  toTooltip(): vscode.MarkdownString { ... } // ❌
}
```

Source: `architecture-specification.md` — Instantiating the Domain / Extend-or-Wrap Decision
