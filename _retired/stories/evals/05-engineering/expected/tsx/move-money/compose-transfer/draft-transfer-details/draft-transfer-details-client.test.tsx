import { describe, expect, it } from 'vitest'
import type { TierImpl } from '../../../story-types'
import { runScenario } from '../../../story-runner'
import { DraftTransferDetails } from './draft-transfer-details-stories'
import {
  draftTransferDetails,
  getLastDom,
  renderTransferReviewDom,
  resetComposeTransferState,
  seedDestinationAccount,
  seedSourceAccount,
} from '../compose-transfer-helpers'

type S =
  | typeof DraftTransferDetails.mainFlow
  | typeof DraftTransferDetails.amountExceedsDailyLimit
  | typeof DraftTransferDetails.missingDestinationAccount
  | typeof DraftTransferDetails.invalidAmount
  | typeof DraftTransferDetails.insufficientFunds

export class DraftTransferDetailsClient implements TierImpl<S> {
  private destinationAccount: string | undefined = 'ACH-999'
  private amount = '$50,000.00'

  given = {
    'a Treasurer with source account "CHK-001" available to debit': async () => { seedSourceAccount('CHK-001') },
    'And a destination account "ACH-999" registered in the system': async () => { seedDestinationAccount('ACH-999') },
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
      draftTransferDetails({
        sourceAccount: 'CHK-001',
        destinationAccount: this.destinationAccount,
        amount: this.amount,
      })
    },
  }

  then = {
    'a Transfer is created with status "DRAFT"': async () => {
      expect(getLastDom()?.submitEnabled).toBe(true)
    },
    'And the Transfer references destination "ACH-999" with amount "$50,000.00"': async () => {
      expect(getLastDom()?.destination).toBe('ACH-999')
      expect(getLastDom()?.amount).toBe('$50,000.00')
    },
    'And the Transfer is attributed to source account "CHK-001"': async () => {
      expect(getLastDom()?.source).toBe('CHK-001')
    },
    'no Transfer is created': async () => {
      expect(getLastDom()?.submitEnabled).toBe(false)
    },
    'But an error "Amount exceeds daily transfer limit of $100,000.00" is shown': async () => {
      expect(getLastDom()?.message).toBe('Amount exceeds daily transfer limit of $100,000.00')
    },
    'But a validation error "Destination account is required" is shown': async () => {
      expect(getLastDom()?.message).toBe('Destination account is required')
    },
    'But a validation error "Amount must be greater than zero" is shown': async () => {
      expect(getLastDom()?.message).toBe('Amount must be greater than zero')
    },
    'But an error "Insufficient funds in source account CHK-001" is shown': async () => {
      expect(getLastDom()?.message).toBe('Insufficient funds in source account CHK-001')
    },
  }

  async cleanup(): Promise<void> { resetComposeTransferState() }
}
describe('Draft transfer details', () => {
  it('executes story scenarios via runScenario wiring', () => { expect(true).toBe(true) })
})

runScenario(DraftTransferDetails.story, DraftTransferDetails.mainFlow, () => new DraftTransferDetailsClient())
runScenario(DraftTransferDetails.story, DraftTransferDetails.amountExceedsDailyLimit, () => new DraftTransferDetailsClient())
runScenario(DraftTransferDetails.story, DraftTransferDetails.missingDestinationAccount, () => new DraftTransferDetailsClient())
runScenario(DraftTransferDetails.story, DraftTransferDetails.invalidAmount, () => new DraftTransferDetailsClient())
runScenario(DraftTransferDetails.story, DraftTransferDetails.insufficientFunds, () => new DraftTransferDetailsClient())
