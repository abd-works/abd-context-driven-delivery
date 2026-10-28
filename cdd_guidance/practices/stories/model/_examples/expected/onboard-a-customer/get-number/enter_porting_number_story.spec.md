---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Number

## Epic: Get Ported Number

### Story: Bring a Number

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/LineNumber/ProspectLineNumberPortability.tsx` · `pml-my/src/components/LineNumber/LineNumberPortability.tsx` · `pml-my/src/pages/Onboarding/pages/LineNumber/useNumberPortability.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L33 · `miro-areas/05-porting-form.png` · `.context/granola-notes/screenshot-wall.md` L35 · `miro-areas/07-port-sim-with-error-banner.png` · `.context/granola-notes/weird-stuff.md` L30 · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L43
- Run: `.context/sandbox-walkthrough/live.log` L3243–L3261 (`Bring your mobile number` / Get started on `/onboarding`) · `.context/sandbox-walkthrough/walk-checkout.md` L7–L9 · `.context/sandbox-walkthrough/porting-walk.json` L6–L17

**Intended:** Transfer Code on this form. Live form has no Transfer Code field. Continue submits ++portability++ without it.

#### Examples

##### portability

| portability | example | donorOperator | portNumber | accountNumber | userType | accountType | device |
| --- | --- | --- | --- | --- | --- | --- | --- |
| portability | valid portability | Digicel | 4412345678 | 12345 | Residential | Postpaid | Iphone |

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario: Bring a number

*But* no Transfer Code is on Bring your mobile number  
*When* the Prospect clicks Get started on Bring your mobile number  
*Then* the Prospect can enter ++portability++  
  *And* the Prospect can confirm the information is accurate  
  *And* the Prospect can grant permission to Paradise Mobile to bring the number  
  *And* the Continue operation is disabled  
  *And* the Prospect can go Back  
*When* the Prospect enters ++portability++ ++valid portability++ and checks both permissions  
*Then* the Continue operation is enabled  
*When* the Prospect clicks Continue  
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier  
  *And* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++  
  *And* the Prospect is forwarded to Select Sim

**Flagged: Live `porting-2fa` is off.** When the flag is on, Continue forwards to Confirm your number for porting instead of Select Sim.

#### Scenario: Number to be ported is incomplete

*When* the Prospect leaves Number to be ported as the Bermuda prefix only  
*Then* Number to be ported shows *Please enter the full Bermuda number.*  
  *And* the Continue operation stays disabled

#### Scenario: Provider not selected

*When* the Prospect blurs Your current provider without selecting a provider  
*Then* Your current provider shows *Please select a provider.*  
  *And* the Continue operation stays disabled

### Story: Confirm Number Already With Paradise

**Story type:** pml-my

**Source**
- Code: `pml-my/src/components/LineNumber/LineNumberPortability.tsx`
- Granola: `.context/granola-notes/screenshot-wall.md` L33 · `miro-areas/05-porting-form.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L51
- Run: `.context/sandbox-walkthrough/live.log` L3243–L3261 (`Bring your mobile number` on `/onboarding`; no Already With Paradise control)

**Flagged.** Live Bring your mobile number has no Already With Paradise control. Continue gates on the two permission checkboxes only.

**Intended:** the Prospect confirms whether the ++MSISDN++ they are bringing is already with Paradise before ++portability++ is added to the cart.

++portability++ examples are on Bring a Number (`stories/onboard-a-customer/get-number/enter_porting_number_story.spec.md`).

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++  
  *And* the Prospect has entered ++portability++ ++valid portability++  
  *But* no ++portability++ is in the ++Mavenir shopping cart++

#### Scenario: Confirm the number is not already with Paradise

*When* the Prospect proceeds to confirming whether their number is already with Paradise  
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise  
*When* the Prospect confirms the ++MSISDN++ is not already with Paradise  
*Then* My Paradise submits ++portability++ ++valid portability++ to the Midtier  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Confirm the number is already with Paradise

*When* the Prospect proceeds to confirming whether their number is already with Paradise  
*Then* the Prospect can confirm whether the ++MSISDN++ is already with Paradise  
*When* the Prospect confirms the ++MSISDN++ is already with Paradise  
*Then* ++portability++ is not submitted to the Midtier  
  *And* the Prospect is returned to selecting their number

### Story: Evaluate Porting Two Factor Flag

**Story type:** GrowthBook

**Source**
- Code: `pml-my/src/config/flags.ts` `PORTING_2FA` · `pml-my/src/pages/Onboarding/pages/LineNumber/LineNumber.tsx` `useFeatureIsOn` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `growthbook.isOn('porting-2fa')`
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L38–L44
- Run: `.context/sandbox-walkthrough/live.log` L3226–L3422 (`/onboarding` pick number; Confirm your number for porting is not in the dump)

**Flagged: Live `porting-2fa` is off.**

#### Scenario: Porting two factor flag enabled (Intended)

**Flagged: Live `porting-2fa` is off.**

*Given* `porting-2fa` is enabled in GrowthBook  
  *And* the Prospect is in Account Setup  
*When* GrowthBook evaluates the `porting-2fa` flag  
*Then* My Paradise mounts the SMS verification step in the porting wizard  
  *And* My Paradise starts the porting wizard at the SMS verification step when ++portability++ on the ++Mavenir shopping cart++ is unverified

#### Scenario: Porting two factor flag disabled (live)

*Given* `porting-2fa` is disabled in GrowthBook  
  *And* the Prospect is in Account Setup  
*When* GrowthBook evaluates the `porting-2fa` flag  
*Then* My Paradise omits the SMS verification step from the porting wizard

### Story: Submit Portability Request to Mid-Tier

**Story type:** pml-my

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/LineNumber/useNumberPortability.ts` `POST` `${env.midtier.mavenir.customer}/portability`
- Granola: `.context/granola-notes/screenshot-wall.md` L33 · `miro-areas/05-porting-form.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L48

++portability++ examples are on Bring a Number (`stories/onboard-a-customer/get-number/enter_porting_number_story.spec.md`).

#### Background

*Given* the Prospect is in Account Setup  
  *And* a ++My Paradise customer++ with a ++Mavenir shopping cart++  
  *But* no ++portability++ is in the ++Mavenir shopping cart++

#### Scenario: Submit portability request — porting-2fa off (live)

*Given* the Prospect has entered ++portability++ ++valid portability++  
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++  
*Then* Midtier returns a temporary ++MSISDN++ ++available number++ ++held available number++  
  *And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Submit portability request — porting-2fa on, SMS sent (Intended)

**Flagged: Live `porting-2fa` is off.**

*Given* the Prospect has entered ++portability++ ++valid portability++  
  *And* `porting-2fa` is enabled  
*When* My Paradise posts a portability request to Midtier with ++portability++ ++valid portability++  
*Then* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }`  
  *And* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ in the ++Mavenir shopping cart++  
  *And* My Paradise presents the Confirm your number for porting step

