import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { AttachMemoToTransfer } from './attach-memo-to-transfer-stories'
import * as helpers from '../compose-transfer-helpers'

type Scenarios = | typeof AttachMemoToTransfer.mainFlow | typeof AttachMemoToTransfer.memoTooLong | typeof AttachMemoToTransfer.replaceMemo

export class AttachMemoToTransferServer implements TierImpl<Scenarios> {
  private memo = 'Q3 vendor settlement — invoice #4421'

  given = {
    'a Transfer draft with status "DRAFT"': async () => {
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT' })
    },
    'And a memo text of "Q3 vendor settlement — invoice #4421"': async () => {
      this.memo = 'Q3 vendor settlement — invoice #4421'
    },
    'And a memo text of 501 characters': async () => {
      this.memo = 'x'.repeat(501)
    },
    'And an existing memo of "Original note"': async () => {
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', memo: 'Original note' })
    },
    'And a new memo text of "Revised: Q3 vendor settlement — invoice #4421"': async () => {
      this.memo = 'Revised: Q3 vendor settlement — invoice #4421'
    },
  }

  when = {
    'the Treasurer attaches the memo to the Transfer': async () => {
      helpers.attachMemoToTransfer({ transferId: 'TRF-001', memo: this.memo })
    },
    'the Treasurer attaches the new memo to the Transfer': async () => {
      helpers.attachMemoToTransfer({ transferId: 'TRF-001', memo: this.memo })
    },
  }

  then = {
    'the Transfer memo is set to "Q3 vendor settlement — invoice #4421"': async () => {
      expect(helpers.getLastMemo()?.kind).toBe('saved')
      if (helpers.getLastMemo()?.kind === 'saved') expect(helpers.getLastMemo().transfer.memo).toBe('Q3 vendor settlement — invoice #4421')
    },
    'And the Transfer remains in status "DRAFT"': async () => {
      expect(helpers.getLastMemo()?.kind).toBe('saved')
      if (helpers.getLastMemo()?.kind === 'saved') expect(helpers.getLastMemo().transfer.status).toBe('DRAFT')
    },
    'no memo is saved': async () => { expect(helpers.getLastMemo()?.kind).toBe('rejected') },
    'But a validation error "Memo must not exceed 500 characters" is shown': async () => {
      expect(helpers.getLastMemo()?.kind).toBe('rejected')
      if (helpers.getLastMemo()?.kind === 'rejected') expect(helpers.getLastMemo().error).toBe('Memo must not exceed 500 characters')
    },
    'the Transfer memo is updated to "Revised: Q3 vendor settlement — invoice #4421"': async () => {
      expect(helpers.getLastMemo()?.kind).toBe('saved')
      if (helpers.getLastMemo()?.kind === 'saved') expect(helpers.getLastMemo().transfer.memo).toBe('Revised: Q3 vendor settlement — invoice #4421')
    },
    'And the previous memo "Original note" is no longer stored': async () => {
      expect(helpers.getLastMemo()?.kind).toBe('saved')
      if (helpers.getLastMemo()?.kind === 'saved') expect(helpers.getLastMemo().transfer.memo).not.toBe('Original note')
    },
  }

  async cleanup(): Promise<void> { helpers.resetComposeTransferState() }
}
describe(AttachMemoToTransfer.story, () => {
  describe(AttachMemoToTransfer.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new AttachMemoToTransferServer()
      // Given
      await tier.given['a Transfer draft with status "DRAFT"']()
      await tier.given['And a memo text of "Q3 vendor settlement — invoice #4421"']()
      // When
      await tier.when['the Treasurer attaches the memo to the Transfer']()
      // Then
      await tier.then['the Transfer memo is set to "Q3 vendor settlement — invoice #4421"']()
      await tier.then['And the Transfer remains in status "DRAFT"']()
      await tier.cleanup()
    })
  })
  describe(AttachMemoToTransfer.memoTooLong.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new AttachMemoToTransferServer()
      // Given
      await tier.given['a Transfer draft with status "DRAFT"']()
      await tier.given['And a memo text of 501 characters']()
      // When
      await tier.when['the Treasurer attaches the memo to the Transfer']()
      // Then
      await tier.then['no memo is saved']()
      await tier.then['But a validation error "Memo must not exceed 500 characters" is shown']()
      await tier.cleanup()
    })
  })
  describe(AttachMemoToTransfer.replaceMemo.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new AttachMemoToTransferServer()
      // Given
      await tier.given['a Transfer draft with status "DRAFT"']()
      await tier.given['And an existing memo of "Original note"']()
      await tier.given['And a new memo text of "Revised: Q3 vendor settlement — invoice #4421"']()
      // When
      await tier.when['the Treasurer attaches the new memo to the Transfer']()
      // Then
      await tier.then['the Transfer memo is updated to "Revised: Q3 vendor settlement — invoice #4421"']()
      await tier.then['And the previous memo "Original note" is no longer stored']()
      await tier.cleanup()
    })
  })
})
