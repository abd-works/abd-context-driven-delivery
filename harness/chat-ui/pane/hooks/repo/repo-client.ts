import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { CommitData } from '@cdd/space/repo/repo'

import type { ToMainJson } from '../../types'
import { callTool, refreshChatBar } from '../chat-bar/chat-bar-client'
import { showFailure } from '../error-display/failure-client'

// Where a push lands: the session's own branch, or merged into main on origin.
export type PushTarget = 'branch' | 'main'

const TOOLS: Record<PushTarget, string> = { branch: 'repo.push_work', main: 'repo.push_to_main' }
const PRESSED: Record<PushTarget, string> = { branch: 'Push on the chat bar', main: 'Push & merge to origin/main on the chat bar' }
const FAILED: Record<PushTarget, string> = { branch: 'The push failed', main: 'The push to main failed' }
const SHORT_SHA = 7

const toMain = atom({ plugin: 'cdd-board', key: 'toMain' } as const, { isAsking: false, state: 'idle', target: 'branch', landed: null, error: null } as ToMainJson, { shape: 'to-main-3' })

// Mirrors the Python Repo for the chat bar's two pushes: whether Push to main's dialog is open, and how the last push went.
export class RepoClient {
  constructor(private readonly json: ToMainJson) {}

  get isAsking(): boolean {
    return this.json.isAsking
  }

  get state(): ToMainJson['state'] {
    return this.json.state
  }

  get target(): PushTarget {
    return this.json.target
  }

  get error(): string | null {
    return this.json.error
  }

  // What the bar says once it is done, such as pushed at 1a2b3c4, or main at 1a2b3c4.
  get landed(): string {
    const commit = this.json.landed as CommitData | null
    if (!commit) return ''
    return `${this.json.target === 'main' ? 'main' : 'pushed'} at ${commit.sha.slice(0, SHORT_SHA)}`
  }
}

// Atom toMain, declared in pane/types/index.d.ts and kept in this file.
export async function currentRepo($: EngineInterface): Promise<RepoClient> {
  return new RepoClient(await read($, toMain))
}

export async function askToPush($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: true }))
}

export async function cancelPush($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: false }))
}

// Push: one call to repo.push_work for the folder this chat works in, its branch pushed and nothing merged.
export async function pushWork($: EngineInterface): Promise<void> {
  await pushTo($, 'branch')
}

// Confirmed in the dialog: one call to repo.push_to_main for the folder this chat works in.
export async function pushToMain($: EngineInterface): Promise<void> {
  await pushTo($, 'main')
}

// The one call both pushes share; then the board is read again so the bar shows the session as it now is.
async function pushTo($: EngineInterface, target: PushTarget): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: false, state: 'running', target, error: null }))
  try {
    const landed = await callTool<CommitData>($, TOOLS[target], {})
    await update($, toMain, json => ({ ...json, state: 'installed', landed }))
  } catch (failure) {
    await update($, toMain, json => ({ ...json, state: 'failed', error: String(failure) }))
    await showFailure($, FAILED[target], `${PRESSED[target]}, calling ${TOOLS[target]}`, failure)
  }
  await refreshChatBar($)
}
