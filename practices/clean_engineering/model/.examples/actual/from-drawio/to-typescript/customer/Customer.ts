class Customer {
  id: string;
  verified: boolean;
  // << composition >>
  identity: Identity;
  // << composition >>
  address: Address;
  // << association >>
  accountCredentials: AccountCredentials;
  // << association >>
  cart: Cart | null;
  // << association >>
  billing: Billing | null;
  // << association >>
  subscriptions: Subscription[];
  // << association >>
  personaInquiry: PersonaInquiry | null;

  constructor(id: string, verified: boolean, identity: Identity, address: Address, accountCredentials: AccountCredentials, cart: Cart | null, billing: Billing | null, subscriptions: Subscription[], personaInquiry: PersonaInquiry | null) {
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
  }
  load(accountCredentials: AccountCredentials): Customer {
  }
}

class MidtierCustomerService {

  constructor() {
  }

  validate(accountToken: AccountToken): string | Error {
  }
  create(accountToken: AccountToken): string | Error {
  }
  read(accountToken: AccountToken): MavenirCustomer | Error {
  }
}

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

class AccountCredentials {
  email: string;
  password: string;
  confirmPassword: string;
  validationCode: string;
  verified: boolean;
  token: AccountToken | null;
  customerId: string | null;
  validationCodeWasSent: boolean;
  canActivate: boolean;
  isUpdatable: boolean;
  isPersistable: boolean;
  resendMessage: string | null;
  // << composition >>
  errors: AccountCredentialsErrors;
  // << composition >>
  requirements: AccountCredentialRequirements;

  constructor(email: string, password: string, confirmPassword: string, validationCode: string, verified: boolean, token: AccountToken | null, customerId: string | null, validationCodeWasSent: boolean, canActivate: boolean, isUpdatable: boolean, isPersistable: boolean, resendMessage: string | null, errors: AccountCredentialsErrors, requirements: AccountCredentialRequirements) {
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
  }
  register(): void {
  }
  activate(validationCode: ValidationCode): void {
  }
  authenticateAccount(): void {
  }
  resendValidationCode(): void {
  }
  signOut(): void {
  }
  storeCustomerId(customerId: string): CognitoUser {
  }
}

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
  }
  persistNewAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors {
  }
  confirmAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors {
  }
  authenticateAccount(accountCredentials: AccountCredentials): CognitoUser | AccountCredentialsErrors {
  }
  resendAccountCode(accountCredentials: AccountCredentials): CognitoUser | null {
  }
}

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
  }
  getUser(email: string): CognitoUser | null {
  }
}

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
  productOrder: MavenirProductOrder | null;
  // << association >>
  billingAccount: MavenirBillingAccount | null;
  phoneVerified: boolean;
  waitingPsim: string | null;
  done: string | null;
  inquiryId: string | null;
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

class PortalGateway {

  constructor() {
  }

  create(email: string): MavenirCustomer | Error {
  }
  read(id: string): MavenirCustomer | Error {
  }
  patchPhoneVerified(mavenirCustomerId: string): MavenirCustomer | Error {
  }
  patchWaitingPsim(mavenirCustomerId: string, waitingPsim: boolean): MavenirCustomer | Error {
  }
  patchProfile(mavenirCustomer: MavenirCustomer, engagedParty: EngagedParty, contactMedium: ContactMedium): MavenirCustomer | Error {
  }
  patchVoucher(mavenirCustomer: MavenirCustomer, voucher: Voucher): MavenirCustomer | Error {
  }
  removeVoucher(mavenirCustomer: MavenirCustomer): MavenirCustomer | Error {
  }
  patchDone(mavenirCustomerId: string): MavenirCustomer | Error {
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
  identificationId: string;
  identificationType: string;
  issuingAuthority: string;
  validated: boolean;
  endDateTime: string;

  constructor(identificationId: string, identificationType: string, issuingAuthority: string, validated: boolean, endDateTime: string) {
    this.identificationId = identificationId;
    this.identificationType = identificationType;
    this.issuingAuthority = issuingAuthority;
    this.validated = validated;
    this.endDateTime = endDateTime;
  }

}
