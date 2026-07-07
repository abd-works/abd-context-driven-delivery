// draft-transfer-details-stories.ts — typed story data for Draft transfer details.
// Specification fidelity: all scenario paths expanded. No test implementation.

import type { Story } from '../../../templates/ts/story-types'

export const DraftTransferDetails = {
  story:       'Draft transfer details',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Source Account', 'Destination Account', 'Amount', 'Transfer Reference', 'Draft'],
  evidence:    ['Treasury product brief'],

  // ── Scenario 1 — happy path ────────────────────────────────────────────────
  mainFlow: {
    name: 'Treasurer drafts a valid same-day transfer',
    given: [
      'a Treasurer with source account "CHK-001" available to debit',
      'And a destination account "ACH-999" registered in the system',
      'And an amount of "$50,000.00"',
      'And a transfer date of today',
    ],
    interactions: [
      {
        when: ['the Treasurer submits the transfer details form'],
        then: [
          'a Transfer is created with status "DRAFT"',
          'And the Transfer references destination "ACH-999" with amount "$50,000.00"',
          'And the Transfer is attributed to source account "CHK-001"',
        ],
      },
    ],
  },

  // ── Scenario 2 — amount exceeds daily limit ───────────────────────────────
  amountExceedsDailyLimit: {
    name: 'Treasurer attempts to draft a transfer exceeding the daily limit',
    given: [
      'a Treasurer with source account "CHK-001" with a daily transfer limit of "$100,000.00"',
      'And a destination account "ACH-999" registered in the system',
      'And an amount of "$150,000.00"',
    ],
    interactions: [
      {
        when: ['the Treasurer submits the transfer details form'],
        then: [
          'no Transfer is created',
          'But an error "Amount exceeds daily transfer limit of $100,000.00" is shown',
        ],
      },
    ],
  },

  // ── Scenario 3 — missing required field ───────────────────────────────────
  missingDestinationAccount: {
    name: 'Treasurer submits transfer details without a destination account',
    given: [
      'a Treasurer with source account "CHK-001" available to debit',
      'And no destination account provided',
      'And an amount of "$50,000.00"',
    ],
    interactions: [
      {
        when: ['the Treasurer submits the transfer details form'],
        then: [
          'no Transfer is created',
          'But a validation error "Destination account is required" is shown',
        ],
      },
    ],
  },

  // ── Scenario 4 — zero or negative amount ──────────────────────────────────
  invalidAmount: {
    name: 'Treasurer submits a transfer with a zero amount',
    given: [
      'a Treasurer with source account "CHK-001" available to debit',
      'And a destination account "ACH-999" registered in the system',
      'And an amount of "$0.00"',
    ],
    interactions: [
      {
        when: ['the Treasurer submits the transfer details form'],
        then: [
          'no Transfer is created',
          'But a validation error "Amount must be greater than zero" is shown',
        ],
      },
    ],
  },

  // ── Scenario 5 — insufficient funds ───────────────────────────────────────
  insufficientFunds: {
    name: 'Treasurer drafts a transfer with insufficient source account balance',
    given: [
      'a Treasurer with source account "CHK-001" with available balance of "$20,000.00"',
      'And a destination account "ACH-999" registered in the system',
      'And an amount of "$50,000.00"',
    ],
    interactions: [
      {
        when: ['the Treasurer submits the transfer details form'],
        then: [
          'no Transfer is created',
          'But an error "Insufficient funds in source account CHK-001" is shown',
        ],
      },
    ],
  },
} as const satisfies Story
