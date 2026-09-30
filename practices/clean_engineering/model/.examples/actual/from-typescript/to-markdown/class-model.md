# Customer

## Customer

+ Customer(id: string, verified: boolean, identity: Identity, address: Address, accountCredentials: AccountCredentials, cart: Cart | null, billing: Billing | null, subscriptions: Subscription[], personaInquiry: PersonaInquiry | null)
	// canonical form: new Customer(accountCredentials)
	// id, identity, and address are derived from accountCredentials when not passed
	// repository passes explicit id / identity / address when Mavenir has richer data
------
+ id: string
	// derived from accountCredentials.customerId when not passed
	// empty string when credentials have no customer id
+ verified: boolean
	// persisted KYC on the party
	// always false after ProfileRequirements.mapInquiry / storeFailedInquiry
	// flips true on confirmIdentity when PersonaInquiry.verified
	// Cart.storeOrderResult overwrites from order-body verified
	// order-body verified is Midtier verifiedResponse = KYC | Portability.portNumber | Plan.bypassVerified
	// fail Cart.storeOrderResult does not write verified
+ << composition >> identity: Identity
	// derived from accountCredentials.email when not passed
+ << composition >> address: Address
	// empty Address when not passed
+ << association >> accountCredentials: AccountCredentials
	// required constructor argument; own aggregate, not composed
+ << association >> cart: Cart | null
	// from Cart
	// 0..1
	// set by CartRepository.find / create
+ << association >> billing: Billing | null
	// from Billing
	// 0..1
	// Mavenir customer.account[0]
+ << association >> subscriptions: Subscription[]
	// from Subscription
	// 0..*
	// each line is one Subscription after cook
+ << association >> personaInquiry: PersonaInquiry | null
	// from Care
	// 0..1
----
+ confirmIdentity(): Customer
	-> ProfileRequirements.missing
	-> PortalGateway.patchProfile
	// AccountToken already on the wrap
	// maps Identity / Address onto EngagedParty + ContactMedium
	// uses Customer.personaInquiry internally
	// Customer.verified from PersonaInquiry.verified when the inquiry is present
	// always true on the happy path
	// inquiryId on Mavenir from PersonaInquiry.inquiryId when present
	// duplicate Identity.idNumber or patch failure throws CustomerException with operation confirmIdentity
	// auto-apply voucher after success is Cart.applyVoucher

## CustomerRepository

+ CustomerRepository(customers: Collection<Customer>, midtierCustomerService: MidtierCustomerService)
------
+ << aggregation >> customers: Collection<Customer>
+ << association >> midtierCustomerService: MidtierCustomerService
----
+ create(accountCredentials: AccountCredentials): Customer | null
	-> AccountCredentials.verified
	-> MidtierCustomerService.create
	// existing CognitoUser.customerId: returns null without MidtierCustomerService.create
	// missing CognitoUser.customerId: submits Create Customer Request to Midtier
	// failure throws CustomerException with operation create, AccountCredentials and cause
	// returns the new Customer; Cart.setupAccount stores its id on the Cognito user
+ load(accountCredentials: AccountCredentials): Customer
	-> MidtierCustomerService.read
	-> AccountCredentials.signOut
	// failure throws CustomerException with operation load, AccountCredentials and cause
	// terminated billing or load failure signs out

## MidtierCustomerService

+ MidtierCustomerService()
------
----
+ validate(accountToken: AccountToken): string | Error
	// Midtier validates the JWT and returns its Cognito email claim
+ create(accountToken: AccountToken): string | Error
+ read(accountToken: AccountToken): MavenirCustomer | Error

## CustomerException

+ CustomerException(operation: CustomerOperation, accountCredentials: AccountCredentials, message: string, cause: Error)
------
+ << association >> operation: CustomerOperation
+ << association >> accountCredentials: AccountCredentials
+ message: string
+ cause: Error
----

## Identity

+ Identity(email: string, name: string, lastName: string, fullName: string, preferredName: string, expiryDate: string, dateOfBirth: string, idNationality: string, idNumber: string, idType: string, otherPhoneNumber: string)
------
+ email: string
+ name: string
+ lastName: string
+ fullName: string
+ preferredName: string
+ expiryDate: string
+ dateOfBirth: string
+ idNationality: string
+ idNumber: string
+ idType: string
+ otherPhoneNumber: string
----

## Address

+ Address(street: string, complement: string, city: string, parish: string, postalCode: string, country: string)
------
+ street: string
+ complement: string
+ city: string
+ parish: string
+ postalCode: string
+ country: string
----

## AccountCredentials

+ AccountCredentials(email: string, password: string, confirmPassword: string, validationCode: string, verified: boolean, token: AccountToken | null, customerId: string | null, validationCodeWasSent: boolean, canActivate: boolean, isUpdatable: boolean, isPersistable: boolean, resendMessage: string | null, errors: AccountCredentialsErrors, requirements: AccountCredentialRequirements)
	// from CognitoUser: email and verified come from the user; do not re-pass them
	// from email: password, confirmPassword, validationCode, verified optional
------
+ email: string
	// from CognitoUser.email when constructed from CognitoUser
+ password: string
+ confirmPassword: string
+ validationCode: string
+ verified: boolean
	// from CognitoUser.confirmed when constructed from CognitoUser
+ << association >> token: AccountToken | null
	// derived from CognitoUser.accountToken
+ customerId: string | null
	// derived from CognitoUser.customerId
+ validationCodeWasSent: boolean
	// true when CognitoUser.validationCodeSentAt is set
+ canActivate: boolean
	// true when a validation code has been sent
+ isUpdatable: boolean
+ isPersistable: boolean
	// true when missingRequirements is empty
+ resendMessage: string | null
+ << composition >> errors: AccountCredentialsErrors
+ << composition >> requirements: AccountCredentialRequirements
----
+ missingRequirements(): AccountCredentialRequirement[]
	// when AccountCredentials are updated
	// empty: credentials meet all requirements
	// otherwise the unmet AccountCredentialRequirement rows
+ register(): void
	-> AccountRepository.persistNewAccount
	// missingRequirements must be empty
	// already-registered email fails
	// writes CognitoUser onto these credentials; verified stays false until activate
+ activate(validationCode: ValidationCode): void
	-> AccountRepository.confirmAccount
	-> AccountRepository.authenticateAccount
	// requires validationCodeWasSent
	// unusable ValidationCode fails
	// reads CognitoUser.confirmed into verified
	// signs in after confirmation
