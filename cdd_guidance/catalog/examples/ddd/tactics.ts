import { Billing, BillingConflict, BillingException, BillingOperation, BillingState, billingRepository } from '../billing/Billing';
import { CreditServiceProviderId } from '../systems/mavenir/billing';
import { Cart } from '../cart/Cart';
import { AccountToken, CognitoUser } from '../systems/Cognito/Cognito';
import { Subscription } from '../subscription/Subscription';
import { profileRequirements } from '../KYC/Profile';
import type { Profile } from '../KYC/Profile';
import { amplifyService } from '../systems/amplify';
import type { AmplifyService } from '../systems/amplify';
import {
  ContactMedium,
  EngagedParty,
  IndividualIdentification,
  MavenirCreateContactMedium,
  MavenirCreateCustomerRequest,
  MavenirCreateCustomerResponse,
  MavenirCustomer,
  MavenirProfileError,
  MavenirCustomerSource,
  portalGateway,
} from '../systems/mavenir/portal-gateway';
import type { PortalGateway } from '../systems/mavenir/portal-gateway';


//───── Customer Aggregate ─────
//<<Entity | Root>>
export class Customer {
  public id: string;
  public identity: Identity;
  public address: Address;
  public verified = false;
  public done = false;
  public profile: Profile | null = null;
  _repository?: CustomerRepository;

  public cart: Cart | null;
  public billing: Billing | null;
  public subscriptions: Subscription[];

  constructor(public accountCredentials: AccountCredentials, record: CustomerRecord = {}) {
    this.id = record.id ?? accountCredentials.customerId ?? '';
    this.identity = record.identity ?? new Identity({ email: accountCredentials.email ?? '' });
    this.address = record.address ?? new Address();
    this.cart = record.cart ?? null;
    this.billing = record.billing ?? null;
    this.subscriptions = record.subscriptions ?? [];
  }

  confirmIdentity(): Customer {
    if (!this._repository) throw new Error('Customer has no repository. Load through customerRepository.');
    this.requireProfileRequirementsMet();
    const inquiryVerified = this.profile?.inquiry?.verified;
    const result = this._repository.update(this);
    if (result instanceof Error) {
      throw new CustomerException(CustomerOperation.ConfirmIdentity, this.accountCredentials, {
        message: this.updateFailureMessage(result),
        cause: result,
      });
    }
    const mapped = this._repository.translateUpdateResponse(result, this.accountCredentials);
    this.identity = mapped.identity;
    this.address = mapped.address;
    this.verified = inquiryVerified ?? mapped.verified;
    if (this.profile) this.profile.inquiry = null;
    return this;
  }

  private requireProfileRequirementsMet(): void {
    if (profileRequirements.missing(this.identity, this.address).length === 0) return;
    throw new CustomerException(CustomerOperation.ConfirmIdentity, this.accountCredentials, {
      message: 'Profile requirements are unmet',
      cause: new Error('unmet'),
    });
  }

  /** What the customer reads when the portal refuses their profile: a duplicate gets its own message. */
  private updateFailureMessage(error: Error): string {
    return error.message === MavenirProfileError.CustomerAlreadyExists
      ? 'Customer already exists.'
      : 'Something went wrong, please contact the support.';
  }

  createBilling(): Billing {
    if (this.billing?.id) {
      throw new BillingException(
        BillingOperation.Create,
        this,
        'Billing account already exists.',
        new Error(BillingConflict.AlreadyExists),
      );
    }
    const billing = billingRepository.create(this);
    if (billing instanceof Error) {
      throw new BillingException(BillingOperation.Create, this, 'Could not create billing account.', billing);
    }
    this.billing = billing;
    return billing;
  }
}

/** What a customer is created or loaded with; anything left out starts empty. */
export interface CustomerRecord {
  id?: string;
  identity?: Identity;
  address?: Address;
  cart?: Cart | null;
  billing?: Billing | null;
  subscriptions?: Subscription[];
}

//<<Entity>>
export class Identity {
  email = '';
  name = '';
  lastName = '';
  fullName = '';
  preferredName = '';
  expiryDate = '';
  dateOfBirth = '';
  idNationality = '';
  idNumber = '';
  idType = '';
  otherPhoneNumber = '';

