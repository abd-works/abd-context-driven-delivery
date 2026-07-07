import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { runScenario } from '../../../story-runner'
import { ReviewComposedTransfer } from './review-composed-transfer-stories'
import * as H from '../compose-transfer-helpers'

type S = | typeof ReviewComposedTransfer.mainFlow | typeof ReviewComposedTransfer.destinationNotValidated | typeof ReviewComposedTransfer.destinationInvalid

export class ReviewComposedTransferServer implements TierImpl<S> {
  given = {
    'a Transfer draft with status "DRAFT"': async () => {
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT' })
    },
    'And source account "CHK-001", destination account "ACH-999", amount "$50,000.00", date today': async () => {
      H.ensureTransfer('TRF-001', {
        id: 'TRF-001', status: 'DRAFT', sourceAccount: 'CHK-001', destinationAccount: 'ACH-999', amount: '$50,000.00',
      })
    },
    'And destination account validation status "VALID"': async () => {
      H.ensureTransfer('TRF-001', {
        id: 'TRF-001', status: 'DRAFT', sourceAccount: 'CHK-001', destinationAccount: 'ACH-999', amount: '$50,000.00', destinationValidation: 'VALID',
      })
    },
    'And destination account validation status "PENDING"': async () => {
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationValidation: 'PENDING' })
    },
    'And destination account validation status "INVALID"': async () => {
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationValidation: 'INVALID' })
    },
  }

  when = {
    'the Treasurer opens the transfer review screen': async () => {
      H.reviewComposedTransfer({ transferId: 'TRF-001' })
      H.renderTransferReviewDom('TRF-001')
    },
  }

  then = {
    'the Transfer summary displays source "CHK-001", destination "ACH-999", amount "$50,000.00"': async () => {
      expect(H.getLastReview()?.summary).toEqual({ source: 'CHK-001', destination: 'ACH-999', amount: '$50,000.00' })
    },
    'And a Submit for approval action is available': async () => {
      expect(H.getLastReview()?.submitEnabled).toBe(true)
    },
    'the Submit for approval action is disabled': async () => {
      expect(H.getLastReview()?.submitEnabled).toBe(false)
    },
    'And a warning "Validate destination account before submitting" is shown': async () => {
      expect(H.getLastReview()?.message).toBe('Validate destination account before submitting')
    },
    'And an error "Destination account is invalid — correct before submitting" is shown': async () => {
      expect(H.getLastReview()?.message).toBe('Destination account is invalid — correct before submitting')
    },
  }

  async cleanup(): Promise<void> { H.resetComposeTransferState() }
}

})

describe(ReviewComposedTransfer.story, () => {
  describe(ReviewComposedTransfer.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ReviewComposedTransferServer()
      for (const step of ReviewComposedTransfer.mainFlow.given)            await tier.given[step]()
      for (const { when, then } of ReviewComposedTransfer.mainFlow.interactions) {
        for (const step of when)  await tier.when[step]()
        for (const step of then)  await tier.then[step]()
      }
      await tier.cleanup()
    })
  })
  describe(ReviewComposedTransfer.destinationNotValidated.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ReviewComposedTransferServer()
      for (const step of ReviewComposedTransfer.destinationNotValidated.given)            await tier.given[step]()
      for (const { when, then } of ReviewComposedTransfer.destinationNotValidated.interactions) {
        for (const step of when)  await tier.when[step]()
        for (const step of then)  await tier.then[step]()
      }
      await tier.cleanup()
    })
  })
  describe(ReviewComposedTransfer.destinationInvalid.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ReviewComposedTransferServer()
      for (const step of ReviewComposedTransfer.destinationInvalid.given)            await tier.given[step]()
      for (const { when, then } of ReviewComposedTransfer.destinationInvalid.interactions) {
        for (const step of when)  await tier.when[step]()
        for (const step of then)  await tier.then[step]()
      }
      await tier.cleanup()
    })
  })})
