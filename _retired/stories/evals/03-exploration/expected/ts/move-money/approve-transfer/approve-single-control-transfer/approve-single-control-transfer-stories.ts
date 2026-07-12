// approve-single-control-transfer-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const ApproveSingleControlTransfer = {
  story:       'Approve single-control transfer',
  actor:       'Approver',
  domainTerms: ['Approver', 'Transfer', 'Pending Approval', 'Approved', 'Dual-Control Threshold'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Approver approves a below-threshold transfer',
    given: [
      'the Approver Bob is reviewing the approval queue',
      'And Transfer T-001 is in status "Pending Approval" with Amount "$50,000.00" below the Dual-Control Threshold "$250,000.00"',
    ],
    interactions: [
      {
        when: ['the Approver Bob approves Transfer T-001'],
        then: [
          'Transfer T-001 status is "Approved"',
          'And Transfer T-001 shows approval recorded by Approver Bob',
        ],
      },
    ],
  },
} as const satisfies Story
