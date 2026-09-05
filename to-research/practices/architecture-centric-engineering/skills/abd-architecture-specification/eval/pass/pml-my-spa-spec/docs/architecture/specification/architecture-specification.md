# pml-my React SPA Architecture Specification

> **Status:** Draft -- Exploration fidelity (document mode; describes what exists)
> **Date:** 2026-06-30
> **Mode:** document (Exploration -- describe; do not prescribe)

---

## Where to Start -- What Does This Feature Touch?

Answer each question about the feature or story you are working on. Each "yes" points to a context file with the details you need. Read only those files -- you don't need the rest of this document.

If every answer is "no", the feature is either infrastructure-only or out of scope for this spec; if you are unsure, read the Overview and Source Layout below to orient yourself and follow the relevant context files from there.

| Question                                                                                  | Read this                                                                                                                |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Is there a new authenticated operation against pml-midtier?                               | [Communication (HTTP Client)](/src/utils/api/architecture-context.md)                                                    |
| Should access be restricted to authenticated subscribers?                                 | [Security (Identity)](/src/services/aws/architecture-context.md)                                                         |
| Are there specific failure conditions the user needs to see distinctly?                   | [Error Handling & Resilience](/src/utils/api/architecture-context.md)                                                    |
| Does it require a new third-party credential or environment-specific value?               | [Configuration & Secrets](/src/config/architecture-context.md)                                                           |
| Does it read or write in-session state (customer, plan, cart, session, attribution)?      | [Persistence](/src/recoil/architecture-context.md)                                                                       |
| Should the feature be toggleable from a dashboard without a code deploy?                  | [Feature Flag Control](/src/config/architecture-context.md)                                                              |
| Does it need to capture card details or take a payment?                                   | [Hosted-Iframe Payment Integration](/src/pages/Onboarding/pages/Checkout/steps/Payment/architecture-context.md)          |
| Does it need to attribute a marketing campaign or track a conversion event?               | [Analytics Attribution](/src/utils/analytics/architecture-context.md)                                                    |
| Does it depend on the plan catalog?                                                       | [Catalog Caching](/src/services/mavenir/architecture-context.md)                                                         |
| Should something run before React mounts, or be part of the app's provider stack?         | [App Bootstrap](/src/architecture-context.md)                                                                            |

---

## Overview

pml-my is a React 18 / TypeScript single-page application hosted on AWS Amplify that owns the customer-facing surface of Paradise Mobile: the prospect onboarding wizard and the authenticated subscriber self-care experience. It does not own domain state -- every business decision happens behind pml-midtier and the downstream systems pml-midtier talks to. pml-my's job is to render the right UI, collect input, prove caller identity to pml-midtier, and reflect the resulting state in the browser.

The architecture has six top-level concerns: bringing the app up before React mounts (App Bootstrap), proving the user is who they claim to be (Security), talking to pml-midtier safely (Communication, Error Handling), holding the in-session working copy of domain state (Persistence via Recoil atoms), routing the user to the right view (Onboarding and Self-Care module trees), and adapting to remote feature toggles, marketing attribution, and the hosted payment iframe.

> **Sources:** `docs/architecture/architecture-outline.md`; `docs/architecture/architecture-blueprint.md`; ADR-001 through ADR-010; code-research `agent-2-deep-dive`.

---

## Mechanisms

**App Bootstrap** (`src/main.tsx`, `src/App.tsx`) -- imperative pre-mount initialisation (`main.tsx`) followed by a declarative provider stack (`App.tsx`); `QueryClient` and `GrowthBook` singletons are created at module scope so they survive `<App />` re-renders. [src/architecture-context.md](/src/architecture-context.md)

**Security (Identity)** (`src/services/aws/`) -- single Cognito seam (`cognito.ts`) over Amplify SDK v6 plus the `<ProtectedRoute>` / `Protected` route-guard pair; every authenticated call to pml-midtier first calls `getAuthorizationHeader()` which force-refreshes the session. [src/services/aws/architecture-context.md](/src/services/aws/architecture-context.md)

**Communication (HTTP Client)** (`src/utils/api/`) -- shared Axios wrapper (`request()`) called by every mutation hook with dual `idtoken` + `Authorization: Bearer` headers; service functions and the `useRequestGet/Post/Patch` hook family all return `Promise<ApiReturn<T>>`. [src/utils/api/architecture-context.md](/src/utils/api/architecture-context.md)

**Error Handling & Resilience** (`src/utils/api/`, `src/utils/snackbar/`) -- `request()` never throws; the `ApiReturn<T>` discriminated union forces every call site to check `result.success`; failures route to `enqueueSnackbarError` and TanStack Query errors funnel through `QueryCache.onError` (same wrapper as Communication; documented from the failure-handling angle). [src/utils/api/architecture-context.md](/src/utils/api/architecture-context.md)

