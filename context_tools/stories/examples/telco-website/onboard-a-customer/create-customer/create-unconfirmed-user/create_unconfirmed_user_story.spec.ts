/**
 * Story: Create Unconfirmed User — golden fixture wiring (excerpt).
 *
 * Paradise Mobile reference:
 * `stories/onboard-a-customer/create-customer/create-unconfirmed-user/`
 */

import { background, scenario, story } from 'stories/story-test';
import {
  validAccountCredentials,
  invalidPasswordLength,
  invalidConfirmMismatch,
} from '../../examples/account-credentials.examples';
import { unconfirmedIdentityUser } from '../../examples/identity-provider-user.examples';
import { purchasablePlansExamples } from '../../examples/purchasable-plans.examples';

story('Enter Account Credentials', () => {
  background(({ given }) => {
    given('the plan catalog contains purchasable plans', async () => {
      await planRepository.seed(purchasablePlansExamples);
    });
  });

  scenario('Valid account credentials', ({ when, then }) => {
    when('the User validates ++account credentials++', () => {
      account = validAccountCredentials;
    });
    then('++account credentials++ are validated continuously', () => {
      expect(account.missingRequirements()).toHaveLength(0);
    });
  });

  scenario('Password too short', ({ when, then }) => {
    when('the User validates ++account credentials++', () => {
      account = invalidPasswordLength;
    });
    then('the password length rule is unmet', () => {
      expect(account.missingRequirements()).toContain('passwordLength');
    });
  });

  scenario('Confirm password mismatch', ({ when, then }) => {
    when('the User validates ++account credentials++', () => {
      account = invalidConfirmMismatch;
    });
    then('the confirm-password rule is unmet', () => {
      expect(account.missingRequirements()).toContain('confirmMismatch');
    });
  });

  // After create: assert against unconfirmedIdentityUser — not a fresh inline object.
});