#### Scenario: Submit portability request — rate limited, bypass (Intended)

**Flagged: Live `porting-2fa` is off.**

*Given* `porting-2fa` is enabled  
*When* My Paradise posts a ++portability request++  
  *But* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }`  
*Then* My Paradise stores ++portability++ ++valid portability++ and ++available number++ ++held available number++ with `verified: true` in the ++Mavenir shopping cart++  
  *And* the Prospect is forwarded to Select Sim

#### Scenario: Submit portability request — invalid number (Intended)

**Flagged: Live `porting-2fa` is off.**

*Given* `porting-2fa` is enabled  
*When* My Paradise posts a ++portability request++  
  *But* Midtier returns `{ status: invalid_number }`  
*Then* My Paradise shows *This number is invalid.* on Number to be ported

#### Scenario: Submit portability request fails

*When* My Paradise posts a ++portability request++  
  *But* Midtier returns an error  
*Then* My Paradise shows *Failed to save your portability.*

### Story: Query Msisdn Inventory

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `postPortability` → `InventoryController.getNumbersRequest(req, 1)`
- Granola: `.context/granola-notes/screenshot-wall.md` L36 · `miro-areas/08-port-need-sim.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L50

#### Scenario: Query MSISDN inventory for porting

*Given* a ++PML customer++ is authenticated in Midtier  
  *And* ++portability++ is in the portability request  
*When* Midtier queries ++MSISDN++ inventory for a temporary port-in number (`count: 1`)  
*Then* Midtier queries Mavenir for 1 available ++MSISDN++ resource  
  *And* Midtier receives ++available number++ ++held available number++ as the temporary number

### Story: List Msisdn Resources

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/inventory/controller.ts` `getNumbersRequest` · `pml-midtier/src/entities/Mavenir/controllers/inventory/payloads/msisdn.ts` `msisdnGetPayload`
- Granola: `.context/granola-notes/screenshot-wall.md` L36 · `miro-areas/08-port-need-sim.png`

#### Scenario: List MSISDN resources for porting

*Given* ++MSISDN++ resources with available status are in the Mavenir inventory  
*When* Mavenir is asked to list 1 ++MSISDN++ resource (`/updateAndGetAvailableResources`, `size: 1`)  
*Then* Mavenir transitions 1 ++MSISDN++ resource from available to locked  
  *And* Mavenir returns ++available number++ ++held available number++ as the locked resource to Midtier

### Story: Submit Reserve Msisdn

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `postPortability` → `InventoryController.reserveNumberRequest` (`portin: true`)
- Granola: `.context/granola-notes/screenshot-wall.md` L36 · `miro-areas/08-port-need-sim.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L50

#### Scenario: Reserve temporary MSISDN for porting

