// attach-memo-to-transfer-stories.ts — specification fidelity with scenario outlines.

import type { Story } from '../../../story-types'

export const ATTACH_MEMO_TO_TRANSFER_EXAMPLES = [
  {
    scenario: 'Scenario 1',
    existing_memo: '',
    memo_text: 'Q3 vendor settlement — invoice #4421',
    memo_saved: true,
    transfer_memo: 'Q3 vendor settlement — invoice #4421',
    error_message: '',
  },
  {
    scenario: 'Scenario 2',
    existing_memo: 'Original note',
    memo_text: 'Revised: Q3 vendor settlement — invoice #4421',
    memo_saved: true,
    transfer_memo: 'Revised: Q3 vendor settlement — invoice #4421',
    error_message: '',
  },
  {
    scenario: 'Scenario 3',
    existing_memo: '',
    memo_text: '501 characters',
    memo_saved: false,
    transfer_memo: '',
    error_message: 'Memo must not exceed 500 characters',
  },
] as const

export const AttachMemoToTransfer = {
  story: 'Attach memo to transfer',
  actor: 'Treasurer',
  domainTerms: ['Transfer', 'Memo', 'Audit Trail'],
  evidence: ['Treasury product brief §"Transfer memo and audit trail"'],

  memoAttachedOrUpdatedOnDraftTransfer: {
    name: 'Treasurer attaches or updates a memo on a draft transfer',
    given: [
      'Transfer T-001 has Memo {existing_memo}',
      'And a Memo text of {memo_text}',
    ],
    interactions: [
      {
        when: ['the Treasurer Alice attaches the Memo to Transfer T-001'],
        then: [
          'Transfer T-001 has Memo {transfer_memo} when {memo_saved} is true',
          'And Transfer T-001 remains in status Draft when {memo_saved} is true',
          'But no Memo is saved when {memo_saved} is false',
          'And a validation error {error_message} is shown when {memo_saved} is false',
        ],
      },
    ],
  },
} as const satisfies Story
