/**
 * ++Account credentials++ examples — shared across Create Customer stories.
 *
 * One named export per scenario branch; story specs import these.
 * Source: create-unconfirmed-user/story-scenarios.md Examples tables.
 */

export const validAccountCredentials = {
  email: 'prospect@example.com',
  password: 'Valid-pass99',
  confirmPassword: 'Valid-pass99',
  verified: false,
};

export const invalidPasswordLength = {
  email: 'prospect@example.com',
  password: 'Sh0rt!',
  confirmPassword: 'Sh0rt!',
  verified: false,
};

export const invalidConfirmMismatch = {
  email: 'prospect@example.com',
  password: 'Valid-pass99',
  confirmPassword: 'Other-pass99',
  verified: false,
};
