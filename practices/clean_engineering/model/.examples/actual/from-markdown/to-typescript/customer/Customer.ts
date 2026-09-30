class Customer {
  // derived from accountCredentials.customerId when not passed
  // empty string when credentials have no customer id
  id: string;
  // persisted KYC on the party
  // always false after ProfileRequirements.mapInquiry / storeFailedInquiry
  // flips true on confirmIdentity when PersonaInquiry.verified
  // Cart.storeOrderResult overwrites from order-body verified
  // order-body verified is Midtier verifiedResponse = KYC | Portability.portNumber | Plan.bypassVerified
  // fail Cart.storeOrderResult does not write verified
  verified: boolean;
  // << composition >>
  // derived from accountCredentials.email when not passed
  identity: Identity;
  // << composition >>
  // empty Address when not passed
  address: Address;
  // << association >>
  // required constructor argument; own aggregate, not composed
  accountCredentials: AccountCredentials;
  // << association >>
  // from Cart
  // 0..1
  // set by CartRepository.find / create
  cart: Cart | null;
  // << association >>
  // from Billing
  // 0..1
  // Mavenir customer.account[0]
  billing: Billing | null;
  // << association >>
  // from Subscription
  // 0..*
  // each line is one Subscription after cook
  subscriptions: Subscription[];
  // << association >>
  // from Care
  // 0..1
  personaInquiry: PersonaInquiry | null;

  constructor(id: string, verified: boolean, identity: Identity, address: Address, accountCredentials: AccountCredentials, cart: Cart | null, billing: Billing | null, subscriptions: Subscription[], personaInquiry: PersonaInquiry | null) {
    // canonical form: new Customer(accountCredentials)
    // id, identity, and address are derived from accountCredentials when not passed
    // repository passes explicit id / identity / address when Mavenir has richer data
    this.id = id;
    this.verified = verified;
    this.identity = identity;
    this.address = address;
    this.accountCredentials = accountCredentials;
    this.cart = cart;
    this.billing = billing;
    this.subscriptions = subscriptions;
    this.personaInquiry = personaInquiry;
  }

  confirmIdentity(): Customer {
    // AccountToken already on the wrap
    // maps Identity / Address onto EngagedParty + ContactMedium
    // uses Customer.personaInquiry internally
    // Customer.verified from PersonaInquiry.verified when the inquiry is present
    // always true on the happy path
    // inquiryId on Mavenir from PersonaInquiry.inquiryId when present
    // duplicate Identity.idNumber or patch failure throws CustomerException with operation confirmIdentity
    // auto-apply voucher after success is Cart.applyVoucher
    ProfileRequirements.missing();
    PortalGateway.patchProfile();
  }
}

class CustomerRepository {
  // << aggregation >>
  customers: Collection<Customer>;
  // << association >>
  midtierCustomerService: MidtierCustomerService;

  constructor(customers: Collection<Customer>, midtierCustomerService: MidtierCustomerService) {
    this.customers = customers;
    this.midtierCustomerService = midtierCustomerService;
  }

  create(accountCredentials: AccountCredentials): Customer | null {
    // existing CognitoUser.customerId: returns null without MidtierCustomerService.create
    // missing CognitoUser.customerId: submits Create Customer Request to Midtier
    // failure throws CustomerException with operation create, AccountCredentials and cause
    // returns the new Customer; Cart.setupAccount stores its id on the Cognito user
    AccountCredentials.verified();
    MidtierCustomerService.create();
  }
  load(accountCredentials: AccountCredentials): Customer {
    // failure throws CustomerException with operation load, AccountCredentials and cause
    // terminated billing or load failure signs out
    MidtierCustomerService.read();
    AccountCredentials.signOut();
  }
}

/**
 * My Paradise HTTP boundary to Midtier. Midtier validates the account token and forwards customer operations to Mavenir.
 */
class MidtierCustomerService {

  constructor() {
  }

  validate(accountToken: AccountToken): string | Error {
    // Midtier validates the JWT and returns its Cognito email claim
  }
  create(accountToken: AccountToken): string | Error {
  }
  read(accountToken: AccountToken): MavenirCustomer | Error {
  }
}