+ authenticateAccount(): void
	-> AccountRepository.authenticateAccount
	// email required, email format, and password required must be met — otherwise no Cognito call
	// existing account holder signs in
	// writes signed-in CognitoUser, account token, and customerId onto these credentials
	// wrong password and unknown email fail with the same NotAuthorizedException
	// unconfirmed account returns CONFIRM_SIGN_UP
+ resendValidationCode(): void
	-> AccountRepository.resendAccountCode
	// throws ValidationCodeResendWaitException when 60 seconds have not elapsed
+ signOut(): void
	-> AmplifyService.signOut
+ storeCustomerId(customerId: string): CognitoUser
	-> AmplifyService.updateUserAttributes
	// failure throws CustomerException with operation storeCustomerId, these AccountCredentials and cause

## AccountRepository

+ AccountRepository(accountCredentials: Collection<AccountCredentials>, amplifyService: AmplifyService)
------
+ << aggregation >> accountCredentials: Collection<AccountCredentials>
+ << association >> amplifyService: AmplifyService
----
+ newAccount(credentials?: AccountCredentials): AccountCredentials
	// constructs AccountCredentials('') when none given
	// wires the repository onto the returned aggregate
+ persistNewAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
	-> AmplifyService.signUp
	// called by AccountCredentials.register
+ confirmAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
	-> AmplifyService.confirmSignUp
	// called by AccountCredentials.activate
+ authenticateAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
	-> AmplifyService.signIn
	// called by AccountCredentials.authenticateAccount and by activate after confirm
	// unverified: no AccountToken
	// wrong password or unknown email fails
+ resendAccountCode(accountCredentials: AccountCredentials): CognitoUser | null
	-> AmplifyService.resendSignUpCode
	// called by AccountCredentials.resendValidationCode

## AccountCredentialsErrors

+ AccountCredentialsErrors(register: string | null, signIn: string | null, validationCode: string | null)
------
+ register: string | null
+ signIn: string | null
+ validationCode: string | null
----

## ValidationCodeResendWaitException

+ ValidationCodeResendWaitException(availableAt: Date)
------
+ availableAt: Date
----

## AccountCredentialRequirement

+ AccountCredentialRequirement(field: string, requirement: string)
------
+ field: string
+ requirement: string
----

## AccountCredentialRequirements

+ AccountCredentialRequirements(emailRequired: AccountCredentialRequirement, emailFormat: AccountCredentialRequirement, passwordRequired: AccountCredentialRequirement, passwordLetters: AccountCredentialRequirement, passwordNumber: AccountCredentialRequirement, passwordSymbol: AccountCredentialRequirement, passwordLength: AccountCredentialRequirement, confirmRequired: AccountCredentialRequirement, confirmMismatch: AccountCredentialRequirement)
------
+ << association >> emailRequired: AccountCredentialRequirement
+ << association >> emailFormat: AccountCredentialRequirement
+ << association >> passwordRequired: AccountCredentialRequirement
+ << association >> passwordLetters: AccountCredentialRequirement
+ << association >> passwordNumber: AccountCredentialRequirement
+ << association >> passwordSymbol: AccountCredentialRequirement
+ << association >> passwordLength: AccountCredentialRequirement
+ << association >> confirmRequired: AccountCredentialRequirement
+ << association >> confirmMismatch: AccountCredentialRequirement
----

## AmplifyService

+ AmplifyService()
------
----
+ signUp(email: string, password: string): CognitoUser | Error
+ signIn(email: string, password: string): CognitoUser | Error
+ confirmSignUp(email: string, validationCode: ValidationCode): CognitoUser | Error
+ resendSignUp(email: string): ValidationCodeSend | Error
+ signOut(): void
+ fetchUserAttributes(email: string): CognitoUser | Error
	// My Paradise reads the Mavenir customer id from Cognito user attributes through Amplify
+ getUser(email: string): CognitoUser | null

## CognitoUser

+ CognitoUser(email: string, confirmed: boolean, customerId: string | null, validationCodeSentAt: Date | null, accountToken: AccountToken | null)
------
+ email: string
+ confirmed: boolean
+ customerId: string | null
+ validationCodeSentAt: Date | null
+ << association >> accountToken: AccountToken | null
----

## AccountToken

+ AccountToken(email: string, customerId: string | null)
------
+ email: string
+ customerId: string | null
----

## ValidationCode

+ ValidationCode(code: string)
------
+ code: string
----

## ValidationCodeSend

+ ValidationCodeSend(code: string, sentAt: Date, kind: initial | resend)
------
+ code: string
+ sentAt: Date
+ kind: initial | resend
----

## MavenirCustomer

+ MavenirCustomer(id: string, productOrder: MavenirProductOrder | null, billingAccount: MavenirBillingAccount | null, phoneVerified: boolean, waitingPsim: string | null, done: string | null, inquiryId: string | null, voucher: Voucher | null, shoppingCart: MavenirShoppingCart | null, contactMedium: ContactMedium, engagedParty: EngagedParty)
------
+ id: string
+ << association >> productOrder: MavenirProductOrder | null
	// from Subscription
+ << association >> billingAccount: MavenirBillingAccount | null
	// from Billing
+ phoneVerified: boolean
	// always phone_verified
+ waitingPsim: string | null
	// 'true' | 'false' | absent
	// true when pSIM no iccid via patchWaitingPsim
+ done: string | null
	// 'true' | absent
+ inquiryId: string | null
	// inquiryID
	// from PersonaInquiry.inquiryId when present
+ << association >> voucher: Voucher | null
	// JSON-encoded Voucher characteristic
	// Cart.applyVoucher writes this
	// absent after Cart.removeVoucher
+ << association >> shoppingCart: MavenirShoppingCart | null
+ << composition >> contactMedium: ContactMedium
+ << composition >> engagedParty: EngagedParty
----

## PortalGateway

+ PortalGateway()
------
----
+ create(email: string): MavenirCustomer | Error
	// email already in Mavenir fails
+ read(id: string): MavenirCustomer | Error
	// deliverPsim validates waitingPsim from this read
+ patchPhoneVerified(mavenirCustomerId: string): MavenirCustomer | Error
	// always writes phone_verified true
	// when Twilio approved
