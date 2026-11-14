import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FailureData } from '@cdd/tools/error_display/failure'

import type { FailureJson } from '../../types'

// Every failure in the mod is shown the same way, above the chat bar's line: what failed with the reason it gave, the
// context it failed in, Fix, which sends both to this chat to find the cause and fix it, and ✕ to dismiss it. It stays
// until the person fixes or dismisses it, since a toast passes before anyone reads it. The shape is tools/error_display's
// Failure; the mod builds it itself, since a failure must show while the cdd server is what is broken.
const shownFailure = atom({ plugin: 'cdd-board', key: 'failure' } as const, null as FailureJson)

export class FailureClient {
  constructor(private readonly json: FailureData) {}

  get failure(): string {
    return this.json.failure
  }

  get context(): string {
    return this.json.context
  }

  // What Fix sends to the chat: the failure and its context, and the ask to find the cause and fix it.
  get fixPrompt(): string {
    return `The CDD chat bar above the prompt shows this failure; find its cause and fix it.\n\nFailure: ${this.failure}\nContext: ${this.context}`
  }
}

// The words a failure carries: the server's own text for a failed cdd tool, a thrown error's message otherwise.
export function reasonOf(failure: unknown): string {
  return failure instanceof Error ? failure.message : String(failure)
}

export async function currentFailure($: EngineInterface): Promise<FailureClient | null> {
  const json = await read($, shownFailure)
  return json ? new FailureClient(json as FailureData) : null
}

// Shows a failure above the line: what failed, with the reason the thrown failure gave when there is one, and the
// context it failed in, such as the button pressed and the tool it called.
export async function showFailure($: EngineInterface, failure: string, context: string, thrown?: unknown): Promise<void> {
  const said = thrown === undefined ? failure : `${failure}: ${reasonOf(thrown)}`
  await update($, shownFailure, () => ({ failure: said, context }))
}

// A catch handler that shows what it caught: `.catch(shownAsFailure($, 'The board did not load', 'Reading the board'))`.
export function shownAsFailure($: EngineInterface, failure: string, context: string): (thrown: unknown) => Promise<void> {
  return thrown => showFailure($, failure, context, thrown)
}

export async function dismissFailure($: EngineInterface): Promise<void> {
  await update($, shownFailure, () => null)
}

// Fix sends the failure and its context to this chat's agent and clears it from the line.
export async function fixFailure($: EngineInterface, failure: FailureClient): Promise<void> {
  await $.prompt.submit({ text: failure.fixPrompt, asUser: true })
  await dismissFailure($)
}
