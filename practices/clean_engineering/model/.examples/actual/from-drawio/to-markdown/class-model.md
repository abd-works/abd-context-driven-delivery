# Customer

## Customer

+ Customer(accountCredentials: AccountCredentials)
------
+ id: string
+ verified: boolean
+ << composition >> identity: Identity
+ << composition >> address: Address
+ << association >> accountCredentials: AccountCredentials
+ << association >> cart: Cart | null
+ << association >> billing: Billing | null
+ << association >> subscriptions: Subscription[]
+ << association >> personaInquiry: PersonaInquiry | null
----
+ confirmIdentity(): Customer

## CustomerRepository

+ CustomerRepository(...)
------
+ << aggregation >> customers: Collection<Customer>
+ << association >> midtierCustomerService: MidtierCustomerService
----
+ create(accountCredentials: AccountCredentials): Customer | null
+ load(accountCredentials: AccountCredentials): Customer

## MidtierCustomerService

+ MidtierCustomerService(...)
------
----
+ validate(accountToken: AccountToken): string | Error
+ create(accountToken: AccountToken): string | Error
+ read(accountToken: AccountToken): MavenirCustomer | Error

## CustomerException

+ CustomerException(...)
------
+ operation: CustomerOperation
+ accountCredentials: AccountCredentials
+ message: string
+ cause: Error
----

## Identity

+ Identity(...)
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

+ Address(...)
------
+ street: string
+ complement: string
+ city: string
+ parish: string
+ postalCode: string
+ country: string
----

## AccountCredentials

+ AccountCredentials(emailOrCognitoUser: string | CognitoUser)
------
+ email: string
+ password: string
+ confirmPassword: string
+ validationCode: string
+ verified: boolean
+ token: AccountToken | null
+ customerId: string | null
+ validationCodeWasSent: boolean
+ canActivate: boolean
+ isUpdatable: boolean
+ isPersistable: boolean
+ resendMessage: string | null
+ << composition >> errors: AccountCredentialsErrors
+ << composition >> requirements: AccountCredentialRequirements
----
+ missingRequirements(): AccountCredentialRequirement[]
+ register(): void
+ activate(validationCode: ValidationCode): void
+ authenticateAccount(): void
+ resendValidationCode(): void
+ signOut(): void
+ storeCustomerId(customerId: string): CognitoUser

## AccountRepository

+ AccountRepository(...)
------
+ << aggregation >> accountCredentials: Collection<AccountCredentials>
+ << association >> amplifyService: AmplifyService
----
+ newAccount(credentials?: AccountCredentials): AccountCredentials
+ persistNewAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
+ confirmAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
+ authenticateAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors
+ resendAccountCode(accountCredentials: AccountCredentials): CognitoUser | null

## AccountCredentialsErrors

+ AccountCredentialsErrors(...)
------
+ register: string | null
+ signIn: string | null
+ validationCode: string | null
----

## ValidationCodeResendWaitException

+ ValidationCodeResendWaitException(...)
------
+ availableAt: Date
----

## AccountCredentialRequirement

+ AccountCredentialRequirement(...)
------
+ field: string
+ requirement: string
----

## AccountCredentialRequirements

+ AccountCredentialRequirements(...)
------
+ emailRequired: AccountCredentialRequirement
+ emailFormat: AccountCredentialRequirement
+ passwordRequired: AccountCredentialRequirement
+ passwordLetters: AccountCredentialRequirement
+ passwordNumber: AccountCredentialRequirement
+ passwordSymbol: AccountCredentialRequirement
+ passwordLength: AccountCredentialRequirement
+ confirmRequired: AccountCredentialRequirement
+ confirmMismatch: AccountCredentialRequirement
----

## AmplifyService

+ AmplifyService(...)
------
----
+ signUp(email: string, password: string): CognitoUser | Error
+ signIn(email: string, password: string): CognitoUser | Error
+ confirmSignUp(email: string, validationCode: ValidationCode): CognitoUser | Error
+ resendSignUp(email: string): ValidationCodeSend | Error
+ signOut(): void
+ fetchUserAttributes(email: string): CognitoUser | Error
+ getUser(email: string): CognitoUser | null