+ patchWaitingPsim(mavenirCustomerId: string, waitingPsim: boolean): MavenirCustomer | Error
	// true when pSIM no iccid (createOrder)
	// false after deliverPsim
+ patchProfile(mavenirCustomer: MavenirCustomer, engagedParty: EngagedParty, contactMedium: ContactMedium): MavenirCustomer | Error
	// EngagedParty names + birthDate + individualIdentification.validated
	// ContactMedium street + city + stateOrProvince + postCode + phoneNumber
	// contact country always Bermuda
	// inquiryID when mavenirCustomer.inquiryId is present
	// individualIdentification.identificationId already on another MavenirCustomer: conflict
	// invalid AccountToken fails
+ patchVoucher(mavenirCustomer: MavenirCustomer, voucher: Voucher): MavenirCustomer | Error
	// JSON-encoded Voucher as voucher characteristic
+ removeVoucher(mavenirCustomer: MavenirCustomer): MavenirCustomer | Error
	// removes voucher characteristic
+ patchDone(mavenirCustomerId: string): MavenirCustomer | Error
	// always writes done 'true'
	// Billing.createBilling / applyCredit live in # Billing
	// createOrder lives in # Subscription

## ContactMedium

+ ContactMedium(emailAddress: string, phoneNumber: string, street1: string, street2: string, city: string, stateOrProvince: string, postCode: string, country: string)
------
+ emailAddress: string
+ phoneNumber: string
+ street1: string
+ street2: string
+ city: string
+ stateOrProvince: string
+ postCode: string
+ country: string
	// always Bermuda
----

## EngagedParty

+ EngagedParty(givenName: string, familyName: string, preferredGivenName: string, birthDate: string, individualIdentification: IndividualIdentification)
------
+ givenName: string
+ familyName: string
+ preferredGivenName: string
	// preferredName when present; otherwise givenName
+ birthDate: string
+ << composition >> individualIdentification: IndividualIdentification
----

## IndividualIdentification

+ IndividualIdentification(identificationId: string, identificationType: string, issuingAuthority: string, validated: boolean, endDateTime: string)
------
+ identificationId: string
	// Identity.idNumber
+ identificationType: string
	// Identity.idType
+ issuingAuthority: string
	// Identity.idNationality
+ validated: boolean
	// Customer.verified
+ endDateTime: string
	// Identity.expiryDate
----

# KYC

## ProfileRequirement

+ ProfileRequirement(field: string, requirement: string)
------
+ field: string
+ requirement: string
----

## ProfileRequirements

+ ProfileRequirements(nameRequired: ProfileRequirement, lastNameRequired: ProfileRequirement, dateOfBirthRequired: ProfileRequirement, idNationalityRequired: ProfileRequirement, idTypeRequired: ProfileRequirement, idNumberRequired: ProfileRequirement, expiryRequired: ProfileRequirement, streetRequired: ProfileRequirement, parishRequired: ProfileRequirement, postalCodeRequired: ProfileRequirement)
------
+ << association >> nameRequired: ProfileRequirement
+ << association >> lastNameRequired: ProfileRequirement
+ << association >> dateOfBirthRequired: ProfileRequirement
+ << association >> idNationalityRequired: ProfileRequirement
+ << association >> idTypeRequired: ProfileRequirement
+ << association >> idNumberRequired: ProfileRequirement
+ << association >> expiryRequired: ProfileRequirement
+ << association >> streetRequired: ProfileRequirement
+ << association >> parishRequired: ProfileRequirement
+ << association >> postalCodeRequired: ProfileRequirement
----
+ missing(identity: Identity, address: Address): ProfileRequirement[]
	// when Identity / Address are updated
	// empty: Confirm ID may proceed
	// otherwise the unmet ProfileRequirement rows
+ validateInquiry(identity: Identity): string
	// Identity.idNumber
	// absent: inquiry required
	// present: already complete
+ mapInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer
	// maps PersonaInquiry onto Identity / Address
	// expiryDate from PersonaDocument or empty
	// PersonaInquiry.verified from status completed
	// Customer.verified stays false
	// failed inquiry: PersonaInquiry.verified false; Identity / Address may stay empty
+ storeFailedInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer
	// create failed
	// no field map
	// PersonaInquiry.verified false
	// Customer.verified stays false

# Cart

## Cart

+ Cart(customer: Customer, id: string, line: Line, bundle: Bundle | null, portability: Portability | null, voucher: Voucher | null, growthBook: GrowthBook, defaultPayment: boolean, orderSuccess: boolean | null, payUpFront: boolean | null)
------
+ << association >> customer: Customer
+ id: string
+ << composition >> line: Line
+ << composition >> bundle: Bundle | null
	// snapshot of selected Plan
	// set by Cart.pickPlan
	// catalog Plan changes do not rewrite this snapshot
+ << association >> portability: Portability | null
	// link to Porting
	// set by Cart.bringNumber
	// details and SMS live on Portability
+ << association >> voucher: Voucher | null
	// selected code until cook
	// null until applyVoucher
	// always null after removeVoucher
	// cook reads this code for Vouchera.redeem
+ << association >> growthBook: GrowthBook
	// flags Cart consults (sim, pay-up-front, attempts, roaming ticket)
+ defaultPayment: boolean
	// always true after storeOrderResult
+ orderSuccess: boolean | null
	// success from Store Order Result
+ payUpFront: boolean | null
	// stored when present
	// null on fail
----
+ setupAccount(): Customer | null
	-> CustomerRepository.create
	// existing Cognito customer id: CustomerRepository.load through Midtier
	// missing Cognito customer id: CustomerRepository.create through Midtier, then AccountCredentials.storeCustomerId
+ pickPlan(plan: Plan): Cart | CartErrors    //applyPlan
	-> PortalGateway.patchBundle
	// copies Plan onto Cart.bundle
	// Cart.bundle.plan is that Plan
	// first Select writes bundle onto empty cart
	// later Select replaces bundle
	// Get Data Freedom Upgrade is later Select
	// Get Review Plan is later Select
	// when the same Plan is already on cart: no patch
	// when portability is present: portability.planSelected is the Plan name
	// when patch fails: CartErrors.patch
