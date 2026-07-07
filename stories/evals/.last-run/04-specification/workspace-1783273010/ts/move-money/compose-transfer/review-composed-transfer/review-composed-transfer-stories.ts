import type { Story } from '../../../story-types'

export const ReviewComposedTransfer = {
  story:       'Review composed transfer',
  actor:       'Treasurer',
  domainTerms: [],
  evidence:    [],

  treasurerReviewsAFullyComposedTransferReadyForSubmission: {
    name: 'Treasurer reviews a fully composed transfer ready for submission',
    given: [
      'Transfer T-001 is in status Draft',
      'And Transfer T-001 has Source Account CHK-001, Destination Account ACH-999, Amount $50,000.00',
      'And Transfer T-001 has Validation Status Valid',
    ],
    interactions: [
      {
        when: [
          'the Treasurer Alice opens the review screen for Transfer T-001',
        ],
        then: [
          'the summary shows Source Account CHK-001, Destination Account ACH-999, Amount $50,000.00',
          'And the Submit for Approval action is available',
        ],
      },
    ],
  },
} as const satisfies Story