## CognitoUser

+ CognitoUser(...)
------
+ email: string
+ confirmed: boolean
+ customerId: string | null
+ validationCodeSentAt: Date | null
+ << association >> accountToken: AccountToken | null
----

## AccountToken

+ AccountToken(...)
------
+ email: string
+ customerId: string | null
----

## ValidationCode

+ ValidationCode(...)
------
+ code: string
----

## ValidationCodeSend

+ ValidationCodeSend(...)
------
+ code: string
+ sentAt: Date
+ kind: initial | resend
----

## MavenirCustomer

+ MavenirCustomer(...)
------
+ id: string
+ << association >> productOrder: MavenirProductOrder | null
+ << association >> billingAccount: MavenirBillingAccount | null
+ phoneVerified: boolean
+ waitingPsim: string | null
+ done: string | null
+ inquiryId: string | null
+ voucher: Voucher | null
+ << association >> shoppingCart: MavenirShoppingCart | null
+ << composition >> contactMedium: ContactMedium
+ << composition >> engagedParty: EngagedParty
----

## PortalGateway

+ PortalGateway(...)
------
----
+ create(email: string): MavenirCustomer | Error
+ read(id: string): MavenirCustomer | Error
+ patchPhoneVerified(mavenirCustomerId: string): MavenirCustomer | Error
+ patchWaitingPsim(mavenirCustomerId: string, waitingPsim: boolean): MavenirCustomer | Error
+ patchProfile(mavenirCustomer: MavenirCustomer, engagedParty: EngagedParty, contactMedium: ContactMedium): MavenirCustomer | Error
+ patchVoucher(mavenirCustomer: MavenirCustomer, voucher: Voucher): MavenirCustomer | Error
+ removeVoucher(mavenirCustomer: MavenirCustomer): MavenirCustomer | Error
+ patchDone(mavenirCustomerId: string): MavenirCustomer | Error

## ContactMedium

+ ContactMedium(...)
------
+ emailAddress: string
+ phoneNumber: string
+ street1: string
+ street2: string
+ city: string
+ stateOrProvince: string
+ postCode: string
+ country: string
----

## EngagedParty

+ EngagedParty(...)
------
+ givenName: string
+ familyName: string
+ preferredGivenName: string
+ birthDate: string
+ << composition >> individualIdentification: IndividualIdentification
----

## IndividualIdentification

+ IndividualIdentification(...)
------
+ identificationId: string
+ identificationType: string
+ issuingAuthority: string
+ validated: boolean
+ endDateTime: string
----

# KYC

## ProfileRequirement

+ ProfileRequirement(...)
------
+ field: string
+ requirement: string
----

## ProfileRequirements

+ ProfileRequirements(...)
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
+ validateInquiry(identity: Identity): string
+ mapInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer
+ storeFailedInquiry(customer: Customer, personaInquiry: PersonaInquiry): Customer

# Cart

## Cart

+ Cart(...)
------
+ << association >> customer: Customer
+ id: string
+ << composition >> line: Line
+ << composition >> bundle: Bundle | null
+ << association >> portability: Portability | null
+ << association >> voucher: Voucher | null
+ << association >> growthBook: GrowthBook
+ defaultPayment: boolean
+ orderSuccess: boolean | null
+ payUpFront: boolean | null
----
+ setupAccount(): Customer | null
+ pickPlan(plan: Plan): Cart | CartErrors    //applyPlan
+ pickNumber(availableNumber: AvailableNumber): Cart | CartErrors
+ bringNumber(portability: Portability): Cart | CartErrors
+ applyVoucher(code: string): Cart | VoucherErrors
+ removeVoucher(): Cart | VoucherErrors
+ checkout(payment: Payment): Cart | PaymentErrors
+ createOrder(customer: Customer): Cart
+ storeOrderResult(customer: Customer, success: boolean, payUpFront: boolean | null, verified: boolean): Cart

