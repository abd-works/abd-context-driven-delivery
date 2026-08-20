# don-t-put-a-given-for-a-condition-the-system-isn-t-actually-

- **entry_id:** c131b2b3
- **artifact:** .context/sessions/pml-my-current-state/cdd-sketch.md — Stories > Access Selfcare > Sign In scenarios
- **rule:** don't put a Given for a condition the system isn't actually checking/testing
- **wrong:** Given clauses cited metadata.verified true/false as the gate deciding Dashboard vs. resume-onboarding-at-step, but the code (pml-my: Protected.tsx, useLoggedUser.ts, useStepRedirect.ts) never checks metadata.verified for that decision — the real gate is customer.billing.id (userHasAccount), with per-step resume driven by cart.bundle, cart.msisdn/cart.portability, cart.simType, identity.idNumber, billing, and metadata.onboard.done; metadata.verified is set post-checkout from the order-placement response (active-subscriber/order-verified status) and is unrelated to this routing decision.
- **status:** open
