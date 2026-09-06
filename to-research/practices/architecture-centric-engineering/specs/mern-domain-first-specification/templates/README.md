# MERN Specification Templates

Parameterized scaffold for the MERN architecture specification. Peer to `../template/` — the template slice is a filled instance of these templates.

## Structure

```
templates/
├── domain-module/         ← copy as packages/<domainNames>/
│   ├── shared/            ← entity, collection, schema, repository interface
│   ├── server/            ← repository impl, routes, composition
│   └── client/            ← API client, hook, views
├── app-server/            ← composition root — mounts domain routers
├── app-client/            ← composition root — React app, routes
└── tests/                 ← test scaffold — epic/sub-epic structure
```

## Placeholders

| Placeholder | Casing | Example |
|-------------|--------|---------|
| `{{appName}}` | camelCase | channelone |
| `{{DomainName}}` | PascalCase | Recipient |
| `{{domainName}}` | camelCase | recipient |
| `{{domainNames}}` | camelCase plural | recipients |
| `{{EpicName}}` | Title | Create Wire Payment |
| `{{epicSlug}}` | kebab-case | create-wire-payment |
| `{{SubEpicName}}` | Title | Select Recipient |
| `{{subEpicSlug}}` | kebab-case | select-recipient |

## Usage

1. Copy `domain-module/` as `packages/{{domainNames}}/`.
2. Copy `app-server/` and `app-client/` as `packages/app-server/` and `packages/app-client/`.
3. Copy `tests/` as `tests/`.
4. Replace all `{{placeholders}}` with concrete domain values.
5. Fill domain-specific logic — entity fields, value objects, business rules, test data.
6. Ensure all tests pass.
