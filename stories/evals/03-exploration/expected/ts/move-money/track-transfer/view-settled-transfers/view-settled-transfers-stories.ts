// view-settled-transfers-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const ViewSettledTransfers = {
  story:       'View settled transfers',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Settled Transfers', 'Settled', 'Same-Day Settlement'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer views a same-day settled transfer',
    given: [
      'Transfer T-001 has completed Same-Day Settlement',
      'And Transfer T-001 status is "Settled"',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice opens Settled Transfers'],
        then: [
          'Transfer T-001 is listed with status "Settled"',
          'And the list entry shows settlement date as today and Amount "$50,000.00"',
        ],
      },
    ],
  },
} as const satisfies Story
