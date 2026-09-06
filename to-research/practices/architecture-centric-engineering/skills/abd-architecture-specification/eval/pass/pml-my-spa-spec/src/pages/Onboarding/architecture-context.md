# Onboarding Module

The Onboarding module is the prospect-to-subscriber conversion wizard. It is a feature module, not a mechanism -- its job is to compose the App Bootstrap, Security, Communication, Persistence, Feature Flag Control, Analytics Attribution, and Hosted-Iframe Payment mechanisms into a multi-step flow that produces a verified Customer + Subscription.

Used by every unauthenticated visitor on the prospect path. Driven by `customerAtom.cart` plus a small set of onboarding-scoped atoms; uses `useCustomer.patchCart` as the canonical mutator.

**Step composition** -- `LineNumber`, `SelectPlan`, `SelectSim`, `Profile`, `Checkout`, `Done`. Step order and resume behaviour are encoded in `config.ts` plus the `sessionAtom.onboardingStep` redirect logic in `<Protected>`.

**`config.ts`** -- exports the `atoms[]` reset manifest (consumed by sign-out) and the per-step config (route paths, atom resets, telemetry events).

**Step-local atoms** -- `recoil/atoms/` contains atoms scoped to specific steps (e.g. `numberOptionsAtom`, `personaDataAtom`, `simTypeHelperAtom`, `backToCheckoutAtom`); they hold intermediate UI state that does not belong on `customerAtom`.

**`useCustomer` (Onboarding)** -- mutation hook for `patchCustomer`, `patchCart`, and `patchCartPlan`; lives at `src/hooks/useCustomer.ts` and is the Onboarding-side counterpart to the Self-Care `useCustomer`.

**Why the wizard is here and not under `pages/My/`** -- Onboarding is the unauthenticated path; Self-Care is the authenticated one. They share the `Customer` domain concept but not the route guard, atom set, or step ordering.

**Trade-offs** -- step-local state held in step-scoped atoms can be lost if the user navigates away before `patchCart` is called; this is accepted because the alternative (persisting form state to localStorage) increases privacy surface.