/**
 * One typed Customer failure carrying enough domain context for callers to handle and report repository and aggregate failures safely.
 */
class CustomerException {
  operation: CustomerOperation;
  accountCredentials: AccountCredentials;
  message: string;
  cause: Error;

  constructor(operation: CustomerOperation, accountCredentials: AccountCredentials, message: string, cause: Error) {
    this.operation = operation;
    this.accountCredentials = accountCredentials;
    this.message = message;
    this.cause = cause;
  }

}

class Identity {
  email: string;
  name: string;
  lastName: string;
  fullName: string;
  preferredName: string;
  expiryDate: string;
  dateOfBirth: string;
  idNationality: string;
  idNumber: string;
  idType: string;
  otherPhoneNumber: string;

  constructor(email: string, name: string, lastName: string, fullName: string, preferredName: string, expiryDate: string, dateOfBirth: string, idNationality: string, idNumber: string, idType: string, otherPhoneNumber: string) {
    this.email = email;
    this.name = name;
    this.lastName = lastName;
    this.fullName = fullName;
    this.preferredName = preferredName;
    this.expiryDate = expiryDate;
    this.dateOfBirth = dateOfBirth;
    this.idNationality = idNationality;
    this.idNumber = idNumber;
    this.idType = idType;
    this.otherPhoneNumber = otherPhoneNumber;
  }

}

class Address {
  street: string;
  complement: string;
  city: string;
  parish: string;
  postalCode: string;
  country: string;

  constructor(street: string, complement: string, city: string, parish: string, postalCode: string, country: string) {
    this.street = street;
    this.complement = complement;
    this.city = city;
    this.parish = parish;
    this.postalCode = postalCode;
    this.country = country;
  }

}

/**
 * Paradise wrap of ++CognitoUser++. Own aggregate: constructed through `AccountRepository.newAccount()`. Auth operations live on this object and persist through the wired repository. `verified` is Cognito confirmed / unconfirmed.
 */
class AccountCredentials {
  // from CognitoUser.email when constructed from CognitoUser
  email: string;
  password: string;
  confirmPassword: string;
  validationCode: string;
  // from CognitoUser.confirmed when constructed from CognitoUser
  verified: boolean;
  // derived from CognitoUser.accountToken
  token: AccountToken | null;
  // derived from CognitoUser.customerId
  customerId: string | null;
  // true when CognitoUser.validationCodeSentAt is set
  validationCodeWasSent: boolean;
  // true when a validation code has been sent
  canActivate: boolean;
  isUpdatable: boolean;
  // true when missingRequirements is empty
  isPersistable: boolean;
  resendMessage: string | null;
  // << composition >>
  errors: AccountCredentialsErrors;
  // << composition >>
  requirements: AccountCredentialRequirements;

  constructor(email: string, password: string, confirmPassword: string, validationCode: string, verified: boolean, token: AccountToken | null, customerId: string | null, validationCodeWasSent: boolean, canActivate: boolean, isUpdatable: boolean, isPersistable: boolean, resendMessage: string | null, errors: AccountCredentialsErrors, requirements: AccountCredentialRequirements) {
    // from CognitoUser: email and verified come from the user; do not re-pass them
    // from email: password, confirmPassword, validationCode, verified optional
    this.email = email;
    this.password = password;
    this.confirmPassword = confirmPassword;
    this.validationCode = validationCode;
    this.verified = verified;
    this.token = token;
    this.customerId = customerId;
    this.validationCodeWasSent = validationCodeWasSent;
    this.canActivate = canActivate;
    this.isUpdatable = isUpdatable;
    this.isPersistable = isPersistable;
    this.resendMessage = resendMessage;
    this.errors = errors;
    this.requirements = requirements;
  }

