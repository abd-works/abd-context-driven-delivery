import type { Story } from '../../../story-types'

export const DraftTransferDetails = {
  story:       'Draft transfer details',
  actor:       'Treasurer',
  domainTerms: [],
  evidence:    [],

  treasurerDraftsAValidSameDayTransfer: {
    name: 'Treasurer drafts a valid same-day transfer',
    given: [
      'Source Account CHK-001 is available to debit',
      'And Destination Account ACH-999 is registered in the system',
      'And an Amount of $50,000.00',
    ],
    interactions: [
      {
        when: [
          'the Treasurer Alice submits the transfer details form',
        ],
        then: [
          'a Transfer T-001 is created with status Draft',
          'And Transfer T-001 references Destination Account ACH-999 with Amount $50,000.00',
          'And Transfer T-001 is attributed to Source Account CHK-001',
        ],
      },
    ],
  },
} as const satisfies Story
