---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Sim

## Domain terms

- ++SIM type++ — SimType.Esim or SimType.Psim — the kind of SIM on the ++Line++ (`Line.simType` · `SIM_TYPE` characteristic on the Mavenir cart item)
- ++ICCID++ — the SIM card identifier on the ++Line++ (`Line.iccid` · `ICCID` characteristic on the Mavenir cart item)
- ++waiting pSIM++ — characteristic on the ++Mavenir customer++; WaitingPsim.Active when a physical SIM order is pending agent completion; WaitingPsim.Cleared after the Customer activates the SIM

eSIM available vs start at physical SIM are Given preconditions on the owning stories (GrowthBook `DISABLE_ESIM` / `DISABLE_PSIM` live in the application layer). Phone compatibility is a Given that selects eSIM vs pSIM.

++available number++ examples are on Determine Number (`stories/onboard-a-customer/get-number/get_new_number_story.spec.md`).

## Examples

### ICCID

| ICCID | example | iccid |
| --- | --- | --- |
| ICCID | valid ICCID | 8901260000000000001 |
| ICCID | ICCID with spaces | 8914410000000 1 |
| ICCID | invalid ICCID | 8914410000000999999 |

---

## Story: Choose Esim

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/SelectSim/ProspectSelecSim.tsx` (`patchCart({ simType: 'eSIM' })`) · `pml-my/src/hooks/useCustomer.ts` (`PATCH` cart)
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` (`PATCH /customer/cart`) · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/patchCartItemProduct.ts` (`SIM_TYPE`)
- Granola: `.context/granola-notes/screenshot-wall.md` L42
- Run: `.context/sandbox-walkthrough/walk-profile-kyc.md` L332–L384

#### Background

*Given* eSIM is available
  *And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++
  *And* the phone supports eSIM

#### Scenario: Choose eSIM

*Given* no ++SIM type++ is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM
*Then* My Paradise stores eSIM on the line
  *And* the Customer is forwarded to Verify ID

#### Scenario: Choose eSIM — already on the line

*Given* the line already has ++SIM type++ eSIM
*When* the Customer selects eSIM
*Then* My Paradise skips the cart patch

#### Scenario: Choose eSIM — cart patch fails

*Given* Mavenir returns an error on cart patch
*When* the Customer selects eSIM
*Then* the SIM selection fails
  *And* the line has no ++SIM type++

---

## Story: Request a Paradise Sim Card

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/SelectSim/ProspectPSim.tsx` · `pml-my/src/pages/Onboarding/components/Iccid/useIccid.ts` (`patchCart({ simType: 'pSIM' })`)
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` (`PATCH /customer/cart`) · `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/patchCartItemProduct.ts` (`SIM_TYPE`)
- Granola: `.context/granola-notes/screenshot-wall.md` L44 · L91 · `.context/granola-notes/weird-stuff.md` L17

#### Background

*Given* the Customer is choosing a physical SIM
  *And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

#### Scenario: Request a Paradise SIM card

*Given* no ++SIM type++ is on the line
  *And* no ++ICCID++ is on the line
*When* the Customer requests a Paradise SIM card
*Then* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM
*Then* My Paradise stores pSIM on the line
  *But* the line has no ++ICCID++
  *And* the Customer is forwarded to Verify ID

#### Scenario: Request a Paradise SIM card — already on the line

*Given* the line already has ++SIM type++ pSIM
*When* the Customer requests a Paradise SIM card
*Then* My Paradise skips the cart patch

#### Scenario: Request a Paradise SIM card — cart patch fails

*Given* Mavenir returns an error on cart patch
*When* the Customer requests a Paradise SIM card
*Then* the SIM selection fails
  *And* the line has no ++SIM type++

---

## Story: Enter Existing Sim

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/SelectSim/ProspectPSim.tsx` · `pml-my/src/pages/Onboarding/components/Iccid/useIccid.ts` (`validateIccid` · `patchCart({ simType: 'pSIM', iccid })`) · `pml-my/src/pages/Onboarding/components/Iccid/config.ts` (`/^[^\s]*$/`)
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` (`GET /inventory/iccid/:number` · `PATCH /customer/cart`) · `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` (`validateIccid`)
- Granola: `.context/granola-notes/screenshot-wall.md` L44–L45 · `11-sim-have-iccid.png`

#### Background

*Given* the Customer is choosing a physical SIM
  *And* the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++

#### Scenario: Enter existing SIM

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*When* the Customer attaches ++ICCID++ ++valid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
  *And* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
*Then* My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line
  *And* the Customer is forwarded to Verify ID

#### Scenario: ICCID contains spaces

*Given* the Customer has ++ICCID++ ++ICCID with spaces++
*When* the Customer attaches ++ICCID++ ++ICCID with spaces++
*Then* the ICCID format is rejected
  *And* My Paradise does not query inventory or patch the cart

#### Scenario: Inventory rejects ICCID

*Given* Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory
*When* the Customer attaches ++ICCID++ ++invalid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++
  *And* My Paradise does not patch the cart
  *And* the ICCID is rejected

---

## Story: Activate Sim

**Story type:** pml-my

**Source**
- Code: `pml-my/src/components/Done/IccidBanner.tsx` (`POST /customer/order/psim-delivered`) · `pml-my/src/pages/Onboarding/components/Iccid/useIccid.ts`
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` (`POST /customer/order/psim-delivered`) · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` (`createOrderPsimDelivered` · `waitingPsimPayload`)
- Granola: `.context/granola-notes/screenshot-wall.md` L46 · `20-almost-there-activate-sim.png` · `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L47–L58

