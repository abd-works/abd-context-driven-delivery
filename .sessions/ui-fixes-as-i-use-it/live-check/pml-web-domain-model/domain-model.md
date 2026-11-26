---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Domain Model — My Paradise

**Sources / context:** the existing model in markdown, which is the primary source for every class, property, and operation and its wording: `src/customer/credentials/.context/class-model.md`, `src/customer/customer-profile/.context/class-model.md`, `src/inventory/{numbers,plans,porting,sim}/.context/class-model.md`, `src/revenue/{billing,payment,product-order,subscription,voucher}/.context/class-model.md`, with each folder's `domain-language.md` and `src/my-paradise/.context/domain-language.md`. The existing diagram, `src/.context/domain-model.previous.drawio`, cross-checks the relationships. The prototype's screens, one per story, in `sandbox/extracted-context/app-extraction/story-screens/*.jpg`, are the only reason anything below differs from that model; each difference is listed, with its screen, in **Changed from the existing model** at the end.

**Extends:** `practices/clean_engineering/templates/class-model.md` — same class notation (`------` properties · `----` operations). Constructors are left out of this view; the per-aggregate class models keep them.

**What changed.** The existing model is altered for one thing: a cart now holds several lines, each on its own plan. The **Cart** keeps its name and its cart-wide work (the step, the voucher, the order outcome, what is paid now); a new **Line**, owned by the Cart, takes over what the Cart held for its one line (the plan, the number or port-in, the SIM) and adds the line's nickname. The Cart prices the lines together with the family discount, and its voucher now applies across the lines. When the order is placed, each Line becomes a **Subscription**, the line in service. Everything else is the existing model unchanged.

**Why the Cart is its own aggregate.** Building an order and running a line in service are two different jobs with different rules, so they are two aggregates in Revenue, each with its own root and its own repository. The Cart holds the rules that span the lines while the order is built: the family discount counts the lines; one voucher applies across them; a number one line holds is never offered to another line; removing a line releases its numbers and renumbers the rest; the step order runs every line in turn before the ID; the billing account must be active before the cart moves past Checkout. Everything used while building the order belongs to the Cart and its Lines: the held and reserved numbers, the port-in, the voucher, the billing account's status, the SIM choice, the family discount, and the up-front charge. A Subscription is a line in service: it needs its plan, its number, its SIM, and its usage, and never needs to look a number up in the inventory, check a port-in, redeem a voucher, or read the billing account. In the user's words: "You don't need to look up inventory once you've got a subscription; you only need to do that when creating a cart." So the Cart is the root of the Cart aggregate, kept by **CartRepository**; the Subscription is the root of the Subscription aggregate, kept by **SubscriptionRepository**; neither repository holds the other or any other repository. When the order is placed, the Cart creates a Subscription from each Line (`Cart.recordPlaced` → `SubscriptionRepository.create`). A Line is not a type of Subscription: a line being built holds numbers it can still release, a port-in in progress, and a step, while a subscription holds a fixed number, usage, and a plan-change lock; inheritance would hand an unplaced line `changePlan` and put the Cart's lines back in the Subscription's repository. The Subscription keeps the Line's id, so the port-in filed under it is still found in self-care.

**Audit, 2026-11-18.** This model was checked against every prototype screen. Only clear shape problems were changed: the root above, fields, relationships, and operations a screen plainly shows and the model lacked, and members a screen plainly contradicts. Every other class, member, and name is the existing model's; each audit change is listed with its screen under **Changed from the existing model**.

**Cross-aggregate sync (all arrows below).** From `.context/grill-answers.md`: the application layer that owns the flow calls each aggregate's repository in turn, one request at a time; each aggregate keeps its own store and never opens another's. So for every arrow the source owner is the target aggregate, the receiving side holds only the target's identity, the trigger is the operation named on the arrow, and the receiving side reads the target fresh at that call, so it is never staler than the request that uses it. The step's own aggregate runs first, then the Cart records it, in one request on the Cart's route. The handover from Cart to Subscription is the same kind of call: placing the order runs `Cart.recordPlaced`, which calls `SubscriptionRepository.create` once per line in that request.

---

## Layout

`##` is a bounded context, `###` an aggregate inside it, `####` a class inside the aggregate. Every aggregate is written in the same order: the root, then the members the root composes. The root's section ends with its repository, a `**{Root}Repository** «Repository»` block with the repository's properties and operations, drawn inside the root's card below its domain operations. The model has no exception classes; an operation's refusal rule is a `// refuses when …` comment on it.

---

## Customer

Who the customer is and how they sign in — credentials, profile, and identity check.

### Credentials

The email and password a customer signs in with, and the session token.

#### Credentials <<Aggregate Root>> <<Entity>>

------
+ email: string
	// identity
+ password: string
+ confirmPassword: string
+ requirements: CredentialRequirements
+ registrationRequirements: RegistrationPasswordRequirements
+ newPasswordRequirements: NewPasswordRequirements
	// Access Selfcare
+ << composition >> token: CredentialsToken | null
+ << composition >> validation: CredentialsValidation
+ << composition >> passwordReset: PasswordReset
	// Access Selfcare
+ resendMessage: string | null
+ isUpdatable: boolean
+ isPersistable: boolean
+ isAuthenticatable: boolean
+ isLoggedIn: boolean
+ newPasswordRequired: boolean
	// Access Selfcare; true while a sign-in with a temporary password waits for a new password
----
+ register(): Credentials
	-> CredentialsRepository.create(this)
	-> CredentialsValidation.emailValidationCode()
+ authenticateCredentials(): Credentials
	-> CredentialsRepository.load(this)
	-> PasswordReset.matches(password)
	// Access Selfcare: a temporary password asks for a new password instead of issuing a token
+ requestTemporaryPassword(): Credentials
	-> CredentialsRepository.prepareTemporaryPassword(this)
	-> CredentialsRepository.load(this)
	-> PasswordReset.send()
	-> CredentialsRepository.update(stored)
+ resendTemporaryPassword(): Credentials
	-> PasswordReset.canResend
	-> requestTemporaryPassword()
	// refused during the resend wait; then "A new password was sent! Please check your email."
+ setNewPassword(): Credentials
	-> missingRequirements()
	-> PasswordReset.clear()
	-> CredentialsRepository.update(this)
	// Access Selfcare; uses password and confirmPassword already entered
+ signOut(): void
	-> CredentialsRepository.update(this)
+ issueSessionToken(): void
+ passwordRequirements(purpose: PasswordPurpose): PasswordRequirements
	// registration or new-password rules
+ missingRequirements(purpose: PasswordPurpose): CredentialRequirement[]
	// registration by default
+ requireRepository(): CredentialsRepository

**Invariants**

- A token is issued only to a verified account with no new password pending.
- A temporary password signs in once: setting the new password clears it.
- A new password meets the same requirements as registering (letters, number, symbol, length, confirmed).
- `signOut` always leaves the account without a token.

**CredentialsRepository** «Repository»

------
+ accounts: Collection<Credentials>
----
+ new(): Credentials
+ create(credentials: Credentials): Credentials
+ load(credentials: Credentials): Credentials | null
+ update(credentials: Credentials): Credentials
+ prepareTemporaryPassword(credentials: Credentials): void
	// Access Selfcare

#### CredentialsValidation <<Entity>>

------
+ validationCode: string
+ verified: boolean
+ validationCodeSentAt: Date | null
+ expectedValidationCode: string | null
+ << composition >> validationCodeMessages: ValidationCodeMessage[]
+ validationCodeWasSent: boolean
+ canActivate: boolean
+ canResend: boolean
+ resendWaitSeconds: number
	// 30 after a resend: "Resend in 30s"
----
+ emailValidationCode(): void
+ verify(validationCode: ValidationCode): CredentialsValidation
	// the application then runs CustomerProfileRepository.create(credentials) and Cart.startCart(customerProfile, cartRepository)
+ resendValidationCode(): void
	// refused during the resend wait
+ copyFrom(stored: CredentialsValidation): void

#### ValidationCodeMessage <<Value Object>>

------
+ sentAt: Date
+ email: string
+ code: string
+ executed: boolean

#### ValidationCode <<Value Object>>

------
+ code: string
+ sentAt: Date

#### PasswordReset <<Entity>>

Access Selfcare.

------
+ << composition >> sent: TemporaryPassword[]
	// the temporary passwords emailed, latest last
+ newPasswordRequired: boolean
+ canResend: boolean
+ resendWaitSeconds: number
	// 30 after a resend: "Resend in 30s"
----
+ send(): TemporaryPassword
	// issues a temporary password and emails it to the account's email
+ matches(password: string): boolean
	// true for the latest unexpired temporary password
+ requireNewPassword(): void
+ clear(): void
+ copyFrom(stored: PasswordReset): void

**Invariants**

- Only the latest temporary password matches.
- After `clear`, nothing matches and no new password is required.

#### TemporaryPassword <<Value Object>>

Access Selfcare.

------
+ email: string
+ password: string
+ sentAt: Date

#### CredentialsToken <<Entity>>

------
+ email: string
+ jwt: string | null

Integrations:
  - → Auth System · Account
    pattern: Anticorruption Layer
    crosses: credentials, validation codes, session tokens, temporary passwords
    integration: CredentialsRepositoryNode (local store stands in for the Auth System)

### Customer Profile

The customer's identity, address, billing link, and recorded identity verification; created only once their credentials are verified, and reached through them.

#### CustomerProfile <<Aggregate Root>> <<Entity>>

------
+ id: string
	// identity
+ << association >> credentials: Credentials
	// held by email — Credentials
+ << composition >> identity: Identity
+ << composition >> address: Address
+ billing: CustomerProfileBilling | null
+ done: boolean
	// onboarding is complete; a completed customer's home is the dashboard
+ << composition >> kyc: Kyc
	// what Verify ID left: the Persona inquiry and whether it verified the identity; set by Confirm ID
+ identityVerified: boolean
	// derived from kyc.verified
+ kycRequired: boolean
	// Verify ID is asked for while the identity has no ID number
+ identityTicketRequired: boolean
+ << composition >> supportTickets: SupportTicket[]
	// Use My Account; the support tickets this customer sent, latest last
