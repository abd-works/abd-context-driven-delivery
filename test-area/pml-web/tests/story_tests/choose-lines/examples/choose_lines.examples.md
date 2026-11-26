---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Choose Lines

Everything that happens to the onboarding cart before the account exists. The **Customer** reads the plan catalog, puts one or more lines in the cart, looks at the cart, takes lines off, and brings the price down with the family discount or a voucher; PROMO30 unlocks the hidden Promo plan instead. From the cart the **Customer** continues to Create Credentials.

### Evidence

| Source | Note |
|--------|------|
| `sandbox/extracted-context/app-extraction/story-screens/display-plans.jpg` | *Choose Your Unlimited Mobile Plan*: Atlas's card (Unlimited Data, All high-speed data; Unlimited Local Calling; Included Calls to 190+ countries; 70+ Countries included, Talk, text and data, 30GB high-speed data, then slower); the empty-order footer "Add a line to start. 3 or more lines get a family discount.", **Add a voucher**, **Continue** (observed) |
| `story-screens/add-line-to-cart.jpg`, `remove-line-from-cart.jpg`, `view-cart.jpg` | the cart with Line 1 Atlas $193/mo and Line 2 Ace $153/mo, each with its own remove; "$346/mo", "Hide cart 2", "Family discount: save $180 a year with 1 more line"; with one line "$193/mo", "Hide cart 1", "… with 2 more lines" (observed) |
| `story-screens/apply-family-discount.jpg` | three lines struck through ($193 → $188, $153 → $148, $103 → $98); "Family discount: you save $180 a year"; "Family discount · $5 × 3 lines −$15/mo"; "Voucher ALL10, first bill only −$30"; "You pay now $404, then $434/mo"; "$449 → $434/mo"; "Family discount: $180 a year · $240 with a 4th line"; chip "ALL10 −$30 first bill" (observed) |
| `story-screens/apply-voucher.jpg` | the Voucher sheet: "ALL10 — $10 off every line", **Remove**, **Done** (observed) |
| `story-screens/unlock-promo-plan.jpg` | "Your Promo plan is ready", Unlocked, PROMO, Free for 30 days, Essentials' allowances, "$0/mo", "View cart 1", chip "PROMO30 free for 30 days" (observed) |
| `sandbox/extracted-context/app-extraction/extraction-overview.md` — *Choose Your Unlimited Mobile Plan*, *Line added*, *Vouchers*, *Cart*, *Family discount*, *Goal 3*, *Goal 4* | copy the screenshots cut off: the other three plans, the line-added announcement, CART10 and TRAVEL25 amounts, "Invalid code. Please try again.", the cart on the checklist, **Remove line** from Edit with **Keep it** (observed) |
| `tests/onboard-a-customer/select-plan/select_plan_story.test.md` — *See the plan catalog*, *Load plan catalog* | merged into Display Plans' one scenario, *See the plan catalog*, which also shows the unsold plan left out. Changed from the screens: the catalog lists Atlas first and Essentials last; each plan shows its tagline and features In Bermuda and When you travel, not data / calling / texting lines; each plan can be added as a line, where legacy signed up with one plan; the empty cart's nudge is new; the catalog comes before the account, so the scenario starts from an ++empty cart++ that belongs to no account yet, not a signed-up customer's onboarding cart; the unsold plan is ++plan++ ++Promo++, not ++plan++ ++Internal Test Plan++. Prices changed as the *plan* table notes |
| `tests/onboard-a-customer/select-plan/select_plan_story.test.md` — *Sign up with a plan*, *Select a plan* | carried over as Add Line To Cart's *Add the first line*. Changed from the screens: the plan goes in the cart as Line 1 and the **Customer** stays on the catalog with every plan offering one more line, instead of going straight to Create Account or Pick Number; adding several lines on several plans (*Add one more line*, *Add a line from the order checklist*) is new |
| `tests/onboard-a-customer/select-plan/select_plan_story.test.md` — *Change an existing plan*, *Keep current plan*, *Failed to update plan* | not carried over: the screens add lines rather than replace one plan; changing a set-up line's plan is Change Line Plan; no failure message was shown |
| `tests/onboard-a-customer/place-order/place_order_story.test.md` — *Redeem Voucher and Apply Credit* | carried over: a voucher restricted to some plans gives nothing for a line on another plan (TRAVEL25 counts the Atlas and Ace lines only); *Remove an applied voucher* nearly word for word, with the cart now offering the code field again, still holding the last code. The screen wins on where: the voucher is applied on the catalog and cart, not at payment, and is shown on the first bill. The voucher catalog's failed redemption and the billing account's voucher credit are not carried over: the first product keeps vouchers inside My Paradise |
| `pml-domainmodel/depecrated/v1-system-stories/stories/onboard-a-customer/sign-up-select-plan.e2e.ts` | carried over: the hidden zero-price promo plan is not available on the catalog |
| `src/.context/bounded-context-map.md` — Revenue · Cart, Voucher; Inventory · Plans, Numbers | domain words; removing a line releases the number it held |

