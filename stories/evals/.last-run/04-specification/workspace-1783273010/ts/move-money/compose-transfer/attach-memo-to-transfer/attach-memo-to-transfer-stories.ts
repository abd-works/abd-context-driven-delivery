import type { Story } from '../../../story-types'

export const AttachMemoToTransfer = {
  story:       'Attach memo to transfer',
  actor:       'Treasurer',
  domainTerms: [],
  evidence:    [],

  treasurerAttachesOrReplacesAMemoOnADraftTransfer: {
    name: 'Treasurer attaches or replaces a memo on a draft transfer',
    given: [
      'Transfer T-001 has existing Memo {existing_memo}',
    ],
    interactions: [
      {
        when: [
          'the Treasurer Alice attaches Memo text {memo_text} to Transfer T-001',
        ],
        then: [
          'Transfer T-001 has Memo {expected_memo}',
          'And Transfer T-001 remains in status Draft',
        ],
      },
    ],
  },
  memoExceeds500CharacterLimit: {
    name: 'Memo exceeds 500-character limit',
    given: [
      'Transfer T-001 is in status Draft',
    ],
    interactions: [
      {
        when: [
          'the Treasurer Alice attaches a Memo of 501 characters to Transfer T-001',
        ],
        then: [
          'no Memo is saved on Transfer T-001',
          'And a validation error "Memo must not exceed 500 characters" is shown',
        ],
      },
    ],
  },
} as const satisfies Story
