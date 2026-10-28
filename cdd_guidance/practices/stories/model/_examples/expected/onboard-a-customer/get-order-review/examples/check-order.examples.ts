import type { CartOpts } from '../../get-number/examples/cart.examples';
import { stubBundle } from '../../get-number/examples/cart.examples';
import {
  enteredChosenAvailableNumber,
  storedHeldAvailableNumber,
} from '../../get-number/examples/available-number.examples';
import { enteredValidPortability } from '../../get-number/examples/portability.examples';

export interface CheckOrderOutline {
  example: string;
  opts: CartOpts;
  expectedMsisdn: string;
  expectedPortNumber?: string;
}

export const checkOrderOutlines: CheckOrderOutline[] = [
  {
    example: 'new number',
    opts: {
      bundleId: stubBundle.id,
      msisdn: enteredChosenAvailableNumber,
      simType: 'eSIM',
      idNumber: 'ID12345',
    },
    expectedMsisdn: enteredChosenAvailableNumber,
  },
  {
    example: 'port-in number',
    opts: {
      bundleId: stubBundle.id,
      msisdn: storedHeldAvailableNumber,
      portNumber: enteredValidPortability.portNumber,
      donorOperator: enteredValidPortability.donorOperator,
      accountNumber: enteredValidPortability.accountNumber,
      userType: enteredValidPortability.userType,
      accountType: enteredValidPortability.accountType,
      device: enteredValidPortability.device,
      portabilityVerified: true,
      simType: 'eSIM',
      idNumber: 'ID12345',
    },
    expectedMsisdn: storedHeldAvailableNumber,
    expectedPortNumber: enteredValidPortability.portNumber,
  },
];
