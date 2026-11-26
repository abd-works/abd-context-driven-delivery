import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { GuidanceSelectionData } from '@cdd/space/session/session'

import { shownAsFailure } from '../error-display/failure-client'
import { callTool } from '../shared/cdd-tool'
import { clearChosenAction } from './action-picker-client'
import { whileBusy } from './busy-client'

// The session's guidance selection as the bar last drew it: the stages, practices, and format groups selected, the
// fidelities they cover, the command each action runs on them, and the version every change raises. The session holds it
// (Session.guidance_selection); the bar follows it with one waiting read, so a press in the Files app draws here in a
// fraction of a second, and draws the answer to a press of its own, ignoring any answer older than the version drawn. Atom guidance, declared in pane/types/index.d.ts.
const guidance = atom({ plugin: 'cdd-board', key: 'guidance' } as const, null as object | null)

// How long the bar waits before reading the selection again after a read failed, and how many failed in a row show: a
// cdd server restarting for a repin drops the read in flight.
const RETRY_MILLISECONDS = 1_000
const FAILED_READS_SHOWN = 10

export async function currentGuidance($: EngineInterface): Promise<GuidanceSelectionData | null> {
  return ((await read($, guidance)) as GuidanceSelectionData | null) ?? null
}

// Follow the session's guidance selection for as long as the chat's mod runs: read it, then wait for each change.
// sessionFileOf names the session the bar shows, which a chat switching sessions changes. Before anyone chose stages,
// the session answers its ticket's stage selected itself.
export async function followGuidance($: EngineInterface, sessionFileOf: () => Promise<string>): Promise<void> {
  let failed = 0
  for (;;) {
    const session = await sessionFileOf()
    if (!session) {
      await pause($)
      continue
    }
    try {
      const drawn = await currentGuidance($)
      const answer = drawn ? await callTool<GuidanceSelectionData>($, 'session.guidance_selection_after', { session, version: drawn.version }) : await callTool<GuidanceSelectionData>($, 'session.guidance_selection', { session })
      await accept($, answer)
      failed = 0
    } catch (failure) {
      failed += 1
      if (failed === FAILED_READS_SHOWN) await shownAsFailure($, 'The chat bar has not read the stages, practices and formats selected for ten tries', 'Following the session, calling session.guidance_selection_after')(failure)
      await pause($)
    }
  }
}

// The part of the selection a press toggles, as Session.toggle_guidance names it.
export type SelectionPart = 'stage' | 'practice' | 'format'

// Atom pressedGuidance, declared in pane/types/index.d.ts and kept in this file: the press running now, as part:name.
const pressedGuidance = atom({ plugin: 'cdd-board', key: 'pressedGuidance' } as const, '')

// The press running now, as part:name, such as format:markdown; empty while none runs.
export async function currentPressedGuidance($: EngineInterface): Promise<string> {
  return read($, pressedGuidance)
}

// A press on a stage button, a practice's dot, or a format chip: one toggle, whose answer the bar draws. The session works
// out the selection the press leaves, which can take a while with many files to filter, so the bar shows the busy wheel
// and what it filters by until the answer lands, and a second press while one runs starts nothing.
export async function toggleGuidance($: EngineInterface, session: string, part: SelectionPart, name: string): Promise<void> {
  if (!session || (await read($, pressedGuidance))) return
  await update($, pressedGuidance, () => `${part}:${name}`)
  await clearChosenAction($)
  try {
    await whileBusy($, `filtering by ${name}`, async () => accept($, await callTool<GuidanceSelectionData>($, 'session.toggle_guidance', { session, part, name })))
  } catch (failure) {
    await shownAsFailure($, `The ${name} ${part} was not changed`, `Pressing ${name} on the chat bar, calling session.toggle_guidance`)(failure)
  } finally {
    await update($, pressedGuidance, () => '')
  }
}

// A reload cuts off the press that would clear it, so a fresh start clears it.
export async function clearPressedGuidance($: EngineInterface): Promise<void> {
  await update($, pressedGuidance, () => '')
}

// An answer older than the version drawn is one a press has already moved past.
async function accept($: EngineInterface, answer: GuidanceSelectionData): Promise<void> {
  const drawn = await currentGuidance($)
  if (drawn && answer.version < drawn.version) return
  await update($, guidance, () => answer)
}

function pause($: EngineInterface): Promise<void> {
  return new Promise(resolve => $.clock.after(RETRY_MILLISECONDS, () => resolve()))
}
