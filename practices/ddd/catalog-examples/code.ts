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

export class ValidationCode {
  constructor(public code: string, public sentAt: Date = new Date()) {}
}

export class Identity {
  constructor(
    public email: string,
    public name = '',
    public lastName = '',
    public fullName = '',
    public preferredName = '',
    public expiryDate = '',
    public dateOfBirth = '',
    public idNationality = '',
    public idNumber = '',
    public idType = '',
    public otherPhoneNumber = '',
  ) {}
}

export class Address {
  constructor(
    public street = '',
    public complement = '',
    public city = '',
    public parish = '',
    public postalCode = '',
    public country = '',
  ) {}
}

export class Customer {
  public id: string;
  public identity: Identity;
  public address: Address;
  public verified = false;
  public done = false;
  public profile: Profile | null = null;
  _repository?: CustomerRepository;

  /** Canonical: `new Customer(accountCredentials)`. id, identity, and address are derived unless the repository passes richer Mavenir data. */
  constructor(
    public accountCredentials: AccountCredentials,
    id?: string,
    identity?: Identity,
    address?: Address,
    public cart: Cart | null = null,
    public billing: Billing | null = null,
    public subscriptions: Subscription[] = [],
  ) {
    this.id = id ?? accountCredentials.customerId ?? '';
    this.identity = identity ?? new Identity(accountCredentials.email ?? '');
    this.address = address ?? new Address();
  }