  missingRequirements(): AccountCredentialRequirement[] {
    // when AccountCredentials are updated
    // empty: credentials meet all requirements
    // otherwise the unmet AccountCredentialRequirement rows
  }
  register(): void {
    // missingRequirements must be empty
    // already-registered email fails
    // writes CognitoUser onto these credentials; verified stays false until activate
    AccountRepository.persistNewAccount();
  }
  activate(validationCode: ValidationCode): void {
    // requires validationCodeWasSent
    // unusable ValidationCode fails
    // reads CognitoUser.confirmed into verified
    // signs in after confirmation
    AccountRepository.confirmAccount();
    AccountRepository.authenticateAccount();
  }
  authenticateAccount(): void {
    // email required, email format, and password required must be met — otherwise no Cognito call
    // existing account holder signs in
    // writes signed-in CognitoUser, account token, and customerId onto these credentials
    // wrong password and unknown email fail with the same NotAuthorizedException
    // unconfirmed account returns CONFIRM_SIGN_UP
    AccountRepository.authenticateAccount();
  }
  resendValidationCode(): void {
    // throws ValidationCodeResendWaitException when 60 seconds have not elapsed
    AccountRepository.resendAccountCode();
  }
  signOut(): void {
    AmplifyService.signOut();
  }
  storeCustomerId(customerId: string): CognitoUser {
    // failure throws CustomerException with operation storeCustomerId, these AccountCredentials and cause
    AmplifyService.updateUserAttributes();
  }
}

/**
 * Wraps the Cognito agent. Credentials exist before a Customer. `newAccount` is the canonical constructor: it returns AccountCredentials with the repository wired so register / activate / authenticateAccount / resendValidationCode persist.
 */
class AccountRepository {
  // << aggregation >>
  accountCredentials: Collection<AccountCredentials>;
  // << association >>
  amplifyService: AmplifyService;

  constructor(accountCredentials: Collection<AccountCredentials>, amplifyService: AmplifyService) {
    this.accountCredentials = accountCredentials;
    this.amplifyService = amplifyService;
  }

  newAccount(credentials?: AccountCredentials): AccountCredentials {
    // constructs AccountCredentials('') when none given
    // wires the repository onto the returned aggregate
  }
  persistNewAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors {
    // called by AccountCredentials.register
    AmplifyService.signUp();
  }
  confirmAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors {
    // called by AccountCredentials.activate
    AmplifyService.confirmSignUp();
  }
  authenticateAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors {
    // called by AccountCredentials.authenticateAccount and by activate after confirm
    // unverified: no AccountToken
    // wrong password or unknown email fails
    AmplifyService.signIn();
  }
  resendAccountCode(accountCredentials: AccountCredentials): CognitoUser | null {
    // called by AccountCredentials.resendValidationCode
    AmplifyService.resendSignUpCode();
  }
}

/**
 * Commit failures after `AccountCredentials.register` / `activate` / `AccountRepository.authenticateAccount`. Field rules are `missingRequirements()`.
 */
class AccountCredentialsErrors {
  register: string | null;
  signIn: string | null;
  validationCode: string | null;

  constructor(register: string | null, signIn: string | null, validationCode: string | null) {
    this.register = register;
    this.signIn = signIn;
    this.validationCode = validationCode;
  }

}

/**
 * Thrown by `AccountCredentials.resendValidationCode` when the 60-second wait has not elapsed. No Cognito call is made.
 */
class ValidationCodeResendWaitException {
  availableAt: Date;

  constructor(availableAt: Date) {
    this.availableAt = availableAt;
  }

}

class AccountCredentialRequirement {
  field: string;
  requirement: string;

  constructor(field: string, requirement: string) {
    this.field = field;
    this.requirement = requirement;
  }

}

/**
 * Catalog of rules. `missingRequirements()` returns the unmet subset.
 */
class AccountCredentialRequirements {
  emailRequired: AccountCredentialRequirement;
  emailFormat: AccountCredentialRequirement;
  passwordRequired: AccountCredentialRequirement;
  passwordLetters: AccountCredentialRequirement;
  passwordNumber: AccountCredentialRequirement;
  passwordSymbol: AccountCredentialRequirement;
  passwordLength: AccountCredentialRequirement;
  confirmRequired: AccountCredentialRequirement;
  confirmMismatch: AccountCredentialRequirement;