**Configuration & Secrets** (`src/config/`) -- single typed `env` object built via the `requireEnv()` guard at module load; missing `VITE_*` variables fail the bundle at startup before users see a broken app. [src/config/architecture-context.md](/src/config/architecture-context.md)

**Persistence** (`src/recoil/`) -- Recoil atoms hold the in-session working copy of every domain concept (`customerAtom`, `selectedPlanAtom`, `sessionAtom`, `utmAtom`); mutation hooks write atoms only on `result.success`; the `atoms[]` reset manifest is iterated on sign-out so PII never leaks between sessions. [src/recoil/architecture-context.md](/src/recoil/architecture-context.md)

**Feature Flag Control** (`src/config/flags.ts`, `src/App.tsx`) -- GrowthBook singleton + provider; flag keys are named constants in `flags.ts`; consumers call `useFeatureIsOn(flags.KEY)` or `useFeatureValue(flags.KEY, safeDefault)`; `Router.tsx` consumes `MAINTENANCE` and `DISABLE_SELFCARE` to gate whole route trees. [src/config/architecture-context.md](/src/config/architecture-context.md)

**Analytics Attribution** (`src/utils/analytics/`) -- UTM capture at the root via `AnalyticsWrapper` writes `utmAtom`; typed event-name registries plus `sendPageViewEvent` / `sendGAPurchaseEvent` / `sendUserAttributesEvent` wrap GA4, GTM, and Hotjar behind a stable surface; `checkEmailType()` gates production purchase events on email classification. [src/utils/analytics/architecture-context.md](/src/utils/analytics/architecture-context.md)

**Hosted-Iframe Payment Integration** (`src/pages/Onboarding/pages/Checkout/steps/Payment/`) -- pml-my never handles raw card data; pml-midtier returns FAC iframe HTML as `srcdoc`; the `usePayment` hook orchestrates load -> `postMessage('submitForm')` -> status poll -> `POST /billing` -> `POST /order`, capped by the `PAYMENT_ATTEMPTS` flag. [src/pages/Onboarding/pages/Checkout/steps/Payment/architecture-context.md](/src/pages/Onboarding/pages/Checkout/steps/Payment/architecture-context.md)

### Package Context

Every folder with significant logic has an `architecture-context.md` alongside its code.

**Mechanisms**

- **App Bootstrap** -- pre-mount init plus provider stack [src/](/src/architecture-context.md)
- **Security (Identity)** -- Cognito seam plus `<ProtectedRoute>` / `Protected` [src/services/aws/](/src/services/aws/architecture-context.md)
- **Communication & Error Handling** -- `request()`, `ApiReturn<T>`, hook family, and the snackbar sink [src/utils/api/](/src/utils/api/architecture-context.md)
- **Configuration, Secrets & Feature Flags** -- typed `env`, `requireEnv` guard, GrowthBook flag-key constants [src/config/](/src/config/architecture-context.md)
- **Persistence** -- Recoil atoms and the sign-out reset manifest [src/recoil/](/src/recoil/architecture-context.md)
- **Analytics Attribution** -- typed event registries, multi-vendor sender, UTM atom [src/utils/analytics/](/src/utils/analytics/architecture-context.md)
- **Hosted-Iframe Payment Integration** -- iframe + postMessage + sequential billing/order flow [src/pages/Onboarding/pages/Checkout/steps/Payment/](/src/pages/Onboarding/pages/Checkout/steps/Payment/architecture-context.md)

**Packages**

- **Catalog Caching** -- single TanStack Query usage; `useCatalog` with `staleTime: Infinity` [src/services/mavenir/](/src/services/mavenir/architecture-context.md)
- **Snackbar** -- module-scoped `enqueueSnackbarError` singleton bridging `QueryCache.onError` to notistack [src/utils/snackbar/](/src/utils/snackbar/architecture-context.md)
- **Onboarding Module** -- prospect-to-subscriber conversion wizard, atom reset manifest [src/pages/Onboarding/](/src/pages/Onboarding/architecture-context.md)
- **Self-Care Module** -- authenticated subscriber dashboard, billing, profile, plan management [src/pages/My/](/src/pages/My/architecture-context.md)

**Utilities & Legacy**

- **disableConsole** -- production console suppression; single helper used by `main.tsx` [src/utils/logger/](/src/utils/logger/architecture-context.md)

**Testing**

- **Domain Test Objects** -- per-sub-epic domain test object files plus shared MSW handlers and provider helpers [tests/](/tests/architecture-context.md)

