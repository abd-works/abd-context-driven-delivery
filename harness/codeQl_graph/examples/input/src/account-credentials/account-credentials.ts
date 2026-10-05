import { CustomerRepository, type Customer } from '../customer/customer';
import { OnboardingStep } from '../onboarding/onboarding-step';

export { OnboardingStep };

export class ValidationCode {
  constructor(public code: string, public sentAt: Date = new Date()) {}
}

export class ValidationCodeMessage {
  executed = false;

  constructor(
    public readonly sentAt: Date,
    public readonly email: string,
    public readonly code: string,
  ) {}
}


export class AccountToken {
  constructor(
    public email: string,
    public customerId: string | null,
    public jwt: string | null = null,
  ) {}
}

export class AccountCredentials {
  static readonly RESEND_WAIT_MILLISECONDS = 60_000;

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
    signInMismatch: { field: 'signIn', requirement: 'The email or password you entered did not match our records.' },
    emailAlreadyRegistered: { field: 'register', requirement: 'Email is already registered.' },
    requirementsUnmet: { field: 'register', requirement: 'Account credential requirements are unmet' },
    validationCodeMismatch: { field: 'validationCode', requirement: "Hmm. That code didn't work." },
    validationCodeAttempts: { field: 'validationCode', requirement: 'Attempts limit exceeded. Please try again later.' },
    resendSent: { field: 'validationCode', requirement: 'We sent you a new code. Please check your email.' },
    resendWait: { field: 'validationCode', requirement: 'Validation code cannot be resent before the 60-second wait has elapsed.' },
  };

  //invariant
  token: AccountToken | null = null;
  //foreign Customer
  private _customer: Customer | null = null;
  customerId: string | null = null;
  _validationCodeSentAt: Date | null = null;
  expectedValidationCode: string | null = null;
  readonly validationCodeMessages: ValidationCodeMessage[] = [];

  /** Set by AccountCredentialsRepository.new() — gives credentials their behaviour. */
  _repository?: AccountCredentialsRepository;

  constructor(
    public email = '',
    public password = '',
    public confirmPassword = '',
    public validationCode = '',
    public verified = false,
  ) {}

  get validationCodeWasSent(): boolean {
    return this.validationCodeMessages.some(message => message.executed);
  }

  get onboardingStep(): OnboardingStep | null {
    if (this.token && !this.verified) return OnboardingStep.VerifyAccount;
    return null;
  }

  emailValidationCode(): void {
    const code = this.validationCodeMessages.length === 0 ? '123456' : '654321';
    const message = new ValidationCodeMessage(new Date(), this.email, code);
    message.executed = true;
    this.validationCodeMessages.push(message);
    this._validationCodeSentAt = message.sentAt;
    this.expectedValidationCode = message.code;
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

  get isAuthenticatable(): boolean {
    return this.unmetSignInRequirements().length === 0;
  }

  get customer(): Customer | null {
    return this._customer;
  }

  set customer(customer: Customer | null) {
    this._customer = customer;
    if (!customer) return;
    this.customerId = customer.id;
    if (this.token) this.token.customerId = customer.id;
    else if (this.verified) this.issueSessionToken();
  }

  issueSessionToken(): void {
    this.token = new AccountToken(this.email, this.customerId, `token:${this.email}`);
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
    const repository = this.requireRepository();
    if (this.missingRequirements().length > 0) {
      throw this.failure(
        AccountCredentialsOperation.Register,
        this.requirements.requirementsUnmet.requirement,
        'Requirements are unmet',
      );
    }
    if (await repository.load(this.email)) {
      throw this.failure(
        AccountCredentialsOperation.Register,
        this.requirements.emailAlreadyRegistered.requirement,
        'Email is already registered',
      );
    }
    this.verified = false;
    this.customerId = null;
    this.token = null;
    this.emailValidationCode();
    await repository.create(this);
  }

  async verify(validationCode: ValidationCode): Promise<Customer> {
    const repository = this.requireRepository();
    if (!this.validationCodeWasSent) throw this.validationCodeError('No validation code has been sent.');
    this.validationCode = validationCode.code;
    const rejected = REJECTED_VALIDATION_CODES[this.validationCode];
    if (rejected) throw this.validationCodeError(this.requirements[rejected].requirement);
    if (this.expectedValidationCode !== this.validationCode) {
      throw this.validationCodeError(this.requirements.validationCodeMismatch.requirement);
    }
    this.verified = true;
    await repository.update(this);
    await this.newCustomer();
    await this.authenticateAccount();
    if (!this.customer) throw new Error('Customer was not created');
    return this.customer;
  }

  async authenticateAccount(): Promise<void> {
    const repository = this.requireRepository();
    if (this.unmetSignInRequirements().length > 0) {
      throw this.failure(
        AccountCredentialsOperation.SignIn,
        this.requirements.requirementsUnmet.requirement,
        'Requirements are unmet',
      );
    }
    const stored = await repository.load(this.email);
    if (!stored || stored.password !== this.password) {
      throw this.failure(
        AccountCredentialsOperation.SignIn,
        this.requirements.signInMismatch.requirement,
        'Credentials do not match',
      );
    }
    this.verified = stored.verified;
    this.customerId = stored.customerId;
    this.customer = stored.customer ?? this.customer;
    if (this.customer) this.customer.accountCredentials = this;
    this._validationCodeSentAt = stored._validationCodeSentAt;
    this.expectedValidationCode = stored.expectedValidationCode;
    this.validationCodeMessages.splice(0, this.validationCodeMessages.length, ...stored.validationCodeMessages);
    this.issueSessionToken();
    await repository.update(this);
  }

  async resendValidationCode(): Promise<void> {
    const repository = this.requireRepository();
    const sentAt = this._validationCodeSentAt;
    if (sentAt && Date.now() - sentAt.getTime() < AccountCredentials.RESEND_WAIT_MILLISECONDS) {
      throw new ValidationCodeResendWaitException(
        new Date(sentAt.getTime() + AccountCredentials.RESEND_WAIT_MILLISECONDS),
      );
    }
    this.emailValidationCode();
    this.resendMessage = this.requirements.resendSent.requirement;
    await repository.update(this);
  }

  async signOut(): Promise<void> {
    this.token = null;
    await this._repository?.update(this);
  }

  async storeCustomerId(customerId: string): Promise<void> {
    this.customerId = customerId;
    if (this.token) this.token.customerId = customerId;
    await this._repository?.update(this);
  }

  /** Fluent cross-aggregate exception: verify creates the Customer and its Onboarding. */
  private async newCustomer(): Promise<Customer> {
    const customer = await this.requireRepository().customerRepository.create(this);
    const { onboardingRepository } = await import('../onboarding/onboarding');
    onboardingRepository.create(customer);
    this.customer = customer;
    await this.requireRepository().update(this);
    return customer;
  }

  private requireRepository(): AccountCredentialsRepository {
    if (!this._repository) throw new Error('AccountCredentials has no repository. Use accountCredentialsRepository.new().');
    return this._repository;
  }

  private unmetSignInRequirements(): AccountCredentialRequirement[] {
    return this.missingRequirements().filter(
      r =>
        r === this.requirements.emailRequired ||
        r === this.requirements.emailFormat ||
        r === this.requirements.passwordRequired,
    );
  }

  private validationCodeError(message: string): AccountCredentialsException {
    return this.failure(AccountCredentialsOperation.ValidationCode, message, message);
  }

  private failure(
    operation: AccountCredentialsOperation,
    message: string,
    cause: string,
  ): AccountCredentialsException {
    return new AccountCredentialsException(operation, this, message, new Error(cause));
  }
}

export class ValidationCodeResendWaitException extends Error {
  constructor(public readonly availableAt: Date) {
    super('Validation code cannot be resent before the 60-second wait has elapsed.');
    this.name = 'ValidationCodeResendWaitException';
  }
}

export const AccountCredentialsOperation = {
  Register: 'register',
  SignIn: 'signIn',
  ValidationCode: 'validationCode',
} as const;
export type AccountCredentialsOperation = (typeof AccountCredentialsOperation)[keyof typeof AccountCredentialsOperation];

export class AccountCredentialsException extends Error {
  constructor(
    public readonly operation: AccountCredentialsOperation,
    public readonly accountCredentials: AccountCredentials,
    message: string,
    public readonly cause: Error,
  ) {
    super(message);
    this.name = 'AccountCredentialsException';
  }
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
  signInMismatch: AccountCredentialRequirement;
  emailAlreadyRegistered: AccountCredentialRequirement;
  requirementsUnmet: AccountCredentialRequirement;
  validationCodeMismatch: AccountCredentialRequirement;
  validationCodeAttempts: AccountCredentialRequirement;
  resendSent: AccountCredentialRequirement;
  resendWait: AccountCredentialRequirement;
}

const REJECTED_VALIDATION_CODES: Record<string, 'validationCodeMismatch' | 'validationCodeAttempts'> = {
  '000000': 'validationCodeMismatch',
  '111111': 'validationCodeMismatch',
  '222222': 'validationCodeAttempts',
};

type StoredAccount = {
  email: string;
  password: string;
  confirmPassword: string;
  validationCode: string;
  verified: boolean;
  customerId: string | null;
  token: AccountToken | null;
  _validationCodeSentAt: Date | null;
  expectedValidationCode: string | null;
  validationCodeMessages: ValidationCodeMessage[];
};

export class AccountCredentialsRepository {
  constructor(readonly customerRepository: CustomerRepository = new CustomerRepository()) {}

  private readonly accounts = new Map<string, StoredAccount>();

  new(): AccountCredentials {
    const accountCredentials = new AccountCredentials();
    accountCredentials._repository = this;
    return accountCredentials;
  }

  async create(accountCredentials: AccountCredentials): Promise<AccountCredentials> {
    if (this.accounts.has(accountCredentials.email)) {
      throw new AccountCredentialsException(
        AccountCredentialsOperation.Register,
        accountCredentials,
        accountCredentials.requirements.emailAlreadyRegistered.requirement,
        new Error('Email is already registered'),
      );
    }
    this.saveSnapshot(accountCredentials);
    return accountCredentials;
  }

  async load(email: string): Promise<AccountCredentials | null> {
    const stored = this.accounts.get(email);
    if (!stored) return null;
    return this.restore(stored);
  }

  find(email: string): AccountCredentials | null {
    const stored = this.accounts.get(email);
    if (!stored) return null;
    return this.restore(stored);
  }

  async update(accountCredentials: AccountCredentials): Promise<AccountCredentials> {
    if (!this.accounts.has(accountCredentials.email)) return accountCredentials;
    this.saveSnapshot(accountCredentials);
    return accountCredentials;
  }

  /** @testControl Empty account the test fills, then stores with `_seed`. */
  _empty(): AccountCredentials {
    return this.new();
  }

  /** @testControl Persist an account the test already filled. */
  _seed(accountCredentials: AccountCredentials): void {
    this.saveSnapshot(accountCredentials);
  }

  /** @testControl */
  _reset(): void {
    this.accounts.clear();
  }

  private saveSnapshot(accountCredentials: AccountCredentials): void {
    this.accounts.set(accountCredentials.email, {
      email: accountCredentials.email,
      password: accountCredentials.password,
      confirmPassword: accountCredentials.confirmPassword,
      validationCode: accountCredentials.validationCode,
      verified: accountCredentials.verified,
      customerId: accountCredentials.customer?.id || accountCredentials.customerId,
      token: accountCredentials.token
        ? new AccountToken(accountCredentials.token.email, accountCredentials.token.customerId, accountCredentials.token.jwt)
        : null,
      _validationCodeSentAt: accountCredentials._validationCodeSentAt,
      expectedValidationCode: accountCredentials.expectedValidationCode,
      validationCodeMessages: accountCredentials.validationCodeMessages.map(message => {
        const copy = new ValidationCodeMessage(message.sentAt, message.email, message.code);
        copy.executed = message.executed;
        return copy;
      }),
    });
  }

  private restore(stored: StoredAccount): AccountCredentials {
    const account = new AccountCredentials(
      stored.email,
      stored.password,
      stored.confirmPassword,
      stored.validationCode,
      stored.verified,
    );
    account.customerId = stored.customerId;
    account.token = stored.token
      ? new AccountToken(stored.token.email, stored.token.customerId, stored.token.jwt)
      : null;
    account._validationCodeSentAt = stored._validationCodeSentAt;
    account.expectedValidationCode = stored.expectedValidationCode;
    account.validationCodeMessages.push(...stored.validationCodeMessages);
    account._repository = this;
    return account;
  }
}

export const accountCredentialsRepository = new AccountCredentialsRepository();
