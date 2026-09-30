---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Applied Voucher

## Domain terms

- ++voucher++ — Vouchera promotion code stored on the ++Mavenir customer++ `voucher` characteristic after apply. Carries `discount` (percent or amount off) or `trial` metadata. Vocabulary consistent with Get Sign Up Plan.
- ++voucher credit++ — discount amount displayed on the plan price at Order Review (e.g. *10% on us!*).

## Examples

### voucher

| voucher | example | code |
| --- | --- | --- |
| voucher | valid percent voucher | STUBPORT10 |
| voucher | valid trial voucher | TRIAL30 |
| voucher | invalid voucher | NOPE |
| voucher | expired voucher | EXPIRED |
| voucher | redeemed voucher | USED |

| voucher | example | helper |
| --- | --- | --- |
| voucher | invalid voucher | Invalid code. Please try again. |
| voucher | expired voucher | Sorry this code has expired. |
| voucher | redeemed voucher | The code you entered was already redeemed. |

---

## Story: Submit Apply Voucher Request to Mid-Tier

**Source**
- Code: `pml-my/src/pages/Onboarding/app/components/Voucher/useVoucherCustomer.ts` · `pml-my/src/pages/Onboarding/app/components/Voucher/VoucherFieldCustomer.tsx` · `pml-my/src/components/Review/ReviewPlan.tsx`
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L35
- Granola: `.context/granola-notes/screenshot-wall.md` L63 · `18-upsell-go-to-payment.png`
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L350–355 · L451–535

**Story type:** pml-my

### Background

*Given* the Prospect is in Order Review

### Scenario: Apply Voucher

*But* no ++voucher++ is applied  
*When* the Prospect submits ++voucher++ ++valid percent voucher++ to the Midtier  
*Then* My Paradise applies ++voucher++ ++valid percent voucher++ to the ++Mavenir customer++ through the Midtier  
  *And* My Paradise stores the ++voucher++ on the ++My Paradise customer++ in Session

### Scenario: Add code disabled below 4 characters

*But* no ++voucher++ is applied  
*When* the Prospect enters a promotion code shorter than 4 characters in the promotion code field  
*Then* the Add code operation is disabled

### Scenario Outline: Submit unusable ++voucher++

#### Steps

*But* no ++voucher++ is applied  
*When* the Prospect submits ++voucher++ ++{scenario}++ to the Midtier  
*Then* the promotion code shows helper text {helper}

**Flagged: Intended.** ++expired voucher++ and ++redeemed voucher++: Midtier `postVoucher` returns 400 without body; `postVoucher.errors.expired` and `.redeemed` never fire — client shows *Something went wrong.* instead. Intended: midtier returns a typed error body so the client shows the specific {helper} text.

### Scenario: Midtier or Vouchera error

*Given* Midtier returns an unexpected error for the voucher request  
*But* no ++voucher++ is applied  
*When* the Prospect submits a ++voucher++ to the Midtier  
*Then* the promotion code shows *Something went wrong.*

### Scenario: Remove applied voucher

*Given* ++voucher++ ++valid percent voucher++ is applied  
*When* the Prospect removes ++voucher++ ++valid percent voucher++  
*Then* My Paradise removes ++voucher++ ++valid percent voucher++ from the ++Mavenir customer++ through the Midtier  
  *And* My Paradise stores the voucher removal on the ++My Paradise customer++ in Session

---

## Story: Get Vouchera Voucher and Patch Mavenir Customer

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` (`POST /customer/voucher`, `DELETE /customer/voucher`) · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` (`postVoucher`, `deleteVoucher`) · `pml-midtier/src/entities/Voucher/controller.ts` (`getVoucherRequest`) · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/voucher.ts` · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/deleteVoucher.ts`
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L30–L35
- Granola: `.context/granola-notes/Modeliong story capabilitites.md` L50

**Story type:** Midtier

