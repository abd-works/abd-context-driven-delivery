import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { DraftTransferDetails } from './draft-transfer-details-stories'
import {
  getLastHttp,
  postTransferDetailsHttp,
  resetComposeTransferState,
  seedDestinationAccount,
  seedSourceAccount,
} from '../compose-transfer-helpers'

type Scenarios =
  | typeof DraftTransferDetails.mainFlow
  | typeof DraftTransferDetails.amountExceedsDailyLimit
  | typeof DraftTransferDetails.missingDestinationAccount
  | typeof DraftTransferDetails.invalidAmount
  | typeof DraftTransferDetails.insufficientFunds

export class DraftTransferDetailsServer implements TierImpl<Scenarios> {
  private destinationAccount: string | undefined = 'ACH-999'
  private amount = '$50,000.00'

  given = {
    'a Treasurer with source account "CHK-001" available to debit': async () => {
      seedSourceAccount('CHK-001')
    },
    'And a destination account "ACH-999" registered in the system': async () => {
      seedDestinationAccount('ACH-999')
    },
    'And an amount of "$50,000.00"': async () => { this.amount = '$50,000.00' },
    'And a transfer date of today': async () => { void new Date() },
    'a Treasurer with source account "CHK-001" with a daily transfer limit of "$100,000.00"': async () => {
      seedSourceAccount('CHK-001', { dailyLimit: 100_000 })
    },
    'And an amount of "$150,000.00"': async () => { this.amount = '$150,000.00' },
    'And no destination account provided': async () => { this.destinationAccount = undefined },
    'And an amount of "$0.00"': async () => { this.amount = '$0.00' },
    'a Treasurer with source account "CHK-001" with available balance of "$20,000.00"': async () => {
      seedSourceAccount('CHK-001', { balance: 20_000 })
    },
  }

  when = {
    'the Treasurer submits the transfer details form': async () => {
      postTransferDetailsHttp({
        sourceAccount: 'CHK-001',
        destinationAccount: this.destinationAccount,
        amount: this.amount,
      })
    },
  }

  then = {
    'a Transfer is created with status "DRAFT"': async () => {
      expect(getLastHttp()?.status).toBe(201)
      expect((getLastHttp()?.body as { status: string }).status).toBe('DRAFT')
    },
    'And the Transfer references destination "ACH-999" with amount "$50,000.00"': async () => {
      const body = getLastHttp()?.body as { destinationAccount: string; amount: string }
      expect(body.destinationAccount).toBe('ACH-999')
      expect(body.amount).toBe('$50,000.00')
    },
    'And the Transfer is attributed to source account "CHK-001"': async () => {
      expect((getLastHttp()?.body as { sourceAccount: string }).sourceAccount).toBe('CHK-001')
    },
    'no Transfer is created': async () => {
      expect(getLastHttp()?.status).toBe(400)
    },
    'But an error "Amount exceeds daily transfer limit of $100,000.00" is shown': async () => {
      expect((getLastHttp()?.body as { error: string }).error).toBe('Amount exceeds daily transfer limit of $100,000.00')
    },
    'But a validation error "Destination account is required" is shown': async () => {
      expect((getLastHttp()?.body as { error: string }).error).toBe('Destination account is required')
    },
    'But a validation error "Amount must be greater than zero" is shown': async () => {
      expect((getLastHttp()?.body as { error: string }).error).toBe('Amount must be greater than zero')
    },
    'But an error "Insufficient funds in source account CHK-001" is shown': async () => {
      expect((getLastHttp()?.body as { error: string }).error).toBe('Insufficient funds in source account CHK-001')
    },
  }

  async cleanup(): Promise<void> { resetComposeTransferState() }
}
describe(DraftTransferDetails.story, () => {
  describe(DraftTransferDetails.mainFlow.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new DraftTransferDetailsServer()
      // Given
      await tier.given['a Treasurer with source account "CHK-001" available to debit']()
      await tier.given['And a destination account "ACH-999" registered in the system']()
      await tier.given['And an amount of "$50,000.00"']()
      await tier.given['And a transfer date of today']()
      // When
      await tier.when['the Treasurer submits the transfer details form']()
      // Then
      await tier.then['a Transfer is created with status "DRAFT"']()
      await tier.then['And the Transfer references destination "ACH-999" with amount "$50,000.00"']()
      await tier.then['And the Transfer is attributed to source account "CHK-001"']()
      await tier.cleanup()
    })
  })
  describe(DraftTransferDetails.amountExceedsDailyLimit.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new DraftTransferDetailsServer()
      // Given
      await tier.given['a Treasurer with source account "CHK-001" with a daily transfer limit of "$100,000.00"']()
      await tier.given['And a destination account "ACH-999" registered in the system']()
      await tier.given['And an amount of "$150,000.00"']()
      // When
      await tier.when['the Treasurer submits the transfer details form']()
      // Then
      await tier.then['no Transfer is created']()
      await tier.then['But an error "Amount exceeds daily transfer limit of $100,000.00" is shown']()
      await tier.cleanup()
    })
  })
  describe(DraftTransferDetails.missingDestinationAccount.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new DraftTransferDetailsServer()
      // Given
      await tier.given['a Treasurer with source account "CHK-001" available to debit']()
      await tier.given['And no destination account provided']()
      await tier.given['And an amount of "$50,000.00"']()
      // When
      await tier.when['the Treasurer submits the transfer details form']()
      // Then
      await tier.then['no Transfer is created']()
      await tier.then['But a validation error "Destination account is required" is shown']()
      await tier.cleanup()
    })
  })
  describe(DraftTransferDetails.invalidAmount.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new DraftTransferDetailsServer()
      // Given
      await tier.given['a Treasurer with source account "CHK-001" available to debit']()
      await tier.given['And a destination account "ACH-999" registered in the system']()
      await tier.given['And an amount of "$0.00"']()
      // When
      await tier.when['the Treasurer submits the transfer details form']()
      // Then
      await tier.then['no Transfer is created']()
      await tier.then['But a validation error "Amount must be greater than zero" is shown']()
      await tier.cleanup()
    })
  })
  describe(DraftTransferDetails.insufficientFunds.name, () => {
    it('runs Given / When / Then in order', async () => {
      const tier = new DraftTransferDetailsServer()
      // Given
      await tier.given['a Treasurer with source account "CHK-001" with available balance of "$20,000.00"']()
      await tier.given['And a destination account "ACH-999" registered in the system']()
      await tier.given['And an amount of "$50,000.00"']()
      // When
      await tier.when['the Treasurer submits the transfer details form']()
      // Then
      await tier.then['no Transfer is created']()
      await tier.then['But an error "Insufficient funds in source account CHK-001" is shown']()
      await tier.cleanup()
    })
  })
})
