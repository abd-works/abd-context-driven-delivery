// portability examples from enter_porting_number_story.spec.md
// | portability | example          | donorOperator | portNumber | accountNumber | userType    | accountType | device |
// | portability | valid portability | Digicel       | 4412345678 | 12345         | Residential | Postpaid    | Iphone |

import {
  Portability,
  DonorOperator,
  UserType,
  AccountType,
  Device,
} from '../../../../domain/number/Portability';
import { PortabilityStatus } from '../../../../domain/systems/twilio';
import { storedHeldAvailableNumber } from './available-number.examples';

export const enteredValidPortability = new Portability(
  DonorOperator.Digicel,
  '4412345678',
  '12345',
  UserType.Residential,
  AccountType.Postpaid,
  Device.Iphone,
);
export const expectedValidPortability = enteredValidPortability;

export type PortErrorOutline = {
  example: string;
  portNumber: string;
  donorOperator: DonorOperator;
  accountNumber: string;
  userType: UserType;
  accountType: AccountType;
  device: Device;
  mavenirResult: string | Error | undefined;
  twilioResult: PortabilityStatus | undefined;
  expectedMessage: string;
};

export const portErrorOutlines: PortErrorOutline[] = [
  {
    example: 'incomplete portNumber',
    portNumber: '441', donorOperator: DonorOperator.Digicel, accountNumber: '12345',
    userType: UserType.Residential, accountType: AccountType.Postpaid, device: Device.Iphone,
    mavenirResult: undefined,
    twilioResult: undefined,
    expectedMessage: 'Please enter the full Bermuda number.',
  },
  {
    example: 'no provider selected',
    portNumber: '4412345678', donorOperator: '' as DonorOperator, accountNumber: '12345',
    userType: UserType.Residential, accountType: AccountType.Postpaid, device: Device.Iphone,
    mavenirResult: undefined,
    twilioResult: undefined,
    expectedMessage: 'Please select a provider.',
  },
  {
    example: 'port number not SMS-capable',
    portNumber: enteredValidPortability.portNumber, donorOperator: enteredValidPortability.donorOperator,
    accountNumber: enteredValidPortability.accountNumber, userType: enteredValidPortability.userType,
    accountType: enteredValidPortability.accountType, device: enteredValidPortability.device,
    mavenirResult: storedHeldAvailableNumber,
    twilioResult: PortabilityStatus.InvalidNumber,
    expectedMessage: 'This number cannot receive SMS messages.',
  },
  {
    example: 'Mavenir POST /portability fails',
    portNumber: enteredValidPortability.portNumber, donorOperator: enteredValidPortability.donorOperator,
    accountNumber: enteredValidPortability.accountNumber, userType: enteredValidPortability.userType,
    accountType: enteredValidPortability.accountType, device: enteredValidPortability.device,
    mavenirResult: new Error('Failed to save portability'),
    twilioResult: undefined,
    expectedMessage: 'Failed to save portability',
  },
];
