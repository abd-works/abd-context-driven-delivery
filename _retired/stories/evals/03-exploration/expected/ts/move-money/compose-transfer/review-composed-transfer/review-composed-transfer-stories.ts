// review-composed-transfer-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const ReviewComposedTransfer = {
  story:       'Review composed transfer',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Composed Transfer', 'Submit for Approval', 'Validation Status'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer reviews a fully composed transfer ready for submission',
    given: [
      'the Treasurer Alice has a Composed Transfer T-001 in status "Draft" with Validation Status "Valid"',
      'And Transfer T-001 shows Source Account "CHK-001", Destination Account "ACH-999", Amount "$50,000.00"',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice opens the review screen for Transfer T-001'],
        then: [
          'the summary shows Source Account "CHK-001", Destination Account "ACH-999", Amount "$50,000.00"',
          'And the Submit for Approval action is available',
        ],
      },
    ],
  },
} as const satisfies Story