  constructor(emailRequired: AccountCredentialRequirement, emailFormat: AccountCredentialRequirement, passwordRequired: AccountCredentialRequirement, passwordLetters: AccountCredentialRequirement, passwordNumber: AccountCredentialRequirement, passwordSymbol: AccountCredentialRequirement, passwordLength: AccountCredentialRequirement, confirmRequired: AccountCredentialRequirement, confirmMismatch: AccountCredentialRequirement) {
    this.emailRequired = emailRequired;
    this.emailFormat = emailFormat;
    this.passwordRequired = passwordRequired;
    this.passwordLetters = passwordLetters;
    this.passwordNumber = passwordNumber;
    this.passwordSymbol = passwordSymbol;
    this.passwordLength = passwordLength;
    this.confirmRequired = confirmRequired;
    this.confirmMismatch = confirmMismatch;
  }

}

/**
 * AWS Amplify Auth in My Paradise. Talks to Cognito. Not a hosted record store.
 */
class AmplifyService {

  constructor() {
  }

  signUp(email: string, password: string): CognitoUser | Error {
  }
  signIn(email: string, password: string): CognitoUser | Error {
  }
  confirmSignUp(email: string, validationCode: ValidationCode): CognitoUser | Error {
  }
  resendSignUp(email: string): ValidationCodeSend | Error {
  }
  signOut(): void {
  }
  fetchUserAttributes(email: string): CognitoUser | Error {
    // My Paradise reads the Mavenir customer id from Cognito user attributes through Amplify
  }
  getUser(email: string): CognitoUser | null {
  }
}

/**
 * Cognito confirmed status is `confirmed`; Paradise reads it as `AccountCredentials.verified`. `AccountCredentials` `<<represents>>` this type.
 */
class CognitoUser {
  email: string;
  confirmed: boolean;
  customerId: string | null;
  validationCodeSentAt: Date | null;
  // << association >>
  accountToken: AccountToken | null;

  constructor(email: string, confirmed: boolean, customerId: string | null, validationCodeSentAt: Date | null, accountToken: AccountToken | null) {
    this.email = email;
    this.confirmed = confirmed;
    this.customerId = customerId;
    this.validationCodeSentAt = validationCodeSentAt;
    this.accountToken = accountToken;
  }

}

class AccountToken {
  email: string;
  customerId: string | null;

  constructor(email: string, customerId: string | null) {
    this.email = email;
    this.customerId = customerId;
  }

}

class ValidationCode {
  code: string;

  constructor(code: string) {
    this.code = code;
  }

}

/**
 * Timestamped record of every initial or repeated validation-code send performed by Amplify.
 */
class ValidationCodeSend {
  code: string;
  sentAt: Date;
  kind: initial | resend;

  constructor(code: string, sentAt: Date, kind: initial | resend) {
    this.code = code;
    this.sentAt = sentAt;
    this.kind = kind;
  }

}

class MavenirCustomer {
  id: string;
  // << association >>
  // from Subscription
  productOrder: MavenirProductOrder | null;
  // << association >>
  // from Billing
  billingAccount: MavenirBillingAccount | null;
  // always phone_verified
  phoneVerified: boolean;
  // 'true' | 'false' | absent
  // true when pSIM no iccid via patchWaitingPsim
  waitingPsim: string | null;
  // 'true' | absent
  done: string | null;
  // inquiryID
  // from PersonaInquiry.inquiryId when present
  inquiryId: string | null;
  // JSON-encoded Voucher characteristic
  // Cart.applyVoucher writes this
  // absent after Cart.removeVoucher
  voucher: Voucher | null;
  // << association >>
  shoppingCart: MavenirShoppingCart | null;
  // << composition >>
  contactMedium: ContactMedium;
  // << composition >>
  engagedParty: EngagedParty;

