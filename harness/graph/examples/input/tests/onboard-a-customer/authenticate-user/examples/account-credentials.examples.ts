/**
 * Account credentials examples.
 * Each function fills a real account from the repository. `seed*` stores it.
 */

import {
  AccountCredentials,
  type AccountCredentialRequirements,
  type AccountCredentialsRepository,
} from '@src/account-credentials/account-credentials';
import { asAccountCredentialsNode, type AccountCredentialsNode } from '@src/account-credentials/account-credentials-node';

/** Unverified account ready to register. Not stored. */
export function unverifiedAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = repo._empty();
  accountCredentials.email = 'Jeff.anderson@Abdworks.com';
  accountCredentials.password = 'Spider-man99p';
  accountCredentials.confirmPassword = 'Spider-man99p';
  return accountCredentials;
}

/** Verified account that already holds a customer id. Not stored. */
export function verifiedAccountCredentials(repo: AccountCredentialsRepository): AccountCredentialsNode {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.verified = true;
  accountCredentials.customerId = 'cus_1';
  return asAccountCredentialsNode(accountCredentials);
}

/** Verified account stored so a later step can load it. */
export function seedVerifiedAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = verifiedAccountCredentials(repo);
  repo._seed(accountCredentials);
  return accountCredentials;
}

/** Already-registered account the customer types at sign-in. Not stored. */
export function alreadyRegisteredAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = repo._empty();
  accountCredentials.email = 'Jeff.anderson@Agilebydesign.com';
  accountCredentials.password = 'Stub@12345';
  accountCredentials.confirmPassword = 'Stub@12345';
  accountCredentials.verified = true;
  return accountCredentials;
}

/** Already-registered account stored so sign-in can load it. */
export function seedAlreadyRegisteredAccountCredentials(
  repo: AccountCredentialsRepository,
  customerId: string | null = null,
): AccountCredentials {
  const accountCredentials = alreadyRegisteredAccountCredentials(repo);
  accountCredentials.customerId = customerId;
  repo._seed(accountCredentials);
  return accountCredentials;
}

export function missingEmailAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.email = '';
  return accountCredentials;
}

export function invalidEmailFormatAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.email = 'example.prospect';
  return accountCredentials;
}

export function missingPasswordAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.password = '';
  accountCredentials.confirmPassword = '';
  return accountCredentials;
}

export function passwordMissingLettersAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.password = 'spider-man99p';
  accountCredentials.confirmPassword = 'spider-man99p';
  return accountCredentials;
}

export function passwordMissingNumberAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.password = 'Spider-manpp';
  accountCredentials.confirmPassword = 'Spider-manpp';
  return accountCredentials;
}

export function passwordMissingSymbolAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.password = 'Spiderman99';
  accountCredentials.confirmPassword = 'Spiderman99';
  return accountCredentials;
}

export function passwordTooShortAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.password = 'Sp1!Man';
  accountCredentials.confirmPassword = 'Sp1!Man';
  return accountCredentials;
}

export function missingConfirmPasswordAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.confirmPassword = '';
  return accountCredentials;
}

export function confirmPasswordMismatchAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = unverifiedAccountCredentials(repo);
  accountCredentials.confirmPassword = 'Spider-man00p';
  return accountCredentials;
}

export function wrongPasswordAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = alreadyRegisteredAccountCredentials(repo);
  accountCredentials.password = 'Wrong#Pass1';
  accountCredentials.confirmPassword = 'Wrong#Pass1';
  return accountCredentials;
}

export function unknownEmailAccountCredentials(repo: AccountCredentialsRepository): AccountCredentials {
  const accountCredentials = alreadyRegisteredAccountCredentials(repo);
  accountCredentials.email = 'unknown.prospect@example.com';
  accountCredentials.verified = false;
  return accountCredentials;
}

type IncorrectSignInOutlineCase = {
  example: string;
  email: string;
  password: string;
};

type IncorrectSignInOutlineRow = IncorrectSignInOutlineCase & {
  build: (repo: AccountCredentialsRepository) => AccountCredentials;
};

