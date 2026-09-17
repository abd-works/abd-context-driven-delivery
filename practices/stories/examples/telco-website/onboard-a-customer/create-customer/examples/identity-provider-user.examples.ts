/**
 * ++Identity provider user++ examples — shared across Create Customer stories.
 */

import { validAccountCredentials } from './account-credentials.examples';

export const unconfirmedIdentityUser = {
  email: validAccountCredentials.email,
  confirmed: false,
  customerId: null,
};
