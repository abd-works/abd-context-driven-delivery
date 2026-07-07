// compose-transfer-helpers.ts — shared fixtures for compose-transfer story tests.
import { expect } from 'vitest'

export type TransferDraft = {
  id: string
  status: 'DRAFT'
  sourceAccount?: string
  destinationAccount?: string
  amount?: string
  memo?: string
  destinationValidation?: 'VALID' | 'INVALID' | 'PENDING'
}

export type DraftOutcome =
  | { kind: 'created'; transfer: TransferDraft }
  | { kind: 'rejected'; error: string }

export type MemoOutcome =
  | { kind: 'saved'; transfer: TransferDraft }
  | { kind: 'rejected'; error: string }

export type ValidationOutcome = {
  validationStatus: 'VALID' | 'INVALID'
  transfer: TransferDraft
  error?: string
}

export type ReviewOutcome = {
  summary?: { source: string; destination: string; amount: string }
  submitEnabled: boolean
  message?: string
}

const registry = {
  accounts: new Map<string, { registered: boolean; active: boolean; balance: number; dailyLimit?: number }>(),
  transfers: new Map<string, TransferDraft>(),
  lastDraft: null as DraftOutcome | null,
  lastMemo: null as MemoOutcome | null,
  lastValidation: null as ValidationOutcome | null,
  lastReview: null as ReviewOutcome | null,
  lastHttp: null as { status: number; body: unknown } | null,
  lastDom: null as Record<string, string | boolean> | null,
}

export function resetComposeTransferState(): void {
  registry.accounts.clear()
  registry.transfers.clear()
  registry.lastDraft = null
  registry.lastMemo = null
  registry.lastValidation = null
  registry.lastReview = null
  registry.lastHttp = null
  registry.lastDom = null
}

export function seedSourceAccount(id: string, opts: { balance?: number; dailyLimit?: number } = {}): void {
  registry.accounts.set(id, {
    registered: true,
    active: true,
    balance: opts.balance ?? 1_000_000,
    dailyLimit: opts.dailyLimit,
  })
}

export function seedDestinationAccount(id: string, opts: { registered?: boolean; active?: boolean } = {}): void {
  registry.accounts.set(id, {
    registered: opts.registered ?? true,
    active: opts.active ?? true,
    balance: 0,
  })
}

