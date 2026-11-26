---
fidelity: [discovery]
artifact: [bounded-context-map]
format: md
---

# Bounded Context Map — My Paradise

**Sources / context:** `src/.context/domain-model.md` (the existing model, altered for multiple lines; every aggregate, member, and integration below names what it holds); `tests/.context/story-map.md` (the story map drawn from Leo's multi-line prototype); `sandbox/extracted-context/app-extraction/extraction-overview.md`; the Granola meeting *Domain modeling for credential and customer profile with Nico* (2026-11-17); the previous version of this map and the domain language under `src/{customer,inventory,revenue}/**/.context/domain-language.md`.

My Paradise is the system on this map: the web app a customer uses to buy lines and then look after them. Customer, Inventory, and Revenue are the business areas inside it, each with its own words. The map follows the existing domain model, changed only so that a cart holds several lines.

## Map format

`##` is a bounded context. `###` is an aggregate inside that context. The first line of the aggregate is its root; indented lines under it are the concepts that change with the root.

## Customer

Who the customer is and how they sign in. Onboarding and self-care use the same words here.

### Credentials

Credentials - the email and password the customer signs in with; unverified until the emailed validation code is entered, and asking for a new password when the CRM created it with a temporary password or an administrator forced a reset
  ValidationCode
  PasswordReset
  NewPasswordRequired

### Customer Profile

CustomerProfile - who the customer is; created only once their Credentials are verified, and reached through them; it holds whether the identity is verified and whether an identity ticket is required
  Identity - name, date of birth, ID nationality, ID type, ID number, expiry date, preferred name, alternate contact number
  Address - street, unit, city, parish, postal code; kept apart from Identity because it changes
  Kyc - what Verify ID left: the Persona inquiry and whether it verified the identity with the ID fields locked; a deferred check goes to manual review for up to 48 hours and raises an identity ticket
  SupportTicket - an issue or idea the customer sends from self-care

## Inventory

What can be sold and given to a line: plans, numbers, port-ins, and SIMs.

### Plans

Plan - what a line pays for each month (Atlas, Ace, Data Freedom, Essentials), all fees included; the Promo plan stays in the catalog unsold until PROMO30 unlocks it, free for 30 days
  PlanFeature - what the plan gives in Bermuda and when you travel

### Numbers

NumberInventory - one Bermuda number: available, held while a line is choosing, or reserved for a line; a number one line holds is not offered to another
  NumberInventorySearch - the page of numbers held for a line while it chooses, matched against 3 to 5 letters or digits

### Porting

Portability - a number brought in from another provider (port-in): provider, number, account number, account, account type, and the two confirmations; verified now with the SMS code, or verification skipped for later, when the team contacts the customer; it takes 3 to 5 business days
  InterimNumber - an available number from Numbers the line uses until the port completes

### SIM

Sim - how a line reaches the phone: an eSIM, a Paradise SIM card the customer has (20-digit ICCID), or one to pick up at a Paradise store or an authorized retailer
  IccidInventory - the Paradise SIM card stock an ICCID must be in before it is attached

## Revenue

What the customer buys and owes: the cart of lines they build, the subscriptions those lines become, the vouchers, the order that places the cart, and the billing account that pays for it.

### Cart

Cart - the lines being set up during onboarding, the voucher, and the step reached; it prices the lines together and can be saved and resumed until the order is placed; $5 per line per month family discount once it holds 3 or more lines; the up-front charge is the lines' monthly price less the voucher; it holds everything used while building the order: the numbers each line holds or reserved, the port-in, the SIM choice, the voucher, and whether the billing account is active; kept by its own repository, CartRepository
  Line - one line in the cart: who it is for (required nickname), its plan, the numbers it holds and the one it reserved or its port-in, and its SIM; not a Subscription: when the order is placed it becomes one, which keeps its id
  CartStep - where the customer is: Account, then Lines for each line in turn, Your ID, Payment

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Customer Profile
    crosses: the profile the cart and its lines belong to; a cart whose lines were chosen before the account exists is attached to the profile once the credentials are verified; whether the identity check is done, which moves the cart past Your ID
    integration: after CredentialsValidation.verify, the application runs CustomerProfileRepository.create(credentials) and then Cart.startCart(), which attaches the cart to its customer; CartRepository.load(customerProfile) at each load
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Plans
    crosses: each line's plan, its name and monthly price
    integration: Cart.addLine(plan) adds a line on a plan; Line.choosePlan(plan) changes it and keeps everything else set up for the line
  - → Inventory · Numbers · NumberInventory (by MSISDN)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Numbers
    crosses: the numbers each line holds, then the one it reserves or keeps
    integration: Line.recordHeldNumbers after NumberInventorySearch.search; Line.reserveSelectedNumber after NumberInventorySearch.reserve releases the number it held before; Cart.removeLine releases every number the line held or reserved
  - → Inventory · Porting · Portability (by line id)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Porting
    crosses: the ported number, the interim number, and whether it is verified now or later (Portability.verified, verificationSkipped)
    integration: Line.recordPort(portability) after Portability.beginPort puts the line on the interim number
  - → Inventory · SIM · IccidInventory (by ICCID)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on SIM
    crosses: whether a Paradise SIM card's ICCID is in stock; the line keeps the Sim it chose (eSIM, a Paradise SIM card with its ICCID, or one to pick up)
    integration: Line.selectSim(sim); Line.attachIccid(sim) checks the ICCID against the stock
  - → Revenue · Voucher · AppliedVoucher (by code)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Voucher
    crosses: the voucher on the cart and the discount it gives across the lines
    integration: Cart.applyVoucher(voucher) after AppliedVoucher.redeem(plans)
  - → Revenue · Billing · BillingAccount (by customer id)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Billing
    crosses: whether the customer's billing account is active, which moves the cart from Checkout to Done
    integration: the application reads BillingAccountRepository.load(customerProfile) at each load of the cart and sets Cart.billingAccount
  - → Revenue · Subscription · Subscription (by line id)
    pattern: Customer/Supplier
    direction: downstream — Cart depends on Subscription
    crosses: each line's plan, number (its MSISDN), and SIM, handed over when the order is placed; a Paradise SIM card activated afterwards
    integration: placing the order runs Cart.recordPlaced, which calls SubscriptionRepository.create once per line in that request; Line.activateSim updates the Subscription made from the line
    sync: trigger: the order is placed · source owner: the Cart, until then · receiver: the Subscription, from then on · direct repository calls (.context/grill-answers.md, Cross-aggregate sync)

### Subscription

Subscription - a line in service after the order is placed: its plan, its number (the MSISDN it was given), its SIM, and its usage; what self-care shows and changes; kept by SubscriptionRepository, which holds only Subscriptions
  SubscriptionUsage

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    direction: downstream — Subscription depends on Customer Profile
    crosses: the customer whose lines are in service
    integration: SubscriptionRepository.load(customerProfile)
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    direction: downstream — Subscription depends on Plans
    crosses: the plan a line in service is on, and the plan it changes to
    integration: Subscription.changePlan(plan), refused for a cheaper or same-priced plan within 31 days of the plan order

### Voucher

AppliedVoucher - a code and the terms it carries, one at a time on the cart, redeemed against the plans of every line and taken off the first bill only, on top of the family discount: $10 off every line (ALL10), 10% off the first bill (CART10), $25 off each Atlas or Ace line (TRAVEL25), or unlock the Promo plan (PROMO30)
  VoucherRedemption

Integrations:
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    direction: downstream — Voucher depends on Plans
    crosses: the plans a voucher is limited to (Atlas and Ace for TRAVEL25) and the Promo plan PROMO30 unlocks
    integration: AppliedVoucherRepository.forCode(code, planOf) reads the plans when the code is entered; Cart.applyVoucher adds a line on the Promo plan PROMO30 unlocks

### Product Order

ProductOrder - the placed cart: the up-front payment, the stored order, and the follow-up the team owes the customer
  OrderTicket - ID manual review, port verification later, a Paradise SIM card to deliver or pick up, a promotional trial, a failed payment, a roaming plan

Integrations:
  - → Revenue · Cart · Cart (by customer id)
    pattern: Customer/Supplier
    direction: downstream — Product Order depends on Cart
    crosses: the lines, the up-front charge, the voucher, and the outcome the order records back
    integration: ProductOrderRepository.create(cart); ProductOrder.place → Cart.recordPlaced(outcome, today)
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    direction: downstream — Product Order depends on Customer Profile
    crosses: whether the customer is already done, whether an identity ticket is required, and the name and email its tickets carry
    integration: ProductOrder.place → CustomerProfile.completeCart(done); placing the order opens the ID manual-review ticket when one is required, and the result reads Almost there! until the ID is checked

### Billing

BillingAccount - what the customer owes and how they pay it; opened at the payment step and active once the card is authorized
  Payment - the $1 card authorization, the up-front payment, and later payments
  PaymentMethod - a saved card; one is the default
  Invoice
  CreditAdjustment

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    direction: downstream — Billing depends on Customer Profile
    crosses: the profile the account is opened for
    integration: BillingAccountRepository.create(customerProfile) at the payment step; BillingAccountRepository.load(customerProfile) in self-care; the account takes the cart's up-front charge when the customer pays and subscribes

### Device Wallet

DeviceWalletMerchantCredential - the merchant key and certificate checkout uses so the customer can pay from a device wallet

Device Wallet depends on no other aggregate: checkout reads the one stored credential.

**Systems outside the first product.**

The first product has no live external systems: each one below is kept as stored data inside the context that uses it.

- **Persona** — the ID check behind Kyc; the prototype shows it as a stand-in.
- **Card processor** — the hosted card form behind Payment; the form is preloaded from the order summary and reloaded about every 5 minutes, because the hosted page times out.
- **Voucher catalog** — each code's terms and its redemption, behind AppliedVoucher.
- **Ticketing (Zendesk)** — where OrderTickets and SupportTickets go.
- **CRM and the sign-in service** — the CRM creates customers with a temporary password, and an administrator forces a reset; both set NewPasswordRequired on Credentials.

**Changes from the previous map.**

- **Line** joins the Subscription aggregate: the Cart now holds several Lines, each with a required nickname and its own plan, number or port-in, and SIM; a Line is a type of Subscription, the same subscription in service once the order is placed.
- The **Cart** prices the lines together: the family discount ($5 per line per month from the third line) and the up-front charge are the Cart's.
- **AppliedVoucher** now redeems against the plans of every line in the cart.
- **ProductOrder** is placed from the Cart, and its OrderTickets follow every line.
- **CartStep** runs the plan, port, number, and SIM steps for each line in turn.
- **Cart** is the root of the Subscription aggregate (audit, 2026-11-18): the rules that span the lines hold in the Cart, and each Subscription is reached through it. The aggregate keeps its name, Subscription.
- **Cart** is its own aggregate (board review, 2026-11-18), with its own repository, CartRepository; it composes Line and CartStep and holds everything used while building the order. The **Subscription** aggregate keeps only the line in service and SubscriptionUsage. In the user's words: "You don't need to look up inventory once you've got a subscription; you only need to do that when creating a cart."
- **Line** is no longer a type of Subscription: when the order is placed, the Cart creates a Subscription from each Line (Cart → Subscription).
- The integrations to Numbers, Porting, SIM, Voucher, and Billing move from the Subscription aggregate to the Cart; Product Order now depends on the Cart.
- The contexts are named Customer, Inventory, and Revenue, without the vendor word "custom".