### Source Layout

```
src/
+-- main.tsx                    <- DOM mount + pre-mount vendor init  [App Bootstrap]
+-- App.tsx                     <- provider stack composition         [App Bootstrap]
+-- Router.tsx                  <- route tree + maintenance gate      [Feature Flag Control]
+-- config/
|   +-- env.ts                  <- typed env + requireEnv guard       [Configuration & Secrets]
|   +-- flags.ts                <- GrowthBook flag-key constants      [Feature Flag Control]
+-- recoil/                     <- session-scoped domain atoms        [Persistence]
+-- services/
|   +-- aws/cognito.ts          <- Amplify auth seam                  [Security (Identity)]
|   +-- mavenir/useCatalog.tsx  <- plan catalog query                 [Catalog Caching]
+-- utils/
|   +-- api/                    <- request() + ApiReturn + hooks      [Communication (HTTP Client)]
|   +-- snackbar/               <- enqueueSnackbarError sink
|   +-- analytics/              <- typed senders + UTM wrapper        [Analytics Attribution]
|   +-- logger/disableConsole/  <- production console suppression     [legacy]
+-- pages/
|   +-- Protected/              <- session guard + step-resume        [Security (Identity)]
|   +-- ProtectedRoute.tsx      <- render-time auth gate              [Security (Identity)]
|   +-- Onboarding/             <- prospect conversion wizard
|   |   +-- pages/Checkout/steps/Payment/   <- FAC iframe flow        [Hosted-Iframe Payment Integration]
|   +-- My/                     <- authenticated self-care
+-- types/
    +-- request.ts              <- ApiReturn<T> discriminated union   [Communication (HTTP Client)]
tests/
+-- mocks/                      <- MSW handlers shared T1/T2/T3
+-- helpers/                    <- with-providers wrapper
+-- <epic>/<sub-epic>/          <- one folder per sub-epic
```

### Instantiating the Domain

> **Domain concepts drive file names, not technical layers.** A domain concept (`Customer`, `Plan`, `Cart`, `Subscription`, `Session`, `UTM`) gives its name to its Recoil atom (`customerAtom`, `selectedPlanAtom`, `sessionAtom`, `utmAtom`), to its mutation hook (`useCustomer`, `useCatalog`), and to its API service shape (`fetchCustomer`, `patchCart`). Mechanism infrastructure lives in `src/utils/`, `src/services/`, and `src/config/`; everything else is organised by business module (`Onboarding/`, `My/`, `services/mavenir/`).
>
> - **Customer** -- session source of truth; atom in `src/recoil/customerAtom.ts`; mutations in `src/hooks/useCustomer.ts` (Onboarding) and `src/pages/My/hooks/useCustomer.ts` (Self-Care).
> - **Plan** -- selected plan in `src/recoil/selectedPlanAtom.ts`; catalog cache via `src/services/mavenir/useCatalog.tsx`.
> - **Cart** -- nested inside `customerAtom.cart` during onboarding; `useCustomer.patchCart` is the only mutator.
> - **Subscription** -- authenticated self-care multi-line state via `subscriptionSelector` in `src/pages/My/recoil/subscription.ts`.
> - **Session** -- Cognito-backed; `sessionAtom` plus `useSession()` hook over `cognito.ts`.
> - **UTM** -- campaign attribution; captured once at mount by `AnalyticsWrapper`, lives in `utmAtom`.

---

## Testing Architecture

Tests use a **Sandbox** pattern: per-sub-epic domain test objects drive the real React tree (Recoil + hooks + Axios) via Vitest, Testing Library, and -- at the E2E tier -- Playwright; only the network boundary (pml-midtier and other downstream systems) and Cognito are stubbed, via MSW handlers shared across all three tiers. See [tests/architecture-context.md](/tests/architecture-context.md) for principles, file layout, the T1/T2/T3 vertical-slice workflow, and the epic / sub-epic map.

---

## References

- **Architecture source of truth:** `docs/architecture/architecture-outline.md`; `docs/architecture/architecture-blueprint.md`; ADR-001 through ADR-010
- **Code research:** `docs/external/code-research/agent-2-deep-dive/` -- eight deep-dive reports (auth, API layer, Recoil state, payment flow, GrowthBook, onboarding, analytics, customer domain)
- **Domain model:** `docs/domain/model/domain-model.md`; `docs/domain/model/domain-code-map.md`
- **Story map:** `docs/stories/story-map/story-map.md`
- **Coding standard:** `abd-clean-code`
- **Testing standard:** `abd-story-acceptance-test`
- **Flow diagram:** `docs/architecture/specification/architecture-flow.drawio`