  constructor(fields: Partial<Identity> & { email: string }) {
    Object.assign(this, fields);
  }
}

//<<Entity>>
export class Address {
  street = '';
  complement = '';
  city = '';
  parish = '';
  postalCode = '';
  country = '';

  constructor(fields: Partial<Address> = {}) {
    Object.assign(this, fields);
  }
}

//<<Value Object>>
export class ValidationCode {
  constructor(public code: string, public sentAt: Date = new Date()) {}
}

export const CustomerOperation = {
  ConfirmIdentity: 'confirmIdentity',
  Create: 'create',
  Load: 'load',
  StoreCustomerId: 'storeCustomerId',
} as const;
export type CustomerOperation = (typeof CustomerOperation)[keyof typeof CustomerOperation];

/** What went wrong: the message the customer reads and the error underneath it. */
export interface CustomerFailure {
  message: string;
  cause: Error;
}

export class CustomerException extends Error {
  public readonly cause: Error;

  constructor(
    public readonly operation: CustomerOperation,
    public readonly accountCredentials: AccountCredentials,
    failure: CustomerFailure,
  ) {
    super(failure.message);
    this.cause = failure.cause;
    this.name = 'CustomerException';
  }
}

/** Why the repository refused: the message the customer reads and the reason underneath it. */
interface Refusal {
  message: string;
  reason: string;
}

export class CustomerRepository {
  constructor(private readonly portalGateway: PortalGateway) {}

  async create(accountCredentials: AccountCredentials): Promise<Customer> {
    const created = await this.persistCustomer(accountCredentials);
    if (!created) {
      throw this.exception(CustomerOperation.Create, accountCredentials, {
        message: 'Could not create customer.',
        reason: 'Customer already exists',
      });
    }
    return created;
  }

  async load(accountCredentials: AccountCredentials): Promise<Customer> {
    const invalidToken = { message: 'Something went wrong when loading your account', reason: 'Invalid token' };
    const customerId = accountCredentials.customerId ?? accountCredentials.token?.customerId;
    if (!accountCredentials.token || !customerId) throw this.exception(CustomerOperation.Load, accountCredentials, invalidToken);
    const email = this.validateToken(accountCredentials.token);
    if (email instanceof Error || !accountCredentials.token.customerId)
      throw this.exception(CustomerOperation.Load, accountCredentials, invalidToken);
    const customer = await this.read(accountCredentials.token.customerId, accountCredentials);
    if (customer.billing?.state === BillingState.Terminated) {
      await accountCredentials.signOut();
      throw this.exception(CustomerOperation.Load, accountCredentials, {
        message: 'Your account has been terminated.',
        reason: 'Billing account is terminated',
      });
    }
    return customer;
  }

  update(customer: Customer): MavenirCustomer | Error {
    const mavenirCustomer = this.portalGateway.read(customer.id);
    if (mavenirCustomer instanceof Error) return mavenirCustomer;
    if (customer.profile?.inquiry) mavenirCustomer.inquiryId = customer.profile.inquiry.inquiryId;
    const { party, medium } = this.translateUpdateRequest(customer);
    return this.portalGateway.patchProfile(mavenirCustomer, party, medium);
  }

  private translateUpdateRequest(customer: Customer): { party: EngagedParty; medium: ContactMedium } {
    const givenName = formatName(customer.identity.name);
    const familyName = formatName(customer.identity.lastName);
    const preferredGivenName = customer.identity.preferredName
      ? formatName(customer.identity.preferredName)
      : givenName;
    return {
      party: new EngagedParty(
        givenName,
        familyName,
        preferredGivenName,
        customer.identity.dateOfBirth,
        new IndividualIdentification(
          customer.identity.idNumber,
          customer.identity.idType,
          customer.identity.idNationality,
          customer.profile?.inquiry?.verified ?? customer.verified,
          customer.identity.expiryDate,
        ),
      ),
      medium: new ContactMedium(
        customer.identity.email,
        customer.identity.otherPhoneNumber,
        customer.address.street,
        customer.address.complement,
        customer.address.city,
        customer.address.parish,
        customer.address.postalCode,
        'Bermuda',
      ),
    };
  }