++ICCID++ examples are on Enter Existing Sim.

#### Background

*Given* the Customer is waiting for a Paradise SIM
  *And* the Customer is verified
  *And* the line has ++SIM type++ pSIM
  *But* no ++ICCID++ is on the line
  *And* the ++Mavenir customer++ has ++waiting pSIM++ Active

#### Scenario: Activate Sim

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++
  *And* My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++
  *And* My Paradise sends the pSIM delivered order to Mavenir
*When* Mavenir creates the product order and clears ++waiting pSIM++
*Then* My Paradise stores ++ICCID++ ++valid ICCID++ on the line

#### Scenario: waiting pSIM is absent

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
  *But* the ++Mavenir customer++ has no ++waiting pSIM++ characteristic
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* the pSIM delivered order is rejected

#### Scenario: waiting pSIM already completed

*Given* Mavenir has ++ICCID++ ++valid ICCID++ available in inventory
  *And* the ++Mavenir customer++ has ++waiting pSIM++ Cleared
*When* the Customer activates the SIM with ++ICCID++ ++valid ICCID++
*Then* the pSIM delivered order is rejected

---

## Story: Complete Draft Sim Order

**Story type:** Care

**Source**
- Granola: `.context/granola-notes/screenshot-wall.md` L75–L76 · L91 · `22-dep-orders-grid.png` · `23-dep-order-history.png` · `.context/granola-notes/weird-stuff.md` L17 · L49

**Flagged** — intended GWT; the DEP draft order completion UI has no matching code in `pml-my` or `pml-midtier`; observable from `22-dep-orders-grid.png` and `23-dep-order-history.png`.

#### Background

*Given* a Customer completed the My Paradise onboarding flow
  *And* the Customer's line has ++SIM type++ pSIM
  *But* the Customer never entered an ++ICCID++
  *And* the ++Mavenir customer++ has ++waiting pSIM++ Active

#### Scenario: Complete Draft Sim Order

*Given* Care opens the ++Mavenir customer++ record in Mavenir DEP
  *And* Care sees the draft order in the orders grid (`22-dep-orders-grid.png`)
*When* Care attaches the ++ICCID++ to the draft order and completes it
*Then* the order status in DEP Order History changes from draft to active (`23-dep-order-history.png`)
  *And* the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared
