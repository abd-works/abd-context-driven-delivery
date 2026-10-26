/**
 * ++Account credentials++ examples for Create Unconfirmed User.
 *
 * Names say the role: entered (When input), stored (Given backend), expected (Then).
 * When entered and expected are the same value, both names alias the same object.
 */

import { AccountToken, CognitoUser } from '../../../domain/systems/Cognito/Cognito';
import { AccountCredentials } from '../../../domain/customer/Customer';
import { amplifyService } from '../../../domain/systems/amplify';

export const enteredValidAccountCredentials = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'Spider-man99p',
  'Spider-man99p',
  '',
  false
);
export const expectedValidAccountCredentials = enteredValidAccountCredentials;

export const enteredAlreadyRegisteredAccountCredentials = new AccountCredentials(
  'Jeff.anderson@Agilebydesign.com',
  'Stub@12345',
  'Stub@12345',
  '',
  true
);
export const expectedAlreadyRegisteredAccountCredentials = enteredAlreadyRegisteredAccountCredentials;

export const enteredInvalidPasswordLetters = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'spider-man99p',
  'spider-man99p',
  '',
  false
);

export const enteredInvalidPasswordNumber = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'Spider-manpp',
  'Spider-manpp',
  '',
  false
);

export const enteredInvalidPasswordSymbol = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'Spiderman99',
  'Spiderman99',
  '',
  false
);

export const enteredInvalidPasswordLength = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'Sp1!Man',
  'Sp1!Man',
  '',
  false
);

export const enteredInvalidConfirmRequired = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'Spider-man99p',
  '',
  '',
  false
);

export const enteredInvalidConfirmMismatch = new AccountCredentials(
  'Jeff.anderson@Abdworks.com',
  'Spider-man99p',
  'Spider-man00p',
  '',
  false
);

export const enteredInvalidEmailRequired = new AccountCredentials(
  '',
  'Spider-man99p',
  'Spider-man99p',
  '',
  false
);

export const enteredInvalidEmailFormat = new AccountCredentials(
  'example.prospect',
  'Spider-man99p',
  'Spider-man99p',
  '',
  false
);

export const enteredNonExistentAccountCredentials = new AccountCredentials(
  'unknown.user@paradise.com',
  'Spider-man99p',
  'Spider-man99p',
  '',
  false
);

export const enteredWrongPasswordAccountCredentials = new AccountCredentials(
  enteredAlreadyRegisteredAccountCredentials.email,
  'Wrong#Pass1',
  'Wrong#Pass1',
  '',
  true
);

export const enteredUnknownEmailAccountCredentials = new AccountCredentials(
  'unknown.prospect@example.com',
  'Stub@12345',
  'Stub@12345',
  '',
  false
);

export const incorrectCredentialOutlines = [
  { example: 'wrong password', credentials: enteredWrongPasswordAccountCredentials },
  { example: 'unknown email', credentials: enteredUnknownEmailAccountCredentials },
];

/** Seeds a stored Cognito user with an account token and returns credentials wrapping that user. */
export function storedAccountCredentialsWithToken(customerId: string | null = 'cus_1'): AccountCredentials {
  const cognitoUser = amplifyService.seedCognitoUser(
    new CognitoUser(
      enteredValidAccountCredentials.email,
      true,
      customerId,
      new AccountToken(
        enteredValidAccountCredentials.email,
        customerId,
        `token:${enteredValidAccountCredentials.email}`,
      ),
    ),
  );
  return new AccountCredentials(cognitoUser);
}
