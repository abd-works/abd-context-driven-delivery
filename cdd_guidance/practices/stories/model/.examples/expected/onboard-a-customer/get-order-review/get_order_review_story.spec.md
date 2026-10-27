---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Order Review

++plan++ examples are on Onboard A Customer (`stories/onboard-a-customer/story-scenarios.md`).  
++voucher++ examples are on Apply Catalog Voucher (`stories/onboard-a-customer/get-sign-up-plan/get_sign_up_plan_story.spec.md`).  
++available number++ examples are on Determine Number (`stories/onboard-a-customer/get-number/get_new_number_story.spec.md`).

## Epic: Get Order Review

### Story: Check The Order

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/Checkout/steps/Review.tsx`
- Code: `pml-my/src/components/Review/ReviewPersonalSection.tsx`, `ReviewNumberSection.tsx`, `ReviewUpsell.tsx`, `ReviewPlan.tsx`
- Granola: `.context/granola-notes/screenshot-wall.md` L62–L63
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L257–L356 · L451–L593

**Story type:** pml-my

#### Background

*Given* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
  *And* ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
  *And* the Customer has chosen eSIM

#### Scenario: Check the order

*Given* the Customer has completed account setup, number, SIM, and profile
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
  *And* the Checkout step is the next onboarding step

#### Scenario: Check the order with port-in number

*Given* the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
  *And* the Checkout step is the next onboarding step

---

## Epic: Get Data Freedom Upgrade

### Story: Upgrade To Data Freedom

**Source**
- Code: `pml-my/src/components/Review/ReviewUpsell.tsx`
- Code: `pml-my/src/hooks/useCustomer.ts`
- Granola: `.context/granola-notes/screenshot-wall.md` L63 · `18-upsell-go-to-payment.png`
- Run: `.context/sandbox-walkthrough/walk-checkout.md` L257–L356 · L358–L449

**Story type:** pml-my

#### Examples

| plan upgrade | example | currentPlan | newPlan |
| --- | --- | --- | --- |
| plan upgrade | upgrade to Data Freedom | Essentials | Data Freedom |
| plan upgrade | upgrade to Ace | Data Freedom | Ace |
| plan upgrade | upgrade to Atlas | Ace | Atlas |

#### Background

*Given* the Customer is reviewing their order
  *And* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario Outline: Upgrade plan from review

*Given* ++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
*Then* My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle
  *And* the Customer sees *You have been upgraded!*

#### Scenario: No upsell shown on top-tier plan

*Given* ++plan++ ++Atlas++ is in the ++Mavenir shopping cart++
*When* the Customer proceeds to reviewing their order
*Then* no upgrade option is available

---

## Epic: Change Plan From Review

### Story: Change Plan From Review

**Source**
- Code: `pml-my/src/pages/Onboarding/pages/Checkout/steps/Review.tsx`
- Code: `pml-my/src/pages/Onboarding/pages/SelectPlan/SelectPlan.tsx`
- Granola: `.context/granola-notes/screenshot-wall.md` L62 · `17-review.png`

**Story type:** pml-my

#### Background

*Given* the Customer is reviewing their order
  *And* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++

#### Scenario: Select a different plan from review

*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++Data Freedom++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise stores ++plan++ ++Data Freedom++ as the cart bundle
  *And* the Customer is forwarded to Checkout

#### Scenario: Keep current plan from review

*Given* the Customer has opened plan selection from review
*When* the Customer keeps their current plan
*Then* the Customer is forwarded to Checkout

#### Scenario: Select the plan already in the cart from review

*Given* the Customer has opened plan selection from review
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Essentials++
*Then* the cart bundle remains ++plan++ ++Essentials++

#### Scenario: Plan update fails from review

**Flagged** — sandbox stub does not trigger a Midtier failure during plan select.

*Given* the Customer has opened plan selection from review
  *And* Mavenir returns an error on cart patch
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++
*Then* My Paradise shows *Failed to update new plan choice.*
  *And* the cart bundle remains ++plan++ ++Essentials++
