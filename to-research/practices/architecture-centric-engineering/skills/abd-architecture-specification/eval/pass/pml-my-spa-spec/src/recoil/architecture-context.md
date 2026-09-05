# Mechanism: Persistence

### Overview

Persistence in pml-my is in-session-only: Recoil atoms hold the working copy of every domain concept the SPA needs during a single browser session; pml-midtier is the system of record. A full page refresh recovers state by re-fetching from midtier using the Amplify-managed Cognito tokens in `localStorage`. On sign-out the `atoms[]` reset manifest is iterated and every session atom is cleared so no PII leaks between users on a shared device.

There is no client-side database; `recoil-persist` is present in `package.json` from an earlier prototype but no `persistAtom` effects are attached.

### File Structure

```
src/
+-- recoil/
|   +-- customerAtom.ts             <- full <<Customer>> object; default {} as Customer
|   +-- sessionAtom.ts              <- { isLogged; onboardingStep } for step-resume redirect
|   +-- accountAtom.ts              <- sign-up credential buffer between sign-up and confirm
|   +-- selectedPlanAtom.ts         <- <<Plan>> | null during onboarding
|   +-- utmAtom.ts                  <- UTM campaign attribution captured once at mount
+-- pages/
|   +-- Onboarding/
|   |   +-- config.ts               <- atoms[] reset manifest fed to useResetRecoilState on sign-out
|   |   +-- recoil/atoms/           <- onboarding-scoped atoms (numberOptionsAtom, personaDataAtom, ...)
|   +-- My/
|       +-- recoil/subscription.ts  <- subscriptionAtom + subscriptionSelector for multi-line self-care
+-- services/aws/cognito.ts         <- signOut iterates the reset manifest and clears localStorage
```

### Participants

| Class / Module              | Responsibility                                                                                       | Collaborators                                    |
| --------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `customerAtom`              | Full `Customer` working copy; default `{} as Customer`; reads use optional chaining                  | All domain modules                               |
| `selectedPlanAtom`          | Onboarding plan selection; flows from SelectPlan to Checkout                                         | Onboarding pages                                 |
| `utmAtom`                   | Campaign attribution captured once at mount                                                          | `AnalyticsWrapper`, purchase events              |
| `subscriptionSelector`      | Derived state choosing the active line for multi-line self-care                                      | Self-Care pages                                  |
| `config.atoms[]`            | Reset manifest enumerating every session atom; iterated on sign-out                                  | `signOut()` in `cognito.ts`                      |
| Amplify token store         | SDK-managed `localStorage` entries for Cognito tokens; survives page refresh                         | Amplify SDK (opaque to feature code)             |

### Class Specification

```mermaid
classDiagram
    class CustomerAtom {
        +default: {} as Customer
        +useRecoilValue() Customer
        +useSetRecoilState() (next: Customer) -> void
    }
    class ResetManifest ["config.atoms[]"] {
        +customerAtom
        +sessionAtom
        +selectedPlanAtom
        +utmAtom
        +accountAtom
        +...onboarding-scoped atoms
    }
    class SignOut {
        +signOut() void
        +iterates ResetManifest
    }
    SignOut --> ResetManifest : iterates
    SignOut --> CustomerAtom : resets
```

### Rules

- **Atoms are written by mutation hooks on `result.success` only.** Components never write atoms directly; they call the hook, which decides whether to write.
- **Reads use optional chaining.** Atom defaults are `{}` casts (not null-safe), so `customer.cart?.simType` is the correct shape; `customer.cart.simType` will compile but break.
- **Every session atom appears in `config.atoms[]`.** Adding a new top-level atom means adding it to the manifest -- forgetting it leaks state across sessions on the same device.
- **No persistence outside Amplify's token store.** Domain state is not cached to `localStorage`, `sessionStorage`, or IndexedDB; a refresh always re-fetches from midtier.
- **Sign-out is the only legitimate reset path.** Component unmount does not reset atoms.

### Canonical Patterns

```typescript
// src/recoil/customerAtom.ts
export const customerAtom = atom<Customer>({
  key: 'customerAtom',
  default: {} as Customer,
})

// src/pages/Onboarding/config.ts
export const atoms = [
  customerAtom,
  sessionAtom,
  accountAtom,
  selectedPlanAtom,
  utmAtom,
  numberOptionsAtom,
  personaDataAtom,
  simTypeHelperAtom,
  backToCheckoutAtom,
]

// src/services/aws/cognito.ts (sign-out reset shape)
export async function signOut() {
  await Auth.signOut()
  atoms.forEach((atom) => useResetRecoilState(atom)())
}
```
