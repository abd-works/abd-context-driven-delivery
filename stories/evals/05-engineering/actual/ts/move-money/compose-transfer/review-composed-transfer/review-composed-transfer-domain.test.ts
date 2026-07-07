import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { ReviewComposedTransfer } from './review-composed-transfer-stories'
import * as helpers from '../compose-transfer-helpers'

type Scenarios = | typeof ReviewComposedTransfer.mainFlow | typeof ReviewComposedTransfer.destinationNotValidated | typeof ReviewComposedTransfer.destinationInvalid

export class ReviewComposedTransferDomain implements TierImpl<Scenarios> {
  given = {
    'a Transfer draft with status "DRAFT"': async () => {
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT' })
    },
    'And source account "CHK-001", destination account "ACH-999", amount "$50,000.00", date today': async () => {
      helpers.ensureTransfer('TRF-001', {
        id: 'TRF-001', status: 'DRAFT', sourceAccount: 'CHK-001', destinationAccount: 'ACH-999', amount: '$50,000.00',
      })
    },
    'And destination account validation status "VALID"': async () => {
      helpers.ensureTransfer('TRF-001', {
        id: 'TRF-001', status: 'DRAFT', sourceAccount: 'CHK-001', destinationAccount: 'ACH-999', amount: '$50,000.00', destinationValidation: 'VALID',
      })
    },
    'And destination account validation status "PENDING"': async () => {
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationValidation: 'PENDING' })
    },
    'And destination account validation status "INVALID"': async () => {
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationValidation: 'INVALID' })
    },
  }

  when = {
    'the Treasurer opens the transfer review screen': async () => {
      helpers.reviewComposedTransfer({ transferId: 'TRF-001' })
      helpers.renderTransferReviewDom('TRF-001')
    },
  }

  then = {
    'the Transfer summary displays source "CHK-001", destination "ACH-999", amount "$50,000.00"': async () => {
      expect(helpers.getLastReview()?.summary).toEqual({ source: 'CHK-001', destination: 'ACH-999', amount: '$50,000.00' })
    },
    'And a Submit for approval action is available': async () => {
      expect(helpers.getLastReview()?.submitEnabled).toBe(true)
    },
    'the Submit for approval action is disabled': async () => {
      expect(helpers.getLastReview()?.submitEnabled).toBe(false)
    },
    'And a warning "Validate destination account before submitting" is shown': async () => {
      expect(helpers.getLastReview()?.message).toBe('Validate destination account before submitting')
    },
    'And an error "Destination account is invalid — correct before submitting" is shown': async () => {
      expect(helpers.getLastReview()?.message).toBe('Destination account is invalid — correct before submitting')
    },
  }

  async cleanup(): Promise<void> { helpers.resetComposeTransferState() }
}
describe(ReviewComposedTransfer.story, () => {
  describe(ReviewComposedTransfer.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ReviewComposedTransferDomain()
      // Given
      await tier.given['a Transfer draft with status "DRAFT"']()
      await tier.given['And source account "CHK-001", destination account "ACH-999", amount "$50,000.00", date today']()
      await tier.given['And destination account validation status "VALID"']()
      // When
      await tier.when['the Treasurer opens the transfer review screen']()
      // Then
      await tier.then['the Transfer summary displays source "CHK-001", destination "ACH-999", amount "$50,000.00"']()
      await tier.then['And a Submit for approval action is available']()
      await tier.cleanup()
    })
  })
  describe(ReviewComposedTransfer.destinationNotValidated.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ReviewComposedTransferDomain()
      // Given
      await tier.given['a Transfer draft with status "DRAFT"']()
      await tier.given['And destination account validation status "PENDING"']()
      // When
      await tier.when['the Treasurer opens the transfer review screen']()
      // Then
      await tier.then['the Submit for approval action is disabled']()
      await tier.then['And a warning "Validate destination account before submitting" is shown']()
      await tier.cleanup()
    })
  })
  describe(ReviewComposedTransfer.destinationInvalid.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ReviewComposedTransferDomain()
      // Given
      await tier.given['a Transfer draft with status "DRAFT"']()
      await tier.given['And destination account validation status "INVALID"']()
      // When
      await tier.when['the Treasurer opens the transfer review screen']()
      // Then
      await tier.then['the Submit for approval action is disabled']()
      await tier.then['And an error "Destination account is invalid — correct before submitting" is shown']()
      await tier.cleanup()
    })
  })
})
