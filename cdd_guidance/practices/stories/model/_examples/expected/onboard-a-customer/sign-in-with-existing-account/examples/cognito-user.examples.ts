import { CognitoUser } from '../../../../domain/systems/Cognito/Cognito';
import { enteredAlreadyRegisteredAccountCredentials } from '../../examples/account-credentials.examples';

export const storedAlreadyRegisteredCognitoUser = new CognitoUser(
  enteredAlreadyRegisteredAccountCredentials.email,
  true,
  'cus_stub_pml_my_001',
  null,
);