  confirmIdentity(): Customer {
    if (!this._repository) throw new Error('Customer has no repository. Load through customerRepository.');
    const missing = profileRequirements.missing(this.identity, this.address);
    if (missing.length > 0) {
      throw new CustomerException(
        CustomerOperation.ConfirmIdentity,
        this.accountCredentials,
        'Profile requirements are unmet',
        new Error('unmet'),
      );
    }
    const inquiryVerified = this.profile?.inquiry?.verified;
    const result = this._repository.update(this);
    if (result instanceof Error) {
      const message = result.message === MavenirProfileError.CustomerAlreadyExists
        ? 'Customer already exists.'
        : 'Something went wrong, please contact the support.';
      throw new CustomerException(CustomerOperation.ConfirmIdentity, this.accountCredentials, message, result);
    }
    const mapped = this._repository.translateUpdateResponse(result, this.accountCredentials);
    this.identity = mapped.identity;
    this.address = mapped.address;
    this.verified = inquiryVerified ?? mapped.verified;
    if (this.profile) this.profile.inquiry = null;
    return this;
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

export const CustomerOperation = {
  ConfirmIdentity: 'confirmIdentity',
  Create: 'create',
  Load: 'load',
  StoreCustomerId: 'storeCustomerId',
} as const;
export type CustomerOperation = (typeof CustomerOperation)[keyof typeof CustomerOperation];

export class CustomerException extends Error {
  constructor(
    public readonly operation: CustomerOperation,
    public readonly accountCredentials: AccountCredentials,
    message: string,
    public readonly cause: Error,
  ) {
    super(message);
    this.name = 'CustomerException';
  }
}

// ── AccountCredentials ───────────────────────────────────────────────────────

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

  constructor(emailOrCognitoUser: string | CognitoUser, password = '', confirmPassword = '', validationCode = '', verified = false, cognitoUser: CognitoUser | null = null) {
    if (emailOrCognitoUser instanceof CognitoUser) {
      this.email = emailOrCognitoUser.email;
      this.password = password;
      this.confirmPassword = confirmPassword;
      this.validationCode = validationCode;
      this.verified = emailOrCognitoUser.confirmed;
      this.cognitoUser = emailOrCognitoUser;
    } else {
      this.email = emailOrCognitoUser;
      this.password = password;
      this.confirmPassword = confirmPassword;
      this.validationCode = validationCode;
      this.verified = verified;
      this.cognitoUser = cognitoUser;
    }
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
    if (!this._repository) throw new Error('AccountCredentials has no repository. Use accountRepository.newAccount().');
    if (this.missingRequirements().length > 0)
      throw { ...emptyAccountCredentialsErrors(), register: 'Account credential requirements are unmet' };
    const user = await this._repository.create(this);
    if (!(user instanceof CognitoUser)) throw user;
    this.cognitoUser = user;
    this.verified = user.confirmed;
  }

  async activate(validationCode: ValidationCode): Promise<void> {
    if (!this._repository) throw new Error('AccountCredentials has no repository. Use accountRepository.newAccount().');
    if (!this.validationCodeWasSent) throw this.validationCodeError('No validation code has been sent.');
    this.validationCode = validationCode.code;

    const confirmedUser = await this._repository.update(this);
    if (!(confirmedUser instanceof CognitoUser)) throw confirmedUser;
    this.cognitoUser = confirmedUser;
    this.verified = confirmedUser.confirmed;

    const signedInUser = await this._repository.read(this);
    if (signedInUser instanceof CognitoUser) this.cognitoUser = signedInUser;
  }

  async authenticateAccount(): Promise<void> {
    if (!this._repository) throw new Error('AccountCredentials has no repository. Use accountRepository.newAccount().');
    if (this.unmetSignInRequirements().length > 0)
      throw { ...emptyAccountCredentialsErrors(), signIn: 'Account credential requirements are unmet' };
    const user = await this._repository.read(this);
    if (!(user instanceof CognitoUser)) throw user;
    this.cognitoUser = user;
    this.verified = user.confirmed;
  }

  async resendValidationCode(): Promise<void> {
    if (!this._repository) throw new Error('AccountCredentials has no repository. Use accountRepository.newAccount().');
    const sentAt = this.cognitoUser?.validationCodeSentAt;
    if (sentAt && Date.now() - sentAt.getTime() < AccountCredentials.RESEND_WAIT_MILLISECONDS) {
      throw new ValidationCodeResendWaitException(
        new Date(sentAt.getTime() + AccountCredentials.RESEND_WAIT_MILLISECONDS),
      );
    }
    const updatedUser = await this._repository.resendAccountCode(this);
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
      throw new CustomerException(
        'storeCustomerId',
        this,
        'Could not store customer id.',
        user,
      );
    }
    this.cognitoUser = user;
    return user;
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

  translateCreateRequest(accountCredentials: AccountCredentials): {
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

  translateCreateResponse(result: CognitoUser | Error): CognitoUser | AccountCredentialsErrors {
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

  translateUpdateResponse(result: CognitoUser | Error): CognitoUser | AccountCredentialsErrors {
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

  translateReadResponse(result: CognitoUser | Error): CognitoUser | AccountCredentialsErrors {
    return result instanceof Error
      ? { ...emptyAccountCredentialsErrors(), signIn: result.name }
      : result;
  }

  async resendAccountCode(accountCredentials: AccountCredentials): Promise<CognitoUser | null> {
    const result = await this.amplify.resendSignUpCode({ username: accountCredentials.email });
    return this.translateResendResponse(result, accountCredentials);
  }

  translateResendResponse(
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

export class CustomerRepository {
  constructor(private readonly portalGateway: PortalGateway) {}

  async create(accountCredentials: AccountCredentials): Promise<Customer> {
    const created = await this.persistCustomer(accountCredentials);
    if (!created) {
      throw this.exception(CustomerOperation.Create, accountCredentials, 'Could not create customer.', 'Customer already exists');
    }
    return created;
  }

  async load(accountCredentials: AccountCredentials): Promise<Customer> {
    const customerId = accountCredentials.customerId ?? accountCredentials.token?.customerId;
    if (!accountCredentials.token || !customerId)
      throw this.exception(CustomerOperation.Load, accountCredentials, 'Something went wrong when loading your account', 'Invalid token');
    const email = this.validateToken(accountCredentials.token);
    if (email instanceof Error || !accountCredentials.token.customerId)
      throw this.exception(CustomerOperation.Load, accountCredentials, 'Something went wrong when loading your account', 'Invalid token');
    const customer = await this.read(accountCredentials.token.customerId, accountCredentials);
    if (customer.billing?.state === BillingState.Terminated) {
      await accountCredentials.signOut();
      throw this.exception(
        CustomerOperation.Load,
        accountCredentials,
        'Your account has been terminated.',
        'Billing account is terminated',
      );
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

  translateUpdateRequest(customer: Customer): { party: EngagedParty; medium: ContactMedium } {
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
      throw this.exception(CustomerOperation.Create, accountCredentials, 'Could not create customer.', 'Invalid token');
    if (accountCredentials.customerId) return null;
    const email = this.validateToken(accountCredentials.token);
    if (email instanceof Error)
      throw new CustomerException(CustomerOperation.Create, accountCredentials, 'Could not create customer.', email);
    return this.persistNewCustomer(email, accountCredentials);
  }

  private async persistNewCustomer(email: string, accountCredentials: AccountCredentials): Promise<Customer> {
    const request = this.translateCreateRequest(email);
    const result = this.portalGateway.create(request);
    if (result instanceof Error) {
      throw new CustomerException(CustomerOperation.Create, accountCredentials, 'Could not create customer.', result);
    }
    return this.translateCreateResponse(result, accountCredentials);
  }

  private async read(customerId: string, accountCredentials: AccountCredentials): Promise<Customer> {
    const mavenirCustomer = this.portalGateway.read(customerId);
    if (mavenirCustomer instanceof Error) {
      await accountCredentials.signOut();
      throw new CustomerException(
        CustomerOperation.Load,
        accountCredentials,
        'Something went wrong when loading your account',
        mavenirCustomer,
      );
    }
    return this.translateLoadResponse(mavenirCustomer, accountCredentials);
  }

  translateCreateRequest(email: string): MavenirCreateCustomerRequest {
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

  translateCreateResponse(result: MavenirCreateCustomerResponse, accountCredentials: AccountCredentials): Customer {
    return this.attach(new Customer(accountCredentials, result.id, new Identity(accountCredentials.email), new Address()));
  }

  private translateLoadResponse(mavenirCustomer: MavenirCustomer, accountCredentials: AccountCredentials): Customer {
    const { contactMedium, engagedParty } = mavenirCustomer;
    const identity = new Identity(
      contactMedium.emailAddress,
      engagedParty.givenName,
      engagedParty.familyName,
      `${engagedParty.givenName} ${engagedParty.familyName}`.trim(),
      engagedParty.preferredGivenName,
      engagedParty.individualIdentification.endDateTime,
      engagedParty.birthDate,
      engagedParty.individualIdentification.issuingAuthority,
      engagedParty.individualIdentification.identificationId,
      engagedParty.individualIdentification.identificationType,
      contactMedium.phoneNumber,
    );
    const address = new Address(
      contactMedium.street1,
      contactMedium.street2,
      contactMedium.city,
      contactMedium.stateOrProvince,
      contactMedium.postCode,
      contactMedium.country,
    );
    const customer = new Customer(accountCredentials, mavenirCustomer.id, identity, address);
    if (mavenirCustomer.billingAccount) {
      customer.billing = new Billing(mavenirCustomer.billingAccount.id, customer, billingRepository);
      customer.billing.state = (mavenirCustomer.billingAccount.state as BillingState) || BillingState.Active;
      customer.billing.creditAdjustments = [...mavenirCustomer.billingAccount.creditAdjustments];
    }
    customer.verified = engagedParty.individualIdentification.validated;
    customer.done = mavenirCustomer.done === 'true';
    return this.attach(customer);
  }

  private attach(customer: Customer): Customer {
    customer._repository = this;
    return customer;
  }

  private validateToken(token: AccountToken): string | Error {
    return token.jwt?.startsWith('token:') ? token.email : new Error('Invalid token');
  }

  private exception(
    operation: CustomerOperation,
    accountCredentials: AccountCredentials,
    message: string,
    cause: string,
  ): CustomerException {
    return new CustomerException(operation, accountCredentials, message, new Error(cause));
  }
}
export const accountRepository = new AccountRepository(amplifyService);
export const customerRepository = new CustomerRepository(portalGateway);

