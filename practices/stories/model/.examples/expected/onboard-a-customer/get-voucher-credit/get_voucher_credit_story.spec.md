---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Get Voucher Credit

POST-ORDER voucher redemption and Mavenir billing credit during order creation. Catalog voucher (Get Sign Up Plan) and apply-to-cart (`Cart.applyVoucher`, Get Applied Voucher) are separate mechanics.

## Domain terms

- ++voucher++ — Promotion code stored on the ++PML customer++ after Apply Voucher; carries code, campaign, discount (`amount_off` or `percent_off`), and optional planIds restricting which ++plan++ qualifies.
- ++voucher redemption++ — Redemption record that Vouchera creates on a POST to `vouchers/{code}/redeem`; carries discountAmount and totalAmount calculated against the submitted orderAmount.
- ++credit adjustment++ — Credit transaction (`transactionType: creditAdjustment`, `transactionSubType: Credit`) posted to the ++Mavenir customer++ billing account in BMD.

## Examples

### voucher

| voucher | example | code | campaign | amount_off | percent_off | planId |
| --- | --- | --- | --- | --- | --- | --- |
| voucher | amount-off voucher | SUMMER25 | SUMMER25 | 25 |  | 100000000014 |
| voucher | percent-off voucher | FIRST10 | FIRST10 |  | 10 | 100000000014 |
| voucher | any-plan voucher | WELCOME | WELCOME |  |  |  |

### voucher redemption

| voucher redemption | example | voucherCode | orderAmount | discountAmount | totalAmount |
| --- | --- | --- | --- | --- | --- |
| voucher redemption | amount redemption | SUMMER25 | 70.00 | 25.00 | 45.00 |
| voucher redemption | percent redemption | FIRST10 | 70.00 | 7.00 | 63.00 |
| voucher redemption | zero redemption | WELCOME | 0.00 | 0.00 | 0.00 |

### credit adjustment

| credit adjustment | example | amount | unit | glCode | reason |
| --- | --- | --- | --- | --- | --- |
| credit adjustment | summer credit | 25 | BMD | 100004 | $SUMMER25 |
| credit adjustment | percent credit | 7 | BMD | 100004 | $FIRST10 |

---

## Story: Redeem Voucher and Apply Credit

**Source**
- Code: `pml-midtier/src/entities/Voucher/controller.ts` `redeemVoucherRequest()` — POST `${voucherConfig.host}/vouchers/${code}/redeem`
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` `createOrder()` cook path · `voucherDiscount()` · `creditRequest()`
- Code: `pml-midtier/src/entities/Mavenir/controllers/customer/payloads/credit.ts`
- Granola: `.context/granola-notes/2026-08-25-onboarding-flow-walkthrough.md` L30–L36
- Granola: `.context/granola-notes/weird-stuff.md` L18 · `19-payment-hpp.png`

**Story type:** My Paradise

++voucher++, ++voucher redemption++, and ++credit adjustment++ examples are on this epic.

### Scenario Outline: Redeem a plan-restricted voucher that matches the cart bundle

*Given* the Customer is in Order Creation with ++voucher++ ++{voucher}++ applied
  *And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
  *And* Vouchera has ++voucher++ ++{voucher}++
  *And* the Customer has a billing account
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++{redemption}++ (voucherCode, redeemerIdentifier, orderAmount `70.00`)
*When* Vouchera records the ++voucher redemption++
*Then* My Paradise stores ++voucher redemption++ ++{redemption}++
*When* the Customer applies the voucher credit
*Then* My Paradise sends the ++credit adjustment++ ++{credit}++ to Mavenir (`transactionType` creditAdjustment, glCode `100004`, unit BMD, channel `@type`)
*When* Mavenir records the ++credit adjustment++ on the billing account
*Then* My Paradise stores the credit on the Customer billing account
  *And* continues to Create Product Order

| voucher | redemption | credit |
| --- | --- | --- |
| amount-off voucher | amount redemption | summer credit |
| percent-off voucher | percent redemption | percent credit |

### Scenario: Redeem an any-plan voucher

*Given* the Customer is in Order Creation with ++voucher++ ++any-plan voucher++ applied
  *And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++ (id `100000000014`, totalPrice `70.00`)
  *And* Vouchera has ++voucher++ ++any-plan voucher++
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera with ++voucher redemption++ ++zero redemption++ (orderAmount `0.00`)
*When* Vouchera records the ++voucher redemption++
*Then* My Paradise stores ++voucher redemption++ ++zero redemption++
  *And* My Paradise skips the apply credit request to Mavenir
  *And* continues to Create Product Order

### Scenario: Skip redeem when the cart bundle is not in the voucher plan list

*Given* the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
  *But* the ++Mavenir shopping cart++ carries ++plan++ ++Ace++ (id `100000000042`) which is not in ++voucher++ ++amount-off voucher++ planIds
*When* the Customer redeems the voucher
*Then* My Paradise skips the redeem request to Vouchera
  *And* My Paradise skips the apply credit request to Mavenir
  *And* continues to Create Product Order

### Scenario: Failed voucher redemption

**Flagged — Vouchera returns error (network or 5xx):** the redeem call returns `{ success: false }`. Credit is skipped, order creation continues. No sandbox evidence for this path.

*Given* the Customer is in Order Creation with ++voucher++ ++amount-off voucher++ applied
  *And* the ++Mavenir shopping cart++ carries ++plan++ ++Essentials++
  *And* Vouchera returns an error for the redeem request
*When* the Customer redeems the voucher
*Then* My Paradise sends the redeem request to Vouchera
*When* Vouchera returns an error
*Then* the voucher redemption is unsuccessful
*When* the Customer applies the voucher credit
*Then* My Paradise skips the apply credit request to Mavenir
  *And* continues to Create Product Order
