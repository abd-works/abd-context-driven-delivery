import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { CddVersionData } from '@cdd/harness/release/cdd-version'

import type { CddVersionJson } from '../../types'
import { BRAND } from '../shared/brand'
import { promptCommand, showFailure } from '../error-display/failure-client'
import { callTool, CddToolFailed } from '../shared/cdd-tool'

const CHECK_TOOL = 'cdd-version.check'
// Reads the version on disk against the latest release tag as last fetched, without fetching: cheap enough for every turn.
const READ_TOOL = 'cdd-version.read'
const INSTALL_LATEST_COMMAND = '/harness:installation:install-latest'
// The cdd server is still connecting as a chat opens, so the first check waits as the server health's first look does.
const FIRST_CHECK_WAIT_MS = 5000
// Twelve tries five seconds apart: a minute for cdd to connect after the chat opens or the plugins reload.
const CHECK_TRIES = 12
// The colour of each standing CddVersion answers: green current, yellow a patch or minor update behind, red a major one.
const STANDING_COLOURS: Record<string, string> = {
  current: BRAND.success,
  'behind patch': BRAND.warning,
  'behind minor': BRAND.warning,
  'behind major': BRAND.error,
  unknown: BRAND.muted,
}

const cddVersion = atom({ plugin: 'cdd-board', key: 'cddVersion' } as const, { data: null, problem: null, isAsking: false, update: 'idle', error: null } as CddVersionJson)

export class CddVersionClient {
  constructor(private readonly json: CddVersionJson) {}

  private get data(): CddVersionData | null {
    return this.json.data as CddVersionData | null
  }

  // The badge's words, such as v0.1; a dash until cdd-version.check has answered.
  get label(): string {
    return this.data?.version ?? 'v–'
  }

  get colour(): string {
    return STANDING_COLOURS[this.data?.standing ?? 'unknown'] ?? BRAND.muted
  }

  get summary(): string {
    return this.data?.summary ?? (this.json.problem ? `The CDD version is not read yet: ${this.json.problem}` : 'Reading the CDD version.')
  }

  // The badge's hover: updating while an update runs, up to date once one leaves this chat on the latest, why it failed
  // if it did, and otherwise the version's summary, which says when the chat is still behind.
  get tip(): string {
    if (this.json.update === 'running') return 'updating…'
    if (this.json.update === 'installed' && this.data?.standing === 'current') return 'up to date'
    if (this.json.update === 'failed') return `update failed: ${this.json.error ?? 'no reason given'}`
    return this.summary
  }

  get latest(): string {
    return this.data?.latest ?? ''
  }

  get isAsking(): boolean {
    return this.json.isAsking
  }
}

export async function currentCddVersion($: EngineInterface): Promise<CddVersionClient> {
  return new CddVersionClient(await read($, cddVersion))
}

// The first check, a moment after the chat opens, then again every few seconds while cdd is still connecting, up to a
// limit; a chat whose cdd stays down tries again after its next turn.
export function checkVersionSoon($: EngineInterface, attempt: number = 1): void {
  $.clock.after(FIRST_CHECK_WAIT_MS, () => void checkUntilReadOrTriesRunOut($, attempt))
}

async function checkUntilReadOrTriesRunOut($: EngineInterface, attempt: number): Promise<void> {
  await checkVersion($)
  if ((await read($, cddVersion)).data === null && attempt < CHECK_TRIES) checkVersionSoon($, attempt + 1)
}

// After a turn: the version on disk read again without fetching, so a version changed by a reset or a pull shows at
// once; while it is not read yet, the full check, as cdd may only now have connected.
export async function readVersionAfterTurn($: EngineInterface): Promise<void> {
  await askVersion($, (await read($, cddVersion)).data === null ? CHECK_TOOL : READ_TOOL)
}

// A call that cannot reach cdd, which is still connecting or down, leaves the badge grey with the reason on hover: the
// server health mark already says cdd is not connected. An answer that is an error or not JSON is a failure.
export async function checkVersion($: EngineInterface): Promise<void> {
  await askVersion($, CHECK_TOOL)
}

async function askVersion($: EngineInterface, tool: string): Promise<void> {
  try {
    const data = await callTool<CddVersionData>($, tool, {})
    await update($, cddVersion, version => ({ ...version, data, problem: null }))
  } catch (failure) {
    if (failure instanceof CddToolFailed) await showFailure($, `The CDD version was not read: ${failure.message}`, `Reading the CDD version, calling ${tool}`)
    else await update($, cddVersion, version => ({ ...version, problem: String(failure) }))
  }
}

export async function askToUpdate($: EngineInterface): Promise<void> {
  await update($, cddVersion, version => ({ ...version, isAsking: true }))
}

export async function cancelUpdate($: EngineInterface): Promise<void> {
  await update($, cddVersion, version => ({ ...version, isAsking: false }))
}

// The update goes in the prompt box, as the action button's command does, and the person's Enter sends it as their own
// /install-latest: the agent runs it as a turn, lists its steps in the task list, and ticks each one off as the script
// reports it. The badge reads the version again after that turn, as after every turn.
export async function updateToLatest($: EngineInterface): Promise<void> {
  await update($, cddVersion, version => ({ ...version, isAsking: false }))
  await promptCommand($, INSTALL_LATEST_COMMAND)
}
