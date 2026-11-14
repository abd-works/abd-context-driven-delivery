import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { CddVersionData } from '@cdd/harness/diagnostics/cdd-version'

import type { CddVersionJson } from '../../types'
import { BRAND } from '../shared/brand'
import { showFailure } from '../error-display/failure-client'

const SERVER = 'plugin:cdd:cdd'
const CHECK_TOOL = 'cdd-version.check'
// A full install from the latest pulls, restarts every server and reinstalls every toolset: minutes, not seconds.
const UPDATE_TIMEOUT_MS = 600000
const ERROR_LINES_SHOWN = 1
// The colour of each standing CddVersion answers: green current, yellow a minor update behind, red a major one.
const STANDING_COLOURS: Record<string, string> = {
  current: BRAND.success,
  'behind minor': BRAND.warning,
  'behind major': BRAND.error,
  unknown: BRAND.muted,
}

const cddVersion = atom({ plugin: 'cdd-board', key: 'cddVersion' } as const, { data: null, isAsking: false, update: 'idle', error: null } as CddVersionJson)

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
    return this.data?.summary ?? 'Reading the CDD version.'
  }

  get latest(): string {
    return this.data?.latest ?? ''
  }

  get isAsking(): boolean {
    return this.json.isAsking
  }

  get update(): CddVersionJson['update'] {
    return this.json.update
  }

  get error(): string | null {
    return this.json.error
  }
}

export async function currentCddVersion($: EngineInterface): Promise<CddVersionClient> {
  return new CddVersionClient(await read($, cddVersion))
}

// Read once as the chat opens: the check fetches origin main, too slow to repeat on every prompt.
export async function checkVersion($: EngineInterface): Promise<void> {
  let result
  try {
    result = await $.mcp.call(SERVER, CHECK_TOOL, {})
  } catch (failure) {
    await showFailure($, `The CDD version was not read: ${String(failure)}`, `Opening the chat, calling ${CHECK_TOOL}`, failure)
    return
  }
  const text = result.content[0]?.text ?? ''
  const data = result.isError ? null : versionFrom(text)
  if (data === null) {
    await showFailure($, `The CDD version was not read: ${text || `${CHECK_TOOL} sent back nothing`}`, `Opening the chat, calling ${CHECK_TOOL}`)
    return
  }
  await update($, cddVersion, version => ({ ...version, data }))
}

export async function askToUpdate($: EngineInterface): Promise<void> {
  await update($, cddVersion, version => ({ ...version, isAsking: true }))
}

export async function cancelUpdate($: EngineInterface): Promise<void> {
  await update($, cddVersion, version => ({ ...version, isAsking: false }))
}

// The update restarts the cdd server, so it runs from here, as Run install does, and not through a cdd tool.
export async function updateToLatest($: EngineInterface): Promise<void> {
  await update($, cddVersion, version => ({ ...version, isAsking: false, update: 'running', error: null }))
  const folder = await $.session.root()
  let command: string[] = []
  try {
    command = [...(await installCommand($)), folder, '--from-latest']
    const run = await $.process.run(command, { cwd: folder, timeoutMs: UPDATE_TIMEOUT_MS })
    const error = run.exitCode === 0 ? null : lastLines(run.stderr || run.stdout)
    await update($, cddVersion, version => ({ ...version, update: error === null ? 'installed' : 'failed', error }))
    if (error !== null) await showFailure($, `The update failed: ${error}`, `Update and reinstall on the version badge, running ${command.join(' ')} in ${folder}`)
    else await checkVersion($)
  } catch (failure) {
    await update($, cddVersion, version => ({ ...version, update: 'failed', error: String(failure) }))
    await showFailure($, 'The update did not run', `Update and reinstall on the version badge, running ${command.join(' ')}`, failure)
  }
}

function versionFrom(text: string): CddVersionData | null {
  try {
    return JSON.parse(text) as CddVersionData
  } catch {
    return null
  }
}

// The cdd home publishes this mod with the command that installs for a chat's folder.
async function installCommand($: EngineInterface): Promise<string[]> {
  const published = `${$.plugin.root}/install.json`
  if (!(await $.fs.exists(published))) throw new Error(`this board mod was not published by a cdd home, so it has no install command; run python scripts/install-latest.py in a CDD checkout`)
  return (JSON.parse(await $.fs.read(published)) as { command: string[] }).command
}

function lastLines(text: string): string {
  return text.trim().split('\n').slice(-ERROR_LINES_SHOWN).join('\n')
}
