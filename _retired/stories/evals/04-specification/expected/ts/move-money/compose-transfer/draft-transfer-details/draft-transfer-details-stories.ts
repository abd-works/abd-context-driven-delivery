// draft-transfer-details-stories.ts — specification fidelity with scenario outlines.

import type { Story } from '../../../story-types'

export const DRAFT_TRANSFER_VALID_EXAMPLES = [
  {
    scenario: 'Scenario 1',
    source_account: 'CHK-001',
    destination_account: 'ACH-999',
    amount: '$50,000.00',
    transfer_id: 'T-001',
    transfer_status: 'Draft',
  },
] as const

export const DRAFT_TRANSFER_REJECTION_EXAMPLES = [
  {
    scenario: 'Scenario 2',
    source_account: 'CHK-001',
    available_balance: '$500,000.00',
    daily_transfer_limit: '$100,000.00',
    destination_account: 'ACH-999',
    destination_status: 'registered',
    amount: '$150,000.00',
    error_message: 'Amount exceeds daily transfer limit of $100,000.00',
  },
  {
    scenario: 'Scenario 3',
    source_account: 'CHK-001',
    available_balance: '$500,000.00',
    daily_transfer_limit: '$5,000,000.00',
    destination_account: '',
    destination_status: 'not provided',
    amount: '$50,000.00',
    error_message: 'Destination account is required',
  },
  {
    scenario: 'Scenario 4',
    source_account: 'CHK-001',
    available_balance: '$500,000.00',
    daily_transfer_limit: '$5,000,000.00',
    destination_account: 'ACH-999',
    destination_status: 'registered',
    amount: '$0.00',
    error_message: 'Amount must be greater than zero',
  },
  {
    scenario: 'Scenario 5',
    source_account: 'CHK-001',
    available_balance: '$20,000.00',
    daily_transfer_limit: '$5,000,000.00',
    destination_account: 'ACH-999',
    destination_status: 'registered',
    amount: '$50,000.00',
    error_message: 'Insufficient funds in source account CHK-001',
  },
] as const

export const DraftTransferDetails = {
  story: 'Draft transfer details',
  actor: 'Treasurer',
  domainTerms: [
    'Transfer',
    'Source Account',
    'Destination Account',
    'Amount',
    'Draft',
    'Daily Transfer Limit',
  ],
  evidence: ['Treasury product brief §"Same-day transfer flow"'],

  validSameDayTransferDrafted: {
    name: 'Treasurer drafts a valid same-day transfer',
    given: [
      'Source Account {source_account} is available to debit',
      'And Destination Account {destination_account} is registered in the system',
      'And an Amount of {amount}',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice submits the transfer details form'],
        then: [
          'a Transfer {transfer_id} is created with status {transfer_status}',
          'And Transfer {transfer_id} references Destination Account {destination_account} with Amount {amount}',
          'And Transfer {transfer_id} is attributed to Source Account {source_account}',
        ],
      },
    ],
  },

  transferDetailsRejectedWithValidationError: {
    name: 'Transfer details submission rejected with validation error',
    given: [
      'Source Account {source_account} has Available Balance {available_balance}',
      'And Source Account {source_account} has Daily Transfer Limit {daily_transfer_limit}',
      'And Destination Account {destination_account} is {destination_status} in the system',
      'And an Amount of {amount}',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice submits the transfer details form'],
        then: [
          'no Transfer is created',
          'But a validation error {error_message} is shown',
        ],
      },
    ],
  },
} as const satisfies Story