const incorrectSignInOutlineRows: IncorrectSignInOutlineRow[] = [
  {
    example: 'wrong password',
    email: 'Jeff.anderson@Agilebydesign.com',
    password: 'Wrong#Pass1',
    build: wrongPasswordAccountCredentials,
  },
  {
    example: 'unknown email',
    email: 'unknown.prospect@example.com',
    password: 'Stub@12345',
    build: unknownEmailAccountCredentials,
  },
];

/** Scenario outline cases for sign-in with incorrect credentials. */
export function incorrectSignInOutlineCases(): IncorrectSignInOutlineCase[] {
  return incorrectSignInOutlineRows.map(({ example, email, password }) => ({
    example,
    email,
    password,
  }));
}

/** Scenario outline: Authenticate with incorrect account credentials */
export function incorrectSignInOutlines(
  repo: AccountCredentialsRepository,
  example: string,
): AccountCredentials {
  const row = incorrectSignInOutlineRows.find(entry => entry.example === example);
  if (!row) {
    throw new Error(`Unknown incorrect sign-in outline: ${example}`);
  }
  return row.build(repo);
}

type InvalidAccountCredentialsOutlineCase = {
  example: string;
  unmet: keyof AccountCredentialRequirements;
  email: string;
  password: string;
  confirmPassword: string;
};

type InvalidAccountCredentialsOutlineRow = InvalidAccountCredentialsOutlineCase & {
  build: (repo: AccountCredentialsRepository) => AccountCredentials;
};

const invalidAccountCredentialsOutlineRows: InvalidAccountCredentialsOutlineRow[] = [
  { example: 'missing email', unmet: 'emailRequired', email: '', password: 'Spider-man99p', confirmPassword: 'Spider-man99p', build: missingEmailAccountCredentials },
  { example: 'invalid email format', unmet: 'emailFormat', email: 'example.prospect', password: 'Spider-man99p', confirmPassword: 'Spider-man99p', build: invalidEmailFormatAccountCredentials },
  { example: 'missing password', unmet: 'passwordRequired', email: 'Jeff.anderson@Abdworks.com', password: '', confirmPassword: '', build: missingPasswordAccountCredentials },
  { example: 'password missing letters', unmet: 'passwordLetters', email: 'Jeff.anderson@Abdworks.com', password: 'spider-man99p', confirmPassword: 'spider-man99p', build: passwordMissingLettersAccountCredentials },
  { example: 'password missing number', unmet: 'passwordNumber', email: 'Jeff.anderson@Abdworks.com', password: 'Spider-manpp', confirmPassword: 'Spider-manpp', build: passwordMissingNumberAccountCredentials },
  { example: 'password missing symbol', unmet: 'passwordSymbol', email: 'Jeff.anderson@Abdworks.com', password: 'Spiderman99', confirmPassword: 'Spiderman99', build: passwordMissingSymbolAccountCredentials },
  { example: 'password too short', unmet: 'passwordLength', email: 'Jeff.anderson@Abdworks.com', password: 'Sp1!Man', confirmPassword: 'Sp1!Man', build: passwordTooShortAccountCredentials },
  { example: 'confirm password missing', unmet: 'confirmRequired', email: 'Jeff.anderson@Abdworks.com', password: 'Spider-man99p', confirmPassword: '', build: missingConfirmPasswordAccountCredentials },
  { example: 'confirm password mismatch', unmet: 'confirmMismatch', email: 'Jeff.anderson@Abdworks.com', password: 'Spider-man99p', confirmPassword: 'Spider-man00p', build: confirmPasswordMismatchAccountCredentials },
];

/** Scenario outline cases for registration. */
export function invalidAccountCredentialsOutlineCases(): InvalidAccountCredentialsOutlineCase[] {
  return invalidAccountCredentialsOutlineRows.map(({ example, unmet, email, password, confirmPassword }) => ({
    example,
    unmet,
    email,
    password,
    confirmPassword,
  }));
}

/** Scenario outline: Enter Invalid account credentials */
export function invalidAccountCredentialsOutlines(
  repo: AccountCredentialsRepository,
  example: string,
): AccountCredentials {
  const row = invalidAccountCredentialsOutlineRows.find(entry => entry.example === example);
  if (!row) {
    throw new Error(`Unknown invalid account credentials outline: ${example}`);
  }
  return row.build(repo);
}
