// validate-destination-account-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const ValidateDestinationAccount = {
  story:       'Validate destination account',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Destination Account', 'Validation Status', 'Draft'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer validates a registered destination account',
    given: [
      'Transfer T-001 has Destination Account "ACH-999"',
      'And Destination Account "ACH-999" is registered and active in the system',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice validates the Destination Account on Transfer T-001'],
        then: [
          'Transfer T-001 has Validation Status "Valid"',
          'And Transfer T-001 remains in status "Draft"',
        ],
      },
    ],
  },
} as const satisfies Story
