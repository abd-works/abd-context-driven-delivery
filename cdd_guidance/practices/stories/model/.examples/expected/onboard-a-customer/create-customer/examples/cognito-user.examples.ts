/**
 * Stored ++Cognito user++ examples (Given backend state).
 */

import { CognitoUser, AccountToken } from '../../../../domain/systems/Cognito/Cognito';
import {
  enteredValidAccountCredentials,
  enteredAlreadyRegisteredAccountCredentials,
} from '../../examples/account-credentials.examples';

export const storedUnconfirmedCognitoUser = new CognitoUser(
  enteredValidAccountCredentials.email,
  false,
  null,
  null
);

export const storedConfirmedCognitoUser = new CognitoUser(
  enteredValidAccountCredentials.email,
  true,
  null,
  null
);

export const storedAlreadyRegisteredUnconfirmedCognitoUser = new CognitoUser(
  enteredAlreadyRegisteredAccountCredentials.email,
  false,
  null,
  null,
);

export const storedCognitoUserWithAccountToken = new CognitoUser(
  enteredValidAccountCredentials.email,
  true,
  'cus_stub_pml_my_001',
  new AccountToken(enteredValidAccountCredentials.email, 'cus_stub_pml_my_001')
);
