// submit-transfer-for-approval-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const SubmitTransferForApproval = {
  story:       'Submit transfer for approval',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Composed Transfer', 'Pending Approval', 'Dual-Control Threshold'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer submits a below-threshold transfer for approval',
    given: [
      'the Treasurer Alice is reviewing Transfer T-001 ready for submission',
      'And Transfer T-001 is a Composed Transfer with Amount "$50,000.00", Validation Status "Valid", below the Dual-Control Threshold "$250,000.00"',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice selects Submit for Approval on Transfer T-001'],
        then: [
          'Transfer T-001 status is "Pending Approval"',
          'And Transfer T-001 is visible in the approval queue requiring single approval',
        ],
      },
    ],
  },
} as const satisfies Story