+ pickNumber(availableNumber: AvailableNumber): Cart | CartErrors
	-> MsisdnInventoryRepository.reserve
	-> PortalGateway.patchMsisdn
	// previousId is always the current msisdn
	// portin is always false
	// premium selected id uses the same patchMsisdn hop
	// portability stays null
	// when reserve fails: CartErrors.reserve
	// when patch fails: CartErrors.patch
+ bringNumber(portability: Portability): Cart | CartErrors
	-> MsisdnInventoryRepository.list
	-> MsisdnInventoryRepository.reserve
	-> PortalGateway.patchPortability
	// always list size 1
	// previousId is always the current msisdn
	// portin is always true
	// msisdn is always the reserved temporary number
	// when reserve fails: CartErrors.reserve
	// when patch fails: CartErrors.patch
	// when portability fails: CartErrors.portability
	// when porting-2fa is off: no SMS
	// when porting-2fa is on: Twilio after patch
	// Portability.verified is false
	// Line.portability is the link to that Portability
+ applyVoucher(code: string): Cart | VoucherErrors
	-> Vouchera.read
	-> PortalGateway.patchVoucher
	// POST /customer/voucher
	// sets Cart.voucher
	// skip when voucher is present
	// auto-apply after Customer.confirmIdentity
	// session storage clear after auto-apply is intended
	// trial voucher requires a trial plan on cart
	// trial without trial plan: VoucherErrors.trial (500)
	// unknown code: VoucherErrors.invalid
	// expired: VoucherErrors.expired
	// redeemed: VoucherErrors.redeemed
	// intended: expired and redeemed are typed; live 400 has no body
	// other request failure: VoucherErrors.request
	// auto-apply rejection: VoucherErrors.notWorking
+ removeVoucher(): Cart | VoucherErrors
	-> PortalGateway.removeVoucher
	// DELETE /customer/voucher
	// voucher always null after success
+ checkout(payment: Payment): Cart | PaymentErrors
	-> FAC.read
	-> createOrder
	// payment is on the cart (Authorize Card)
	// Payment is not on the order
	// always GET /customer/payment/status/:transactionId
	// when completed: PortalGateway.createBilling on the Customer then Cart.createOrder
	// when failed and attempts under PAYMENT_ATTEMPTS: PaymentErrors.unverified; Payment.enter again
	// when failed and attempts equal PAYMENT_ATTEMPTS: Payment.recordFailed then Cart.createOrder
+ createOrder(customer: Customer): Cart
	-> PortalGateway.createProductOrder
	-> CaseRepository.open
	-> storeOrderResult
	// writes MavenirProductOrder (lives on Subscription after cook)
	// always POST /customer/order
	// no body
	// Redeem Voucher when cook: Vouchera.redeem writes VoucherRedemption on Subscription
	// Apply Credit when cook: Billing / PortalGateway.applyCredit
	// Create Order Ticket: CaseRepository.open in # Care
	// Then hop Store Order Result
+ storeOrderResult(customer: Customer, success: boolean, payUpFront: boolean | null, verified: boolean): Cart
	// always defaultPayment true
	// orderSuccess = success
	// payUpFront stored when present; null on fail
	// success: overwrite Customer.verified from order-body verified
	// order-body verified is Midtier verifiedResponse = KYC | Portability.portNumber | Plan.bypassVerified
	// fail: does not write verified
	// Then View Order Result when allSet else View Almost There
	// banners: orderUnprocessed / paymentUnverified / SimBanner iccidRequired

## OnboardingStep


## Bundle

+ Bundle(id: string, name: string, description: string, price: number, fees: number, totalPrice: number, features: any, plan: Plan)
------
+ id: string
	// Plan.id
+ name: string
+ description: string
+ price: number
+ fees: number
+ totalPrice: number
+ features: any
	// copied at pick time
+ << association >> plan: Plan
	// from Plans
	// where this snapshot came from
	// not composed; catalog Plan stays in Plans
----

## GrowthBook

+ GrowthBook(DISABLEEsim: string, DISABLEPsim: string, PAYUpFront: string, PAYMENTAttempts: string, ROAMINGPlanTicket: string)
------
+ DISABLEEsim: string
	// disable-esim
+ DISABLEPsim: string
	// disable-psim
+ PAYUpFront: string
	// pay-up-front
	// when off: invoicePayment
	// when on: upfrontPayment
+ PAYMENTAttempts: string
	// payment-attempts
	// always 3 on the scenario
	// live default is always 1
+ ROAMINGPlanTicket: string
	// roaming-plan-ticket
----
+ evaluate(key: string): boolean
	// DISABLE_ESIM or DISABLE_PSIM or PAY_UP_FRONT or ROAMING_PLAN_TICKET
	// esimFlagOn / esimFlagOff / psimFlagOn / psimFlagOff
	// when DISABLE_ESIM is true: wizard starts at physical SIM
	// when DISABLE_PSIM is true: hide pSIM card and dialog Nope
	// Flagged: live also hides Yay
	// when PAY_UP_FRONT is off: invoicePayment Time to add your payment
	// when PAY_UP_FRONT is on: upfrontPayment Complete your payment
+ value(key: string): number
	// always PAYMENT_ATTEMPTS
	// always 3 on the scenario
	// live default is always 1

## CartRepository

+ CartRepository(carts: Collection<Cart>, portalGateway: PortalGateway, customerRepository: CustomerRepository)
------
+ << aggregation >> carts: Collection<Cart>
+ << association >> portalGateway: PortalGateway
+ << association >> customerRepository: CustomerRepository
----
+ load(customer: Customer): Cart | null
	-> PortalGateway.read
	// always sets Customer.cart when a Cart exists
	// customer.id is always the MavenirCustomer id
	// when none: null
	// when Mavenir is unreachable: throws CartException with operation load, Customer and cause
+ create(customer: Customer): Cart
	-> PortalGateway.create
	// always sets Customer.cart
	// customer.id is always the MavenirCustomer id
	// when find is null
	// never when a cart already exists for that Customer
	// when a Cart already exists or Mavenir is unreachable: throws CartException with operation create, Customer and cause

## CartException

+ CartException(operation: CartOperation, customer: Customer, message: string, cause: Error)
------
+ << association >> operation: CartOperation
+ << association >> customer: Customer
+ message: string
+ cause: Error
----

## Voucher

+ Voucher(code: string, campaign: string, expired: boolean, redeemed: boolean)
------
+ code: string
+ campaign: string
+ expired: boolean
+ redeemed: boolean
----

