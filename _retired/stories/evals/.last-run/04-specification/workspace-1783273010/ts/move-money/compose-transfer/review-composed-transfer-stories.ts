// review-composed-transfer-stories.ts — specification fidelity with scenario outlines.

import type { Story } from '../../../story-types'

export const REVIEW_COMPOSED_TRANSFER_EXAMPLES = [
  {
    scenario: 'Scenario 1',
    validation_status: 'Valid',
    source_account: 'CHK-001',
    destination_account: 'ACH-999',
    amount: '$50,000.00',
    submit_for_approval_available: true,
    warning_or_error_message: '',
  },
  {
    scenario: 'Scenario 2',
    validation_status: 'Pending',
    source_account: 'CHK-001',
    destination_account: 'ACH-999',
    amount: '$50,000.00',
    submit_for_approval_available: false,
    warning_or_error_message: 'Validate destination account before submitting',
  },
  {
    scenario: 'Scenario 3',
    validation_status: 'Invalid',
    source_account: 'CHK-001',
    destination_account: 'ACH-999',
    amount: '$50,000.00',
    submit_for_approval_available: false,
    warning_or_error_message: 'Destination account is invalid — correct before submitting',
  },
] as const

export const ReviewComposedTransfer = {
  story: 'Review composed transfer',
  actor: 'Treasurer',
  domainTerms: [
    'Transfer',
    'Composed Transfer',
    'Validation Status',
    'Submit for Approval',
  ],
  evidence: ['Treasury product brief §"Transfer review and submit"'],

  composedTransferReviewBeforeSubmission: {
    name: 'Treasurer reviews a composed transfer before submission',
    given: ['Transfer T-001 has Validation Status {validation_status}'],
    interactions: [
      {
        when: ['the Treasurer Alice opens the review screen for Transfer T-001'],
        then: [
          'the summary shows Source Account {source_account}, Destination Account {destination_account}, Amount {amount}',
          'And the Submit for Approval action is available when {submit_for_approval_available} is true',
          'But the Submit for Approval action is disabled when {submit_for_approval_available} is false',
          'And a message {warning_or_error_message} is shown when {submit_for_approval_available} is false',
        ],
      },
    ],
  },
} as const satisfies Story
