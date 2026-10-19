---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Onboarding Plan

## Epic: Get Catalog

### Story: Query Product Offerings And Map To Catalog

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/gateway/controller.ts` (`GatewayController.getCatalogParsed`)

**Story type:** Midtier

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Scenario: Query Product Offerings And Map To Catalog

*Given* Mavenir has returned product offerings for service provider 100000000  
*When* Midtier is asked to query product offerings and map to catalog  
*Then* Midtier filters offerings to valid bundle IDs — ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++  
  *And* strips "PROMO" from ++plan++ ++Internal Test Plan PROMO++ name  
  *And* marks ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++ as isSellable  
  *And* marks ++plan++ ++Internal Test Plan PROMO++ as not isSellable  
  *And* tags ++plan++ ++Ace++ as "Best value"  
  *And* returns the ++plan++ catalog sorted by price descending to Choose Onboarding Plan

### Story: List Product Offerings

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/gateway/controller.ts` (`GatewayController.catalogRequest`)
- Granola: `.context/granola-notes/Modeliong story capabilitites.md` L12
- Granola: `.context/granola-notes/weird-stuff.md` L20 · `01-dep-base-customer.png`

**Story type:** Mavenir

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Scenario: List Product Offerings

*Given* Mavenir catalog for service provider 100000000 is reachable  
*When* Mavenir is asked to list product offerings with channelName CRM  
*Then* Mavenir returns product bundles including ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, ++plan++ ++Atlas++, and ++plan++ ++Internal Test Plan PROMO++ with their productOfferingPrice and bundledProductOffering

## Epic: Get Plan On Cart

### Story: Load Plan Catalog

**Story type:** pml-my

### Story: Choose Onboarding Plan

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/SelectPlan/SelectPlan.tsx`
- Code: `pml-my/src/hooks/useCustomer.ts` (`patchCartPlan`)
- Code: `pml-my/src/pages/Onboarding/app/services/mavenir/useCatalog/useCatalog.ts`
- Code: `pml-my/src/pages/Protected/hooks/useStepRedirect.ts` (`getCurrentOnboardingStepUrl`)
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L21
- Granola: `.context/granola-notes/screenshot-wall.md` L95 · `17-review.png`

**Story type:** pml-my

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`). Outline rows: ++Essentials++, ++Data Freedom++, ++Ace++, ++Atlas++.

#### Background

*Given* the Prospect is in Account Setup  
  *And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario Outline: Choose Onboarding Plan

##### Steps

*But* no ++plan++ is in the ++Mavenir shopping cart++  
  *And* Keep current plan is not shown  
*When* the Prospect is forwarded to Plan Selection  
*Then* the system retrieves the ++plan++ catalog from the Midtier  
  *And* the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++  
  *And* each ++plan++ has a Select operation  
*When* the Prospect clicks Select on ++plan++ ++{scenario}++  
*Then* the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier  
  *And* the ++My Paradise customer++ cart is updated in session with ++{scenario}++  
  *And* the Prospect is forwarded to Time to pick your number

#### Scenario: Choose a different ++plan++

*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++  
*When* the Prospect arrives at Plan Selection from Checkout  
*Then* the Prospect sees "Your current plan Essentials"  
  *And* Keep current plan is enabled  
  *And* the ++plan++ catalog is displayed  
  *And* each ++plan++ has a Select operation  
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++  
*Then* the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier  
  *And* the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++  
  *And* the Prospect is forwarded to Checkout

#### Scenario: Select the ++plan++ already in the cart

*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++  
*When* the Prospect clicks Select on ++plan++ ++Essentials++  
*Then* the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan

#### Scenario: Failed to update plan

**Flagged:** Midtier PATCH failure not reproducible in sandbox; intended GWT.

*Given* Midtier PATCH to ++Mavenir shopping cart++ returns a server error  
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++  
*Then* My Paradise shows "Failed to update new plan choice."  
  *And* the Prospect stays on Plan Selection

### Story: Patch Cart With Plan

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` (`CustomerController.patchCart`, `CustomerController.patchCartRequest`)
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/utils/parseCart.ts`

**Story type:** Midtier

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Scenario: Patch Cart With Plan

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir  
*When* Midtier is asked to patch cart with bundleId for ++plan++ ++Essentials++  
*Then* Midtier fetches the catalog bundle for ++plan++ ++Essentials++ from Mavenir  
  *And* builds the cart item payload with the bundle product offering  
  *And* patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart  
  *And* returns the ++PML customer++ cart with ++plan++ ++Essentials++ bundle to Choose Onboarding Plan

#### Scenario: Patch Cart With Plan — portability plan name updated

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ that has a ++portability++ record in Mavenir  
*When* Midtier is asked to patch cart with bundleId for ++plan++ ++Data Freedom++ and portability planSelected "Data Freedom"  
*Then* Midtier builds the cart item for ++plan++ ++Data Freedom++ with the portability planName characteristic set to "Data Freedom"  
  *And* patches the ++Mavenir shopping cart++ through Mavenir Patch Shopping Cart  
  *And* returns the ++PML customer++ cart with ++plan++ ++Data Freedom++ bundle and updated ++portability++ planName

### Story: Patch Shopping Cart

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` (`CustomerController.patchCartRequest` → `PATCH /v2/shoppingCart/${customerId}`)

**Story type:** Mavenir

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Scenario: Patch Shopping Cart

*Given* a ++Mavenir customer++ with a ++Mavenir shopping cart++ (no bundle) in Mavenir  
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with a bundle cart item for ++plan++ ++Essentials++  
*Then* Mavenir updates the ++Mavenir shopping cart++ with the ++plan++ ++Essentials++ bundle product item  
  *And* returns the patched ++Mavenir shopping cart++ to Patch Cart With Plan

### Story: Keep Current Plan

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/SelectPlan/SelectPlan.tsx` (`NextStepButton` `to='../checkout'`)

**Story type:** pml-my

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).

#### Background

*Given* the Prospect is in Account Setup  
  *And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++  
  *And* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++

#### Scenario: Keep Current Plan

*When* the Prospect clicks Keep current plan  
*Then* the Prospect is forwarded to Checkout