**Compound story — confirmed intentional per `right-size-story-nodes`.** `CustomerController.postVoucher` calls `VoucherController.getVoucherRequest` (Vouchera `GET /vouchers/{code}`) and then `patchCustomerRequest` (Mavenir `PATCH patchaccount`) in one handler. My Paradise sends one request (`POST /customer/voucher`) and receives one response. Splitting would require two separate Midtier endpoints, which do not exist. Vouchera and Mavenir each have their own callee stories on the map.

### Background

*Given* Midtier has a valid ++account token++ for the Prospect  
  *And* a ++Mavenir customer++ exists for the Prospect

### Scenario: Get Vouchera Voucher and Patch Mavenir Customer

*When* Midtier is asked to apply ++voucher++ ++valid percent voucher++  
*Then* Midtier reads ++voucher++ ++valid percent voucher++ from Vouchera  
  *And* Midtier patches the ++Mavenir customer++ with the ++voucher++ characteristic  
  *And* Midtier returns ++voucher++ ++valid percent voucher++ to My Paradise

### Scenario: Expired voucher

*When* Midtier is asked to apply ++voucher++ ++expired voucher++  
*Then* Midtier reads ++voucher++ ++expired voucher++ from Vouchera  
  *And* Midtier returns 400 Bad Request

### Scenario: Redeemed voucher

*When* Midtier is asked to apply ++voucher++ ++redeemed voucher++  
*Then* Midtier reads ++voucher++ ++redeemed voucher++ from Vouchera  
  *And* Midtier returns 400 Bad Request

### Scenario: Invalid voucher code

*When* Midtier is asked to apply ++voucher++ ++invalid voucher++  
*Then* Vouchera returns 404 Not Found for ++voucher++ ++invalid voucher++  
  *And* Midtier returns 404 Not Found

### Scenario: Trial voucher requires a trial plan

*Given* the ++Mavenir customer++ ++Mavenir shopping cart++ holds a non-trial ++plan++ ++Essentials++  
*When* Midtier is asked to apply ++voucher++ ++valid trial voucher++  
*Then* Midtier returns 500 — trial voucher requires a trial plan

**Flagged: Intended.** No sandbox evidence for trial vouchers; `trialPlans` config keys required in live environment.

### Scenario: Remove applied voucher

*Given* the ++Mavenir customer++ has a `voucher` characteristic for ++voucher++ ++valid percent voucher++  
*When* Midtier is asked to remove the ++voucher++  
*Then* Midtier patches the ++Mavenir customer++ to remove the ++voucher++ characteristic  
  *And* Midtier returns 204 No Content

---

## Story: Validate Voucher

**Source**
- Code: `pml-vouchera/apps/api/src/vouchers/vouchers.controller.ts` · `pml-midtier/src/entities/Voucher/controller.ts` (`getVoucherRequest` — callee context)
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L32 · L35
- Granola: `.context/granola-notes/Modeliong story capabilitites.md` L50

**Story type:** Vouchera

### Scenario: Validate Voucher — percentage discount

*Given* Vouchera has ++voucher++ ++valid percent voucher++  
*When* Vouchera is asked to read ++voucher++ ++valid percent voucher++  
*Then* Vouchera returns ++voucher++ ++valid percent voucher++ with code STUBPORT10, campaign, discount type percentage value 10, redemption counts, and plan eligibility

### Scenario: Validate Voucher — trial

*Given* Vouchera has ++voucher++ ++valid trial voucher++  
*When* Vouchera is asked to read ++voucher++ ++valid trial voucher++  
*Then* Vouchera returns ++voucher++ ++valid trial voucher++ with code TRIAL30, trial plan with 30 free days, and redemption counts

**Flagged: Intended.** No sandbox evidence for trial vouchers.

### Scenario: Unknown voucher code

*Given* Vouchera has no ++voucher++ for ++voucher++ ++invalid voucher++  
*When* Vouchera is asked to read ++voucher++ ++invalid voucher++  
*Then* Vouchera returns 404 Not Found

---

