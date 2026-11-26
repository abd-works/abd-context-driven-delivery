---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Object Model — My Paradise

**Sources / context:** the existing object model, which is the primary source for every class, tier, property, and operation and its wording: the per-aggregate class models `src/customer/credentials/.context/class-model.md`, `src/customer/customer-profile/.context/class-model.md`, `src/inventory/{numbers,plans,porting,sim}/.context/class-model.md`, `src/revenue/{billing,payment,product-order,subscription,voucher}/.context/class-model.md`, each folder's `modules.md` and `src/my-paradise/.context/modules.md`. The node and client tiers come from the per-aggregate diagrams (`src/**/<aggregate>.drawio`, `src/customer/customer-profile/.context/customer-profile.drawio`), checked against the tier files committed at `HEAD` (`src/**/*-node.ts`, `src/**/*-client.tsx`). The multi-line changes are the ones the domain model makes (`src/.context/domain-model.md`, **Changed from the existing model**), carried into each tier. The prototype's screens, one per story, `sandbox/extracted-context/app-extraction/story-screens/*.jpg`, are the only reason anything below differs from the existing model; each difference is listed, with its screen, in **Changed from the existing model** at the end.

**Extends:** `practices/clean_engineering/templates/class-model.md` — `+` constructor · `------` properties · `----` operations · `->` an interaction with a collaborator's named operation · `//` a constraint the signature cannot say.

**Diagram:** `src/.context/src-model.drawio` shows the same classes, operations, and relationships.

**What changed.** The existing model is altered for one thing: a cart now holds several lines, each on its own plan. The **Cart** keeps its name and its cart-wide work (the step, the voucher, the order outcome, what is paid now); a new **Line**, owned by the Cart, takes over what the Cart held for its one line (the plan, the number or port-in, the SIM) and adds the line's nickname. The Cart is its own aggregate and module (`src/revenue/cart`), with `CartRepository`, `CartNode`, `CartRepositoryNode`, and `CartClient`; each per-line operation names the line it acts on. When the order is placed, each Line becomes a **Subscription** (`src/revenue/subscription`), the line in service, which self-care reads and changes through `SubscriptionNode` and `SubscriptionClient`. Everything else is the existing model unchanged.

---

## Layout

`##` is a bounded context, `###` a module (one aggregate folder `src/<boundedContext>/<aggregate>/`, named as in its `modules.md`), `####` a LERN tier inside it, `#####` a class. Each aggregate has up to three tiers:

- **Core** — `<aggregate>.ts`: the aggregate root, the members it composes, its in-memory `{Root}Repository`, and its `{Root}Exception`. Framework-free; every business rule lives here.
- **Node** — `<aggregate>-node.ts`: `{Root}Node` extends the root and parses the posted body (`fromRequest`, `fromPosted…`); `{Root}RepositoryNode` extends the repository, runs the Zod `.parse()` on what it reads, and writes `<aggregate>.json` through lowdb.
- **Client** — `<aggregate>-client.tsx`: `{Root}Client` extends the root for the browser; a field change returns a new client for React state, and every domain operation the browser asks for keeps the core operation's name.

The routes (`<aggregate>-routes.ts`), the views (`*View`), and the paths module (`<aggregate>-paths.ts`) of each aggregate are named on its module's seam; they hold no rules, so they carry no class card.

**Cross-aggregate sync.** From `.context/grill-answers.md`: the application layer that owns the flow calls each aggregate's repository in turn, one request at a time; each aggregate keeps its own store and never opens another's. For every arrow the source owner is the target aggregate, the receiving side holds only the target's identity, the trigger is the operation named on the arrow, and the receiving side reads the target fresh at that call. The step's own aggregate runs first, then the Cart records it on the Line, in one request on the Cart's route (`compose-steps-from-the-owner`). Placing the order hands each line to the Subscription the same way: `Cart.recordPlaced` calls `SubscriptionRepository.create` once per line in that request.

---

## Customer

Who the customer is and how they sign in — credentials, profile, and identity check.

### credentials

**Module:** `src/customer/credentials`

*Credentials* are how a customer signs in: the email and password they register, the validation code that confirms them, the session token every other aggregate reads, and — for a customer who forgot their password — a temporary password and the new password they set after it.

- **Purpose:** Register, confirm, and sign in an account; sign it out; send a temporary password and take the new password that replaces it.
- **Seam (terms):** Credentials, CredentialsValidation, CredentialsRepository, CredentialsNode, CredentialsClient, createCredentialsRoutes, credentials-paths
- **Dependencies (one-way):** my-paradise

Change credentials only through `Credentials` operations and `CredentialsRepository.update`. A sign-in with a temporary password issues no token: the caller must send the customer to set a new password. Resend timing follows `CredentialsValidation`.

Integrations:
  - → Auth System · Account
    pattern: Anticorruption Layer
    crosses: credentials, validation codes, session tokens, temporary passwords
    integration: CredentialsRepositoryNode (local store stands in for the Auth System)

#### Core — `credentials.ts`

##### **Credentials** <<Aggregate Root>> <<Entity>>

- How a customer signs in: the email and password they register, and the session token they hold once signed in. The customer creates them on *Let's create your account.* with Email, Password, and Confirm password, then **Create account**; an email already in use is refused with "Email is already registered. Want to sign in instead?"
- Its *registration requirements* are the rules a password must meet: upper and lowercase letters, a number, a symbol, 8 or more characters, and a confirmation that matches. On screen they are one hint, "Use 8+ characters, upper & lowercase letters, a number and a symbol.", and one message naming what a typed password still needs, such as "Your password still needs a number."; a confirmation that differs shows "Passwords don't match".
- Its *new password* is the password a customer sets on *Choose your new password!* after signing in with a *temporary password*, so they sign in with a password of their own from then on. Once saved with **Save password**, the credentials hold a *session token* and the *password reset* no longer requires a new password.
- To *log out*, **Logout** in the header asks "Do you want to log out?"; **Log out** removes the *session token*, so nobody can reach the customer's My Paradise pages from that browser, and **Cancel** keeps it.
- Registering leaves an *unconfirmed account* (*CredentialsValidation*) and emails a *validation code*; the *CustomerProfile* is created only once the credentials are verified, and is reached through them.
- **Invariant:** a token is issued only to a verified account with no new password pending.
- **Invariant:** a new password meets the same requirements as registering (letters, number, symbol, length, confirmed).
- **Invariant:** signing out always leaves the account without a token.

+ Credentials(email: string, password: string, confirmPassword: string, validationCode: string, verified: boolean, repository: CredentialsRepository)
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
+ register(): Promise<this>
	-> CredentialsRepository.create(this)
	-> CredentialsValidation.emailValidationCode()
+ authenticateCredentials(): Promise<this>
	-> CredentialsRepository.load(this)
	-> PasswordReset.matches(password)
	// Access Selfcare: a temporary password asks for a new password instead of issuing a token
+ requestTemporaryPassword(): Promise<this>
	-> CredentialsRepository.prepareTemporaryPassword(this)
	-> CredentialsRepository.load(this)
	-> PasswordReset.send()
	-> CredentialsRepository.update(stored)
	// Access Selfcare
+ setNewPassword(): Promise<this>
	-> missingRequirements()
	-> PasswordReset.clear()
	-> CredentialsRepository.update(this)
	// Access Selfcare; uses password and confirmPassword already entered
+ signOut(): Promise<void>
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

##### **CredentialsRepository** <<Repository>>

+ CredentialsRepository()
------
+ << aggregation >> accounts: Collection<Credentials>
----
+ new(): Credentials
+ create(credentials: Credentials): Promise<Credentials>
+ load(credentials: Credentials): Promise<Credentials | null>
+ update(credentials: Credentials): Promise<Credentials>
+ prepareTemporaryPassword(credentials: Credentials): void
	// Access Selfcare

##### **CredentialsValidation** <<Entity>>

- Confirms that the person registering owns the email, before any customer is created for the account.
- Its *unconfirmed account* state means a registered account whose validation code has not been entered yet; no customer exists for it. A code that is missing or unusable keeps the account unconfirmed ("Code is required.", "Enter all 6 digits.", "Invalid verification code."), and signing in with an unconfirmed account takes the customer back to entering the code.
- Its *verified* state means the emailed code was entered on *Check your email!* with **Verify email**; the credentials then hold a *session token*.
- Its *resend wait* stops a customer asking for code after code: after **Resend** the link reads "Resend in 30s" and tells them "We sent you a new code. Please check your email."; a resend during the wait is refused, and once 30 seconds have passed another code is sent.
- It keeps each emailed code as a *ValidationCodeMessage* and checks the *ValidationCode* the customer enters. Once it verifies, the application creates the *CustomerProfile* and the onboarding *Cart* becomes theirs, with Account done on the progress bar.

+ CredentialsValidation(credentials: Credentials)
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
+ verify(validationCode: ValidationCode): Promise<this>
	// the application then runs CustomerProfileRepository.create(credentials) and Cart.startCart()
+ resendValidationCode(): Promise<void>
	// refused during the resend wait
+ copyFrom(stored: CredentialsValidation): void

##### **ValidationCodeMessage** <<Value Object>>

- The *validation code* emailed to confirm an *unconfirmed account*: six digits, so only someone who can read that inbox can finish creating the account.
- The screen says where it went: "We've sent you a code to alex@example.com", then "It may take a few minutes to arrive. Check your spam if you don't get it."
- Each one records the email, the code, and when it was sent; a resend after the *resend wait* of *CredentialsValidation* emails a new one.

+ ValidationCodeMessage(sentAt: Date, email: string, code: string)
------
+ sentAt: Date
+ email: string
+ code: string
+ executed: boolean

##### **PasswordReset** <<Entity>>

Access Selfcare.

- Lets a customer who cannot use their password get back into their account. A customer starts one on *Forgot your password?*: "We'll send a temporary password to the email associated with your account."
- It holds the *temporary passwords* emailed, latest last. One can also come from the CRM creating the customer, or from an administrator forcing a reset; each ends on *Choose your new password!*.
- Its *new password required* state holds the customer at *Choose your new password!* until they replace the temporary password they signed in with; while it is set, signing in issues no *session token*.
- Saving the *new password* on *Credentials* clears it.
- **Invariant:** only the latest temporary password matches.
- **Invariant:** after the reset is cleared, nothing matches and no new password is required.

+ PasswordReset(credentials: Credentials)
------
+ << composition >> sent: TemporaryPassword[]
	// the temporary passwords emailed, latest last
+ newPasswordRequired: boolean
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

##### **TemporaryPassword** <<Value Object>>

Access Selfcare.

- A *temporary password* emailed to the customer when they forgot theirs, when the CRM created them, or after an administrator forced a reset, so they can sign in once and choose a *new password*.
- It records the email it went to, the password, and when it was sent.
- Signing in with it asks for a *new password* instead of signing the customer in. Asking again emails another one with "A new password was sent! Please check your email.", then waits "Resend in 30s".
- It is kept by *PasswordReset*, latest last.
- **Invariant:** a temporary password signs in once: setting the new password clears it.

+ TemporaryPassword(email: string, password: string, sentAt: Date)
------
+ email: string
+ password: string
+ sentAt: Date

##### **ValidationCode** <<Value Object>>

- The code the customer types into the six code boxes on *Check your email!* to verify their account.
- *CredentialsValidation* checks it against the emailed *validation code* (*ValidationCodeMessage*): an empty entry gives "Code is required.", fewer than six digits "Enter all 6 digits.", and a wrong code "Invalid verification code."

+ ValidationCode(code: string, sentAt: Date)
------
+ code: string
+ sentAt: Date

##### **CredentialsToken** <<Entity>>

- The *session token*: what tells every other part of My Paradise that this browser's customer is signed in.
- *Credentials* receive it when the account is verified, when the customer signs in, and when they save a *new password*. A refused sign-in leaves them without one: "The email or password you entered did not match our records. Check them and try again."
- Logging out removes it.
- **Invariant:** a token is issued only to a verified account with no new password pending.

+ CredentialsToken(email: string, jwt: string | null)
------
+ email: string
+ jwt: string | null

##### **CredentialsException** <<Value Object>>

+ CredentialsException(operation: CredentialsOperation, credentials: Credentials, message: string, cause: Error)
------
+ operation: register | signIn | validationCode | temporaryPassword | newPassword
	// Access Selfcare adds the last two
+ << association >> credentials: Credentials
+ cause: Error

#### Node — `credentials-node.ts`

##### **CredentialsNode** <<Node>> : Credentials

+ CredentialsNode(response?: Response)
----
+ fromRequest(req: ParadiseRequest, response: Response): Promise<CredentialsNode | null>
+ fromPostedValidationCode(req: ParadiseRequest): ValidationCode
+ fromPostedNewPassword(req: ParadiseRequest): { email, password, confirmPassword }
+ register(): Promise<this>
+ authenticateCredentials(): Promise<this>
+ setNewPassword(): Promise<this>
+ signOut(): Promise<void>
+ response(): CredentialsResponse

##### **CredentialsRepositoryNode** <<Repository>> : CredentialsRepository

+ CredentialsRepositoryNode()
----
+ new(response: Response): CredentialsNode
+ load(credentials: Credentials): Promise<CredentialsNode | null>
+ loadByEmail(email: string): Promise<CredentialsNode | null>
+ inResponse(credentials: Credentials, response: Response): CredentialsNode
+ remember(credentials: Credentials): CredentialsNode

#### Client — `credentials-client.tsx`

##### **CredentialsClient** <<Client>> : Credentials

------
+ operationError: string | null
+ isSubmitting: boolean
+ emailTouched: boolean
+ passwordTouched: boolean
+ confirmPasswordTouched: boolean
+ emailLeft: boolean
+ passwordLeft: boolean
+ confirmPasswordLeft: boolean
+ validationCodesResent: number
+ temporaryPasswordSent: boolean
+ temporaryPasswordResent: boolean
+ emailIsRegistered: boolean
+ signInError: string | null
+ registerError: string | null
+ validationCodeError: string | null
+ temporaryPasswordEmailMessage: string | null
+ showsSignInRetryHint: boolean
+ canRequestTemporaryPassword: boolean
+ canConfirmNewPassword: boolean
+ canSubmitValidationCode: boolean
----
+ loadState(): Promise<CredentialsClient | null>
+ withEmail(email: string): CredentialsClient
+ withPassword(password: string): CredentialsClient
+ withConfirmPassword(confirmPassword: string): CredentialsClient
+ withValidationCode(code: string): CredentialsClient
+ touch(field: CredentialFieldName): CredentialsClient
+ snapshot(): CredentialsClient
+ requirementLines(purpose: PasswordPurpose): CredentialRequirementLine[]
+ fieldMessage(field: CredentialFieldName, purpose: PasswordPurpose): string | null
+ fieldInvalid(field: CredentialFieldName, purpose: PasswordPurpose): boolean
+ register(): Promise<this>
+ authenticateCredentials(): Promise<this>
+ verify(validationCode: ValidationCode): Promise<this>
+ resendValidationCode(): Promise<CredentialsClient>
+ requestTemporaryPassword(): Promise<this>
+ setNewPassword(): Promise<this>
+ signOut(): Promise<void>
+ settle(operation: Promise<unknown>): Promise<CredentialsClient>

