---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Number

## Epic: Get New Number

### Story: Determine Number

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/LineNumber/ProspectLineNumberSelector.tsx` · `pml-my/src/components/LineNumber/LineNumberSelector.tsx` · `pml-my/src/components/LineNumber/hooks/useGetNumbers.ts` · `pml-my/src/components/LineNumber/SearchInput.tsx`
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png`
- Run: `.context/sandbox-walkthrough/live.log` L3226–L3422 (`/onboarding`) · `.context/sandbox-walkthrough/walk-checkout.md` L2–L103

#### Examples

##### available number

| available number | example | number |
| --- | --- | --- |
| available number | held available number | 4415550100 |
| available number | chosen available number | 4415550101 |

##### search term

| search term | example | input | converted |
| --- | --- | --- | --- |
| search term | James search | JAMES | 52637 |

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario: View available numbers

*But* no ++MSISDN++ is in the ++Mavenir shopping cart++  
*When* the Prospect proceeds to selecting their number  
*Then* My Paradise loads ++available number++ inventory through the Midtier  
  *And* the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list  
  *And* the Prospect can Bring your mobile number  
  *And* the Prospect can search for numbers (up to 5 characters: letters or numbers)  
  *And* the Prospect can Refresh  
  *And* the Continue operation is disabled  
*When* the Prospect selects ++available number++ ++chosen available number++  
*Then* the Continue operation is enabled

#### Scenario: View available numbers — MSISDN in cart

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++  
*When* the Prospect proceeds to selecting their number  
*Then* the Prospect sees their number is ++available number++ ++held available number++  
  *And* the Pick new number operation is disabled  
  *And* the Keep current number operation is enabled  
*When* the Prospect selects ++available number++ ++chosen available number++  
*Then* the Pick new number operation is enabled

#### Scenario: Refresh available numbers

*When* the Prospect clicks Refresh  
*Then* My Paradise loads a fresh set of ++available number++ through the Midtier  
  *And* the Prospect sees a new Available Number list  
  *And* the Continue operation is disabled

#### Scenario: Search for a number

*When* the Prospect enters ++search term++ ++James search++ in the search field  
*Then* the search field helper shows *Your number: JAMES (52637)*  
*When* the Prospect triggers the search  
*Then* My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier

### Story: Query Msisdn Inventory

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `GET /inventory/msisdn` · `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `getNumbers`
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48
- Run: `.context/sandbox-walkthrough/live.log` L3255–L3258 (`GET /mv/inventory/msisdn` 200) · `.context/sandbox-walkthrough/porting-walk.json` L262–L264

#### Scenario: Query MSISDN inventory

*Given* a ++PML customer++ is authenticated in Midtier  
*When* Midtier is asked to query ++MSISDN++ inventory  
*Then* Midtier queries Mavenir for 5 available ++MSISDN++ resources  
  *And* Midtier returns a list of ++available number++ values to My Paradise

### Story: List Msisdn Resources

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `getNumbersRequest` · `pml-midtier/src/entities/Mavenir/controllers/inventory/payloads/msisdn.ts` `msisdnGetPayload` (`/updateAndGetAvailableResources`)
- Granola: `.context/granola-notes/screenshot-wall.md` L77 · `miro-areas/03-resource-inventory-dashboard.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48
- Run: `.context/sandbox-walkthrough/live.log` L3255–L3258 (`GET /mv/inventory/msisdn` 200)

#### Scenario: List MSISDN resources

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory  
*When* Mavenir is asked to list ++MSISDN++ resources (`/updateAndGetAvailableResources`, `size: 5`)  
*Then* Mavenir transitions 5 ++MSISDN++ resources from available to locked  
  *And* Mavenir returns the list of locked ++available number++ values to Midtier

