// view-pending-transfers-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const ViewPendingTransfers = {
  story:       'View pending transfers',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Pending Transfers', 'Pending'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer views a transfer pending settlement',
    given: [
      'Transfer T-001 is in status "Pending" in the settlement queue',
      'And Transfer T-001 has Amount "$50,000.00" and Destination Account "ACH-999"',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice opens Pending Transfers'],
        then: [
          'Transfer T-001 is listed with status "Pending"',
          'And the list entry shows Amount "$50,000.00" and Destination Account "ACH-999"',
        ],
      },
    ],
  },
} as const satisfies Story
