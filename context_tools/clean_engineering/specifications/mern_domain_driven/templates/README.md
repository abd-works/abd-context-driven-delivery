# MERN Specification Templates

Parameterized scaffold for the MERN architecture specification.

## Structure

```
templates/
├── {epicSlug}/                      ← feature package (e.g. packages/wires/)
│   ├── {EpicName}View.tsx           ← feature view
│   ├── app.ts / serve.ts            ← Express factory + process listen
│   ├── main.tsx / index.html / vite.config.ts  ← browser boot
│   ├── package.json
│   ├── index.ts
│   └── {domainName}/                ← domain module nested in the feature
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