### Story: Search Msisdn Inventory

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `GET /inventory/msisdn/search/:number` · `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `searchNumbers` · `pml-my/src/components/LineNumber/hooks/useSearchNumber.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png`
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L36–L43 (search input empty on `/onboarding`)

#### Scenario: Search MSISDN inventory

*Given* a ++PML customer++ is authenticated in Midtier  
*When* Midtier is asked to search ++MSISDN++ inventory for ++search term++ ++James search++ (`52637`)  
*Then* Midtier queries Mavenir for available ++MSISDN++ resources matching `52637`  
  *And* Midtier returns matching ++available number++ values to My Paradise

### Story: Search Msisdn Resources

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `searchNumbers` · `pml-midtier/src/entities/Mavenir/controllers/inventory/payloads/msisdn.ts` `msisdnSearchPayload` (`pattern_search`)
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png`

#### Scenario: Search MSISDN resources by pattern

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory  
*When* Mavenir is asked to search ++MSISDN++ resources with `pattern_search: 52637` (`/updateAndGetAvailableResources`)  
*Then* Mavenir transitions matching ++MSISDN++ resources from available to locked  
  *And* Mavenir returns the matching ++available number++ values to Midtier

### Story: Choose a Number

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/LineNumber/ProspectLineNumberSelector.tsx` · `pml-my/src/components/LineNumber/hooks/useReserveNumber.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png`
- Run: `.context/sandbox-walkthrough/live.log` L3226–L3422 (`/onboarding`) · `.context/sandbox-walkthrough/walk-checkout.md` L21–L28 · L105 · `.context/sandbox-walkthrough/porting-walk.json` L266–L274

++available number++ examples are on Determine Number (`stories/onboard-a-customer/get-number/get_new_number_story.spec.md`).

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario: Pick new number

*Given* the Prospect has selected ++available number++ ++chosen available number++  
  *But* no ++MSISDN++ is in the ++Mavenir shopping cart++  
*When* the Prospect clicks Continue  
*Then* My Paradise reserves ++available number++ ++chosen available number++ through the Midtier  
  *And* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Pick new number — replace existing

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++  
  *And* the Prospect has selected ++available number++ ++chosen available number++  
*When* the Prospect clicks Pick new number  
*Then* My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier  
  *And* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Keep current number

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++  
*When* the Prospect clicks Keep current number  
*Then* the Prospect is forwarded to Select Sim

### Story: Submit Reserve Number Request to Mid-Tier

**Story type:** pml-my

**Source**
- Code: `pml-my/src/components/LineNumber/hooks/useReserveNumber.ts` `POST` `${env.midtier.mavenir.inventory}/msisdn`
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48
- Run: `.context/sandbox-walkthrough/porting-walk.json` L266–L269 (`POST /mv/inventory/msisdn` 204)

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario: Reserve number

*Given* ++available number++ ++chosen available number++ is selected  
  *But* no ++MSISDN++ is in the ++Mavenir shopping cart++  
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++  
*Then* Midtier returns 204  
  *And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier

#### Scenario: Reserve number — replace existing

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++  
  *And* ++available number++ ++chosen available number++ is selected  
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++  
*Then* Midtier returns 204  
  *And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier

#### Scenario: Reserve number request fails

*Given* ++available number++ ++chosen available number++ is selected  
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++  
  *But* Midtier returns an error  
*Then* My Paradise shows *Failed to reserve your number.*

### Story: Submit Reserve Msisdn

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `POST /inventory/msisdn` · `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `postReserveNumber`
- Granola: `.context/granola-notes/screenshot-wall.md` L32 · `miro-areas/02-pick-number.png`
- Run: `.context/sandbox-walkthrough/porting-walk.json` L266–L269 (`POST /mv/inventory/msisdn` 204)

#### Scenario: Reserve MSISDN

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory  
*When* Midtier is asked to reserve ++MSISDN++ ++available number++ ++chosen available number++  
*Then* Midtier reserves ++available number++ ++chosen available number++ in Mavenir  
  *And* Midtier returns 204 to My Paradise

