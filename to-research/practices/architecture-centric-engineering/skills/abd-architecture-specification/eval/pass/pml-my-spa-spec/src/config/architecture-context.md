# Mechanism: Configuration, Secrets & Feature Flags

### Overview

This folder hosts two related mechanisms. **Configuration & Secrets** is the typed `env` object built at module load by the `requireEnv()` guard in `env.ts`; every `VITE_*` variable used anywhere in the app flows through this file. **Feature Flag Control** is the GrowthBook string-constant registry in `flags.ts` that prevents magic strings in `useFeatureIsOn` / `useFeatureValue` calls.

Both share a config-tier shape (no UI, no Recoil, no Axios) and are imported the same way -- `import { env } from '@/config'`, `import { flags } from '@/config'`. Secret rotation requires a new Amplify build because all values are build-time-injected.

### File Structure

```
src/
+-- config/
    +-- env.ts                  <- requireEnv guard; typed env object; throws on missing VITE_ vars
    +-- flags.ts                <- GrowthBook flag-key string constants (`as const`)
    +-- index.ts                <- barrel: re-exports env + flags
```

### Participants

| Class / Module             | Responsibility                                                                            | Collaborators                       |
| -------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------- |
| `requireEnv(name, value)`  | Throws synchronously at module load if `value` is falsy; returns the value otherwise      | `import.meta.env.*`                 |
| `env`                      | Typed namespaced object: `env.awsCognito`, `env.midtier`, `env.google`, `env.growthbook`, etc. | `requireEnv`                        |
| `flags`                    | `as const` string-constant registry of every GrowthBook key in use                        | `useFeatureIsOn`, `useFeatureValue` |
| AWS Amplify CI/CD          | Injects `VITE_*` variables at build time into the Vite bundle                             | Build pipeline                      |

### Class Specification

```mermaid
classDiagram
    class RequireEnv {
        +requireEnv(name, value) string
    }
    class Env {
        +awsCognito: { region, userPoolId, webClientId }
        +midtier: { url, mavenir: {...} }
        +google: { gaId, gtmId, testDomains }
        +growthbook: { apiHost, clientKey }
        +environment: 'development' | 'staging' | 'production'
    }
    class Flags {
        +MAINTENANCE: 'maintenance'
        +DISABLE_SELFCARE: 'disable-selfcare'
        +PAYMENT_ATTEMPTS: 'payment-attempts'
        +...other GrowthBook keys
    }
    Env --> RequireEnv : built via
```

### Rules

- **`import.meta.env` is read in `env.ts` only.** A `grep` on `import.meta.env` outside `src/config/env.ts` is the audit; deviations are immediately flagged.
- **Missing required configuration fails the bundle at startup.** `requireEnv` throws synchronously; the white-screen-with-console-error during deploy is intentional and surfaces misconfiguration before any user load.
- **Every GrowthBook flag key is a named constant in `flags.ts`.** Adding a new flag means adding it to `flags.ts` first; magic strings in `useFeatureIsOn` are forbidden.
- **All flag consumers tolerate `false` (or the supplied default) before features load.** `growthbook.loadFeatures()` is fire-and-forget; the first render happens before remote definitions arrive.
- **Secret rotation = build + deploy.** There is no runtime config endpoint; this is a deliberate trade-off given the SPA architecture.

### Canonical Patterns

```typescript
// src/config/env.ts
const requireEnv = (name: string, value: string | undefined) => {
  if (!value) throw new Error(`Missing required environment variable: ${name}`)
  return value
}

export const env = {
  environment: import.meta.env.MODE,
  awsCognito: {
    region: requireEnv('VITE_COGNITO_REGION', import.meta.env.VITE_COGNITO_REGION),
    userPoolId: requireEnv('VITE_COGNITO_USER_POOL_ID', import.meta.env.VITE_COGNITO_USER_POOL_ID),
    webClientId: requireEnv('VITE_COGNITO_WEB_CLIENT_ID', import.meta.env.VITE_COGNITO_WEB_CLIENT_ID),
  },
  midtier: { url: requireEnv('VITE_MIDTIER_URL', import.meta.env.VITE_MIDTIER_URL) },
  growthbook: {
    apiHost: requireEnv('VITE_GROWTHBOOK_API_HOST', import.meta.env.VITE_GROWTHBOOK_API_HOST),
    clientKey: requireEnv('VITE_GROWTHBOOK_CLIENT_KEY', import.meta.env.VITE_GROWTHBOOK_CLIENT_KEY),
  },
} as const

// src/config/flags.ts
export const flags = {
  MAINTENANCE: 'maintenance',
  MAINTENANCE_TEXT: 'maintenance-text',
  DISABLE_SELFCARE: 'disable-selfcare',
  DISABLE_PSIM: 'disable-psim',
  DISABLE_ESIM: 'disable-esim',
  PORTING_2FA: 'porting-2fa',
  PAYMENT_ATTEMPTS: 'payment-attempts',
  PAY_UP_FRONT: 'pay-up-front',
  CHANGE_PLAN_ROAMING_TICKET: 'change-plan-roaming-ticket',
} as const
```