## OnboardingStep


## Bundle

+ Bundle(...)
------
+ id: string
+ name: string
+ description: string
+ price: number
+ fees: number
+ totalPrice: number
+ features
+ << association >> plan: Plan
----

## GrowthBook

+ GrowthBook(...)
------
+ DISABLE_ESIM: string
+ DISABLE_PSIM: string
+ PAY_UP_FRONT: string
+ PAYMENT_ATTEMPTS: string
+ ROAMING_PLAN_TICKET: string
----
+ evaluate(key: string): boolean
+ value(key: string): number

## CartRepository

+ CartRepository(...)
------
+ << aggregation >> carts: Collection<Cart>
+ << association >> portalGateway: PortalGateway
+ << association >> customerRepository: CustomerRepository
----
+ load(customer: Customer): Cart | null
+ create(customer: Customer): Cart

## CartException

+ CartException(...)
------
+ operation: CartOperation
+ customer: Customer
+ message: string
+ cause: Error
----

## Voucher

+ Voucher(...)
------
+ code: string
+ campaign: string
+ expired: boolean
+ redeemed: boolean
----

## Vouchera

+ Vouchera(...)
------
----
+ read(code: string): Voucher | Error
+ redeem(code: string, redeemerIdentifier: string, orderAmount: number): VoucherRedemption

## MavenirShoppingCart

+ MavenirShoppingCart(...)
------
+ id: string
+ customerId: string
+ lineCount: number
+ serviceProviderId: string
+ cartItem: bundle
+ << composition >> productCharacteristic: ProductCharacteristic
+ << composition >> channel: Channel
----

## PortalGateway

+ PortalGateway(...)
------
----
+ read(mavenirCustomerId: string): MavenirShoppingCart | Error
+ create(mavenirCustomerId: string): MavenirShoppingCart | Error
+ patchBundle(mavenirCustomerId: string, bundleId: string): MavenirShoppingCart | Error
+ patchMsisdn(mavenirCustomerId: string, msisdn: string): MavenirShoppingCart | Error
+ patchPortability(mavenirCustomerId: string, msisdn: string, characteristics: ProductCharacteristic[]): MavenirShoppingCart | Error
+ patchSimType(mavenirCustomerId: string, simType: string): MavenirShoppingCart | Error
+ patchIccid(mavenirCustomerId: string, iccid: string): MavenirShoppingCart | Error
+ createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error
+ patchSubmitOrder(mavenirCustomerId: string): MavenirShoppingCart | Error

## ProductCharacteristic

+ ProductCharacteristic(...)
------
+ name: string
+ value: string
----

## Channel

+ Channel(...)
------
+ id: string
+ name: string
+ role: string
----

# Plans

## Plan

+ Plan(...)
------
+ id: string
+ name: string
+ price: number
+ isSellable: boolean
+ bypassVerified: boolean
----

## PlanRepository

+ PlanRepository(...)
------
+ << aggregation >> plans: Collection<Plan>
+ << association >> portalGateway: PortalGateway
----
+ list(): Plan[]

## MavenirProductOffering

+ MavenirProductOffering(...)
------
+ id: string
+ name: string
+ isBundle: boolean
+ productOfferingPrice
+ bundledProductOffering
----

## PortalGateway

+ PortalGateway(...)
------
----
+ list(): MavenirProductOffering[]

# Numbers and SIMs

## MsisdnInventoryRepository

+ MsisdnInventoryRepository(...)
------
+ << aggregation >> availableNumbers: Collection<AvailableNumber>
+ << association >> inventoryGateway: InventoryGateway
----
+ list(size: number, category: string): AvailableNumber[]
+ search(searchTerm: SearchTerm): AvailableNumber[]
+ reserve(id: string, previousId: string | null, portin: boolean): void | Error

## IccidInventoryRepository

+ IccidInventoryRepository(...)
------
+ << aggregation >> availableSims: Collection<AvailableSim>
+ << association >> inventoryGateway: InventoryGateway
----
+ read(id: string): AvailableSim | Error

