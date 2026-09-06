# disableConsole (legacy console suppression)

A single helper in `disableConsole/index.ts` that overwrites `console.log`, `console.error`, and `console.warn` with no-ops. Called once from `main.tsx` when `env.environment !== 'development'`. There is no structured logging, no OpenTelemetry instrumentation, and no error monitoring service in pml-my; the documented gap is acknowledged in the Mechanisms list under Error Handling & Resilience.

The folder is tagged `[legacy]` in the Source Layout because it predates the analytics-only observability decision and would be replaced if an error monitoring service were ever introduced.

```typescript
// src/utils/logger/disableConsole/index.ts
export function disableConsole() {
  console.log = () => {}
  console.error = () => {}
  console.warn = () => {}
}
```
