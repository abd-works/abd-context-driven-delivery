// review-composed-transfer-stories.ts — typed story data.
// Specification fidelity: all scenario paths. No test implementation.

import type { Story } from '../../../templates/ts/story-types'

export const ReviewComposedTransfer = {
  story:       'Review composed transfer',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Composed Transfer', 'Review', 'Approval'],
  evidence:    ['Treasury product brief'],

  // ── Scenario 1 — happy path ────────────────────────────────────────────────
  mainFlow: {
    name: 'Treasurer reviews a fully composed transfer',
    given: [
      'a Transfer draft with status "DRAFT"',
      'And source account "CHK-001", destination account "ACH-999", amount "$50,000.00", date today',
      'And destination account validation status "VALID"',
    ],
    interactions: [
      {
        when: ['the Treasurer opens the transfer review screen'],
        then: [
          'the Transfer summary displays source "CHK-001", destination "ACH-999", amount "$50,000.00"',
          'And a Submit for approval action is available',
        ],
      },
    ],
  },

  // ── Scenario 2 — destination not validated ────────────────────────────────
  destinationNotValidated: {
    name: 'Treasurer attempts to review a transfer with unvalidated destination',
    given: [
      'a Transfer draft with status "DRAFT"',
      'And destination account validation status "PENDING"',
    ],
    interactions: [
      {
        when: ['the Treasurer opens the transfer review screen'],
        then: [
          'the Submit for approval action is disabled',
          'And a warning "Validate destination account before submitting" is shown',
        ],
      },
    ],
  },

  // ── Scenario 3 — destination invalid ──────────────────────────────────────
  destinationInvalid: {
    name: 'Treasurer reviews a transfer with an invalid destination account',
    given: [
      'a Transfer draft with status "DRAFT"',
      'And destination account validation status "INVALID"',
    ],
    interactions: [
      {
        when: ['the Treasurer opens the transfer review screen'],
        then: [
          'the Submit for approval action is disabled',
          'And an error "Destination account is invalid — correct before submitting" is shown',
        ],
      },
    ],
  },
} as const satisfies Story