## AvailableNumber

+ AvailableNumber(...)
------
+ id: string
----

## AvailableSim

+ AvailableSim(...)
------
+ id: string
----

## SearchTerm

+ SearchTerm(...)
------
+ input: string
+ converted: string
----
+ convert(): string

## MavenirMsisdnResource

+ MavenirMsisdnResource(...)
------
+ id: string
+ resourceStatus: string
----

## InventoryGateway

+ InventoryGateway(...)
------
----
+ list(size: number, category: string): MavenirMsisdnResource[]
+ search(pattern: string): MavenirMsisdnResource[]
+ reserve(id: string, previousId: string | null, portin: boolean): void | Error
+ read(id: string): MavenirSimResource | Error

## MavenirSimResource

+ MavenirSimResource(...)
------
+ id: string
+ resourceStatus: string
----

# Porting

## Portability

+ Portability(...)
------
+ donorOperator: string
+ portNumber: string
+ accountNumber: string | null
+ userType: string
+ accountType: string
+ device: string
+ planSelected: string
+ verified: boolean
----
+ verify(portingSmsCode: PortingSmsCode): Portability | PortingErrors
+ resendSms(): void

## TwilioService

+ TwilioService(...)
------
----
+ start(portNumber: string): void
+ check(portNumber: string, portingSmsCode: PortingSmsCode): void | Error

## PortingSmsCode

+ PortingSmsCode(...)
------
+ code: string
----

## PortingErrors

+ PortingErrors(...)
------
+ portingSmsCode: string | null
----

# Payments

## Payment

+ Payment(...)
------
+ paymentAttempts: number
+ << composition >> paymentCharge: PaymentCharge
+ << composition >> paymentErrors: PaymentErrors
----
+ enter(cart: Cart): Payment | PaymentErrors
+ recordFailed(): Payment | PaymentErrors

## PaymentErrors

+ PaymentErrors(...)
------
+ load: string | null
+ unverified: string | null
----

## PaymentCharge

+ PaymentCharge(...)
------
+ title: string
+ submit: string
+ chargedValue: number
----

## PaymentIframe

+ PaymentIframe(...)
------
+ html: string
+ transactionId: string
----

## FAC

+ FAC(...)
------
----
+ create(customer: Customer): PaymentIframe | Error
+ read(customer: Customer, transactionId: string): PaymentStatus | Error

## PaymentStatus

+ PaymentStatus(...)
------
+ status: string
+ reason: string
----

## ApplePayCertificate

+ ApplePayCertificate(...)
------
+ keyIdentifier: string
+ certificate: string
----

## Apple

+ Apple(...)
------
----
+ read(): ApplePayCertificate

# Billing

## Billing

+ Billing(...)
------
+ id: string
+ state: string
+ balance: string
+ defaultPayment
+ << composition >> invoices: Invoice[]
+ << composition >> transactions: Transaction[]
----
+ create(customer: Customer): Billing | Error
+ applyCredit(): Billing

## BillingRepository

+ BillingRepository(...)
------
+ << aggregation >> billings: Collection<Billing>
+ << association >> portalGateway: PortalGateway
----
+ find(customer: Customer): Billing | null
+ create(customer: Customer): Billing | Error

## Invoice

+ Invoice(...)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string
----

## Transaction

+ Transaction(...)
------
+ id: string
+ paymentDate: string
+ totalAmount: string
----

## MavenirBillingAccount

+ MavenirBillingAccount(...)
------
+ id: string
+ name: string
+ href: string
+ state: string
+ ratingType: string
+ billCycle: string
+ defaultPaymentMethod
+ relatedParty
+ accountBalance
+ << composition >> creditAdjustments: MavenirCreditAdjustment[]
----

## MavenirInvoice

+ MavenirInvoice(...)
------
+ invoiceId: string
+ billDate: string
+ dueDate: string
+ dueAmount: string
+ status: string
----

## ArTransaction

