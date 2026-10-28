---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Sign Up Plan

Actor: **Customer**. Website handoff is a navigation fact — there is no Website domain type.

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/examples/purchasable-plans.examples.ts`).  
++catalog voucher++ examples are in this folder (`examples/catalog-voucher.examples.ts`).

**Load Plan Catalog** is owned by Get Onboarding Plan (`stories/onboard-a-customer/get-onboarding-plan/get_onboarding_plan_story.spec.ts` — `planRepository.list()`). This epic seeds `planRepository` as Given for deep-link and voucher stories. It does not re-specify catalog load. Mavenir product-offering hops stay inside that owning story.

---

## Story: Hand Off Sign Up To Onboarding

**Story type:** navigation

**Source**
- Code: `pml-website/src/components/Plans/Plans.tsx` L41–L51 · `pml-website/src/config/app.ts` L9–L11
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L20–L23

Sign-up from the Paradise Mobile website opens My Paradise in a new tab. That arrival is Given on Open Plan Deep Link. No Website domain type.

---

## Story: Open Plan Deep Link

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/SignUp/SignUp.tsx` L9–L27 · `pml-my/src/Router.tsx` L48–L52
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L21 · `.context/granola-notes/weird-stuff.md` L28

My Paradise selects a catalog ++plan++ by id. Unknown id is not found.

### Background

*Given* the plan catalog contains purchasable plans  
  *And* the Customer arrived at sign-up from the Paradise Mobile website

### Scenario Outline: Open Plan Deep Link

#### Steps

*When* the Customer opens a plan deep link for ++plan++ ++{scenario}++  
*Then* ++{scenario}++ is selected  
  *And* the Customer continues to Enter Account Credentials

### Scenario: Unknown plan deep link

*Given* the plan catalog contains purchasable plans  
  *But* the deep-link plan id is not in the catalog  
*When* the Customer opens a plan deep link  
*Then* the plan is not found

---

## Story: Load Plan Catalog

Owned by Get Onboarding Plan. Seed `planRepository` here; do not duplicate `planRepository.list()`.

---

## Story: Apply Catalog Voucher

**Story type:** pml-my → Vouchera

**Source**
- Code: `pml-my/src/pages/SignUp/steps/Catalog/Catalog.tsx` · `pml-my/src/pages/SignUp/steps/Catalog/useCatalogVoucher.ts` · `pml-my/src/pages/Onboarding/app/components/Voucher/useVoucherValidate.ts` L10–L26 (`GET /voucher/validate`)
- Code: `pml-midtier/src/entities/Voucher/controller.ts` L58–L126 (`VoucherController.getVoucherRequest` → `GET ${vouchera}/vouchers/${code}`)
- Code: `pml-vouchera/apps/api/src/vouchers/vouchers.controller.ts` L47–L57 · `pml-vouchera/apps/api/src/vouchers/vouchers.service.ts` L68–L72
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L30–L36
- Run: `.context/sandbox-walkthrough/live.log` L2271–L2385 (`/sign-up/` Catalog body — "Got a promotion code?")

Catalog voucher is pre-account session state on `Voucher` (`Voucher.apply` / `Voucher.applied` / `Voucher.remove`). `VoucherRepository.get` is the Vouchera read. It is not `Cart.applyVoucher`.

**Flagged:** live sandbox `/voucher/validate` accepts any code of length 4 or more. Intended: invalid / expired / redeemed reject with a domain Error. The Vouchera stub seeds those states so the stories can assert the Error.

### Background

*Given* the plan catalog contains purchasable plans

### Scenario: Apply Catalog Voucher via deep link

*Given* Vouchera has ++catalog voucher++ ++valid catalog voucher++  
*When* the Customer applies ++catalog voucher++ ++valid catalog voucher++ from a promotional voucher link  
*Then* My Paradise sends the voucher code to Vouchera  
*When* Vouchera returns the voucher view  
*Then* the catalog voucher is applied  
  *And* the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent

### Scenario: Apply Catalog Voucher manually

*Given* the Customer is selecting a plan  
  *And* Vouchera has ++catalog voucher++ ++valid catalog voucher++  
*When* the Customer applies ++catalog voucher++ ++valid catalog voucher++  
*Then* My Paradise sends the voucher code to Vouchera  
*When* Vouchera returns the voucher view  
*Then* the catalog voucher is applied  
  *And* the voucher discounts ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ by 10 percent

### Scenario: Short catalog voucher code is rejected

*Given* the Customer is selecting a plan  
*When* the Customer applies a catalog voucher shorter than 4 characters  
*Then* the catalog voucher is rejected  
  *And* Vouchera is not asked for the voucher

### Scenario: Remove Catalog Voucher

*Given* the Customer is selecting a plan with ++catalog voucher++ ++valid catalog voucher++ applied  
*When* the Customer removes ++catalog voucher++ ++valid catalog voucher++  
*Then* the catalog has no catalog voucher

### Scenario Outline: Apply unusable catalog voucher

**Flagged:** sandbox accepts any code of length 4 or more. Intended GWT — stub seeds the unusable voucher.

#### Steps

*Given* the Customer is selecting a plan  
  *And* Vouchera has ++catalog voucher++ ++{scenario}++  
*When* the Customer applies ++{scenario}++  
*Then* My Paradise sends the voucher code to Vouchera  
*When* Vouchera returns  
*Then* the catalog voucher is rejected