## Vouchera

+ Vouchera()
------
----
+ read(code: string): Voucher | Error
	// unknown code: none
+ redeem(code: string, redeemerIdentifier: string, orderAmount: number): VoucherRedemption
	// Redeem Voucher
	// always POST vouchers/{code}/redeem
	// cook only
	// planIds match: orderAmount totalPrice then hop Apply Credit
	// no planIds: orderAmount 0.00 then cook
	// planIds miss: skip redeem then cook
	// flagged 5xx: success false; cook continues
	// writes Subscription.voucherRedemption

## MavenirShoppingCart

+ MavenirShoppingCart(id: string, customerId: string, lineCount: number, serviceProviderId: string, cartItem: bundle, productCharacteristic: ProductCharacteristic, channel: Channel)
------
+ id: string
+ customerId: string
+ lineCount: number
+ serviceProviderId: string
+ cartItem: bundle
	// Get Plan On Cart writes the bundle
	// Get Data Freedom Upgrade replaces the bundle
	// Get Review Plan replaces the bundle
	// always a bundle when patching MSISDN, ++portability++, SIM_TYPE, or ICCID
	// bundle cartItem already present for pickSim and pickIccid
+ << composition >> productCharacteristic: ProductCharacteristic
+ << composition >> channel: Channel
----

## PortalGateway

+ PortalGateway()
------
----
+ read(mavenirCustomerId: string): MavenirShoppingCart | Error
	// when none for that MavenirCustomer: none
+ create(mavenirCustomerId: string): MavenirShoppingCart | Error
	// always lineCount 1, empty cartItem, ON-BOARDING channel
	// never when a cart already exists for that MavenirCustomer
+ patchBundle(mavenirCustomerId: string, bundleId: string): MavenirShoppingCart | Error
	-> PortalGateway.list
	// always fetches the catalog bundle
	// always builds the bundle cartItem
	// always PATCH shopping cart
	// first Select writes bundle onto empty cart
	// later Select replaces bundle
	// Get Data Freedom Upgrade is later Select
	// Get Review Plan is later Select
	// when portability is present: planName is the bundle name
+ patchMsisdn(mavenirCustomerId: string, msisdn: string): MavenirShoppingCart | Error
	// always writes MSISDN ProductCharacteristic on the bundle cartItem
	// premium ++MSISDN++ is the same MSISDN ProductCharacteristic (no premium variant)
+ patchPortability(mavenirCustomerId: string, msisdn: string, characteristics: ProductCharacteristic[]): MavenirShoppingCart | Error
	// always writes MSISDN and ++portability++ ProductCharacteristic rows on the bundle cartItem
+ patchSimType(mavenirCustomerId: string, simType: string): MavenirShoppingCart | Error
	// always writes SIM_TYPE ProductCharacteristic on the bundle cartItem
	// Get Esim: value always 'eSIM'
	// Get Paradise Sim Card: value always 'pSIM'
	// no ICCID characteristic
	// bundle cartItem already present
+ patchIccid(mavenirCustomerId: string, iccid: string): MavenirShoppingCart | Error
	// always writes SIM_TYPE 'pSIM' and ICCID on the existing bundle cartItem
	// no sim-resource reserve
+ createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error
	// PATCH shoppingCart billing (pre-cook) then POST productOrderFromCart
	// SIM_TYPE 'pSIM' and ICCID already on bundle
	// Create Product Order cook
+ patchSubmitOrder(mavenirCustomerId: string): MavenirShoppingCart | Error
	// always writes submitOrder true on the bundle cartItem
	// when unverified no bypass no portability

## ProductCharacteristic

+ ProductCharacteristic(name: string, value: string)
------
+ name: string
+ value: string
----

## Channel

+ Channel(id: string, name: string, role: string)
------
+ id: string
+ name: string
+ role: string
----

# Plans

## Plan

+ Plan(id: string, name: string, price: number, isSellable: boolean, bypassVerified: boolean)
------
+ id: string
+ name: string
	// after Midtier map
+ price: number
+ isSellable: boolean
+ bypassVerified: boolean
	// dataFreedom essentials trial
----

## PlanRepository

+ PlanRepository(plans: Collection<Plan>, portalGateway: PortalGateway)
------
+ << aggregation >> plans: Collection<Plan>
+ << association >> portalGateway: PortalGateway
----
+ list(): Plan[]
	-> PortalGateway.list
	// Midtier maps
	// Get Data Freedom Upgrade uses the same list
	// Get Review Plan uses the same list
	// valid bundle ids: essentials, dataFreedom, ace, atlas, hiddenPromo
	// isBundle in live
	// isSellable when price > 0
	// hiddenPromo not sellable
	// name without the PROMO token
	// list order: price descending
	// Ace Best value is presentation

## MavenirProductOffering

+ MavenirProductOffering(id: string, name: string, isBundle: boolean, productOfferingPrice: any, bundledProductOffering: any)
------
+ id: string
+ name: string
+ isBundle: boolean
+ productOfferingPrice: any
+ bundledProductOffering: any
----

## PortalGateway

+ PortalGateway()
------
----
+ list(): MavenirProductOffering[]
	// always service provider 100000000
	// always channelName CRM

# Numbers and SIMs

## MsisdnInventoryRepository

+ MsisdnInventoryRepository(availableNumbers: Collection<AvailableNumber>, inventoryGateway: InventoryGateway)
------
+ << aggregation >> availableNumbers: Collection<AvailableNumber>
+ << association >> inventoryGateway: InventoryGateway
----
+ list(size: number, category: string): AvailableNumber[]
	-> InventoryGateway.list
	// always size 5 when picking a new number
	// always size 1 when bringing a number
	// new-number category always standard
	// listing premium inventory category always premium
	// always available to locked
+ search(searchTerm: SearchTerm): AvailableNumber[]
	-> InventoryGateway.search
	// when SearchTerm.converted is the pattern
	// always available to locked
+ reserve(id: string, previousId: string | null, portin: boolean): void | Error
	-> InventoryGateway.reserve
	// always locked to reserved
	// premium selected id: always locked to reserved
	// premium portin always false
	// category is always on list
	// when previousId is present, previousId must go reserved to available
	// when portin: kv_tempNumber

## IccidInventoryRepository