## Story: Patch Mavenir Customer

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/voucher.ts` · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/deleteVoucher.ts` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts`
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L32
- Granola: `.context/granola-notes/Modeliong story capabilitites.md` L50

**Story type:** Mavenir

### Scenario: Store Voucher on Mavenir Customer

*Given* Mavenir has a ++Mavenir customer++ for the Prospect  
*When* Mavenir is asked to patch the ++Mavenir customer++ with a `voucher` characteristic  
*Then* Mavenir stores the JSON-encoded ++voucher++ ++valid percent voucher++ as the `voucher` characteristic on the ++Mavenir customer++

### Scenario: Remove Voucher from Mavenir Customer

*Given* the ++Mavenir customer++ has a `voucher` characteristic for ++voucher++ ++valid percent voucher++  
*When* Mavenir is asked to patch the ++Mavenir customer++ removing the `voucher` characteristic  
*Then* Mavenir removes the `voucher` characteristic from the ++Mavenir customer++ characteristic array

---

## Story: Store Vouchera Voucher on My Paradise Customer in Session

**Source**
- Code: `pml-my/src/pages/Onboarding/app/components/Voucher/VoucherFieldCustomer.tsx` · `pml-my/src/pages/Onboarding/pages/Profile/hooks/useFormUserData/useVoucherCode.ts` · `pml-my/src/pages/Protected/hooks/useVoucherCode.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L63 · `18-upsell-go-to-payment.png`
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L451–535

**Story type:** pml-my

### Scenario: Store Voucher on My Paradise Customer in Session

*Given* the Prospect is in Order Review  
  *And* the Midtier has returned ++voucher++ ++valid percent voucher++  
*When* My Paradise stores ++voucher++ ++valid percent voucher++ on the ++My Paradise customer++ in session  
*Then* the promotion code field shows ++voucher++ ++valid percent voucher++ applied  
  *And* the plan price shows $49.50 with ++voucher credit++ *10% on us!* for ++plan++ ++Data Freedom++ ($55)  
  *And* the Prospect proceeds to Get Order Review

### Scenario: Remove Voucher from My Paradise Customer in Session

*Given* the Prospect is in Order Review  
  *And* ++voucher++ ++valid percent voucher++ is stored on the ++My Paradise customer++ in session  
*When* My Paradise removes ++voucher++ ++valid percent voucher++ from the ++My Paradise customer++  
*Then* the promotion code field shows the Add code input  
  *And* the plan price reverts to $55 for ++plan++ ++Data Freedom++

### Scenario: Auto-apply catalog voucher on Profile page entry

*Given* the Prospect is in Profile Entry  
  *And* the ++My Paradise customer++ has no ++voucher++ applied  
  *And* session storage holds ++voucher++ ++valid percent voucher++ for the ++My Paradise customer++  
*When* My Paradise applies the session voucher to the Midtier on Profile page entry  
*Then* My Paradise stores ++voucher++ ++valid percent voucher++ on the ++My Paradise customer++ in session  
  *And* the session storage entry for the ++My Paradise customer++ is cleared

**Flagged.** `useVoucherCode.ts` calls `localStorage.removeItem(customer.metadata.id)` but the entry was set via `sessionStorage.setItem`. The session storage entry is not actually removed — intended behaviour is to clear it after apply.

### Scenario: Auto-apply fails — voucher not working

*Given* the Prospect is in Profile Entry  
  *And* the ++My Paradise customer++ has no ++voucher++ applied  
  *And* session storage holds a ++voucher++ code that the Midtier rejects  
*When* My Paradise applies the session voucher to the Midtier on Profile page entry  
*Then* My Paradise shows *The promotional or referral code you have entered is not working. Continue signing up and try again at the checkout page.*  
  *And* no ++voucher++ is stored on the ++My Paradise customer++ in session

**Flagged: Intended.** Sandbox `/customer/voucher` stub accepts any code ≥ 4 characters; a live Vouchera rejection is required to reach this path.
