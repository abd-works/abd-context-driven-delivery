import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { ValidateDestinationAccount } from './validate-destination-account-stories'
import * as helpers from '../compose-transfer-helpers'

type Scenarios = | typeof ValidateDestinationAccount.mainFlow | typeof ValidateDestinationAccount.accountNotRegistered | typeof ValidateDestinationAccount.accountInactive

export class ValidateDestinationAccountE2e implements TierImpl<Scenarios> {
  private destination = 'ACH-999'

  given = {
    'a Transfer draft with destination account "ACH-999"': async () => {
      this.destination = 'ACH-999'
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationAccount: 'ACH-999' })
    },
    'And destination account "ACH-999" is registered and active in the system': async () => {
      helpers.seedDestinationAccount('ACH-999')
    },
    'a Transfer draft with destination account "ACH-000"': async () => {
      this.destination = 'ACH-000'
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationAccount: 'ACH-000' })
    },
    'And destination account "ACH-000" is not registered in the system': async () => {
      helpers.seedDestinationAccount('ACH-000', { registered: false })
    },
    'a Transfer draft with destination account "ACH-888"': async () => {
      this.destination = 'ACH-888'
      helpers.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationAccount: 'ACH-888' })
    },
    'And destination account "ACH-888" is registered but inactive': async () => {
      helpers.seedDestinationAccount('ACH-888', { active: false })
    },
  }

  when = {
    'the Treasurer triggers destination account validation': async () => {
      helpers.validateDestinationAccount({ transferId: 'TRF-001', destinationAccount: this.destination })
    },
  }

  then = {
    'the destination account is confirmed as "VALID"': async () => {
      expect(helpers.getLastValidation()?.validationStatus).toBe('VALID')
    },
    'And the Transfer draft remains in status "DRAFT"': async () => {
      expect(helpers.getLastValidation()?.transfer.status).toBe('DRAFT')
    },
    'the destination account is flagged as "INVALID"': async () => {
      expect(helpers.getLastValidation()?.validationStatus).toBe('INVALID')
    },
    'But the Transfer draft remains in status "DRAFT"': async () => {
      expect(helpers.getLastValidation()?.transfer.status).toBe('DRAFT')
    },
    'And an error "Destination account ACH-000 is not registered" is shown': async () => {
      expect(helpers.getLastValidation()?.error).toBe('Destination account ACH-000 is not registered')
    },
    'And an error "Destination account ACH-888 is inactive" is shown': async () => {
      expect(helpers.getLastValidation()?.error).toBe('Destination account ACH-888 is inactive')
    },
  }

  async cleanup(): Promise<void> { helpers.resetComposeTransferState() }
}
describe(ValidateDestinationAccount.story, () => {
  describe(ValidateDestinationAccount.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ValidateDestinationAccountE2e()
      // Given
      await tier.given['a Transfer draft with destination account "ACH-999"']()
      await tier.given['And destination account "ACH-999" is registered and active in the system']()
      // When
      await tier.when['the Treasurer triggers destination account validation']()
      // Then
      await tier.then['the destination account is confirmed as "VALID"']()
      await tier.then['And the Transfer draft remains in status "DRAFT"']()
      await tier.cleanup()
    })
  })
  describe(ValidateDestinationAccount.accountNotRegistered.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ValidateDestinationAccountE2e()
      // Given
      await tier.given['a Transfer draft with destination account "ACH-000"']()
      await tier.given['And destination account "ACH-000" is not registered in the system']()
      // When
      await tier.when['the Treasurer triggers destination account validation']()
      // Then
      await tier.then['the destination account is flagged as "INVALID"']()
      await tier.then['But the Transfer draft remains in status "DRAFT"']()
      await tier.then['And an error "Destination account ACH-000 is not registered" is shown']()
      await tier.cleanup()
    })
  })
  describe(ValidateDestinationAccount.accountInactive.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ValidateDestinationAccountE2e()
      // Given
      await tier.given['a Transfer draft with destination account "ACH-888"']()
      await tier.given['And destination account "ACH-888" is registered but inactive']()
      // When
      await tier.when['the Treasurer triggers destination account validation']()
      // Then
      await tier.then['the destination account is flagged as "INVALID"']()
      await tier.then['But the Transfer draft remains in status "DRAFT"']()
      await tier.then['And an error "Destination account ACH-888 is inactive" is shown']()
      await tier.cleanup()
    })
  })
})
