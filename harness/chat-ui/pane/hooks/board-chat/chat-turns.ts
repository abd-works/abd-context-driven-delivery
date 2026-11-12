import type { EngineInterface } from 'claude-code'

import { post } from './board'

// The chat's own turns, which tell the board when a message it sent is done.

let isBusy = false
// Messages the chat showed and is still working on, each with the turns started before it arrived; a message is done
// when a turn that started after it ends, not the turn the chat was already in.
const unfinished = new Map<string, number>()
// Counts the chat's own turns, so a command that returned without starting one is known to be done.
let turnsStarted = 0
// Ticks of the one-second check-in clock since the chat last worked: a turn of its own, or a command from the board.
let idleTicks = 0
// While the chat works, and for this many ticks after, it checks in every tick, so a Run pressed on the board arrives
// within a second; after that it checks in every IDLE_CHECK_IN_TICKS, since every open chat checking in every second
// keeps the one cdd server every chat shares busy for nothing.
const ACTIVE_TICKS = 60
const IDLE_CHECK_IN_TICKS = 5

export function isCheckInDue(): boolean {
  if (isBusy) {
    idleTicks = 0
    return true
  }
  idleTicks += 1
  return idleTicks <= ACTIVE_TICKS || idleTicks % IDLE_CHECK_IN_TICKS === 0
}

// The board gave the chat something to do, so it checks in every second again for a while.
export function chatWorked(): void {
  idleTicks = 0
}

export function isChatBusy(): boolean {
  return isBusy
}

export function turnsSoFar(): number {
  return turnsStarted
}

// The message waits for a turn that starts after now to end.
export function awaitTurn(message: string): void {
  unfinished.set(message, turnsStarted)
}

export function forgetTurn(message: string): void {
  unfinished.delete(message)
}

export async function finish($: EngineInterface, chat: string, message: string): Promise<void> {
  if (!unfinished.delete(message)) return
  await post($, { chat, operation: 'finish', body: { message } })
}

export function turnStarted(): void {
  isBusy = true
  idleTicks = 0
  turnsStarted += 1
}

// A board message is done once a turn that started after it ends.
export async function turnCompleted($: EngineInterface): Promise<void> {
  isBusy = false
  const chat = await $.session.id()
  for (const [message, turnsBefore] of [...unfinished]) if (turnsStarted > turnsBefore) await finish($, chat, message)
}