+ IccidInventoryRepository(availableSims: Collection<AvailableSim>, inventoryGateway: InventoryGateway)
------
+ << aggregation >> availableSims: Collection<AvailableSim>
+ << association >> inventoryGateway: InventoryGateway
----
+ read(id: string): AvailableSim | Error
	-> InventoryGateway.read
	// available only
	// empty or not-available is miss

## AvailableNumber

+ AvailableNumber(id: string)
------
+ id: string
----

## AvailableSim

+ AvailableSim(id: string)
------
+ id: string
----

## SearchTerm

+ SearchTerm(input: string, converted: string)
------
+ input: string
+ converted: string
----
+ convert(): string
	// when input is letters, converted is always keypad digits

## MavenirMsisdnResource

+ MavenirMsisdnResource(id: string, resourceStatus: string)
------
+ id: string
+ resourceStatus: string
	// always available, locked, or reserved
----

## InventoryGateway

+ InventoryGateway()
------
----
+ list(size: number, category: string): MavenirMsisdnResource[]
	// always size 5 when picking a new number
	// always size 1 when bringing a number
	// new-number category always standard
	// listing premium inventory category always premium
	// always available to locked
+ search(pattern: string): MavenirMsisdnResource[]
	// always available to locked
+ reserve(id: string, previousId: string | null, portin: boolean): void | Error
	// always locked to reserved
	// premium selected id: always locked to reserved
	// premium portin always false
	// category is always on list
	// when previousId is present, previousId must go reserved to available
	// when portin: kv_tempNumber
+ read(id: string): MavenirSimResource | Error
	// GET sim resource
	// when none: none
	// when not-available: none

## MavenirSimResource

+ MavenirSimResource(id: string, resourceStatus: string)
------
+ id: string
+ resourceStatus: string
	// available passes
----

# Porting

## Portability

+ Portability(donorOperator: string, portNumber: string, accountNumber: string | null, userType: string, accountType: string, device: string, planSelected: string, verified: boolean)
------
+ donorOperator: string
+ portNumber: string
+ accountNumber: string | null
+ userType: string
+ accountType: string
+ device: string
+ planSelected: string
	// always the cart bundle name
+ verified: boolean
	// false after Cart.bringNumber
	// true after Portability.verify
----
+ verify(portingSmsCode: PortingSmsCode): Portability | PortingErrors
	-> TwilioService.check
	-> PortalGateway.patchPhoneVerified
	// always Twilio check against portNumber
	// verified is always true after success
	// when Twilio is not approved: PortingErrors.portingSmsCode; verified stays false
	// when no portNumber: fails
+ resendSms(): void
	-> TwilioService.start
	// always Twilio send to portNumber
	// waits 30 seconds before another resend
	// when no portNumber: fails

## TwilioService

+ TwilioService()
------
----
+ start(portNumber: string): void
+ check(portNumber: string, portingSmsCode: PortingSmsCode): void | Error

## PortingSmsCode

+ PortingSmsCode(code: string)
------
+ code: string
----

## PortingErrors

+ PortingErrors(portingSmsCode: string | null)
------
+ portingSmsCode: string | null
----

# Payments

## Payment

+ Payment(paymentAttempts: number, paymentCharge: PaymentCharge, paymentErrors: PaymentErrors)
------
+ paymentAttempts: number
	// always compared to GrowthBook PAYMENT_ATTEMPTS
	// always null until enter
	// always html + transactionId after GET /customer/payment/auth
+ << composition >> paymentCharge: PaymentCharge
+ << composition >> paymentErrors: PaymentErrors
----
+ enter(cart: Cart): Payment | PaymentErrors
	-> GrowthBook.evaluate
	-> GrowthBook.value
	-> FAC.create
	// always GET /customer/payment/auth (Authorize Card)
	// always sets Payment.paymentIframe from html + transactionId
	// when PAY_UP_FRONT is off: invoicePayment title Time to add your payment; submit Checkout
	// when PAY_UP_FRONT is on: upfrontPayment title Complete your payment; submit Pay $N and subscribe
	// chargedValue is always Plan.price minus Cart.voucher discount; floor always 0
	// when flag on and no portability.portNumber and not trial voucher and chargedValue > 0: heads-up charged upfront
	// when flag on and chargedValue <= 0 and voucher discount >= 0: heads-up add credit
	// when load fails: PaymentErrors.load
	// PAYMENT_ATTEMPTS is always 3 on the scenario; live default is always 1
+ recordFailed(): Payment | PaymentErrors
	// always POST /customer/payment/failed with transactionId
	// always Then Cart.createOrder

## PaymentErrors

+ PaymentErrors(load: string | null, unverified: string | null)
------
+ load: string | null
	// always Failed to load — It's not you, it's me. Please refresh the page.
+ unverified: string | null
	// always We are unable to verify your card at this time.
	// when attempts under PAYMENT_ATTEMPTS
----

## PaymentCharge

+ PaymentCharge(title: string, submit: string, chargedValue: number)
------
+ title: string
	// when invoicePayment: Time to add your payment
	// when upfrontPayment: Complete your payment
+ submit: string
	// when invoicePayment: Checkout
	// when upfrontPayment: Pay $N and subscribe
+ chargedValue: number
	// always Plan.price minus Cart.voucher discount; floor always 0
	// table submit Pay $55 is leftover copy
	// FAC SPI auth TotalAmount $1 is FAC.create, not this chargedValue
----

## PaymentIframe

+ PaymentIframe(html: string, transactionId: string)
------
+ html: string
+ transactionId: string
----

## FAC

+ FAC()
------
----
+ create(customer: Customer): PaymentIframe | Error
	// Request Payment Authorization
	// Authorize Card (Mavenir)
	// always GET /customer/payment/auth
	// always POST fac/cards/spi/auth
	// stubAuth fixture: transactionId, TotalAmount 1, ON-BOARDING
	// returns html + transactionId
	// FAC timeout 3s no TransactionId: Error 504
+ read(customer: Customer, transactionId: string): PaymentStatus | Error
	// Read Tokenized Card Midtier + Mavenir
	// always GET /customer/payment/status/:transactionId
	// always GET getTokenizedCard
	// completed: status completed, reason APPROVED
	// failed: status failed, reason DECLINED; Midtier 504
	// optional 15s poll is Midtier retry, not a type

## PaymentStatus