  translateUpdateResponse(mavenirCustomer: MavenirCustomer, accountCredentials: AccountCredentials): Customer {
    return this.translateLoadResponse(mavenirCustomer, accountCredentials);
  }

  private async persistCustomer(accountCredentials: AccountCredentials): Promise<Customer | null> {
    if (!accountCredentials.verified || !accountCredentials.token)
      throw this.exception(CustomerOperation.Create, accountCredentials, { message: 'Could not create customer.', reason: 'Invalid token' });
    if (accountCredentials.customerId) return null;
    const email = this.validateToken(accountCredentials.token);
    if (email instanceof Error)
      throw new CustomerException(CustomerOperation.Create, accountCredentials, { message: 'Could not create customer.', cause: email });
    return this.persistNewCustomer(email, accountCredentials);
  }

  private async persistNewCustomer(email: string, accountCredentials: AccountCredentials): Promise<Customer> {
    const request = this.translateCreateRequest(email);
    const result = this.portalGateway.create(request);
    if (result instanceof Error) {
      throw new CustomerException(CustomerOperation.Create, accountCredentials, { message: 'Could not create customer.', cause: result });
    }
    return this.translateCreateResponse(result, accountCredentials);
  }

  private async read(customerId: string, accountCredentials: AccountCredentials): Promise<Customer> {
    const mavenirCustomer = this.portalGateway.read(customerId);
    if (mavenirCustomer instanceof Error) {
      await accountCredentials.signOut();
      throw new CustomerException(CustomerOperation.Load, accountCredentials, {
        message: 'Something went wrong when loading your account',
        cause: mavenirCustomer,
      });
    }
    return this.translateLoadResponse(mavenirCustomer, accountCredentials);
  }

  private translateCreateRequest(email: string): MavenirCreateCustomerRequest {
    return new MavenirCreateCustomerRequest(
      email,
      CreditServiceProviderId.Paradise,
      MavenirCustomerSource.OnBoarding,
      [
        new MavenirCreateContactMedium(
          true,
          'ContactMedium',
          { endDateTime: null, startDateTime: new Date().toISOString() },
          { emailAddress: email },
        ),
      ],
    );
  }

  private translateCreateResponse(result: MavenirCreateCustomerResponse, accountCredentials: AccountCredentials): Customer {
    const identity = new Identity({ email: accountCredentials.email });
    return this.attach(new Customer(accountCredentials, { id: result.id, identity, address: new Address() }));
  }

  private translateLoadResponse(mavenirCustomer: MavenirCustomer, accountCredentials: AccountCredentials): Customer {
    const customer = new Customer(accountCredentials, {
      id: mavenirCustomer.id,
      identity: this.translateIdentity(mavenirCustomer),
      address: this.translateAddress(mavenirCustomer.contactMedium),
    });
    if (mavenirCustomer.billingAccount) customer.billing = this.translateBilling(mavenirCustomer.billingAccount, customer);
    customer.verified = mavenirCustomer.engagedParty.individualIdentification.validated;
    customer.done = mavenirCustomer.done === 'true';
    return this.attach(customer);
  }

  private translateIdentity({ contactMedium, engagedParty }: MavenirCustomer): Identity {
    const identification = engagedParty.individualIdentification;
    return new Identity({
      email: contactMedium.emailAddress,
      name: engagedParty.givenName,
      lastName: engagedParty.familyName,
      fullName: `${engagedParty.givenName} ${engagedParty.familyName}`.trim(),
      preferredName: engagedParty.preferredGivenName,
      expiryDate: identification.endDateTime,
      dateOfBirth: engagedParty.birthDate,
      idNationality: identification.issuingAuthority,
      idNumber: identification.identificationId,
      idType: identification.identificationType,
      otherPhoneNumber: contactMedium.phoneNumber,
    });
  }

