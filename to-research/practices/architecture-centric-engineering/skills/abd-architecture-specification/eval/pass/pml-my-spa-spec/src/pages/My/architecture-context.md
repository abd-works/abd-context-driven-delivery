# Self-Care Module

The Self-Care module is the authenticated subscriber experience: dashboard, billing, services, profile, payment method, support. Like Onboarding it is a feature module that composes mechanisms; unlike Onboarding it sits entirely behind `<ProtectedRoute>` and operates on an existing `Customer` rather than building one.

Used by every authenticated subscriber. Driven by `customerAtom` plus `subscriptionSelector` (multi-line state).

**Page composition** -- `Home` (dashboard), `Billing`, `Services` (plan and add-on management), `Profile` (identity and address update), `Payment` (payment-method update via the same Hosted-Iframe mechanism), `Support`.

**`useCustomer` (Self-Care)** -- mutation hook for `patchCustomer`; lives at `src/pages/My/hooks/useCustomer.ts`. Distinct from the Onboarding `useCustomer` because the Self-Care operation set is smaller and the optimistic-merge shape is different.

**`recoil/subscription.ts`** -- `subscriptionAtom` and `subscriptionSelector` for multi-line accounts. The selector reads `customerAtom.subscriptions` and the current line selection to produce the active `<<Subscription>>`.

**`pages/Payment/`** -- payment-method update; reuses the Hosted-Iframe Payment mechanism against `POST /payment-method` instead of `POST /billing` + `POST /order`. The orchestration shape is the same; the endpoints differ.

**Self-care disable gate** -- the entire Self-Care tree is collapsed behind `flags.DISABLE_SELFCARE` in `Router.tsx`. When that flag is on, `/sign-in/*` routes render the maintenance screen.

**Why Self-Care is separate from Onboarding** -- they share the `Customer` domain but operate on it from different states (creating-vs-modifying) and through different mutation surfaces.