+ PaymentStatus(status: string, reason: string)
------
+ status: string
	// completed | failed
+ reason: string
	// APPROVED | DECLINED
----

## ApplePayCertificate

+ ApplePayCertificate(keyIdentifier: string, certificate: string)
------
+ keyIdentifier: string
	// bmApplePayCert serial CertificateSerialNumber=08b3a3b7b23c2c56a625e95211699f0b
	// live JSON wraps serial in []
+ certificate: string
	// always certificates.bm whitespace stripped
----

## Apple

+ Apple()
------
----
+ read(): ApplePayCertificate
	// Provide Apple Pay Certificate
	// always POST /apple/cert getCert
	// always certificates.bm
	// Given CognitoUser vs live unauthenticated /apple

# Billing

## Billing

+ Billing(id: string, state: string, balance: string, defaultPayment: any, invoices: Invoice[], transactions: Transaction[])
------
+ id: string
+ state: string
	// active | suspended | terminated
+ balance: string
	// currentBalance on MavenirBillingAccount.accountBalance
+ defaultPayment: any
	// id, status, brand, lastFourDigits
	// Payments token after FAC; account.defaultPaymentMethod
+ << composition >> invoices: Invoice[]
+ << composition >> transactions: Transaction[]
----
+ create(customer: Customer): Billing | Error
	-> PortalGateway.createBilling
	// after Payment approved
	// POST /customer/billing
	// body transactionId ignored
	// 409 when customer.account already present
	// 201 empty body
+ applyCredit(): Billing
	-> PortalGateway.applyCredit
	// posts onto this account; uses Customer, Cart voucher, and VoucherRedemption already on the graph
	// cook after Vouchera.redeem, before productOrderFromCart
	// skip when VoucherRedemption.success false
	// then appears as Transaction / ArTransaction

## BillingRepository

+ BillingRepository(billings: Collection<Billing>, portalGateway: PortalGateway)
------
+ << aggregation >> billings: Collection<Billing>
+ << association >> portalGateway: PortalGateway
----
+ find(customer: Customer): Billing | null
	-> PortalGateway.read
	// Customer.account[0]
	// assembles invoices, transactions, defaultPayment, balance
+ create(customer: Customer): Billing | Error
	-> PortalGateway.createBilling

## Invoice

+ Invoice(invoiceId: string, billDate: string, dueDate: string, dueAmount: string, status: string)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string
----

## Transaction

+ Transaction(id: string, paymentDate: string, totalAmount: string)
------
+ id: string
+ paymentDate: string
+ totalAmount: string
----

## MavenirBillingAccount

+ MavenirBillingAccount(id: string, name: string, href: string, state: string, ratingType: string, billCycle: string, defaultPaymentMethod: any, relatedParty: any, accountBalance: any, creditAdjustments: MavenirCreditAdjustment[])
------
+ id: string
+ name: string
+ href: string
+ state: string
	// active | suspended | terminated
+ ratingType: string
	// always POSTPAID
+ billCycle: string
	// always 1st of every month
+ defaultPaymentMethod: any
+ relatedParty: any
+ accountBalance: any
	// currentBalance is Paradise Billing.balance
+ << composition >> creditAdjustments: MavenirCreditAdjustment[]
	// posted onto this account
	// PortalGateway.applyCredit
	// then listed as ArTransaction
----

## MavenirInvoice

+ MavenirInvoice(invoiceId: string, billDate: string, dueDate: string, dueAmount: string, status: string)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string
----

## ArTransaction

+ ArTransaction(id: string, status: string, totalAmount: string, paymentDate: string)
------
+ id: string
+ status: string
+ totalAmount: string
+ paymentDate: string
----

## MavenirCreditAdjustment

+ MavenirCreditAdjustment(amount: number, unit: string, glCode: string, transactionType: string, transactionSubType: string, serviceProviderId: string, reason: string)
------
+ amount: number
+ unit: string
	// always BMD
+ glCode: string
	// always 100004
+ transactionType: string
	// always creditAdjustment
+ transactionSubType: string
	// always Credit
+ serviceProviderId: string
	// always 100000000
+ reason: string
	// always $ + Voucher.campaign
----

## PortalGateway

