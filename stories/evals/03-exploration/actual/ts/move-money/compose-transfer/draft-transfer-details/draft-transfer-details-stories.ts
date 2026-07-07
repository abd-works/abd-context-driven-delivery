// draft-transfer-details-stories.ts — exploration fidelity: mainFlow only. No test implementation.

import type { Story } from '../../../story-types'

export const DraftTransferDetails = {
  story:       'Draft transfer details',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Source Account', 'Destination Account', 'Amount', 'Draft'],
  evidence:    ['Treasury product brief'],

  mainFlow: {
    name: 'Happy path — Treasurer drafts a valid same-day transfer',
    given: [
      'the Treasurer Alice is composing a new Transfer',
      'And Source Account "CHK-001" is available to debit and Destination Account "ACH-999" is registered in the system',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice submits Amount "$50,000.00" on the transfer details form'],
        then: [
          'a Transfer T-001 is created in status "Draft" referencing Source Account "CHK-001", Destination Account "ACH-999", and Amount "$50,000.00"',
        ],
      },
    ],
  },
} as const satisfies Story