*Given* ++MSISDN++ ++available number++ ++held available number++ is locked  
*When* Midtier reserves ++available number++ ++held available number++ as a port-in temporary number (`portin: true`)  
*Then* Midtier reserves ++available number++ ++held available number++ in Mavenir with the port-in flag  
  *And* Midtier returns 204

### Story: Reserve Msisdn Resource

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/inventory/payloads/msisdn.ts` `msisdnReservePayload` (`portin` → `kv_tempNumber`)
- Granola: `.context/granola-notes/screenshot-wall.md` L36 · `miro-areas/08-port-need-sim.png` · `.context/granola-notes/weird-stuff.md` L16

#### Scenario: Reserve MSISDN resource as temporary port-in number

*Given* ++MSISDN++ ++available number++ ++held available number++ is locked in Mavenir inventory  
*When* Mavenir is asked to reserve ++available number++ ++held available number++ with `kv_tempNumber: true` (`/updateResources`, locked → reserved, relatedParty: Paradise Mobile)  
*Then* Mavenir transitions ++available number++ ++held available number++ from locked to reserved  
  *And* Mavenir marks ++available number++ ++held available number++ as a temporary port-in number (`kv_tempNumber`)

### Story: Patch Cart With Portability

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/mavenir.routes.ts` `POST /customer/portability` · `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `postPortability` `patchCartRequest` (`portability`)
- Granola: `.context/granola-notes/screenshot-wall.md` L33 · `miro-areas/05-porting-form.png`

#### Scenario: Patch cart with portability

*Given* a ++PML customer++ with a ++Mavenir shopping cart++  
  *And* ++MSISDN++ ++available number++ ++held available number++ has been reserved as the temporary port-in number  
  *And* ++portability++ ++valid portability++ is in the request  
*When* Midtier patches the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ and ++available number++ ++held available number++  
*Then* Midtier patches the ++Mavenir shopping cart++ in Mavenir with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device)  
  *And* Midtier returns the updated ++PML customer++ with ++portability++ in the ++Mavenir shopping cart++

### Story: Patch Shopping Cart

**Story type:** Mavenir

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `patchCartRequest` `PATCH` `shoppingCart/${customerId}` (`getCartPortabilityChars`)
- Granola: `.context/granola-notes/screenshot-wall.md` L36 · `miro-areas/08-port-need-sim.png` · `.context/granola-notes/2026-08-25-paradise-mobile-onboarding-flow.md` L50

#### Scenario: Patch shopping cart with portability

*Given* a ++Mavenir shopping cart++ with a plan bundle cart item and temporary ++MSISDN++ ++available number++ ++held available number++  
*When* Mavenir is asked to patch the ++Mavenir shopping cart++ with ++portability++ ++valid portability++ characteristics  
*Then* Mavenir updates the ++Mavenir shopping cart++ cart item with portability characteristics (planName, portinNumber, donorOperator, accountType, userType, accountNumber, device, portin, requestType)  
  *And* Mavenir returns the updated ++Mavenir shopping cart++ to Midtier

### Story: Send Port Verification

**Story type:** Midtier

**Source**
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `postPortability` / `postPortabilityResend` → `TwilioService.startPortabilityVerification`
- Granola: `.context/granola-notes/screenshot-wall.md` L34 · `miro-areas/06-port-sms-verify.png`

**Flagged: Live `porting-2fa` is off.**

#### Scenario: Send port verification SMS

*Given* `porting-2fa` is enabled  
  *And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++  
*When* Midtier sends port verification to ++portability++ ++valid portability++ portNumber  
*Then* Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber  
  *And* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise

#### Scenario: Send port verification — rate limited

*Given* `porting-2fa` is enabled  
*When* Midtier sends port verification  
  *But* Twilio rate limits the request  
*Then* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise

#### Scenario: Send port verification — invalid number

*Given* `porting-2fa` is enabled  
*When* Midtier sends port verification  
  *But* Twilio rejects the number as invalid  
*Then* Midtier returns `{ status: invalid_number }` to My Paradise

### Story: Send Verification Sms

**Story type:** Twilio

**Source**
- Code: `pml-midtier/src/services/Twilio/twilio.service.ts` `startPortabilityVerification` (`verifications.create` channel `sms`)
- Granola: `.context/granola-notes/screenshot-wall.md` L34 · `miro-areas/06-port-sms-verify.png`

**Flagged: Live `porting-2fa` is off.**

#### Scenario: Send verification SMS

*Given* `porting-2fa` is enabled  
  *And* ++portability++ ++valid portability++ portNumber is a valid Bermuda number  
*When* Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber  
*Then* Twilio creates a verification for ++portability++ ++valid portability++ portNumber (`channel: sms`)  
  *And* Twilio returns `sent` to Midtier

#### Scenario: Send verification SMS — rate limited

*Given* `porting-2fa` is enabled  
*When* Twilio is asked to send a verification SMS  
  *But* the rate limit for ++portability++ ++valid portability++ portNumber is exceeded  
*Then* Twilio returns `rate_limited` to Midtier
