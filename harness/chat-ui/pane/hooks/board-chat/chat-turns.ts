import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ChatTurnsJson } from '../../types'
import { post } from './board'

// The chat's own turns, which tell the board when a message it sent is done. They are kept in the chat's state, not in
// the module, so a reload of the mod finds the messages it is still working on.

// Atom chatTurns, declared in pane/types/index.d.ts and kept in this file. unfinished holds the messages the chat showed
// and is still working on, each with the turns started before it arrived; a message is done when a turn that started
// after it ends, not the turn the chat was already in. turnsStarted counts the chat's own turns, so a command that
// returned without starting one is known to be done. idleCheckIns counts the one-second check-in clock's ticks since the
// chat last worked: a turn of its own, or a command from the board.
const chatTurns = atom({ plugin: 'cdd-board', key: 'chatTurns' } as const, { isBusy: false, turnsStarted: 0, idleCheckIns: 0, unfinished: {} } as ChatTurnsJson)

// Atom waitingSubmits, declared in pane/types/index.d.ts and kept in this file: the texts of the board messages submitted
// to the chat that have not run yet. The engine runs a plugin's prompt only once the chat is idle, and runs every one
// waiting then as one message, so a second press on the board while the first waits would reach the chat twice.
const waitingSubmits = atom({ plugin: 'cdd-board', key: 'waitingSubmits' } as const, [] as string[])

// Whether a message with this text waits for the chat already.
export async function isSubmitWaiting($: EngineInterface, text: string): Promise<boolean> {
  return (await read($, waitingSubmits)).includes(text)
}

export async function submitWaits($: EngineInterface, text: string): Promise<void> {
  await update($, waitingSubmits, texts => (texts.includes(text) ? texts : [...texts, text]))
}

export async function submitRan($: EngineInterface, text: string): Promise<void> {
  await update($, waitingSubmits, texts => texts.filter(waiting => waiting !== text))
}

// While the chat works, and for this many ticks after, it checks in every tick, so a Run pressed on the board arrives
// within a second; after that it checks in every IDLE_CHECK_IN_TICKS, since every open chat checking in every second
// keeps the one cdd server every chat shares busy for nothing.
const ACTIVE_TICKS = 60
const IDLE_CHECK_IN_TICKS = 5

// A chat starting, or a mod reloaded, is in no turn yet: one reloaded mid-turn would otherwise come back still busy.
export async function chatStarted($: EngineInterface): Promise<void> {
  await update($, chatTurns, turns => ({ ...turns, isBusy: false, idleCheckIns: 0 }))
  await update($, waitingSubmits, () => [])
}

// Whether this tick of the check-in clock checks in: every tick while the chat works and for a while after, then every
// few ticks.
export async function isCheckInDue($: EngineInterface): Promise<boolean> {
  await update($, chatTurns, held => (held.isBusy ? { ...held, idleCheckIns: 0 } : { ...held, idleCheckIns: held.idleCheckIns + 1 }))
  const turns = await read($, chatTurns)
  return turns.isBusy || turns.idleCheckIns <= ACTIVE_TICKS || turns.idleCheckIns % IDLE_CHECK_IN_TICKS === 0
}

// The board gave the chat something to do, so it checks in every second again for a while.
export async function chatWorked($: EngineInterface): Promise<void> {
  await update($, chatTurns, turns => ({ ...turns, idleCheckIns: 0 }))
}

export async function isChatBusy($: EngineInterface): Promise<boolean> {
  return (await read($, chatTurns)).isBusy
}

export async function turnsSoFar($: EngineInterface): Promise<number> {
  return (await read($, chatTurns)).turnsStarted
}

// The message waits for a turn that starts after now to end.
export async function awaitTurn($: EngineInterface, message: string): Promise<void> {
  await update($, chatTurns, turns => ({ ...turns, unfinished: { ...turns.unfinished, [message]: turns.turnsStarted } }))
}

export async function forgetTurn($: EngineInterface, message: string): Promise<void> {
  await update($, chatTurns, turns => ({ ...turns, unfinished: withoutMessage(turns.unfinished, message) }))
}

// Tells the board the message is done, once: a message the chat is no longer working on was told already.
export async function finish($: EngineInterface, chat: string, message: string): Promise<void> {
  if (!(message in (await read($, chatTurns)).unfinished)) return
  await forgetTurn($, message)
  await post($, { chat, operation: 'finish', body: { message } })
}

// A turn that starts takes every message waiting for the chat, so none waits any longer.
export async function turnStarted($: EngineInterface): Promise<void> {
  await update($, chatTurns, turns => ({ ...turns, isBusy: true, idleCheckIns: 0, turnsStarted: turns.turnsStarted + 1 }))
  await update($, waitingSubmits, () => [])
}

// A board message is done once a turn that started after it ends.
export async function turnCompleted($: EngineInterface): Promise<void> {
  await update($, chatTurns, held => ({ ...held, isBusy: false }))
  const turns = await read($, chatTurns)
  const chat = await $.session.id()
  for (const [message, turnsBefore] of Object.entries(turns.unfinished)) if (turns.turnsStarted > turnsBefore) await finish($, chat, message)
}

function withoutMessage(unfinished: Record<string, number>, message: string): Record<string, number> {
  const { [message]: _done, ...rest } = unfinished
  return rest
}