### customer-profile

**Module:** `src/customer/customer-profile`

*Customer profile* is who the customer is: their identity, address, billing link, and the KYC Confirm ID records on it: the Persona inquiry and whether it verified the ID. In self-care the customer can change their preferred name, alternate contact number, and address; the rest of their identity stays as onboarding recorded it.

- **Purpose:** Create and load the profile for a signed-in account, take profile details, save a customer's own updates, and keep the identity verification outcome.
- **Seam (terms):** CustomerProfile, Identity, Address, CustomerProfileRepository, CustomerProfileNode, CustomerProfileClient, createCustomerProfileRoutes
- **Dependencies (one-way):** customer/credentials, my-paradise

Change a profile only through `CustomerProfile` operations. `saveUpdates` never changes given name, last name, date of birth, or email. On the server, reach the profile through `CustomerProfileNode.fromRequest`.

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

#### Core — `customer-profile.ts`

##### **CustomerProfile** <<Aggregate Root>> <<Entity>>

- Who the customer is: their *Identity*, *Address*, billing link, and the *Kyc* their ID check left. It is created only once the *Credentials* are verified, is reached through them, and the onboarding *Cart* then belongs to it.
- Its *onboarding customer* state means the profile's cart is not placed yet; signing in takes them back to their order checklist (Check Order).
- Its *completed customer* state (done) means the cart is placed as a *ProductOrder*; onboarding is complete, signing in takes them to self-care, and their home is the dashboard.
- Its *identity ticket* asks the team to check the ID by hand when the customer skipped Persona's ID check with **Skip and enter my details**: the customer sees "We're checking your ID — It takes up to 48 hours. Our team will be in touch.", order review shows "ID: Manual review", and the ticket is opened when the order is placed (Create Order Ticket).
- Whether the identity is *verified* is read from its *Kyc*; *KYC verification required* means the customer is sent to *Verify your ID* while the identity has no ID number, where they can **Finish ID** or **Skip and enter my details**.
- In self-care the customer can change only the *preferred name*, *alternate contact number*, and *Address*; the rest stays as onboarding recorded it. It keeps the *SupportTicket*s the customer sent, latest last.
- **Invariant:** saving updates never changes given name, last name, date of birth, or email.
- **Invariant:** confirming the identity refuses a missing given name, last name, date of birth, ID nationality, ID type, ID number, expiry date, street, parish, or postal code, and an ID number another customer holds ("Customer already exists."); nothing is stored when it refuses.

+ CustomerProfile(credentials: Credentials, customerProfileId: string, identity: Identity, address: Address, billing: CustomerProfileBilling | null)
------
+ id: string
	// identity
+ << association >> credentials: Credentials
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
	// Access Selfcare; a refused update throws CustomerProfileException (saveUpdates) naming the unmet rule
+ sendSupportRequest(subject: string, message: string): void
	-> SupportTicket.missingRequirements()
	-> CustomerProfileRepository.update(this)
	// Use My Account; the sent ticket joins supportTickets; a failed store leaves supportTickets as it was
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

##### **CustomerProfileRepository** <<Repository>>

------
+ << aggregation >> customerProfiles: Collection<CustomerProfile>
----
+ create(credentials: Credentials): Promise<CustomerProfile>
+ load(credentials: Credentials): Promise<CustomerProfile | null>
+ loadById(customerProfileId: string, credentials?: Credentials): CustomerProfile | null
+ update(customerProfile: CustomerProfile): void

##### **Identity** <<Value Object>>

- The customer's details as their ID document shows them, confirmed on *Confirm your details*: given name, last name, date of birth, ID nationality, ID type, ID number, and expiry date, plus the email, which is read-only in self-care.
- Its *preferred name* is the name the customer would like to be called; optional, and one of the few details they can change later in self-care.
- Its *alternate contact number* is a second phone number the team can reach the customer on; optional, and changeable in self-care. Changing it with the preferred name gives the same identity with only those two changed.
- Its *ID number* ties one ID to one customer; while there is none, *KYC verification required* sends the customer to *Verify your ID*.
- Its *ID types offered* follow the ID nationality: Bermuda offers Driver's License, Passport, Voter ID; United Kingdom Driver's License, Passport; Canada adds Identification Card and Permanent Residence Card; United States adds Identification Card, Municipal ID, and Permanent Residence Card. Before a nationality is chosen, ID type offers nothing and reads "Choose a nationality first".
- It belongs to the *CustomerProfile*; a *PersonaInquiry* fills it from what Persona read, and a *verified KYC* locks its ID fields.
- **Invariant:** a preferred name that is not one word is refused, and nothing is stored.

+ Identity(email, name, lastName, fullName, preferredName, expiryDate, dateOfBirth, idNationality, idNumber, idType, otherPhoneNumber)
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

##### **Address** <<Value Object>>

- Where the customer lives, entered on *Confirm your details* and changeable in self-care: Address (the street), Unit / Apartment (optional), City (optional), Parish, and Postal code, such as 12 Front Street, Hamilton, Pembroke, HM 11.
- It belongs to the *CustomerProfile*; a *PersonaInquiry* fills it from what Persona read, and the customer can change it even when the ID is verified.
- **Invariant:** an address with a missing street, parish, or postal code is refused, and nothing is stored.

+ Address(street, complement, city, parish, postalCode, country)
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

##### **Kyc** <<Value Object>>

Get Verified Profile.

- What the ID check leaves on the *CustomerProfile* when the details are confirmed: the *Persona inquiry* id and whether Persona verified the ID. The customer profile reads whether the identity is verified from it.
- Its *verified KYC* state means Persona verified the ID and the customer did not edit it: *Confirm your details* is marked **Verified** and order review shows "ID: Verified".
- Its *unverified KYC* state means Persona ran but did not verify the ID: the ID fields stay open, with the "We're checking your ID" banner.
- Its *manual-review KYC* state is what a customer who skipped the ID check has: no Persona inquiry, not verified, and an *identity ticket* required on the *CustomerProfile*. *Confirm your details* starts empty, marked **Not verified**, and coming back reopens it rather than Persona's check.
- **Invariant:** while the KYC is verified, the names, date of birth, ID nationality, ID type, ID number, and expiry date Persona read are locked; only the alternate contact number, the preferred name, and the address change.

+ Kyc(personaInquiryId: string | null, verified: boolean)
------
+ personaInquiryId: string | null
	// the Persona inquiry Verify ID ran
+ verified: boolean
	// Persona verified the ID and the customer did not edit it

##### **PersonaInquiry** <<Value Object>>

Get Verified Profile; Persona's answer on Verify ID, never stored.

- Persona's ID check on *Verify your ID*: it reads the customer's ID document so they do not type their details by hand.
- It answers with an inquiry id, whether it verified the ID, and the *Identity* and *Address* it read, which *Confirm your details* starts from. Nothing of it is stored until the customer confirms their details; then its id and outcome become the *Kyc*.
- A *completed Persona inquiry* verified the ID: *Confirm your details* starts from what it read, marked Verified, with the ID fields locked and no "We're checking your ID" banner.
- A *failed Persona inquiry* read nothing: *Confirm your details* starts empty, marked Not verified, with its ID fields open and the "We're checking your ID" banner.

+ PersonaInquiry(inquiryId: string | null, verified: boolean, identity: Identity, address: Address)
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

##### **SupportTicket** <<Entity>>

Use My Account.

- A request the customer sends from self-care so the team hears about an issue or an idea.
- Its *subject* says what it is about, chosen from Found an issue, Had a great idea, or Other; sending without one gives "Please select an option."
- Its *message* holds up to 512 characters; an empty message gives "Please enter a message."
- The *CustomerProfile* keeps every ticket sent, latest last; sending it on to the CRM is intended, not built.
- **Invariant:** a missing subject or message, or a ticket the profile store cannot keep, is refused, and no ticket is recorded.

+ SupportTicket(subject: string, message: string, sentAt: Date)
------
+ subject: string
	// one of SupportTicket.subjects: Found an issue, Had a great idea, Other
+ message: string
	// up to 512 characters
+ sentAt: Date
+ requirements: { subject: "Please select an option.", message: "Please enter a message." }
----
+ missingRequirements(): SupportTicketRequirement[]
+ toJSON(): SupportTicketJson

##### **CustomerProfileException** <<Value Object>>

+ CustomerProfileException(operation: CustomerProfileOperation, credentials: Credentials, message: string, cause: Error)
------
+ operation: create | load | saveUpdates | sendSupportRequest | confirmIdentity
	// Access Selfcare adds saveUpdates; Use My Account adds sendSupportRequest; Get Verified Profile adds confirmIdentity
+ << association >> credentials: Credentials
+ cause: Error

#### Node — `customer-profile-node.ts`

##### **CustomerProfileNode** <<Node>> : CustomerProfile

------
+ stored: boolean
----
+ fromRequest(req: ParadiseRequest, customerProfileRepository: CustomerProfileRepositoryNode, visitorAccess: VisitorAccess): Promise<CustomerProfileNode>
+ fromPostedUpdates(req: ParadiseRequest): { preferredName, otherPhoneNumber, address }
+ fromPostedIdentityConfirmation(req: ParadiseRequest): { identity, address, kyc }
	// Get Verified Profile
+ fromPostedSupportRequest(req: ParadiseRequest): { subject, message }
+ response(): CustomerProfileResponse

##### **CustomerProfileRepositoryNode** <<Repository>> : CustomerProfileRepository

+ CustomerProfileRepositoryNode()
----
+ loadById(customerProfileId: string, credentials: Credentials): CustomerProfileNode | null
+ load(credentials: Credentials): Promise<CustomerProfileNode | null>
+ createOnVerified(credentials: Credentials): Promise<CustomerProfileNode>
+ draft(credentials: Credentials): CustomerProfileNode

#### Client — `customer-profile-client.tsx`

##### **CustomerProfileClient** <<Client>> : CustomerProfile

------
+ operationError: string | null
+ isSubmitting: boolean
+ changed: boolean
+ supportSubject: string
+ supportMessage: string
+ supportTouched: SupportTicketRequirement[]
+ supportRequestSent: boolean
+ detailsLocked: boolean
	// Get Verified Profile; Confirm your details keeps the verified ID fields locked until the customer presses Edit
+ detailsTouched: ProfileField[]
+ shownDateOfBirth: string
+ canSaveUpdates: boolean
+ canSendSupportRequest: boolean
+ showsVerified: boolean
+ canConfirmIdentity: boolean
----
+ create(credentials: Credentials): Promise<CustomerProfileClient>
+ load(credentials: Credentials): Promise<CustomerProfileClient>
+ withPreferredName(preferredName: string): CustomerProfileClient
	// Access Selfcare
+ withOtherPhoneNumber(otherPhoneNumber: string): CustomerProfileClient
	// Access Selfcare
+ withAddress(field: AddressField, entered: string): CustomerProfileClient
	// Access Selfcare
+ addressMessage(field: AddressField): string | null
	// Access Selfcare
+ saveUpdates(preferredName: string, otherPhoneNumber: string, address: Address): Promise<CustomerProfileClient>
	// Access Selfcare
+ withSupportSubject(subject: string): CustomerProfileClient
	// Use My Account
+ withSupportMessage(message: string): CustomerProfileClient
	// Use My Account
+ leftSupportField(field: SupportTicketField): CustomerProfileClient
	// Use My Account
+ supportMessageFor(field: SupportTicketField): string | null
	// Use My Account
+ sendSupportRequest(subject: string, message: string): Promise<CustomerProfileClient>
	// Use My Account
+ withPersonaInquiry(inquiry: PersonaInquiry): CustomerProfileClient
	// Get Verified Profile
+ isDetailLocked(field: ProfileField): boolean
+ detailOf(field: ProfileField): string
+ withDetail(field: ProfileField, entered: string): CustomerProfileClient
+ detailMessage(field: ProfileField): string | null
+ editDetails(): CustomerProfileClient
+ confirmIdentity(identity: Identity, address: Address, kyc: Kyc): Promise<CustomerProfileClient>
	// Get Verified Profile

---

## Inventory

What can be sold and assigned to a line: plans, numbers, port-ins, and SIMs.

### plans

**Module:** `src/inventory/plans`

*Plan* is what a customer can buy: each sellable entry in the catalog, what a line gets each month, and what it costs.

- **Purpose:** List the catalog plans and name the plan a request chose. Putting a plan on a line of the cart is the Cart's; changing an active line's plan is the Subscription's.
- **Seam (terms):** Plan, PlanFeature, PlanRepository, PlanRepositoryNode, PlanNode, PlanClient, createPlanRoutes, PlanCardView, PlanFeaturesView, PlanCarouselView
- **Dependencies (one-way):** my-paradise. Nothing in this folder imports the Cart or the Subscription.

Read the catalog through `PlanRepository.list` and a named plan through `PlanRepository.load`. The plan cards take the plan and its action as props from the screen that composes them.

#### Core — `plans.ts`

##### **Plan** <<Aggregate Root>> <<Entity>>

