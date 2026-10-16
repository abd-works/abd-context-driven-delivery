/**
 * Authenticate User — Node tier.
 * Tier-only scenarios run before shared ones; extensions only where routing continues a shared scenario.
 */

import { expect } from 'vitest';
import request from 'supertest';
import type { Response } from 'supertest';
import { accountCredentialsRepository, SIGN_UP_PATH } from '@src/account-credentials/account-credentials-node';
import { runAll, scenario, withScenario, withStory } from 'tests/story-test';
import { appWithSession } from './examples/session.examples';
import './authenticate_user.story.shared';

withStory('Create Account', () => {
  scenario('Customer navigates to Paradise Mobile', ({ given, then }) => {
    let response: Response;
    given('the Customer navigates to Paradise Mobile', async () => {
      response = await request(appWithSession()).get('/destination');
    });
    then('My Paradise returns the sign-up path', () => {
      expect(response.status).toBe(200);
      expect(response.body.onboardingPath).toBe(SIGN_UP_PATH);
    });
  });
  runAll();
});

withStory('Enter Validation Code').run();

withStory('Sign In With Existing Account', () => {
  withScenario('Sign in with already-registered account credentials').run();
  withScenario('Email format is unmet').run();
  withScenario('Authenticate with incorrect account credentials: wrong password').run();
  withScenario('Authenticate with incorrect account credentials: unknown email').run();
  withScenario('Authenticate with unconfirmed account').and(
    'My Paradise returns user tothe enter validation code screen',
    async () => {
      const accountCredentials = await accountCredentialsRepository.load('Jeff.anderson@Abdworks.com');
      const response = await request(appWithSession(accountCredentials!)).get('/onboarding/destination');
      expect(response.body.onboardingPath).toBe('/onboarding/enter-validation-code');
      expect(response.body.step).toBe('VerifyAccount');
    },
  );
});