----
+ enterProfileDetails(identity: Identity, address: Address): void
	-> CustomerProfileRepository.update(this)
+ saveUpdates(preferredName: string, otherPhoneNumber: string, address: Address): void
	-> Identity.withContactDetails(preferredName, otherPhoneNumber)
	-> Address.missingRequirements()
	-> CustomerProfileRepository.update(this)
	// Access Selfcare; refuses when an update breaks a rule, naming the unmet rule
+ sendSupportRequest(subject: string, message: string): void
	-> SupportTicket.missingRequirements()
	-> CustomerProfileRepository.update(this)
	// Use My Account; a failed store leaves supportTickets as it was
+ confirmIdentity(identity: Identity, address: Address, kyc: Kyc): void
	-> Identity.missingRequirements()
	-> Address.missingRequirements()
	-> CustomerProfileRepository.rejectSharedIdNumber(this, identity)
	-> CustomerProfileRepository.update(this)
	// Get Verified Profile; refused with the unmet rule, or "Customer already exists."; while kyc.verified the ID fields Persona read stay as read
+ deferIdentityVerification(): void
	// the identity stays unverified and an identity ticket is raised
+ completeCart(done: boolean | null): void

**Invariants**

- `saveUpdates` never changes given name, last name, date of birth, or email.
- `saveUpdates` refuses an address with a missing street, parish, or postal code, and a preferred name that is not one word; nothing is stored when it refuses.
- `sendSupportRequest` refuses a missing subject or message, and a ticket the profile store cannot keep; no ticket is recorded when it refuses.
- `confirmIdentity` refuses a missing given name, last name, date of birth, ID nationality, ID type, ID number, expiry date, street, parish, or postal code, and an ID number another customer holds; nothing is stored when it refuses.
- While `kyc.verified`, `confirmIdentity` keeps the names, date of birth, ID nationality, ID type, ID number, and expiry date Persona read: they are locked; only the alternate contact number, the preferred name, and the address change.

**CustomerProfileRepository** «Repository»

------
+ customerProfiles: Collection<CustomerProfile>
----
+ create(credentials: Credentials): CustomerProfile
+ load(credentials: Credentials): CustomerProfile | null
+ loadById(customerProfileId: string, credentials?: Credentials): CustomerProfile | null
+ update(customerProfile: CustomerProfile): void

#### Identity <<Value Object>>

------
+ email: string
	// read-only in self-care
+ name: string
+ lastName: string
+ fullName: string
+ dateOfBirth: string
+ expiryDate: string
	// the ID document Persona read, as the customer confirmed it
+ idNationality: string
+ idNumber: string
+ idType: string
+ idTypesOffered: string[]
	// by idNationality: Bermuda — Driver's License, Passport, Voter ID; UK — Driver's License, Passport; Canada — adds Identification Card, Permanent Residence Card; US — adds Identification Card, Municipal ID, Permanent Residence Card; none until a nationality is chosen ("Choose a nationality first")
+ preferredName: string
+ otherPhoneNumber: string
	// the alternate contact number
+ preferredNameIsSingleWord: boolean
	// Access Selfcare
----
+ digitsOf(phoneNumber: string): string
+ withContactDetails(preferredName: string, otherPhoneNumber: string): Identity
	// Access Selfcare; the same identity with only these two changed
+ missingRequirements(): IdentityRequirement[]
	// Get Verified Profile; given name, last name, date of birth, ID nationality, ID type (one of idTypesOffered), ID number, and expiry date are required

#### Address <<Value Object>>

------
+ street: string
+ complement: string
+ city: string
+ parish: string
+ postalCode: string
+ country: string
----
+ missingRequirements(): AddressRequirement[]
	// Access Selfcare, Get Verified Profile; street, parish, and postal code are required

#### Kyc <<Value Object>>

Get Verified Profile.

------
+ personaInquiryId: string | null
	// the Persona inquiry Verify ID ran
+ verified: boolean
	// Persona verified the ID and the customer did not edit it

#### PersonaInquiry <<Value Object>>

Get Verified Profile; Persona's answer on Verify ID, never stored.

------
+ inquiryId: string | null
+ verified: boolean
+ << composition >> identity: Identity
+ << composition >> address: Address
----
+ fromCompletion(completion: PersonaCompletion): PersonaInquiry
	// Persona's onComplete fields mapped to the identity and address
+ failed(): PersonaInquiry
	// Persona's onError: nothing read

#### SupportTicket <<Entity>>

Use My Account.

------
+ subject: string
	// Found an issue, Had a great idea, Other
+ message: string
	// up to 512 characters
+ sentAt: Date
+ requirements: { subject: "Please select an option.", message: "Please enter a message." }
----
+ missingRequirements(): SupportTicketRequirement[]
+ toJSON(): SupportTicketJson

Integrations:
  - → Customer · Credentials · Credentials (by email)
    pattern: Customer/Supplier
    crosses: the verified credentials a profile is created for and reached through
    integration: CustomerProfileRepository.create(credentials) after CredentialsValidation.verify; CustomerProfileRepository.load(credentials) on sign-in
    sync: Credentials owns the account · on verifying the email and at each sign-in · never staler than that request
  - → CRM · Feedback
    pattern: Customer/Supplier
    crosses: a support ticket — subject and message (Use My Account · Send Support Request)
    integration: intended — external systems stay out of the first product; the support ticket is stored with the customer profile

---

## Inventory

What can be sold and assigned to a line: plans, numbers, port-ins, and SIMs.

### Plans

What a line pays for each month; each sellable entry in the catalog.

#### Plan <<Aggregate Root>> <<Entity>>

------
+ id: string
	// identity
+ name: string
	// Atlas, Ace, Data Freedom, Essentials; Promo, which only PROMO30 unlocks
+ tagline: string
	// Seamless Global Connectivity, More of What Matters, Go Unlimited in Bermuda, Kids & Seniors Plan; Promo: Free for 30 days
+ price: number
+ tag: string | null
	// the label its catalog card shows
+ isSellable: boolean
	// the catalog offers it; the Promo plan is not sellable
+ << composition >> features: PlanFeature[]
	// View Services lists them under My plan
+ oneYear: boolean
	// Change My Service; a one-year promotional plan, on which a port request asks for a paid plan first
+ roaming: boolean
	// ordering it opens a roaming ticket

**PlanRepository** «Repository»

------
+ plans: Collection<Plan>
	// the catalog
----
+ list(): Plan[]
	// the sellable plans
+ load(id: string): Plan | null
	// any plan in the collection; an unsellable plan (Promo) is never listed, but loads when its voucher unlocks it

#### PlanFeature <<Value Object>>

------
+ region: inBermuda | whenYouTravel
	// the card's two groups, IN BERMUDA and WHEN YOU TRAVEL
+ lines: string[]
	// the lines its catalog card shows: "Unlimited Data / All high-speed data", "70+ Countries included / Talk, text and data / 30GB high-speed data, then slower"

### Numbers

One Bermuda number: available, held while a line is choosing, or reserved for a line.

#### NumberInventory <<Aggregate Root>> <<Entity>>

------
+ msisdn: string
	// identity
+ imsi: string
+ status: available | held | reserved
+ interimPort: boolean
	// reserved as the interim number for a port-in
+ isAvailable: boolean
+ isHeld: boolean
+ isReserved: boolean
----
+ hold(): void
	// refuses when the number is not available
+ reserve(reserveDetails: NumberReserveOptions): void
	// refuses when the number is not held; an interim-port reserve holds an available number first
+ display(msisdn: string): string
	// the number as the screens show it
+ reserved(msisdn: string): NumberInventory
	// a reserved number the pool does not list (an active line's number)
+ releaseHold(): void
+ makeAvailable(): void

**Invariants**

- A number keeps only its own status: it does not know who holds or reserved it. Whoever holds or reserves a number keeps the number — the Line keeps its `number` and its `heldNumbers`.
- Only an available number can be held, and only a held number can be reserved, so a number another line holds or reserved is never offered or reserved again.

**NumberInventoryRepository** «Repository»

------
+ inventory: Collection<NumberInventory>
----
+ load(msisdn: string): NumberInventory | undefined
+ list(): NumberInventory[]
+ update(entry: NumberInventory): void
+ nextAvailable(count: number): NumberInventory[]
	// the pool's next available numbers after the ones it offered last, wrapping round

#### NumberInventorySearch <<Entity>>

------
+ listedInventory: NumberInventory[]
	// the numbers the latest search or listing shows
+ heldInventory: NumberInventory[]
	// the listed numbers this search holds; the line keeps them
+ selected: string | null
+ searchHint: string | null
+ failureMessage: string | null
+ emptyMessage: string | null
+ msisdns: string[]
----
+ search(searchCriteria: NumberInventorySearchOptions, heldNumbers: NumberInventory[], reservedNumber: NumberInventory | null): void
	-> NumberInventory.releaseHold()
	-> NumberInventory.hold()
	-> NumberInventoryRepository.update(entry)
	// releases the numbers the line held, then holds the available matches; the line's reserved number leads the default listing
+ select(msisdn: string): void
+ reserve(msisdn: string, heldNumbers: NumberInventory[]): NumberInventory
	-> NumberInventory.reserve(reserveDetails)
	-> NumberInventoryRepository.update(entry)
	// refuses when the line does not hold the number
+ releaseHeld(heldNumbers: NumberInventory[]): void
	// the line's held numbers go back to the pool; a number since reserved stays reserved
+ applyListed(fields: NumberInventoryFields): void
+ fromFields(body: NumberInventoryFields): NumberInventorySearch

**Invariants**

- The search does not depend on the Cart: the line hands in what it holds (`heldNumbers`) and its `reservedNumber`, and keeps `heldInventory`. It releases only the numbers it is handed, and reserves only one of them.

#### TermNumberSearch <<Value Object>>

------
+ input: string
+ converted: string
	// letters turned into dial-pad digits
----
+ clean(rawText: string): string
+ hintLabel(): string | null
+ toDialable(): string

### Porting

A number brought in from another provider onto a line, on an interim number until the port completes.

#### Portability <<Aggregate Root>> <<Entity>>

------
+ donorOperator: string
+ portNumber: string
+ accountNumber: string
+ userType: string
+ accountType: string
+ device: string
+ informationConfirmed: boolean
	// "I confirm that this information is accurate."
+ permissionGranted: boolean
	// "I grant permission to Paradise Mobile to bring the phone number in this form to the Paradise Mobile network."
+ << association >> interimNumber: NumberInventory | null
	// held by MSISDN — the number reserved while the port completes
+ verified: boolean
+ verificationSkipped: boolean
	// No, verify it later: no code is sent, the team contacts the customer
+ donorNumberConfirmed: boolean
	// Yes, text me the code
+ enteredCode: string
+ verificationMessage: string | null
+ refusedCode: string | null
+ resendNotice: string | null
+ codeSentTo: string | null
+ canResend: boolean
+ resendWaitSeconds: number
+ smsWasSent: boolean
+ smsSendCount: number
+ portNumberShown: string
+ enteredCodeMessage: string | null
+ canEnterCode: boolean
+ canVerifyCode: boolean
+ canResendCode: boolean
+ fieldMessages: PortabilityFieldMessages
----
+ validate(): string | null
	// the first unmet field message: provider, a full Bermuda number, user type (Account), account type, both confirmations
+ submit(heldNumbers: NumberInventory[]): NumberInventory | null
	-> NumberInventory.hold()
	-> NumberInventory.reserve(interimPort)
	-> PortabilityRepository.update(this)
	// reserves an interim number — an available one, or one the line's listing holds — and stores the port-in
+ beginPort(heldNumbers: NumberInventory[]): void
	-> submit(heldNumbers)
	// Continue on the port form; then "Is this phone with you?" asks before any code is sent
+ sendVerification(): PortabilityStatus
+ confirmDonorNumber(): void
	-> sendVerification()
	// Yes, text me the code
+ deferVerification(): void
	-> PortabilityRepository.update(this)
	// No, verify it later: sets verificationSkipped; no code is sent
+ enterCode(code: string): void
+ canVerify(code: string): boolean
+ verify(code: string): void
	// a matching six-digit code verifies the port; a wrong one is refused with its message
+ resendVerificationSms(): void
	// after the resend wait
+ persistUpdate(): void

**Invariants**

- A port-in is not submitted until `validate` passes.
- A port-in does not know the line it ports onto: the Line holds its `portability` and records it (`recordPort`). Its interim number is reserved with no holder; the Line takes it as its `number`.
- Self-care's port request runs `validate()`, then `Subscription.requestLinePortability`, and is filed under the subscription's id; it sends no SMS check.

**PortabilityRepository** «Repository»

------
+ portabilities: Collection<Portability>
----
+ create(subscriptionId: string, donorOperator: string, portNumber: string, accountNumber: string, userType: string, accountType: string, device: string): Portability
	// stored under the line's id, which the line's Subscription keeps; self-care's port request under the subscription's id
+ load(subscriptionId: string): Portability | null
	// the latest port-in stored under that line or subscription id
+ update(portability: Portability): void

Integrations:
  - → Inventory · Numbers · NumberInventory (by MSISDN)
    pattern: Customer/Supplier
    crosses: the interim number the line uses until the port completes
    integration: Portability.submit → NumberInventory.hold, NumberInventory.reserve(interimPort)
    sync: Numbers owns the number's status · at Continue on the port form · never staler than that request

### SIM

How a line reaches the phone: an eSIM, or a physical Paradise SIM card with its ICCID.

The SIM aggregate has no root class: the line keeps its `Sim` value, and the stock is only the ICCIDs in it. So **IccidInventoryRepository** stays its own section here, with no root card to fold into.

#### IccidInventoryRepository <<Repository>>

------
+ << aggregation >> availableIccids: Collection<string>
	// the physical SIM stock
----
+ validate(iccid: string): void
	// refuses when the ICCID is not in stock ("Invalid ICCID.")

#### Sim <<Value Object>>

------
+ simType: eSIM | pSIM | null
+ iccid: string | null
+ ready: boolean
	// an eSIM, or a Paradise SIM card whose ICCID is known
+ awaitsParadiseSimCard: boolean
	// a Paradise SIM card with no ICCID yet
+ iccidEntered: boolean
	// more than the Paradise ICCID prefix
+ iccidFormatValid: boolean

---

## Revenue

What the customer buys and owes: the cart they build their lines in, the subscriptions those lines become, and their billing, payments, vouchers, and orders.

### Cart

The lines the customer is setting up during onboarding, with everything the order needs while it is built: the numbers each line holds or reserved, the port-in, the SIM, the voucher, the family discount, and the up-front charge. The cart ends when the order is placed; each of its lines then becomes a Subscription.

#### Cart <<Aggregate Root>> <<Entity>>

The customer's lines while they are still getting them: the lines, the voucher, and the step, carried through the step screens until the order is placed. It knows which step comes next. The root of the Cart aggregate and the only way in: every Line and CartStep is reached through it.

------
+ id: string
	// identity; the cart exists before the account does
+ << association >> customerProfile: CustomerProfile | null
	// held by id — Customer Profile; none while lines are chosen before the account exists
+ << composition >> lines: Line[]
	// Line 1, Line 2, …; each on its own plan
+ << composition >> cartStep: CartStep
	// the step the cart has reached; Checkout until the customer's billing account is active, then Done
+ canReopenNumberStep: boolean
	// the step reopens the number step (CartStep.reopensNumberStep)
+ << association >> appliedVoucher: AppliedVoucher | null
	// held by code — Voucher; one at a time, across all the lines
+ << association >> billingAccount: BillingAccount | null
	// held by customer id — Billing; read fresh at each load of the cart with BillingAccountRepository.load(customerProfile); its `active` moves the cart from Checkout to Done
+ fullPrice: number
	// the lines' plan prices before any discount: "$449" struck through
+ discountPerLine: number
	// dollars off each paying line every month once the family discount applies; $5 unless the cart is given another amount (the prototype's `lineDiscount`)
+ payingLineCount: number
	// every line but the Promo line
+ familyDiscountPerLine: number
	// `discountPerLine` once 3 lines or more pay; 0 below that
+ familyDiscount: number
	// each paying line's share, every month: "Family discount · $5 × 3 lines −$15/mo"
+ familyDiscountPerLineIfAdded: number
	// what each line would save with one more paying line: "$5 off this line too"
+ familyDiscountWith(lineCount: number): number
	// what the family discount saves every month with that many lines: "$20 with a 4th line"
+ nextFamilyDiscountLineCount: number
	// the next line count, up to 5, that saves more than now: "Add a 3rd line"; 0 when none does
+ monthlyCharge: number
	// the lines' monthly prices after the family discount, e.g. $404/mo
+ monthlySaving: number
	// the full price less the monthly charge: "you save $180 a year" is 12 × this
+ canAddLine: boolean
	// fewer than `MAX_LINES` (5) lines; more go through support
+ voucherKind: plan | cart | trial | unlock | later | null
	// the voucher's kind; a trial voucher with no Promo line yet only unlocks the Promo plan
+ voucherDiscount: number
	// what the voucher takes off the first bill: its amount off each eligible line (at most the line's monthly price), or its percent of the monthly charge, to the cent
+ voucherLines: number
	// how many lines the voucher takes something off
+ firstBill: number
	// the monthly charge less the voucher, never below 0: "You pay now $374"
+ discountsLabel: string
	// what You pay now says comes off: "Discounts −$45" together, "Family discount −$15/mo" alone, "TRAVEL25 −$25" for a voucher alone
+ upFrontCharge: string
	// the first bill as pml-my writes it ('374.00', or '0' when nothing)
+ voucherDescription: string
	// what the voucher gives; for a trial voucher with no Promo line, that it unlocks the plan
+ voucherNote: string
	// the line under the applied code: what it gives, or, while it takes nothing off, what to add ("Add one to use it.")
+ voucherNotUsedYet: boolean
	// the voucher waits (shown grey): it takes nothing off only because no line meets its plan condition yet
+ trialHeld: boolean
	// the Promo voucher is applied and its Promo line is in the cart
+ voucherCredit: number | null
+ chargesUpFront: boolean
+ orderSuccess: boolean | null
+ payUpFront: boolean | null
	// the placed order's outcome
+ submitOrder: boolean
+ defaultPayment: boolean
+ returnToReview: boolean
+ stayingOnPlanSelection: boolean
	// the cart returns to review, or stays on plan selection
+ orderResult: allSet | almostThere
+ orderResultHeadline: string
	// "You're all set!" or "Almost there!"
+ orderNeedsParadiseSim: boolean
	// a verified customer's Paradise SIM card has no ICCID yet, on any line
+ orderPaymentFailed: boolean
	// no default card was kept, or the up-front charge did not go through
----
+ startCart(customerProfile: CustomerProfile, cartRepository: CartRepository): void — the visitor's cart belongs to the verified customer and is stored as theirs
+ orderChecklist: { title, done, about }[] — each line, then Verify your ID
+ progressSteps: { title, done }[] — the progress bar: Account, Your line or Lines, Your ID, Payment
+ orderReviewTitle: string — Your order, Finish your order, or Your order is ready
	// the cart is attached to the customer once the account is activated
+ carryChosenPlan(plan: Plan): void
	-> addLine(plan)
	// a plan carried in from a marketing link
+ addLine(plan: Plan): Line
	-> PlanRepository.load(id)
	-> CartRepository.update(this)
	// Add Line To Cart: the new line is Line n on that plan
	// TO DO: adding a line creates a new Subscription that takes its details from the plan, in an onboarding (in progress) status; the status it moves to when the order is placed is not named yet