#### Scenario: Reserve MSISDN — release previous

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked  
  *And* ++MSISDN++ ++available number++ ++held available number++ is reserved  
*When* Midtier is asked to reserve ++available number++ ++chosen available number++ releasing previous ++available number++ ++held available number++  
*Then* Midtier reserves ++available number++ ++chosen available number++ and releases ++available number++ ++held available number++ in Mavenir  
  *And* Midtier returns 204 to My Paradise

### Story: Reserve Msisdn Resource

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `reserveNumberRequest` · `pml-midtier/src/entities/Mavenir/controllers/inventory/payloads/msisdn.ts` `msisdnReservePayload` (`/updateResources` locked→reserved)
- Granola: `.context/granola-notes/screenshot-wall.md` L77 · `miro-areas/03-resource-inventory-dashboard.png` · `.context/granola-notes/weird-stuff.md` L19
- Run: `.context/sandbox-walkthrough/porting-walk.json` L266–L269 (`POST /mv/inventory/msisdn` 204)

#### Scenario: Reserve MSISDN resource

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked in Mavenir inventory  
*When* Mavenir is asked to reserve ++available number++ ++chosen available number++ (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)  
*Then* Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved  
  *And* Mavenir attaches the Paradise Mobile service provider to ++available number++ ++chosen available number++

#### Scenario: Reserve MSISDN resource — release previous

*Given* ++MSISDN++ ++available number++ ++chosen available number++ is locked  
  *And* ++MSISDN++ ++available number++ ++held available number++ is reserved  
*When* Mavenir is asked to reserve ++available number++ ++chosen available number++ and release previous ++available number++ ++held available number++  
*Then* Mavenir transitions ++available number++ ++chosen available number++ from locked to reserved  
  *And* Mavenir transitions ++available number++ ++held available number++ from reserved to available

### Story: Submit Patch Cart With Number Request to Mid-Tier

**Story type:** pml-my

**Source**
- Code: `pml-my/src/components/LineNumber/hooks/useReserveNumber.ts` `patchCart({ msisdn })` · `pml-my/src/hooks/useCustomer.ts` `PATCH` `${env.midtier.mavenir.customer}/cart`
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48
- Run: `.context/sandbox-walkthrough/porting-walk.json` L271–L274 (`PATCH /mv/customer/cart` 200)

#### Scenario: Patch cart with number

*Given* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved  
*When* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier  
*Then* Midtier returns the updated ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Patch cart with number fails

*Given* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved  
*When* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier  
  *But* Midtier returns an error  
*Then* My Paradise shows *Failed to update your cart.*

### Story: Patch Cart With Number

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `PATCH /customer/cart` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `patchCart`
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48
- Run: `.context/sandbox-walkthrough/porting-walk.json` L271–L274 (`PATCH /mv/customer/cart` 200)

#### Scenario: Patch cart with MSISDN

*Given* a ++PML customer++ with a ++Mavenir shopping cart++  
  *And* ++MSISDN++ ++available number++ ++chosen available number++ has been reserved  
*When* Midtier is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++  
*Then* Midtier patches the ++Mavenir shopping cart++ in Mavenir with ++available number++ ++chosen available number++ as the MSISDN characteristic  
  *And* Midtier returns the updated ++PML customer++ to My Paradise

### Story: Patch Shopping Cart

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `patchCartRequest` `PATCH` `shoppingCart/${customerId}`
- Granola: `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48
- Run: `.context/sandbox-walkthrough/porting-walk.json` L271–L274 (`PATCH /mv/customer/cart` 200)

#### Scenario: Patch shopping cart with MSISDN

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item  
  *But* no MSISDN characteristic on the cart item  
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++MSISDN++ ++available number++ ++chosen available number++ as a cart item characteristic  
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with ++available number++ ++chosen available number++ as the MSISDN characteristic  
  *And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier
