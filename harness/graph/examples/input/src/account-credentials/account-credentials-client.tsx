import {
  AccountCredentialRequirements,
  AccountCredentials,
  AccountCredentialsException,
  AccountCredentialsOperation,
  ValidationCode,
  ValidationCodeResendWaitException,
  type AccountCredentialRequirement,
} from './account-credentials';
import { Customer } from '../customer/customer';
import { CustomerClient } from '../customer/customer-client';

export type AccountCredentialField = 'email' | 'password' | 'confirmPassword';

export type AccountCredentialRequirementLine = {
  key: keyof AccountCredentialRequirements;
  requirement: AccountCredentialRequirement;
  met: boolean;
  touched: boolean;
  tone: 'neutral' | 'met' | 'unmet';
};

/** Browser AccountCredentials — live field entry, visible rules, and host operations. */
export class AccountCredentialsClient extends AccountCredentials {
  emailTouched = false;
  passwordTouched = false;
  confirmPasswordTouched = false;
  operationError: string | null = null;
  isSubmitting = false;

  snapshot(): AccountCredentialsClient {
    return this.replace({});
  }

  enterEmail(email: string): AccountCredentialsClient {
    return this.replace({ email, emailTouched: true, operationError: null });
  }

  enterPassword(password: string): AccountCredentialsClient {
    return this.replace({ password, passwordTouched: true, operationError: null });
  }

  enterConfirmPassword(confirmPassword: string): AccountCredentialsClient {
    return this.replace({ confirmPassword, confirmPasswordTouched: true, operationError: null });
  }

  enterValidationCode(validationCode: string): AccountCredentialsClient {
    return this.replace({ validationCode, operationError: null });
  }

  touchEmail(): AccountCredentialsClient {
    return this.replace({ emailTouched: true });
  }

  touchPassword(): AccountCredentialsClient {
    return this.replace({ passwordTouched: true });
  }

  touchConfirmPassword(): AccountCredentialsClient {
    return this.replace({ confirmPasswordTouched: true });
  }

  requirementLines(field: AccountCredentialField): AccountCredentialRequirementLine[] {
    const missing = new Set(this.missingRequirements());
    const touched = this.touched(field);
    return (Object.keys(this.requirements) as Array<keyof AccountCredentialRequirements>)
      .filter(key => this.requirements[key].field === field && this.isRequirementVisible(key))
      .map(key => {
        const requirement = this.requirements[key];
        const met = !missing.has(requirement);
        return {
          key,
          requirement,
          met,
          touched,
          tone: touched ? (met ? 'met' : 'unmet') : 'neutral',
        };
      });
  }

  get signInError(): string | null {
    return this.operationError;
  }

  get registerError(): string | null {
    return this.operationError;
  }

  get validationCodeError(): string | null {
    return this.operationError;
  }

  get showsSignInRetryHint(): boolean {
    return this.operationError === this.requirements.signInMismatch.requirement;
  }

  async register(): Promise<void> {
    await this.postOperation(
      '/api/account/register',
      {
        email: this.email,
        password: this.password,
        confirmPassword: this.confirmPassword,
      },
      AccountCredentialsOperation.Register,
      this.requirements.emailAlreadyRegistered.requirement,
    );
    this.goToDestination();
  }

  async authenticateAccount(): Promise<void> {
    await this.postOperation(
      '/api/account/sign-in',
      { email: this.email, password: this.password },
      AccountCredentialsOperation.SignIn,
      this.requirements.signInMismatch.requirement,
    );
    this.goToDestination();
  }

  async verify(validationCode: ValidationCode): Promise<Customer> {
    this.validationCode = validationCode.code;
    await this.postOperation(
      '/api/account/verify',
      { validationCode: validationCode.code },
      AccountCredentialsOperation.ValidationCode,
      this.requirements.validationCodeMismatch.requirement,
    );
    this.verified = true;
    this.goToDestination();
    return new CustomerClient(this);
  }

  async resendValidationCode(): Promise<void> {
    const body = await this.postOperation(
      '/api/account/resend-validation-code',
      {},
      AccountCredentialsOperation.ValidationCode,
      this.requirements.resendWait.requirement,
    );
    this.resendMessage = typeof body.resendMessage === 'string'
      ? body.resendMessage
      : this.requirements.resendSent.requirement;
  }

  async signOut(): Promise<void> {
    await this.postOperation(
      '/api/account/sign-out',
      {},
      AccountCredentialsOperation.SignIn,
      this.requirements.signInMismatch.requirement,
    );
    this.token = null;
    this.goToDestination();
  }

  private goToDestination(): void {
    window.location.assign('/onboarding/destination/redirect');
  }

  private async postOperation(
    path: string,
    payload: Record<string, string>,
    operation: AccountCredentialsOperation,
    fallbackMessage: string,
  ): Promise<Record<string, unknown>> {
    this.operationError = null;
    this.isSubmitting = true;
    try {
      const response = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const body = await response.json().catch(() => ({}));
      if (response.ok) return body;
      const message = typeof body.message === 'string' ? body.message : fallbackMessage;
      throw this.hostFailure(operation, message);
    } catch (error) {
      if (error instanceof AccountCredentialsException) throw error;
      if (error instanceof ValidationCodeResendWaitException) throw error;
      throw this.hostFailure(operation, fallbackMessage, error);
    } finally {
      this.isSubmitting = false;
    }
  }

  private hostFailure(
    operation: AccountCredentialsOperation,
    message: string,
    cause?: unknown,
  ): AccountCredentialsException {
    this.operationError = message;
    return new AccountCredentialsException(
      operation,
      this,
      message,
      cause instanceof Error ? cause : new Error(message),
    );
  }

  private touched(field: AccountCredentialField): boolean {
    if (field === 'email') return this.emailTouched;
    if (field === 'password') return this.passwordTouched;
    return this.confirmPasswordTouched;
  }

  private isRequirementVisible(key: keyof AccountCredentialRequirements): boolean {
    const requirement = this.requirements[key];
    if (requirement.field === 'email') return this.emailTouched;
    if (requirement.field === 'confirmPassword') return this.confirmPasswordTouched;
    if (key === 'passwordRequired') return this.passwordTouched && !this.password;
    return true;
  }

  private replace(overrides: Partial<AccountCredentialsClient> & { validationCode?: string }): AccountCredentialsClient {
    const next = new AccountCredentialsClient(
      overrides.email ?? this.email,
      overrides.password ?? this.password,
      overrides.confirmPassword ?? this.confirmPassword,
      overrides.validationCode ?? this.validationCode,
      this.verified,
    );
    next.emailTouched = overrides.emailTouched ?? this.emailTouched;
    next.passwordTouched = overrides.passwordTouched ?? this.passwordTouched;
    next.confirmPasswordTouched = overrides.confirmPasswordTouched ?? this.confirmPasswordTouched;
    next.operationError = overrides.operationError === undefined ? this.operationError : overrides.operationError;
    next.isSubmitting = this.isSubmitting;
    next.resendMessage = this.resendMessage;
    return next;
  }
}
