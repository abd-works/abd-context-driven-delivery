# Mechanism: Analytics Attribution

### Overview

Analytics Attribution is the mechanism by which campaign attribution (UTM parameters) and conversion events flow through a single typed surface to the analytics vendors -- GA4 via ReactGA, GTM, and Hotjar. UTM parameters are captured once at app root via `AnalyticsWrapper` and live in `utmAtom` for the rest of the session; event names are constrained by `as const` arrays in `events.ts`; sender functions in `sendEvent.ts` wrap vendor SDK calls; an `checkEmailType()` gate excludes test-domain signups from production purchase metrics.

### File Structure

```
src/
+-- recoil/
|   +-- utmAtom.ts                       <- UTM campaign parameters; session-scoped
+-- utils/
|   +-- analytics/
|       +-- events.ts                    <- typed event name registries (as const arrays)
|       +-- sendEvent.ts                 <- sendPageViewEvent, sendGAPurchaseEvent, sendUserAttributesEvent
|       +-- AnalyticsWrapper.tsx         <- captures window.location.search; writes utmAtom
|       +-- types.ts                     <- analytics type re-exports
|       +-- index.ts                     <- barrel export
+-- main.tsx                             <- vendor SDK init in non-development (ReactGA, GTM, Hotjar)
```

### Participants

| Class / Module                | Responsibility                                                                                  | Collaborators                                   |
| ----------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `events.ts`                   | `as const` arrays of event names; compile-time typo prevention                                  | All event senders                               |
| `sendEvent.ts`                | Typed sender functions wrapping ReactGA and Hotjar                                              | `ReactGA`, `hotjar`, `events.ts`                |
| `AnalyticsWrapper`            | Mounts inside `RecoilRoot`; parses `window.location.search` once; writes `utmAtom`              | `utmAtom`, `query-string`                       |
| `utmAtom`                     | `{ utmSource, utmMedium, utmCampaign, utmTerm, utmContent }`                                    | All conversion events                           |
| `checkEmailType()`            | Classifies `identity.email` as `'TEST' \| 'CUSTOMER' \| 'GUEST'`; gates purchase send            | `env.google.testDomains`                        |
| `hotjar.identify()`           | PII identity call (name, address, cart, UTM); privacy-reviewed before production enablement     | `sendUserAttributesEvent`                       |

### Flow

```mermaid
sequenceDiagram
    participant User
    participant AW as "AnalyticsWrapper"
    participant UTM as "utmAtom"
    participant Hook as "useCustomer / usePayment"
    participant Send as "sendEvent.ts"
    participant GA4 as "ReactGA"
    participant HJ as "Hotjar"

    User->>AW: app loads with ?utm_source=google&utm_medium=cpc
    AW->>AW: useEffect parses search string
    AW->>UTM: setUtm({ utmSource: 'google', utmMedium: 'cpc', ... })
    User->>Hook: completes onboarding; createOrder() succeeds
    Hook->>Send: sendGAPurchaseEvent('purchase', cart, identity)
    Send->>Send: checkEmailType(identity.email) -> 'CUSTOMER'
    Send->>GA4: ReactGA.event('purchase', { transaction_id, items, value })
    Hook->>Send: sendUserAttributesEvent(utmParams, customer)
    Send->>HJ: hotjar.identify(customerId, { utmSource, name, msisdn, ... })
```

### Rules

- **No component calls `window.gtag`, `window.dataLayer.push`, or `hj()` directly.** All vendor calls go through `sendEvent.ts`.
- **Event names are constants.** Magic-string event names in `sendEvent` calls are forbidden; they must come from the `as const` arrays in `events.ts`.
- **Test-domain emails never emit purchase events.** `checkEmailType` returns `'TEST'` for emails matching `env.google.testDomains`; senders short-circuit on `'TEST'`.
- **UTM capture is single-shot.** `AnalyticsWrapper`'s effect runs once at mount; subsequent navigation does not overwrite `utmAtom`.
- **Hotjar identity payloads are privacy-reviewed.** Any new field added to `sendUserAttributesEvent` requires review because Hotjar receives PII.

### Canonical Patterns

```typescript
// src/utils/analytics/sendEvent.ts
export function sendGAPurchaseEvent(
  eventName: EventPurchaseList[number],
  cart: Cart,
  identity: Identity,
) {
  const emailType = checkEmailType(identity.email)
  sendGAEvent(eventName, 'Onboarding Type', emailType)
  if (emailType !== 'CUSTOMER') return
  ReactGA.event('purchase', {
    transaction_id: cart.transactionId,
    currency: 'USD',
    value: cart.plan?.price ?? 0,
    items: [{ item_id: cart.plan?.id, item_name: cart.plan?.name }],
  })
}

// src/utils/analytics/AnalyticsWrapper.tsx
export function AnalyticsWrapper({ children }: { children: ReactNode }) {
  const setUtm = useSetRecoilState(utmAtom)
  useEffect(() => {
    const parsed = qs.parse(window.location.search)
    setUtm({
      utmSource: parsed.utm_source as string,
      utmMedium: parsed.utm_medium as string,
      utmCampaign: parsed.utm_campaign as string,
      utmTerm: parsed.utm_term as string,
      utmContent: parsed.utm_content as string,
    })
  }, [setUtm])
  return <>{children}</>
}
```
