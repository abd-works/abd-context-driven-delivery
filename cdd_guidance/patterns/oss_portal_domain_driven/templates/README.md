# OSS Portal templates

Parameterized scaffold for the OSS Portal architecture: Angular SSR with a Node Backend-for-Frontend, an Apigee X proxy
per service, and Cloud Run services that each own a Cloud SQL database (OSS Portal Handover Pack v1.0, §3). One folder
per aggregate holds every tier, as in the LERN pattern; the rules are in `oss_portal_domain_driven.md`.

## Structure

```
templates/
├── src/{service}/                       ← one Cloud Run service = one bounded context
│   ├── {service}-app.ts                 ← Cloud Run boot, internal ingress
│   ├── {service}-proxy/apiproxy/        ← Apigee proxy: base path /v1/{{serviceBasePath}}, the standard policy chain
│   ├── migrations/0001-expand-{change}.sql
│   └── {aggregate}/
│       ├── {aggregate}.ts               ← domain, events, in-memory repository
│       ├── {aggregate}-service.ts       ← {{Aggregate}}Service, {{Aggregate}}RepositorySql
│       ├── {aggregate}-service-routes.ts
│       ├── {aggregate}-bff.ts           ← {{Aggregate}}Bff (destination), {{Aggregate}}Gateway
│       ├── {aggregate}-bff-routes.ts
│       ├── {aggregate}-client.ts        ← {{Aggregate}}Client
│       ├── {aggregate}-paths.ts
│       └── {screen}.view.ts             ← {{Screen}}View
├── packages/citizen-portal-app/server.ts ← Angular SSR + BFF: session, mounts every aggregate's BFF routes
└── tests/{epic}/{subEpic}/              ← shared story, domain, service, BFF, Playwright, and journey tiers
```

## Placeholders

| Placeholder | Casing | Example |
|---|---|---|
| `{service}` | kebab-case Cloud Run service | `summer-camp-service` |
| `{{serviceBasePath}}` | the service's Apigee path segment | `summer-camp` |
| `{aggregate}` | kebab-case aggregate folder | `camp-application` |
| `{{Aggregate}}` | PascalCase aggregate root | `CampApplication` |
| `{{aggregates}}` | kebab-case plural resource | `camp-applications` |
| `{screen}` / `{{Screen}}` | screen slug / view class stem | `apply-for-camp` / `ApplyForCamp` |
| `{epic}`, `{subEpic}`, `{snake}` | story map folders and file stem | `summer-camp`, `apply-for-camp`, `apply-for-camp` |
| `{change}` | what the migration changes | `add-seat-preference` |