+ PortalGateway()
------
----
+ createBilling(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error
	// POST v1/billingAccount?customerId=
	// 409 when account already present
	// 201 no body
+ read(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error
	// GET v1/billingAccount/{accountId}
+ readInvoices(mavenirCustomer: MavenirCustomer): MavenirInvoice[]
	// GET v1/invoice/history
+ readTransactions(mavenirCustomer: MavenirCustomer): ArTransaction[]
	// GET allARTransaction
+ readInvoicePdf(billingAccountId: string, invoiceId: string): void
	// GET v1/invoice/invoicePDF
+ applyCredit(mavenirCustomer: MavenirCustomer, creditAdjustment: MavenirCreditAdjustment): MavenirCreditAdjustment
	// POST allARTransaction
	// cook after Vouchera.redeem, before productOrderFromCart
	// skip when VoucherRedemption.success false

# Subscription

## Line

+ Line(msisdn: string | null, simType: SimType | null, iccid: string | null, availableNumbers: string[], portability: Portability | null)
------
+ msisdn: string | null
+ << association >> simType: SimType | null
	// SimType.Esim | SimType.Psim
	// null until selectSim or attachIccid
+ iccid: string | null
	// null until attachIccid
+ availableNumbers: string[]
+ << association >> portability: Portability | null
----
+ selectSim(simType: SimType): void | Error
	-> ShoppingCartGateway.patchCartWithSim
	// when the line already has that SIM type: no patch
	// Request a Paradise SIM card: SimType.Psim, no ICCID
	// when patch fails: Error
+ attachIccid(iccid: string): void | Error
	-> MsisdnRepository.read
	-> ShoppingCartGateway.patchCartWithSim
	// always SimType.Psim
	// when whitespace: Error; no inventory or patch
	// when read miss: Error
+ activateSim(iccid: string): void | Error
	-> Line.attachIccid
	-> PortalGateway.createPsimDeliveredOrder
	// waiting pSIM must already be Active
	// absent waiting pSIM: Error
	// waiting pSIM Cleared: Error

## Subscription

+ Subscription(id: string, status: string, line: Line, bundle: Bundle, usage: Usage, portability: Portability | null, productOrder: MavenirProductOrder | null, voucherRedemption: VoucherRedemption | null)
------
+ id: string
	// MavenirAgreement.id
+ status: string
	// active | suspended | terminated | pendingActive
+ << composition >> line: Line
	// number, simType, iccid, portability live on Line
+ << composition >> bundle: Bundle
	// from Cart
	// same snapshot pickPlan wrote
	// agreementItem.product / productOffering
+ << composition >> usage: Usage
+ << association >> portability: Portability | null
	// from Porting
	// from Cart.portability when they brought a number
+ << association >> productOrder: MavenirProductOrder | null
	// Cart.createOrder / PortalGateway.createProductOrder
+ << association >> voucherRedemption: VoucherRedemption | null
	// cook: Vouchera.redeem on Cart.voucher
----
+ changePlan(plan: Plan): Subscription | Error
	-> PortalGateway.changePlan

## Usage

+ Usage()
------
----

## SubscriptionRepository

+ SubscriptionRepository(subscriptions: Collection<Subscription>, portalGateway: PortalGateway, ccsGateway: CcsGateway)
------
+ << aggregation >> subscriptions: Collection<Subscription>
+ << association >> portalGateway: PortalGateway
+ << association >> ccsGateway: CcsGateway
----
+ list(customer: Customer): Subscription[]
	-> PortalGateway.listAgreements
	-> CcsGateway.readUsage
	// sets Customer.subscriptions
	// active and suspended
	// bundle from latest agreementItem.product
	// number / simType from characteristics

## MavenirAgreement

+ MavenirAgreement(id: string, status: string, agreementType: string, initialDate: string, characteristic: any, agreementItem: MavenirAgreementProduct[])
------
+ id: string
+ status: string
+ agreementType: string
+ initialDate: string
+ characteristic: any
	// MSISDN, SIM_TYPE
+ << composition >> agreementItem: MavenirAgreementProduct[]
----

## MavenirAgreementProduct

+ MavenirAgreementProduct(id: string, name: string, description: string, orderDate: any, productPrice: any)
------
+ id: string
+ name: string
+ description: string
+ orderDate: any
+ productPrice: any
----

## MavenirProductOrder

+ MavenirProductOrder(id: string)
------
+ id: string
----

## MsisdnDataUsage

+ MsisdnDataUsage()
------
----

## PortalGateway

+ PortalGateway()
------
----
+ listAgreements(mavenirCustomerId: string): MavenirAgreement[]
	// GET agreementManagement/agreement
+ createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error
	-> GrowthBook.evaluate
	-> Vouchera.redeem
	-> Billing.applyCredit
	-> PortalGateway.createProductOrder
	-> PortalGateway.patchSubmitOrder
	-> patchDone
	-> patchWaitingPsim
	// Create Product Order
	// always POST /customer/order
	// no body
	// 409 when done is truthy
	// when verified or portability or Plan.bypassVerified: cook
	// when cook: Vouchera.redeem then Billing.applyCredit then productOrderFromCart
	// when unverified no bypass no portability: patchSubmitOrder
	// always patchDone
	// waitingPsim true when pSIM no iccid
	// 201 { payUpFront, verified }
+ changePlan(mavenirCustomerId: string, plan: Plan): MavenirAgreement | Error

## CcsGateway

+ CcsGateway()
------
----
+ readUsage(msisdn: string, planName: string): MsisdnDataUsage
	// GET ccsGateway/subscriber/serviceUsage/.../subscribers/{msisdn}

## VoucherRedemption

+ VoucherRedemption(success: boolean, discountAmount: number, totalAmount: number)
------
+ success: boolean
	// flagged 5xx: false; cook continues
+ discountAmount: number
+ totalAmount: number
----

# Care

## Case

+ Case(subject: string)
------
+ subject: string
	// GWT seven: ID Verification Required | SIM Delivery Required | ID Verification Required and SIM Delivery Required | Promotional trial | Portability Required | Payment failed | Roaming plan - New Subscription
	// cardAdditionFailed config out of GWT
----

## CaseRepository

+ CaseRepository(cases: Collection<Case>, zendesk: Zendesk)
------
+ << aggregation >> cases: Collection<Case>
+ << association >> zendesk: Zendesk
----
+ open(customer: Customer, subject: string): Case
	-> Zendesk.create
	// Create Order Ticket
	// requesterName Identity.fullName
	// requesterEmail Identity.email

## Ticket

+ Ticket(id: string, subject: string, requesterName: string, requesterEmail: string)
------
+ id: string
+ subject: string
+ requesterName: string
	// Identity.fullName
+ requesterEmail: string
	// Identity.email
----

## Zendesk

+ Zendesk()
------
----
+ create(customer: Customer, subject: string): Ticket
	// always POST tickets.json
	// seven GWT subjects
	// trial may also create id / pSim / idAndPsim
	// cardAdditionFailed config out of GWT
	// requesterName Identity.fullName
	// requesterEmail Identity.email

## PersonaInquiry

+ PersonaInquiry(inquiryId: string, status: string, verified: boolean, email: string, nameFirst: string, nameLast: string, birthdate: string, selectedCountryCode: string, identificationNumber: string, identificationClass: string, expiryDate: string, addressStreet1: string, addressStreet2: string, addressCity: string, addressSubdivision: string, addressPostalCode: string, addressCountryCode: string, currentGovernmentId: string | null)
------
+ inquiryId: string
+ status: string
+ verified: boolean
+ email: string
+ nameFirst: string
+ nameLast: string
+ birthdate: string
+ selectedCountryCode: string
+ identificationNumber: string
+ identificationClass: string
+ expiryDate: string
+ addressStreet1: string
+ addressStreet2: string
+ addressCity: string
+ addressSubdivision: string
+ addressPostalCode: string
+ addressCountryCode: string
+ currentGovernmentId: string | null
----

## PersonaDocument

+ PersonaDocument(documentId: string, expirationDate: string, email: string)
------
+ documentId: string
+ expirationDate: string
+ email: string
----

## PersonaService

+ PersonaService()
------
----
+ create(customer: Customer): PersonaInquiry
	// wraps a Persona inquiry with inquiryId + status + fields
	// email pre-filled from Customer.identity.email
	// create failed: status failed, verified false
	// Verify Later: create is not called
+ readDocument(documentId: string): PersonaDocument | Error
	// missing document: not found
	// email mismatch: unauthorized
