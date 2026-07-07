// validate-destination-account-stories.ts — typed story data.
// Specification fidelity: all scenario paths. No test implementation.

import type { Story } from '../../../templates/ts/story-types'

export const ValidateDestinationAccount = {
  story:       'Validate destination account',
  actor:       'Treasurer',
  domainTerms: ['Destination Account', 'Validation', 'Recipient', 'Transfer'],
  evidence:    ['Treasury product brief'],

  // ── Scenario 1 — happy path ────────────────────────────────────────────────
  mainFlow: {
    name: 'Treasurer validates a registered destination account',
    given: [
      'a Transfer draft with destination account "ACH-999"',
      'And destination account "ACH-999" is registered and active in the system',
    ],
    interactions: [
      {
        when: ['the Treasurer triggers destination account validation'],
        then: [
          'the destination account is confirmed as "VALID"',
          'And the Transfer draft remains in status "DRAFT"',
        ],
      },
    ],
  },

  // ── Scenario 2 — account not registered ───────────────────────────────────
  accountNotRegistered: {
    name: 'Treasurer attempts to validate an unregistered destination account',
    given: [
      'a Transfer draft with destination account "ACH-000"',
      'And destination account "ACH-000" is not registered in the system',
    ],
    interactions: [
      {
        when: ['the Treasurer triggers destination account validation'],
        then: [
          'the destination account is flagged as "INVALID"',
          'But the Transfer draft remains in status "DRAFT"',
          'And an error "Destination account ACH-000 is not registered" is shown',
        ],
      },
    ],
  },

  // ── Scenario 3 — account inactive ─────────────────────────────────────────
  accountInactive: {
    name: 'Treasurer attempts to validate an inactive destination account',
    given: [
      'a Transfer draft with destination account "ACH-888"',
      'And destination account "ACH-888" is registered but inactive',
    ],
    interactions: [
      {
        when: ['the Treasurer triggers destination account validation'],
        then: [
          'the destination account is flagged as "INVALID"',
          'But the Transfer draft remains in status "DRAFT"',
          'And an error "Destination account ACH-888 is inactive" is shown',
        ],
      },
    ],
  },
} as const satisfies Story
