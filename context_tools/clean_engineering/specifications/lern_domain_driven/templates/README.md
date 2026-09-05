# LERN / lowdb Specification Templates

Parameterized scaffold for the lowdb domain-driven architecture specification
([lowdb](https://github.com/typicode/lowdb) JSON files / Express / React / Node).
Each aggregate root owns `data/{{domainNames}}.json`. DDD stereotypes:
`context_tools/ddd/ddd.md` building_blocks.

## Structure

```
templates/
├── {epicSlug}/                      ← feature package (e.g. packages/wires/)
│   ├── {EpicName}View.tsx           ← feature view
│   ├── app.ts / serve.ts            ← Express factory + process listen
│   ├── main.tsx / index.html / vite.config.ts  ← browser boot
│   ├── package.json
│   ├── index.ts
│   ├── data/{domainNames}.json      ← lowdb store for this aggregate only
│   └── {domainName}/                ← aggregate module nested in the feature
│       ├── {domainName}.ts
│       ├── {domainName}-server.ts
│       └── {domainName}-client.tsx
└── tests/                           ← test scaffold — epic/sub-epic structure
```

No separate `app-server` / `app-client` packages — process boot lives on the
feature package.

## Placeholders

| Placeholder | Casing | Example |
|---|---|---|
| `{{epicSlug}}` | kebab-case feature package | `wires` |
| `{{EpicName}}` | PascalCase feature view | `WirePayment` |
| `{{domainName}}` | camelCase singular | `recipient` |
| `{{DomainName}}` | PascalCase singular | `Recipient` |
| `{{domainNames}}` | plural domain folder | `recipients` |
| `{{appName}}` | npm scope | `wirepay` |
