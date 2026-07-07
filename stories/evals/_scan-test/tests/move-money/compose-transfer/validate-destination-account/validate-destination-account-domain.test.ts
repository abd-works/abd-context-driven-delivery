import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { runScenario } from '../../../story-runner'
import { ValidateDestinationAccount } from './validate-destination-account-stories'
import * as H from '../compose-transfer-helpers'

type S = | typeof ValidateDestinationAccount.mainFlow | typeof ValidateDestinationAccount.accountNotRegistered | typeof ValidateDestinationAccount.accountInactive

export class ValidateDestinationAccountDomain implements TierImpl<S> {
  private destination = 'ACH-999'

  given = {
    'a Transfer draft with destination account "ACH-999"': async () => {
      this.destination = 'ACH-999'
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationAccount: 'ACH-999' })
    },
    'And destination account "ACH-999" is registered and active in the system': async () => {
      H.seedDestinationAccount('ACH-999')
    },
    'a Transfer draft with destination account "ACH-000"': async () => {
      this.destination = 'ACH-000'
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationAccount: 'ACH-000' })
    },
    'And destination account "ACH-000" is not registered in the system': async () => {
      H.seedDestinationAccount('ACH-000', { registered: false })
    },
    'a Transfer draft with destination account "ACH-888"': async () => {
      this.destination = 'ACH-888'
      H.ensureTransfer('TRF-001', { id: 'TRF-001', status: 'DRAFT', destinationAccount: 'ACH-888' })
    },
    'And destination account "ACH-888" is registered but inactive': async () => {
      H.seedDestinationAccount('ACH-888', { active: false })
    },
  }

  when = {
    'the Treasurer triggers destination account validation': async () => {
      H.validateDestinationAccount({ transferId: 'TRF-001', destinationAccount: this.destination })
    },
  }

  then = {
    'the destination account is confirmed as "VALID"': async () => {
      expect(H.getLastValidation()?.validationStatus).toBe('VALID')
    },
    'And the Transfer draft remains in status "DRAFT"': async () => {
      expect(H.getLastValidation()?.transfer.status).toBe('DRAFT')
    },
    'the destination account is flagged as "INVALID"': async () => {
      expect(H.getLastValidation()?.validationStatus).toBe('INVALID')
    },
    'But the Transfer draft remains in status "DRAFT"': async () => {
      expect(H.getLastValidation()?.transfer.status).toBe('DRAFT')
    },
    'And an error "Destination account ACH-000 is not registered" is shown': async () => {
      expect(H.getLastValidation()?.error).toBe('Destination account ACH-000 is not registered')
    },
    'And an error "Destination account ACH-888 is inactive" is shown': async () => {
      expect(H.getLastValidation()?.error).toBe('Destination account ACH-888 is inactive')
    },
  }

  async cleanup(): Promise<void> { H.resetComposeTransferState() }
}

})

describe(ValidateDestinationAccount.story, () => {
  describe(ValidateDestinationAccount.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ValidateDestinationAccountDomain()
      for (const step of ValidateDestinationAccount.mainFlow.given)            await tier.given[step]()
      for (const { when, then } of ValidateDestinationAccount.mainFlow.interactions) {
        for (const step of when)  await tier.when[step]()
        for (const step of then)  await tier.then[step]()
      }
      await tier.cleanup()
    })
  })
  describe(ValidateDestinationAccount.accountNotRegistered.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ValidateDestinationAccountDomain()
      for (const step of ValidateDestinationAccount.accountNotRegistered.given)            await tier.given[step]()
      for (const { when, then } of ValidateDestinationAccount.accountNotRegistered.interactions) {
        for (const step of when)  await tier.when[step]()
        for (const step of then)  await tier.then[step]()
      }
      await tier.cleanup()
    })
  })
  describe(ValidateDestinationAccount.accountInactive.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new ValidateDestinationAccountDomain()
      for (const step of ValidateDestinationAccount.accountInactive.given)            await tier.given[step]()
      for (const { when, then } of ValidateDestinationAccount.accountInactive.interactions) {
        for (const step of when)  await tier.when[step]()
        for (const step of then)  await tier.then[step]()
      }
      await tier.cleanup()
    })
  })})