  constructor(id: string, productOrder: MavenirProductOrder | null, billingAccount: MavenirBillingAccount | null, phoneVerified: boolean, waitingPsim: string | null, done: string | null, inquiryId: string | null, voucher: Voucher | null, shoppingCart: MavenirShoppingCart | null, contactMedium: ContactMedium, engagedParty: EngagedParty) {
    this.id = id;
    this.productOrder = productOrder;
    this.billingAccount = billingAccount;
    this.phoneVerified = phoneVerified;
    this.waitingPsim = waitingPsim;
    this.done = done;
    this.inquiryId = inquiryId;
    this.voucher = voucher;
    this.shoppingCart = shoppingCart;
    this.contactMedium = contactMedium;
    this.engagedParty = engagedParty;
  }

}

/**
 * Mavenir `portalGateway`. Party create / read / profile. Cart, catalog, billing, and order slices live on the same service in their modules.
 */
class PortalGateway {

  constructor() {
  }

  create(email: string): MavenirCustomer | Error {
    // email already in Mavenir fails
  }
  read(id: string): MavenirCustomer | Error {
    // deliverPsim validates waitingPsim from this read
  }
  patchPhoneVerified(mavenirCustomerId: string): MavenirCustomer | Error {
    // always writes phone_verified true
    // when Twilio approved
  }
  patchWaitingPsim(mavenirCustomerId: string, waitingPsim: boolean): MavenirCustomer | Error {
    // true when pSIM no iccid (createOrder)
    // false after deliverPsim
  }
  patchProfile(mavenirCustomer: MavenirCustomer, engagedParty: EngagedParty, contactMedium: ContactMedium): MavenirCustomer | Error {
    // EngagedParty names + birthDate + individualIdentification.validated
    // ContactMedium street + city + stateOrProvince + postCode + phoneNumber
    // contact country always Bermuda
    // inquiryID when mavenirCustomer.inquiryId is present
    // individualIdentification.identificationId already on another MavenirCustomer: conflict
    // invalid AccountToken fails
  }
  patchVoucher(mavenirCustomer: MavenirCustomer, voucher: Voucher): MavenirCustomer | Error {
    // JSON-encoded Voucher as voucher characteristic
  }
  removeVoucher(mavenirCustomer: MavenirCustomer): MavenirCustomer | Error {
    // removes voucher characteristic
  }
  patchDone(mavenirCustomerId: string): MavenirCustomer | Error {
    // always writes done 'true'
    // Billing.createBilling / applyCredit live in # Billing
    // createOrder lives in # Subscription
  }
}

class ContactMedium {
  emailAddress: string;
  phoneNumber: string;
  street1: string;
  street2: string;
  city: string;
  stateOrProvince: string;
  postCode: string;
  // always Bermuda
  country: string;

  constructor(emailAddress: string, phoneNumber: string, street1: string, street2: string, city: string, stateOrProvince: string, postCode: string, country: string) {
    this.emailAddress = emailAddress;
    this.phoneNumber = phoneNumber;
    this.street1 = street1;
    this.street2 = street2;
    this.city = city;
    this.stateOrProvince = stateOrProvince;
    this.postCode = postCode;
    this.country = country;
  }

}

class EngagedParty {
  givenName: string;
  familyName: string;
  // preferredName when present; otherwise givenName
  preferredGivenName: string;
  birthDate: string;
  // << composition >>
  individualIdentification: IndividualIdentification;

  constructor(givenName: string, familyName: string, preferredGivenName: string, birthDate: string, individualIdentification: IndividualIdentification) {
    this.givenName = givenName;
    this.familyName = familyName;
    this.preferredGivenName = preferredGivenName;
    this.birthDate = birthDate;
    this.individualIdentification = individualIdentification;
  }

}

class IndividualIdentification {
  // Identity.idNumber
  identificationId: string;
  // Identity.idType
  identificationType: string;
  // Identity.idNationality
  issuingAuthority: string;
  // Customer.verified
  validated: boolean;
  // Identity.expiryDate
  endDateTime: string;

  constructor(identificationId: string, identificationType: string, issuingAuthority: string, validated: boolean, endDateTime: string) {
    this.identificationId = identificationId;
    this.identificationType = identificationType;
    this.issuingAuthority = issuingAuthority;
    this.validated = validated;
    this.endDateTime = endDateTime;
  }

}