+ ArTransaction(...)
------
+ id: string
+ status: string
+ totalAmount: string
+ paymentDate: string
----

## MavenirCreditAdjustment

+ MavenirCreditAdjustment(...)
------
+ amount: number
+ unit: string
+ glCode: string
+ transactionType: string
+ transactionSubType: string
+ serviceProviderId: string
+ reason: string
----

## PortalGateway

+ PortalGateway(...)
------
----
+ createBilling(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error
+ read(mavenirCustomer: MavenirCustomer): MavenirBillingAccount | Error
+ readInvoices(mavenirCustomer: MavenirCustomer): MavenirInvoice[]
+ readTransactions(mavenirCustomer: MavenirCustomer): ArTransaction[]
+ readInvoicePdf(billingAccountId: string, invoiceId: string)
+ applyCredit(mavenirCustomer: MavenirCustomer, creditAdjustment: MavenirCreditAdjustment): MavenirCreditAdjustment

# Subscription

## Line

+ Line(...)
------
+ msisdn: string | null
+ simType: SimType | null
+ iccid: string | null
+ availableNumbers: string[]
+ << association >> portability: Portability | null
----
+ selectSim(simType: SimType): void | Error
+ attachIccid(iccid: string): void | Error
+ activateSim(iccid: string): void | Error

## Subscription

+ Subscription(...)
------
+ id: string
+ status: string
+ << composition >> line: Line
+ << composition >> bundle: Bundle
+ << composition >> usage: Usage
+ << association >> portability: Portability | null
+ << association >> productOrder: MavenirProductOrder | null
+ << association >> voucherRedemption: VoucherRedemption | null
----
+ changePlan(plan: Plan): Subscription | Error

## Usage

+ Usage(...)
------
----

## SubscriptionRepository

+ SubscriptionRepository(...)
------
+ << aggregation >> subscriptions: Collection<Subscription>
+ << association >> portalGateway: PortalGateway
+ << association >> ccsGateway: CcsGateway
----
+ list(customer: Customer): Subscription[]

## MavenirAgreement

+ MavenirAgreement(...)
------
+ id: string
+ status: string
+ agreementType: string
+ initialDate: string
+ characteristic
+ << composition >> agreementItem: MavenirAgreementProduct[]
----

## MavenirAgreementProduct

+ MavenirAgreementProduct(...)
------
+ id: string
+ name: string
+ description: string
+ orderDate
+ productPrice
----

## MavenirProductOrder

+ MavenirProductOrder(...)
------
+ id: string
----

## MsisdnDataUsage

+ MsisdnDataUsage(...)
------
----

## PortalGateway

+ PortalGateway(...)
------
----
+ listAgreements(mavenirCustomerId: string): MavenirAgreement[]
+ createProductOrder(mavenirCustomerId: string): MavenirProductOrder | Error
+ changePlan(mavenirCustomerId: string, plan: Plan): MavenirAgreement | Error

## CcsGateway

+ CcsGateway(...)
------
----
+ readUsage(msisdn: string, planName: string): MsisdnDataUsage

## VoucherRedemption

+ VoucherRedemption(...)
------
+ success: boolean
+ discountAmount: number
+ totalAmount: number
----

# Care

## Case

+ Case(...)
------
+ subject: string
----

## CaseRepository

+ CaseRepository(...)
------
+ << aggregation >> cases: Collection<Case>
+ << association >> zendesk: Zendesk
----
+ open(customer: Customer, subject: string): Case

## Ticket

+ Ticket(...)
------
+ id: string
+ subject: string
+ requesterName: string
+ requesterEmail: string
----

## Zendesk

+ Zendesk(...)
------
----
+ create(customer: Customer, subject: string): Ticket

## PersonaInquiry

+ PersonaInquiry(...)
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

+ PersonaDocument(...)
------
+ documentId: string
+ expirationDate: string
+ email: string
----

## PersonaService

+ PersonaService(...)
------
----
+ create(customer: Customer): PersonaInquiry
+ readDocument(documentId: string): PersonaDocument | Error
