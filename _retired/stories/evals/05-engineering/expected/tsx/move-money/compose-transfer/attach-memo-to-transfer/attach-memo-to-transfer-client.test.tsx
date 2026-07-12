import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { runScenario } from '../../../story-runner'
import { AttachMemoToTransfer } from './attach-memo-to-transfer-stories'
import * as H from '../compose-transfer-helpers'

type S = | typeof AttachMemoToTransfer.mainFlow | typeof AttachMemoToTransfer.memoTooLong | typeof AttachMemoToTransfer.replaceMemo

export class AttachMemoToTransferClient implements TierImpl<S> {
  private memo = 'Q3 vendor settlement — invoice #4421'

  given = {
    'a Transfer draft with status "DRAFT"': async () => {
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT' })
    },
    'And a memo text of "Q3 vendor settlement — invoice #4421"': async () => {
      this.memo = 'Q3 vendor settlement — invoice #4421'
    },
    'And a memo text of 501 characters': async () => {
      this.memo = 'x'.repeat(501)
    },
    'And an existing memo of "Original note"': async () => {
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', memo: 'Original note' })
    },
    'And a new memo text of "Revised: Q3 vendor settlement — invoice #4421"': async () => {
      this.memo = 'Revised: Q3 vendor settlement — invoice #4421'
    },
  }

  when = {
    'the Treasurer attaches the memo to the Transfer': async () => {
      H.attachMemoToTransfer({ transferId: 'TRF-001', memo: this.memo })
    },
    'the Treasurer attaches the new memo to the Transfer': async () => {
      H.attachMemoToTransfer({ transferId: 'TRF-001', memo: this.memo })
    },
  }

  then = {
    'the Transfer memo is set to "Q3 vendor settlement — invoice #4421"': async () => {
      expect(H.getLastMemo()?.kind).toBe('saved')
      if (H.getLastMemo()?.kind === 'saved') expect(H.getLastMemo().transfer.memo).toBe('Q3 vendor settlement — invoice #4421')
    },
    'And the Transfer remains in status "DRAFT"': async () => {
      expect(H.getLastMemo()?.kind).toBe('saved')
      if (H.getLastMemo()?.kind === 'saved') expect(H.getLastMemo().transfer.status).toBe('DRAFT')
    },
    'no memo is saved': async () => { expect(H.getLastMemo()?.kind).toBe('rejected') },
    'But a validation error "Memo must not exceed 500 characters" is shown': async () => {
      expect(H.getLastMemo()?.kind).toBe('rejected')
      if (H.getLastMemo()?.kind === 'rejected') expect(H.getLastMemo().error).toBe('Memo must not exceed 500 characters')
    },
    'the Transfer memo is updated to "Revised: Q3 vendor settlement — invoice #4421"': async () => {
      expect(H.getLastMemo()?.kind).toBe('saved')
      if (H.getLastMemo()?.kind === 'saved') expect(H.getLastMemo().transfer.memo).toBe('Revised: Q3 vendor settlement — invoice #4421')
    },
    'And the previous memo "Original note" is no longer stored': async () => {
      expect(H.getLastMemo()?.kind).toBe('saved')
      if (H.getLastMemo()?.kind === 'saved') expect(H.getLastMemo().transfer.memo).not.toBe('Original note')
    },
  }

  async cleanup(): Promise<void> { H.resetComposeTransferState() }
}
describe('Attach memo to transfer', () => {
  it('executes story scenarios via runScenario wiring', () => { expect(true).toBe(true) })
})

runScenario(AttachMemoToTransfer.story, AttachMemoToTransfer.mainFlow, () => new AttachMemoToTransferClient())
runScenario(AttachMemoToTransfer.story, AttachMemoToTransfer.memoTooLong, () => new AttachMemoToTransferClient())
runScenario(AttachMemoToTransfer.story, AttachMemoToTransfer.replaceMemo, () => new AttachMemoToTransferClient())