export function draftTransferDetails(input: {
  sourceAccount: string
  destinationAccount?: string
  amount: string
}): DraftOutcome {
  const source = registry.accounts.get(input.sourceAccount)
  if (!source) {
    const outcome = { kind: 'rejected' as const, error: `Unknown source account ${input.sourceAccount}` }
    registry.lastDraft = outcome
    return outcome
  }
  if (!input.destinationAccount) {
    const outcome = { kind: 'rejected' as const, error: 'Destination account is required' }
    registry.lastDraft = outcome
    registry.lastDom = { submitEnabled: false, message: outcome.error, source: '', destination: '', amount: '' }
    return outcome
  }
  const amount = Number(input.amount.replace(/[^0-9.]/g, ''))
  if (amount <= 0) {
    const outcome = { kind: 'rejected' as const, error: 'Amount must be greater than zero' }
    registry.lastDraft = outcome
    registry.lastDom = { submitEnabled: false, message: outcome.error, source: '', destination: '', amount: '' }
    return outcome
  }
  if (source.dailyLimit !== undefined && amount > source.dailyLimit) {
    const outcome = {
      kind: 'rejected' as const,
      error: `Amount exceeds daily transfer limit of $${source.dailyLimit.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
    }
    registry.lastDraft = outcome
    registry.lastDom = { submitEnabled: false, message: outcome.error, source: '', destination: '', amount: '' }
    return outcome
  }
  if (amount > source.balance) {
    const outcome = { kind: 'rejected' as const, error: `Insufficient funds in source account ${input.sourceAccount}` }
    registry.lastDraft = outcome
    registry.lastDom = { submitEnabled: false, message: outcome.error, source: '', destination: '', amount: '' }
    return outcome
  }
  const transfer: TransferDraft = {
    id: 'TRF-001',
    status: 'DRAFT',
    sourceAccount: input.sourceAccount,
    destinationAccount: input.destinationAccount,
    amount: input.amount,
  }
  registry.transfers.set(transfer.id, transfer)
  const outcome = { kind: 'created' as const, transfer }
  registry.lastDraft = outcome
  registry.lastDom = {
    submitEnabled: true,
    message: 'created',
    source: transfer.sourceAccount ?? '',
    destination: transfer.destinationAccount ?? '',
    amount: transfer.amount ?? '',
  }
  return outcome
}

export function attachMemoToTransfer(input: { transferId: string; memo: string }): MemoOutcome {
  const transfer = registry.transfers.get(input.transferId)
  if (!transfer) throw new Error('missing transfer')
  if (input.memo.length > 500) {
    const outcome = { kind: 'rejected' as const, error: 'Memo must not exceed 500 characters' }
    registry.lastMemo = outcome
    return outcome
  }
  transfer.memo = input.memo
  const outcome = { kind: 'saved' as const, transfer: { ...transfer } }
  registry.lastMemo = outcome
  return outcome
}

export function validateDestinationAccount(input: { transferId: string; destinationAccount: string }): ValidationOutcome {
  const transfer = registry.transfers.get(input.transferId)
  if (!transfer) throw new Error('missing transfer')
  const account = registry.accounts.get(input.destinationAccount)
  let validationStatus: 'VALID' | 'INVALID' = 'VALID'
  let error: string | undefined
  if (!account?.registered) {
    validationStatus = 'INVALID'
    error = `Destination account ${input.destinationAccount} is not registered`
  } else if (!account.active) {
    validationStatus = 'INVALID'
    error = `Destination account ${input.destinationAccount} is inactive`
  }
  transfer.destinationValidation = validationStatus
  const outcome = { validationStatus, transfer: { ...transfer }, error }
  registry.lastValidation = outcome
  return outcome
}

export function reviewComposedTransfer(input: { transferId: string }): ReviewOutcome {
  const transfer = registry.transfers.get(input.transferId)
  if (!transfer) throw new Error('missing transfer')
  const validation = transfer.destinationValidation ?? 'PENDING'
  if (validation === 'VALID') {
    const outcome = {
      summary: {
        source: transfer.sourceAccount ?? '',
        destination: transfer.destinationAccount ?? '',
        amount: transfer.amount ?? '',
      },
      submitEnabled: true,
    }
    registry.lastReview = outcome
    return outcome
  }
  if (validation === 'PENDING') {
    const outcome = {
      submitEnabled: false,
      message: 'Validate destination account before submitting',
    }
    registry.lastReview = outcome
    return outcome
  }
  const outcome = {
    submitEnabled: false,
    message: 'Destination account is invalid — correct before submitting',
  }
  registry.lastReview = outcome
  return outcome
}

export function postTransferDetailsHttp(payload: Record<string, unknown>): void {
  const outcome = draftTransferDetails({
    sourceAccount: String(payload.sourceAccount ?? ''),
    destinationAccount: payload.destinationAccount ? String(payload.destinationAccount) : undefined,
    amount: String(payload.amount ?? ''),
  })
  registry.lastHttp = {
    status: outcome.kind === 'created' ? 201 : 400,
    body: outcome.kind === 'created' ? outcome.transfer : { error: outcome.error },
  }
}

export function renderTransferReviewDom(transferId: string): void {
  const review = reviewComposedTransfer({ transferId })
  registry.lastDom = {
    submitEnabled: review.submitEnabled,
    message: review.message ?? '',
    source: review.summary?.source ?? '',
    destination: review.summary?.destination ?? '',
    amount: review.summary?.amount ?? '',
  }
}

export function assertDraftCreated(status: string): void {
  expect(registry.lastDraft?.kind).toBe('created')
  if (registry.lastDraft?.kind === 'created') expect(registry.lastDraft.transfer.status).toBe(status)
}

export function assertDraftRejected(error: string): void {
  expect(registry.lastDraft?.kind).toBe('rejected')
  if (registry.lastDraft?.kind === 'rejected') expect(registry.lastDraft.error).toBe(error)
}

export function getLastDraft() { return registry.lastDraft }
export function getLastMemo() { return registry.lastMemo }
export function getLastValidation() { return registry.lastValidation }
export function getLastReview() { return registry.lastReview }
export function getLastHttp() { return registry.lastHttp }
export function getLastDom() { return registry.lastDom }
export function ensureTransfer(id: string, draft: TransferDraft): void { registry.transfers.set(id, draft) }