  private translateAddress(contactMedium: MavenirCustomer['contactMedium']): Address {
    return new Address({
      street: contactMedium.street1,
      complement: contactMedium.street2,
      city: contactMedium.city,
      parish: contactMedium.stateOrProvince,
      postalCode: contactMedium.postCode,
      country: contactMedium.country,
    });
  }

  private translateBilling(billingAccount: NonNullable<MavenirCustomer['billingAccount']>, customer: Customer): Billing {
    const billing = new Billing(billingAccount.id, customer, billingRepository);
    billing.state = (billingAccount.state as BillingState) || BillingState.Active;
    billing.creditAdjustments = [...billingAccount.creditAdjustments];
    return billing;
  }

  private attach(customer: Customer): Customer {
    customer._repository = this;
    return customer;
  }

  private validateToken(token: AccountToken): string | Error {
    return token.jwt?.startsWith('token:') ? token.email : new Error('Invalid token');
  }

  /** An exception whose cause is a reason the repository found, not an error a system raised. */
  private exception(operation: CustomerOperation, accountCredentials: AccountCredentials, refusal: Refusal): CustomerException {
    return new CustomerException(operation, accountCredentials, { message: refusal.message, cause: new Error(refusal.reason) });
  }
}
export const customerRepository = new CustomerRepository(portalGateway);

// ── AccountCredentials Aggregatee ─────

/** What a person has typed into the account forms so far; anything left out starts empty. */
export interface EnteredCredentials {
  password?: string;
  confirmPassword?: string;
  validationCode?: string;
  verified?: boolean;
}

export class AccountCredentials {
  static readonly RESEND_WAIT_MILLISECONDS = 60_000;

  readonly errors: AccountCredentialsErrors = emptyAccountCredentialsErrors();
  resendMessage: string | null = null;
  readonly requirements: AccountCredentialRequirements = {
    emailRequired: { field: 'email', requirement: 'Email is required' },
    emailFormat: { field: 'email', requirement: 'Please use a valid email format: yourname@domain.com' },
    passwordRequired: { field: 'password', requirement: 'Password is required' },
    passwordLetters: { field: 'password', requirement: 'Password must contain uppercase and lowercase letters' },
    passwordNumber: { field: 'password', requirement: 'Password must have at least one number' },
    passwordSymbol: { field: 'password', requirement: 'Password must have at least one symbol' },
    passwordLength: { field: 'password', requirement: 'Length must be greater than 8 characters' },
    confirmRequired: { field: 'confirmPassword', requirement: 'Confirm Password is required' },
    confirmMismatch: { field: 'confirmPassword', requirement: "Passwords don't match" },
  };

  public email: string;
  public password: string;
  public confirmPassword: string;
  public validationCode: string;
  public verified: boolean;
  private cognitoUser: CognitoUser | null;

  /** Set by AccountRepository.newAccount() — gives credentials their behaviour. */
  _repository?: AccountRepository;

  /** Credentials for an email typed in, or for a user Cognito already knows, who brings their email and confirmation. */
  constructor(emailOrCognitoUser: string | CognitoUser, entered: EnteredCredentials = {}) {
    this.cognitoUser = emailOrCognitoUser instanceof CognitoUser ? emailOrCognitoUser : null;
    this.email = this.cognitoUser?.email ?? (emailOrCognitoUser as string);
    this.password = entered.password ?? '';
    this.confirmPassword = entered.confirmPassword ?? '';
    this.validationCode = entered.validationCode ?? '';
    this.verified = this.cognitoUser?.confirmed ?? entered.verified ?? false;
  }

  get token(): AccountToken | null {
    return this.cognitoUser?.accountToken ?? null;
  }

  get customerId(): string | null {
    return this.cognitoUser?.customerId ?? null;
  }

  get validationCodeWasSent(): boolean {
    return this.cognitoUser?.validationCodeSentAt != null;
  }

  get canActivate(): boolean {
    return this.validationCodeWasSent;
  }

  get isUpdatable(): boolean {
    return true;
  }

  get isPersistable(): boolean {
    return this.missingRequirements().length === 0;
  }

