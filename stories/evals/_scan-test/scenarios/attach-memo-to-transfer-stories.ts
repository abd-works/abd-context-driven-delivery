// attach-memo-to-transfer-stories.ts — typed story data.
// Specification fidelity: all scenario paths. No test implementation.

import type { Story } from '../../../templates/ts/story-types'

export const AttachMemoToTransfer = {
  story:       'Attach memo to transfer',
  actor:       'Treasurer',
  domainTerms: ['Transfer', 'Memo', 'Audit Trail'],
  evidence:    ['Treasury product brief'],

  // ── Scenario 1 — happy path ────────────────────────────────────────────────
  mainFlow: {
    name: 'Treasurer attaches a memo to a draft transfer',
    given: [
      'a Transfer draft with status "DRAFT"',
      'And a memo text of "Q3 vendor settlement — invoice #4421"',
    ],
    interactions: [
      {
        when: ['the Treasurer attaches the memo to the Transfer'],
        then: [
          'the Transfer memo is set to "Q3 vendor settlement — invoice #4421"',
          'And the Transfer remains in status "DRAFT"',
        ],
      },
    ],
  },

  // ── Scenario 2 — memo exceeds maximum length ──────────────────────────────
  memoTooLong: {
    name: 'Treasurer attempts to attach a memo exceeding the character limit',
    given: [
      'a Transfer draft with status "DRAFT"',
      'And a memo text of 501 characters',
    ],
    interactions: [
      {
        when: ['the Treasurer attaches the memo to the Transfer'],
        then: [
          'no memo is saved',
          'But a validation error "Memo must not exceed 500 characters" is shown',
        ],
      },
    ],
  },

  // ── Scenario 3 — replace existing memo ────────────────────────────────────
  replaceMemo: {
    name: 'Treasurer replaces an existing memo on a draft transfer',
    given: [
      'a Transfer draft with status "DRAFT"',
      'And an existing memo of "Original note"',
      'And a new memo text of "Revised: Q3 vendor settlement — invoice #4421"',
    ],
    interactions: [
      {
        when: ['the Treasurer attaches the new memo to the Transfer'],
        then: [
          'the Transfer memo is updated to "Revised: Q3 vendor settlement — invoice #4421"',
          'And the previous memo "Original note" is no longer stored',
        ],
      },
    ],
  },
} as const satisfies Story
