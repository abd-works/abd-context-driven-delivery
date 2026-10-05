import {
  AccountCredentials,
  AccountCredentialsRepository,
  accountCredentialsRepository,
} from './account-credentials';
import { CustomerRepository } from '../customer/customer';
import { OnboardingStep } from '../onboarding/onboarding-step';

export { accountCredentialsRepository, AccountCredentialsRepository, CustomerRepository };

export const SIGN_UP_PATH = '/sign-up/';
export const SIGN_IN_PATH = '/sign-in';
export const ENTER_VALIDATION_CODE_PATH = '/onboarding/enter-validation-code';

export type AccountCredentialsDestinationEntry = 'landing' | 'protected';

export type ParadiseDestination = {
  onboardingPath: string;
  step: OnboardingStep | null;
};

export type ParadiseRequest = {
  headers?: { cookie?: string };
  paradise?: {
    accountCredentials?: AccountCredentialsNode;
    customer?: import('../customer/customer-node').CustomerNode;
    onboarding?: import('../onboarding/onboarding-node').OnboardingNode;
  };
};

const PARADISE_COOKIE = 'paradise';

declare module 'express-serve-static-core' {
  interface Request extends ParadiseRequest {}
}

export function paradiseSessionCookie(email: string): string {
  return `${PARADISE_COOKIE}=${encodeURIComponent(email)}; Path=/; HttpOnly; SameSite=Lax`;
}

export function clearParadiseSessionCookie(): string {
  return `${PARADISE_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax`;
}

export function paradiseSessionEmail(req: ParadiseRequest): string | undefined {
  const cookie = req.headers?.cookie;
  if (!cookie) return undefined;
  const part = cookie.split(';').map(entry => entry.trim()).find(entry => entry.startsWith(`${PARADISE_COOKIE}=`));
  if (!part) return undefined;
  return decodeURIComponent(part.slice(PARADISE_COOKIE.length + 1));
}

const AUTH_PATH_BY_STEP: Partial<Record<OnboardingStep, string>> = {
  [OnboardingStep.VerifyAccount]: ENTER_VALIDATION_CODE_PATH,
};

export function asAccountCredentialsNode(accountCredentials: AccountCredentials): AccountCredentialsNode {
  Object.setPrototypeOf(accountCredentials, AccountCredentialsNode.prototype);
  return accountCredentials as AccountCredentialsNode;
}

/** Node AccountCredentials — maps auth onboarding steps to browser routes. */
export class AccountCredentialsNode extends AccountCredentials {
  /**
   * Auth destination from request session and entry point.
   * Returns null when the account is verified and Customer routing should take over.
   */
  static destination(
    req: ParadiseRequest,
    entry: AccountCredentialsDestinationEntry,
  ): ParadiseDestination | null {
    req.paradise ??= {};
    if (req.paradise.accountCredentials) {
      req.paradise.accountCredentials = asAccountCredentialsNode(req.paradise.accountCredentials);
    }
    const accountCredentials = req.paradise.accountCredentials;
    if (!accountCredentials) {
      return {
        onboardingPath: entry === 'landing' ? SIGN_UP_PATH : SIGN_IN_PATH,
        step: null,
      };
    }
    return accountCredentials.authDestination();
  }

  /** Auth destination when an account is in session but Customer does not exist yet. */
  authDestination(): ParadiseDestination | null {
    const onboardingPath = this.authOnboardingPath();
    if (!onboardingPath) return null;
    return {
      onboardingPath,
      step: this.onboardingStep ?? OnboardingStep.VerifyAccount,
    };
  }

  private authOnboardingPath(): string | null {
    if (this.onboardingStep === OnboardingStep.VerifyAccount) {
      return AUTH_PATH_BY_STEP[OnboardingStep.VerifyAccount] ?? null;
    }
    if (!this.verified && this.validationCodeWasSent) {
      return AUTH_PATH_BY_STEP[OnboardingStep.VerifyAccount] ?? null;
    }
    return null;
  }
}