+ removeLine(line: Line): void
	-> NumberInventorySearch.releaseHeld(heldNumbers)
	-> NumberInventory.makeAvailable() (the line's number)
	-> CartRepository.update(this)
	// Remove Line From Cart; the remaining lines are numbered again
+ applyVoucher(voucher: AppliedVoucher): void
	-> AppliedVoucher.redeem(plans)
	-> addLine(plan) for a trial voucher limited to a plan the catalog does not sell (PROMO30 unlocks Promo)
	// after AppliedVoucher.redeem, against the plans of every line
+ removeVoucher(): void
+ saveAndExit(): void
	-> CartRepository.update(this)
	// Save And Exit Order: "Your progress is saved."; the cart is resumed by CartRepository.load(customerProfile)
+ orderSummary(): { position, nickname, planName, planPrice, discountedPrice, msisdn, temporaryNumber, portNumber, portPending, simType, setUp }[] and idNumber, identity verified or in manual review, and the customer's full name
	// what the cart, the order review, and Done show, one entry per line
+ whatsNext(): { group: checkingId | installEsims | putSimIn | pickUpSim | portingNumber, lines: Line[] }[]
	// while the ID is not verified the whole order waits: checkingId is all there is
+ voucherEmptiesCart(voucher: AppliedVoucher): boolean
	// PROMO30 asks first before it empties a cart that holds other plans
+ endTrialVoucher(): void
+ temporaryNumberFor(line: Line): string
	// the first number from 555-0199 down that no other line uses
+ numbersInUse(except: Line | null): string[]
+ lineHoldingNumber(msisdn: string, except: Line | null): Line | null
+ portNumberProblem(msisdn: string, line: Line | null): string | null
	// "This number is already on Line N."
	// the order result grouped by line: "Install your eSIMs — Mom and Alice", "Pick up your SIM — Me", "Porting your number — Mom"
+ recordPlaced(outcome, today: Date): void
	-> SubscriptionRepository.create(customerProfile, line.id, line.plan, line.number.msisdn, line.sim, today) for each line, on a successful order
	-> CartRepository.update(this)
	// copies the placed order's outcome; on a successful order each line becomes a Subscription, ordered today

**Invariants**

- A refused step names its operation (reserveNumber, port, choosePlan, selectSim, attachIccid, activateSim) and, when it was for one line, that line.
- The step's own aggregate runs first, then the Cart records it on the Line, in one request on the Cart's route.
- The cart's next step is always the first one it has not met, in order: a verified account, then for each line in turn a plan, a verified port-in (when porting), a number, and a SIM, then the identity check, then checkout. Going back to review from a changed plan returns to Checkout.
- The family discount applies from the third paying line: `discountPerLine` ($5) off each paying line every month. The Promo line pays nothing and takes no discount.
- A cart holds at most 5 lines; a 6th is refused (`addLine`).
- A Promo line exists only with its trial voucher (PROMO30), on its own: applying PROMO30 empties the cart first, and removing or replacing the voucher, or moving the line to a paid plan, ends the trial.
- The cart holds one voucher at a time; its discount comes off the first bill only, on top of the family discount.
- Removing a line releases every number it held or reserved.
- A placed cart is not changed again, except that Done's Activate SIM Card still activates a line's Paradise SIM card.
- Each line becomes exactly one Subscription, once, when the order is placed successfully; a failed order creates none.

**CartRepository** «Repository»

------
+ carts: Collection<Cart>
	// one Cart per customer during onboarding
----
+ create(customerProfile: CustomerProfile | null): Cart
	// an empty cart; null while a visitor chooses lines before the account exists
+ load(customerProfile: CustomerProfile): Cart | null
	// the cart and its lines, each holding its plan id, its numbers' MSISDNs, and the voucher code; the application loads each of those from its own repository
+ update(cart: Cart): void

#### Line <<Entity>>

One line the customer is setting up in the cart: who it is for, its plan, the numbers it holds and the one it reserved or the port-in, and its SIM. A Line is not a Subscription. When the order is placed, the Cart creates a Subscription from it (`Cart.recordPlaced` → `SubscriptionRepository.create`), and the Subscription keeps the line's id, so the port-in filed under that id is the subscription's port-in in self-care.

------
+ id: string
	// identity; the porting store keeps the line's port-in under it, and the line's Subscription keeps it
+ position: number
	// "LINE 1 OF 3"; the remaining lines are numbered again when one is removed
+ nickname: string
	// Who is this line for? e.g. Me, Mom, Alice
+ bringsOwnNumber: boolean | null
	// Bring your mobile number, or Get a new number; required ("Choose an option to continue.")
+ << association >> plan: Plan | null
	// held by id — Plans; the plan the line is on
+ << association >> number: NumberInventory | null
	// held by MSISDN — Numbers; the reserved, kept, or interim port number
+ << association >> heldNumbers: NumberInventory[]
	// held by MSISDN — Numbers; the page of numbers this line holds while the customer browses
+ << association >> portability: Portability | null
	// held by line id — Porting; the port-in onto this line
+ << composition >> sim: Sim | null
	// the SIM the line will run on: modality and, for a Paradise SIM card, its ICCID
+ canKeepCurrentNumber: boolean
+ setUp: boolean
	// a number or port-in, and a SIM; no name needed
+ planPrice: number
+ familyDiscount: number
	// this line's share; the Promo line takes none
+ monthlyPrice: number
	// the plan less its share, never below 0
+ voucherDiscount: number
	// what the cart's voucher takes off this line's first bill
+ nicknameProblem(nickname: string): string | null
	// "Please provide a name.", or "Another line is already called Mom. Use a different name."
+ rename(nickname: string): void
	// Change name: only the name changes, on the same rules
	// a nickname, a number or port-in, and a SIM: the checklist shows "Me · Atlas (done)"
----
+ nameLine(nickname: string, bringsOwnNumber: boolean): void
	// "Who is this line for?", with the number choice on the same screen
+ choosePlan(plan: Plan): void
	// Change Line Plan; everything set up for the line stays
+ keepCurrentPlan(): void
+ recordHeldNumbers(numbers: NumberInventory[]): void
	-> CartRepository.update(cart)
	// after the number step's NumberInventorySearch.search; the line keeps the numbers the listing holds
+ reserveSelectedNumber(number: NumberInventory): void
	-> preparePersist(reserveNumber)
	-> NumberInventory.makeAvailable() (the previous number)
	-> NumberInventorySearch.releaseHeld(heldNumbers)
	-> CartRepository.update(cart)
	// refuses a number that is not reserved or was not in heldNumbers
+ keepCurrentNumber(): void
	// releases heldNumbers
+ recordPort(portability: Portability): void
	// after Portability.beginPort(heldNumbers); the line takes its interim number and releases heldNumbers
+ selectSim(sim: Sim): void
	// an eSIM, or "I need a Paradise SIM card." (a pSIM with no ICCID, to pick up)
+ attachIccid(sim: Sim): void
	-> IccidInventoryRepository.validate(iccid)
+ activateSim(sim: Sim): void
	-> CartRepository.update(cart)
	-> SubscriptionRepository.update(subscription) (the Subscription made from this line, by the line's id)
	// Done's Activate SIM Card, while the line waits for its Paradise SIM card; its Subscription takes the SIM and stops waiting

**Invariants**

- The line takes only a reserved number that was in its `heldNumbers`. It releases its listing when it takes a number, keeps its current number, or ports in, and releases its previous number when it takes another. A number another line holds is never in this line's listing, because a search lists only available numbers.

#### CartStep <<Value Object>>

Where the customer is in onboarding. The node gives it the web path that shows it. Stored and sent as its name.

------
+ name: VerifyAccount | SelectPlan | PickNumber | VerifyPortedNumber | SelectSim | ProfileKyc | Checkout | Done
	// the progress bar groups them: Account (VerifyAccount), Lines (SelectPlan to SelectSim), Your ID (ProfileKyc), Payment (Checkout)
+ << association >> line: Line | null
	// the line a SelectPlan, PickNumber, VerifyPortedNumber, or SelectSim step sets up: "LINE 1 OF 3 · ME · ATLAS"
+ path: string
	// set by the node
+ reopensNumberStep: boolean
	// Select Sim's Back and Change reopen the number step
----
+ at(path: string): CartStep
	// this step shown at path
+ is(step: CartStep): boolean

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: the profile the cart and its lines belong to; a cart whose lines were chosen before the account exists is attached once the credentials are verified
    integration: Cart.startCart(customerProfile, cartRepository) after CredentialsValidation.verify; CartRepository.load(customerProfile)
    sync: Customer Profile owns the customer · on verifying the email and at each load · never staler than that request
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    crosses: each line's plan, its name and monthly price
    integration: Cart.addLine(plan), Cart.carryChosenPlan(plan), Line.choosePlan(plan) → PlanRepository.load(id)
    sync: Plans owns the plan · read on adding a line or changing its plan · never staler than that request
  - → Inventory · Numbers · NumberInventory (by MSISDN)
    pattern: Customer/Supplier
    crosses: the numbers each line holds, then the one it reserves or keeps
    integration: Line.recordHeldNumbers after NumberInventorySearch.search; Line.reserveSelectedNumber after NumberInventorySearch.reserve; Cart.removeLine → NumberInventorySearch.releaseHeld, NumberInventory.makeAvailable; the application loads each line's numbers with NumberInventoryRepository.load(msisdn) after CartRepository.load
    sync: Numbers owns the number's status · at each pick, removal, or load of the cart · never staler than that request
  - → Inventory · Porting · Portability (by line id)
    pattern: Customer/Supplier
    crosses: the ported number, the interim number, and whether it is verified now or later
    integration: Line.recordPort after Portability.beginPort(heldNumbers); the application loads each line's port-in with PortabilityRepository.load(line id) after CartRepository.load
    sync: Porting owns the port-in · at Continue on the port form, and at each load of the cart · never staler than that request
  - → Inventory · SIM · IccidInventoryRepository (by ICCID)
    pattern: Customer/Supplier
    crosses: whether a Paradise SIM card's ICCID is in stock
    integration: Line.attachIccid(sim) → IccidInventoryRepository.validate(iccid)
    sync: the SIM stock owns the ICCIDs · at the attach · the line keeps the Sim value it chose
  - → Revenue · Voucher · AppliedVoucher (by code)
    pattern: Customer/Supplier
    crosses: the voucher on the cart and the discount it gives across the lines
    integration: Cart.applyVoucher(voucher) after AppliedVoucher.redeem(plans); the application loads the cart's voucher with AppliedVoucherRepository.load(code) after CartRepository.load
    sync: Voucher owns the redemption · at Apply, and at each load of the cart · never staler than that request
  - → Revenue · Billing · BillingAccount (by customer id)
    pattern: Customer/Supplier
    crosses: whether the customer's billing account is active, which moves the cart from Checkout to Done
    integration: Cart.billingAccount ← BillingAccountRepository.load(customerProfile), which the application reads after CartRepository.load
    sync: Billing owns the account status · at each load of the cart · never staler than that request
  - → Revenue · Subscription · Subscription (by line id)
    pattern: Customer/Supplier
    crosses: each line's plan, number (its MSISDN), and SIM, handed over when the order is placed; the Paradise SIM card activated afterwards
    integration: Cart.recordPlaced → SubscriptionRepository.create(customerProfile, line.id, line.plan, line.number.msisdn, line.sim, today), one per line; Line.activateSim → SubscriptionRepository.update(subscription)
    sync: trigger: the order is placed (ProductOrder.place → Cart.recordPlaced), by direct repository calls in that request · source owner: the Cart, which owns each line until then · receiver: the Subscription, which owns the line in service from then on · the Cart is not changed again, so the Subscription is never staler than the placed cart

### Subscription

A line in service after the order is placed: its plan, its number, its SIM, its usage, and what self-care does with it.

#### Subscription <<Aggregate Root>> <<Entity>>

One line in service. Created from a Line of the Cart when the order is placed, and from then on found, shown, and changed on its own.

**TO DO:** create the Subscription when the line is added to the cart, not when the order is placed. It takes its details from the Plan and starts in an onboarding (in progress) status; the name of the status it reaches when the order is placed is not decided yet.

------
+ id: string
	// identity; the id of the Line it was created from, so the port-in filed under that id stays the line's
+ << association >> customerProfile: CustomerProfile
	// held by id — Customer Profile; one subscription per line
+ number: string
	// the MSISDN the line was given when the order was placed; a value, with no inventory lookup
+ << composition >> sim: Sim | null
	// the SIM the line runs on: modality and, for a Paradise SIM card, its ICCID
+ waitingForPsim: boolean
	// the order was placed for a Paradise SIM card without an ICCID
+ << composition >> usage: SubscriptionUsage | null
	// Use My Account; null until the network reports usage
+ << association >> plan: Plan | null
	// held by id — Plans; My plan shows its name and features
+ hasActiveLine: boolean
	// Use My Account; the subscription holds a plan
+ planOrderedOn: string | null
	// Change My Service; the Bermuda day the active plan was ordered, at sign-up (SubscriptionRepository.create when the order is placed) or by changePlan
----
+ firstBillDueOn(today: Date): Date
+ nextDowngradeDate(today: Date): string | null
	// Change My Service; within 31 days of the plan order, the day a downgrade opens
+ canChangePlanTo(plan: Plan, today: Date): boolean
	// Change My Service; not the current plan, and not a lower-priced plan while locked
+ changePlan(plan: Plan, agreedToServiceAgreement: boolean, today: Date): void
	-> preparePersist(changePlan)
	-> SubscriptionRepository.update(this)
	// refuses without the Service Agreement or when canChangePlanTo is false
+ requestLinePortability(agreedToTerms: boolean): void
	// Change My Service; refuses on a promotional plan or without the porting terms; the port request itself is a Portability the application validates first and files under this subscription's id only after this passes
+ copyFieldsFrom(source: Subscription): void
+ restore(subscription: Subscription, row: SubscriptionJson): Subscription
+ toJSON(): SubscriptionJson

**Invariants**

- `changePlan` is for an active line (`hasActiveLine`).
- For 31 Bermuda days after `planOrderedOn`, a lower-priced or same-priced plan is refused; only a higher-priced plan is allowed.
- A port request on a one-year promotional plan (`Plan.oneYear`) is refused until the line is on a paid plan; nothing is stored when a request is refused or the store fails.
- A customer with no stored subscription, or one without a plan, has no active lines; the dashboard shows the no-active-lines message.

**SubscriptionRepository** «Repository»

------
+ subscriptions: Collection<Subscription>
	// one per line in service
----
+ create(customerProfile: CustomerProfile, id: string, plan: Plan, number: string, sim: Sim | null, planOrderedOn: Date): Subscription
	// a line in service, made from a Line when the order is placed
+ load(customerProfile: CustomerProfile): Subscription[]
	// the customer's lines in service; none before an order is placed
+ update(subscription: Subscription): void
+ prepareUpdate(): void

#### SubscriptionUsage <<Value Object>>

Use My Account.

------
+ << composition >> local: DataAllowance
+ << composition >> roaming: DataAllowance | null
	// present only on a plan with roaming

#### DataAllowance <<Value Object>>

Use My Account.

------
+ used: number
	// GB of High Speed Data used
+ quota: number | unlimited | unknown
+ hasLimit: boolean
	// the quota is a number, so the dashboard draws a progress bar

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: the customer whose lines are in service
    integration: SubscriptionRepository.load(customerProfile)
    sync: Customer Profile owns the customer · at each load · never staler than that request
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    crosses: the plan a line in service is on, and the plan it changes to
    integration: Subscription.changePlan(plan) → PlanRepository.load(id)
    sync: Plans owns the plan · read at each load and on changing the plan · never staler than that request

### Voucher

A promo code redeemed against the cart's lines.

#### AppliedVoucher <<Aggregate Root>> <<Entity>>

------
+ code: string
	// identity: ALL10, CART10, TRAVEL25, PROMO30
+ plans: VoucherPlan[]
	// the plans it is limited to; empty for any plan (TRAVEL25: Atlas and Ace; PROMO30: Promo)
+ amountOff: number | null
	// per qualifying line: ALL10 $10, TRAVEL25 $25
+ trial: boolean
	// a promotional trial; the line pays nothing up front (PROMO30, free for 30 days)
+ << composition >> redemption: VoucherRedemption | null
+ quotedPrice: number
	// the lines' price the redemption quoted
+ percentOff: number
	// CART10: 10% of the first bill after the family discount
+ redeemFailed: boolean
	// "Invalid code. Please try again."
+ orderAmount: string
----
+ redeem(plans: VoucherPlan[]): void
	-> catalog.redeem(code)
	-> AppliedVoucherRepository.update(this)
	// against the plans of every line in the cart; only lines on its plans qualify, and a voucher none of them qualifies for does nothing
+ credit(): { amount, glCode, remarks } | null
	// what the billing account is credited; null when the redemption failed or gives nothing off

**Invariants**

- The discount comes off the first bill only: ALL10 takes `amountOff` from every line, TRAVEL25 from each line on one of its plans, CART10 takes `percentOff` of the first bill after the family discount.

**AppliedVoucherRepository** «Repository»

------
----
+ create(code: string, plans: VoucherPlan[], amountOff: number | null, trial: boolean): AppliedVoucher
+ forCode(code: string, planOf: (planId: string) => VoucherPlan | null): AppliedVoucher
	// the voucher a customer entered: the stored one, or a new one on the catalog's terms
+ load(code: string): AppliedVoucher | null
+ update(voucher: AppliedVoucher): AppliedVoucher

#### VoucherRedemption <<Value Object>>

------
+ success: boolean
+ discountAmount: number
+ totalAmount: number

Integrations:
  - → Voucher catalog (CatalogVoucherRepository)
    pattern: Anticorruption Layer
    crosses: each code's terms and its redemption
    integration: AppliedVoucher.redeem → catalog.redeem(code); an in-repo stand-in for the external voucher system
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    crosses: the plans a voucher is limited to, and the Promo plan PROMO30 unlocks
    integration: AppliedVoucherRepository.forCode(code, planOf)
    sync: Plans owns the plan · read when the code is entered · never staler than that request

### Product Order

The placed cart: the up-front payment, the stored order, and the follow-up tickets.

#### ProductOrder <<Aggregate Root>> <<Entity>>

------
+ id: string
	// identity
+ << association >> cart: Cart
	// the Cart that created the order
+ << association >> customerProfile: CustomerProfile
	// the cart's profile
+ placed: boolean
+ orderSuccess: boolean
+ submitOrder: boolean
+ payUpFront: boolean | null
+ profileDone: boolean | null
+ defaultPayment: boolean
+ ticketSubjects: OrderTicketSubject[]
	// the follow-ups this order needs, across all its lines
----
+ place(billingAccount: BillingAccount | null): void
	-> BillingAccount.takePayment(cart.upFrontCharge).received
	-> ProductOrderRepository.acceptsOrder()
	-> ProductOrderRepository.update(this)
	-> ProductOrderRepository.createTicket(customerProfile, subject)
	-> Cart.recordPlaced(outcome, today)
	-> CustomerProfile.completeCart(done)
	// Pay And Subscribe; refuses when the profile is already done

**Invariants**

- A completed customer (`customerProfile.done`) never places a second order.
- Ticket subjects follow the cart's lines and its profile: identity and SIM delivery (combined when both), trial, unverified port, failed up-front payment, roaming.

**ProductOrderRepository** «Repository»

------
----
+ create(cart: Cart): ProductOrder
	// a new order for that cart, not stored until it is placed
+ load(cart: Cart): ProductOrder | null
+ update(order: ProductOrder): ProductOrder
	// keeps a placed order; an order not placed takes no id
+ acceptsOrder(): boolean
+ createTicket(customerProfile: CustomerProfile, subject: OrderTicketSubject): OrderTicket
	// also the card-addition ticket the payment status check opens
+ loadTickets(customerProfile: CustomerProfile): OrderTicket[]

#### OrderTicket <<Entity>>

------
+ id: string
+ << association >> customerProfile: CustomerProfile
+ subject: OrderTicketSubject
	// ID Verification Required, SIM Delivery Required, both, Promotional trial, Portability Required, Card addition failed, Payment failed, Roaming plan - New Subscription
+ requesterName: string
+ requesterEmail: string

Integrations:
  - → Revenue · Cart · Cart (by customer id)
    pattern: Customer/Supplier
    crosses: the lines, the up-front charge, the voucher, and the outcome the order records back
    integration: ProductOrderRepository.create(cart); ProductOrder.place → Cart.recordPlaced(outcome, today)
    sync: Cart owns the cart · at Pay and subscribe · never staler than that request
  - → Revenue · Billing · BillingAccount (by customer id)
    pattern: Customer/Supplier
    crosses: the up-front payment, received or declined
    integration: ProductOrder.place → BillingAccount.takePayment(cart.upFrontCharge)
    sync: Billing owns the payment · at Pay and subscribe · never staler than that request
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: whether the customer is already done, the name and email its tickets carry
    integration: ProductOrder.place → CustomerProfile.completeCart(done)
    sync: Customer Profile owns the customer · at Pay and subscribe · never staler than that request
  - → CRM / ticketing
    pattern: Customer/Supplier
    crosses: the order's follow-up tickets
    integration: intended — OrderTickets are stored with their owner instead of Zendesk

### Billing

What the customer owes and how they pay it; opened at the payment step and active once the card is authorized.

#### BillingAccount <<Aggregate Root>> <<Entity>>

------
+ id: string
	// identity
+ << association >> customerProfile: CustomerProfile
	// held by id — Customer Profile; the customer the account bills
+ status: opened | active
	// opened when the payment step starts; active once the card verified and the account was set up
+ active: boolean
	// onboarding's Checkout is done, the order can be charged, the voucher credit applies, and self-care can read the account
+ << composition >> creditAdjustments: CreditAdjustment[]
+ balance: number
	// Use My Account; what the account owes, negative when in credit
+ << composition >> invoices: Invoice[]
	// Pay My Bill; latest first
+ << composition >> payments: Payment[]
	// the account's payments, latest last: the $1 card authorizations and the payments it took
+ cardAuthorization: Payment | null
	// the latest $1 card authorization
+ receivedPayments: Payment[]
	// the payments with status received; what Past payments lists
+ << composition >> paymentMethods: PaymentMethod[]
	// Pay My Bill; the saved cards
+ defaultPaymentMethod: PaymentMethod | null
	// Pay My Bill; the saved card Pay now charges
+ hasBalanceDue: boolean
	// Pay My Bill; something is owed, so Pay now is offered
----
+ canRemoveSavedCard(paymentMethod: PaymentMethod): boolean
	// Pay My Bill; any saved card but the default
+ applyCredit(credit: CreditAdjustment | null): BillingAccount
+ activate(): void
	-> BillingAccountRepository.update(this)
	// after the card verified; refuses an active account as already existing
+ enterCardAuthorization(maxAttempts: number): Payment
	-> Payment.enter()
	-> BillingAccountRepository.update(this)
	// the $1 check: the account's card authorization asks for the card page
+ checkCardAuthorization(): Payment
	-> Payment.checkStatus()
	-> BillingAccountRepository.update(this)
	// reads whether the card verified; a decline under the attempt limit refuses after a fresh card page
+ takePayment(amount: number, today: Date): Payment
	-> Payment.received(amount, today) | Payment.declined(amount)
	// the order up front, or the balance from Pay now
+ payNow(): void
	-> takePayment(balance)
	-> BillingAccountRepository.update(this)
	// Pay My Bill; takes a payment of the balance from the default card and records it
+ enterNewPaymentMethod(paymentMethod: PaymentMethod): void
	-> PaymentMethod.requireTerms()
	-> PaymentMethod.save(id, transactionId)
	-> BillingAccountRepository.update(this)
	// Pay My Bill; the first saved becomes the default
+ chooseDefaultCard(paymentMethod: PaymentMethod): void
	-> BillingAccountRepository.update(this)
+ removeSavedCard(paymentMethod: PaymentMethod): void
	-> BillingAccountRepository.update(this)
	// Pay My Bill; never the default card
+ openInvoice(invoiceId: string): Invoice
	// Pay My Bill

**Invariants**

- `payNow` refuses when nothing is owed, when there is no default card, and when the payment is declined; a declined payment leaves the balance and the payments as they were.
- `takePayment` alone records nothing: the order up front is not one of the account's payments.
- An account is active only after `activate`; the payment step's account stays opened until the card verified, and an opened account is not charged for the order, takes no voucher credit, and keeps onboarding at Checkout.
- `enterNewPaymentMethod` refuses a payment method without the authorization terms and one whose authorization did not complete; nothing is saved when it refuses.
- Exactly one saved card is the default while any card is saved; the first card saved becomes it, and the default card cannot be removed.

**BillingAccountRepository** «Repository»

------
----
+ create(customerProfile: CustomerProfile): BillingAccount
	// opens the account at the payment step; refuses a second one
+ load(customerProfile: CustomerProfile): BillingAccount | null
+ update(billing: BillingAccount): BillingAccount
+ activationFailure(): Error | null
+ chargeAccepted(): boolean
+ invoiceAvailable(): boolean

#### Payment <<Entity>>

Money a billing account moves on a card: the $1 authorization that verifies a new card, or a payment the account takes, which ends received or declined.

------
+ maxAttempts: number
	// how many declines get a fresh card page
+ << composition >> authorization: CardAuthorization | null
+ << composition >> lastStatus: PaymentStatus | null
+ paymentAttempts: number
+ cardAdditionExhausted: boolean
	// the attempts ran out; the order side opens a card-addition ticket
+ received: boolean
+ receivedOn: string | null
+ amount: number | null
+ transactionId: string | null
+ orderIdentifier: string
+ salesChannel: SalesChannel
+ authorizesCard: boolean
	// a $1 card authorization rather than money the account took
----
+ received(amount: number, receivedOn: string): Payment
+ declined(amount: number): Payment
+ enter(): void
	// asks the card processor for an authorization; refuses when none comes back
+ checkStatus(): void
	// refuses when the card is unverified under the attempt limit, after a fresh authorization

**Invariants**

- A status is checked only for an authorization this payment entered.
- Past `maxAttempts`, a declined card stops asking again and is marked `cardAdditionExhausted`.
- A payment a billing account takes is received or declined when it is taken; only a received one is recorded on the account.

#### CardAuthorization <<Value Object>>

------
+ transactionIdentifier: string
+ totalAmount: number
+ orderIdentifier: string
+ salesChannel: SalesChannel
+ hostedPage: string

#### PaymentStatus <<Value Object>>

------
+ status: PaymentResult
+ reason: string
+ completed: boolean

#### PaymentMethod <<Entity>>

------
+ id: string
	// identity once saved
+ cardNumber: string
	// what the customer typed; a saved card no longer has it
+ agreedToTerms: boolean
+ brand: string
	// Visa for a number starting 4, Mastercard for one starting 5
+ lastFourDigits: string
+ status: string
+ transactionId: string
	// the $1 authorization that verified it
+ requirements: { terms: the $1 authorization terms }
----
+ entered(cardNumber: string, agreedToTerms: boolean): PaymentMethod
+ missingRequirements(): PaymentMethodRequirement[]
+ requireTerms(): void
+ save(id: string, transactionId: string): void
	// keeps the brand and last four, drops the number

#### Invoice <<Value Object>>

Pay My Bill.

------
+ invoiceId: string
+ dueDate: string
+ dueAmount: number
+ status: PAID | PARTIALLY_PAID | UNPAID

#### CreditAdjustment <<Value Object>>

------
+ amount: number
+ glCode: string
+ remarks: string

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: the profile the account is opened for
    integration: BillingAccountRepository.create(customerProfile) at the payment step; BillingAccountRepository.load(customerProfile) in self-care
    sync: Customer Profile owns the customer · at the payment step · never staler than that request
  - → Card processor
    pattern: Anticorruption Layer
    crosses: the $1 authorization, its hosted card page, and its status
    integration: Payment.enter, Payment.checkStatus — an in-repo stand-in for FAC, not part of the model

### Device Wallet

The merchant key and certificate checkout uses so the customer can pay from a device wallet.

#### DeviceWalletMerchantCredential <<Aggregate Root>> <<Entity>>

------
+ keyIdentifier: string
+ certificate: string

**DeviceWalletMerchantCredentialRepository** «Repository»

------
+ credential: DeviceWalletMerchantCredential | null
	// the one stored credential
----
+ load(): DeviceWalletMerchantCredential | null

---

## Changed from the existing model

One line per change, with the screen that forces it (`sandbox/extracted-context/app-extraction/story-screens/`).

- **Line** «Entity» is added, a type of Subscription owned by the Cart, with `nickname` and `nameLine(nickname)` — `add-line-to-cart.jpg`, `view-cart.jpg` (Line 1 Atlas, Line 2 Ace), `name-line.jpg` ("Who is this line for?").
- **Cart** is no longer a type of Subscription; the generalisation moves to Line — `view-cart.jpg`, `check-order.jpg` (one cart, several lines, each on its own plan, number, and SIM).
- `Cart.lines`, `Cart.addLine(plan)`, `Cart.removeLine(line)` are added — `add-line-to-cart.jpg`, `remove-line-from-cart.jpg`.
- `Cart.heldNumbers` and `Cart.canKeepCurrentNumber` move to Line — `pick-number.jpg` ("LINE 1 OF 3 · ME · ATLAS" lists numbers for that line).
- `Cart.choosePlan`, `keepCurrentPlan`, `recordHeldNumbers`, `reserveSelectedNumber`, `keepCurrentNumber`, `recordPort`, `selectSim`, `attachIccid`, `activateSim` move to Line under the same names — `change-line-plan.jpg` ("Choose a plan for Line 1 Me"), `pick-number.jpg`, `select-sim.jpg`, `enter-porting-number.jpg`, `activate-sim.jpg`.
- `Subscription.appliedVoucher`, `upFrontCharge`, `voucherDiscount`, `orderSuccess`, `payUpFront`, `submitOrder`, `defaultPayment`, `returnToReview`, `stayingOnPlanSelection` move to Cart, because they belong to the whole cart, not one line — `apply-voucher.jpg` ("$10 off every line"), `enter-payment.jpg` (one "You pay now $364" for all lines), `return-to-order-review.jpg`, `view-cart.jpg`.
- `Cart.customerProfile` is added, and is null until the account exists (it was inherited from Subscription) — `create-customer.jpg` ("Finish your order" lists the lines chosen before the account).
- `Cart.familyDiscount` and `Cart.monthlyCharge` are added — `apply-family-discount.jpg` ("Family discount · $5 × 3 lines −$15/mo", "$434/mo"), `view-cart.jpg` ("save $180 a year with 1 more line").
- `Cart.upFrontCharge` now means the lines' monthly charge less the voucher, not one plan's price — `apply-family-discount.jpg` ("You pay now $404, then $434/mo").
- `Cart.orderSummary()` answers one entry per line, with its nickname — `check-order.jpg` ("Me · Atlas", "Mom · Ace", "Alice · Data Freedom").
- `Cart.carryChosenPlan(plan)` now adds a line on that plan — `display-plans.jpg` ("Add a line to start").
- `Cart.applyVoucher` adds a line on the voucher's unsellable plan for a trial voucher — `unlock-promo-plan.jpg` ("Your Promo plan is ready", PROMO30 free for 30 days).
- `Cart.recordPlaced` sets `planOrderedOn` on every line — `view-order-result.jpg` ("Here's what's next for your lines").
- `CartStep.line` is added: the line a per-line step sets up — `name-line.jpg`, `select-sim.jpg` ("LINE 1 OF 3").
- The cart's step order runs the plan, port, number, and SIM steps for each line in turn — `create-customer.jpg` ("Line 1 · Atlas … Choose a number and a SIM", then "Verify your ID").
- `AppliedVoucher.redeem(plan)` becomes `redeem(plans)`: the voucher is redeemed against every line's plan — `apply-voucher.jpg`, `check-order.jpg` ("ALL10 −$30 first bill" on three lines).
- `AppliedVoucher.quotedPrice` now quotes the lines' price, not one plan's — `apply-family-discount.jpg`.
- `ProductOrder.subscription` becomes `cart: Cart`, and `ProductOrderRepository.create(subscription)` / `load(subscription)` become `create(cart)` / `load(cart)`, because the order is made from the cart, which is no longer a Subscription — `pay-and-subscribe.jpg`.
- `ProductOrder.place` reads `cart.upFrontCharge` and records the outcome back with `Cart.recordPlaced` — `pay-and-subscribe.jpg`, `view-order-result.jpg`.
- `SubscriptionRepository.subscriptions` is one per line, not one per customer profile, and `update` takes a Subscription or a Cart — `view-order-result.jpg` (several lines placed at once).

**Audit, 2026-11-18.**

Only clear shape problems are changed: a single-line shape that has to hold several lines, a field, relationship, or operation a screen plainly shows and the model lacked, and a member a screen plainly contradicts. No class, member, exception, or name is removed or renamed; every exception class is kept as it was, and one exception gains a case.

- **Cart** becomes «Aggregate Root» and **Subscription** becomes «Entity», reached through the Cart, for the reason under *Why the Cart is the root* — `view-cart.jpg`, `apply-family-discount.jpg`, `remove-line-from-cart.jpg` (rules that span every line). `Cart.id` is added, the Cart's own identity now that it is no longer a Subscription — `display-plans.jpg` (an empty cart before any account). The SubscriptionRepository keeps its name; its collection is described as one Cart per customer.
- `Plan.tagline` is added — `display-plans.jpg`, `unlock-promo-plan.jpg` ("Seamless Global Connectivity", "Free for 30 days").
- `PlanFeature.kind: data | calling | texting` becomes `region: inBermuda | whenYouTravel`: the catalog card groups its features IN BERMUDA and WHEN YOU TRAVEL — `display-plans.jpg`, `change-line-plan.jpg`.
- `PlanRepository.load` now loads an unsellable plan too, which `Cart.applyVoucher` needs for the Promo line — `unlock-promo-plan.jpg`.
- `Cart.fullPrice` is added, and the family-discount nudge (`linesToFamilyDiscount`, `familyDiscountYearly`, since replaced by `nextFamilyDiscountLineCount`, `familyDiscountWith`, `monthlySaving` to match the multi-line prototype; see `ux/prototype/multi-line/.context/prototype-rules.md`) — `view-cart.jpg` ("save $180 a year with 1 more line"), `apply-family-discount.jpg` ("$449" struck through, "$240 with a 4th line"), `enter-payment.jpg` ("$409" struck through).
- `Cart.saveAndExit()` is added — `save-and-exit-order.jpg` ("Your progress is saved.").
- `Cart.whatsNext()` is added: the result grouped by line — `view-order-result.jpg`.
- `Cart.orderSummary()` entries add `position`, `discountedPrice`, `temporaryNumber`, `portPending`, `setUp`, and the identity check with the customer's full name — `check-order.jpg` ("Temporary number", "We'll contact you to verify it", "ID Verified", "Jordan Smith"), `apply-family-discount.jpg` ($193 → $188).
- `Line.position`, `bringsOwnNumber`, and `setUp` are added, and `nameLine(nickname)` becomes `nameLine(nickname, bringsOwnNumber)` — `name-line.jpg` ("LINE 1 OF 3", Bring your mobile number / Get a new number), `check-order.jpg` (each line done).
- `Line.selectSim` now also records "I need a Paradise SIM card." (a pSIM to pick up) — `request-paradise-sim-card.jpg`.
- `SubscriptionException.line` is added, a new exception case: a refused step can name the one line it was for — `pick-number.jpg`, `select-sim.jpg` (each step is for one line of several).
- `Portability.informationConfirmed` and `permissionGranted` are added, and `validate` asks for both — `request-line-portability.jpg` (the two confirmations, which the onboarding form's screenshot cuts off; the extraction overview lists them on the onboarding form).
- `Portability.beginPort` no longer sends the code; `confirmDonorNumber()` sends it, and `deferVerification()` is added — `defer-port-verification.jpg` ("Is this phone with you?" — Yes, text me the code / No, verify it later).
- `Identity.idTypesOffered` is added, and `missingRequirements` asks for given name, date of birth, and expiry date — `enter-id-details-manually.jpg`, extraction overview *Confirm your details* (each field's message, ID types by nationality).
- `CustomerProfile.confirmIdentity` keeps the ID fields Persona read while the KYC is verified (comment and invariant) — `record-kyc-inquiry.jpg` (ID fields locked), `confirm-details.jpg` (address and preferred name editable).
- `CredentialsValidation.canResend` and `resendWaitSeconds` are added — `resend-validation-code.jpg` ("Resend in 30s").

**Board review, 2026-11-18.**

The user, on the board: "we only needed that when cart was the same aggregate as subscription. You don't need to look up inventory once you've got a subscription; you only need to do that when creating a cart. You're not following the pattern properly around Domain-driven Design: if you're going to create a new aggregate root it needs a new repository, and if you're going to pull out Cart you need to pull it out properly. Why would Subscription need Number inventory? Makes no sense. Cart would, because you're building a new thing and you need to hold on to numbers. Same with portabilities, applied vouchers: these are all part of the cart and not the subscription. Same with billing account."

The Cart becomes its own aggregate in Revenue, and the Subscription keeps only the line in service. No class or business operation is renamed or dropped; every move is listed here.

- **Cart** is now the «Aggregate Root» «Entity» of a new **Cart** aggregate, composing **Line** and **CartStep**; it is no longer the root of the Subscription aggregate.
- **CartRepository** «Repository» is added: `create(customerProfile)`, `load(customerProfile)`, `update(cart)`, one Cart per customer during onboarding. `Cart` and `Line` operations that wrote through `SubscriptionRepository.update` now write through `CartRepository.update`; `Cart.saveAndExit` resumes through `CartRepository.load`.
- **Subscription** becomes the «Aggregate Root» «Entity» of the Subscription aggregate: a line in service, created when the order is placed and from then on loaded and changed on its own.
- **Line** is no longer a type of Subscription. It creates a Subscription when the order is placed (`Cart.recordPlaced` → `SubscriptionRepository.create(customerProfile, line.id, line.plan, line.number.msisdn, line.sim, today)`, one per line); the Subscription keeps the line's id. A line being built and a line in service have different rules, and inheritance would give an unplaced line `changePlan` and put the Cart's lines back in the Subscription's repository.
- `Line.id`, `plan`, `number`, `portability`, and `sim`, which Line inherited from Subscription, are now declared on Line. `number` (as a `NumberInventory`) and `portability` move off Subscription onto Line, held by MSISDN and by line id.
- `Cart.billingAccount` is added, held by customer id: the billing account's status the cart reads at each load, which `SubscriptionRepository.billingAccounts` used to supply.
- `Cart.recordPlaced` now creates the Subscriptions and sets `planOrderedOn` through `SubscriptionRepository.create`, instead of setting it on every line.
- `Line.activateSim` now also updates the Subscription made from the line, which takes the SIM and stops waiting for its Paradise SIM card.
- `Subscription.number` is now the MSISDN as a value (`string`), not a `NumberInventory` looked up in the inventory.
- `Subscription.portability` is removed from Subscription: the onboarding port-in is the Line's, and self-care's port request is a Portability filed under the subscription's id. `Subscription.requestLinePortability(portability, agreedToTerms)` becomes `requestLinePortability(agreedToTerms)`; the application runs `Portability.validate()` first, so the Subscription no longer calls the Porting aggregate.
- `Subscription.restore(subscription, row, numberOf)` becomes `restore(subscription, row)`: a subscription's number is stored as its MSISDN, with nothing to look up.
- `Line.choosePlan` and `Subscription.changePlan` no longer share the plan core `putOnPlan`, because Line is no longer a Subscription.
- **CartException** «Value Object» is added for the Cart aggregate, because every aggregate in this model that refuses an operation has its own exception (Credentials, Customer Profile, Numbers, Porting, SIM, Product Order, Billing, Payment). The cart steps (reserveNumber, port, choosePlan, selectSim, attachIccid, activateSim) and `line` move from `SubscriptionException` to `CartException`; `SubscriptionException` keeps `subscription` and the self-care operations (changePlan, requestLinePortability).
- `SubscriptionRepository.billingAccounts: BillingAccountRepository` and `SubscriptionRepository.numberInventory: NumberInventoryRepository` are removed. A repository holding another repository was a modelling mistake carried in from the old code through the class models; the original domain model (`.sessions/main/model-history/domain-model.previous.drawio`) never had it. The application loads each aggregate from its own repository, as `.context/grill-answers.md` *Cross-aggregate sync* decides.
- The per-aggregate class models drop the same mistake from the repository constructors: `SubscriptionRepository(billingAccounts, portabilities, appliedVouchers, numberInventory)` and `PortabilityRepository(numberInventory)` take no other repository.
- `SubscriptionRepository.create(customerProfile)` / `load(customerProfile): Cart` become `create(customerProfile, id, plan, number, sim, planOrderedOn): Subscription` and `load(customerProfile): Subscription[]`, and `update` takes only a Subscription. Its collection is one Subscription per line in service.
- The integrations to Numbers, Porting, SIM, Voucher, and Billing move from the Subscription aggregate to the Cart aggregate. A Cart → Subscription integration is added for placing the order. The Subscription keeps its integrations to Customer Profile and Plans.
- `ProductOrder`'s integration now points at **Revenue · Cart · Cart**.
- The contexts are named Customer, Inventory, and Revenue, without the vendor word "custom".

**Board review, 2026-11-18 (2).**

The user, on the board (domain-model version 4): the repositories create a lot of noise, so each repository's operations and properties go into its root aggregate; a repository's association to another repository is removed, because it already shows in the operations and properties and needs no line; and all exceptions are removed, because "they just make noise".

- Each `#### {Root}Repository <<Repository>>` section folds into its root's section as a closing `**{Root}Repository** «Repository»` block, below the root's domain operations and invariants: CredentialsRepository into Credentials, CustomerProfileRepository into CustomerProfile, PlanRepository into Plan, NumberInventoryRepository into NumberInventory, PortabilityRepository into Portability, CartRepository into Cart, SubscriptionRepository into Subscription, AppliedVoucherRepository into AppliedVoucher, ProductOrderRepository into ProductOrder, BillingAccountRepository into BillingAccount, DeviceWalletMerchantCredentialRepository into DeviceWalletMerchantCredential.
- The repositories' collection properties lose their `<< aggregation >>` line to the root they keep, because the repository is now drawn inside that root's card. No repository holds another repository, so no property is dropped.
- **IccidInventoryRepository** stays its own section: the SIM aggregate has no root class to fold it into.
- The exception classes are removed, with every relationship to them: CredentialsException, CustomerProfileException, NumberInventoryException, PortabilityException, IccidInventoryException, CartException, SubscriptionException, ProductOrderException, PaymentException, BillingException. The rules they named stay as `// refuses when …` comments on the operations (`NumberInventory.hold`, `reserve`, `NumberInventorySearch.reserve`, `IccidInventoryRepository.validate`, `CustomerProfile.saveUpdates`, `ProductOrder.place`, `Payment.enter`, `checkStatus`) and in the invariants; `Portability.validate` returns the first unmet field message (`string | null`); the Cart's refused-step invariant names the operation and the line without an exception class.
- The Coverage table no longer lists the exception classes.

---

## Coverage

Each prototype screen, and the model elements that support it. The onboarding screens read the Cart aggregate; the self-care screens (pml-my), which are off the story map, read the Subscription aggregate.

| Screen | Model elements |
| --- | --- |
| `display-plans.jpg` | PlanRepository.list; Plan.name, tagline, price, tag, features; PlanFeature.region, lines; Cart.nextFamilyDiscountLineCount, familyDiscountWith |
| `add-line-to-cart.jpg` | Cart.addLine; Line.position; Cart.monthlyCharge, nextFamilyDiscountLineCount, familyDiscountWith |
| `view-cart.jpg` | Cart.lines, orderSummary, monthlyCharge, voucherDiscount, upFrontCharge, firstBill, nextFamilyDiscountLineCount |
| `remove-line-from-cart.jpg` | Cart.removeLine; NumberInventorySearch.releaseHeld; NumberInventory.makeAvailable; Line.position |
| `apply-family-discount.jpg` | Cart.familyDiscount, monthlySaving, fullPrice, monthlyCharge, upFrontCharge; orderSummary discountedPrice |
| `apply-voucher.jpg` | Cart.applyVoucher, removeVoucher, appliedVoucher, voucherDiscount; AppliedVoucher.code, plans, amountOff, percentOff, redeem, redeemFailed |
| `unlock-promo-plan.jpg` | Cart.applyVoucher → addLine; AppliedVoucher.trial; Plan.isSellable, tag, tagline; PlanRepository.load |
| `create-credentials.jpg` | Credentials.email, password, confirmPassword, registrationRequirements, register |
| `enter-validation-code.jpg` | CredentialsValidation.validationCode, verify, canActivate; ValidationCodeMessage |
| `resend-validation-code.jpg` | CredentialsValidation.resendValidationCode, canResend, resendWaitSeconds |
| `create-customer.jpg` | CustomerProfileRepository.create; CartRepository.create; Cart.startCart, cartStep; CartStep.name, line; Line.setUp |
| `name-line.jpg` | Line.nameLine, nickname, bringsOwnNumber, position; CartStep.line |
| `pick-number.jpg` | NumberInventorySearch.search, select, reserve; TermNumberSearch; NumberInventoryRepository.nextAvailable; Line.recordHeldNumbers, reserveSelectedNumber, heldNumbers, number |
| `enter-porting-number.jpg` | Portability.donorOperator, portNumber, accountNumber, userType, accountType, informationConfirmed, permissionGranted, validate, beginPort, submit; Line.recordPort, portability |
| `defer-port-verification.jpg` | Portability.confirmDonorNumber, deferVerification, verificationSkipped |
| `verify-ported-number.jpg` | Portability.codeSentTo, enterCode, canVerify, verify, refusedCode, resendVerificationSms, canResend, resendWaitSeconds |
| `select-sim.jpg` | Line.selectSim, sim; Sim.simType |
| `enter-existing-sim.jpg` | Line.attachIccid; Sim.iccid, iccidEntered, iccidFormatValid; IccidInventoryRepository.validate |
| `request-paradise-sim-card.jpg` | Line.selectSim; Sim.awaitsParadiseSimCard |
| `activate-sim.jpg` | Line.activateSim; SubscriptionRepository.update; Subscription.waitingForPsim, sim, firstBillDueOn |
| `verify-id-with-persona.jpg` | CustomerProfile.kycRequired; PersonaInquiry.fromCompletion, failed |
| `record-kyc-inquiry.jpg` | CustomerProfile.confirmIdentity (locked fields), kyc, identityVerified; Kyc.personaInquiryId, verified |
| `enter-id-details-manually.jpg` | CustomerProfile.deferIdentityVerification, identityTicketRequired; Identity.idTypesOffered, missingRequirements |
| `confirm-details.jpg` | CustomerProfile.confirmIdentity; Identity.preferredName, otherPhoneNumber; Address.street, complement, city, parish, postalCode |
| `check-order.jpg` | Cart.orderSummary, fullPrice, monthlyCharge, monthlySaving, appliedVoucher, cartStep; Line.setUp; CustomerProfile.identityVerified, identityTicketRequired; Identity.fullName |
| `change-line-plan.jpg` | Line.choosePlan, keepCurrentPlan, plan; PlanRepository.list |
| `return-to-order-review.jpg` | Cart.returnToReview, orderSummary, monthlyCharge; Line.nameLine, reserveSelectedNumber, keepCurrentNumber, selectSim; Cart.removeLine |
| `save-and-exit-order.jpg` | Cart.saveAndExit; CartRepository.update, load |
| `reload-card-form.jpg` | BillingAccountRepository.create; BillingAccount.enterCardAuthorization; Payment.enter; CardAuthorization.hostedPage |
| `enter-payment.jpg` | Cart.fullPrice, upFrontCharge, familyDiscount, voucherDiscount, monthlyCharge; CardAuthorization.totalAmount |
| `authorize-card.jpg` | BillingAccount.checkCardAuthorization; Payment.checkStatus, paymentAttempts, maxAttempts, cardAdditionExhausted; PaymentStatus |
| `create-billing-account.jpg` | BillingAccount.activate, status, active; Cart.billingAccount, cartStep |
| `pay-and-subscribe.jpg` | ProductOrder.place; BillingAccount.takePayment; Cart.recordPlaced, chargesUpFront; SubscriptionRepository.create; Subscription.planOrderedOn; CustomerProfile.completeCart |
| `create-order-ticket.jpg` | ProductOrder.ticketSubjects; ProductOrderRepository.createTicket; OrderTicket.subject, requesterName, requesterEmail |
| `view-order-result.jpg` | Cart.orderResult, whatsNext, upFrontCharge, monthlyCharge; Subscription.firstBillDueOn |
| `sign-in-with-existing-account.jpg` | Credentials.authenticateCredentials, isAuthenticatable, token; CustomerProfileRepository.load; CartRepository.load; SubscriptionRepository.load |
| `reset-password.jpg` | Credentials.requestTemporaryPassword; PasswordReset.send; TemporaryPassword |
| `set-new-password.jpg` | Credentials.setNewPassword, newPasswordRequirements, newPasswordRequired; PasswordReset.clear |
| `create-customer-with-temporary-password.jpg`, `force-password-reset.jpg` | PasswordReset.requireNewPassword, send; Credentials.newPasswordRequired (the screen is Set New Password) |
| `sign-out.jpg` | Credentials.signOut, isLoggedIn |
| `view-dashboard.jpg`, `view-services.jpg` | Subscription.usage, hasActiveLine, plan; SubscriptionUsage; DataAllowance; Plan.features |
| `change-plan.jpg` | Subscription.canChangePlanTo, changePlan, nextDowngradeDate |
| `request-line-portability.jpg` | Portability.validate; Subscription.requestLinePortability; PortabilityRepository.create (under the subscription's id) |
| `edit-profile.jpg` | CustomerProfile.saveUpdates; Identity.withContactDetails, preferredNameIsSingleWord |
| `send-support-request.jpg` | CustomerProfile.sendSupportRequest; SupportTicket |
| `view-billing.jpg`, `pay-now.jpg`, `open-invoice.jpg` | BillingAccount.balance, hasBalanceDue, payNow, receivedPayments, invoices, openInvoice; Invoice |
| `choose-default-card.jpg`, `enter-new-payment-method.jpg`, `remove-saved-card.jpg` | BillingAccount.paymentMethods, defaultPaymentMethod, enterNewPaymentMethod, chooseDefaultCard, removeSavedCard, canRemoveSavedCard; PaymentMethod |