### Domain terms

- ++[plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ — what a line pays for each month (Atlas, Ace, Data Freedom, Essentials), all fees included.
- ++[plan feature](../../../../src/.context/domain-model.md#planfeature-value-object)++ — what a plan gives in Bermuda and when you travel.
- ++[plan catalog](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ — the sellable plans as the **Customer** sees them on *Choose Your Unlimited Mobile Plan*: each plan's tagline, features, and monthly price with all fees included, and its tag; it hides the ++Promo plan++ until its voucher unlocks it.
- ++[Promo plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity)++ — the unsellable ++plan++ the catalog hides until PROMO30 unlocks it: free for 30 days, on Essentials' allowances, $0/mo.
- ++[cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ — the onboarding cart: what the **Customer** is buying, its lines and the one applied voucher.
- ++[line](../../../../src/.context/domain-model.md#line-entity)++ — one line in the cart: its place (Line 1, Line 2 …), its plan and monthly price, and, once set up, who it is for, its number, and its SIM.
- ++[number](../../../../src/.context/domain-model.md#numberinventory-aggregate-root-entity)++ — a phone number a line holds; removing the line releases it so it can be offered again.
- ++[family discount](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ — the cart's family discount: $5 per line per month once the cart has 3 or more lines.
- ++[voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++ — a code and what it gives: $10 off every line (ALL10), 10% off the first bill (CART10), $25 off each Atlas or Ace line (TRAVEL25), or unlock the Promo plan (PROMO30); one at a time on a cart.
- ++[applied voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity)++ — the one voucher on the cart, taken off the first bill only, on top of the family discount.
- ++[up-front charge](../../../../src/.context/domain-model.md#cart-aggregate-root-entity)++ — the cart's up-front charge, what the **Customer** pays now: the lines' monthly price less the discounts.

> In steps: ++example++ names a row of a table below; {field} is a column of the scenario's Examples. Values live in the tables only.

## Examples

### plan

| plan | example | name | tagline | price | sellable | tag | in Bermuda | when you travel |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [plan](../../../../src/.context/domain-model.md#plan-aggregate-root-entity) | Atlas | Atlas | Seamless Global Connectivity | 193 | yes |  | Unlimited Data / All high-speed data; Unlimited Local Calling; Included Calls to 190+ countries | 70+ Countries included / Talk, text and data / 30GB high-speed data, then slower |
| plan | Ace | Ace | More of What Matters | 153 | yes | Best value | Unlimited Data / All high-speed data; Unlimited Local Calling; Included Calls to 30+ countries | 5+ Countries included / Talk, text and data / 12GB high-speed data, then slower |
| plan | Data Freedom | Data Freedom | Go Unlimited in Bermuda | 103 | yes |  | Unlimited Data / All high-speed data; Unlimited Local Calling; Included Calls to 10+ countries | No Connectivity Abroad |
| plan | Essentials | Essentials | Kids & Seniors Plan | 73 | yes |  | Unlimited Data / 10GB high-speed data, then slower; Unlimited Local Calling; No Long Distance Calling | No Connectivity Abroad |
| plan | Promo | PROMO | Free for 30 days | 0 | no, until PROMO30 unlocks it | Unlocked | Unlimited Data / 10GB high-speed data, then slower; Unlimited Local Calling; No Long Distance Calling | No Connectivity Abroad |

> Carried over from the Select Plan *plan* table (`tests/onboard-a-customer/select-plan/select_plan_story.test.md`). Changed from the screens: prices (Essentials 73, Data Freedom 103, Ace 153, Atlas 193, were 70 / 55 / 99 / 129); features grouped In Bermuda and When you travel instead of data / calling / texting; a tagline on each plan; the unsold plan is now ++plan++ ++Promo++, unlocked by PROMO30, instead of ++plan++ ++Internal Test Plan++.

### cart

| [cart](../../../../src/.context/domain-model.md#cart-aggregate-root-entity) | lines | monthly price | applied voucher | account |
| --- | --- | --- | --- | --- |
| ++empty cart++ |  |  |  | none |
| ++one Atlas line++ | Line 1 · Atlas $193/mo | $193/mo |  | none |
| ++Atlas and Ace lines++ | Line 1 · Atlas $193/mo; Line 2 · Ace $153/mo | $346/mo |  | none |
| ++family of three++ | Line 1 · Atlas $193/mo; Line 2 · Ace $153/mo; Line 3 · Data Freedom $103/mo | $449/mo, $434/mo after the family discount |  | none |
| ++Atlas with TRAVEL25++ | Line 1 · Atlas $193/mo | $193/mo | ++TRAVEL25++ | none |
| ++lines set up for Me and Sam++ | Line 1 · Me · Data Freedom $103/mo, number +1 (441) 555-0106, eSIM; Line 2 · Sam · Ace $153/mo, number +1 (441) 555-0107, eSIM | $256/mo |  | created |
| ++one line set up for Me++ | Line 1 · Me · Data Freedom $103/mo, number +1 (441) 555-0106, eSIM | $103/mo |  | created |

> The walk (*Goal 4*) did not record Sam's plan and number. Sam's line takes Ace and +1 (441) 555-0107 from the ++Sam · Ace++ example in `tests/story_tests/finish-order/examples/finish_order.examples.md`, so the two files agree; Me's line shows Goal 4's changed plan and number.

### voucher

| voucher | example | code | plans | rule | on ++one Atlas line++ | on ++family of three++ | you pay now on ++family of three++ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [voucher](../../../../src/.context/domain-model.md#appliedvoucher-aggregate-root-entity) | ALL10 | ALL10 |  | $10 off every line | −$10 first bill | −$30 first bill | You pay now $404, then $434/mo |
| voucher | CART10 | CART10 |  | 10% off your first bill | −$19.30 first bill | −$43.40 first bill | You pay now $390.60, then $434/mo |
| voucher | TRAVEL25 | TRAVEL25 | Atlas, Ace | $25 off each Atlas or Ace line | −$25 first bill | −$50 first bill | You pay now $384, then $434/mo |
| voucher | PROMO30 | PROMO30 |  | unlock the Promo plan | free for 30 days |  |  |
| voucher | unknown code | HELLO5 |  |  |  |  |  |

> Carried over from the Place Order *applied voucher* table (`code | plans | amount off`; no plans means any plan). Changed from the screens: the codes are ALL10, CART10, TRAVEL25 and PROMO30 instead of SUMMER25, FIRST10 and WELCOME; the amount is per line, per bill, or per qualifying line, shown against the first bill. Intended, not shown in the prototype: the CART10 "you pay now" on ++family of three++ is $434 less 10% (the walk recorded −$43.40 but not the total), and CART10 on ++one Atlas line++ is 10% of $193 (the walk did not apply CART10 to one line). HELLO5 stands for "any other code"; the prototype refuses every code it does not know.

### family discount

| [lines](../../../../src/.context/domain-model.md#line-entity) | line prices | family discount | monthly price | nudge |
| --- | --- | --- | --- | --- |
| ++no lines++ |  |  |  | Add a line to start. 3 or more lines get a family discount. |
| ++one line++ | Atlas $193 |  | $193/mo | Family discount: save $180 a year with 2 more lines |
| ++two lines++ | Atlas $193, Ace $153 |  | $346/mo | Family discount: save $180 a year with 1 more line |
| ++three lines++ | Atlas ~~$193~~ $188, Ace ~~$153~~ $148, Data Freedom ~~$103~~ $98 | Family discount · $5 × 3 lines −$15/mo | ~~$449~~ $434/mo | Family discount: $180 a year · $240 with a 4th line |

### messages

| message | text |
| --- | --- |
| ++all fees included++ | All fees included |
| ++line added++ | Atlas added as Line 1. 1 line, $193 per month. |
| ++invalid code++ | Invalid code. Please try again. |
| ++remove line question++ | Remove Sam’s line? Everything you set up for this line will be lost. |
| ++promo plan ready++ | Your Promo plan is ready |
| ++family discount saving++ | Family discount: you save $180 a year |
