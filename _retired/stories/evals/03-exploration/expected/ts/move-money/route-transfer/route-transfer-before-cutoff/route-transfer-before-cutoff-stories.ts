// route-transfer-before-cutoff-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const RouteTransferBeforeCutoff = {
  story:       'Route transfer before cutoff',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Approved', 'Same-Day Cutoff', 'Same-Day Settlement'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer routes an approved transfer before the same-day cutoff',
    given: [
      'Transfer T-001 is in status "Approved"',
      'And the current time is before the Same-Day Cutoff "15:00 ET"',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice routes Transfer T-001 into the settlement window'],
        then: [
          'Transfer T-001 is marked for Same-Day Settlement',
          'And Transfer T-001 status is "Pending" in the settlement queue',
        ],
      },
    ],
  },
} as const satisfies Story
