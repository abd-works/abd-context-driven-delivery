# LERN / lowdb Specification Templates

Parameterized scaffold for the lowdb domain-driven architecture specification
([lowdb](https://github.com/typicode/lowdb) JSON files / Express / React / Node,
TypeScript everywhere). Each aggregate root owns its JSON store beside the domain
module under `src/`. DDD stereotypes: `practices/ddd/ddd.md` building_blocks.

## Structure

```
templates/
├── src/
│   └── {domainNames}/                 ← shared domain module (one copy per aggregate)
│       ├── {domainNames}.ts           ← core aggregate, repository, VOs
│       ├── {domainNames}-node.ts      ← Node tier (Express, destination, repo node)
│       ├── {domainNames}-client.tsx   ← browser client subtype
│       ├── {screenSlug}.tsx           ← views for this aggregate
│       ├── {domainNames}-routes.ts    ← one route file for this aggregate
│       └── {domainNames}.json         ← lowdb store for this aggregate
├── {epicSlug}/                        ← epic package (boot + epic-wide router, shell, assets)
│   ├── app.ts / serve.ts              ← Express factory + process listen
│   ├── main.tsx / index.html / vite.config.ts
│   └── package.json
└── tests/                             ← test scaffold — epic/sub-epic structure
```

Domain tiers live once under `src/`; epic packages import them through `@src`.

## Placeholders

| Placeholder | Casing | Example |
|---|---|---|
| `{{epicSlug}}` | kebab-case feature package | `wire-pay` |
| `{{domainNames}}` | plural kebab-case folder | `recipients` |
| `{{domainName}}` | camelCase singular | `recipient` |
| `{{DomainName}}` | PascalCase singular | `Recipient` |
| `{{appName}}` | npm scope | `wirepay` |