  missingRequirements(): AccountCredentialRequirement[] {
    const missing: AccountCredentialRequirement[] = [];
    if (!this.email) missing.push(this.requirements.emailRequired);
    else if (!this.email.includes('@')) missing.push(this.requirements.emailFormat);

    if (!this.password) missing.push(this.requirements.passwordRequired);
    else {
      if (!/[a-z]/.test(this.password) || !/[A-Z]/.test(this.password)) missing.push(this.requirements.passwordLetters);
      if (!/[0-9]/.test(this.password)) missing.push(this.requirements.passwordNumber);
      if (!/[^a-zA-Z0-9]/.test(this.password)) missing.push(this.requirements.passwordSymbol);
      if (this.password.length <= 8) missing.push(this.requirements.passwordLength);
    }
    if (!this.confirmPassword) missing.push(this.requirements.confirmRequired);
    else if (this.confirmPassword !== this.password) missing.push(this.requirements.confirmMismatch);
    return missing;
  }

  async register(): Promise<void> {
    const repository = this.repository();
    if (this.missingRequirements().length > 0)
      throw { ...emptyAccountCredentialsErrors(), register: 'Account credential requirements are unmet' };
    this.becomeUser(await repository.create(this));
  }

  async activate(validationCode: ValidationCode): Promise<void> {
    const repository = this.repository();
    if (!this.validationCodeWasSent) throw this.validationCodeError('No validation code has been sent.');
    this.validationCode = validationCode.code;
    this.becomeUser(await repository.update(this));
    const signedInUser = await repository.read(this);
    if (signedInUser instanceof CognitoUser) this.cognitoUser = signedInUser;
  }

  async authenticateAccount(): Promise<void> {
    const repository = this.repository();
    if (this.unmetSignInRequirements().length > 0)
      throw { ...emptyAccountCredentialsErrors(), signIn: 'Account credential requirements are unmet' };
    this.becomeUser(await repository.read(this));
  }

  async resendValidationCode(): Promise<void> {
    const repository = this.repository();
    const sentAt = this.cognitoUser?.validationCodeSentAt;
    if (sentAt && Date.now() - sentAt.getTime() < AccountCredentials.RESEND_WAIT_MILLISECONDS) {
      throw new ValidationCodeResendWaitException(
        new Date(sentAt.getTime() + AccountCredentials.RESEND_WAIT_MILLISECONDS),
      );
    }
    const updatedUser = await repository.resendAccountCode(this);
    if (updatedUser instanceof CognitoUser) this.cognitoUser = updatedUser;
    this.resendMessage = 'We sent you a new code. Please check your email.';
  }

  async signOut(): Promise<void> {
    await amplifyService.signOut();
    if (this.cognitoUser) this.cognitoUser.accountToken = null;
  }

  async storeCustomerId(customerId: string): Promise<CognitoUser> {
    const user = await amplifyService.updateUserAttributes({ userAttributes: { 'custom:customerId': customerId } });
    if (user instanceof Error) {
      throw new CustomerException(CustomerOperation.StoreCustomerId, this, { message: 'Could not store customer id.', cause: user });
    }
    this.cognitoUser = user;
    return user;
  }

  private repository(): AccountRepository {
    if (!this._repository) throw new Error('AccountCredentials has no repository. Use accountRepository.newAccount().');
    return this._repository;
  }

  /** Take on the user Cognito answered with, or throw the errors it answered with instead. */
  private becomeUser(answer: CognitoUser | AccountCredentialsErrors): void {
    if (!(answer instanceof CognitoUser)) throw answer;
    this.cognitoUser = answer;
    this.verified = answer.confirmed;
  }

  private unmetSignInRequirements(): AccountCredentialRequirement[] {
    return this.missingRequirements().filter(
      r =>
        r === this.requirements.emailRequired ||
        r === this.requirements.emailFormat ||
        r === this.requirements.passwordRequired,
    );
  }

  private validationCodeError(validationCode: string): AccountCredentialsErrors {
    return { ...emptyAccountCredentialsErrors(), validationCode };
  }
}

