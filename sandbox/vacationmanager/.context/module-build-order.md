# Module build order — Vacation Manager

Topological order from one-way dependencies. Build lower layers first; `invite` and `itinerary` are independent of each other and may be built in parallel after `vacation`.

```
vacation
  ├── invite      (depends on vacation → VacationId)
  └── itinerary   (depends on vacation → VacationId, Destination)
```

| Order | Module | Depends on |
|---|---|---|
| 1 | `vacation` | *(none)* |
| 2a | `invite` | `vacation` |
| 2b | `itinerary` | `vacation` |
