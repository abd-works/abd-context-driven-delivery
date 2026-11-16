import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { GuidanceSelectionData } from '@cdd/space/session/session'

import { shownAsFailure } from '../error-display/failure-client'
import { callTool } from '../shared/cdd-tool'
import { clearChosenAction } from './action-picker-client'

// The session's guidance selection as the bar last drew it: the stages, practices, and format groups selected, the
// fidelities they cover, and the version every change raises. The session holds it (Session.guidance_selection); the bar
// follows it with one waiting read, so a press in the Files app draws here in a fraction of a second, and draws a press
// of its own at once, ignoring any answer older than the version drawn. Atom guidance, declared in pane/types/index.d.ts.
const guidance = atom({ plugin: 'cdd-board', key: 'guidance' } as const, null as object | null)

// How long the bar waits before reading the selection again after a read failed, and how many failed in a row show: a
// cdd server restarting for a repin drops the read in flight.
const RETRY_MILLISECONDS = 1_000
const FAILED_READS_SHOWN = 10

export async function currentGuidance($: EngineInterface): Promise<GuidanceSelectionData | null> {
  return ((await read($, guidance)) as GuidanceSelectionData | null) ?? null
}

// Follow the session's guidance selection for as long as the chat's mod runs: read it, then wait for each change.
// sessionFileOf names the session the bar shows, which a chat switching sessions changes.
export async function followGuidance($: EngineInterface, sessionFileOf: () => Promise<string>, stageOf: () => Promise<string>): Promise<void> {
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
      if (!answer.is_stage_chosen) await startStage($, session, await stageOf())
      failed = 0
    } catch (failure) {
      failed += 1
      if (failed === FAILED_READS_SHOWN) await shownAsFailure($, 'The chat bar has not read the stages, practices and formats selected for ten tries', 'Following the session, calling session.guidance_selection_after')(failure)
      await pause($)
    }
  }
}

// Before any stage was selected for the session, the bar selects the stage its ticket is in, so turning every stage
// off later shows none.
async function startStage($: EngineInterface, session: string, stage: string): Promise<void> {
  if (!stage) return
  await accept($, await callTool<GuidanceSelectionData>($, 'session.update_guidance_selection', { session, stages: [stage.toLowerCase()] }))
}

// A press on a stage button selects the stage beside those selected, or no longer.
export async function toggleStage($: EngineInterface, session: string, name: string): Promise<void> {
  await toggle($, session, 'stages', name, selection => selection.stages.map(stage => ({ name: stage.name, isSelected: stage.is_selected })))
}

// A press on a practice's dot turns the practice on or off for the session: all its fidelities of the stages selected.
export async function togglePractice($: EngineInterface, session: string, key: string): Promise<void> {
  await toggle($, session, 'practices', key, selection => selection.practices.map(practice => ({ name: practice.key, isSelected: practice.is_selected })))
}

// A press on a format chip selects the format group for every selected fidelity offering it, or no longer.
export async function toggleFormat($: EngineInterface, session: string, label: string): Promise<void> {
  await toggle($, session, 'formats', label, selection => selection.formats.map(format => ({ name: format.label, isSelected: format.is_selected })))
}

type Part = 'stages' | 'practices' | 'formats'
type Named = { name: string; isSelected: boolean }

// The press draws at once, flipped; then one update, whose answer replaces it.
async function toggle($: EngineInterface, session: string, part: Part, name: string, namedIn: (selection: GuidanceSelectionData) => Named[]): Promise<void> {
  const selection = await currentGuidance($)
  if (!selection || !session) return
  const named = namedIn(selection)
  const selected = named.filter(each => each.isSelected !== (each.name === name)).map(each => each.name)
  await update($, guidance, () => flipped(selection, part, name))
  await clearChosenAction($)
  try {
    await accept($, await callTool<GuidanceSelectionData>($, 'session.update_guidance_selection', { session, [part]: selected }))
  } catch (failure) {
    await shownAsFailure($, `The ${name} ${part.slice(0, -1)} was not ${selected.includes(name) ? 'selected' : 'cleared'}`, `Pressing ${name} on the chat bar, calling session.update_guidance_selection`)(failure)
  }
}

function flipped(selection: GuidanceSelectionData, part: Part, name: string): GuidanceSelectionData {
  if (part === 'stages') return { ...selection, is_stage_chosen: true, stages: selection.stages.map(stage => (stage.name === name ? { ...stage, is_selected: !stage.is_selected } : stage)) }
  if (part === 'practices') return { ...selection, practices: selection.practices.map(practice => (practice.key === name ? { ...practice, is_selected: !practice.is_selected } : practice)) }
  return { ...selection, formats: selection.formats.map(format => (format.label === name ? { ...format, is_selected: !format.is_selected } : format)) }
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