- A Plan defines a *Subscription*: what a line gets each month and what it costs, with all fees included. The catalog shows each plan on its card (Atlas, Ace, Data Freedom, Essentials), and a subscription created from a plan takes these details from it.
- A *sellable plan* is one the catalog offers; the plan catalog lists only sellable plans, each with its tagline, its features, its monthly price and its tag, such as *Best value* on Ace.
- The *Promo plan* is the one plan that is not sellable: the catalog never lists it, but it loads when its voucher, PROMO30, unlocks it ("Free for 30 days", on Essentials' allowances, $0/mo).
- A *one-year plan* is a one-year promotional plan ("1Y" in its name); in Change My Service a port request on it asks the customer to pick a paid plan first.
- A *roaming plan* is one whose order opens a roaming ticket ("Roaming plan - New Subscription"), as legacy did for Atlas.
- Putting a plan on a line belongs to the *Cart* and its *Line*; changing an active line's plan belongs to the *Subscription*. The plan itself knows neither.
- **Invariant:** a port request on a one-year promotional plan is refused until the line is on a paid plan; nothing is stored when the request is refused.

+ Plan(id: string, name: string, price: number, isSellable: boolean, tag: string | null, features: PlanFeature[])
------
+ id: string
	// identity
+ name: string
+ tagline: string
	// Seamless Global Connectivity, More of What Matters, Go Unlimited in Bermuda, Kids & Seniors Plan; Promo: Free for 30 days
+ price: number
+ tag: string | null
	// the label its catalog card shows
+ isSellable: boolean
	// the catalog offers it
+ << composition >> features: PlanFeature[]
	// View Services lists them under My plan
+ oneYear: boolean
	// Change My Service; a one-year promotional plan ("1Y" in its name), on which a port request asks for a paid plan first
+ roaming: boolean
	// ordering it opens a roaming ticket

##### **PlanRepository** <<Repository>>

------
+ << aggregation >> plans: Collection<Plan>
	// the catalog
----
+ list(): Plan[]
	// the sellable plans
+ load(id: string): Plan | null
	// any plan in the collection; an unsellable plan (Promo) is never listed, but loads when its voucher unlocks it

##### **PlanFeature** <<Value Object>>

- A PlanFeature tells the customer what a plan gives, so they can compare plans before choosing one; the catalog card and View Services under My plan list them.
- Its *region* is one of the card's two groups, *IN BERMUDA* and *WHEN YOU TRAVEL*, so local allowances and travel allowances read apart.
- Its *lines* are the words the card shows, such as "Unlimited Data / All high-speed data" or "70+ Countries included / Talk, text and data / 30GB high-speed data, then slower".
- The *Plan* owns its features; a feature has no identity of its own outside its plan.

+ PlanFeature(region: PlanFeatureRegion, lines: readonly string[])
------
+ region: inBermuda | whenYouTravel
	// the card's two groups, IN BERMUDA and WHEN YOU TRAVEL
+ lines: readonly string[]
	// the lines its catalog card shows: "Unlimited Data / All high-speed data", "70+ Countries included / Talk, text and data / 30GB high-speed data, then slower"

#### Node — `plans-node.ts`

##### **PlanNode** <<Node>> : Plan

----
+ fromRequest(req: ParadiseRequest): Plan

##### **PlanRepositoryNode** <<Repository>> : PlanRepository

+ PlanRepositoryNode()

#### Client — `plans-client.tsx`

##### **PlanClient** <<Client>> : Plan

----
+ list(): Promise<Plan[]>

### numbers

**Module:** `src/inventory/numbers`

*Number inventory* lets a customer find and keep a phone number: it holds the MSISDN pool, lists numbers a line can hold while the customer browses, and reserves the one they pick.

- **Purpose:** Search, hold, reserve, and release Bermuda MSISDNs. A number keeps only its status; the line keeps the numbers it holds and reserved. The number routes change only the inventory: the browser posts the numbers its listing holds (`held_numbers`) and the line's reserved number (`reserved_number`). Recording the held numbers, taking the reserved number, and keeping the current number are the Cart's routes (`/api/onboarding/number-inventory/held`, `/selected`, `/keep-current`), each for the line the body names.
- **Seam (terms):** NumberInventory, NumberInventoryRepository, NumberInventorySearch, NumberInventoryClient, NumberInventorySearchNode, createNumberInventoryRoutes, PickNumberView
- **Dependencies (one-way):** customer/customer-profile, my-paradise. Numbers does not import revenue/cart: the cart depends on numbers.

`PickNumberView` takes the line facts (`loaded`, `currentMsisdn`, `heldNumbers`), `onNumbersHeld`, `onReserve`, `onKeepCurrentNumber`, and the port form as props from the onboarding frame; it searches and reserves through `NumberInventoryClient`. It does not import the Subscription or porting. HTTP bodies use the `number_*` names from `NumberInventoryFields`.

#### Core — `numbers.ts`

##### **NumberInventory** <<Aggregate Root>> <<Entity>>

- A NumberInventory entry is one Bermuda phone number the business can give a line, so a customer can pick a number no other customer is offered or given at the same time.
- It is known by its *MSISDN*, the phone number itself, which the screens show formatted, such as +1 (441) 555-0106.
- Its status is *available*, *held* or *reserved*: an *available number* can be offered to any line; a *held* number is on the page a line is browsing; a *reserved number* is the one a line picked, or an active line's number.
- A number reserved as the *interim number* for a port-in carries the interim-port mark; the screens call it the *temporary number* the line uses until the port completes.
- The *Line* keeps the numbers it holds and the one it reserved; the number keeps only its status. *NumberInventorySearch* holds and reserves numbers for a line, and *Portability* reserves the interim number.
- **Invariant:** a number keeps only its own status: it does not know who holds or reserved it.
- **Invariant:** only an available number can be held, and only a held number can be reserved, so a number another line holds or reserved is never offered or reserved again.

+ NumberInventory(msisdn: string, imsi: string, status: NumberResourceStatus, interimPort: boolean)
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
	// refuses with NumberInventoryException unless available
+ reserve(reserveDetails: NumberReserveOptions): void
	// refuses with NumberInventoryException unless held; an interim-port reserve holds an available number first
+ display(msisdn: string): string
	// the number as the screens show it
+ reserved(msisdn: string): NumberInventory
	// a reserved number the pool does not list (an active line's number)
+ releaseHold(): void
+ makeAvailable(): void

**Invariants**

- A number keeps only its own status: it does not know who holds or reserved it. Whoever holds or reserves a number keeps the number — the Line keeps its `number` and its `heldNumbers`.
- Only an available number can be held, and only a held number can be reserved, so a number another line holds or reserved is never offered or reserved again.

##### **NumberInventoryRepository** <<Repository>>

------
+ << aggregation >> inventory: Collection<NumberInventory>
----
+ load(msisdn: string): NumberInventory | undefined
+ list(): NumberInventory[]
+ update(entry: NumberInventory): void
+ nextAvailable(count: number): NumberInventory[]
	// the pool's next available numbers after the ones it offered last, wrapping round; the default listing takes them, so each refresh offers a fresh set

##### **NumberInventorySearch** <<Entity>>

- A NumberInventorySearch shows the customer a short list of numbers to choose from for one line and reserves the one they pick, so the line gets a number nobody else has.
- Its *listed numbers* are the page the latest search or listing shows; *Get a new number* lists five of them (*Select one below*), and the ones it lists are held for the line while the customer browses.
- A *refresh* releases the page the line held and offers the pool's next available numbers, so each refresh shows a fresh set and none from the page before.
- When the line already has a number, that number leads the default listing as *Your number*, selected at the top; when the pool has none to offer, the screen shows *No numbers available* and the customer cannot continue.
- The *Line* hands in its held numbers and its reserved number and keeps what the search holds; a search by letters or digits goes through *TermNumberSearch*; each number's status changes on *NumberInventory*.
- **Invariant:** the search does not depend on the *Cart*: it releases only the numbers the line hands it, and reserves only one of them, and only one the line holds.

+ NumberInventorySearch(repository: NumberInventoryRepository)
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
	// the listed numbers
----
+ search(searchCriteria: NumberInventorySearchOptions, heldNumbers: NumberInventory[], reservedNumber: NumberInventory | null): void
	-> NumberInventory.releaseHold()
	-> NumberInventory.hold()
	-> NumberInventoryRepository.update(entry)
	// releases the numbers the line held, then holds the available matches; the line's reserved number leads the default listing; the default listing's other numbers are the repository's nextAvailable
+ select(msisdn: string): void
+ reserve(msisdn: string, heldNumbers: NumberInventory[]): NumberInventory
	-> NumberInventory.reserve(reserveDetails)
	-> NumberInventoryRepository.update(entry)
	// refuses a number the line does not hold, then reserves this one and answers it; a failure is NumberInventoryException with reserveFailed. The line releases its previous number when it takes this one
+ releaseHeld(heldNumbers: NumberInventory[]): void
	// the line's held numbers go back to the pool; a number since reserved stays reserved
+ applyListed(fields: NumberInventoryFields): void
	// takes a listing the browser already has
+ fromFields(body: NumberInventoryFields): NumberInventorySearch

**Invariants**

- The search does not depend on the Cart: the line hands in what it holds (`heldNumbers`) and its `reservedNumber`, and keeps `heldInventory`. It releases only the numbers it is handed, and reserves only one of them.

##### **TermNumberSearch** <<Value Object>>

- A TermNumberSearch lets a customer look for a number that spells a word or holds digits they like, such as their name.
- Its *search term* is 3 to 5 letters or digits matched against the numbers; letters match by their phone keypad digits.
- Its *dial-pad pattern* is the term with letters turned into dial-pad digits, shown beside the term, as in "Your number: JAMES (52637)".
- *NumberInventorySearch* uses the dialable pattern to find the available numbers that match.

+ TermNumberSearch(input: string)
------
+ input: string
+ converted: string
	// letters turned into dial-pad digits
----
+ clean(rawText: string): string
+ hintLabel(): string | null
+ toDialable(): string

##### **NumberInventoryException** <<Value Object>>

+ NumberInventoryException(operation: NumberInventoryOperation, number: NumberInventory | null, message: string, cause: Error)
------
+ operation: hold | reserve
+ << association >> number: NumberInventory | null
	// the number it was about; none when the pool does not list it
+ cause: Error

#### Node — `numbers-node.ts`

##### **NumberInventorySearchNode** <<Node>> : NumberInventorySearch

------
+ criteria: NumberInventorySearchOptions
+ << association >> heldNumbers: NumberInventory[]
	// the numbers the line's listing holds, as the browser posted them
+ << association >> reservedNumber: NumberInventory | null
	// the line's reserved number, as the browser posted it
----
+ fromRequest(req: ParadiseRequest, repository: NumberInventoryRepository): NumberInventorySearchNode

##### **NumberInventoryRepositoryNode** <<Repository>> : NumberInventoryRepository

+ NumberInventoryRepositoryNode()
------
+ devPoolStart: number
+ devPoolSize: number
+ devJamesSearchMsisdns: string[]
----
+ ensureDevSeeded(): void

#### Client — `numbers-client.tsx`

##### **NumberInventoryClient** <<Client>> : NumberInventorySearch

------
+ searchInput: string
+ portFormOpen: boolean
+ searched: boolean
+ operationError: string | null
+ heldMsisdns: string[]
+ reservedMsisdn: string | null
+ canSearch: boolean
+ searchHelper: string
----
+ forLine(heldMsisdns: string[], reservedMsisdn: string | null): NumberInventoryClient
	// the listing for the line the number step sets up
+ search(): Promise<NumberInventoryClient>
+ select(msisdn: string): Promise<NumberInventoryClient>
+ reserveSelected(): Promise<NumberInventoryClient>
+ refresh(): Promise<NumberInventoryClient>
+ selecting(msisdn: string): NumberInventoryClient
+ changeSearchInput(rawText: string): Promise<NumberInventoryClient>
+ openPortForm(): NumberInventoryClient
+ closePortForm(): NumberInventoryClient

### porting

**Module:** `src/inventory/porting`

*Portability* lets a customer bring the number they already have: it takes the port-in request, verifies the donor number by SMS code, and keeps an interim number on the line meanwhile.

- **Purpose:** Capture port-in facts and verify the donor number. Starting the port-in on a line of the cart is the Cart's route (`/api/onboarding/portability/begin`), which stores the Portability and records it on the Line.
- **Seam (terms):** Portability, PortabilityRepository, PortabilityRepositoryNode, PortabilityNode, PortabilityClient, createPortingRoutes, PortNumberFormView, VerifyPortedNumberView
- **Dependencies (one-way):** inventory/numbers, my-paradise. Porting does not import revenue/cart: the cart depends on porting. The routes take the subscription id the port-in is stored under — the line's — from the epic app (`PortedLineIdFor`).

The port form reports `onBeginPort`, and the verification screen reports `onVerified`, to the onboarding frame; the screens do not import the Cart. The domain does not hold the Line: the Line holds its port-in, and the repository stores each port-in under the line's subscription id.

Integrations:
  - → Inventory · Numbers · NumberInventory (by MSISDN)
    pattern: Customer/Supplier
    crosses: the interim number the line uses until the port completes
    integration: Portability.submit → NumberInventory.hold, NumberInventory.reserve(interimPort)
    sync: Numbers owns the number's status · at Continue on the port form · never staler than that request

#### Core — `porting.ts`

##### **Portability** <<Aggregate Root>> <<Entity>>

- A Portability lets a customer bring the number they already have from another provider onto a line, instead of taking a new Bermuda number.
- Its *port-in* facts are the *current provider*, the *number to be ported*, the account number, the account and account type, and two confirmations: "I confirm that this information is accurate." and "I grant permission to Paradise Mobile to bring the phone number in this form to the Paradise Mobile network." Moving the number takes 3–5 business days.
- Its *temporary number* (the interim number) is an available number the line uses from today until the port completes (*You'll get a temporary number*).
- Its *porting SMS code* is the six-digit code texted to the port number to prove it is the customer's; after *Is this phone with you?* the customer chooses *Yes, text me the code*, enters it, and may resend it after a 30-second wait.
- *Verify later* ("No, verify it later") sends no code: the port stays unverified and the team contacts the customer (*We'll contact you to verify it*).
- The *Line* holds its port-in and takes the temporary number as its number; the temporary number is reserved on *NumberInventory*.
- **Invariant:** a port-in is not submitted until every port form field and both confirmations pass validation.
- **Invariant:** a port-in does not know the line it ports onto; its interim number is reserved with no holder, and the *Line* takes it as its number.

+ Portability(donorOperator, portNumber, accountNumber, userType, accountType, device, _repository: PortabilityRepository | null, _inventory: NumberInventoryRepository)
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
	// the number reserved while the port completes (stored by its MSISDN)
+ verified: boolean
+ verificationSkipped: boolean
	// No, verify it later: no code is sent, the team contacts the customer
+ donorNumberConfirmed: boolean
	// Yes, text me the code
+ enteredCode: string
+ verificationMessage: string | null
	// what the SMS check shows
+ refusedCode: string | null
+ resendNotice: string | null
+ codeSentTo: string | null
+ canResend: boolean
	// the resend wait
+ resendWaitSeconds: number
+ smsWasSent: boolean
+ smsSendCount: number
+ portNumberShown: string
+ enteredCodeMessage: string | null
+ canEnterCode: boolean
+ canVerifyCode: boolean
+ canResendCode: boolean
+ fieldMessages: PortabilityFieldMessages
	// what each port form field still needs
----
+ validate(): PortabilityException | null
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

##### **PortabilityRepository** <<Repository>>

+ PortabilityRepository()
------
+ << aggregation >> portabilities: Collection<Portability>
----
+ create(subscriptionId: string, donorOperator: string, portNumber: string, accountNumber: string, userType: string, accountType: string, device: string): Portability
	// stored under the line's subscription id
+ load(subscriptionId: string): Portability | null
	// the latest port-in stored under that subscription id
+ update(portability: Portability): void

##### **PortabilityException** <<Value Object>>

+ PortabilityException(operation: PortabilityOperation, portability: Portability, message: string, cause: Error)
------
+ operation: validate | beginPort
+ << association >> portability: Portability
+ cause: Error

#### Node — `porting-node.ts`

##### **PortabilityNode** <<Node>> : Portability

----
+ fromRequest(req: ParadiseRequest, subscriptionId: string): { portability: Portability, posted: PostedPortability }
	// subscriptionId is the line's

##### **PortabilityRepositoryNode** <<Repository>> : PortabilityRepository

+ PortabilityRepositoryNode()
	// each stored port-in keeps the subscription_id of the line it is stored under

#### Client — `porting-client.tsx`

##### **PortabilityClient** <<Client>> : Portability

+ PortabilityClient(donorOperator: string, portNumber: string, accountNumber: string, userType: string, accountType: string)
------
+ operationError: string | null
+ isSubmitting: boolean
+ touchedFields: PortFormField[]
+ infoAccurate: boolean
+ permissionGranted: boolean
+ codeTouched: boolean
+ numberRefusalCleared: boolean
+ portNumberEntry: string
+ canBeginPort: boolean
+ codeMessage: string | null
----
+ blank(): PortabilityClient
+ fromResponse(body: PortabilityStateBody): PortabilityClient
+ load(): Promise<PortabilityClient>
+ withDonorOperator(donorOperator: string): PortabilityClient
+ withPortNumberEntry(entry: string): PortabilityClient
+ withAccountNumber(accountNumber: string): PortabilityClient
+ withUserType(userType: string): PortabilityClient
+ withAccountType(accountType: string): PortabilityClient
+ withCode(enteredCode: string): PortabilityClient
+ withInfoAccurate(infoAccurate: boolean): PortabilityClient
+ withPermissionGranted(permissionGranted: boolean): PortabilityClient
+ touch(field: PortFormField): PortabilityClient
+ fieldMessage(field: PortFormField): string | null
+ numberRefusal(operationError: string | null): string | null
+ clearNumberRefusal(): PortabilityClient
+ forNewPort(): PortabilityClient
+ tickResendWait(): PortabilityClient
+ confirmDonorNumber(): Promise<PortabilityClient>
+ deferVerification(): Promise<PortabilityClient>
+ verify(): Promise<PortabilityClient>
+ resendVerificationSms(): Promise<PortabilityClient>

### sim

**Module:** `src/inventory/sim`

*SIM selection* decides how the line's SIM reaches the customer — an eSIM, or a Paradise SIM card and its ICCID — and checks an entered ICCID against the stock.

- **Purpose:** Say which SIM the customer chose and whether an ICCID is in stock. Selecting the SIM on a line of the cart is the Cart's route (`/api/onboarding/sim/*`).
- **Seam (terms):** Sim, SimNode, IccidInventoryRepository, IccidInventoryRepositoryNode, SelectSimView
- **Dependencies (one-way):** my-paradise. Nothing in this folder imports the Cart; the onboarding frame composes `SelectSimView`.

The SIM step screen takes what it shows as props from the onboarding frame and reports back through callbacks; it never holds the onboarding client.

#### Core — `sim.ts`

##### **Sim** <<Value Object>>

- A Sim says how the line reaches the customer's phone, so the business knows whether to activate an eSIM, check a card the customer has, or give them a card to pick up.
- An *eSIM* is selected by default; the *eSIM check* tells the customer to dial *#06# and look for an EID to see whether their phone has one.
- A *Paradise SIM card* is a physical SIM (*A simpler SIM process.*): one the customer has, identified by its ICCID (*I have my Paradise SIM card.*), or one to pick up at a Paradise store or an authorized retailer (*I need a Paradise SIM card.*).
- Its *ICCID* is the 20-digit number usually printed on the back of a SIM card; it is checked against the ICCID inventory, the physical SIM stock, and refused with "Invalid ICCID." when the stock does not hold it.
- The SIM is *ready* when it is an eSIM or a Paradise SIM card whose ICCID is known; it *awaits a Paradise SIM card* when the card has no ICCID yet, and that card is activated after the order.
- The *Line* keeps its Sim; the SIM has no identity of its own.

+ Sim(simType: eSIM | pSIM | null, iccid: string | null)
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

##### **IccidInventoryRepository** <<Repository>>

------
+ << aggregation >> availableIccids: Collection<string>
	// the physical SIM stock
----
+ validate(iccid: string): void
	// refuses with IccidInventoryException ("Invalid ICCID.") for an ICCID not in stock

##### **IccidInventoryException** <<Value Object>>

+ IccidInventoryException(operation: IccidInventoryOperation, iccid: string, message: string, cause: Error)
------
+ operation: validate
+ iccid: string
	// the ICCID the stock refused; the stock keeps ICCIDs, not SIM objects
+ cause: Error

#### Node — `sim-node.ts`

##### **SimNode** <<Node>> : Sim

----
+ fromRequest(req: ParadiseRequest): SimNode

##### **IccidInventoryRepositoryNode** <<Repository>> : IccidInventoryRepository

+ IccidInventoryRepositoryNode()

#### Client — `sim-client.tsx`

##### **SimClient** <<Client>> : Sim

------
+ hasParadiseSim: boolean | null
+ iccidRefusal: string | null
+ iccidMessage: string | null
+ canContinue: boolean
+ enteredIccid: string
----
+ blank(): SimClient
+ withHasParadiseSim(hasParadiseSim: boolean): SimClient
+ withIccid(iccid: string): SimClient
+ refused(message: string): SimClient

---

## Revenue

What the customer buys and owes: the subscription and its cart, its billing, payments, vouchers, and orders.

### cart

**Module:** `src/revenue/cart`

*Cart* is the customer's lines while they are still building them — each *Line*'s plan, numbers, port-in, and SIM, the voucher, the charges, the order outcome, and the step they have reached — until the order is placed and each line becomes a *Subscription*.

- **Purpose:** Carry the customer's cart and its lines through onboarding. When a step is done, the Cart's route runs the step's aggregate and then records the step on the line the body names, in one request: record held numbers, take the reserved number, keep current number, begin port, select SIM, attach ICCID; the voucher is redeemed against every line. The product order's own route places the order and records it here (`Cart.recordPlaced`), which creates a Subscription from each line.
- **Seam (terms):** Cart, Line, CartStep, CartRepository, CartException, CartNode, CartRepositoryNode, CartClient, createCartRoutes, CheckoutView, SelectPlanView
- **Dependencies (one-way):** customer/customer-profile, customer/credentials, inventory/plans, inventory/numbers, inventory/porting, inventory/sim, revenue/voucher, revenue/billing, revenue/subscription, my-paradise. It does not depend on revenue/product-order: the order depends on the Cart.

Step screens live in their own aggregate folder and never import the Cart. The onboarding frame composes them, passes the line facts as props, and turns their done callbacks into `CartClient` operations on that line; the answer's `onboarding_path` names the next page.

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: the profile the cart and its lines belong to; a cart whose lines were chosen before the account exists is attached once the credentials are verified
    integration: Cart.startCart() after CredentialsValidation.verify; CartRepository.load(customerProfile)
    sync: Customer Profile owns the customer · on verifying the email and at each load · never staler than that request
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    crosses: each line's plan, its name and monthly price
    integration: Cart.addLine(plan), Cart.carryChosenPlan(plan), Line.choosePlan(plan) → PlanRepository.load(id)
    sync: Plans owns the plan · read on adding a line or changing its plan · never staler than that request
  - → Inventory · Numbers · NumberInventory (by MSISDN)
    pattern: Customer/Supplier
    crosses: the numbers each line holds, then the one it reserves or keeps
    integration: Line.recordHeldNumbers after NumberInventorySearch.search; Line.reserveSelectedNumber after NumberInventorySearch.reserve; Cart.removeLine → NumberInventorySearch.releaseHeld, NumberInventory.makeAvailable; CartNode.fromRequest loads each line's numbers with NumberInventoryRepositoryNode.load(msisdn)
    sync: Numbers owns the number's status · at each pick, removal, or load of the cart · never staler than that request
  - → Inventory · Porting · Portability (by line id)
    pattern: Customer/Supplier
    crosses: the ported number, the interim number, and whether it is verified now or later
    integration: Line.recordPort after Portability.beginPort(heldNumbers); CartNode.fromRequest loads each line's port-in with PortabilityRepositoryNode.load(line id)
    sync: Porting owns the port-in · at Continue on the port form, and at each load of the cart · never staler than that request
  - → Inventory · SIM · IccidInventoryRepository (by ICCID)
    pattern: Customer/Supplier
    crosses: whether a Paradise SIM card's ICCID is in stock
    integration: Line.attachIccid(sim) → IccidInventoryRepository.validate(iccid)
    sync: the SIM stock owns the ICCIDs · at the attach · the line keeps the Sim value it chose
  - → Revenue · Voucher · AppliedVoucher (by code)
    pattern: Customer/Supplier
    crosses: the voucher on the cart and the discount it gives across the lines
    integration: Cart.applyVoucher(voucher) after AppliedVoucher.redeem(plans); CartNode.fromRequest loads the cart's voucher with AppliedVoucherRepositoryNode.load(code)
    sync: Voucher owns the redemption · at Apply, and at each load of the cart · never staler than that request
  - → Revenue · Billing · BillingAccount (by customer id)
    pattern: Customer/Supplier
    crosses: whether the customer's billing account is active, which moves the cart from Checkout to Done
    integration: CartNode.fromRequest reads BillingAccountRepositoryNode.load(customerProfile) and sets Cart.billingAccount
    sync: Billing owns the account status · at each load of the cart · never staler than that request
  - → Revenue · Subscription · Subscription (by line id)
    pattern: Customer/Supplier
    crosses: each line's plan, number (its MSISDN), and SIM, handed over when the order is placed; the Paradise SIM card activated afterwards
    integration: Cart.recordPlaced → SubscriptionRepository.create(customerProfile, line.id, line.plan, line.number.msisdn, line.sim, today), one per line; Line.activateSim → SubscriptionRepository.update(subscription)
    sync: trigger: the order is placed (ProductOrder.place → Cart.recordPlaced), by direct repository calls in that request · source owner: the Cart · receiver: the Subscription · the Cart is not changed again, so the Subscription is never staler than the placed cart

#### Core — `cart.ts`

##### **Cart** <<Aggregate Root>> <<Entity>>

The customer's lines while they are still getting them: the lines, the voucher, and the step, carried through the step screens until the order is placed. It knows which step comes next.

- What the customer builds before ordering: the lines they want, the voucher, and how far they have got, until the order is placed.
- Its *family discount* is what the customer saves every month for putting several lines on one cart: "Family discount · $5 × 3 lines −$15/mo". It applies once 3 or more *paying lines* are in the cart; below that the cart shows what one more line would save ("$5 off this line too", "Add a 3rd line").
- Its *first bill* is what the customer pays now when the order is placed: the *monthly charge* less the *voucher* discount, never below 0 ("You pay now $374").
- Its *cart step* is where the customer is in setting up the order: always the first step not yet met, in order: a verified account, then for each *Line* its plan, port-in when porting, number and SIM, then the identity check, then checkout; Done once the *BillingAccount* is active.
- **Invariant:** the family discount applies from the third paying line: $5 off each paying line every month.
- **Invariant:** the voucher's discount comes off the first bill only.

+ Cart(customerProfile: CustomerProfile | null, id: string, _repo: CartRepository | null)
	// handed out by CartRepository.create / load
------
+ id: string
	// identity; the cart exists before the account does
+ << association >> customerProfile: CustomerProfile | null
	// none while lines are chosen before the account exists
+ << composition >> lines: Line[]
	// Line 1, Line 2, …; each on its own plan
+ << composition >> cartStep: CartStep
	// the step the cart has reached; Checkout until billingAccount.active, then Done
+ canReopenNumberStep: boolean
	// the step reopens the number step (CartStep.reopensNumberStep)
+ << association >> appliedVoucher: AppliedVoucher | null
	// one at a time, across all the lines (another aggregate; stored by its code)
+ << association >> billingAccount: BillingAccount | null
	// the customer's billing account (another aggregate; held by customer id); the application reads it with BillingAccountRepository.load(customerProfile) at each load of the cart
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
+ orderSuccess, payUpFront: boolean | null
	// the placed order's outcome
+ submitOrder, defaultPayment: boolean
+ returnToReview, stayingOnPlanSelection: boolean
	// the cart returns to review, or stays on plan selection
+ orderResult: allSet | almostThere
+ orderNeedsParadiseSim: boolean
	// a verified customer's Paradise SIM card has no ICCID yet, on any line
+ orderPaymentFailed: boolean
	// no default card was kept, or the up-front charge did not go through
----
+ startCart(): void
	// the cart is attached to the customer once the account is activated
+ carryChosenPlan(plan: Plan): void
	// a plan carried in from a marketing link
	-> addLine(plan)
+ addLine(plan: Plan): Line
	// Add Line To Cart: the new line is Line n on that plan
	-> PlanRepository.load(id)
	-> CartRepository.update(this)
	// TO DO: adding a line creates a new Subscription that takes its details from the plan, in an onboarding (in progress) status; the status it moves to when the order is placed is not named yet
+ removeLine(line: Line): void
	// Remove Line From Cart; the remaining lines are numbered again
	-> NumberInventorySearch.releaseHeld(heldNumbers)
	-> NumberInventory.makeAvailable() (the line's number)
	-> CartRepository.update(this)
+ applyVoucher(voucher: AppliedVoucher): void
	// after AppliedVoucher.redeem, against the plans of every line
	-> AppliedVoucher.redeem(plans)
	-> addLine(plan) for a trial voucher limited to a plan the catalog does not sell (PROMO30 unlocks Promo)
+ removeVoucher(): void
+ saveAndExit(): void
	// Save And Exit Order: "Your progress is saved."; the cart is resumed by CartRepository.load(customerProfile)
	-> CartRepository.update(this)
+ orderSummary(): { position, nickname, planName, planPrice, discountedPrice, msisdn, temporaryNumber, portNumber, portPending, simType, setUp }[] and idNumber, identity verified or in manual review, and the customer's full name
	// what the cart, the order review, and Done show, one entry per line
+ whatsNext(): { group: installEsims | putSimIn | pickUpSim | portingNumber, lines: Line[] }[]
	// the order result grouped by line: "Install your eSIMs — Mom and Alice", "Pick up your SIM — Me", "Porting your number — Mom"
+ recordPlaced(outcome, today: Date): void
	// copies the placed order's outcome; on a successful order each line becomes a Subscription, ordered today
	-> SubscriptionRepository.create(customerProfile, line.id, line.plan, line.number.msisdn, line.sim, today) for each line, on a successful order
	-> CartRepository.update(this)

**Invariants**

- A refused step throws `CartException` named by its `CartOperation` (reserveNumber, port, choosePlan, selectSim, attachIccid, activateSim).
- The step's own aggregate runs first, then the Cart records it on the Line, in one request on the Cart's route.
- The cart's next step is always the first one it has not met, in order: a verified account, then for each line in turn a plan, a verified port-in (when porting), a number, and a SIM, then the identity check, then checkout. Going back to review from a changed plan returns to Checkout.
- The family discount applies from the third line: $5 off each line every month.
- The cart holds one voucher at a time; its discount comes off the first bill only, on top of the family discount.
- Removing a line releases every number it held or reserved.
- A placed cart is not changed again, except that Done's Activate SIM Card still activates a line's Paradise SIM card.
- Each line becomes exactly one Subscription, once, when the order is placed successfully; a failed order creates none.

##### **Line** <<Entity>>

One line the customer is setting up in the cart. A Line is not a Subscription: when the order is placed, the Cart creates a Subscription from it, and the Subscription keeps the line's id.

- One phone line the customer is setting up in the cart: who it is for, its plan, its number or port-in, and its SIM, so that each line can be ordered and put in service.
- Its *nickname* answers "Who is this line for?" (Me, Mom, Alice), asked on the same screen as whether the customer will *bring their own number* or get a new one ("Choose an option to continue.").
- Its *held numbers* are the page of numbers the line keeps while the customer browses; its *number* is the one it reserved, kept, or was given as the interim number while its own number is ported in.
- The line is *set up* when it has a number or port-in and a SIM: the checklist then shows "Me · Atlas (done)". Its *position* reads "LINE 1 OF 3", and the lines are numbered again when one is removed.
- A line belongs to its *Cart*, holds its *Plan*, its *NumberInventory* numbers, its *Portability* port-in and its *Sim*. It is not a *Subscription*: when the order is placed the Cart creates a Subscription from it, and the Subscription keeps the line's id.
- **Invariant:** the line takes only a reserved number that was in its held numbers, and it releases the rest of its listing when it takes a number, keeps its current number, or ports in.
- **Invariant:** the line releases its previous number when it takes another.

+ Line(id: string, _cart: Cart)
	// handed out by Cart.addLine
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
	// the plan the line is on (another aggregate; stored by its id)
+ << association >> number: NumberInventory | null
	// the reserved, kept, or interim port number (another aggregate; stored by its MSISDN). The line knows its number; the number does not know its line
+ << association >> heldNumbers: NumberInventory[]
	// the page of numbers this line holds while the customer browses (stored by MSISDN in held_numbers)
+ << association >> portability: Portability | null
	// the port-in onto this line (another aggregate; the porting store keeps it under the line's id). The line holds its port-in; the port-in does not know its line
+ << composition >> sim: Sim | null
	// the SIM the line will run on: modality and, for a Paradise SIM card, its ICCID
+ canKeepCurrentNumber: boolean
+ setUp: boolean
	// a nickname, a number or port-in, and a SIM: the checklist shows "Me · Atlas (done)"
----
+ nameLine(nickname: string, bringsOwnNumber: boolean): void
	// "Who is this line for?", with the number choice on the same screen
+ choosePlan(plan: Plan): void
	// Change Line Plan; everything set up for the line stays
+ keepCurrentPlan(): void
+ recordHeldNumbers(numbers: NumberInventory[]): void
	// after the number step's NumberInventorySearch.search; the line keeps the numbers the listing holds
	-> CartRepository.update(cart)
+ reserveSelectedNumber(number: NumberInventory): void
	// after the number step's NumberInventorySearch.reserve; refuses a number that is not reserved or was not in heldNumbers, releases the number the line reserved before and the rest of heldNumbers, and takes the number
	-> preparePersist(reserveNumber)
	-> NumberInventory.makeAvailable() (the previous number)
	-> NumberInventorySearch.releaseHeld(heldNumbers)
	-> CartRepository.update(cart)
+ keepCurrentNumber(): void
	// releases heldNumbers
+ recordPort(portability: Portability): void
	// after Portability.beginPort(heldNumbers); the line takes its interim number and releases heldNumbers
+ selectSim(sim: Sim): void
	// an eSIM, or "I need a Paradise SIM card." (a pSIM with no ICCID, to pick up)
+ attachIccid(sim: Sim): void
	// after IccidInventoryRepository.validate
	-> IccidInventoryRepository.validate(iccid)
+ activateSim(sim: Sim): void
	// Done's Activate SIM Card, while the line waits for its Paradise SIM card; the Subscription made from this line takes the SIM and stops waiting
	-> CartRepository.update(cart)
	-> SubscriptionRepository.update(subscription) (by the line's id)

**Invariants**

- The line takes only a reserved number that was in its `heldNumbers`. It releases its listing when it takes a number, keeps its current number, or ports in (the number step's next search releases it too), and releases its previous number when it takes another. A number another line holds is never in this line's listing, because a search lists only available numbers.

##### **CartStep** <<Value Object>>

Where the customer is in onboarding. `Cart.cartStep` answers one of the named steps; the node gives it the web path that shows it (`node-decides-next-page`). Stored and sent as its name.

- Where the customer is in onboarding, so the cart can send them to the screen for the next thing they have to do.
- Its *name* is one of VerifyAccount, SelectPlan, PickNumber, VerifyPortedNumber, SelectSim, ProfileKyc, Checkout, or Done. The progress bar groups them as Account, Lines, Your ID, and Payment.
- A SelectPlan, PickNumber, VerifyPortedNumber, or SelectSim step is for one *Line*, named on the screen as "LINE 1 OF 3 · ME · ATLAS".
- Some steps *reopen the number step*: Select Sim's Back and Change go back to picking the number.
- The *Cart* answers its cart step; the web path that shows the step is added by the server.

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

##### **CartException** <<Value Object>>

+ CartException(operation: CartOperation, cart: Cart, line: Line | null, message: string, cause: Error)
------
+ operation: CartOperation
	// reserveNumber | port | choosePlan | selectSim | attachIccid | activateSim
+ << association >> cart: Cart
+ << association >> line: Line | null
	// the one line a refused step was for, when the failure is on a single line
+ cause: Error

##### **CartRepository** <<Repository>>

+ CartRepository()
------
+ << aggregation >> carts: Collection<Cart>
	// one Cart per customer during onboarding
----
+ create(customerProfile: CustomerProfile | null): Cart
	// an empty cart; null while a visitor chooses lines before the account exists
+ load(customerProfile: CustomerProfile): Cart | null
	// the cart and its lines, each holding its plan id, its numbers' MSISDNs, and the voucher code; the application loads each of those from its own repository
+ update(cart: Cart): void

#### Node — `cart-node.ts`

##### **CartNode** <<Node>> : Cart

------
+ destination: CartStep
	// the step and its web path; a visitor with no account goes to sign-up: the catalog, then Create Account once a line is chosen
+ anonymous: boolean
	// no account yet: the cart has no customer profile, or its credentials are neither entered, verified, nor signed in
----
+ fromRequest(req: ParadiseRequest, cartRepository: CartRepositoryNode, customerProfileRepository: CustomerProfileRepositoryNode, visitorAccess: { allowVisitor }): Promise<CartNode>
	// loads the cart, then each line's numbers, port-in, and voucher, and the billing account, each from its own repository
+ fromPostedLine(req: ParadiseRequest, cart: Cart): Line
	// the line the posted body names (Line n); each per-line route acts on it
+ fromPostedNickname(req: ParadiseRequest): string
	// Name Line: the nickname the customer typed, with the number choice (bringsOwnNumber)
+ fromPostedHeldNumbers(req: ParadiseRequest): NumberInventory[]
+ fromPostedSelectedNumber(req: ParadiseRequest): NumberInventory
+ addLine(plan: Plan): Line
	// remembers the chosen plans in the response cookie
+ restoreChosenPlans(cookieHeader: string | undefined): void
	-> carryChosenPlan(plan)
	// the plans chosen before sign-up: the account that starts onboarding takes a line for each
+ inResponse(response: Response): CartNode
+ destinationFor(requestedPath: string): CartStep
+ response(): CartResponse
	// the step, its path, the lines (each with its nickname, plan, number, held numbers, port-in, and SIM), the family discount, the monthly and up-front charges, the voucher, and the order outcome

##### **CartRepositoryNode** <<Repository>> : CartRepository

+ CartRepositoryNode()
	// writes cart.json: one cart per customer, each with its lines
----
+ load(customerProfile: CustomerProfile): CartNode | null
+ create(customerProfile: CustomerProfile | null): CartNode
+ draft(customerProfile: CustomerProfile): CartNode

#### Client — `cart-client.tsx`

##### **CartClient** <<Client>> : Cart

------
+ operationError: string | null
+ isSubmitting: boolean
+ anonymous: boolean
+ loaded: boolean
	// the server has answered with the cart
+ plans: Plan[]
+ currentCartPath: string
+ returningToReview: boolean
	// opened from order review (?from=checkout)
+ cartShown: boolean
	// the cart drawer under the plan catalog is open (Show cart / Hide cart)
----
+ blank(): CartClient
+ loadState(): Promise<CartClient>
+ loadPlans(): Promise<CartClient>
+ withCartShown(cartShown: boolean): CartClient
+ addLine(plan: Plan): Promise<CartClient>
+ removeLine(line: Line): Promise<CartClient>
+ nameLine(line: Line, nickname: string, bringsOwnNumber: boolean): Promise<CartClient>
+ choosePlan(line: Line, plan: Plan): Promise<CartClient>
+ keepCurrentPlan(line: Line): Promise<CartClient>
+ recordHeldNumbers(line: Line, numbers: NumberInventory[]): Promise<CartClient>
+ keepCurrentNumber(line: Line): Promise<CartClient>
+ reserveSelectedNumber(line: Line, number: NumberInventory): Promise<CartClient>
+ recordPort(line: Line, portability: Portability): Promise<CartClient>
+ selectSim(line: Line, sim: Sim): Promise<CartClient>
+ attachIccid(line: Line, sim: Sim): Promise<CartClient>
+ activateSim(line: Line, sim: Sim): Promise<CartClient>
+ applyVoucher(voucher: AppliedVoucher): Promise<CartClient>
+ removeVoucher(): Promise<CartClient>
+ saveAndExit(): Promise<CartClient>
+ snapshot(): CartClient
+ applyApiResponse(body: CartResponse): CartClient
+ followStepIfNeeded(): CartClient
+ postCart(path: string, body: Record<string, unknown>): Promise<CartClient>

### subscription

**Module:** `src/revenue/subscription`

*Subscription* is a line in service: the plan, number, SIM, and usage it holds once the order is placed, and what self-care changes on it.

- **Purpose:** Keep the customer's lines in service and run self-care on them: show usage and the plan, change the plan, request line portability. A Subscription is created by the Cart when the order is placed (`SubscriptionRepository.create`); nothing in this module reads the cart, the number inventory, the port-in, the voucher, or the billing account.
- **Seam (terms):** Subscription, SubscriptionUsage, DataAllowance, SubscriptionRepository, SubscriptionException, SubscriptionNode, SubscriptionRepositoryNode, SubscriptionClient
- **Dependencies (one-way):** customer/customer-profile, inventory/plans, inventory/sim, my-paradise. It does not depend on revenue/cart: the Cart depends on the Subscription.

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

#### Core — `subscription.ts`

##### **Subscription** <<Aggregate Root>> <<Entity>>

One line in service, found, shown, and changed on its own.

**TO DO:** create the Subscription when the line is added to the cart, not when the order is placed. It takes its details from the Plan and starts in an onboarding (in progress) status; the name of the status it reaches when the order is placed is not decided yet.

- One line in service after the order is placed, so the customer can see their usage and plan and change the line in self-care.
- It is created from a *Line* of the *Cart* when the order is placed, keeps that line's id, and holds the line's *number* (its MSISDN) and *Sim*.
- It is *waiting for a pSIM* when the order was placed for a Paradise SIM card without an ICCID; Activate SIM Card on Done gives it the SIM and ends the wait.
- Its *plan details* (name, features, monthly price) are taken from the *Plan* it was created from, or changed to; the subscription holds them, and My plan shows them.
- It has an *active line* when it holds a *Plan*; its *usage* (*SubscriptionUsage*) shows on the dashboard once the network reports it.
- Its *plan ordered on* date is the Bermuda day the current plan was ordered, at sign-up or by a plan change; it starts the *downgrade wait*.
- **Invariant:** a plan is changed only on an active line, and only with the Service Agreement agreed.
- **Invariant:** for 31 Bermuda days after the plan was ordered, a lower-priced or same-priced plan is refused; only a higher-priced plan is allowed.
- **Invariant:** a port request on a one-year promotional plan is refused until the line is on a paid plan, and nothing is stored when a request is refused.

+ Subscription(customerProfile: CustomerProfile, id: string, _repo: SubscriptionRepository | null)
------
+ id: string
	// identity; the id of the Line it was created from, so the port-in filed under that id stays the line's
+ << association >> customerProfile: CustomerProfile
	// one subscription per line
+ number: string
	// the MSISDN the line was given when the order was placed; a value, with no inventory lookup
+ << composition >> sim: Sim | null
	// the SIM the line runs on: modality and, for a Paradise SIM card, its ICCID
+ waitingForPsim: boolean
	// the order was placed for a Paradise SIM card without an ICCID
+ << composition >> usage: SubscriptionUsage | null
	// *Use My Account*; null until the network reports usage
+ << association >> plan: Plan | null
	// My plan shows its name and features (another aggregate; stored by its id)
+ hasActiveLine: boolean
	// *Use My Account*; the subscription holds a plan
+ planOrderedOn: string | null
	// *Change My Service*; the Bermuda day the active plan was ordered, at sign-up (SubscriptionRepository.create when the order is placed) or by changePlan (yyyy-MM-dd)
----
+ firstBillDueOn(today: Date): Date
+ nextDowngradeDate(today: Date): string | null
	// *Change My Service*; within 31 days of the plan order, the day a downgrade opens
+ canChangePlanTo(plan: Plan, today: Date): boolean
	// *Change My Service*; not the current plan, and not a lower-priced plan while locked
+ changePlan(plan: Plan, agreedToServiceAgreement: boolean, today: Date): void
	// *Change My Service*; refuses without the Service Agreement or when canChangePlanTo is false
	-> preparePersist(changePlan)
	-> SubscriptionRepository.update(this)
+ requestLinePortability(agreedToTerms: boolean): void
	// *Change My Service*; refuses on a promotional plan or without the porting terms. The port request itself is a Portability the application validates first (Portability.validate()) and files under this subscription's id only after this passes
+ copyFieldsFrom(source: Subscription): void
+ static restore(subscription: Subscription, row: SubscriptionJson): Subscription
	// the stored row back on a subscription; its number is stored as its MSISDN
+ toJSON(): SubscriptionJson
	// carries number, usage, and plan_ordered_on

**Invariants (Change My Service)**

- `changePlan` is for an active line (`hasActiveLine`).
- For 31 Bermuda days after `planOrderedOn`, a lower-priced or same-priced plan is refused; only a higher-priced plan is allowed (pml-backend `downgrade-wait`, `deriveOrderType`).
- A port request on a one-year promotional plan (`Plan.oneYear`) is refused until the line is on a paid plan; nothing is stored when a request is refused or the store fails.

##### **SubscriptionUsage** <<Value Object>>

- How much data a line in service has used, so the customer can see it on the dashboard (Use My Account).
- Its *local* allowance is the data used at home; its *roaming* allowance is there only on a plan with roaming.
- Each allowance is a *DataAllowance*; the usage belongs to its *Subscription*, which has none until the network reports usage.

+ SubscriptionUsage(local: DataAllowance, roaming: DataAllowance | null)
------
+ << composition >> local: DataAllowance
+ << composition >> roaming: DataAllowance | null
	// present only on a plan with roaming

##### **DataAllowance** <<Value Object>>

- One amount of data a line can use and how much of it is gone, so the dashboard can show the customer where they stand.
- Its *used* amount is the GB of High Speed Data used so far.
- Its *quota* is a number of GB, unlimited, or unknown; when it is a number the allowance *has a limit* and the dashboard draws a progress bar.
- It is the local or roaming part of a *SubscriptionUsage*.

+ DataAllowance(used: number, quota: number | 'unlimited' | 'unknown')
------
+ used: number
	// GB of High Speed Data used
+ quota: number | 'unlimited' | 'unknown'
+ hasLimit: boolean
	// the quota is a number, so the dashboard draws a progress bar

**Invariants**

- A customer with no stored subscription, or one without a plan, has no active lines; the dashboard shows the no-active-lines message.

##### **SubscriptionException** <<Value Object>>

+ SubscriptionException(operation: SubscriptionOperation, subscription: Subscription, message: string, cause: Error)
------
+ operation: SubscriptionOperation
	// changePlan | requestLinePortability
+ << association >> subscription: Subscription
+ cause: Error

##### **SubscriptionRepository** <<Repository>>

+ SubscriptionRepository()
------
+ << aggregation >> subscriptions: Collection<Subscription>
	// one per line in service
----
+ create(customerProfile: CustomerProfile, id: string, plan: Plan, number: string, sim: Sim | null, planOrderedOn: Date): Subscription
	// a line in service, made from a Line when the order is placed
+ load(customerProfile: CustomerProfile): Subscription[]
	// the customer's lines in service; none before an order is placed
+ update(subscription: Subscription): void
+ prepareUpdate(): void

#### Node — `subscription-node.ts`

##### **SubscriptionNode** <<Node>> : Subscription

----
+ fromRequest(req: ParadiseRequest, subscriptionRepository: SubscriptionRepositoryNode, customerProfileRepository: CustomerProfileRepositoryNode): Promise<SubscriptionNode[]>
	// the signed-in customer's lines in service
+ fromPostedPlanChange(req: ParadiseRequest): { plan, agreedToServiceAgreement }
+ fromPostedPortRequest(req: ParadiseRequest): { donorOperator, portNumber, accountNumber, userType, accountType, device, agreedToTerms }
	// the route validates the Portability, runs requestLinePortability, then files the port request under the subscription's id
+ response(): SubscriptionResponse

##### **SubscriptionRepositoryNode** <<Repository>> : SubscriptionRepository

+ SubscriptionRepositoryNode()
	// writes subscription.json: one stored subscription per line in service
----
+ load(customerProfile: CustomerProfile): SubscriptionNode[]
+ create(customerProfile: CustomerProfile, id: string, plan: Plan, number: string, sim: Sim | null, planOrderedOn: Date): SubscriptionNode

#### Client — `subscription-client.tsx`

##### **SubscriptionClient** <<Client>> : Subscription

------
+ activeLine: boolean
	// the server's answer: the customer has a line in service
+ hasActiveLine: boolean
----
+ changePlan(plan: Plan, agreedToServiceAgreement: boolean): Promise<SubscriptionClient>
	// Change My Service; the line in service
+ requestLinePortability(portability: Portability, agreedToTerms: boolean): Promise<SubscriptionClient>
	// Change My Service; posts the port request; the route validates it before the Subscription records it

### voucher

**Module:** `src/revenue/voucher`

*Applied voucher* gives the customer a discount or trial for a promo code: it redeems the code against the plans of the cart's lines and works out the credit.

- **Purpose:** Redeem catalog vouchers against the lines' plans and work out the credit. The repository hands out the voucher a code names (`AppliedVoucherRepository.forCode`); `AppliedVoucherNode.fromPostedCode` only reads the posted code. Applying the voucher to the cart and crediting billing is the Cart's route (`/api/onboarding/voucher/redeem`).
- **Seam (terms):** AppliedVoucher, CatalogVoucherRepository, AppliedVoucherRepository, AppliedVoucherNode, AppliedVoucherClient, RedeemVoucherView
- **Dependencies (one-way):** my-paradise. A voucher's plans are anything with an id and a price (`VoucherPlan`); the caller supplies them.

`RedeemVoucherView` takes `onRedeem` from the checkout that composes it; the voucher folder never imports the Cart.

Integrations:
  - → Voucher catalog (CatalogVoucherRepository)
    pattern: Anticorruption Layer
    crosses: each code's terms and its redemption
    integration: AppliedVoucher.redeem → catalog.redeem(code); an in-repo stand-in for the external voucher system, outside the model
  - → Inventory · Plans · Plan (by plan id)
    pattern: Customer/Supplier
    crosses: the plans a voucher is limited to, and the Promo plan PROMO30 unlocks
    integration: AppliedVoucherRepository.forCode(code, planOf)
    sync: Plans owns the plan · read when the code is entered · never staler than that request

#### Core — `voucher.ts`

##### **AppliedVoucher** <<Aggregate Root>> <<Entity>>

- A promo code the customer enters to get a discount or a free trial on their order.
- Its *code* names it: ALL10, CART10, TRAVEL25, PROMO30. An unknown code is refused with "Invalid code. Please try again."
- Its *plans* are the plans it is limited to, or any plan when there are none (TRAVEL25: Atlas and Ace; PROMO30: Promo). Only lines on those plans qualify.
- Its *amount off* is taken from each qualifying line (ALL10 $10, TRAVEL25 $25); its *percent off* is taken from the first bill after the family discount (CART10, 10%).
- A *trial* voucher lets the line pay nothing up front: PROMO30 unlocks the Promo plan, free for 30 days.
- It is redeemed against the plans of every *Line* in the *Cart*; its *redemption* (*VoucherRedemption*) records the result, and its *credit* is what the *BillingAccount* is credited.
- **Invariant:** the discount comes off the first bill only.

+ AppliedVoucher(code: string, plans: VoucherPlan[], amountOff: number | null, trial: boolean, catalog: CatalogVoucherRepository)
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
	// against the plans of every line in the cart; only lines on its plans qualify, and a voucher none of them qualifies for does nothing; otherwise the catalog redeems the code
+ credit(): { amount, glCode, remarks } | null
	// what the billing account is credited; null when the redemption failed or gives nothing off

**Invariants**

- The discount comes off the first bill only: ALL10 takes `amountOff` from every line, TRAVEL25 from each line on one of its plans, CART10 takes `percentOff` of the first bill after the family discount.

##### **AppliedVoucherRepository** <<Repository>>

----
+ create(code: string, plans: VoucherPlan[], amountOff: number | null, trial: boolean): AppliedVoucher
+ forCode(code: string, planOf: (planId: string) => VoucherPlan | null): AppliedVoucher
	// the voucher a customer entered: the stored one, or a new one on the catalog's terms for the plans planOf finds
+ load(code: string): AppliedVoucher | null
+ update(voucher: AppliedVoucher): AppliedVoucher

##### **VoucherRedemption** <<Value Object>>

- The result of redeeming a voucher code, so the cart knows whether the code worked and what it takes off.
- It records whether the redemption *succeeded*, the *discount amount*, and the *total amount* quoted for the lines.
- It belongs to its *AppliedVoucher*.

+ VoucherRedemption(success: boolean, discountAmount?: number, totalAmount?: number)
------
+ success: boolean
+ discountAmount: number
+ totalAmount: number

#### Node — `voucher-node.ts`

##### **AppliedVoucherNode** <<Node>> : AppliedVoucher

----
+ fromPostedCode(req: ParadiseRequest): string
	// the code the customer entered, read with its schema; the catalog supplies the terms

##### **AppliedVoucherRepositoryNode** <<Repository>> : AppliedVoucherRepository

+ AppliedVoucherRepositoryNode()

#### Client — `voucher-client.tsx`

##### **AppliedVoucherClient** <<Client>> : AppliedVoucher

------
+ operationError: string | null
+ isSubmitting: boolean
----
+ blank(): AppliedVoucherClient
+ fromResponse(body: unknown): AppliedVoucherClient
+ failed(code: string, message: string): AppliedVoucherClient
+ withCode(code: string): AppliedVoucherClient

### product-order

**Module:** `src/revenue/product-order`

*Product order* places the customer's order from their cart and opens the follow-up tickets its lines need. The order is created from the cart (`ProductOrderRepository.create(cart)`) and placed on the customer's billing account (`ProductOrder.place(billingAccount)`), which stores it and opens its tickets. The order route places it (`/api/onboarding/product-order`) and records the outcome on the cart (`Cart.recordPlaced`), and answers the payment status check, which may open a card-addition ticket.

- **Purpose:** Place the onboarding order for all the cart's lines, set pay-up-front and profile-done outcomes, and open the right order tickets.
- **Seam (terms):** ProductOrder, OrderTicket, ProductOrderException, OrderTicketSubject, ProductOrderRepository, ProductOrderRepositoryNode, ProductOrderClient, createProductOrderRoutes, OrderResultView
- **Dependencies (one-way):** revenue/cart, revenue/billing, customer/customer-profile, revenue/payment, my-paradise

Routes must not invent ticket subjects outside `ProductOrder`. A profile that is already `done` must not place again: `ProductOrderException` signals the conflict. The order knows its cart; nothing on the Cart side imports the order, in any tier. `OrderResultView` takes what it shows as props: the order's summary, one entry per line, and the plan features the frame composes.

Integrations:
  - → Revenue · Cart · Cart (by customer id)
    pattern: Customer/Supplier
    crosses: the lines, the up-front charge, the voucher, and the outcome the order records back
    integration: ProductOrderRepository.create(cart); the order route, after ProductOrder.place, runs Cart.recordPlaced(outcome, today)
    sync: Cart owns the cart · at Pay and subscribe · never staler than that request
  - → Revenue · Billing · BillingAccount (by customer id)
    pattern: Customer/Supplier
    crosses: the up-front payment, received or declined
    integration: ProductOrder.place → BillingAccount.takePayment(cart.upFrontCharge)
    sync: Billing owns the payment · at Pay and subscribe · never staler than that request
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: whether the customer is already done, the name and email its tickets carry
    integration: the order route, after ProductOrder.place, runs CustomerProfile.completeCart(done)
    sync: Customer Profile owns the customer · at Pay and subscribe · never staler than that request
  - → CRM / ticketing
    pattern: Customer/Supplier
    crosses: the order's follow-up tickets
    integration: intended — OrderTickets are stored with their owner instead of Zendesk

#### Core — `product-order.ts`

##### **ProductOrder** <<Aggregate Root>> <<Entity>>

- The customer's order, placed from their cart at Pay and subscribe, which takes the up-front charge, starts a subscription for each line, and opens the follow-ups the order still needs.
- It is *placed* on the customer's *BillingAccount*, which takes the *Cart*'s up-front charge; when the charge is declined the order is not placed and asks for the Payment failed ticket.
- Its outcome is copied back onto the *Cart*: whether the order *succeeded* and whether it was *paid up front*. A successful order turns each *Line* into a *Subscription* and marks the customer's onboarding done.
- Its *ticket subjects* are the follow-ups the order needs across its lines, each opened as an *OrderTicket*: identity and SIM delivery (combined when both), the promotional trial, an unverified port, a failed up-front payment, and roaming.
- **Invariant:** a customer whose onboarding is already done never places a second order ("rejected as already existing").
- **Invariant:** ticket subjects follow the cart's lines and the customer's profile; an order the store cannot take did not succeed and opens no tickets.

+ ProductOrder(id: string, cart: Cart)
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
	-> BillingAccount.takePayment(cart.upFrontCharge)
	-> ProductOrderRepository.acceptsOrder()
	-> ProductOrderRepository.update(this)
	-> ProductOrderRepository.createTicket(customerProfile, subject)
	// refuses with ProductOrderException (place) for a profile already done; the customer's active billing account takes the up-front payment (an account the payment step only opened, or none, is a failed charge), the order works out its outcome and ticket subjects from its cart's lines, is stored once placed, and opens a ticket for each subject. An order the store cannot take did not succeed and opens no tickets

**Invariants**

- A completed customer (`customerProfile.done`) never places a second order.
- Ticket subjects follow the cart's lines and its profile: identity and SIM delivery (combined when both), trial, unverified port, failed up-front payment, roaming.

##### **ProductOrderRepository** <<Repository>>

----
+ create(cart: Cart): ProductOrder
	// a new order for that cart, not stored until it is placed
+ load(cart: Cart): ProductOrder | null
+ update(order: ProductOrder): ProductOrder
	// keeps a placed order; an order not placed takes no id
+ acceptsOrder(): boolean
	// the store takes the order being placed
+ createTicket(customerProfile: CustomerProfile, subject: OrderTicketSubject): OrderTicket
	// also the card-addition ticket the payment status check opens
+ loadTickets(customerProfile: CustomerProfile): OrderTicket[]

##### **OrderTicket** <<Entity>>

- A follow-up a placed order still needs from the Paradise team, stored for the customer so it is not lost.
- Its *subject* names the follow-up: ID Verification Required, SIM Delivery Required, both together, Promotional trial, Portability Required, Card addition failed, Payment failed, or Roaming plan - New Subscription.
- It is requested in the customer's name: its *requester name* and *requester email* are the customer's full name and email.
- It is opened by the *ProductOrder*, or by the payment status check when the card attempts ran out, and belongs to the customer's *CustomerProfile*.

+ OrderTicket(id: string, customerProfile: CustomerProfile, subject: OrderTicketSubject, requesterName: string, requesterEmail: string)
------
+ id: string
+ << association >> customerProfile: CustomerProfile
+ subject: OrderTicketSubject
+ requesterName: string
+ requesterEmail: string

##### **ProductOrderException** <<Value Object>>

+ ProductOrderException(operation: ProductOrderOperation, order: ProductOrder, message: string, cause: Error)
------
+ operation: place
+ << association >> order: ProductOrder
+ cause: Error

#### Node — `product-order-node.ts`

##### **ProductOrderRepositoryNode** <<Repository>> : ProductOrderRepository

+ ProductOrderRepositoryNode()
	// writes product-order.json: the placed orders and their tickets

#### Client — `product-order-client.tsx`

##### **ProductOrderClient** <<Client>> : ProductOrder

------
+ operationError: string | null
----
+ create(cart: Cart): Promise<ProductOrderClient>
	// Pay And Subscribe: places the order for the cart's lines

### billing

**Module:** `src/revenue/billing`

*Billing account* is how the customer pays Paradise: the account their card is kept on, the up-front charge and credits it takes, and the invoices and cards Pay My Bill shows. The billing account onboarding opens when the payment step starts, so the card's $1 authorization is one of its payments, and activates once the card verifies. The account holds every payment — the $1 card authorizations, the order's up-front payment for all the cart's lines, and Pay now — and each payment it takes ends received or declined.

- **Purpose:** Open the customer's billing account at the payment step, take the $1 card authorization on it, activate it once the card verifies (which ends Checkout), and serve Pay My Bill. Routes: `/api/onboarding/payment/enter` (open the account and enter the card authorization) and `/api/onboarding/billing` (activate), plus the self-care billing routes.
- **Seam (terms):** BillingAccount, PaymentMethod, BillingAccountRepository, BillingAccountNode, BillingAccountRepositoryNode, BillingAccountClient, createBillingRoutes
- **Dependencies (one-way):** customer/customer-profile, revenue/payment, my-paradise

Change billing through `BillingAccount` operations and `BillingAccountRepository` lifecycle methods; terminated billing flows sign out via domain exceptions — routes map errors to HTTP without reimplementing billing rules.

Integrations:
  - → Customer · Customer Profile · CustomerProfile (by customer id)
    pattern: Customer/Supplier
    crosses: the profile the account is opened for
    integration: BillingAccountRepository.create(customerProfile) at the payment step; BillingAccountRepository.load(customerProfile) in self-care
    sync: Customer Profile owns the customer · at the payment step · never staler than that request

#### Core — `billing.ts`

##### **BillingAccount** <<Aggregate Root>> <<Entity>>

- How the customer pays Paradise: the account their card is kept on, which takes the up-front charge for the order and later serves Pay My Bill.
- Its *status* is *opened* when the payment step starts and *active* once the card is verified and the account is set up; an active account ends Checkout, can be charged for the order, takes the voucher credit, and can be read in self-care.
- Its *balance* is what the account owes, negative when it is in credit; when something is owed the account *has a balance due* and Pay now is offered.
- Its *payments* (*Payment*) are the $1 card authorizations and the payments it took; *Past payments* lists the received ones. Its *invoices* (*Invoice*) are listed latest first, and its *credit adjustments* (*CreditAdjustment*) record credits such as the voucher's.
- Its *saved cards* (*PaymentMethod*) are the cards Pay My Bill shows; the *default card* is the one Pay now charges.
- **Invariant:** an account is active only after it is activated; until then it is not charged for the order, takes no voucher credit, and keeps onboarding at Checkout.
- **Invariant:** Pay now refuses when nothing is owed, when there is no default card, and when the payment is declined; a declined payment leaves the balance and the payments as they were.
- **Invariant:** exactly one saved card is the default while any card is saved; the first card saved becomes it, and the default card cannot be removed.

+ BillingAccount(id: string, customerProfile: CustomerProfile, repo: BillingAccountRepository)
------
+ id: string
	// identity
+ << association >> customerProfile: CustomerProfile
	// the customer the account bills
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
	// the latest $1 card authorization; the card page and the status check use it
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
	// after the card verified; refuses an active account as already existing (409), and refuses with BillingException (activate) when the account cannot be set up
+ enterCardAuthorization(maxAttempts: number): Payment
	-> Payment.enter()
	-> BillingAccountRepository.update(this)
	// the $1 check: the account's card authorization (a new one when it has none) asks for the card page
+ checkCardAuthorization(): Payment
	-> Payment.checkStatus()
	-> BillingAccountRepository.update(this)
	// reads whether the card verified; a decline under the attempt limit refuses after a fresh card page
+ takePayment(amount: number, today: Date): Payment
	-> Payment.received(amount, today)
	-> Payment.declined(amount)
	// the order up front, or the balance from Pay now; the payment ends received or declined
+ payNow(): void
	-> takePayment(balance)
	-> BillingAccountRepository.update(this)
	// Pay My Bill; takes a payment of the balance from the default card and records it
+ enterNewPaymentMethod(paymentMethod: PaymentMethod): void
	-> PaymentMethod.requireTerms()
	-> PaymentMethod.save(id, transactionId)
	-> BillingAccountRepository.update(this)
	// Pay My Bill; the account's card authorization has already run (enterCardAuthorization, checkCardAuthorization); the first saved becomes the default
+ chooseDefaultCard(paymentMethod: PaymentMethod): void
	-> BillingAccountRepository.update(this)
	// Pay My Bill
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

##### **BillingAccountRepository** <<Repository>>

----
+ create(customerProfile: CustomerProfile): BillingAccount
	// opens the account (at the payment step); refuses a second one (409)
+ load(customerProfile: CustomerProfile): BillingAccount | null
	// the dashboard and billing read the account through the signed-in profile
+ update(billing: BillingAccount): BillingAccount
+ activationFailure(): Error | null
	// the in-repo stand-in for an account that cannot be set up
+ chargeAccepted(): boolean
	// the in-repo stand-in for whether the card accepts a payment
+ invoiceAvailable(): boolean
	// the in-repo stand-in for whether an invoice can be opened

##### **Invoice** <<Value Object>>

Pay My Bill.

- One bill on the customer's billing account, so Pay My Bill can list what was billed and when it is due.
- Its *due date* and *due amount* say when the bill falls due and how much.
- Its *status* is Paid, Partially paid, or Unpaid.
- It belongs to the *BillingAccount*, which lists its invoices latest first and opens one by its *invoice id*.

+ Invoice(invoiceId: string, dueDate: string, dueAmount: number, status: InvoiceStatus)
------
+ invoiceId: string
+ dueDate: string
	// yyyy-MM-dd
+ dueAmount: number
+ status: PAID | PARTIALLY_PAID | UNPAID

##### **PaymentMethod** <<Entity>>

The card the account pays with. The customer enters it on the card form (`PaymentMethodClient` holds the entry while they type; `BillingAccountNode.fromPostedNewPaymentMethod` reads the posted one); once its $1 authorization completes the account saves it.

- A card the customer pays with, entered on the card form and saved on the billing account once it is verified.
- Its *card number* is what the customer typed; once the card is saved only its *brand* and *last four digits* are kept. The brand is Visa for a number starting 4 and Mastercard for one starting 5.
- The customer must *agree to the terms* of the $1 authorization before the card is checked.
- Its *transaction id* is the $1 authorization, a *Payment*, that verified the card.
- It belongs to the *BillingAccount*, which saves it and chooses the default card.
- **Invariant:** a card without the authorization terms, or whose authorization did not complete, is refused, and nothing is saved.

------
+ id: string
	// identity once saved
+ cardNumber: string
	// what the customer typed; a saved card no longer has it
+ agreedToTerms: boolean
+ brand: string
	// Visa for a number starting 4, Mastercard for one starting 5; a saved card keeps the brand it was saved with
+ lastFourDigits: string
+ status: string
+ transactionId: string
	// the $1 authorization that verified it
+ requirements: { terms: the $1 authorization terms }
----
+ entered(cardNumber: string, agreedToTerms: boolean): PaymentMethod
	// the card the customer entered
+ missingRequirements(): PaymentMethodRequirement[]
+ requireTerms(): void
	// refuses with BillingException (enterNewPaymentMethod); the route checks it before the $1 authorization runs
+ save(id: string, transactionId: string): void
	// keeps the brand and last four, drops the number

##### **CreditAdjustment** <<Value Object>>

- A credit applied to the customer's billing account, such as what a voucher takes off, so the account owes less.
- It holds the credit's *amount*, the *GL code* it is booked under, and *remarks* saying what it is for.
- It belongs to the *BillingAccount*; the *AppliedVoucher*'s credit is applied as one.

------
+ amount: number
+ glCode: string
+ remarks: string

##### **BillingException** <<Value Object>>

+ BillingException(operation: BillingOperation, billingAccount: BillingAccount | null, message: string, cause: Error)
------
+ operation: create | activate | applyCredit | payNow | enterNewPaymentMethod | chooseDefaultCard | removeSavedCard | openInvoice
+ << association >> billingAccount: BillingAccount | null
	// the account it was about; none for a card refused before it joins an account
+ cause: Error
	// BillingConflict.AlreadyExists when the customer already has an account

#### Node — `billing-node.ts`

##### **BillingAccountNode** <<Node>> : BillingAccount

----
+ fromRequest(req: ParadiseRequest, customerProfileRepository: CustomerProfileRepositoryNode): Promise<BillingAccount | null>
+ openedFromRequest(req: ParadiseRequest, customerProfileRepository: CustomerProfileRepositoryNode): Promise<BillingAccount>
+ fromPostedNewPaymentMethod(req: ParadiseRequest): PaymentMethod
+ fromPostedPaymentMethod(req: ParadiseRequest, billingAccount: BillingAccount): PaymentMethod

##### **BillingAccountRepositoryNode** <<Repository>> : BillingAccountRepository

+ BillingAccountRepositoryNode()

#### Client — `billing-client.tsx`

##### **BillingAccountClient** <<Client>> : BillingAccount

------
+ operationError: string | null
+ currentBalance: string
+ inCredit: boolean
+ balanceDueOn: string | null
+ yourCards: PaymentMethod[]
----
+ create(customerProfile: CustomerProfile): Promise<BillingAccountClient>
+ load(customerProfile: CustomerProfile): Promise<BillingAccountClient | null>
+ invoiceMonth(invoice: Invoice): string
+ invoiceStatus(invoice: Invoice): string
+ paymentMonth(receivedOn: string): string
+ payNow(): Promise<BillingAccountClient>
+ enterNewPaymentMethod(paymentMethod: PaymentMethod, _authorization: unknown): Promise<BillingAccountClient>
+ chooseDefaultCard(paymentMethod: PaymentMethod): Promise<BillingAccountClient>
+ removeSavedCard(paymentMethod: PaymentMethod): Promise<BillingAccountClient>
+ openInvoiceInNewTab(invoiceId: string): Promise<BillingAccountClient>

##### **PaymentMethodClient** <<Client>> : PaymentMethod

------
+ canAdd: boolean
----
+ blank(): PaymentMethodClient
+ withAgreedToTerms(agreedToTerms: boolean): PaymentMethodClient
+ withCardNumber(cardNumber: string): PaymentMethodClient

### payment

**Module:** `src/revenue/payment`

*Payment* proves the customer's card can pay: the $1 card authorization and its status, the payments a billing account holds, and the device wallet credential checkout uses. A Payment is a member of the BillingAccount aggregate: the account composes its payments (`BillingAccount.payments`), reaches the customer, and stores them with itself — a Payment holds no customer and has no repository.

- **Purpose:** Authorize a card and keep its attempts and status, and record a payment a billing account took. The billing account owns its payments and stores them: entering the card authorization is the billing account's route (`/api/onboarding/payment/enter`), and the status check that can open an order ticket is the order side's route.
- **Seam (terms):** Payment, CardAuthorization, PaymentGateway, PaymentClient, EnterPaymentView, DeviceWalletMerchantCredential
- **Dependencies (one-way):** none on other aggregates; revenue/billing depends on it

The onboarding frame hands `EnterPaymentView` to the checkout, with the cart's monthly charge, family discount, and up-front charge for all its lines. Nothing in this folder imports the billing account, the order, the Subscription, or the customer profile.

Integrations:
  - → Card processor
    pattern: Anticorruption Layer
    crosses: the $1 authorization, its hosted card page, and its status
    integration: Payment.enter, Payment.checkStatus — an in-repo stand-in for FAC, not part of the model

#### Core — `payment.ts`

##### **Payment** <<Entity>>

Money a billing account moves on a card: the $1 authorization that verifies a new card, or a payment the account takes, which ends received or declined.

- Money a billing account moves on a card: the $1 authorization that proves a new card can pay, or a payment the account takes, such as the up-front charge or Pay now.
- A *card authorization* payment asks the card processor for the $1 authorization (*CardAuthorization*) and shows the customer the card page under "Add your card".
- Its *last status* (*PaymentStatus*) says whether the card was approved or declined, with the processor's reason. Each decline counts in its *payment attempts* and gets a fresh card page.
- When the attempts reach the maximum, the card addition is *exhausted*: no fresh card page is offered, and a Card addition failed ticket is opened.
- A payment the account takes ends *received* or *declined*; a received payment records its amount and the day it was received.
- It belongs to the *BillingAccount*, which holds and stores its payments.
- **Invariant:** a status is checked only for an authorization this payment entered.
- **Invariant:** only a received payment is recorded on the account.

+ Payment(maxAttempts: number, payerReference: string, gateway: PaymentGateway, takenAmount: number | null)
------
+ maxAttempts: number
	// how many declines get a fresh card page
+ << composition >> authorization: CardAuthorization | null
	// the processor's record of the $1 authorization
+ << composition >> lastStatus: PaymentStatus | null
	// completed, failed, received, or declined, with the processor's reason
+ paymentAttempts: number
+ cardAdditionExhausted: boolean
	// the attempts ran out; the order side opens a card-addition ticket
+ received: boolean
	// a billing account received this payment
+ receivedOn: string | null
	// the day it was received (yyyy-MM-dd)
+ amount: number | null
+ transactionId: string | null
+ orderIdentifier: string
+ salesChannel: SalesChannel
+ authorizesCard: boolean
	// a $1 card authorization rather than money the account took
----
+ received(amount: number, receivedOn: string): Payment
	// a payment the account received
+ declined(amount: number): Payment
	// a payment the card declined
+ enter(): void
	// asks the card processor for an authorization, filed under the account holder's reference the billing account gives it; refuses with PaymentException (load) when none comes back
+ checkStatus(): void
	// reads the authorization's status; an unverified card under the attempt limit gets a fresh authorization and refuses with PaymentException (unverified)

**Invariants**

- A status is checked only for an authorization this payment entered.
- Past `maxAttempts`, a declined card stops asking again and is marked `cardAdditionExhausted`.
- A payment a billing account takes is received or declined when it is taken; only a received one is recorded on the account.

##### **CardAuthorization** <<Value Object>>

- The card processor's record of the $1 authorization, so the customer can enter their card and the payment can check whether it was approved.
- Its *hosted page* is the card page the customer enters the card on; its *transaction identifier* names the authorization, and its *total amount* is the $1.
- It belongs to its *Payment*.

------
+ transactionIdentifier: string
+ totalAmount: number
+ orderIdentifier: string
+ salesChannel: SalesChannel
+ hostedPage: string

##### **PaymentStatus** <<Value Object>>

- What the card processor said about an authorization or a payment, so the customer knows whether their card went through.
- Its *status* is completed, failed, received, or declined, with the processor's *reason*; *completed* means the card was approved.
- It is the *last status* of a *Payment*.

------
+ status: PaymentResult
+ reason: string
+ completed: boolean

##### **PaymentException** <<Value Object>>

+ PaymentException(operation: PaymentOperation, payment: Payment | null, failure: PaymentFailure, cause: Error)
------
+ operation: enter | checkStatus
+ << association >> payment: Payment | null
	// the payment it was about; none when the billing account has no card authorization yet
+ failure: load | unverified
	// the message follows it
+ cause: Error

##### **DeviceWalletMerchantCredential** <<Aggregate Root>> <<Entity>>

The merchant key and certificate checkout uses so the customer can pay from a device wallet.

- The merchant key and certificate checkout uses so the customer can pay from a device wallet.
- Its *key identifier* names the merchant key, and its *certificate* proves Paradise is the merchant.
- There is one stored credential, and checkout reads it when the customer pays.

+ DeviceWalletMerchantCredential(keyIdentifier: string, certificate: string)
------
+ keyIdentifier: string
+ certificate: string

##### **DeviceWalletMerchantCredentialRepository** <<Repository>>

+ DeviceWalletMerchantCredentialRepository()
------
+ << aggregation >> credential: DeviceWalletMerchantCredential | null
	// the one stored credential
----
+ load(): DeviceWalletMerchantCredential | null

#### Node — `payment-node.ts`

##### **DeviceWalletMerchantCredentialRepositoryNode** <<Repository>> : DeviceWalletMerchantCredentialRepository

+ DeviceWalletMerchantCredentialRepositoryNode()

#### Client — `payment-client.tsx`

##### **PaymentClient** <<Client>> : Payment

------
+ operationError: string | null
+ isSubmitting: boolean
+ hostedPage: string | null
----
+ blank(): PaymentClient
+ enter(): Promise<PaymentClient>
+ checkStatus(): Promise<PaymentClient>

---

## My Paradise | epic-wide

What every aggregate shares across one browser session and one request.

### my-paradise

**Module:** `src/my-paradise`

*My Paradise* is what every aggregate shares across one browser session and one request: the per-request record of what each aggregate's node already read, the My Paradise paths, the destination the browser asks for, and the scroll a step page hands to the next. It belongs to no aggregate and knows none of them.

- **Purpose:** Give each aggregate's node one place to keep what it read from a request (`ParadiseRequest.paradise`), so a second read in the same request answers the same object; name the My Paradise paths; ask the server where the browser belongs (`MyParadiseClient`); carry a step page's scroll to the next (`keepScroll`).
- **Seam (terms):** ParadiseRequest, ParadiseRequestContext, MyParadiseClient, ParadiseDestinationResponse, keepScroll, MY_PATH, MY_DESTINATION_REDIRECT_PATH, NOT_FOUND_PATH, ROOT_PATH
- **Dependencies (one-way):** none. Every aggregate's node and routes depend on it.

My Paradise imports no aggregate. Each aggregate adds its own key to `ParadiseRequestContext` (`credentials`, `customerProfile`, `onboarding`, `sim`). What needs several aggregates at once — where the browser belongs and the session routes — lives in the epic app.

#### Node — `paradise-request.ts`

##### **ParadiseRequest** <<Node>>

------
+ method: string
+ headers: { cookie }
+ << composition >> paradise: ParadiseRequestContext
	// what each aggregate's node already read in this request, by aggregate

##### **ParadiseRequestContext** <<Value Object>>

------
+ credentials: CredentialsNode
+ customerProfile: CustomerProfileNode
+ onboarding: CartNode
+ sim: SimNode

#### Client — `my-paradise-client.ts`

##### **MyParadiseClient** <<Client>>

----
+ fetchDestination(apiBase: string, pathname: string): Promise<ParadiseDestinationResponse>
	// the page the server says the browser belongs on: the cart path and the step

---

## Changed from the existing model

One line per change, with the screen that forces it (`sandbox/extracted-context/app-extraction/story-screens/`).

- **Line** «Entity» is added in the subscription core, a type of Subscription owned by the Cart, with `nickname` and `nameLine(nickname)` — `add-line-to-cart.jpg`, `view-cart.jpg` (Line 1 Atlas, Line 2 Ace), `name-line.jpg` ("Who is this line for?").
- **Cart** is no longer a type of Subscription; the generalisation moves to Line — `view-cart.jpg`, `check-order.jpg` (one cart, several lines, each on its own plan, number, and SIM).
- `Cart.lines`, `Cart.addLine(plan)`, `Cart.removeLine(line)` are added — `add-line-to-cart.jpg`, `remove-line-from-cart.jpg`.
- `Cart.heldNumbers` and `Cart.canKeepCurrentNumber` move to Line — `pick-number.jpg` ("LINE 1 OF 3 · ME · ATLAS" lists numbers for that line).
- `Cart.choosePlan`, `keepCurrentPlan`, `recordHeldNumbers`, `reserveSelectedNumber`, `keepCurrentNumber`, `recordPort`, `selectSim`, `attachIccid`, `activateSim` move to Line under the same names — `change-line-plan.jpg` ("Choose a plan for Line 1 Me"), `pick-number.jpg`, `select-sim.jpg`, `enter-porting-number.jpg`, `activate-sim.jpg`.
- `Subscription.appliedVoucher`, `upFrontCharge`, `voucherDiscount`, `orderSuccess`, `payUpFront`, `submitOrder`, `defaultPayment`, `returnToReview`, `stayingOnPlanSelection` move to Cart, because they belong to the whole cart, not one line — `apply-voucher.jpg` ("$10 off every line"), `enter-payment.jpg` (one "You pay now" for all lines), `return-to-order-review.jpg`, `view-cart.jpg`.
- `Subscription.customerProfile` now reads "one subscription per line", not "one subscription per customer profile" — `view-order-result.jpg` (several lines placed at once).
- `Cart.customerProfile` is added, and is null until the account exists (it was inherited from Subscription); `Cart(customerProfile: CustomerProfile | null, …)` — `create-customer.jpg` ("Finish your order" lists the lines chosen before the account).
- `Cart.familyDiscount` and `Cart.monthlyCharge` are added — `apply-family-discount.jpg` ("Family discount · $5 × 3 lines −$15/mo", "$434/mo"), `view-cart.jpg` ("save $180 a year with 2 more lines").
- `Cart.upFrontCharge` now means the lines' monthly charge less the voucher, not one plan's price — `apply-family-discount.jpg` ("You pay now $404, then $434/mo").
- `Cart.orderSummary()` answers one entry per line, with its nickname — `check-order.jpg` ("Me · Atlas", "Mom · Ace", "Alice · Data Freedom").
- `Cart.carryChosenPlan(plan)` now adds a line on that plan — `display-plans.jpg` ("Add a line to start").
- `Cart.applyVoucher` adds a line on the voucher's unsellable plan for a trial voucher — `unlock-promo-plan.jpg` ("Your Promo plan is ready", PROMO30 free for 30 days).
- `Cart.recordPlaced` sets `planOrderedOn` on every line — `view-order-result.jpg` ("Here's what's next for your lines").
- `CartStep.line` is added: the line a per-line step sets up — `name-line.jpg`, `select-sim.jpg` ("LINE 1 OF 3").
- The cart's step order runs the plan, port, number, and SIM steps for each line in turn — `create-customer.jpg` ("Line 1 · Atlas … Choose a number and a SIM", then "Verify your ID").
- `SubscriptionRepository.subscriptions` is one per line, not one per customer profile, and `update` takes a Subscription or a Cart — `view-order-result.jpg`.
- `CartNode.fromPostedLine(req, cart)` is added: every per-line route names the line it acts on — `pick-number.jpg`, `select-sim.jpg` ("LINE 1 OF 3").
- `CartNode.fromPostedNickname(req)` is added for Name Line — `name-line.jpg`.
- `CartNode.choosePlan(plan)`'s override, which remembered the chosen plan in the response cookie, becomes `CartNode.addLine(plan)`, because a visitor now adds lines before the account exists — `display-plans.jpg`, `create-customer.jpg`.
- `CartNode.restoreChosenPlan(cookieHeader)` becomes `restoreChosenPlans(cookieHeader)`, restoring a line for each plan chosen before sign-up — `create-customer.jpg` (several lines listed before the account).
- `CartNode.anonymous` also holds for a cart with no customer profile, and the visitor's destination asks whether any line is chosen instead of whether the cart has a plan — `display-plans.jpg`, `create-customer.jpg`.
- `CartNode.response()` answers the lines, the family discount, and the monthly and up-front charges instead of one plan, number, and SIM — `view-cart.jpg`, `check-order.jpg`.
- `SubscriptionRepositoryNode` stores the cart and one subscription per line — `view-order-result.jpg`.
- `CartClient`'s per-line operations (`choosePlan`, `keepCurrentPlan`, `recordHeldNumbers`, `keepCurrentNumber`, `reserveSelectedNumber`, `recordPort`, `selectSim`, `attachIccid`, `activateSim`) keep their names and take the line first — `change-line-plan.jpg`, `pick-number.jpg`, `select-sim.jpg`, `activate-sim.jpg`.
- `CartClient.addLine(plan)`, `removeLine(line)`, and `nameLine(line, nickname)` are added — `add-line-to-cart.jpg`, `remove-line-from-cart.jpg`, `name-line.jpg`.
- `CartClient.cartShown` and `withCartShown(cartShown)` are added — `view-cart.jpg`, `remove-line-from-cart.jpg` ("Hide cart").
- `CartClient.planName` is removed: each line's plan name is in `orderSummary()` — `view-cart.jpg` (a plan name per line).
- `CartClient.changePlan` and `requestLinePortability` take the line in service first and no longer override a Cart operation, because the Cart is no longer a Subscription; `activeLine` now means a line of the cart is in service — `change-plan.jpg`, `view-services.jpg`.
- `NumberInventoryClient.forCart(heldMsisdns, reservedMsisdn)` becomes `forLine(heldMsisdns, reservedMsisdn)`; the numbers module's "cart" becomes "line" throughout — `pick-number.jpg` ("LINE 1 OF 3 · ME · ATLAS").
- `PortabilityRepository.create` stores the port-in under the line's subscription id; `PortabilityNode.fromRequest`'s `subscriptionId` is the line's — `enter-porting-number.jpg`, `verify-ported-number.jpg`.
- `AppliedVoucher.redeem(plan)` becomes `redeem(plans)`: the voucher is redeemed against every line's plan — `apply-voucher.jpg`, `check-order.jpg` ("ALL10 −$30 first bill" on three lines).
- `AppliedVoucher.quotedPrice` now quotes the lines' price, not one plan's; `amountOff` is per qualifying line and `percentOff` applies after the family discount — `apply-family-discount.jpg`, `apply-voucher.jpg`.
- `ProductOrder.subscription` becomes `cart: Cart`, `ProductOrder(id, subscription)` becomes `ProductOrder(id, cart)`, and `ProductOrderRepository.create(subscription)` / `load(subscription)` become `create(cart)` / `load(cart)`, because the order is made from the cart, which is no longer a Subscription — `pay-and-subscribe.jpg`.
- `ProductOrder.place` reads `cart.upFrontCharge` and works out its ticket subjects across the cart's lines — `pay-and-subscribe.jpg`, `view-order-result.jpg`.
- `ProductOrderClient.create(subscription)` becomes `create(cart)` — `pay-and-subscribe.jpg`.
- The payment module's `EnterPaymentView` takes the cart's monthly charge, family discount, and up-front charge instead of one plan name and monthly price — `enter-payment.jpg`, `apply-family-discount.jpg`.

**Audit, 2026-11-18.** Carried from the domain model's audit (`src/.context/domain-model.md`, **Changed from the existing model**): only clear shape problems; no class, member, exception, or name is removed or renamed.

- **Cart** becomes «Aggregate Root» and **Subscription** becomes «Entity», reached through the Cart; `Cart.id` is added; the SubscriptionRepository keeps its name and its collection is one Cart per customer — `view-cart.jpg`, `apply-family-discount.jpg`, `remove-line-from-cart.jpg`, `display-plans.jpg`.
- `Plan.tagline` is added — `display-plans.jpg`, `unlock-promo-plan.jpg`.
- `PlanFeature.kind: data | calling | texting` becomes `region: inBermuda | whenYouTravel` — `display-plans.jpg`, `change-line-plan.jpg`.
- `PlanRepository.load` now loads an unsellable plan too, for the Promo line — `unlock-promo-plan.jpg`.
- `Cart.fullPrice` is added, with the family-discount nudge (now `nextFamilyDiscountLineCount`, `familyDiscountWith`, `monthlySaving`, after the multi-line prototype) — `view-cart.jpg`, `apply-family-discount.jpg`, `enter-payment.jpg`.
- `Cart.saveAndExit()` and `CartClient.saveAndExit()` are added — `save-and-exit-order.jpg`.
- `Cart.whatsNext()` is added — `view-order-result.jpg`.
- `Cart.orderSummary()` entries add `position`, `discountedPrice`, `temporaryNumber`, `portPending`, `setUp`, and the identity check with the customer's full name — `check-order.jpg`, `apply-family-discount.jpg`.
- `Line.position`, `bringsOwnNumber`, and `setUp` are added; `nameLine(nickname)` becomes `nameLine(nickname, bringsOwnNumber)`, and `CartClient.nameLine` takes `bringsOwnNumber` — `name-line.jpg`, `check-order.jpg`.
- `Line.selectSim` also records "I need a Paradise SIM card." — `request-paradise-sim-card.jpg`.
- `SubscriptionException.line` is added — `pick-number.jpg`, `select-sim.jpg`.
- `Portability.informationConfirmed` and `permissionGranted` are added, and `validate` asks for both — `request-line-portability.jpg`.
- `Portability.beginPort` no longer sends the code; `confirmDonorNumber()` sends it; `deferVerification()` is added on the core and on `PortabilityClient` — `defer-port-verification.jpg`.
- `Identity.idTypesOffered` is added, and `missingRequirements` asks for given name, date of birth, and expiry date — `enter-id-details-manually.jpg`.
- `CustomerProfile.confirmIdentity` keeps the ID fields Persona read while the KYC is verified — `record-kyc-inquiry.jpg`, `confirm-details.jpg`.
- `CredentialsValidation.canResend` and `resendWaitSeconds` are added — `resend-validation-code.jpg`.


**Board review, 2026-11-18.** The Cart becomes its own aggregate and module; the changes match `src/.context/domain-model.md` (**Board review, 2026-11-18**), carried into each tier.

- Module `src/revenue/cart` is added: core `cart.ts` (Cart, Line, CartStep, CartException, CartRepository), node `cart-node.ts` (CartNode, CartRepositoryNode), client `cart-client.tsx` (CartClient). Cart, Line, CartStep, CartNode, and CartClient move here from `src/revenue/subscription` under the same names.
- `CartRepository` and `CartRepositoryNode` are added; the cart is stored in `cart.json`. `CartNode.fromRequest` takes the `CartRepositoryNode` and loads each line's numbers, port-in, and voucher, and the billing account, from their own repositories.
- `src/revenue/subscription` keeps Subscription, SubscriptionUsage, DataAllowance, SubscriptionException, and SubscriptionRepository; Subscription becomes «Aggregate Root» «Entity», created from each Line when the order is placed.
- `SubscriptionNode` is added with `fromRequest`, and `CartNode.fromPostedPlanChange` and `fromPostedPortRequest` move to it, because they parse self-care requests on a line in service.
- `SubscriptionClient` is added, and `CartClient.changePlan`, `requestLinePortability`, `activeLine`, and `hasActiveLine` move to it, because Change My Service acts on a Subscription, not on the cart; the operations no longer take a line.
- `SubscriptionRepository(billingAccounts, portabilities, appliedVouchers, numberInventory)`, `SubscriptionRepository.billingAccounts`, `SubscriptionRepository.numberInventory`, and `PortabilityRepository(numberInventory)` are removed: a repository holding another repository was a modelling mistake carried in from the old code; the original domain model never had it.
- `SubscriptionRepositoryNode` stores one subscription per line in service in `subscription.json`; its `load` answers `SubscriptionNode[]` and its `create` takes the line's id, plan, MSISDN, SIM, and order day.
- `CartException` is added, taking the cart steps and `line` from `SubscriptionException`.
- Line is no longer a type of Subscription; `Subscription.number` is the MSISDN as a value; `Subscription.portability` moves to Line; `Subscription.requestLinePortability` takes only `agreedToTerms`; `Subscription.restore` drops `numberOf`.
- The contexts are named Customer, Inventory, and Revenue, without the vendor word "custom".