export class ValidationCodeResendWaitException extends Error {
  constructor(public readonly availableAt: Date) {
    super('Validation code cannot be resent before the 60-second wait has elapsed.');
    this.name = 'ValidationCodeResendWaitException';
  }
}

export interface AccountCredentialsErrors {
  register: string | null;
  signIn: string | null;
  validationCode: string | null;
}

export interface AccountCredentialRequirement {
  field: string;
  requirement: string;
}

export interface AccountCredentialRequirements {
  emailRequired: AccountCredentialRequirement;
  emailFormat: AccountCredentialRequirement;
  passwordRequired: AccountCredentialRequirement;
  passwordLetters: AccountCredentialRequirement;
  passwordNumber: AccountCredentialRequirement;
  passwordSymbol: AccountCredentialRequirement;
  passwordLength: AccountCredentialRequirement;
  confirmRequired: AccountCredentialRequirement;
  confirmMismatch: AccountCredentialRequirement;
}

function emptyAccountCredentialsErrors(): AccountCredentialsErrors {
  return { register: null, signIn: null, validationCode: null };
}

export class AccountRepository {
  constructor(private readonly amplify: AmplifyService) {}

  newAccount(credentials?: AccountCredentials): AccountCredentials {
    const account = credentials ?? new AccountCredentials('');
    account._repository = this;
    return account;
  }

  async create(accountCredentials: AccountCredentials): Promise<CognitoUser | AccountCredentialsErrors> {
    const result = await this.amplify.signUp(this.translateCreateRequest(accountCredentials));
    return this.translateCreateResponse(result);
  }

  private translateCreateRequest(accountCredentials: AccountCredentials): {
    username: string;
    password: string;
    options: { userAttributes: Record<string, string> };
  } {
    return {
      username: accountCredentials.email,
      password: accountCredentials.password,
      options: {
        userAttributes: {
          email: accountCredentials.email,
          'custom:language': 'en',
          'custom:role': 'customer',
          'custom:serviceproviderId': CreditServiceProviderId.Paradise,
        },
      },
    };
  }

  private translateCreateResponse(result: CognitoUser | Error): CognitoUser | AccountCredentialsErrors {
    return result instanceof Error
      ? { ...emptyAccountCredentialsErrors(), register: result.name }
      : result;
  }

  async update(accountCredentials: AccountCredentials): Promise<CognitoUser | AccountCredentialsErrors> {
    const result = await this.amplify.confirmSignUp({
      username: accountCredentials.email,
      confirmationCode: accountCredentials.validationCode,
    });
    return this.translateUpdateResponse(result);
  }

  private translateUpdateResponse(result: CognitoUser | Error): CognitoUser | AccountCredentialsErrors {
    if (result instanceof Error) {
      const validationCode = result.name.includes('Exceeded')
        ? 'Attempts limit exceeded. Please try again later.'
        : "Hmm. That code didn't work.";
      return { ...emptyAccountCredentialsErrors(), validationCode };
    }
    return result;
  }

  async read(accountCredentials: AccountCredentials): Promise<CognitoUser | AccountCredentialsErrors> {
    const result = await this.amplify.signIn({
      username: accountCredentials.email,
      password: accountCredentials.password,
    });
    return this.translateReadResponse(result);
  }

  private translateReadResponse(result: CognitoUser | Error): CognitoUser | AccountCredentialsErrors {
    return result instanceof Error
      ? { ...emptyAccountCredentialsErrors(), signIn: result.name }
      : result;
  }

  async resendAccountCode(accountCredentials: AccountCredentials): Promise<CognitoUser | null> {
    const result = await this.amplify.resendSignUpCode({ username: accountCredentials.email });
    return this.translateResendResponse(result, accountCredentials);
  }

  private translateResendResponse(
    result: { error?: Error },
    accountCredentials: AccountCredentials,
  ): CognitoUser | null {
    if (result.error) return null;
    return new CognitoUser(accountCredentials.email, accountCredentials.verified, null, null, new Date());
  }
}

function formatName(name: string): string {
  return name
    .split(' ')
    .map(part => part.trim())
    .filter(Boolean)
    .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}


export const accountRepository = new AccountRepository(amplifyService);


